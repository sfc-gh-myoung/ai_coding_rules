# Phase 4: Dependency Resolution

## Purpose

Ensure prerequisite rules are loaded before dependent rules, based on each rule's `Depends` metadata field.

## Algorithm

### Step 1: Collect Dependencies

For each rule selected in Phases 2-3:
1. Read the rule's metadata (specifically the `Depends` field)
2. If `Depends` lists other rules, add those to the load list
3. Repeat recursively until no new dependencies are found

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

## Common Dependency Chains

| Rule | Depends On |
|------|-----------|
| `101-snowflake-streamlit-core.md` | `100-snowflake-core.md` |
| `102-snowflake-sql-core.md` | `100-snowflake-core.md` |
| `206-python-pytest.md` | `200-python-core.md` |
| `115a-snowflake-cortex-agents-instructions.md` | `100-snowflake-core.md`, `115-snowflake-cortex-agents-core.md` |
| `002a-rule-creation.md` | `002-rule-governance.md`, `000-global-core.md` |

Consult RULES_INDEX.md for the authoritative dependency list for each rule.

### Step 5: Check for Companion Examples (complex configurations only)

If any loaded rule involves Cortex Agent, Cortex Search, or Semantic View:

1. Check for companion example: `{rules_path}/examples/{rule-number}-*-example.md`
2. If example exists: Load for reference implementation
3. Record with reason: `"(companion example for NNN-rule-name.md)"`

This step is only required for complex configuration rules. Skip for standard domain and activity rules.
