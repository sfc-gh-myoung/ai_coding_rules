---
schema_version: v4.0
rule_version: v3.0.0
description: "Strategies for managing context in long-horizon agent tasks (>10 agent turns within a session, OR tasks spanning multiple sessions). A task is long-horizon when context from earlier turns is needed"
last_updated: 2026-10-06
keywords:
  - kw:long-horizon tasks
  - kw:context compaction
  - kw:persistent memory
  - kw:sub-agent delegation
  - kw:multi-session continuity
  - kw:checkpointing protocols
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 003-context-engineering.md
    - 000-global-core.md
---
# Long-Horizon Task Strategies for AI Agents

## Scope

**What This Rule Covers:**
Compaction, checkpoints, durable notes and bounded delegation for tasks whose earlier decisions matter across many turns or sessions.

**When to Load This Rule:**
When work spans sessions, repeated turns need historical decisions, recall degrades or context approaches capacity. Ten turns/60% use are warning heuristics, not a universal definition.

## Contract

### Inputs and Prerequisites

- Active objective, acceptance criteria, authorization limits and current task state.
- Current source/tool outcomes plus an established authorized persistence location.
- Optional subagent infrastructure only when delegation is warranted.

### Mandatory

- Preserve foundation, active core rules, mandatory dependency closure, unresolved blockers and user decisions through compaction.
- Choose one authoritative task-state location per project; do not split decisions across divergent notes and memory APIs. Native APIs are optional; use existing files/task tooling when available.
- Track completed work, actual verification, current state, next actions, evidence locations, ownership and outstanding permissions. Store secrets nowhere in handoffs.
- Persist before resets or context limits; verify the checkpoint write succeeded. Plan compaction around 75% utilization or sooner when recall degrades.
- Compact redundant history/tool output and completed exploration, not required safety constraints or current source evidence. A 10-20% summary target is a heuristic; fidelity takes precedence.
- Each delegated task needs narrow scope, explicit deliverable, authorization constraints and exclusive write ownership. Parallelize only independent work; keep dependent implementation behind its prerequisite.
- Reconcile interrupted work from evidence before retrying. A checkpoint alone is not proof an uncertain mutation completed; never blindly replay a side effect.

### Execution Steps

1. Select compaction for a single long session, durable notes for cross-session work, and delegation for independently bounded complex tasks; combine when needed.
2. Save the objective, decisions/rationale, blockers, source/evidence references, exact completion status and next steps in the established task-state location.
3. Compact historical narrative while keeping active rules/constraints and the current work state accessible.
4. Resume by reading the checkpoint and current task queue, then verify relevant files, outstanding processes and tool outcomes against the saved state.
5. For delegated work, validate the returned artifact and test evidence; integrate only within its ownership boundary. Narrow off-topic/empty results instead of inventing findings.
6. Update state after each verified step and before session end. Keep the next action concrete and forward-focused.

### Validation

- A resumed session can identify objective, authority, pending steps, blockers and evidence without guessing.
- Decisions/rationale and current relevant file references survive compaction; mandatory rules are not silently dropped.
- Checkpoints distinguish started, completed, failed and unknown outcomes, preserving unsuccessful attempts where protocol requires.
- Subagent deliverables are scoped, concise and actionable; no concurrent writer's changes are overwritten.
- Corrupted/truncated notes: preserve recoverable bytes, inspect recent outputs and version history, reconstruct only verified state. Do not broadly restore files.
- Missing persistent storage: disclose it and provide one concise resumable summary for user-mediated continuation; do not pretend persistence succeeded.
- Timeout/crash: inspect partial artifacts and ownership first. Retry only safe, authorized, uncompleted work, never a recorded benchmark identity prohibited from retry.

## References

- [Anthropic: Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- `003-context-engineering.md` for attention budgets and required context preservation.
- `001-memory-bank.md` for the optional file-based memory-bank workflow.
