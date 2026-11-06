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

# náhled sestaveného promptu bez volání modelu (mock data)
di run match_preview --input agents/match_preview/examples/mock_alert.json --dry-run

# ostrý běh nad jedním souborem
di run match_preview --input agents/match_preview/examples/mock_alert.json --out outputs/mock_alert.md
```

## Reálná data

Reálné vstupy (`*.json` nebo `*.txt` z Hockey Logic chatbota) patří do `data/raw/<agent>/` (např.
`data/raw/match_preview/`, `data/raw/match_analysis/`), které je gitignorované.
Celou složku vyhodnotíš jedním příkazem, výstupy se uloží jako `outputs/<agent>/<název>.md`:

```bash
di run-dir match_preview --dry-run          # jen validace a sestavení promptů, bez volání modelu
di run-dir match_analysis                   # ostrý běh nad data/raw/match_analysis, existující výstupy přeskočí
di run-dir match_analysis --overwrite       # přepíše existující výstupy
di run-dir match_preview --input-dir D:\jina\slozka --out-dir D:\vystupy
```

## Agenti

| Agent | Účel | Předzpracování (skill) |
|---|---|---|
| `match_preview` | předzápasový skautský přehled (CZ) | `standings-alert` |
| `match_analysis` | pozápasová analýza, EN + CZ | `match-facts` |

Chyba v jednom souboru dávku nezastaví, na konci je souhrn. Testy nad `data/raw` se spustí jen
tehdy, když tam nějaká data jsou.

## Mock data

Vymyšlená data ve stejném formátu jsou v `agents/<agent>/examples/`. Pro `match_preview` je generuje
`python scripts/make_mock_data.py` (`mock_alert.json` se spuštěným upozorněním na tabulku,
`mock_no_alert.json` bez něj), pro `match_analysis` jsou ručně psané (`mock_close.json` s prodloužením
a pozdním vyrovnáním, `mock_dominance.json` s rozdílem nad prahy). Testy používají jen je.

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
3. Přidej mock vstup do `examples/` (nikdy reálná data, ta patří do `data/raw/`).
