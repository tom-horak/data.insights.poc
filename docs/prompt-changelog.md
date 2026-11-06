# Changelog promptů

## match_preview 0.2.0
- Schéma vstupu a popis dat v `system.md` upraveny podle reálného payloadu z Hockey Logic chatbota (`team_name`/`opp_name`, metriky jako pole `{metric, metricsValue, order}`, tabulka s řetězcovými čísly).
- Příklady v `examples/` jsou vymyšlená mock data (`scripts/make_mock_data.py`); reálné vzorky jsou v gitignorovaném `data/raw/`.

## match_preview 0.1.0
- Převod původního promptu `di_match_preview_text_cz.md` na agenta.
- Logika „KRITICKÉ UPOZORNĚNÍ NA TABULKU" přesunuta do skillu `standings-alert` (deterministický výpočet).
