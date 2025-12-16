# COMPARISON Mode Example

This example demonstrates comparing multiple plans for the same task.

## Input

```text
target_files: [plans/auth-plan-claude.md, plans/auth-plan-gpt.md]
task_description: Implement OAuth2 authentication for the API
review_date: 2025-12-16
review_mode: COMPARISON
model: claude-sonnet45
```

## Expected Output

```markdown
## Plan Comparison: OAuth2 Authentication Implementation

**Task:** Implement OAuth2 authentication for the API
**Review Date:** 2025-12-16
**Reviewing Model:** Claude Sonnet 4.5

### Plans Reviewed
| # | Plan File | Created By | Lines |
|---|-----------|------------|-------|
| A | plans/auth-plan-claude.md | Claude Sonnet 4.5 | 180 |
| B | plans/auth-plan-gpt.md | GPT-5.2 | 145 |

---

### Comparative Scores
| Criterion | Weight | Plan A | Plan B | Winner |
|-----------|--------|--------|--------|--------|
| Executability | 2× | 9/10 | 7/10 | A |
| Completeness | 2× | 8/10 | 9/10 | B |
| Success Criteria | 2× | 8/10 | 6/10 | A |
| Scope | 2× | 9/10 | 8/10 | A |
| Decomposition | 1× | 4/5 | 5/5 | B |
| Dependencies | 1× | 5/5 | 4/5 | A |
| Context | 1× | 4/5 | 5/5 | B |
| Risk Awareness | 1× | 4/5 | 3/5 | A |
| **Total** | | **51/60** | **47/60** | **A** |

### Verdict by Plan
| Plan | Score | Verdict |
|------|-------|---------|
| A | 51/60 (85%) | EXECUTABLE |
| B | 47/60 (78%) | NEEDS_REFINEMENT |

---

### Head-to-Head Analysis

#### Executability: Plan A wins (9/10 vs 7/10)

**Plan A:**
- All commands explicit with full paths
- Zero ambiguous phrases
- Token refresh flow has exact curl commands

**Plan B:**
- 5 instances of "if needed" or "as appropriate"
- Token validation step says "check token" without specifying how
- Missing explicit error codes for failure cases

*Evidence:*
- Plan A, Line 45: `curl -X POST https://auth.example.com/oauth/token -d "grant_type=..."`
- Plan B, Line 38: "validate the token as appropriate" ← ambiguous

---

#### Completeness: Plan B wins (9/10 vs 8/10)

**Plan A:**
- Missing cleanup for expired token cache
- No rollback procedure for partial deployment

**Plan B:**
- Includes token cache cleanup cron job
- Database migration rollback documented
- Error recovery for each phase

*Evidence:*
- Plan B, Line 89: "Rollback: `alembic downgrade -1`"
- Plan A: No equivalent rollback procedure found

---

#### Success Criteria: Plan A wins (8/10 vs 6/10)

**Plan A:**
- 95% of tasks have explicit verification
- Integration tests with expected outputs
- Health check endpoints documented

**Plan B:**
- Many tasks end with "verify it works"
- Fewer explicit test assertions
- Success states often subjective

*Evidence:*
- Plan A, Line 78: "Success: `pytest tests/auth/ -v` returns 0 with 100% pass"
- Plan B, Line 65: "Success: authentication working correctly" ← not measurable

---

#### Scope: Plan A wins (9/10 vs 8/10)

**Plan A:**
- Explicit in-scope/out-of-scope section
- Defined starting state (fresh db, no existing auth)
- Measurable end state (all endpoints protected)

**Plan B:**
- Scope boundaries implicit
- Starting state assumed
- End state clear but not measurable

---

#### Decomposition: Plan B wins (5/5 vs 4/5)

**Plan B:**
- Every task is single-action
- Consistent granularity
- No monolithic steps

**Plan A:**
- Task 2.3 bundles 3 actions
- Phase 3 has one oversized task

---

#### Dependencies: Plan A wins (5/5 vs 4/5)

**Plan A:**
- Explicit dependency graph
- Blocking relationships marked
- Parallel opportunities noted

**Plan B:**
- Linear ordering assumed
- Some dependencies implicit

---

#### Context: Plan B wins (5/5 vs 4/5)

**Plan B:**
- OAuth2 terminology explained
- Links to RFC 6749 where relevant
- No assumed domain knowledge

**Plan A:**
- Assumes familiarity with OAuth2 flows
- "PKCE" mentioned without definition

---

#### Risk Awareness: Plan A wins (4/5 vs 3/5)

**Plan A:**
- Security risks documented
- Token leakage prevention
- Rate limiting considerations

**Plan B:**
- Minimal risk discussion
- No fallback for auth provider outage

---

### Recommendation

**Winner:** Plan A (51/60)

**Rationale:** Plan A is more immediately executable by an autonomous agent due to:

1. **Zero ambiguous phrases** vs 5 in Plan B
2. **Explicit success criteria** (95% vs ~70% verifiable)
3. **Clear scope boundaries** with defined start/end states
4. **Better risk awareness** with documented fallbacks

**When to use Plan B instead:**
If the implementation team is unfamiliar with OAuth2, Plan B's superior context
and finer granularity may reduce onboarding time. Consider merging Plan B's
context sections into Plan A's structure.

### Synthesis Recommendations

Combine the best of both plans:

1. Use Plan A's structure and commands
2. Add Plan B's context/explanations for OAuth2 concepts
3. Add Plan B's cleanup procedures (token cache cron)
4. Split Plan A's Task 2.3 into 3 separate tasks

---

**Output written to:** reviews/plan-comparison-claude-sonnet45-2025-12-16.md
```

## Key Points Demonstrated

1. **Side-by-side scoring** for all 8 dimensions
2. **Winner declared per dimension** with evidence
3. **Overall winner determined** by total score
4. **Head-to-head analysis** with specific line citations
5. **Verdict assigned per plan** (EXECUTABLE vs NEEDS_REFINEMENT)
6. **When to use alternative** - acknowledges Plan B strengths
7. **Synthesis recommendations** - practical guidance for combining best elements

