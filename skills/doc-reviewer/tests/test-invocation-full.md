# Test Invocation: doc-reviewer (FULL Mode)

## Purpose

Verify doc-reviewer skill executes correctly with all 6 dimensions.

## Test Input

```
Use the doc-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
target_files: README.md
timing_enabled: false
```

## Expected Behavior

### Phase 1: Input Validation
-  Date format valid (YYYY-MM-DD)
-  Mode recognized (FULL)
-  Model slug created (claude-sonnet-45)
-  Target file exists

### Phase 2: Review Execution
-  Read README.md completely
-  Load rubrics progressively:
  - accuracy.md (verify file paths, commands)
  - completeness.md (check feature coverage)
  - clarity.md (new user test)
  - structure.md (heading hierarchy)
  - staleness.md (link validation)
  - consistency.md (formatting)
-  Score each dimension (6 scores)
-  Calculate total score (0-100)
-  Determine verdict

### Phase 3: Output
-  Generate recommendations
-  Write to: `reviews/doc-reviews/README-claude-sonnet-45-2026-01-06.md`
-  Confirm: "Review written to: reviews/doc-reviews/README-claude-sonnet-45-2026-01-06.md"

## Expected Output Structure

```markdown
# Documentation Review: README.md

**Reviewed:** 2026-01-06
**Model:** claude-sonnet-45
**Mode:** FULL

## Executive Summary

[Summary paragraph]

**Overall Score:** XX/100
**Verdict:** [EXCELLENT|GOOD|NEEDS_IMPROVEMENT|POOR|INADEQUATE]

## Dimension Scores

- **Accuracy** - Score: X/5, Weight: ×5, Points: Y/25, Status: ...
- **Completeness** - Score: X/5, Weight: ×5, Points: Y/25, Status: ...
- **Clarity** - Score: X/5, Weight: ×4, Points: Y/20, Status: ...
- **Structure** - Score: X/5, Weight: ×3, Points: Y/15, Status: ...
- **Staleness** - Score: X/5, Weight: ×2, Points: Y/10, Status: ...
- **Consistency** - Score: X/5, Weight: ×1, Points: Y/5, Status: ...

## Verification Tables

### Cross-Reference Verification (Accuracy)

- **...** - Line: ..., Type: ..., Status: ..., Notes: ...

### Link Validation (Staleness)

- **...** - Line: ..., Status: ..., Response Time: ..., Action: ...

## Recommendations

### Accuracy (Score: X/25)
[Issues and fixes]

### Completeness (Score: X/25)
[Issues and fixes]

[...]

## Conclusion

[Summary and next steps]
```

## Success Criteria

- [ ] Review file created
- [ ] All 6 dimensions scored
- [ ] Total score calculated correctly
- [ ] Verdict matches score range
- [ ] Recommendations include line numbers
- [ ] Verification tables present
- [ ] No errors during execution

## Failure Scenarios

**Scenario 1: Target file missing**
```
Error: File not found: README.md
```

**Scenario 2: Invalid date format**
```
Error: Invalid date format. Expected YYYY-MM-DD, got: 2026/01/06
```

**Scenario 3: Rubric file missing**
```
Error: Rubric not found: rubrics/accuracy.md
```
