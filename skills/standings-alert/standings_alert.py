"""Deterministický výpočet „KRITICKÉHO UPOZORNĚNÍ NA TABULKU".

Čistá aritmetika nad `league_standings`; model dostane hotový výsledek a jen ho interpretuje.
Očekávané položky tabulky: {team, rank, pts}. Pozor: názvy polí upřesni podle reálných dat.
"""

from __future__ import annotations


def _by_rank(standings: list[dict]) -> dict[int, dict]:
    return {int(row["rank"]): row for row in standings}


def compute(data: dict, config: dict) -> dict:
    league = config["league"]
    gap = league["critical_pts_gap"]
    standings = data["league_standings"]
    ranks = _by_rank(standings)
    by_team = {row["team"]: row for row in standings}

    us = by_team[data["team_overview"]["team"]]
    opp = by_team[data["opp_overview"]["team"]]
    reasons: list[dict] = []

    # 1) přímý souboj
    diff = abs(us["pts"] - opp["pts"])
    if diff < gap:
        reasons.append({
            "type": "direct_match",
            "pts_diff": diff,
            "text": f"Přímý souboj: {us['team']} a {opp['team']} dělí {diff:g} b.",
        })

    # 2) hranice TOP 4 / TOP 12 / 14. místo
    def boundary(kind: str, cutoff: int, label: str) -> None:
        # tým nahoře hájí hranici (srovnává se s prvním týmem pod čárou),
        # tým dole se může posunout (srovnává se s posledním týmem nad čárou)
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

    last = league["last_place"]
    last_row = ranks.get(last)
    if last_row:
        if us["rank"] == last:
            ref = ranks.get(last - 1)
            action = "může opustit"
        else:
            ref = last_row
            action = "se může vyhnout"
        if ref:
            d = abs(us["pts"] - ref["pts"])
            if d < gap:
                reasons.append({
                    "type": "last_place",
                    "pts_diff": d,
                    "reference_team": ref["team"],
                    "text": f"{us['team']} {action} 14. místo (sestupové pásmo); "
                            f"rozdíl na {ref['team']} je {d:g} b.",
                })

    return {
        "active": bool(reasons),
        "our_team": {"team": us["team"], "rank": us["rank"], "pts": us["pts"]},
        "opponent": {"team": opp["team"], "rank": opp["rank"], "pts": opp["pts"]},
        "critical_pts_gap": gap,
        "reasons": reasons,
    }
