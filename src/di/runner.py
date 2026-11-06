"""Spuštění agenta: validace, sestavení promptu, volání modelu."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from .loader import Agent, build_prompt, load_agent
from .validate import validate_input


def run(agent_name: str, input_path: Path, dry_run: bool = False) -> str:
    load_dotenv()
    agent: Agent = load_agent(agent_name)
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    validate_input(data, agent.schema)
    system, user = build_prompt(agent, data)

    if dry_run:
        return f"=== SYSTEM ===\n{system}\n\n=== USER ===\n{user[:1500]}"

    import anthropic

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=os.getenv("DI_MODEL", agent.spec["model"]),
        max_tokens=agent.spec.get("max_tokens", 4096),
        temperature=agent.spec.get("temperature", 0.3),
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in response.content if b.type == "text")
