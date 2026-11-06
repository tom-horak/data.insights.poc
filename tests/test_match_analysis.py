import json
from pathlib import Path

import pytest

from di.loader import build_prompt, load_agent, run_preprocessors
from di.validate import validate_input

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "agents/match_analysis/examples"
RAW = ROOT / "data/raw/match_analysis"  # reálná data, gitignored


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _facts(data: dict) -> dict:
    return run_preprocessors(load_agent("match_analysis"), data)["match_facts"]


def _mock(name: str) -> dict:
    return _load(EXAMPLES / f"{name}.json")


@pytest.mark.parametrize("name", ["mock_close", "mock_dominance"])
def test_mock_validates_and_prompt_builds(name):
    agent = load_agent("match_analysis")
    data = _mock(name)
    validate_input(data, agent.schema)
    system, user = build_prompt(agent, data)
    assert "{{" not in system
    assert data["home_team"] in system and data["away_team"] in system
    assert "25 words limit" in system  # z config.output.summary_max_words
    assert "match_facts" in system
    assert data["home_team"] in user


def test_close_game_no_outshoot_claim_and_leverage_moments():
    f = _facts(_mock("mock_close"))
    cf = f["five_on_five"]["shot_attempts"]
    assert cf["abs_difference"] == 3
    assert cf["may_claim_one_team_outshot_the_other"] is False
    assert f["five_on_five"]["dominance"]["term_dominance_allowed_for"] == []
    assert f["match"]["decided_in"] == "overtime" and f["match"]["winner"] == "HC Alfa"
    assert f["power_play"]["time_on_ice"] == {"HC Alfa": "4:14", "HC Beta": "2:00"}
    kinds = [(g["time"], g["type"], g["late_game"], g["overtime"]) for g in f["goal_timeline"]]
    assert kinds == [
        ("10:12", "opening goal", False, False),
        ("25:40", "equaliser", False, False),
        ("41:05", "go-ahead goal", False, False),
        ("58:30", "equaliser", True, False),
        ("62:10", "go-ahead goal", False, True),
    ]
    assert f["goal_list_consistent_with_score"] is True
    assert f["goals_outside_5v5_and_power_play"] == {"HC Alfa": 0, "HC Beta": 0}


def test_dominance_allowed_over_thresholds():
    f = _facts(_mock("mock_dominance"))
    assert f["five_on_five"]["shot_attempts"]["team_with_edge"] == "HC Gamma"
    assert f["five_on_five"]["dominance"]["term_dominance_allowed_for"] == ["HC Gamma"]
    assert f["five_on_five"]["finishing"] == {"HC Gamma": -0.9, "HC Delta": -0.8}
    # více času v přesilovce není výkon: pravidlo je v předpočítaných faktech
    assert "NOT a performance indicator" in f["power_play"]["rule"]


def test_threshold_edges():
    data = _mock("mock_close")
    for row in data["metrics_5_on_5"]:
        if row["metric"] == "cf":
            row["HC Alfa"], row["HC Beta"] = 50, 45  # rozdíl přesně 5 => stále bez tvrzení
    assert _facts(data)["five_on_five"]["shot_attempts"]["may_claim_one_team_outshot_the_other"] is False
    for row in data["metrics_5_on_5"]:
        if row["metric"] == "cf":
            row["HC Alfa"], row["HC Beta"] = 51, 45  # rozdíl 6 => smí
    assert _facts(data)["five_on_five"]["shot_attempts"]["team_with_edge"] == "HC Alfa"
    for row in data["metrics_5_on_5"]:
        if row["metric"] == "cf":
            row["HC Alfa"], row["HC Beta"] = 65, 45  # rozdíl přesně 20 => ještě ne dominance
    assert _facts(data)["five_on_five"]["dominance"]["by_shot_attempts"] is None


def test_invalid_score_rejected():
    agent = load_agent("match_analysis")
    data = _mock("mock_close")
    data["final_score"] = "tři dva"
    with pytest.raises(ValueError):
        validate_input(data, agent.schema)


@pytest.mark.skipif(not list(RAW.glob("*")) if RAW.exists() else True, reason="data/raw/match_analysis je prázdné")
@pytest.mark.parametrize("path", sorted(RAW.glob("*")) if RAW.exists() else [], ids=lambda p: p.name)
def test_real_data_is_valid_and_processable(path):
    agent = load_agent("match_analysis")
    data = _load(path)
    validate_input(data, agent.schema)
    f = _facts(data)
    assert f["goal_list_consistent_with_score"] is True
    build_prompt(agent, data)
