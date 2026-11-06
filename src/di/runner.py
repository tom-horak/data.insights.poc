"""Spuštění agenta: validace, sestavení promptu, volání modelu (jeden soubor nebo celá složka)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .loader import Agent, build_prompt, load_agent
from .validate import validate_input

DEFAULT_PATTERNS = ("*.json", "*.txt")


def _run_one(agent: Agent, input_path: Path, dry_run: bool, client=None) -> str:
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    validate_input(data, agent.schema)
    system, user = build_prompt(agent, data)

    if dry_run:
        return f"=== SYSTEM ===\n{system}\n\n=== USER ===\n{user[:1500]}"

    response = client.messages.create(
        model=os.getenv("DI_MODEL", agent.spec["model"]),
        max_tokens=agent.spec.get("max_tokens", 4096),
        temperature=agent.spec.get("temperature", 0.3),
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in response.content if b.type == "text")


def _client(dry_run: bool):
    if dry_run:
        return None
    import anthropic

    return anthropic.Anthropic()


def run(agent_name: str, input_path: Path, dry_run: bool = False) -> str:
    load_dotenv()
    agent = load_agent(agent_name)
    return _run_one(agent, input_path, dry_run, _client(dry_run))


@dataclass
class DirResult:
    ok: list[Path]
    failed: list[tuple[Path, str]]
    skipped: list[Path]


def find_inputs(input_dir: Path, patterns: tuple[str, ...] = DEFAULT_PATTERNS) -> list[Path]:
    files: set[Path] = set()
    for pattern in patterns:
        files.update(p for p in Path(input_dir).glob(pattern) if p.is_file())
    return sorted(files)


def run_dir(
    agent_name: str,
    input_dir: Path,
    out_dir: Path,
    dry_run: bool = False,
    overwrite: bool = False,
    patterns: tuple[str, ...] = DEFAULT_PATTERNS,
    log=print,
) -> DirResult:
    """Vyhodnotí všechny vstupy ve složce; každý výstup uloží jako `<out_dir>/<název>.md`.

    Chyba jednoho souboru neukončí zbytek dávky. Existující výstupy se přeskočí,
    pokud není `overwrite=True` (ať se zbytečně neplatí za volání modelu).
    """
    load_dotenv()
    agent = load_agent(agent_name)
    inputs = find_inputs(input_dir, patterns)
    if not inputs:
        raise FileNotFoundError(f"Ve složce {input_dir} nebyl nalezen žádný vstup ({', '.join(patterns)})")

    out_dir = Path(out_dir)
    client = _client(dry_run)
    result = DirResult(ok=[], failed=[], skipped=[])
    for path in inputs:
        target = out_dir / f"{path.stem}.md"
        if target.exists() and not overwrite and not dry_run:
            log(f"přeskočeno (výstup existuje): {path.name}")
            result.skipped.append(path)
            continue
        try:
            text = _run_one(agent, path, dry_run, client)
        except Exception as e:  # noqa: BLE001 - dávka musí pokračovat
            log(f"CHYBA {path.name}: {e}")
            result.failed.append((path, str(e)))
            continue
        if dry_run:
            log(f"OK (dry-run) {path.name}")
        else:
            out_dir.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            log(f"OK {path.name} -> {target}")
        result.ok.append(path)
    return result
