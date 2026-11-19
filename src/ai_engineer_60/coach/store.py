"""SQLite persistence for progress logs, quiz scores and mock interviews."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

DEFAULT_DB = Path(os.environ.get("COACH_DB", Path.home() / ".ai_coach" / "progress.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS logs (
    day INTEGER PRIMARY KEY,
    logged_on TEXT NOT NULL,
    learned TEXT NOT NULL,
    built TEXT NOT NULL,
    commit_url TEXT,
    leetcode INTEGER NOT NULL DEFAULT 0,
    blockers TEXT
);
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    taken_on TEXT NOT NULL,
    day INTEGER NOT NULL,
    score REAL NOT NULL,
    weak_topics TEXT
);
CREATE TABLE IF NOT EXISTS interviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    taken_on TEXT NOT NULL,
    kind TEXT NOT NULL,
    score INTEGER NOT NULL,
    feedback TEXT
);
"""


class Store:
    def __init__(self, path: Path | str = DEFAULT_DB):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(SCHEMA)
            self._migrate(c)

    @staticmethod
    def _migrate(c: sqlite3.Connection) -> None:
        """Drop the old `hours` column from databases created before hours tracking was removed."""
        cols = {row["name"] for row in c.execute("PRAGMA table_info(logs)")}
        if "hours" in cols:
            c.execute("ALTER TABLE logs DROP COLUMN hours")

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    # ---- writes
    def log_day(
        self,
        day: int,
        learned: str,
        built: str,
        commit_url: str | None = None,
        leetcode: int = 0,
        blockers: str | None = None,
    ) -> None:
        if not 1 <= day <= 60:
            raise ValueError("day must be 1-60")
        with self._conn() as c:
            c.execute(
                "INSERT OR REPLACE INTO logs (day, logged_on, learned, built, commit_url, leetcode, blockers) "
                "VALUES (?,?,?,?,?,?,?)",
                (
                    day,
                    date.today().isoformat(),
                    learned,
                    built,
                    commit_url,
                    leetcode,
                    blockers,
                ),
            )

    def record_quiz(self, day: int, score: float, weak_topics: str = "") -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO quizzes (taken_on, day, score, weak_topics) VALUES (?,?,?,?)",
                (date.today().isoformat(), day, score, weak_topics),
            )

    def record_interview(self, kind: str, score: int, feedback: str) -> None:
        with self._conn() as c:
            c.execute(
                "INSERT INTO interviews (taken_on, kind, score, feedback) VALUES (?,?,?,?)",
                (date.today().isoformat(), kind, score, feedback),
            )

    # ---- reads
    def logs(self) -> list[dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM logs ORDER BY day")]

    def stats(self, today_day: int) -> dict:
        logs = self.logs()
        logged = {log["day"] for log in logs}
        due = list(range(1, max(0, min(today_day, 60)) + 1))
        # a day counts as missed only once it's fully past
        missed = [d for d in due[:-1] if d not in logged] if due else []
        with self._conn() as c:
            q = c.execute("SELECT AVG(score) a, COUNT(*) n FROM quizzes").fetchone()
            weak = [
                r["weak_topics"]
                for r in c.execute("SELECT weak_topics FROM quizzes WHERE weak_topics != '' ORDER BY id DESC LIMIT 5")
            ]
            iv = [dict(r) for r in c.execute("SELECT kind, score, taken_on FROM interviews ORDER BY id DESC LIMIT 5")]
        streak = 0
        for d in range(min(today_day, 60), 0, -1):
            if d in logged:
                streak += 1
            elif d == today_day:
                continue  # today not logged yet doesn't break the streak
            else:
                break
        return {
            "days_logged": len(logged),
            "days_due": len(due),
            "missed_days": missed,
            "streak": streak,
            "leetcode_total": sum(log["leetcode"] for log in logs),
            "days_without_commit": [log["day"] for log in logs if not log["commit_url"]],
            "quiz_avg": round(q["a"], 1) if q["a"] is not None else None,
            "quizzes_taken": q["n"],
            "recent_weak_topics": weak,
            "recent_interviews": iv,
        }
