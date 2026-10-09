---
schema_version: v4.0
rule_version: v3.0.0
description: Clear tutorial distinctions between demonstrated and executed approaches with grounded tradeoffs and safe migration guidance.
last_updated: 2026-10-07
keywords:
  - kw:two-approach clarification
  - kw:notebook approach selection
  - kw:production vs learning approach
  - kw:feature demonstration without full utilization
  - kw:approach migration guidance
  - kw:educational context justification
token_budget: ~850
context_tier: Low
depends:
  optional:
    - 109a-snowflake-notebooks-tutorials.md
---
# Snowflake Notebook Two-Approach Clarification Pattern

## Scope

**What This Rule Covers:**
Explaining a feature demonstrated but not used in the active tutorial path, contextual tradeoffs, and explicit production migration prerequisites.

**When to Load This Rule:**
When a notebook shows one approach but executes another, or compares learning and production implementations.

## Contract

### Inputs and Prerequisites

- Read actual feature setup and downstream calls; identify which approach executes and which is only described.
- Verify intended learning goal, data/grain/time semantics, supported APIs, and operational requirements for each approach.

### Mandatory

- Explain each approach neutrally and conditionally. Both can be valid in their contexts, but do not label a demonstrably incorrect/insecure approach valid just to preserve symmetry.
- Immediately clarify why a demonstrated setup is unused and how it relates to the lesson. Avoid implying feature integration, lineage, governance, or point-in-time guarantees absent from the executed code.
- Name the active approach and its reason: learning focus, dependency limits, transparency, or supported scope. A simplified path is not automatically inferior or universally production-safe.
- Document benefits, limitations, prerequisites, and when to select each approach based on actual needs, not a universal feature-count threshold.
- Show only correct examples when they aid understanding; do not require runnable snippets for untested alternatives or provide placeholder API calls as production instructions.
- Migration guidance must identify supported methods, inputs, keys, temporal alignment, authorization, tests, and rollback/compatibility work. Switching production behavior is not necessarily uncommenting one line.
- For feature/data joins, verify key uniqueness, cardinality, observation time, and leakage prevention in both approaches. Feature-store use alone does not prove temporal correctness, and manual joins can be correct with proper controls.
- For inline SQL versus procedures, preserve parameters, rights, transactions, dependencies, and verification when moving implementation. Avoid assuming every tutorial requires stored procedures.
- Separate optional feature registration/deployment from learning-only explanation; do not create unused cloud objects merely for demonstration without approval.
- Keep extensions to three or more approaches readable and explicit about the one active path. Cite relevant current primary feature documentation only after checking actual API claims.

### Execution Steps

1. Trace demonstrated setup to downstream execution and identify the actual learning/operational distinction.
2. Add a context-before-code clarification describing both approaches, active choice, benefits and constraints.
3. Provide concrete migration prerequisites and expected-result tests, or label the alternative conceptual when not verified.
4. Review claims against actual calls and evidence; test active/alternative paths only with appropriate execution authorization.

### Validation

- Readers can distinguish demonstrated, conceptual, and executed behavior without confusing feature setup with integration.
- Active choice justified and alternatives contextual, with no unsupported API/lineage/time-correctness guarantee.
- Migration guidance preserves data/security semantics and specifies real verification, not blanket uncomment-and-switch advice.
- Output includes clarification and tested/untested limits; no unapproved feature deployment or false production-readiness claim.

## References

- [Notebooks in Workspaces](https://docs.snowflake.com/en/user-guide/ui-snowsight/notebooks-in-workspaces/notebooks-in-workspaces-overview)
- `109a-snowflake-notebooks-tutorials.md` for educational structure.
- `109e-snowflake-notebook-checkpoints.md` for truthful checkpoints.
- `102b-snowflake-sql-procedures.md` for procedure migration when relevant.
