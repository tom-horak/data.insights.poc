---
name: hokejcoach-adapter
description: Převede surový export zápasu z hokej.COACH (soupisky, gameState, shot[], goal[]) na vstup ve tvaru match_analysis (metriky 5v5 a přesilovky, průběh gólů, skóre).
---

# hokejcoach-adapter

Vstupní adaptér agenta `match_analysis_hc`. Kód: `hokejcoach_adapter.py`, funkce
`to_match_input(raw, config) -> dict`. Volá se přes `input_adapter` v `agent.yaml` dřív, než běží
preprocesory, takže výstup pak zpracuje beze změny skill `match-facts`.

## Transformace

| Výstup | Zdroj |
|---|---|
| `home_team` / `away_team` | `homeTeam/awayTeam.<team_name_field>` (výchozí `name`) |
| `final_score` | `score` obou týmů; `n` = gól s `time > length`; `p` = nájezdy (počet gólů v `goal[]` nesedí se skóre, po hře remíza; neověřeno na reálných datech) |
| `match_goals` | `goal[]`: čas `m:ss` z `time` (s), tým a jméno střelce ze soupisky |
| `metrics_5_on_5` | střely ve stavu `5:5` s brankáři na obou stranách: `gf`, `xgf`, `cf`, `hd.cf`, `r.cf`, `o.cf`, `f.cf`, `l.cf` |
| `metrics_power_play` | střely týmu v intervalu `type: PP` jeho `gameState`: `gf`, `xgf`, `cf`, `hd.cf`, `toi` (součet délek PP intervalů v s) |

- `cf` = všechny záznamy `shot[]` (saved, missed, post, deflected = zblokovaná, goal), včetně trestných střílení.
- `xgf` = součet `xG` všech pokusů, zaokrouhleno na 2 místa.
- `hd.cf` = pokusy s `xG > hd_xg_min`.
- `r.cf` / `f.cf` / `l.cf` = `actionType` rush / forecheck / longAttack, `o.cf` = `oddManRush: true`; `afterFO` a `none` se nepočítají.
- Interval `gameState` platí jako `(start, end]` (gól ukončí přesilovku přesně v `end`).
- Situace mimo 5v5 a přesilovku (oslabení, 4:4, prázdná branka, 3:3 v prodloužení) do metrik nevstupují.

## Konfigurace (`config.yaml` agenta, sekce `adapter`)

| Klíč | Význam |
|---|---|
| `hd_xg_min` | práh xG pro střelu s vysokou nebezpečností (0.138) |
| `team_name_field` | `name` nebo `shortName` |
| `goal_shot_max_dt_sec` | tolerance při párování `goal[]` se střelou `result: goal` (časy se liší o ~1 s) |

## Kontroly

Adaptér skončí `ValueError`, když: střela nebo gól patří hráči mimo soupisky, gól nemá odpovídající
střelu s výsledkem `goal`, nebo počet gólů v `goal[]` neodpovídá skóre (mimo nájezdy).
