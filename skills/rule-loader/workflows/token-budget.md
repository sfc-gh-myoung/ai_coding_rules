# Phase 5: Token Budget Management

## Purpose

Manage the total token cost of loaded rules to prevent context window exhaustion, deferring low-priority rules when the budget is exceeded.

## Algorithm

### Step 1: Sum Token Budgets

For each rule selected in Phases 1-4, read its `TokenBudget` metadata value. Sum all values.

### Step 2: Check Against Limit

The budget uses a two-tier threshold model:

- **Soft warning** at 75% of `token_budget_limit`: Begin evaluating Low-tier rules for deferral
- **Hard limit** at 100% of `token_budget_limit`: Mandatory deferral by priority

With default `token_budget_limit: 20000`:
- Soft warning: 15,000 tokens
- Hard limit: 20,000 tokens

With custom `token_budget_limit: 10000`:
- Soft warning: 7,500 tokens
- Hard limit: 10,000 tokens

```
IF total_tokens <= 15000:
    Load all rules (no action needed)
IF total_tokens > 15000 AND <= 20000:
    Log warning: "Approaching token budget limit"
    Begin evaluating Low-tier rules for deferral
IF total_tokens > 20000:
    STOP loading additional rules
    Defer by priority (see Step 3)
```

### Step 3: Deferral Priority

When over budget, defer rules in this order:

1. **Low tier** rules first (all of them)
2. **Medium tier** rules not directly related to task keywords
3. **High tier** rules only if critically over budget
4. **Critical tier** rules are **never** deferred

### Step 4: Declare Deferrals

Deferred rules must be declared in the Rules Loaded section:

```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/206-python-pytest.md (keyword: test)
- [Deferred: 204-python-docs.md - Low tier, not required for task]
```

## Loading Tiers

| Tier | Load Strategy | Token Range |
|------|--------------|-------------|
| **Minimal** | Foundation + Domain | ~3,000-5,000 |
| **Standard** | + 1-2 activity rules | ~8,000-12,000 |
| **Complete** | + specialized rules | ~15,000-20,000 |

## Rules

- Agent self-regulates token budget (no external enforcement)
- Warning threshold: 15,000 tokens
- Hard limit: 20,000 tokens
- Token budgets are approximate (declared in each rule's `TokenBudget` metadata)
- When in doubt about a rule's priority, check its `ContextTier` metadata

## Worked Example

**Request:** "Write tests for my Streamlit dashboard"

| Rule | TokenBudget | ContextTier |
|------|------------|-------------|
| 000-global-core.md | ~4,050 | Critical |
| 200-python-core.md | ~1,800 | High |
| 206-python-pytest.md | ~3,500 | Medium |
| 100-snowflake-core.md | ~1,800 | High |
| 101-snowflake-streamlit-core.md | ~3,700 | High |

**Total:** ~14,850 tokens (under warning threshold, load all)

If a 6th rule with ~4,000 tokens were needed, total would hit ~18,850. At that point, evaluate whether any Medium/Low tier rules can be deferred.
