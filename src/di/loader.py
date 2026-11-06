"""Načtení agenta ze složky, předzpracování a sestavení promptu."""

from __future__ import annotations

import importlib.util
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import AGENTS_DIR, SKILLS_DIR


@dataclass
class Agent:
    path: Path
    spec: dict
    config: dict
    system_prompt: str
    output_template: str
    schema: dict | None
    preprocessors: list[dict] = field(default_factory=list)

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
    return Agent(
        path=path,
        spec=spec,
        config=config,
        system_prompt=(path / prompts["system"]).read_text(encoding="utf-8"),
        output_template=(path / prompts["output_template"]).read_text(encoding="utf-8"),
        schema=schema,
        preprocessors=spec.get("preprocessors", []),
    )


def _load_skill_function(skill: str, module: str, function: str):
    file = SKILLS_DIR / skill / f"{module}.py"
    spec = importlib.util.spec_from_file_location(f"di_skill_{module}", file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, function)


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


def build_prompt(agent: Agent, data: dict) -> tuple[str, str]:
    """Vrátí (system_prompt, user_message)."""
    facts = run_preprocessors(agent, data)
    variables = {
        "league_teams": agent.config.get("league", {}).get("teams", ""),
        "last_n_games": agent.config.get("form", {}).get("last_n_games", 5),
        "team_name": data["team_name"],
        "opponent_name": data["opp_name"],
        "facts": facts,
    }
    system = render(agent.system_prompt, variables) + "\n\n---\n" + render(agent.output_template, variables)
    user = "### VSTUPNÍ DATA JSON:\n" + json.dumps(data, ensure_ascii=False)
    return system, user
