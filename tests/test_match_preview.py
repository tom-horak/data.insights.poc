import json
from pathlib import Path

import pytest

from di.loader import build_prompt, load_agent, run_preprocessors
from di.runner import find_inputs, run_dir
from di.validate import validate_input

ROOT = Path(__file__).parents[1]
EXAMPLES = ROOT / "agents/match_preview/examples"
RAW = ROOT / "data/raw/match_preview"  # reálná data, gitignored


def _data(name: str) -> dict:
    return json.loads((EXAMPLES / f"{name}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["mock_alert", "mock_no_alert"])
def test_mock_validates_and_prompt_builds(name):
    agent = load_agent("match_preview")
    data = _data(name)
    validate_input(data, agent.schema)
    system, user = build_prompt(agent, data)
    assert "{{" not in system
    assert data["team_name"] in system and data["opp_name"] in system
    assert "14týmové" in system
    assert data["team_name"] in user


def test_alert_active_for_close_teams():
    # 4. (28 b.) vs 5. (26 b.): přímý souboj + hájení TOP 4
    alert = run_preprocessors(load_agent("match_preview"), _data("mock_alert"))["standings_alert"]
    assert alert["active"]
    assert {r["type"] for r in alert["reasons"]} == {"direct_match", "top4"}


def test_alert_inactive_for_distant_teams():
    alert = run_preprocessors(load_agent("match_preview"), _data("mock_no_alert"))["standings_alert"]
    assert not alert["active"]
    assert alert["reasons"] == []


def test_invalid_input_rejected():
    agent = load_agent("match_preview")
    data = _data("mock_alert")
    del data["opp_name"]
    with pytest.raises(ValueError):
        validate_input(data, agent.schema)


def test_find_inputs_picks_json_and_txt(tmp_path):
    (tmp_path / "a.json").write_text("{}")
    (tmp_path / "b.txt").write_text("{}")
    (tmp_path / "c.md").write_text("x")
    assert [p.name for p in find_inputs(tmp_path)] == ["a.json", "b.txt"]


def test_run_dir_dry_run_continues_after_error(tmp_path):
    (tmp_path / "ok.json").write_text((EXAMPLES / "mock_alert.json").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "bad.json").write_text("{}", encoding="utf-8")
    logs: list[str] = []
    res = run_dir("match_preview", tmp_path, tmp_path / "out", dry_run=True, log=logs.append)
    assert [p.name for p in res.ok] == ["ok.json"]
    assert [p.name for p, _ in res.failed] == ["bad.json"]


def test_run_dir_empty_folder_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_dir("match_preview", tmp_path, tmp_path / "out", dry_run=True)


# Reálná data: spustí se jen pokud jsou ve složce data/raw (lokálně), jinak se přeskočí.
@pytest.mark.skipif(not find_inputs(RAW), reason="data/raw/match_preview je prázdné")
@pytest.mark.parametrize("path", find_inputs(RAW), ids=lambda p: p.name)
def test_real_data_is_valid_and_processable(path):
    agent = load_agent("match_preview")
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_input(data, agent.schema)
    build_prompt(agent, data)
