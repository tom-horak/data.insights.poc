# Changelog promptů

## match_analysis_hc 0.1.0
- Nový agent: stejný výstup jako `match_analysis`, ale vstupem je surový export zápasu z hokej.COACH.
- Skill `hokejcoach-adapter` (`input_adapter` v `agent.yaml`) převede data na vstup ve tvaru `match_analysis`; do promptu jde jen převedený vstup, ne surová data.
- Prompty jsou kopií `match_analysis` 0.1.0. V glosáři se upřesnilo, že `cf` zahrnuje všechny pokusy včetně zblokovaných a že `hd.cf` = xG nad `{{hd_xg_min}}` (`config.adapter.hd_xg_min`, 0.138).
- `match_date` je nepovinné (hokej.COACH datum zápasu nedodává).

## match_analysis 0.1.0
- Nový agent z `di_match_analysis.md` (dvojjazyčný EN + CZ pozápasový souhrn a 3 klíčové faktory).
- Prahy (rozdíl `cf` ≤ 5, „dominance" při `cf` > 20 nebo `xgf` > 1.5) a limity slov jsou v `config.yaml` a doplňují se do promptu.
- Skill `match-facts` předpočítá povolená tvrzení, čas přesilovky v mm:ss, průběh skóre a góly mimo 5v5/PP.

## match_preview 0.2.0 (úprava)
- Proměnné promptu se nově deklarují v `agent.yaml` (`variables`), obsah promptu beze změny.

## match_preview 0.2.0
- Schéma vstupu a popis dat v `system.md` upraveny podle reálného payloadu z Hockey Logic chatbota (`team_name`/`opp_name`, metriky jako pole `{metric, metricsValue, order}`, tabulka s řetězcovými čísly).
- Příklady v `examples/` jsou vymyšlená mock data (`scripts/make_mock_data.py`); reálné vzorky jsou v gitignorovaném `data/raw/`.

## match_preview 0.1.0
- Převod původního promptu `di_match_preview_text_cz.md` na agenta.
- Logika „KRITICKÉ UPOZORNĚNÍ NA TABULKU" přesunuta do skillu `standings-alert` (deterministický výpočet).
