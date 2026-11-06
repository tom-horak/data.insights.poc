import json
from pathlib import Path

from di.loader import build_prompt, load_agent
from di.validate import validate_input

SAMPLE = Path(__file__).parents[1] / "agents/match_preview/examples/sample_input.json"


def _data():
    return json.loads(SAMPLE.read_text(encoding="utf-8"))


def test_sample_validates_and_prompt_builds():
    agent = load_agent("match_preview")
    data = _data()
    validate_input(data, agent.schema)
    system, user = build_prompt(agent, data)
    assert "{{" not in system
    assert "Tým A" in system and "Tým B" in system
    assert "14týmové" in system


def test_alert_direct_match_and_top4():
    agent = load_agent("match_preview")
    from di.loader import run_preprocessors

    alert = run_preprocessors(agent, _data())["standings_alert"]
    types = {r["type"] for r in alert["reasons"]}
    assert alert["active"]
    assert {"direct_match", "top4"} <= types  # A (55 b.) vs B (54 b.), 4. místo
