# Example: Streamlit Dashboard

## User Request

> "Write tests for my Streamlit dashboard"

## Phase 1: Foundation Loading

```
Load: 000-global-core.md (~3,500 tokens)
```

## Phase 2: Domain Matching

**Keywords detected:** `streamlit` (keyword-domain match)
**Extensions detected:** None explicitly, but implied `.py`

```
Match: "streamlit" keyword -> 101-snowflake-streamlit-core.md
Match: implied .py -> 200-python-core.md
```

## Phase 3: Activity Matching

**Keywords extracted:**
- Primary verb: `test`
- Primary technology: `Streamlit`

```bash
grep -i "test" rules/RULES_INDEX.md
# Matches: 206-python-pytest.md (keyword: test)

grep -i "streamlit" rules/RULES_INDEX.md
# Matches: 101-snowflake-streamlit-core.md (already selected in Phase 2)
```

**High-risk check:** `test` is a high-risk keyword. Confirm `206-python-pytest.md` is in selection (yes).

## Phase 4: Dependency Resolution

```
206-python-pytest.md -> Depends: 200-python-core.md (already selected)
101-snowflake-streamlit-core.md -> Depends: 100-snowflake-core.md (add)
200-python-core.md -> Depends: 000-global-core.md (already loaded)
100-snowflake-core.md -> Depends: 000-global-core.md (already loaded)
```

**Load order:**
1. 000-global-core.md (foundation)
2. 200-python-core.md (extension: .py)
3. 100-snowflake-core.md (dependency of 101)
4. 101-snowflake-streamlit-core.md (keyword: Streamlit)
5. 206-python-pytest.md (keyword: test)

## Phase 5: Token Budget

| Rule | TokenBudget | ContextTier |
|------|------------|-------------|
| 000-global-core.md | ~3,500 | Critical |
| 200-python-core.md | ~1,800 | High |
| 100-snowflake-core.md | ~1,800 | High |
| 101-snowflake-streamlit-core.md | ~3,700 | High |
| 206-python-pytest.md | ~3,500 | Medium |
| **Total** | **~14,300** | |

Under 15,000 warning threshold. Load all rules.

## Final Output

```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (dependency of 101)
- rules/101-snowflake-streamlit-core.md (keyword: Streamlit)
- rules/206-python-pytest.md (keyword: test)
```
