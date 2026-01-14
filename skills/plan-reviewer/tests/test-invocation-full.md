# Test Invocation: plan-reviewer (FULL Mode)

## Purpose

Verify plan-reviewer skill executes correctly with all 8 dimensions.

## Test Input

```
Use the plan-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
target_file: plans/example-plan.md
```

## Expected Behavior

### Phase 1: Input Validation
-  Date format valid (YYYY-MM-DD)
-  Mode recognized (FULL)
-  Target file exists

### Phase 2: Agent Execution Test
-  Count blocking issues:
  - Ambiguous phrases
  - Implicit commands
  - Missing conditional branches
  - Undefined thresholds
-  Apply scoring cap if ≥10 issues

### Phase 3: Review Execution
-  Read plan file completely
-  Load rubrics progressively:
  - executability.md (ambiguous phrases)
  - completeness.md (setup, validation, error recovery)
  - success-criteria.md (measurable criteria)
  - scope.md (boundaries, termination)
  - dependencies.md (prerequisites)
  - decomposition.md (task sizing)
  - context.md (rationale)
  - risk-awareness.md (failures, rollback)
-  Score each dimension (8 scores)
-  Apply weighted formula
-  Determine verdict

### Phase 4: Output
-  Generate recommendations
-  Write to: `reviews/example-plan-claude-sonnet-45-2026-01-06.md`
-  Confirm: "Review written to: ..."

## Expected Output Structure

```markdown
# Plan Review: example-plan.md

**Reviewed:** 2026-01-06
**Model:** claude-sonnet-45
**Mode:** FULL

## Executive Summary

[Summary paragraph]

**Overall Score:** XX/100
**Verdict:** [EXCELLENT_PLAN|GOOD_PLAN|NEEDS_WORK|POOR_PLAN|INADEQUATE_PLAN]

## Agent Execution Test

**Blocking Issues Count:** X

- Ambiguous phrases: Y
- Implicit commands: Z
- Missing branches: A
- Undefined thresholds: B

**Impact:** [None | Cap at 60 | Cap at 40]

## Dimension Scores

- **Executability** - Raw: X/5, Weight: ×4, Points: Y/20, Status: ...
- **Completeness** - Raw: X/5, Weight: ×4, Points: Y/20, Status: ...
- **Success Criteria** - Raw: X/5, Weight: ×4, Points: Y/20, Status: ...
- **Scope** - Raw: X/5, Weight: ×3, Points: Y/15, Status: ...
- **Dependencies** - Raw: X/5, Weight: ×2, Points: Y/10, Status: ...
- **Decomposition** - Raw: X/5, Weight: ×1, Points: Y/5, Status: ...
- **Context** - Raw: X/5, Weight: ×1, Points: Y/5, Status: ...
- **Risk Awareness** - Raw: X/5, Weight: ×1, Points: Y/5, Status: ...

**Total:** XX/100

## Detailed Analysis

### Executability (Y/20)

**Ambiguous phrases found:**
- Line 23: "if necessary"
- Line 45: "large file"

**Recommendations:**
1. Replace "if necessary" with explicit condition
2. Quantify "large file" (e.g., ">10MB")

[...]

### Completeness (Y/20)

**Missing components:**
- [ ] Error recovery (CRITICAL)
- [x] Setup steps
- [x] Validation

**Recommendations:**
1. Add error recovery for migration failure
2. Define rollback procedure

[...]

## Recommendations (Prioritized)

### CRITICAL (Must Fix)
1. Add error recovery (Completeness)
2. Define success criteria for 5 tasks (Success Criteria)

### HIGH (Should Fix)
3. Quantify thresholds (Executability)
4. Add rollback plan (Risk Awareness)

### MEDIUM (Consider)
5. Add task time estimates (Decomposition)

## Conclusion

[Summary and verdict explanation]
```

## Success Criteria

- [ ] Review file created
- [ ] All 8 dimensions scored
- [ ] Agent Execution Test performed
- [ ] Blocking issues counted
- [ ] Scoring cap applied if needed
- [ ] Weighted formula applied correctly
- [ ] Verdict matches score range
- [ ] Recommendations prioritized

## Failure Scenarios

**Scenario 1: Plan file missing**
```
Error: Plan file not found: plans/example-plan.md
```

**Scenario 2: Rubric file missing**
```
Error: Rubric not found: rubrics/executability.md
```
