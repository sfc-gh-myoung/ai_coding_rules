---
schema_version: v4.0
rule_version: v5.0.0
description: "Comprehensive context engineering practices that treat context as a finite resource with diminishing returns. Covers attention budgets (n² pairwise relationships), context rot, progressive"
last_updated: 2026-10-06
keywords:
  - kw:context window management
  - kw:attention budget
  - kw:context rot prevention
  - kw:progressive disclosure patterns
  - kw:agentic search vs RAG
  - kw:context compaction strategies
  - kw:long-horizon task state
token_budget: ~1400
context_tier: Critical
depends:
  required:
    - 000-global-core.md
---
# Context Engineering for AI Agents

## Scope

**What This Rule Covers:**
Attention budgets, progressive disclosure, retrieval, compaction and durable state for long-horizon work. Context is finite; retained information should support the next decision.

**When to Load This Rule:**
When managing long tasks, context limits, degraded recall, retrieval strategy or multi-agent handoffs.

## Contract

### Inputs and Prerequisites

- Actual model/context limits, output reserve and current usage when available.
- Active objective, success criteria, authorization boundaries, loaded rules and relevant source files.
- Authorized search/read tools and established project state storage; native memory is optional, not a required dependency.

### Mandatory

- Preserve injected foundation, `000-global-core.md`, active domain core and mandatory dependency closure. Never silently trim required rules for token pressure.
- Treat matched rules as candidates: select up to three relevant leaf rules, then load required dependencies through successful reads. Defer optional/irrelevant leaves first.
- Estimate attention budget as context limit minus loaded rules, retained history and output reserve. Character-count/4 is only an estimate; use actual tokenizer/usage data when available.
- Monitor context growth and degraded recall. Begin compaction planning around 75% use; below 20% remaining attention budget shed optional context, and below 10% escalate if required context cannot fit. Thresholds are workflow heuristics, not model guarantees.
- Keep objective, blocking decisions, active errors, relevant source, tool contracts and recent task context. Drop duplicates, obsolete history, completed-task detail with no remaining dependency and irrelevant output.
- Use progressive disclosure: Quick Start/objective first, overview when task demands it, full referenced source/documentation when needed. Do not substitute summaries for mandatory successful rule reads or source inspection before editing.
- Persist long-task decisions, remaining steps and evidence locations in existing authorized project locations before compaction. Reconcile state against current files on recovery.
- Keep prompts concrete: responsibilities, boundaries and observable acceptance criteria, neither brittle exhaustive branching nor vague platitudes.
- Avoid bulk-loading codebases or preloading knowledge bases. Prefer targeted search and evidence-driven follow-up reads.
- Keep every operational rule within 250 lines and at most three correct examples; declare token budgets as estimates until measured. Link optional details instead of duplicating them.

### Execution Steps

1. Assess context/attention budget and identify indispensable constraints and evidence.
2. Search exact identifiers with lexical search or unknown functionality with semantic search; verify matches with current source reads. Follow imports/dependencies only as needed.
3. Choose retrieval: agentic exploration for changing code and adaptive questions; indexed retrieval for large, well-bounded corpora when freshness is checked. A hybrid can retrieve initial context then inspect current sources.
4. Work with focused context and track completion/evidence outside the window for long tasks. Delegate independent complex subtasks only when useful; provide narrow scope, ownership, deliverable and constraints.
5. Before limits or recall degradation, compact completed work/history while preserving foundation, required rules, current objective, blockers, authorization and unresolved evidence. Defer optional leaves rather than mandatory closure.
6. Resume from durable state, re-read key source files and verify tool/run outcomes before continuing. If state is missing or contradictory, report the gap rather than inventing completion.
7. Validate fidelity, remaining budget and next-step clarity; update persistent state without turning routine progress into permanent personal memory.

### Validation

- Current objective, constraints and success criteria remain explicit after compaction.
- Required-rule closure and active domain core are preserved; no inaccessible file is declared read.
- Token estimates are labeled; output reserve and tool-result size are accounted for.
- Context is relevant and nonduplicated, with historical/current status separated.
- Long-horizon task state names next actions, blockers, evidence and ownership; a new session can verify and resume it.
- Overflow: compact nonessential history first. If mandatory context still exceeds limits, escalate rather than silently dropping instructions.
- Lost state: restore from authorized notes and re-read current source; off-topic subagent output requires narrower scope, not unsupported synthesis.
- Small windows: reduce optional leaves and task breadth, retain mandatory closure and durable state. Do not discard required High/Medium-tier dependencies merely because the model is small.

## References

- [Anthropic: Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic: Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic: Agent skills and progressive disclosure](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- `003a-long-horizon-tasks.md` for long-task checkpoints and handoffs.
- `001-memory-bank.md` for the optional file-based memory-bank workflow.
