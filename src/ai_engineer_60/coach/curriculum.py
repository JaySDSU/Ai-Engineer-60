"""The 60-day AI Engineer curriculum as data. Day 1 = Sun Nov 1, 2026."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

START_DATE = date(2026, 11, 1)


@dataclass(frozen=True)
class Day:
    n: int
    phase: int
    learn: str
    build: str
    gate: bool = False
    light: bool = False

    @property
    def date(self) -> date:
        return START_DATE + timedelta(days=self.n - 1)


PHASES = {
    1: "LLM foundations and API fluency",
    2: "RAG and evals",
    3: "Agents, tool use and MCP",
    4: "Production, LLMOps and ML depth",
    5: "Interview gauntlet",
}

GATES = {
    1: [
        "Explain self-attention on a whiteboard in under 5 minutes without notes",
        "Explain token by token what happens when a model calls a tool",
        "Coach Agent v1 public on GitHub with tests and README",
        "12 of 14 days logged; 10 LeetCode mediums done",
        "Coach quiz score >= 80% on Phase 1 topics",
    ],
    2: [
        "Retrieval recall@5 >= 0.80 on golden set, improvement history documented",
        "Explain why your chunking choice won, with numbers",
        "Design RAG over 10M docs for 1,000 concurrent users in 35 minutes",
        "Evals run in CI",
        "22 LeetCode mediums cumulative; quiz >= 80% on Phase 2",
    ],
    3: [
        "Explain workflow vs agent vs multi-agent with an example of each",
        "Pricing Analyst Agent passes 70%+ of 30 tasks, blocks 10/10 injections",
        "Working MCP server you wrote",
        "Design an airline support agent with refunds in 35 minutes",
        "32 LeetCode mediums cumulative",
    ],
    4: [
        "Live URL with tracing; quote p50 latency and cost/query from memory",
        "Explain LoRA and fine-tune vs RAG vs prompt with your own experiment",
        "20 random classical ML questions at 80%+",
        "Resume rewritten; 30 applications submitted",
    ],
    5: ["Full mock loop: 3/4 or better on every round"],
}

_RAW = [
    # Phase 1
    (1, "Set up repo, uv, ruff, pytest, pre-commit, API keys", "Run Coach Agent; log Day 1"),
    (
        1,
        "Tokenization (BPE), embeddings, token cost",
        "Script: count tokens and cost for 5 prompts",
    ),
    (
        1,
        "Transformer architecture: attention, positional encoding",
        "1-page notes + diagram in your words",
    ),
    (
        1,
        "Pretraining vs instruction tuning vs RLHF; sampling params",
        "Temperature experiment 0 / 0.7 / 1.2",
    ),
    (
        1,
        "Messages API: system prompts, roles, streaming, stop reasons",
        "Coach: streaming responses",
    ),
    (
        1,
        "Structured outputs: JSON schema, Pydantic, retries",
        "Coach: progress log parsed into Pydantic",
    ),
    (1, "Tool calling: tool_use / tool_result loop", "Coach: hand-written agent loop with 3 tools"),
    (
        1,
        "Prompt engineering patterns: examples, XML tags, chaining",
        "Write-up #1: how tool calling works",
    ),
    (1, "Context engineering; prompt caching", "Coach: cache curriculum, measure savings"),
    (
        1,
        "Hallucination causes and mitigations; grounding",
        "Coach: quiz refuses to grade without rubric",
    ),
    (
        1,
        "Async Python: asyncio, semaphores, backoff, rate limits",
        "Coach: parallel question generation",
    ),
    (
        1,
        "Model selection: frontier vs small vs open-weight",
        "Benchmark 3 models: cost/latency/quality",
    ),
    (
        1,
        "Local inference: Ollama, vLLM, quantization",
        "Coach: provider abstraction (Claude or local)",
    ),
    (1, "Testing LLM code: mocks, snapshot tests", "Coach v1 shipped with README, tests, demo"),
    # Phase 2
    (
        2,
        "RAG end to end; RAG vs fine-tuning vs long context",
        "Collect 50-100 public pricing/RM docs",
    ),
    (2, "Document parsing, cleaning, metadata", "Ingestion pipeline"),
    (2, "Chunking: fixed, recursive, semantic, parent-child", "Two chunkers for comparison"),
    (2, "Embeddings, cosine similarity, HNSW/IVF", "Embed into Postgres + pgvector"),
    (2, "Eval design: golden datasets, leakage", "Hand-write 50 Q/A/source triples"),
    (2, "Retrieval metrics: recall@k, MRR, nDCG", "Retrieval eval script + baseline"),
    (2, "Hybrid search (BM25 + vector), RRF, rerankers", "Add hybrid + reranker; record delta"),
    (
        2,
        "Generation evals: faithfulness, LLM-as-judge biases",
        "Judge prompt calibrated on 20 labels",
    ),
    (2, "Citations, grounding, 'I don't know'", "Cited answers + unanswerable-question eval"),
    (2, "Query rewriting, HyDE, multi-query, filters", "Implement one; keep only if evals improve"),
    (2, "Evals in CI: regression gates", "GitHub Action fails on faithfulness drop"),
    (2, "Thanksgiving: light day", "1 h flashcards + review notes"),
    (2, "FastAPI for RAG; streaming endpoints", "/ask endpoint with streaming + sources"),
    (2, "Write the eval scorecard", "Project 2 shipped: README metrics + demo"),
    # Phase 3
    (3, "Agent patterns: ReAct, plan-execute, workflows vs agents", "Pricing Agent design doc"),
    (3, "Synthetic data generation", "Hotel bookings dataset in Postgres"),
    (3, "Text-to-SQL: schema prompting, validation, safety", "Read-only SQL tool with limits"),
    (3, "Tool design: names, descriptions, recoverable errors", "Forecast tool + RAG tool"),
    (3, "Model Context Protocol: servers, tools, resources", "SQL tool as an MCP server"),
    (3, "LangGraph vs Claude Agent SDK vs OpenAI Agents SDK", "Port agent to LangGraph"),
    (3, "Memory: short/long-term, persistence", "Checkpointing + memory"),
    (3, "Agent evals: task success, trajectories, tool accuracy", "30 test tasks; success rate"),
    (3, "Human-in-the-loop: approvals, interrupts", "Approval gate before recommendations"),
    (
        3,
        "Multi-agent: supervisor, handoffs, when not to",
        "Supervisor + 2 subagents vs single, with evals",
    ),
    (3, "Guardrails: prompt injection, permissions, PII", "10-attack injection suite + defenses"),
    (3, "Failure analysis: loops, wrong tool, overflow", "Fix top 3 failures"),
    (3, "Coach upgrade: MCP + scheduled check-ins", "Coach v2 exposes progress via MCP"),
    (3, "Consolidate", "Agent >= 70% task success; README"),
    # Phase 4
    (4, "Containerization, secrets, config", "docker-compose: agent + API + Postgres"),
    (4, "Deployment: Cloud Run / Fly / ECS", "Public URL with auth"),
    (4, "Observability: tracing, Langfuse/LangSmith", "Latency + cost dashboard"),
    (4, "Cost/latency: caching, routing, batching", "Model routing; start applying 5/day"),
    (4, "Angular streaming UI for AI apps (SSE)", "Angular chat UI with tool calls + sources"),
    (4, "Classical ML: bias/variance, metrics, CV, leakage", "30 flashcards + sklearn model"),
    (4, "PyTorch essentials: training loop, loss, optimizers", "Tiny model, explain every line"),
    (4, "Fine-tuning: SFT, LoRA/QLoRA, DPO", "LoRA a small model; compare vs prompting"),
    (4, "Responsible AI: bias, privacy, governance", "Risks section in all READMEs"),
    (4, "Portfolio polish", "3 projects pinned, diagrams, evals, demos"),
    # Phase 5
    (5, "AI system design #1: enterprise RAG search", "Recorded mock + rubric self-score"),
    (5, "Coding mocks: 2 timed mediums out loud", "Recording + mistake list"),
    (5, "Christmas: light day", "1 h flashcards"),
    (5, "Take-home simulation (4 hours)", "Feature with tests + evals in time box"),
    (5, "System design #2, #3: coding agent; fraud explanations", "Two recorded mocks"),
    (5, "Behavioral: 8 STAR stories", "Each under 2.5 minutes"),
    (5, "Project deep-dive drills", "Defend every choice with a number"),
    (5, "Final exam: full mock loop", "FINAL GATE"),
]

_GATE_DAYS = {14, 28, 42, 52, 60}
_LIGHT_DAYS = {26, 55}

CURRICULUM: list[Day] = [
    Day(n=i + 1, phase=p, learn=learn_topic, build=b, gate=(i + 1) in _GATE_DAYS, light=(i + 1) in _LIGHT_DAYS)
    for i, (p, learn_topic, b) in enumerate(_RAW)
]
assert len(CURRICULUM) == 60, len(CURRICULUM)


def day_for(d: date) -> Day | None:
    n = (d - START_DATE).days + 1
    return CURRICULUM[n - 1] if 1 <= n <= 60 else None


def get_day(n: int) -> Day:
    if not 1 <= n <= 60:
        raise ValueError(f"Day must be 1-60, got {n}")
    return CURRICULUM[n - 1]


def topics_through(n: int) -> list[str]:
    """Everything studied up to and including day n — what the quizmaster may ask about."""
    return [d.learn for d in CURRICULUM[: max(0, min(n, 60))] if not d.light]
