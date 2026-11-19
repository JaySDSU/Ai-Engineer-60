"""Three coaching agents built on a hand-written tool-use loop (no frameworks — that's the point).

- Coach:       daily accountability. Knows the plan, reads your logs, calls out slippage.
- Quizmaster:  strict oral exam on everything covered so far; grades and records scores.
- Interviewer: mock AI-engineer interview rounds scored on a 1-4 hiring rubric.
"""

from __future__ import annotations

import json
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .curriculum import GATES, PHASES, START_DATE, day_for, get_day, topics_through
from .store import Store

log = logging.getLogger(__name__)

DEFAULT_MODEL = "claude-sonnet-5-5"  # override with COACH_MODEL in .env


def model_name() -> str:
    """Read at call time (not import time) so values loaded from .env by the CLI are picked up."""
    return os.environ.get("COACH_MODEL") or DEFAULT_MODEL


MAX_TOOL_ROUNDS = 8


def current_day_number(today: date | None = None) -> int:
    d = day_for(today or date.today())
    if d:
        return d.n
    return 0 if (today or date.today()) < START_DATE else 60


# ------------------------------------------------------------------ tools
@dataclass
class Tool:
    name: str
    description: str
    schema: dict
    fn: Callable[..., Any]

    def spec(self) -> dict:
        return {"name": self.name, "description": self.description, "input_schema": self.schema}


def build_tools(store: Store, today: date | None = None) -> dict[str, Tool]:
    def get_plan(day: int | None = None) -> dict:
        n = day or current_day_number(today)
        if n == 0:
            return {
                "status": "not_started",
                "message": f"Program starts {START_DATE:%a %b %d, %Y}.",
                "start_date": START_DATE.isoformat(),
            }
        d = get_day(n)
        out = {
            "day": d.n,
            "date": d.date.isoformat(),
            "phase": f"{d.phase}: {PHASES[d.phase]}",
            "learn": d.learn,
            "build": d.build,
            "is_gate_day": d.gate,
            "is_light_day": d.light,
        }
        if d.gate:
            out["gate_criteria"] = GATES[d.phase]
        return out

    def get_progress() -> dict:
        return store.stats(current_day_number(today))

    def log_progress(
        day: int,
        learned: str,
        built: str,
        commit_url: str = "",
        leetcode: int = 0,
        blockers: str = "",
    ) -> dict:
        store.log_day(day, learned, built, commit_url or None, leetcode, blockers or None)
        return {"ok": True, "logged_day": day}

    def get_quiz_topics(through_day: int | None = None) -> dict:
        n = through_day or current_day_number(today)
        return {"through_day": n, "topics": topics_through(n)}

    def record_quiz(score: float, weak_topics: str = "") -> dict:
        store.record_quiz(current_day_number(today), score, weak_topics)
        return {"ok": True}

    def record_interview(kind: str, score: int, feedback: str) -> dict:
        if score not in (1, 2, 3, 4):
            return {"error": "score must be 1-4"}
        store.record_interview(kind, score, feedback)
        return {"ok": True}

    tools = [
        Tool(
            "get_plan",
            "Get the curriculum entry for a day (default: today). Includes gate criteria on gate days.",
            {
                "type": "object",
                "properties": {"day": {"type": "integer", "minimum": 1, "maximum": 60}},
            },
            get_plan,
        ),
        Tool(
            "get_progress",
            "Get the student's progress stats: days logged, missed days, streak, "
            "LeetCode count, days logged without a commit, quiz average, weak topics, recent mock interviews.",
            {"type": "object", "properties": {}},
            get_progress,
        ),
        Tool(
            "log_progress",
            "Save the student's log for a day. Only call after the student has given "
            "what they learned and what they built. Ask for a commit URL; record empty if they have none.",
            {
                "type": "object",
                "properties": {
                    "day": {"type": "integer", "minimum": 1, "maximum": 60},
                    "learned": {"type": "string"},
                    "built": {"type": "string"},
                    "commit_url": {"type": "string"},
                    "leetcode": {"type": "integer", "minimum": 0},
                    "blockers": {"type": "string"},
                },
                "required": ["day", "learned", "built"],
            },
            log_progress,
        ),
        Tool(
            "get_quiz_topics",
            "List every topic covered so far — the only topics you may quiz on.",
            {"type": "object", "properties": {"through_day": {"type": "integer"}}},
            get_quiz_topics,
        ),
        Tool(
            "record_quiz",
            "Record the final quiz score (0-100) and a comma-separated list of weak topics.",
            {
                "type": "object",
                "properties": {
                    "score": {"type": "number", "minimum": 0, "maximum": 100},
                    "weak_topics": {"type": "string"},
                },
                "required": ["score"],
            },
            record_quiz,
        ),
        Tool(
            "record_interview",
            "Record a finished mock interview: kind (system_design, llm_concepts, coding, "
            "behavioral, project_deep_dive), score 1-4, and written feedback.",
            {
                "type": "object",
                "properties": {
                    "kind": {"type": "string"},
                    "score": {"type": "integer", "minimum": 1, "maximum": 4},
                    "feedback": {"type": "string"},
                },
                "required": ["kind", "score", "feedback"],
            },
            record_interview,
        ),
    ]
    return {t.name: t for t in tools}


