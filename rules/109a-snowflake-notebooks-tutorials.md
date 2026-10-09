---
schema_version: v4.0
rule_version: v5.0.0
description: Grounded notebook learning objectives, progressive explanations, truthful checkpoints, and safe self-paced tutorials.
last_updated: 2026-10-07
keywords:
  - kw:notebook-tutorial design
  - kw:learning objectives structure
  - kw:checkpoint validation cells
  - kw:anti-pattern teaching
  - kw:progressive complexity management
  - kw:teaching point callouts
token_budget: ~1050
context_tier: High
depends:
  required:
    - 109-snowflake-notebooks.md
    - 920-data-science-analytics.md
---
# Snowflake Notebook Tutorial Design Patterns

## Scope

**What This Rule Covers:**
Notebook-based instruction with measurable outcomes, business context, progressive complexity, learning checkpoints, and reproducible safe execution.

**When to Load This Rule:**
When creating or refining educational Snowflake notebooks and self-paced technical workshops.

## Contract

### Inputs and Prerequisites

- Read actual live/source cells, section structure, code dependencies, audience prerequisites, learning goals, and completion budget.
- Identify notebook runtime/surface, data availability, execution permissions, compute costs, and current technical documentation.

### Mandatory

- Derive objectives from actual taught content, not generic assumed ML/data topics. Place clear measurable action outcomes near the introduction; a small focused set (often 3-6) is guidance, not permission to invent content or force a cell index.
- Provide a roadmap of logical parts and prerequisites, quick/full paths where meaningful, and explicit optional advanced sections. Skipping ahead is safe only when dependencies/data state are satisfied.
- Explain business context, inputs, expected result, and why before code. Define audience-relevant jargon on first use; use concise Markdown teaching callouts such as [NOTE] where they help.
- Start with the simplest correct working pattern, then explain production requirements and justified optimization. Demonstrate only correct executable examples; describe pitfalls and their consequences in prose, not runnable unsafe code.
- Keep at most three distinct correct examples in this operational rule. Tutorial content should likewise avoid needless repetition and copied negative executable snippets; no mandatory quota of mistakes per topic.
- Place focused checkpoints at meaningful transitions. Verify actual keys/counts/types/metrics and required prerequisites with actionable failures, not generic COUNT > 0 or unconditional pass text.
- Distinguish unresolved checks from passes; empty/missing data, unavailable APIs, mocked/synthetic outputs, and unexecuted account checks must be disclosed. Checkpoints must not authorize new SQL/cloud writes.
- Recovery guidance names the required input/step and explains replay safety. Do not tell learners to rerun mutating setup/load cells blindly after failure; inspect actual state and preserve owned/unrelated data.
- Estimate duration from measured or honestly labeled assumed reading/execution costs, including package/data/compute startup. No universal seconds-per-cell formula or claim SQL always runs faster than Python.
- For SQL-focused tutorials use SQL and Markdown with meaningful result assertions/interpretation; Python is not mandatory. Use the actual surface's supported error/validation mechanism rather than inventing universal SQL assertion syntax.
- When demonstrating a feature but using a simplified implementation, identify both approaches, which one executes, limitations, and production migration requirements. Do not imply a shown-but-unused feature is integrated.
- Record actual last-verification date/runtime/package versions and significant changes; do not stamp verification before tests. Replace deprecated guidance using current primary docs and retest relevant checkpoints under approval.
- Preserve secrets/data confidentiality and bounded computation; no unapproved uploads, live service calls, or production cleanup for teaching convenience.

### Execution Steps

1. Read notebook and map demonstrated concepts, dependencies, audience difficulty, and existing checkpoints.
2. Add grounded introduction/objectives, roadmap, prerequisites, and realistic quick/full execution paths.
3. Explain correct patterns and pitfalls before implementation, then add meaningful checkpoint/recovery guidance.
4. Review source/metadata/runtime and perform applicable local lint/structure checks; execute fresh-state tests only when approved.
5. Reconcile every objective to taught content/checkpoint evidence and report timing/verification limitations.

### Validation

- Objectives measurable and taught, roadmap coherent, jargon explained, and complexity increases deliberately.
- Checkpoints detect actual failures with scoped actionable recovery; no false passes or unsafe automatic reruns.
- Self-paced paths preserve prerequisites; simplified/production alternatives and optional work clearly labeled.
- Duration/version verification claims supported or explicitly estimates; relevant current docs cited.
- Output is the revised tutorial with learning/verification evidence, not a promise of unexecuted runtime success.

## References

- [Notebooks in Workspaces](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks-in-workspaces/notebooks-in-workspaces-overview)
- [Snowpark Python](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- `109-snowflake-notebooks.md` for runtime and reproducibility.
- `109e-snowflake-notebook-checkpoints.md` for validation cells.
- `109f-snowflake-notebook-two-approach-pattern.md` for approach clarification.
