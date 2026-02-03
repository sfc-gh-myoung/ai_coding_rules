# Consistency Check Workflow

**Purpose:** Ensure score consistency across multiple reviews of the same plan, including score locking for iterative refinement.

## Score Locking Protocol

### When to Apply Score Locking

Score locking applies when reviewing a plan that has been previously reviewed (DELTA mode or re-review).

**Apply score locking IF:**
- Previous review exists for this plan
- Previous score ≥8/10 for a dimension
- `full_rescore: false` (default)

**Skip score locking IF:**
- No previous review exists
- `full_rescore: true` explicitly requested
- Previous score <8/10 (too much room for genuine change)

### Score Locking Rules

**For dimensions with prior score ≥8/10:**

1. **Do NOT re-score from scratch**
   - Load prior score from baseline review
   - Verify issues from prior review are still fixed
   - Check for new issues only

2. **Score change options:**
   - **Same score:** No changes detected
   - **+1 point:** Improvements detected (issues fixed, clarity added)
   - **-1 point:** Regressions detected (new issues, previously fixed issues returned)

3. **Changes >±1 require documented justification:**
   - List specific issues that changed
   - Explain why change exceeds normal variance
   - Include line numbers for evidence

### Variance Thresholds by Dimension

| Dimension | Weight | Max Variance | Justification Required If |
|-----------|--------|--------------|---------------------------|
| Executability | 4 | ±1 point | >±1 |
| Completeness | 4 | ±1 point | >±1 |
| Success Criteria | 4 | ±1 point | >±1 |
| Scope | 3 | ±1 point | >±1 |
| Dependencies | 2 | ±0.5 points | >±0.5 |
| Decomposition | 1 | ±0.5 points | >±0.5 |
| Context | 1 | ±0.5 points | >±0.5 |
| Risk Awareness | 1 | ±0.5 points | >±0.5 |

**Overall score variance:** ±2 points without justification

### Discrepancy Documentation

When score changes exceed variance threshold, document:

```markdown
### Consistency Notes

| Dimension | Prior | Current | Change | Status | Justification |
|-----------|-------|---------|--------|--------|---------------|
| Executability | 8/10 | 7/10 | -1 | FLAGGED | New issue at L45: "as needed" |
| Completeness | 7/10 | 8/10 | +1 | OK | Added error recovery (L120-135) |
| Success Criteria | 9/10 | 9/10 | 0 | OK | No change |
| Scope | 6/10 | 8/10 | +2 | FLAGGED | See justification below |

**Scope +2 Justification:**
- Prior review missed "Future Work" section (L200-210) that provides explicit exclusions
- This was a counting error in prior review, not plan improvement
- Evidence: "Future Work" section existed in prior plan version (diff shows no changes L200-210)
```

## Inter-Review Consistency Check

### Step 1: Detect Prior Reviews

```bash
# Find existing reviews for this plan
PLAN_NAME="PLAN_RULES_SPLIT"
ls reviews/plan-reviews/${PLAN_NAME}*.md | sort
```

**Output example:**
```
reviews/plan-reviews/PLAN_RULES_SPLIT-claude-sonnet-4-2026-01-15.md
reviews/plan-reviews/PLAN_RULES_SPLIT-claude-sonnet-4-2026-01-18.md
reviews/plan-reviews/PLAN_RULES_SPLIT-claude-sonnet-4-2026-01-21.md
```

### Step 2: Load Most Recent Prior Review

Extract from prior review:
- Overall score (e.g., 78/100)
- Verdict (e.g., NEEDS_WORK)
- Dimension scores (8 values)
- Blocking issues list with line numbers

### Step 3: Calculate Variance

**Formula:**
```
Variance = abs(current_score - prior_score)
```

**Expected variance by metric:**

| Metric | Expected | High Variance Threshold |
|--------|----------|------------------------|
| Blocking Issues | ±2 | >3 issues |
| Per Dimension | ±1 point | >1 point |
| Overall Score | ±5 points | >5 points |

