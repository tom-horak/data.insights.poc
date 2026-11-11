"""Deterministická fakta o zápase pro agenta `match_analysis`.

Všechna pravidla s prahy (kdy smí model tvrdit, že tým byl lepší, a kdy smí použít slovo
„dominance"), formátování času a průběh skóre se počítají zde, ne v modelu.

Vstup: {match_date, home_team, away_team, final_score, match_goals[], metrics_5_on_5[],
        metrics_power_play[]}; metriky mají tvar {metric, <home_team>: x, <away_team>: y}.
"""

from __future__ import annotations

import re

_SCORE = re.compile(r"^\s*(\d+)\s*:\s*(\d+)\s*([A-Za-z]*)\s*$")


def _parse_time(value: str) -> int:
    minutes, seconds = value.split(":")
    return int(minutes) * 60 + int(seconds)


def _fmt_time(seconds: float) -> str:
    seconds = round(seconds)
    return f"{seconds // 60}:{seconds % 60:02d}"


def _metric_table(rows: list[dict], home: str, away: str) -> dict[str, dict]:
    table = {}
    for row in rows or []:
        if home in row and away in row:
            h, a = row[home], row[away]
            table[row["metric"]] = {"home": h, "away": a, "diff_home_minus_away": round(h - a, 2)}
    return table


def _leader(diff: float, home: str, away: str, threshold: float, strict: bool) -> str | None:
    """Tým s náskokem; `strict` = náskok musí být větší než práh, jinak stačí rovno/větší."""
    magnitude = abs(diff)
    passes = magnitude > threshold if strict else magnitude >= threshold
    if not passes:
        return None
    return home if diff > 0 else away


def compute(data: dict, config: dict) -> dict:
    t = config["thresholds"]
    home, away = data["home_team"], data["away_team"]

    # --- skóre
    m = _SCORE.match(data["final_score"])
    if not m:
        raise ValueError(f"Neplatné final_score: {data['final_score']!r}")
    hg, ag, suffix = int(m.group(1)), int(m.group(2)), m.group(3).lower()
    decided = {"": "regulation", "n": "overtime", "p": "shootout"}.get(suffix, f"other:{suffix}")
    winner = home if hg > ag else away

    # --- 5v5 a přesilovka
    even = _metric_table(data.get("metrics_5_on_5", []), home, away)
    pp = _metric_table(data.get("metrics_power_play", []), home, away)

    cf_diff = even.get("cf", {}).get("diff_home_minus_away")
    xgf_diff = even.get("xgf", {}).get("diff_home_minus_away")

    cf_edge = _leader(cf_diff, home, away, t["cf_equal_max"], strict=True) if cf_diff is not None else None
    cf_dom = _leader(cf_diff, home, away, t["dominance_cf_min"], strict=True) if cf_diff is not None else None
    xgf_dom = (
        _leader(xgf_diff, home, away, t["dominance_xgf_min"], strict=True) if xgf_diff is not None else None
    )

    five_on_five = {
        "metrics": even,
        "shot_attempts": {
            "abs_difference": abs(cf_diff) if cf_diff is not None else None,
            "team_with_edge": cf_edge,
            "may_claim_one_team_outshot_the_other": cf_edge is not None,
        },
        "dominance": {
            "by_shot_attempts": cf_dom,
            "by_expected_goals": xgf_dom,
            "term_dominance_allowed_for": sorted({x for x in (cf_dom, xgf_dom) if x}),
        },
        "finishing": {  # skutečné minus očekávané góly
            team: round(even["gf"][side] - even["xgf"][side], 2)
            for team, side in ((home, "home"), (away, "away"))
        }
        if "gf" in even and "xgf" in even
        else None,
    }

    power_play = {
        "metrics": pp,
        "time_on_ice": {
            team: _fmt_time(pp["toi"][side])
            for team, side in ((home, "home"), (away, "away"))
        }
        if "toi" in pp
        else None,
        "finishing": {
            team: round(pp["gf"][side] - pp["xgf"][side], 2)
            for team, side in ((home, "home"), (away, "away"))
        }
        if "gf" in pp and "xgf" in pp
        else None,
        "rule": "Time on ice is NOT a performance indicator; judge by conversion (gf vs xgf).",
    }

    # --- průběh gólů
    goals = sorted(data.get("match_goals", []), key=lambda g: _parse_time(g["time"]))
    score = {home: 0, away: 0}
    timeline = []
    for g in goals:
        team = g["team"]
        other = away if team == home else home
        before_diff = score[team] - score[other]
        score[team] += 1
        after_diff = score[team] - score[other]
        seconds = _parse_time(g["time"])
        if before_diff == 0 and score[team] + score[other] == 1:
            kind = "opening goal"
        elif before_diff == 0:
            kind = "go-ahead goal"
        elif before_diff < 0 and after_diff == 0:
            kind = "equaliser"
        elif before_diff < 0:
            kind = "goal cutting the deficit"
        else:
            kind = "goal extending the lead"
        timeline.append({
            "time": g["time"],
            "team": team,
            "player": g.get("player_name"),
            "type": kind,
            "score_after": f"{score[home]}:{score[away]}",
            "late_game": seconds >= t["late_game_from_sec"] and seconds < t["regulation_sec"],
            "overtime": seconds >= t["regulation_sec"],
        })

    # --- góly mimo 5v5 a přesilovku (extra útočník, oslabení, 4v4 ...)
    other_goals = None
    if "gf" in even and "gf" in pp:
        other_goals = {
            home: hg - even["gf"]["home"] - pp["gf"]["home"],
            away: ag - even["gf"]["away"] - pp["gf"]["away"],
        }

    return {
        "match": {
            "date": data.get("match_date"),
            "home_team": home,
            "away_team": away,
            "final_score": data["final_score"],
            "home_goals": hg,
            "away_goals": ag,
            "decided_in": decided,
            "winner": winner,
        },
        "five_on_five": five_on_five,
        "power_play": power_play,
        "goal_timeline": timeline,
        "goals_outside_5v5_and_power_play": other_goals,
        "goal_list_consistent_with_score": (
            sum(1 for g in goals if g["team"] == home) == hg
            and sum(1 for g in goals if g["team"] == away) == ag
        ),
    }
