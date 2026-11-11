"""Převod surového exportu zápasu z hokej.COACH na vstup agenta `match_analysis`.

Výstup má stejný tvar jako payload z Hockey Logic ({home_team, away_team, final_score,
match_goals[], metrics_5_on_5[], metrics_power_play[]}), takže na něj lze pustit beze změny
skill `match-facts`. Všechny agregace (cf, xgf, hd.cf, typy akcí, čas v přesilovce) se počítají
zde; surová data (směny, buly, vstupy do pásma ...) se do promptu neposílají.

Pravidla:
- Herní stav v čase t se bere z `gameState` obou týmů; interval platí jako (start, end],
  protože gól ukončí přesilovku přesně v čase `end`. Pro t = 0 platí interval začínající nulou.
- 5v5 = stav "5:5" a oba týmy mají brankáře. PP týmu = interval typu "PP" v jeho `gameState`.
- cf = všechny záznamy `shot[]` (včetně zblokovaných a trestných střílení), xgf = součet `xG`
  všech pokusů, hd.cf = pokusy s `xG` nad `config.adapter.hd_xg_min`.
- r/o/f/l.cf podle `actionType` (rush / longAttack / forecheck) a `oddManRush`.
"""

from __future__ import annotations

ACTION_METRICS = {"r.cf": "rush", "f.cf": "forecheck", "l.cf": "longAttack"}
EVEN_METRICS = ("gf", "xgf", "cf", "hd.cf", "r.cf", "o.cf", "f.cf", "l.cf")
PP_METRICS = ("gf", "xgf", "cf", "hd.cf", "toi")


def _fmt_time(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def _interval_at(intervals: list[dict], t: float) -> dict | None:
    for iv in intervals:
        if iv["start"] < t <= iv["end"] or (t == iv["start"] == 0):
            return iv
    return None


def _situation(home_states: list[dict], away_states: list[dict], t: float, home: str, away: str):
    """Vrátí ("5v5", None), ("pp", <tým v přesilovce>) nebo (None, None) pro ostatní situace."""
    h, a = _interval_at(home_states, t), _interval_at(away_states, t)
    if h is None or a is None:
        return None, None
    if h["state"] == "5:5" and h.get("hasGoalie") and a.get("hasGoalie"):
        return "5v5", None
    if h["type"] == "PP":
        return "pp", home
    if a["type"] == "PP":
        return "pp", away
    return None, None


def _empty(metrics: tuple[str, ...]) -> dict:
    return {m: 0 for m in metrics}


def _add_shot(bucket: dict, shot: dict, hd_xg_min: float, with_actions: bool) -> None:
    xg = shot.get("xG") or 0.0
    bucket["cf"] += 1
    bucket["xgf"] += xg
    bucket["gf"] += 1 if shot["result"] == "goal" else 0
    bucket["hd.cf"] += 1 if xg > hd_xg_min else 0
    if with_actions:
        for metric, action in ACTION_METRICS.items():
            bucket[metric] += 1 if shot.get("actionType") == action else 0
        bucket["o.cf"] += 1 if shot.get("oddManRush") else 0


def _rows(metrics: tuple[str, ...], values: dict, home: str, away: str) -> list[dict]:
    rows = []
    for m in metrics:
        h, a = values[home][m], values[away][m]
        if m == "xgf":
            h, a = round(h, 2), round(a, 2)
        rows.append({"metric": m, home: h, away: a})
    return rows


def to_match_input(raw: dict, config: dict) -> dict:
    cfg = config["adapter"]
    name_field = cfg.get("team_name_field", "name")
    hd_xg_min = cfg["hd_xg_min"]
    max_dt = cfg["goal_shot_max_dt_sec"]

    home_raw, away_raw = raw["homeTeam"], raw["awayTeam"]
    home, away = home_raw[name_field], away_raw[name_field]
    if home == away:
        raise ValueError(f"Domácí a hosté mají stejný název týmu: {home!r}")

    players: dict[str, tuple[str, str]] = {}
    for team_raw, team in ((home_raw, home), (away_raw, away)):
        for p in team_raw["roster"]:
            full_name = " ".join(x for x in (p.get("name"), p.get("surname")) if x)
            players[str(p["id"])] = (team, full_name)

    def team_of(player_id, what: str) -> str:
        if player_id is None or str(player_id) not in players:
            raise ValueError(f"{what}: hráč {player_id!r} není na soupisce ani jednoho týmu")
        return players[str(player_id)][0]

    home_states, away_states = home_raw["gameState"], away_raw["gameState"]

    # --- metriky ze střel
    even = {home: _empty(EVEN_METRICS), away: _empty(EVEN_METRICS)}
    pp = {home: _empty(PP_METRICS), away: _empty(PP_METRICS)}
    for shot in raw.get("shot", []):
        team = team_of(shot.get("playerId"), f"Střela v čase {shot.get('time')}")
        kind, pp_team = _situation(home_states, away_states, shot["time"], home, away)
        if kind == "5v5":
            _add_shot(even[team], shot, hd_xg_min, with_actions=True)
        elif kind == "pp" and pp_team == team:
            _add_shot(pp[team], shot, hd_xg_min, with_actions=False)

    for team, states in ((home, home_states), (away, away_states)):
        pp[team]["toi"] = sum(iv["end"] - iv["start"] for iv in states if iv["type"] == "PP")

    # --- góly
    goal_shots = [s for s in raw.get("shot", []) if s["result"] == "goal"]
    match_goals = []
    counts = {home: 0, away: 0}
    for g in sorted(raw.get("goal", []), key=lambda g: g["time"]):
        team = team_of(g.get("playerId"), f"Gól v čase {g.get('time')}")
        if not any(
            str(s["playerId"]) == str(g["playerId"]) and abs(s["time"] - g["time"]) <= max_dt
            for s in goal_shots
        ):
            raise ValueError(
                f"Gól v {_fmt_time(g['time'])} ({players[str(g['playerId'])][1]}) nemá odpovídající "
                f"střelu s výsledkem 'goal' (tolerance {max_dt} s)"
            )
        counts[team] += 1
        match_goals.append(
            {
                "time": _fmt_time(g["time"]),
                "team": team,
                "player_name": players[str(g["playerId"])][1],
            }
        )

    # --- skóre
    hs, as_ = home_raw["score"], away_raw["score"]
    length = raw.get("length", 3600)
    suffix = "n" if any(g["time"] > length for g in raw.get("goal", [])) else ""
    if (counts[home], counts[away]) != (hs, as_):
        # nájezdy: po hře remíza, konečné skóre se liší o jeden gól (neověřeno na reálných datech)
        if counts[home] == counts[away] and abs(hs - as_) == 1 and min(hs, as_) == counts[home]:
            suffix = "p"
        else:
            raise ValueError(
                f"Počet gólů v goal[] ({counts[home]}:{counts[away]}) neodpovídá skóre {hs}:{as_}"
            )

    return {
        "source": {
            "provider": "hokej.COACH",
            "game_id": raw.get("id"),
            "league": raw.get("league"),
            "round": raw.get("round"),
        },
        "home_team": home,
        "away_team": away,
        "final_score": f"{hs}:{as_}{suffix}",
        "match_goals": match_goals,
        "metrics_5_on_5": _rows(EVEN_METRICS, even, home, away),
        "metrics_power_play": _rows(PP_METRICS, pp, home, away),
    }
