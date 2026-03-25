---
name: rule-loader
description: Determines which rule files to load for a given user request by matching file extensions, directory paths, and keywords against RULES_INDEX.md. Handles foundation loading, domain matching, activity matching, dependency resolution, and token budget management. Use when loading rules, selecting rules for a task, resolving rule dependencies, or managing token budgets during rule loading.
version: 1.2.0
---

# Rule Loader

Selects and loads the correct set of rule files for any user request, ensuring consistent rule discovery across agents and sessions.

## Purpose

Given a user request, determine which rules to load, in what order, respecting dependencies and token budgets. This skill formalizes the rule-loading algorithm defined in AGENTS.md Steps 1-3 into a reusable, progressively-disclosed workflow.

## Use this skill when

- Loading rules for a new user request (first response or task switch)
- Resolving which domain rules match a file extension
- Determining activity rules from request keywords
- Managing token budgets when multiple rules are candidates
- Debugging why a rule was or was not loaded
- Building rule-loading logic into new agent configurations

## Inputs

### Required
- `user_request`: `string` - The user's message text to analyze for keywords, extensions, and technologies

### Optional
- `rules_path`: `string` (default: `rules/`) - Path to the rules directory
- `token_budget_limit`: `number` (default: `20000`) - Hard maximum token budget for loaded rules. A soft warning triggers at 75% of this value (default: 15,000) to begin evaluating Low-tier deferrals.
- `context_tier_filter`: `string` (default: `all`) - Filter by ContextTier: `all`, `critical`, `critical+high`, `critical+high+medium`

### Input Validation

Before executing Phase 1:

1. `user_request` must be a non-empty string. If empty or whitespace-only: STOP with "No user request provided."
2. `token_budget_limit` must be a positive integer >= 5000. If below 5000: WARN "Token budget too low for foundation + any domain rule. Minimum recommended: 5000."
3. `context_tier_filter` must be one of: `all`, `critical`, `critical+high`, `critical+high+medium`. If invalid: WARN and default to `all`.

## Output (required)

A `## Rules Loaded` section listing all selected rules with loading reasons, formatted per AGENTS.md Step 4.

**Example output:**
```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 101)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
- rules/206-python-pytest.md (keyword: test)
- [Deferred: 204-python-docs-comments.md - Low tier, not required for task]
```

## Workflow (progressive disclosure)

Execute phases in order. Load workflow files only as needed.

### Phase 1: Foundation Loading
Always load `000-global-core.md`. Non-negotiable.

**Details:** `workflows/foundation-loading.md`

### Phase 2: Domain Matching
Match file extensions and directory paths to domain rules using RULES_INDEX.md Section 2.

**Details:** `workflows/domain-matching.md`

### Phase 3: Activity Matching
Search RULES_INDEX.md for keyword matches from the user request.

**Details:** `workflows/activity-matching.md`

### Phase 4: Dependency Resolution
For each selected rule, check `Depends` metadata and load prerequisites first.

**Details:** `workflows/dependency-resolution.md`

### Phase 5: Token Budget Management
Sum TokenBudget values, defer low-priority rules if over budget.

**Details:** `workflows/token-budget.md`

## Quick Validation

After rule selection, verify:

1. Foundation (000-global-core.md) is always present
2. Every loaded rule was actually read via `read_file` (not assumed)
3. Dependencies loaded before dependents
4. Total token budget does not exceed limit (default 20,000)
5. Deferred rules are declared with reason

## Error Handling

**RULES_INDEX.md not found:**
- Warn, fall back to foundation + file-extension matching only
- Proceed in degraded mode

**Rule file not found:**
- If only matched rule: Report with options (A) correct path, (B) proceed without, (C) cancel
- If other rules loaded: Note failure, mark Gate 3 as PASSED, continue

**Dependency not found:**
- Skip the dependent rule, log warning
- Continue with remaining rules

**Token budget exceeded:**
- Defer Low tier rules first, then Medium tier
- Never defer Critical tier rules
- Declare deferrals in Rules Loaded section

## Examples

See `examples/` for complete walkthroughs:
- `streamlit-dashboard.md` - "Write tests for my Streamlit dashboard"
- `python-api.md` - "Add a FastAPI endpoint"
- `multi-domain.md` - Cross-domain request (Snowflake SQL + Python)
- `token-budget-deferral.md` - Token budget deferral with Low-tier rule deferred

## Related

- **AGENTS.md** - Bootstrap protocol that invokes this loading logic (Steps 1-3)
- **RULES_INDEX.md** - Authoritative source for rule discovery mappings
- **002h-claude-code-skills.md** - Skill authoring standards this skill follows
- **003-context-engineering.md** - Token budget and attention management principles