def run_tool(tools: dict[str, Tool], name: str, args: dict) -> tuple[str, bool]:
    """Execute a tool; return (json_result, is_error).

    Every failure becomes an is_error tool_result so the model can recover (retry with fixed args,
    pick another tool, or tell the user). The agent loop itself must never crash because a tool did.
    """
    tool = tools.get(name)
    if tool is None:
        return json.dumps({"error": f"unknown tool {name!r}", "available_tools": sorted(tools)}), True
    try:
        result = tool.fn(**args)
    except TypeError as e:  # wrong / missing / extra arguments from the model
        return json.dumps({"error": f"bad arguments for {name}: {e}"}), True
    except ValueError as e:  # our own validation (e.g. day out of range)
        return json.dumps({"error": str(e)}), True
    except Exception as e:  # anything else (sqlite3.Error, OSError, bugs): report, don't crash
        log.exception("tool %s failed", name)
        return json.dumps({"error": f"{name} failed: {type(e).__name__}: {e}"}), True
    try:
        return json.dumps(result, default=str), False
    except (TypeError, ValueError) as e:  # result not JSON-serialisable
        return json.dumps({"error": f"{name} returned unserialisable output: {e}"}), True


# ------------------------------------------------------------------ personas
STRICT = """You are a strict, demanding but fair coach preparing a software engineer (MS CS, ~5 years at
Revenue Analytics, strong in Python and Angular) to become interview-ready as an AI Engineer by January 2027.
You do not accept vague answers or excuses. Praise only what is earned, specifically. Be concise.
Always ground claims about their progress in tool results, never guess. Today's date: {today}."""

PERSONAS = {
    "coach": STRICT
    + """
ROLE: Daily accountability coach.
1. Call get_plan and get_progress first.
2. State today's assignment in 3 lines. If it's a gate day, list the gate criteria as pass/fail checks.
3. Call out every missed day and every logged day without a commit. Missed days must be made up within 72 hours:
   assign the concrete make-up task.
4. If the student wants to log, collect learned, built, commit URL, LeetCode count, blockers, then call
   log_progress. If 'learned' is vague ("read about RAG"), make them restate it as something they can explain.
5. End with the top 3 tasks for the next session.""",
    "quiz": STRICT
    + """
ROLE: Quizmaster.
1. Call get_quiz_topics and get_progress. Weight questions toward recent_weak_topics.
2. Ask ONE question at a time, 8 questions total, mixing conceptual ("why"), applied ("what would you do"),
   and numbers ("what recall@k means"). Interview difficulty, not trivia.
3. Grade each answer 0-10 with a one-line correction. Partial credit only for precise partial answers.
4. After question 8, give the score out of 100, weak topics, and call record_quiz.""",
    "interview": STRICT
    + """
ROLE: Interviewer at a top AI company running one 45-minute round. Ask the student which round:
system_design (LLM/RAG/agent system), llm_concepts, project_deep_dive, or behavioral.
Behave like a real interviewer: open with the prompt, push back on hand-waving, ask about evals, failure modes,
cost, latency, scaling. Do not teach during the round. When the student says "done" (or after ~12 exchanges),
score 1-4 (1 strong no hire, 2 no hire, 3 hire, 4 strong hire) with specific evidence, list 3 things to fix,
and call record_interview.""",
}


# ------------------------------------------------------------------ agent loop
@dataclass
class Agent:
    persona: str
    store: Store
    client: Any = None
    today: date | None = None
    messages: list[dict] = field(default_factory=list)
    model: str | None = None

    def __post_init__(self):
        self.model = self.model or model_name()
        if self.client is None:
            import anthropic  # imported lazily so tests run without the SDK

            self.client = anthropic.Anthropic()
        self.tools = build_tools(self.store, self.today)
        self.system = PERSONAS[self.persona].format(today=(self.today or date.today()).isoformat())

    def send(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        for _ in range(MAX_TOOL_ROUNDS):
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                # cache the stable prefix (system + tools): Day 9 lesson in action
                system=[{"type": "text", "text": self.system, "cache_control": {"type": "ephemeral"}}],
                tools=[t.spec() for t in self.tools.values()],
                messages=self.messages,
            )
            self.messages.append({"role": "assistant", "content": resp.content})
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text")
            results = []
            for block in resp.content:
                if block.type == "tool_use":
                    out, is_err = run_tool(self.tools, block.name, block.input)
                    results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": out,
                            "is_error": is_err,
                        }
                    )
            self.messages.append({"role": "user", "content": results})
        return "[stopped: too many tool rounds]"
