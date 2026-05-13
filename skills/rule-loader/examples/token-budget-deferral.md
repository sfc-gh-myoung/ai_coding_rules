# Example: Token Budget Deferral

## User Request

> "Build a Streamlit dashboard with Snowflake backend, pytest tests, and full docstrings"

## Phase 1: Foundation Loading

```
Load: 000-global-core.md (~4,050 tokens)
```

## Phase 2: Domain Matching

**Keywords detected:** `streamlit`, `snowflake` (keyword-domain matches)
**Extensions detected:** None explicitly, but implied `.py`

```
Match: "streamlit" keyword -> 101-snowflake-streamlit-core.md
Match: "snowflake" keyword -> 100-snowflake-core.md
Match: implied .py -> 200-python-core.md
```

## Phase 3: Activity Matching

**Keywords extracted:**
- Primary verb: `build` (create)
- Primary technologies: `Streamlit`, `Snowflake`
- Domain nouns: `dashboard`, `tests`, `docstrings`

```bash
grep -iE "test|docstring|dashboard" rules/RULES_INDEX.md
# Matches: 206-python-pytest.md (keyword: test)
#          204-python-docs.md (keyword: docstring)
```

## Phase 4: Dependency Resolution

```
206-python-pytest.md -> Depends: 200-python-core.md (already selected)
204-python-docs.md -> Depends: 200-python-core.md (already selected)
101-snowflake-streamlit-core.md -> Depends: 100-snowflake-core.md (already selected)
200-python-core.md -> Depends: 000-global-core.md (already loaded)
100-snowflake-core.md -> Depends: 000-global-core.md (already loaded)
```

**Candidate rules (6 total):**
1. 000-global-core.md (foundation)
2. 200-python-core.md (implied .py)
3. 100-snowflake-core.md (keyword: Snowflake)
4. 101-snowflake-streamlit-core.md (keyword: Streamlit)
5. 206-python-pytest.md (keyword: test)
6. 204-python-docs.md (keyword: docstring)

## Phase 5: Token Budget Management

### Step 1: Sum Token Budgets

| Rule | TokenBudget | ContextTier |
|------|------------|-------------|
| 000-global-core.md | ~4,050 | Critical |
| 200-python-core.md | ~1,800 | High |
| 100-snowflake-core.md | ~1,800 | High |
| 101-snowflake-streamlit-core.md | ~3,700 | High |
| 206-python-pytest.md | ~3,500 | Medium |
| 204-python-docs.md | ~3,500 | Low |
| **Total** | **~18,350** | |

### Step 2: Check Against Limit

- Soft warning threshold (75% of 20,000): 15,000 tokens -- **EXCEEDED**
- Hard limit (100% of 20,000): 20,000 tokens -- Not exceeded

**Action:** Begin evaluating Low-tier rules for deferral.

### Step 3: Deferral Logic

1. Identify Low-tier rules: `204-python-docs.md` (~3,500, Low)
2. Deferring `204` reduces total from ~18,350 to ~14,850 (under soft warning)
3. No Medium-tier deferrals needed since we are now under 15,000

**Decision:** Defer `204-python-docs.md`

### Step 4: Declare Deferrals

## Final Output

```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (implied .py from keyword: Streamlit)
- rules/100-snowflake-core.md (keyword: Snowflake)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
- rules/206-python-pytest.md (keyword: test)
- [Deferred: 204-python-docs.md - Low tier, budget exceeded soft warning at ~18,350]
```

**Final budget:** ~14,850 / 20,000 tokens

---

## Variant: Pre-Filtered with context_tier_filter

**Same request with:** `context_tier_filter: critical+high`

With this filter, only Critical and High tier rules are candidates. Low and Medium tiers are excluded before Phase 5 even runs.

**Candidate rules after filtering:**
1. 000-global-core.md (Critical)
2. 200-python-core.md (High)
3. 100-snowflake-core.md (High)
4. 101-snowflake-streamlit-core.md (High)

**Excluded by filter:**
- 206-python-pytest.md (Medium)
- 204-python-docs.md (Low)

| Rule | TokenBudget | ContextTier |
|------|------------|-------------|
| 000-global-core.md | ~4,050 | Critical |
| 200-python-core.md | ~1,800 | High |
| 100-snowflake-core.md | ~1,800 | High |
| 101-snowflake-streamlit-core.md | ~3,700 | High |
| **Total** | **~11,350** | |

```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (implied .py from keyword: Streamlit)
- rules/100-snowflake-core.md (keyword: Snowflake)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
```

**Final budget:** ~11,350 / 20,000 tokens (well under all thresholds)
