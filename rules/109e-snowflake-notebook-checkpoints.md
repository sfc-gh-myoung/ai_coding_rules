---
schema_version: v4.0
rule_version: v3.0.0
description: Truthful notebook learning checkpoints, actionable scoped recovery, and context-before-code teaching callouts.
last_updated: 2026-10-07
keywords:
  - kw:notebook checkpoint validation
  - kw:teaching point callouts
  - kw:actionable error messages
  - kw:progress verification gates
  - kw:context before code pedagogy
  - kw:checkpoint frequency placement
token_budget: ~950
context_tier: Low
depends:
  optional:
    - 109a-snowflake-notebooks-tutorials.md
---
# Snowflake Notebook Checkpoints and Teaching Points

## Scope

**What This Rule Covers:**
Meaningful transition checks, truthful pass/fail/blocked reporting, safe recovery directions, and explanatory Markdown before implementation.

**When to Load This Rule:**
When adding validation checkpoints or teaching callouts to notebook tutorials.

## Contract

### Inputs and Prerequisites

- Read actual cells, section transitions, learning objectives, expected state and critical dependencies.
- Know available data/runtime evidence, approved check/execution scope, and whether recovery steps mutate persistent state.

### Mandatory

- Place checkpoints at meaningful dependency transitions rather than after every cell or by a fixed cell-count quota. Select focused checks for actual critical state; often a few checks suffice, but no mandatory 3-7 padding.
- Verify expected row/key counts, schema/types, NULLs, model/feature readiness, units, or metric expectations as appropriate. Nonempty data alone does not prove completeness and checking a variable exists does not prove correct results.
- Evaluate each check before labeling it pass. A checkpoint title must not claim completed success before checks run; no unconditional ALL CHECKS PASSED or fabricated counts.
- Represent passed, failed, blocked, and unexecuted checks distinctly. Aggregate success only if every required applicable check actually passes; unavailable tools/data and synthetic evidence cannot certify runtime success.
- Failure messages state observed versus expected state, the relevant named prerequisite/cell, and a safe next action. Do not recommend indiscriminate run-all or rerunning mutating loads without checking actual committed state.
- Gate downstream sections on critical failures using the surface's supported mechanism. Printing a failure alone may not stop execution; explicit control flow or documented stop instructions must match the tutorial.
- Avoid expensive repeated actions such as multiple Snowpark counts per condition; collect bounded diagnostics once where safe and preserve snapshot consistency. Validation SQL still needs authorized execution/compute.
- Test checkpoints against synthetic missing/empty/wrong-schema or incorrect-value states without corrupting production data. Test negative controls separately; examples shown to learners remain correct executable patterns.
- Place Markdown teaching rationale before the implementation it explains, with [NOTE] or project-supported callouts. Explain business meaning, expected inputs/outputs, tradeoffs, and tutorial approach without invented monetary/performance facts.
- Use concrete diagnostic values only from evidence, or explicitly label illustrative assumptions. ML imbalance/cost examples do not justify unverified failure rates or financial claims for the user's dataset.
- Show concise completed/remaining work and next prerequisites; retain failed outcomes and keep learner troubleshooting scoped to owned state.

### Execution Steps

1. Map major transitions and expected state from the actual notebook, identifying critical blockers and replay risks.
2. Add rationale before implementation and focused conditional checkpoint logic after the relevant work.
3. Provide actual pass/fail/blocked summaries and safe named recovery instructions, including downstream stop behavior.
4. Exercise authorized/synthetic positive and negative cases, review output honesty, and preserve evidence.

### Validation

- Checkpoints evaluate real conditions, detect expected defects, and block required downstream work appropriately.
- Messages actionable with observed/expected values and safe prerequisite references; no blind load replay.
- Required checks unavailable/unexecuted never count as passes; no premature completion banner.
- Teaching points precede code and explain supported business/technical rationale, not invented statistics.
- Deliver changed cells/callouts and exact tests/limitations, preserving live/source state and confidential data.

## References

- [Notebooks in Workspaces](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks-in-workspaces/notebooks-in-workspaces-overview)
- `109a-snowflake-notebooks-tutorials.md` for learning-path design.
- `109-snowflake-notebooks.md` for runtime/execution boundaries.
- `109f-snowflake-notebook-two-approach-pattern.md` for demonstrated versus executed approaches.
