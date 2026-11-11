"""Načtení agenta ze složky, předzpracování a sestavení promptu."""

from __future__ import annotations

import importlib.util
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import AGENTS_DIR, SKILLS_DIR
from .validate import validate_input


@dataclass
class Agent:
    path: Path
    spec: dict
    config: dict
    system_prompt: str
    output_template: str
    schema: dict | None
    preprocessors: list[dict] = field(default_factory=list)
    raw_schema: dict | None = None
    input_adapter: dict | None = None

    @property
    def name(self) -> str:
        return self.spec["name"]


def load_agent(name: str) -> Agent:
    path = AGENTS_DIR / name
    if not path.is_dir():
        raise FileNotFoundError(f"Agent '{name}' neexistuje v {AGENTS_DIR}")
    spec = yaml.safe_load((path / "agent.yaml").read_text(encoding="utf-8"))
    config_file = path / "config.yaml"
    config = yaml.safe_load(config_file.read_text(encoding="utf-8")) if config_file.exists() else {}
    prompts = spec["prompts"]
    schema = None
    if spec.get("input_schema"):
        schema = json.loads((path / spec["input_schema"]).read_text(encoding="utf-8"))
    raw_schema = None
    if spec.get("raw_input_schema"):
        raw_schema = json.loads((path / spec["raw_input_schema"]).read_text(encoding="utf-8"))
    return Agent(
        path=path,
        spec=spec,
        config=config,
        system_prompt=(path / prompts["system"]).read_text(encoding="utf-8"),
        output_template=(path / prompts["output_template"]).read_text(encoding="utf-8"),
        schema=schema,
        preprocessors=spec.get("preprocessors", []),
        raw_schema=raw_schema,
        input_adapter=spec.get("input_adapter"),
    )


def _load_skill_function(skill: str, module: str, function: str):
    file = SKILLS_DIR / skill / f"{module}.py"
    spec = importlib.util.spec_from_file_location(f"di_skill_{module}", file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, function)


def prepare_input(agent: Agent, raw: dict) -> dict:
    """Zvaliduje vstup a případně ho převede adaptérem na vstup agenta.

    Bez `input_adapter` jen validuje proti `input_schema`. S adaptérem: validace surových dat
    proti `raw_input_schema` -> převod funkcí skillu -> validace výsledku proti `input_schema`.
    """
    if not agent.input_adapter:
        validate_input(raw, agent.schema)
        return raw
    validate_input(raw, agent.raw_schema)
    a = agent.input_adapter
    data = _load_skill_function(a["skill"], a["module"], a["function"])(raw, agent.config)
    validate_input(data, agent.schema)
    return data


def run_preprocessors(agent: Agent, data: dict) -> dict:
    facts: dict = {}
    for p in agent.preprocessors:
        fn = _load_skill_function(p["skill"], p["module"], p["function"])
        facts[p["result_key"]] = fn(data, agent.config)
    return facts


def render(template: str, variables: dict) -> str:
    def sub(m: re.Match) -> str:
        key = m.group(1).strip()
        if key not in variables:
            raise KeyError(f"Chybí proměnná promptu: {key}")
        value = variables[key]
        return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)

    return re.sub(r"\{\{\s*([\w.]+)\s*\}\}", sub, template)


def _resolve(ref, data: dict, config: dict):
    """`data.a.b` / `config.a.b` se přeloží na hodnotu, cokoli jiného je literál."""
    if not isinstance(ref, str) or not ref.startswith(("data.", "config.")):
        return ref
    root_name, *path = ref.split(".")
    node = data if root_name == "data" else config
    for key in path:
        if not isinstance(node, dict) or key not in node:
            raise KeyError(f"Proměnná '{ref}' nenalezena (chybí '{key}')")
        node = node[key]
    return node


def build_prompt(agent: Agent, data: dict) -> tuple[str, str]:
    """Vrátí (system_prompt, user_message).

    Proměnné promptu se berou ze sekce `variables` v agent.yaml; hodnoty `data.*` / `config.*`
    se dosadí ze vstupu a configu. Navíc je vždy k dispozici `facts` (výstup preprocesorů).
    """
    facts = run_preprocessors(agent, data)
    variables = {
        name: _resolve(ref, data, agent.config) for name, ref in agent.spec.get("variables", {}).items()
    }
    variables["facts"] = facts
    system = render(agent.system_prompt, variables) + "\n\n---\n" + render(agent.output_template, variables)
    user = agent.spec.get("user_prefix", "### INPUT DATA JSON:\n") + json.dumps(data, ensure_ascii=False)
    return system, user
