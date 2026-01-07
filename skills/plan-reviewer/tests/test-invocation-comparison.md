# Test Invocation: plan-reviewer (COMPARISON Mode)

## Purpose

Verify plan-reviewer skill correctly compares multiple plans and declares a winner.

## Test Input

```
Use the plan-reviewer skill.

review_date: 2026-01-06
review_mode: COMPARISON
model: claude-sonnet-45
target_files:
  - plans/plan-a.md
  - plans/plan-b.md
  - plans/plan-c.md
```

## Expected Behavior

### Phase 1: Input Validation
- ✅ Multiple target files provided
- ✅ All target files exist

### Phase 2: Review Each Plan
- ✅ For each plan (A, B, C):
  - Execute FULL mode review (all 8 dimensions)
  - Record individual scores
  - Store recommendations

### Phase 3: Comparative Analysis
- ✅ Build side-by-side comparison table
- ✅ Declare winner per dimension
- ✅ Calculate total scores
- ✅ Determine overall winner

### Phase 4: Output
- ✅ Write to: `reviews/_comparison-plans-abc-claude-sonnet-45-2026-01-06.md`
- ✅ Include individual plan summaries
- ✅ Include comparison table
- ✅ Declare winner with rationale

## Expected Output Structure

```markdown
# Plan Comparison Review

**Reviewed:** 2026-01-06
**Model:** claude-sonnet-45
**Mode:** COMPARISON
**Plans:** plan-a.md, plan-b.md, plan-c.md

## Executive Summary

Compared 3 plans for [task description].

**Winner:** Plan B (score: 85/100)
**Runner-up:** Plan A (score: 78/100)
**Third:** Plan C (score: 62/100)

## Individual Plan Summaries

### Plan A (78/100 - GOOD_PLAN)
- Strengths: Clear executability, good scope
- Weaknesses: Missing error recovery
- Key issue: No rollback plan

### Plan B (85/100 - EXCELLENT_PLAN)
- Strengths: Complete, well-scoped, explicit commands
- Weaknesses: Minor context gaps
- Key advantage: Comprehensive error recovery

### Plan C (62/100 - NEEDS_WORK)
- Strengths: Good task decomposition
- Weaknesses: Many ambiguous phrases, unclear success criteria
- Key issue: Unbounded scope

## Dimension Comparison

| Dimension | Plan A | Plan B | Plan C | Winner |
|-----------|--------|--------|--------|--------|
| Executability | 15/20 | 18/20 | 10/20 | Plan B |
| Completeness | 12/20 | 20/20 | 12/20 | Plan B |
| Success Criteria | 16/20 | 16/20 | 8/20 | Tie: A+B |
| Scope | 15/15 | 15/15 | 9/15 | Tie: A+B |
| Dependencies | 8/10 | 10/10 | 6/10 | Plan B |
| Decomposition | 4/5 | 3/5 | 5/5 | Plan C |
| Context | 4/5 | 3/5 | 4/5 | Tie: A+C |
| Risk Awareness | 4/5 | 5/5 | 2/5 | Plan B |
| **Total** | **78/100** | **85/100** | **62/100** | **Plan B** |

## Winner Rationale

**Plan B wins** due to:
1. Highest total score (85/100)
2. Strongest critical dimensions:
   - Executability: 18/20 (few ambiguous phrases)
   - Completeness: 20/20 (all components present)
   - Risk Awareness: 5/5 (comprehensive rollback)
3. Only minor weakness: Context (3/5)

## Dimension-by-Dimension Analysis

### Executability (Winner: Plan B)

**Plan B advantages:**
- All commands explicit
- Only 2 ambiguous phrases (vs 7 in A, 15 in C)
- All conditionals complete

**Evidence:**
- Plan A (line 45): "if necessary" (ambiguous)
- Plan B (line 50): "if exit code != 0" (explicit)

[Continue for each dimension...]

## Integration Recommendations

Best elements from each plan:
- Use Plan B as base (highest score)
- Adopt Plan C's task decomposition (5/5)
- Integrate Plan A's success criteria (tie with B)

**Suggested hybrid approach:**
1. Start with Plan B
2. Split large tasks per Plan C's decomposition
3. Verify success criteria match Plan A's thoroughness

## Conclusion

**Recommendation:** Execute Plan B with minor enhancements from Plans A and C.

Next steps:
1. Address Plan B's context gaps
2. Consider adopting Plan C's task sizing
3. Proceed to execution
```

## Success Criteria

- [ ] All plans reviewed independently
- [ ] Comparison table created
- [ ] Winner declared
- [ ] Rationale provided with evidence
- [ ] Integration recommendations included
- [ ] Dimension-by-dimension comparison detailed

## Edge Cases

**Scenario 1: Tied scores**
```
Plan A: 85/100
Plan B: 85/100

Winner: Plan A (higher critical dimension scores)
- Executability: A=18, B=16
```

**Scenario 2: Single plan provided**
```
Error: COMPARISON mode requires multiple plans, use FULL for single plan
```
