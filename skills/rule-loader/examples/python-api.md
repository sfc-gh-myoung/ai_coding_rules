# Example: FastAPI Endpoint

## User Request

> "Add a FastAPI endpoint for user authentication"

## Phase 1: Foundation Loading

```
Load: 000-global-core.md (~3,500 tokens)
```

## Phase 2: Domain Matching

**Extensions detected:** None explicitly, but implied `.py`

```
Match: implied .py -> 200-python-core.md
```

## Phase 3: Activity Matching

**Keywords extracted:**
- Primary verb: `add` (create)
- Primary technology: `FastAPI`
- Domain nouns: `endpoint`, `authentication`

```bash
grep -i "fastapi" rules/RULES_INDEX.md
# Matches: 210-python-fastapi-core.md (keyword: fastapi)

grep -i "security" rules/RULES_INDEX.md
# Matches: 210a-python-fastapi-security.md (keyword: fastapi-security)
#          107-snowflake-security-governance.md (keyword: security)
```

`210a` is relevant (FastAPI security). `107` is Snowflake-specific, not relevant here.

## Phase 4: Dependency Resolution

```
210-python-fastapi-core.md -> Depends: 200-python-core.md (already selected)
210a-python-fastapi-security.md -> Depends: 210-python-fastapi-core.md (already selected)
200-python-core.md -> Depends: 000-global-core.md (already loaded)
```

**Load order:**
1. 000-global-core.md (foundation)
2. 200-python-core.md (extension: .py)
3. 210-python-fastapi-core.md (keyword: fastapi)
4. 210a-python-fastapi-security.md (keyword: authentication/security)

## Phase 5: Token Budget

| Rule | TokenBudget | ContextTier |
|------|------------|-------------|
| 000-global-core.md | ~3,500 | Critical |
| 200-python-core.md | ~1,800 | High |
| 210-python-fastapi-core.md | ~3,500 | High |
| 210a-python-fastapi-security.md | ~3,000 | Medium |
| **Total** | **~11,800** | |

Under 15,000 warning threshold. Load all rules.

## Final Output

```markdown
## Rules Loaded
- rules/000-global-core.md (foundation)
- rules/200-python-core.md (file extension: .py)
- rules/210-python-fastapi-core.md (keyword: fastapi)
- rules/210a-python-fastapi-security.md (keyword: authentication)
```
