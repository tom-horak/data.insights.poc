import copy
import json
from pathlib import Path

import pytest

from di.loader import build_prompt, load_agent, prepare_input, run_preprocessors

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "agents/match_analysis_hc/examples"
RAW = ROOT / "data/raw/match_analysis_hc"  # reálná data, gitignored
AGENT = "match_analysis_hc"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _mock(name: str) -> dict:
    return _load(EXAMPLES / f"{name}.json")


def _adapt(raw: dict) -> dict:
    return prepare_input(load_agent(AGENT), raw)


def _metrics(rows: list[dict], team: str) -> dict:
    return {r["metric"]: r[team] for r in rows}


@pytest.mark.parametrize("name", ["mock_hc_close", "mock_hc_overtime"])
def test_mock_adapts_and_prompt_builds(name):
    agent = load_agent(AGENT)
    data = prepare_input(agent, _mock(name))
    system, user = build_prompt(agent, data)
    assert "{{" not in system
    assert data["home_team"] in system and data["away_team"] in system
    assert "0.138" in system  # hd_xg_min z config.adapter
    assert "match_facts" in system
    # do promptu jde převedený vstup, ne surová data
    assert "gameState" not in user and "roster" not in user
    assert "metrics_5_on_5" in user


def test_close_game_metrics_and_situations():
    data = _adapt(_mock("mock_hc_close"))
    assert data["final_score"] == "2:1"
    even_a = _metrics(data["metrics_5_on_5"], "HC Alfa")
    # 4 pokusy 5v5; střela v oslabení a při prázdné brance se nepočítá
    assert even_a["cf"] == 4
    assert even_a["xgf"] == 0.61
    assert even_a["hd.cf"] == 2  # 0.1413 a 0.3 ano, 0.1374 ne
    assert (even_a["r.cf"], even_a["f.cf"], even_a["l.cf"]) == (2, 1, 0)
    assert _metrics(data["metrics_5_on_5"], "HC Beta")["o.cf"] == 2
    pp_a = _metrics(data["metrics_power_play"], "HC Alfa")
    # gól v čase 650 ukončil přesilovku (600, 650] a patří do ní
    assert (pp_a["gf"], pp_a["cf"], pp_a["toi"]) == (1, 2, 50)
    assert _metrics(data["metrics_power_play"], "HC Beta")["toi"] == 120
    assert data["match_goals"][0] == {"time": "10:50", "team": "HC Alfa", "player_name": "Hráč A1"}

    f = run_preprocessors(load_agent(AGENT), data)["match_facts"]
    assert f["goals_outside_5v5_and_power_play"] == {"HC Alfa": 0, "HC Beta": 0}
    assert f["goal_list_consistent_with_score"] is True
    assert f["match"]["date"] is None


def test_overtime_suffix_and_dominance():
    data = _adapt(_mock("mock_hc_overtime"))
    assert data["final_score"] == "3:2n"
    f = run_preprocessors(load_agent(AGENT), data)["match_facts"]
    assert f["match"]["decided_in"] == "overtime"
    assert f["goal_timeline"][-1]["overtime"] is True
    assert f["five_on_five"]["dominance"]["term_dominance_allowed_for"] == ["HC Gamma"]
    # gól 3:3 v prodloužení není 5v5 ani PP
    assert f["goals_outside_5v5_and_power_play"] == {"HC Gamma": 1, "HC Delta": 0}


def test_short_name_option():
    agent = load_agent(AGENT)
    agent.config = copy.deepcopy(agent.config)
    agent.config["adapter"]["team_name_field"] = "shortName"
    data = prepare_input(agent, _mock("mock_hc_close"))
    assert (data["home_team"], data["away_team"]) == ("Alfa", "Beta")


def test_goal_without_matching_shot_rejected():
    raw = _mock("mock_hc_close")
    raw["goal"][0]["time"] = 700
    with pytest.raises(ValueError, match="nemá odpovídající"):
        _adapt(raw)


def test_score_mismatch_rejected():
    raw = _mock("mock_hc_close")
    raw["homeTeam"]["score"] = 4
    with pytest.raises(ValueError, match="neodpovídá skóre"):
        _adapt(raw)


def test_unknown_player_rejected():
    raw = _mock("mock_hc_close")
    raw["shot"][0]["playerId"] = "x99"
    with pytest.raises(ValueError, match="není na soupisce"):
        _adapt(raw)


def test_invalid_raw_rejected():
    raw = _mock("mock_hc_close")
    del raw["homeTeam"]["gameState"]
    with pytest.raises(ValueError, match="gameState"):
        _adapt(raw)


@pytest.mark.skipif(
    not list(RAW.glob("*")) if RAW.exists() else True,
    reason="data/raw/match_analysis_hc je prázdné",
)
@pytest.mark.parametrize(
    "path", sorted(RAW.glob("*")) if RAW.exists() else [], ids=lambda p: p.name
)
def test_real_data_is_valid_and_processable(path):
    agent = load_agent(AGENT)
    data = prepare_input(agent, _load(path))
    f = run_preprocessors(agent, data)["match_facts"]
    assert f["goal_list_consistent_with_score"] is True
    build_prompt(agent, data)
