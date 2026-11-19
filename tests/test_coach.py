import csv
import sqlite3
from datetime import date
from importlib.resources import files
from types import SimpleNamespace

import pytest

from ai_engineer_60.coach import cli
from ai_engineer_60.coach.agents import Agent, build_tools, current_day_number, run_tool
from ai_engineer_60.coach.curriculum import CURRICULUM, PHASES, day_for, get_day, topics_through
from ai_engineer_60.coach.store import Store


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "t.db")


def test_curriculum_shape():
    assert len(CURRICULUM) == 60
    assert get_day(1).date == date(2026, 11, 18)
    assert get_day(60).date == date(2027, 1, 16)
    assert get_day(9).light and get_day(9).date == date(2026, 11, 26)  # Thanksgiving
    assert get_day(38).light and get_day(38).date == date(2026, 12, 25)  # Christmas
    assert [d.n for d in CURRICULUM if d.light] == [9, 38]
    assert [d.n for d in CURRICULUM if d.gate] == [14, 28, 42, 53, 60]
    assert day_for(date(2026, 11, 17)) is None
    assert day_for(date(2027, 1, 17)) is None


def test_gate_days_close_their_phase():
    for n in (14, 28, 42, 53):
        assert get_day(n).phase != get_day(n + 1).phase
    assert {d.phase for d in CURRICULUM} == set(PHASES)


def test_current_day_number_bounds():
    assert current_day_number(date(2026, 11, 17)) == 0
    assert current_day_number(date(2026, 11, 18)) == 1
    assert current_day_number(date(2027, 1, 16)) == 60


def test_topics_exclude_light_days():
    assert "Thanksgiving: light day" not in topics_through(30)
    assert len(topics_through(3)) == 3
    assert len(topics_through(10)) == 9  # Day 9 is light


def test_stats_missed_and_streak(store):
    for d in (1, 2, 4, 5):
        store.log_day(d, "x", "y", commit_url="u" if d != 5 else None)
    s = store.stats(today_day=6)  # day 6 in progress, not yet logged
    assert s["missed_days"] == [3]
    assert s["streak"] == 2
    assert s["days_without_commit"] == [5]


def test_log_validation(store):
    with pytest.raises(ValueError):
        store.log_day(61, "x", "y")


def test_run_tool_errors_returned_to_model(store):
    tools = build_tools(store, today=date(2026, 12, 1))  # Day 14 = Gate 1
    out, err = run_tool(tools, "get_plan", {})
    assert not err and '"is_gate_day": true' in out
    out, err = run_tool(tools, "log_progress", {"day": 99, "learned": "a", "built": "b"})
    assert err and "1-60" in out
    _, err = run_tool(tools, "nope", {})
    assert err


def test_get_plan_before_start(store):
    tools = build_tools(store, today=date(2026, 11, 17))
    out, err = run_tool(tools, "get_plan", {})
    assert not err and "not_started" in out and "2026-11-18" in out


def test_run_tool_never_raises(store):
    tools = build_tools(store, today=date(2026, 11, 18))
    out, err = run_tool(tools, "get_plan", {"bogus": 1})  # extra arg -> TypeError
    assert err and "bad arguments for get_plan" in out
    out, err = run_tool(tools, "nope", {})
    assert err and "available_tools" in out

    def boom() -> dict:
        raise sqlite3.OperationalError("database is locked")

    tools["get_progress"].fn = boom
    out, err = run_tool(tools, "get_progress", {})
    assert err and "OperationalError" in out and "database is locked" in out


def test_plan_csv_matches_curriculum():
    """plan.csv is an export of CURRICULUM; fail if the two ever drift apart."""
    text = files("ai_engineer_60.coach").joinpath("plan.csv").read_text(encoding="utf-8")
    rows = list(csv.DictReader(text.splitlines()))
    assert len(rows) == 60
    for row, d in zip(rows, CURRICULUM, strict=True):
        assert (int(row["day"]), row["date"], row["learn"], row["build"]) == (d.n, d.date.isoformat(), d.learn, d.build)
        assert (row["tag"] == "LIGHT") == d.light
        assert ("GATE" in row["tag"]) == d.gate


def test_store_migrates_old_hours_column(tmp_path):
    db = tmp_path / "old.db"
    with sqlite3.connect(db) as c:
        c.execute(
            "CREATE TABLE logs (day INTEGER PRIMARY KEY, logged_on TEXT NOT NULL, hours REAL NOT NULL, "
            "learned TEXT NOT NULL, built TEXT NOT NULL, commit_url TEXT, leetcode INTEGER NOT NULL DEFAULT 0, blockers TEXT)"
        )
        c.execute("INSERT INTO logs VALUES (1, '2026-11-18', 3, 'uv', 'repo', 'u', 5, NULL)")
    s = Store(db)
    s.log_day(2, "bpe", "token script", commit_url="u2", leetcode=1)
    assert [(r["day"], r["leetcode"]) for r in s.logs()] == [(1, 5), (2, 1)]
    assert "hours" not in s.logs()[0]


def test_cli_chat_without_api_key_exits_cleanly(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("COACH_DB", str(tmp_path / "c.db"))
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "load_dotenv", lambda *a, **k: False)  # never read the real .env in tests
    monkeypatch.setattr(cli, "Store", lambda: Store(tmp_path / "c.db"))

    def no_network(*a, **k):
        raise AssertionError("chat() must not start without an API key")

    monkeypatch.setattr(cli, "chat", no_network)
    assert cli.main(["checkin"]) == 2
    assert "ANTHROPIC_API_KEY is not set" in capsys.readouterr().err


def test_model_read_from_env_at_call_time(monkeypatch, store):
    monkeypatch.setenv("COACH_MODEL", "my-model")
    assert Agent("coach", store, client=FakeClient()).model == "my-model"


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
    a = Agent("coach", store, client=FakeClient(), today=date(2026, 11, 24))  # Day 7
    assert a.send("hi") == "Do Day 7."
