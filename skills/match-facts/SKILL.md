---
name: match-facts
description: Deterministicky předpočítá fakta o zápase (rozdíly cf/xgf, povolení tvrzení o převaze a „dominance", čas přesilovky v mm:ss, průběh skóre, pozdní góly) pro popis zápasu.
---

# match-facts

Předzpracovatel agenta `match_analysis`. Kód: `match_facts.py`, funkce `compute(data, config) -> dict`.

Prahy jsou v `config.yaml` agenta (`thresholds`):

| Klíč | Význam |
|---|---|
| `cf_equal_max` | rozdíl střelných pokusů ≤ této hodnoty => nesmí se tvrdit, že tým střílel víc |
| `dominance_cf_min` | slovo „dominance" smí padnout při rozdílu cf **větším** než tato hodnota |
| `dominance_xgf_min` | totéž pro rozdíl xgf |
| `late_game_from_sec` | od kdy je gól „pozdní" (výchozí 55:00) |
| `regulation_sec` | konec základní hrací doby (3600) |

Výstup obsahuje mimo jiné `may_claim_one_team_outshot_the_other`, `term_dominance_allowed_for`,
`time_on_ice` ve tvaru `m:ss`, `goal_timeline` (otevírací gól, vyrovnání, pozdní gól...) a
`goals_outside_5v5_and_power_play` (např. extra útočník nebo oslabení, které metriky 5v5 a PP nepokrývají).
