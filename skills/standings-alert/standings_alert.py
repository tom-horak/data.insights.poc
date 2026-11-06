"""Deterministický výpočet „KRITICKÉHO UPOZORNĚNÍ NA TABULKU".

Čistá aritmetika nad `league_standings`; model dostane hotový výsledek a jen ho interpretuje.
Formát tabulky (Hockey Logic): {team_name, order, PTS, GP, GF, GA}, všechna čísla jako řetězce.
Názvy týmů se berou z `team_name` / `opp_name` na nejvyšší úrovni vstupu.
"""

from __future__ import annotations


def _rows(standings: list[dict]) -> list[dict]:
    return [
        {
            "team": r["team_name"],
            "rank": int(r["order"]),
            "pts": float(r["PTS"]),
            "gp": int(r["GP"]),
        }
        for r in standings
    ]


def compute(data: dict, config: dict) -> dict:
    league = config["league"]
    gap = league["critical_pts_gap"]
    rows = _rows(data["league_standings"])
    ranks = {r["rank"]: r for r in rows}
    by_team = {r["team"]: r for r in rows}

    us = by_team[data["team_name"]]
    opp = by_team[data["opp_name"]]
    reasons: list[dict] = []

    # 1) přímý souboj
    diff = abs(us["pts"] - opp["pts"])
    if diff < gap:
        reasons.append({
            "type": "direct_match",
            "pts_diff": diff,
            "text": f"Přímý souboj: {us['team']} a {opp['team']} dělí {diff:g} b.",
        })

    # 2) hranice TOP 4 / TOP 12
    def boundary(kind: str, cutoff: int, label: str) -> None:
        # tým nad čárou hájí (srovnává se s prvním týmem pod čárou),
        # tým pod čárou se může posunout (srovnává se s posledním týmem nad čárou)
        other_rank = cutoff + 1 if us["rank"] <= cutoff else cutoff
        other = ranks.get(other_rank)
        if not other:
            return
        d = abs(us["pts"] - other["pts"])
        if d < gap:
            action = "hájí" if us["rank"] <= cutoff else "může dosáhnout na"
            reasons.append({
                "type": kind,
                "pts_diff": d,
                "reference_team": other["team"],
                "text": f"{us['team']} {action} {label}; rozdíl na {other['team']} "
                        f"({other_rank}. místo) je {d:g} b.",
            })

    boundary("top4", league["top4_cutoff"], "TOP 4 (přímé čtvrtfinále)")
    boundary("top12", league["playoff_cutoff"], "TOP 12 (předkolo play-off)")

    # 3) poslední místo
    last = league["last_place"]
    if last in ranks:
        if us["rank"] == last:
            ref, action = ranks.get(last - 1), "může opustit"
        else:
            ref, action = ranks[last], "se může vyhnout"
        if ref:
            d = abs(us["pts"] - ref["pts"])
            if d < gap:
                reasons.append({
                    "type": "last_place",
                    "pts_diff": d,
                    "reference_team": ref["team"],
                    "text": f"{us['team']} {action} {last}. místo (sestupové pásmo); "
                            f"rozdíl na {ref['team']} je {d:g} b.",
                })

    return {
        "active": bool(reasons),
        "our_team": {"team": us["team"], "rank": us["rank"], "pts": us["pts"], "gp": us["gp"]},
        "opponent": {"team": opp["team"], "rank": opp["rank"], "pts": opp["pts"], "gp": opp["gp"]},
        "critical_pts_gap": gap,
        "reasons": reasons,
    }
