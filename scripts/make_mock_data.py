"""Vygeneruje vymyšlená (mock) vstupní data ve stejném formátu jako reálný payload.

Použití:  python scripts/make_mock_data.py
Výstup:   agents/match_preview/examples/mock_*.json  (deterministické, seed je pevný)
"""

from __future__ import annotations

import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "agents/match_preview/examples"

TEAMS = [
    "HC Alfa", "HC Beta", "HC Gamma", "HC Delta", "HC Epsilon", "HC Zeta", "HC Eta",
    "HC Theta", "HC Iota", "HC Kappa", "HC Lambda", "HC Mí", "HC Ný", "HC Ksí",
]
METRICS = {  # metric: (min, max)
    "gf60": (1.4, 2.6), "ga60": (1.4, 2.6), "sh_ga60": (3.0, 12.0),
    "pp_gf60": (4.0, 8.0), "gsax": (-9.0, 17.0), "form": (1, 14),
}


def standings(points: list[int]) -> list[dict]:
    rows = []
    for i, (team, pts) in enumerate(zip(TEAMS, points), start=1):
        rows.append({
            "team_name": team, "order": str(i), "PTS": str(pts), "GP": "17",
            "GF": str(35 + (14 - i) * 2), "GA": str(35 + i * 2),
        })
    return rows


def overview(rng: random.Random) -> list[dict]:
    out = []
    for metric, (lo, hi) in METRICS.items():
        value = rng.randint(int(lo), int(hi)) if metric == "form" else round(rng.uniform(lo, hi), 2)
        out.append({"metric": metric, "metricsValue": value, "order": rng.randint(1, 14)})
    return out


def players(prefix: str, n: int) -> list[str]:
    return [f"{prefix} Hráč {i + 1}" for i in range(n)]


def game(rng: random.Random, team: str, opps: list[str], idx: int, prefix: str) -> dict:
    home = rng.random() < 0.5
    opp = opps[idx % len(opps)]
    gf, ga = rng.randint(0, 5), rng.randint(0, 5)
    if gf == ga:
        gf += 1
    home_g, away_g = (gf, ga) if home else (ga, gf)
    xg_h, xg_a = round(rng.uniform(1.0, 4.5), 2), round(rng.uniform(1.0, 4.5), 2)
    win = round(100 * xg_h / (xg_h + xg_a), 4)
    names = players(prefix, 20)

    def line(i: int, roles: list[str]) -> dict:
        d = {"line": str(i)}
        for j, r in enumerate(roles):
            d[r] = names[(i * 3 + j) % len(names)]
        d.update({"GF": rng.randint(0, 1), "GA": rng.randint(0, 1), "xGF%": round(rng.uniform(15, 85), 2)})
        return d

    return {
        "matchInfo": {
            "matchDate": f"2026-10-{31 - idx * 3:02d}",
            "homeTeam": team if home else opp,
            "awayTeam": opp if home else team,
            "score": f"{home_g}:{away_g}",
        },
        "stats": [
            {"metric": "C", "home": rng.randint(40, 75), "away": rng.randint(40, 75)},
            {"metric": "xG", "home": xg_h, "away": xg_a},
            {"metric": "expectedWin", "home": win, "away": round(100 - win, 4)},
        ],
        "statsSpecialTeams": [
            {"specialTeam": "powerPlay", "GF": "0", "GA": "0",
             "xGF/60": str(round(rng.uniform(0, 12), 2)), "xGA/60": str(round(rng.uniform(0, 3), 2))},
            {"specialTeam": "shortHanded", "GF": "0", "GA": "0",
             "xGF/60": str(round(rng.uniform(0, 1.5), 2)), "xGA/60": str(round(rng.uniform(0, 12), 2))},
        ],
        "goalkeepers": [{
            "goalkeeper_name": f"{prefix} Brankář", "GA": str(ga),
            "GSAx": str(round(rng.uniform(-1.5, 2.0), 2)),
        }],
        "forwards": [line(i, ["RW", "C", "LW"]) for i in range(1, 5)]
        + [{"line": "5", "GF": 0, "GA": 0, "xGF%": 0}],
        "defencemen": [line(i, ["LD", "RD"]) for i in range(1, 4)],
    }


def build(name: str, points: list[int], our_rank: int, opp_rank: int, seed: int) -> dict:
    rng = random.Random(seed)
    team, opp = TEAMS[our_rank - 1], TEAMS[opp_rank - 1]
    others = [t for t in TEAMS if t not in (team, opp)]
    return {
        "team_name": team,
        "opp_name": opp,
        "team_overview": overview(rng),
        "opp_overview": overview(rng),
        "league_standings": standings(points),
        "team_games": [game(rng, team, others, i, "A") for i in range(5)],
        "opp_games": [game(rng, opp, others, i, "B") for i in range(5)],
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    scenarios = {
        # 4. vs 5. místo, rozdíl 2 b.: přímý souboj + hájení TOP 4
        "mock_alert": build("alert", [42, 36, 30, 28, 26, 22, 20, 18, 16, 14, 12, 10, 8, 5], 4, 5, 1),
        # vzdálené týmy a odstupy 5 b.: žádné kritické upozornění
        "mock_no_alert": build("no_alert", [70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10, 5], 7, 9, 2),
    }
    for name, data in scenarios.items():
        (OUT / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("zapsáno:", OUT / f"{name}.json")


if __name__ == "__main__":
    main()
