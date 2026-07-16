# Phase 4: Dependency Resolution

## Purpose

Ensure prerequisite rules are loaded before dependent rules, based on each rule's `depends:` metadata field (v3.5 YAML frontmatter; inline `**Depends:**` remains readable via dual-parse fallback).

## Algorithm

### Step 1: Compute Required-Closure (MUST RUN — deterministic)

**This step is mandatory and MUST complete before any other dependency work.**

After Phases 2–3 produce the initial selection, compute the full transitive
`required:` closure deterministically:

```
closure = set(selected_rules)
queue   = list(closure)

while queue is not empty:
    rule = queue.pop()
    for dep in rule.depends.required:          # from YAML frontmatter
        if dep not in closure:
            closure.add(dep)
            queue.append(dep)

effective_loaded = sorted(closure)
```

This fixpoint loop is **cycle-safe**: once a rule is in `closure` it is never
re-enqueued.  Treat every rule in `effective_loaded` as if it were explicitly
loaded.  Deduplicate against already-loaded rules before announcing them in
the PRE-FLIGHT Gate 3 header.

> **Why deterministic closure matters:** an LLM-prose instruction like "repeat
> recursively" is nondeterministic under token pressure.  The explicit algorithm
> above produces the same result on every run and eliminates R8 violations caused
> by forgotten `required:` parents.

### Step 2: Determine Load Order

Sort rules so that dependencies are loaded before dependents:

```
Example dependency chain:
  206-python-pytest.md
    -> Depends: 200-python-core.md
       -> Depends: 000-global-core.md (already loaded as foundation)

Load order:
  1. 000-global-core.md (foundation, already loaded)
  2. 200-python-core.md (dependency of 206)
  3. 206-python-pytest.md (originally selected)
```

### Step 3: Handle Missing Dependencies

If a dependency cannot be loaded:
- Skip the dependent rule
- Log warning: "Dependency [name] not found, skipping [dependent-name]"
- Continue with remaining rules

### Step 4: Record Loading Reasons

Dependencies loaded via this phase use the reason format:
- `"(dependency of 206-python-pytest.md)"`

## Rules

- Dependencies are loaded **before** the rules that require them
- A missing dependency causes its dependent to be skipped (not a full stop)
- Circular dependencies should not exist; if detected, log warning and break the cycle
- Foundation (000-global-core.md) is never listed as a dependency to resolve since it is always loaded in Phase 1
- **Dependencies loaded via `required:` closure do NOT count against the R3 domain-rule cap.** The cap counts only the agent's LEAF/domain SELECTIONS. `required:` dependency closure is loaded in addition to — and does not count against — the 3 domain/activity-selection cap, and a `required:` parent is never deferred for token pressure. If loading a mandatory closure would exceed the 20,000-token R4 ceiling, defer LEAF/optional selections first; a still-over-budget mandatory closure is escalated (see `token-budget.md` Q3-resolution), never silently trimmed.

## Common Dependency Chains

| Rule | Depends On |
|------|-----------|
| `101-snowflake-streamlit-core.md` | `100-snowflake-core.md` |
| `102-snowflake-sql-core.md` | `100-snowflake-core.md` |
| `206-python-pytest.md` | `200-python-core.md` |
| `115a-snowflake-cortex-agents-instructions.md` | `100-snowflake-core.md`, `115-snowflake-cortex-agents-core.md` |
| `002a-rule-creation.md` | `002-rule-governance.md`, `000-global-core.md` |

Consult `rules/RULES_INDEX.md` (the agent discovery index) for the authoritative dependency list for each rule.

**Worked closure example:** Agent selects `119-snowflake-warehouse-core.md` (1 LEAF selection, counts as 1 against the 3-rule cap). `119` declares `required: 100-snowflake-core.md, 103-snowflake-sql-performance.md, 105-snowflake-query-patterns.md`. Transitive walk adds those 3 rules — closure = {100, 103, 105}. All three are loaded in addition to the cap, not counted against it. Cap usage = 1/3 (only the original leaf selection 119).


### Step 5: Check for Companion Examples (complex configurations only)

If any loaded rule involves Cortex Agent, Cortex Search, or Semantic View:

1. Check for companion example: `rules/examples/{rule-number}-*-example.md`
2. If example exists: Load for reference implementation
3. Record with reason: `"(companion example for NNN-rule-name.md)"`

This step is only required for complex configuration rules. Skip for standard domain and activity rules.