### Step 4: Assess Consistency

**If variance ≤ expected:** ✅ CONSISTENT
- Reviews align within acceptable range
- No investigation needed

**If variance > expected:** ⚠️ HIGH VARIANCE
- Investigation required
- Check for:
  - Counting methodology differences
  - Pattern interpretation drift
  - Non-Issues list application
  - Overlap resolution consistency

### Step 5: Report Variance

Include in review output:

```markdown
## Review Consistency Check

**Prior review:** PLAN_RULES_SPLIT-claude-sonnet-4-2026-01-18.md
**Prior score:** 72/100 (NEEDS_WORK)
**Current score:** 78/100 (NEEDS_WORK)
**Variance:** +6 points ⚠️ HIGH VARIANCE

### Dimension Comparison

| Dimension | Prior | Current | Delta | Status |
|-----------|-------|---------|-------|--------|
| Executability | 6/10 | 7/10 | +1 | OK ✅ |
| Completeness | 7/10 | 8/10 | +1 | OK ✅ |
| Success Criteria | 7/10 | 8/10 | +1 | OK ✅ |
| Scope | 5/10 | 7/10 | +2 | FLAGGED ⚠️ |
| Dependencies | 8/10 | 8/10 | 0 | OK ✅ |
| Decomposition | 8/10 | 8/10 | 0 | OK ✅ |
| Context | 6/10 | 7/10 | +1 | OK ✅ |
| Risk Awareness | 7/10 | 7/10 | 0 | OK ✅ |

### Variance Investigation

**Scope +2 investigation:**
- Prior review: Counted 5 unbounded phrases
- Current review: Counted 3 unbounded phrases
- Difference: 2 phrases were "Future Work" items (should not count as unbounded per Out-of-Scope Handling Rule)
- Resolution: Prior review error, current count is correct

**Conclusion:** Variance explained by prior review counting error. Current review is accurate.
```

## High Variance Recommendations

### If Variance is Unexplained

1. **Re-run current review with worksheet verification**
   - Ensure all worksheets completed
   - Verify line-by-line enumeration

2. **Check rubric interpretation**
   - Re-read relevant rubric definition
   - Verify pattern matching against inventory

3. **Report to user**
   ```markdown
   ⚠️ HIGH VARIANCE ALERT
   
   Prior review score: 72/100
   Current review score: 85/100
   Variance: +13 points (>5 expected)
   
   This variance exceeds expected tolerance. Possible causes:
   1. Plan was significantly improved between reviews
   2. Different counting methodology applied
   3. Rubric interpretation changed
   
   Recommendation: Review worksheets from both reviews to identify specific differences.
   ```

### If Pattern Across Multiple Reviews

If high variance occurs across 3+ reviews:

1. **Flag for rubric clarification**
   - Identify specific pattern causing variance
   - Propose clarification to rubric

2. **Document in improvement backlog**
   ```markdown
   ## Rubric Improvement Needed
   
   **Dimension:** Scope
   **Issue:** "Future Work" section handling inconsistent
   **Variance pattern:** ±2 points across 5 reviews
   **Proposed fix:** Add explicit "Future Work = Out-of-Scope" rule
   ```

## Consistency Check Checklist

Before finalizing review with prior reviews:

- [ ] Prior reviews identified?
- [ ] Most recent prior score loaded?
- [ ] Variance calculated per dimension?
- [ ] High variance items investigated?
- [ ] Discrepancy documentation complete?
- [ ] Score locking applied where appropriate?
- [ ] Consistency section included in output?

## Integration with DELTA Mode

When running in DELTA mode:

1. Consistency check is MANDATORY
2. Score locking is enabled by default
3. All variance must be explained
4. Issue tracking table required (see `workflows/issue-inventory.md`)

**See:** `workflows/delta-review.md` for DELTA-specific workflow
