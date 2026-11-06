---
name: standings-alert
description: Vypočítá kritická upozornění z ligové tabulky (přímý souboj, TOP 4, TOP 12, 14. místo) při rozdílu menším než práh bodů.
---

# standings-alert

Deterministický předzpracovatel pro agenty pracující s `league_standings`.

- Kód: `standings_alert.py`, funkce `compute(data, config) -> dict`.
- Vstup: celý vstupní JSON agenta + `config.yaml` agenta (sekce `league`).
- Výstup: `{active, our_team, opponent, reasons[]}`; agent zobrazí upozornění, pokud `active`.

Podmínky (rozdíl `< critical_pts_gap`): přímý souboj; hájení/dosažení TOP 4; hájení/dosažení TOP 12; opuštění/vyhnutí se poslednímu místu.
