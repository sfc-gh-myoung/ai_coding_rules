# Example: Multi-Domain (Snowflake SQL + Python)

## User Request

> "Create a Python script that loads CSV data into Snowflake using COPY INTO"

## Phase 1: Foundation Loading

```
Load: 000-global-core.md (~4,050 tokens)
```

## Phase 2: Domain Matching

**Extensions detected:** `.py` (Python script)
**Keywords detected:** `Snowflake` (keyword-domain match)

```
Match: .py -> 200-python-core.md
Match: "Snowflake" keyword -> 100-snowflake-core.md
```

## Phase 3: Activity Matching

**Keywords extracted:**
- Primary verb: `create`
- Primary technologies: `Python`, `Snowflake`
- Domain nouns: `CSV`, `COPY INTO`, `data loading`

```bash
grep -i "COPY INTO" rules/RULES_INDEX.md
# Matches: 102-snowflake-sql-core.md (keyword: COPY INTO)
#          108-snowflake-data-loading.md (keyword: copy-into, data-loading)

grep -i "data-loading" rules/RULES_INDEX.md
# Matches: 108-snowflake-data-loading.md
```

Both `102` (SQL patterns for COPY INTO) and `108` (data loading specifics) are relevant.

## Phase 4: Dependency Resolution

```
102-snowflake-sql-core.md -> Depends: 100-snowflake-core.md (already selected)
108-snowflake-data-loading.md -> Depends: 100-snowflake-core.md (already selected)
200-python-core.md -> Depends: 000-global-core.md (already loaded)
100-snowflake-core.md -> Depends: 000-global-core.md (already loaded)
```

**Load order:**
1. 000-global-core.md (foundation)
2. 200-python-core.md (extension: .py)
3. 100-snowflake-core.md (keyword: Snowflake)
4. 102-snowflake-sql-core.md (keyword: COPY INTO)
5. 108-snowflake-data-loading.md (keyword: data-loading)

## Phase 5: Token Budget

| Rule | TokenBudget | ContextTier |
|------|------------|-------------|
| 000-global-core.md | ~4,050 | Critical |
| 200-python-core.md | ~1,800 | High |
| 100-snowflake-core.md | ~1,800 | High |
| 102-snowflake-sql-core.md | ~3,200 | High |
| 108-snowflake-data-loading.md | ~3,500 | Medium |
| **Total** | **~14,350** | |

Under 15,000 warning threshold. Load all rules.

## Final Output

```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (keyword: Snowflake)
- rules/102-snowflake-sql-core.md (keyword: COPY INTO)
- rules/108-snowflake-data-loading.md (keyword: data-loading)
```

## Note: Over-Budget Variant

If this request also involved testing (`"...and write pytest tests"`), adding `206-python-pytest.md` (~3,500) would push total to ~17,850. At that point:

```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/100-snowflake-core.md (keyword: Snowflake)
- rules/102-snowflake-sql-core.md (keyword: COPY INTO)
- rules/108-snowflake-data-loading.md (keyword: data-loading)
- rules/206-python-pytest.md (keyword: test)
- [Warning: Token budget at ~17,850 / 20,000]
```

All rules still loaded because none are Low tier. If a Low-tier rule were also matched, it would be deferred first.
