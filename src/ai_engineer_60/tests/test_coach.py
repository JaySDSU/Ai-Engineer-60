from datetime import date
from types import SimpleNamespace

import pytest

from ai_engineer_60.coach.agents import Agent, build_tools, run_tool
from ai_engineer_60.coach.curriculum import CURRICULUM, day_for, get_day, topics_through
from ai_engineer_60.coach.store import Store


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "t.db")


def test_curriculum_shape():
    assert len(CURRICULUM) == 60
    assert get_day(1).date == date(2026, 11, 1)
    assert get_day(60).date == date(2026, 12, 30)
    assert get_day(26).light and get_day(26).date == date(2026, 11, 26)  # Thanksgiving
    assert get_day(55).light and get_day(55).date == date(2026, 12, 25)  # Christmas
    assert [d.n for d in CURRICULUM if d.gate] == [14, 28, 42, 52, 60]
    assert day_for(date(2026, 10, 31)) is None


def test_topics_exclude_light_days():
    assert "Thanksgiving: light day" not in topics_through(30)
    assert len(topics_through(3)) == 3


def test_stats_missed_and_streak(store):
    for d in (1, 2, 4, 5):
        store.log_day(d, 3, "x", "y", commit_url="u" if d != 5 else None)
    s = store.stats(today_day=6)  # day 6 in progress, not yet logged
    assert s["missed_days"] == [3]
    assert s["streak"] == 2
    assert s["days_without_commit"] == [5]


def test_log_validation(store):
    with pytest.raises(ValueError):
        store.log_day(61, 3, "x", "y")


def test_run_tool_errors_returned_to_model(store):
    tools = build_tools(store, today=date(2026, 11, 14))
    out, err = run_tool(tools, "get_plan", {})
    assert not err and '"is_gate_day": true' in out
    out, err = run_tool(tools, "log_progress", {"day": 99, "hours": 3, "learned": "a", "built": "b"})
    assert err and "1-60" in out
    _, err = run_tool(tools, "nope", {})
    assert err


class FakeClient:
    """Scripts two turns: model calls get_plan, then answers."""

    def __init__(self):
        self.calls = 0
        self.messages = self

    def create(self, **kw):
        self.calls += 1
        if self.calls == 1:
            return SimpleNamespace(
                stop_reason="tool_use",
                content=[SimpleNamespace(type="tool_use", id="t1", name="get_plan", input={})],
            )
        assert kw["messages"][-1]["content"][0]["type"] == "tool_result"
        return SimpleNamespace(stop_reason="end_turn", content=[SimpleNamespace(type="text", text="Do Day 7.")])


def test_agent_loop(store):
    a = Agent("coach", store, client=FakeClient(), today=date(2026, 11, 7))
    assert a.send("hi") == "Do Day 7."
