# AI Engineer Course & Roadmap

A hands-on, 60-day learning plan to build practical AI engineering skills, ship portfolio projects, and prepare for AI Engineer interviews.

**Plan dates:** November 18, 2026 – January 16, 2027  
**Duration:** 60 days  
**Approach:** Learn a concept, implement it, test it, document it, and explain the trade-offs.

> **Core principle:** Build working systems rather than only watching tutorials. Every learning day should produce code, notes, an experiment, an evaluation, or a portfolio artifact.

---

## Table of Contents

- [Goals](#goals)
- [How to Use This Roadmap](#how-to-use-this-roadmap)
- [Projects](#projects)
- [Daily Roadmap](#daily-roadmap)
- [Milestone Gates](#milestone-gates)
- [Suggested Repository Structure](#suggested-repository-structure)
- [Definition of Done](#definition-of-done)
- [Progress Tracker](#progress-tracker)
- [Final Readiness Checklist](#final-readiness-checklist)

---

## Goals

By the end of this plan, aim to be able to:

1. Explain how modern LLMs work, including tokenization, embeddings, transformers, attention, and model training approaches.
2. Build reliable LLM applications with structured outputs, streaming, tool calling, prompt/context engineering, and provider abstraction.
3. Design, implement, and evaluate production-style RAG systems.
4. Build tool-using agents and understand agent frameworks, MCP, memory, human approval, and multi-agent trade-offs.
5. Deploy and operate an AI application with authentication, observability, cost controls, and a usable interface.
6. Demonstrate core ML and fine-tuning knowledge.
7. Present a portfolio and explain engineering decisions with measurable evidence.
8. Prepare for coding, AI system design, take-home, and behavioral interviews.

---

## How to Use This Roadmap

For each day:

1. **Learn:** Study the topic listed in the roadmap.
2. **Build:** Complete the practical deliverable. Prefer a small working implementation over passive reading.
3. **Test:** Add tests or run an experiment. Record what worked and what failed.
4. **Explain:** Write a short explanation in your own words. Be able to describe the design and trade-offs without reading your notes.
5. **Commit:** Commit the day's work to Git and update this README.

Suggested daily study structure (adjust to your schedule):

- 25% — reading and concept learning
- 60% — implementation and experimentation
- 15% — testing, notes, and review

If a day is missed, continue from the unfinished task rather than skipping the concept. The milestone gates are checkpoints, not just dates.

### Daily log template

Copy this into a daily journal or project notes:

```md
## Day N — YYYY-MM-DD

### What I learned
- 

### What I built
- 

### Tests / experiments
- 

### Results and observations
- 

### Questions / gaps to revisit
- 

### Commit / PR
- 

### Can I explain this without notes?
- [ ] Yes
- [ ] Not yet
```

---

## Projects

The roadmap develops three main portfolio projects, plus supporting experiments.

### Project 1 — AI Learning Coach

Build an AI coach that helps manage a learning curriculum, track progress, and quiz the learner.

Planned capabilities:
- Stream model responses.
- Parse progress logs into validated Pydantic models.
- Use a hand-written agent loop with three tools.
- Cache curriculum context and measure savings.
- Refuse to grade a quiz without a rubric.
- Abstract the model provider so the app can use Claude or a local model.
- Include tests, a README, and a demo.

**Target milestone:** Day 14 — Coach v1 shipped.

### Project 2 — Evaluated RAG Application

Build a retrieval-augmented generation application using public pricing/revenue-management documents.

Planned capabilities:
- Ingest and clean documents with metadata.
- Compare at least two chunking strategies.
- Generate embeddings and store them in PostgreSQL with pgvector.
- Build a hand-labeled evaluation set of 50 question/answer/source examples.
- Measure retrieval with recall@k, MRR, and nDCG.
- Compare vector search with hybrid search and reranking.
- Evaluate faithfulness and unanswerable questions.
- Return cited answers and support streaming through a FastAPI endpoint.
- Run evaluation checks in CI.

**Target milestone:** Day 28 — Project 2 shipped with README, metrics, and demo.

### Project 3 — Hotel Pricing Agent

Build an agent that can use hotel-related data and tools to answer questions and support pricing workflows.

Planned capabilities:
- Design an agent using ReAct, plan-execute, or workflow patterns.
- Create a synthetic hotel bookings dataset in PostgreSQL.
- Provide safe, read-only Text-to-SQL access with limits.
- Add forecast and RAG tools.
- Expose a SQL tool through an MCP server.
- Compare agent frameworks and port the agent to LangGraph.
- Add checkpointing, memory, task evaluations, human approval, and (if justified by evaluations) multi-agent orchestration.
- Test prompt-injection defenses, permissions, and PII handling.
- Track task success and fix the most common failure modes.

**Target milestone:** Day 42 — Agent achieves at least 70% task success and has a README.

---

## Daily Roadmap

The schedule below follows the supplied 60-day plan.

### Phase 1 — LLM Foundations and AI Application Engineering

| Day | Date | Learn | Build / Deliverable |
|---:|---|---|---|
| 1 | 2026-11-18 | Set up repo, uv, ruff, pytest, pre-commit, API keys | Run Coach Agent; log Day 1 |
| 2 | 2026-11-19 | Tokenization (BPE), embeddings, token cost | Script: count tokens and cost for 5 prompts |
| 3 | 2026-11-20 | Transformer architecture: attention, positional encoding | 1-page notes + diagram in your words |
| 4 | 2026-11-21 | Pretraining vs instruction tuning vs RLHF; sampling params | Temperature experiment 0 / 0.7 / 1.2 |
| 5 | 2026-11-22 | Messages API: system prompts, roles, streaming, stop reasons | Coach: streaming responses |
| 6 | 2026-11-23 | Structured outputs: JSON schema, Pydantic, retries | Coach: progress log parsed into Pydantic |
| 7 | 2026-11-24 | Tool calling: tool_use / tool_result loop | Coach: hand-written agent loop with 3 tools |
| 8 | 2026-11-25 | Prompt engineering patterns: examples, XML tags, chaining | Write-up #1: how tool calling works |
| 9 | 2026-11-26 | Context engineering; prompt caching | Coach: cache curriculum, measure savings |
| 10 | 2026-11-27 | Hallucination causes and mitigations; grounding | Coach: quiz refuses to grade without rubric |
| 11 | 2026-11-28 | Thanksgiving: light day | 1 h flashcards + review notes |
| 12 | 2026-11-29 | Model selection: frontier vs small vs open-weight | Benchmark 3 models: cost/latency/quality |
| 13 | 2026-11-30 | Local inference: Ollama, vLLM, quantization | Coach: provider abstraction (Claude or local) |
| 14 | 2026-12-01 | **Gate 1: Testing LLM code: mocks, snapshot tests** | Coach v1 shipped with README, tests, demo |

### Phase 2 — Retrieval-Augmented Generation (RAG)

| Day | Date | Learn | Build / Deliverable |
|---:|---|---|---|
| 15 | 2026-12-02 | RAG end to end; RAG vs fine-tuning vs long context | Collect 50–100 public pricing/RM docs |
| 16 | 2026-12-03 | Document parsing, cleaning, metadata | Ingestion pipeline |
| 17 | 2026-12-04 | Chunking: fixed, recursive, semantic, parent-child | Two chunkers for comparison |
| 18 | 2026-12-05 | Async Python: asyncio, semaphores, backoff, rate limits | Coach: parallel question generation |
| 19 | 2026-12-06 | Embeddings, cosine similarity, HNSW/IVF | Embed into Postgres + pgvector |
| 20 | 2026-12-07 | Eval design: golden datasets, leakage | Hand-write 50 Q/A/source triples |
| 21 | 2026-12-08 | Retrieval metrics: recall@k, MRR, nDCG | Retrieval eval script + baseline |
| 22 | 2026-12-09 | Hybrid search (BM25 + vector), RRF, rerankers | Add hybrid + reranker; record delta |
| 23 | 2026-12-10 | Generation evals: faithfulness, LLM-as-judge biases | Judge prompt calibrated on 20 labels |
| 24 | 2026-12-11 | Citations, grounding, 'I don't know' | Cited answers + unanswerable-question eval |
| 25 | 2026-12-12 | Query rewriting, HyDE, multi-query, filters | Implement one; keep only if evals improve |
| 26 | 2026-12-13 | Evals in CI: regression gates | GitHub Action fails on faithfulness drop |
| 27 | 2026-12-14 | FastAPI for RAG; streaming endpoints | `/ask` endpoint with streaming + sources |
| 28 | 2026-12-15 | **Gate 2: Write the eval scorecard** | Project 2 shipped: README metrics + demo |

### Phase 3 — Agents, Tools, and MCP

| Day | Date | Learn | Build / Deliverable |
|---:|---|---|---|
| 29 | 2026-12-16 | Agent patterns: ReAct, plan-execute, workflows vs agents | Pricing Agent design doc |
| 30 | 2026-12-17 | Synthetic data generation | Hotel bookings dataset in Postgres |
| 31 | 2026-12-18 | Text-to-SQL: schema prompting, validation, safety | Read-only SQL tool with limits |
| 32 | 2026-12-19 | Tool design: names, descriptions, recoverable errors | Forecast tool + RAG tool |
| 33 | 2026-12-20 | Model Context Protocol: servers, tools, resources | SQL tool as an MCP server |
| 34 | 2026-12-21 | LangGraph vs Claude Agent SDK vs OpenAI Agents SDK | Port agent to LangGraph |
| 35 | 2026-12-22 | Memory: short/long-term, persistence | Checkpointing + memory |
| 36 | 2026-12-23 | Agent evals: task success, trajectories, tool accuracy | 30 test tasks; success rate |
| 37 | 2026-12-24 | Human-in-the-loop: approvals, interrupts | Approval gate before recommendations |
| 38 | 2026-12-25 | Multi-agent: supervisor, handoffs, when not to | Supervisor + 2 subagents vs single, with evals |
| 39 | 2026-12-26 | Guardrails: prompt injection, permissions, PII | 10-attack injection suite + defenses |
| 40 | 2026-12-27 | Christmas: light day | 1 h flashcards |
| 41 | 2026-12-28 | Failure analysis: loops, wrong tool, overflow | Fix top 3 failures |
| 42 | 2026-12-29 | **Gate 3: Consolidate** | Agent ≥70% task success; README |

### Phase 4 — Deployment, Operations, ML, and Fine-Tuning

| Day | Date | Learn | Build / Deliverable |
|---:|---|---|---|
| 43 | 2026-12-30 | Containerization, secrets, config | docker-compose: agent + API + Postgres |
| 44 | 2026-12-31 | Deployment: Cloud Run / Fly / ECS | Public URL with auth |
| 45 | 2027-01-01 | Observability: tracing, Langfuse/LangSmith | Latency + cost dashboard |
| 46 | 2027-01-02 | Cost/latency: caching, routing, batching | Model routing; start applying 5/day |
| 47 | 2027-01-03 | Coach upgrade: MCP + scheduled check-ins | Coach v2 exposes progress via MCP |
| 48 | 2027-01-04 | Angular streaming UI for AI apps (SSE) | Angular chat UI with tool calls + sources |
| 49 | 2027-01-05 | Classical ML: bias/variance, metrics, CV, leakage | 30 flashcards + sklearn model |
| 50 | 2027-01-06 | PyTorch essentials: training loop, loss, optimizers | Tiny model, explain every line |
| 51 | 2027-01-07 | Fine-tuning: SFT, LoRA/QLoRA, DPO | LoRA a small model; compare vs prompting |
| 52 | 2027-01-08 | Responsible AI: bias, privacy, governance | Risks section in all READMEs |
| 53 | 2027-01-09 | **Gate 4: Portfolio polish** | 3 projects pinned, diagrams, evals, demos |

### Phase 5 — Interview Preparation and Final Assessment

| Day | Date | Learn | Build / Deliverable |
|---:|---|---|---|
| 54 | 2027-01-10 | AI system design #1: enterprise RAG search | Recorded mock + rubric self-score |
| 55 | 2027-01-11 | Coding mocks: 2 timed mediums out loud | Recording + mistake list |
| 56 | 2027-01-12 | Take-home simulation (4 hours) | Feature with tests + evals in time box |
| 57 | 2027-01-13 | System design #2, #3: coding agent; fraud explanations | Two recorded mocks |
| 58 | 2027-01-14 | Behavioral: 8 STAR stories | Each under 2.5 minutes |
| 59 | 2027-01-15 | Project deep-dive drills | Defend every choice with a number |
| 60 | 2027-01-16 | **Final Gate: full mock loop** | Score 3/4+ on every round |

---

## Milestone Gates

Use these checkpoints to decide whether to move forward. If a gate is not met, spend additional time closing the gap.

| Gate | Target date | Exit criteria |
|---|---|---|
| Gate 1 — AI Coach v1 | 2026-12-01 | Working Coach with README, tests, and demo; LLM code tested with mocks/snapshots |
| Gate 2 — RAG project | 2026-12-15 | RAG application shipped with evaluation scorecard, metrics, README, and demo |
| Gate 3 — Pricing Agent | 2026-12-29 | Agent reaches at least 70% task success; failure analysis documented |
| Gate 4 — Portfolio | 2027-01-09 | Three pinned projects, diagrams, evaluations, and demos |
| Final Gate — Interview readiness | 2027-01-16 | Score at least 3/4 in every round of the full mock loop |

---

## Suggested Repository Structure

One possible structure for organizing the work:

```text
ai-engineer-course/
├── README.md
├── notes/
│   ├── llm-foundations/
│   ├── rag/
│   ├── agents/
│   ├── ml-and-fine-tuning/
│   └── interview-prep/
├── experiments/
│   ├── token-cost/
│   ├── model-benchmarks/
│   ├── chunking-comparison/
│   └── fine-tuning/
├── projects/
│   ├── ai-learning-coach/
│   ├── evaluated-rag/
│   └── hotel-pricing-agent/
├── evaluations/
│   ├── rag/
│   └── agents/
└── interview/
    ├── coding/
    ├── system-design/
    └── behavioral/
```

This is a suggested organization, not a required structure. Each project can also live in its own repository.

---

## Definition of Done

A topic is not complete just because the material was read. Mark it complete when you can:

- [ ] Explain the concept in plain language.
- [ ] Implement a small example without blindly copying a tutorial.
- [ ] Test normal cases and at least one failure or edge case.
- [ ] Explain the main trade-offs and alternatives.
- [ ] Record useful results, metrics, or observations.
- [ ] Commit the work and update relevant documentation.

For AI features, also ask:

- [ ] What happens when the model returns invalid or incomplete output?
- [ ] What happens when a tool fails or times out?
- [ ] How are cost and latency measured?
- [ ] How do I evaluate answer quality or task success?
- [ ] What data is sent to the model, and could it contain sensitive information?
- [ ] Can the system safely say “I don't know” or ask for human approval?

---

## Progress Tracker

Update this section as you work through the course.

- [ ] Days 1–14: LLM foundations and AI Learning Coach
- [ ] Days 15–28: RAG application and evaluation
- [ ] Days 29–42: Agents, tools, MCP, and guardrails
- [ ] Days 43–53: Deployment, observability, ML, fine-tuning, and portfolio
- [ ] Days 54–60: Interview preparation and final assessment

### Project status

| Project | Status | Repository / Demo | Key metric |
|---|---|---|---|
| AI Learning Coach | Not started | Add link | Add measured result |
| Evaluated RAG | Not started | Add link | Add retrieval / faithfulness results |
| Hotel Pricing Agent | Not started | Add link | Task success target: ≥70% |

---

## Final Readiness Checklist

### Technical foundations
- [ ] Explain tokenization, embeddings, attention, and transformer architecture.
- [ ] Explain pretraining, instruction tuning, RLHF, and sampling parameters.
- [ ] Work with structured outputs, streaming, tool calls, and provider abstractions.
- [ ] Explain when to use prompting, RAG, fine-tuning, or long context.

### RAG and evaluation
- [ ] Build an ingestion and retrieval pipeline.
- [ ] Explain chunking and embedding choices.
- [ ] Measure retrieval quality using recall@k, MRR, and nDCG.
- [ ] Evaluate faithfulness, citations, and unanswerable questions.
- [ ] Explain the measured impact of hybrid search and reranking.

### Agents and production
- [ ] Design safe tools and a reliable agent loop.
- [ ] Explain workflows vs agents and when multi-agent designs are justified.
- [ ] Use MCP tools/resources where appropriate.
- [ ] Implement memory, checkpointing, and human approval.
- [ ] Test prompt injection, permissions, and privacy risks.
- [ ] Deploy, trace, monitor, and control cost/latency.

### Portfolio and interviews
- [ ] Three projects have clear READMEs, architecture diagrams, tests, and demos.
- [ ] Each project reports meaningful evaluation results.
- [ ] Can explain architecture decisions and trade-offs.
- [ ] Complete timed coding exercises and system design mocks.
- [ ] Prepare eight concise STAR stories.
- [ ] Complete a full mock interview loop.

---

## Notes

- The dates and daily tasks in this README are based on the supplied `plan.csv`.
- The repository structure, daily workflow, project descriptions, and checklists are organizational guidance to help execute the plan.
- Treat the roadmap as a practical target, not a reason to rush past concepts you cannot yet explain or demonstrate.
