# data.insights.poc

Prototypy AI agentů pro zpracování a analýzu dat (Data Insights). Repozitář slouží k rychlému vývoji a ladění skillů a promptů.

## Princip

- **Agent = složka** v `agents/<nazev>/` (prompt, schéma vstupu, konfigurace, příklady, evaly).
- **Skilly** v `skills/` jsou znovupoužitelné napříč agenty. Deterministická logika (výpočty) je v kódu, model ji jen interpretuje.
- **Runtime** `src/di/` je tenká vrstva: načte agenta, zvaliduje vstup, předpočítá fakta, zavolá model.

## Rychlý start

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e ".[dev]"
copy .env.example .env          # doplň ANTHROPIC_API_KEY

# náhled sestaveného promptu bez volání modelu
di run match_preview --input agents/match_preview/examples/sample_input.json --dry-run

# ostrý běh
di run match_preview --input agents/match_preview/examples/sample_input.json --out outputs/preview.md
```

## Struktura

```
agents/      jednotliví agenti (agent.yaml, config.yaml, prompts/, schemas/, examples/, evals/)
skills/      sdílené skilly (SKILL.md + případně skripty)
prompts/     sdílené fragmenty promptů a scratch/ s původními prompty
src/di/      runtime (loader, validace, runner, CLI)
data/        samples/ (verzované), raw/ (gitignored)
outputs/     vygenerované reporty (gitignored)
tests/       testy deterministické části
docs/        poznámky k designu
```

## Nový agent

1. Zkopíruj `agents/match_preview/` a přejmenuj.
2. Uprav `agent.yaml`, `prompts/system.md`, `schemas/input.schema.json`.
3. Přidej vzorový vstup do `examples/`.
