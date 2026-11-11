# Evaly match_analysis_hc

Rubriky pro kontrolu výstupu:

- Výstup má přesně sekce `English Analysis` a `Česká analýza`, žádný úvod ani dodatek.
- Souhrn má přesně 2 věty (max 25 slov), 3 klíčové faktory po max 20 slovech.
- České znění je věrný překlad anglického (stejné body, stejná čísla).
- Používají se jen přesné názvy týmů ze vstupu.
- Žádné zkratky metrik (`cf`, `xgf`...), čas přesilovky v minutách a sekundách.
- Při rozdílu `cf` ≤ 5 žádné tvrzení o převaze ve střelách; "dominance" jen nad prahy (`cf` > 20 nebo `xgf` > 1.5).
- Čas v přesilovce není hodnocen jako výkon.

Specifické pro data z hokej.COACH:

- Čísla ve výstupu odpovídají převedenému vstupu (`metrics_5_on_5`, `metrics_power_play`) a faktům `match_facts`, ne surovým datům.
- Střely s vysokou nebezpečností se popisují jako šance s vysokým xG, ne jako jiný typ metriky.
- Na reálných datech (`data/raw/match_analysis_hc/`) ověřit `di run-dir match_analysis_hc --dry-run`: prompt nesmí obsahovat surová data (`shifts`, `faceOff`, `puckWon`).
