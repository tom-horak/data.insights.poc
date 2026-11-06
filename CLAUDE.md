# CLAUDE.md

Repozitář prototypů AI agentů pro analýzu dat (hokejová analytika, výstupy primárně česky).

## Konvence

- Agent = složka `agents/<name>/` s `agent.yaml`, `config.yaml`, `prompts/`, `schemas/`, `examples/`, `evals/`.
- Prompty jsou Markdown soubory, ne řetězce v kódu. Proměnné ve tvaru `{{nazev}}`.
- Čistá aritmetika (rozdíly bodů, pořadí, trendy za N zápasů) se počítá v kódu (`skills/*/`), model dostane hotová fakta a jen je interpretuje.
- Změny promptů zapisuj do `docs/prompt-changelog.md` a zvyš `version` v `agent.yaml`.
- Reálná data patří do `data/raw/` (gitignored), do repa jen anonymizované vzorky.
- Python 3.10+, formátování `ruff`, testy `pytest`.
