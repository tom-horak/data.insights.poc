"""Vygeneruje vymyšlená (mock) data ve formátu exportu zápasu z hokej.COACH.

Použití:  python scripts/make_mock_hc_data.py
Výstup:   agents/match_analysis_hc/examples/mock_hc_*.json  (deterministické, seed je pevný)

Obsahuje jen pole, která čte skill hokejcoach-adapter (bez směn, buly, vstupů do pásma ...).
"""

from __future__ import annotations

import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "agents/match_analysis_hc/examples"
ACTIONS = ["rush", "longAttack", "forecheck", "afterFO", "none"]


def roster(prefix: str, letter: str) -> list[dict]:
    players = [{"id": f"{prefix}0", "name": "Brankář", "surname": letter, "position": "goalkeeper"}]
    for i in range(1, 7):
        pos = "forward" if i <= 4 else "backward"
        players.append(
            {"id": f"{prefix}{i}", "name": "Hráč", "surname": f"{letter}{i}", "position": pos}
        )
    return players


def mirror(states: list[tuple]) -> tuple[list[dict], list[dict]]:
    """(start, end, home_state, home_type, home_goalie, away_goalie) -> gameState obou týmů."""
    flip = {"PP": "SH", "SH": "PP", "RG": "RG", "WG": "WG"}
    home, away = [], []
    for start, end, state, typ, hg, ag in states:
        a, b = state.split(":")
        home.append({"start": start, "end": end, "state": state, "type": typ, "hasGoalie": hg})
        away.append(
            {"start": start, "end": end, "state": f"{b}:{a}", "type": flip[typ], "hasGoalie": ag}
        )
    return home, away


def shot(pid: str, t: int, result: str, xg: float, action: str = "none", odd: bool = False) -> dict:
    return {
        "playerId": pid,
        "time": t,
        "result": result,
        "xG": xg,
        "actionType": action,
        "oddManRush": odd,
        "penaltyShot": False,
    }


def random_shots(
    rng: random.Random, prefix: str, n: int, windows: list[tuple[int, int]]
) -> list[dict]:
    out = []
    for _ in range(n):
        lo, hi = rng.choice(windows)
        result = rng.choice(["saved", "saved", "missed", "deflected", "post"])
        out.append(
            shot(
                f"{prefix}{rng.randint(1, 6)}",
                rng.randint(lo, hi),
                result,
                round(rng.uniform(0.005, 0.12), 4),
                rng.choice(ACTIONS),
                rng.random() < 0.1,
            )
        )
    return out


def game(
    gid: str, home: str, away: str, hp: str, ap: str, states, shots, goals, scores, length=3600
):
    hs, as_ = mirror(states)
    return {
        "id": gid,
        "league": "Mock liga 2026/27",
        "season": "2026",
        "round": "1",
        "length": length,
        "homeTeam": {
            "id": "1",
            "name": home,
            "shortName": home.split()[-1],
            "score": scores[0],
            "roster": roster(hp, hp.upper()),
            "gameState": hs,
        },
        "awayTeam": {
            "id": "2",
            "name": away,
            "shortName": away.split()[-1],
            "score": scores[1],
            "roster": roster(ap, ap.upper()),
            "gameState": as_,
        },
        "shot": sorted(shots, key=lambda s: s["time"]),
        "goal": goals,
    }


def close_game() -> dict:
    """2:1, PP gól ukončí přesilovku, hosté hrají na konci bez brankáře."""
    states = [
        (0, 600, "5:5", "RG", True, True),
        (600, 650, "5:4", "PP", True, True),  # gól domácích v 650 ukončí přesilovku
        (650, 1800, "5:5", "RG", True, True),
        (1800, 1920, "4:5", "SH", True, True),  # přesilovka hostů 2:00
        (1920, 3540, "5:5", "RG", True, True),
        (3540, 3600, "5:6", "WG", True, False),
    ]
    shots = [
        shot("a1", 120, "saved", 0.1374, "rush"),  # těsně pod prahem hd
        shot("a2", 300, "missed", 0.1413, "forecheck"),  # těsně nad prahem hd
        shot("b1", 420, "deflected", 0.02, "longAttack"),
        shot("a3", 620, "saved", 0.08),  # PP domácích
        shot("a1", 649, "goal", 0.21, "longAttack"),  # PP gól (goal[] má čas 650)
        shot("b2", 900, "saved", 0.05, "rush", True),
        shot("b3", 1500, "goal", 0.16, "rush", True),
        shot("a4", 1850, "deflected", 0.01),  # oslabení domácích: nepočítá se
        shot("b4", 1860, "saved", 0.07),  # PP hostů
        shot("b5", 1900, "post", 0.15),  # PP hostů, hd
        shot("a5", 2400, "saved", 0.03, "afterFO"),
        shot("b1", 2600, "missed", 0.04, "forecheck"),
        shot("a2", 3300, "goal", 0.3, "rush"),
        shot("b2", 3560, "saved", 0.05),  # hosté 6 na 5: nepočítá se
        shot("a6", 3580, "missed", 0.5),  # prázdná branka: nepočítá se
    ]
    goals = [
        {"playerId": "a1", "time": 650, "assist1": "a3", "assist2": None},
        {"playerId": "b3", "time": 1501, "assist1": "b2", "assist2": None},
        {"playerId": "a2", "time": 3301, "assist1": None, "assist2": None},
    ]
    return game("9001", "HC Alfa", "HC Beta", "a", "b", states, shots, goals, (2, 1))


def overtime_game() -> dict:
    """3:2 po prodloužení, domácí výrazně převažují 5v5."""
    rng = random.Random(42)
    states = [
        (0, 1000, "5:5", "RG", True, True),
        (1000, 1120, "5:4", "PP", True, True),
        (1120, 3600, "5:5", "RG", True, True),
        (3600, 3900, "3:3", "RG", True, True),
    ]
    even = [(0, 1000), (1120, 3600)]
    shots = random_shots(rng, "g", 48, even) + random_shots(rng, "d", 22, even)
    shots += random_shots(rng, "g", 6, [(1001, 1110)])
    shots += [
        shot("g1", 500, "goal", 0.25, "rush", True),
        shot("d2", 1400, "goal", 0.09, "forecheck"),
        shot("g3", 1080, "goal", 0.18, "longAttack"),
        shot("d4", 3000, "goal", 0.06, "afterFO"),
        shot("g2", 3725, "goal", 0.3, "rush"),
    ]
    goals = [
        {"playerId": "g1", "time": 501, "assist1": None, "assist2": None},
        {"playerId": "g3", "time": 1081, "assist1": None, "assist2": None},
        {"playerId": "d2", "time": 1401, "assist1": None, "assist2": None},
        {"playerId": "d4", "time": 3001, "assist1": None, "assist2": None},
        {"playerId": "g2", "time": 3725, "assist1": None, "assist2": None},
    ]
    return game("9002", "HC Gamma", "HC Delta", "g", "d", states, shots, goals, (3, 2))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in (("mock_hc_close", close_game()), ("mock_hc_overtime", overtime_game())):
        (OUT / f"{name}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"OK {name}.json")


if __name__ == "__main__":
    main()
