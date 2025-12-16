# Review Mode Tests

## FULL Mode Tests

### Test F1: All Dimensions Scored

**Input:** Valid plan file in FULL mode

**Expected:** Output contains scores for all 8 dimensions:
- Executability (weighted)
- Completeness (weighted)
- Success Criteria (weighted)
- Scope (weighted)
- Decomposition
- Dependencies
- Context
- Risk Awareness

**Verify:** Scores table has 8 rows with non-empty values.

---

### Test F2: Point Score Calculation

**Input:** Plan where:
- Executability = 4/5
- Completeness = 5/5
- Success Criteria = 3/5
- Scope = 4/5
- Dependencies = 5/5
- Decomposition = 4/5
- Context = 3/5
- Risk Awareness = 3/5

**Expected:**
- Executability: 4 × 4 = 16/20
- Completeness: 5 × 4 = 20/20
- Success Criteria: 3 × 4 = 12/20
- Scope: 4 × 3 = 12/15
- Dependencies: 5 × 2 = 10/10
- Decomposition: 4 × 1 = 4/5
- Context: 3 × 1 = 3/5
- Risk Awareness: 3 × 1 = 3/5
- **Total: 80/100**

**Verify:** Total score matches manual calculation.

---

### Test F3: Verification Tables Generated

**Input:** Valid plan file in FULL mode

**Expected:** Output contains:
1. Executability Audit table
2. Completeness Audit table
3. Success Criteria Audit table

**Verify:** All 3 tables present with data.

---

### Test F4: Verdict Assignment - EXECUTABLE

**Input:** Plan scoring 92/100 with no critical dimension ≤2/5

**Expected:** Verdict = EXECUTABLE

**Verify:** Verdict section shows "EXECUTABLE"

---

### Test F5: Verdict Assignment - NEEDS_REFINEMENT

**Input:** Plan scoring 70/100

**Expected:** Verdict = NEEDS_REFINEMENT

**Verify:** Verdict section shows "NEEDS_REFINEMENT"

---

### Test F6: Verdict Override - Critical Dimension Low

**Input:** Plan scoring 83/100 but Executability = 2/5

**Expected:** Verdict = NEEDS_REFINEMENT (override applied)

**Verify:** Output notes critical dimension override.

---

### Test F7: Scoring Impact Rules Applied

**Input:** Plan with 10 ambiguous phrases

**Expected:** Executability ≤ 2/5 (per algorithmic rules)

**Verify:** Executability score respects Scoring Impact Rules.

---

### Test F8: Plan Perspective Checklist Answered

**Input:** Valid plan file in FULL mode

**Expected:** Checklist section with all 5 questions answered

**Verify:** All checkboxes marked with explanations.

---

## COMPARISON Mode Tests

### Test C1: Two Plans Compared

**Input:**
```text
target_files: [plans/plan-a.md, plans/plan-b.md]
task_description: Implement feature X
review_mode: COMPARISON
```

**Expected:** Output contains:
- Plans Reviewed table (2 entries)
- Comparative Scores table
- Winner per dimension
- Overall winner declaration

**Verify:** Both plans scored; winner identified.

---

### Test C2: Three+ Plans Compared

**Input:**
```text
target_files: [plans/a.md, plans/b.md, plans/c.md]
task_description: Test task
review_mode: COMPARISON
```

**Expected:** All 3 plans in comparison table.

**Verify:** Comparative Scores table has 3 columns for plans.

---

### Test C3: Tie Breaking

**Input:** Two plans both scoring 80/100

**Expected:** Tie broken by critical dimension sum; if still tied, documented.

**Verify:** Winner declared or tie explicitly noted.

---

### Test C4: Head-to-Head Analysis

**Input:** Two plans in COMPARISON mode

**Expected:** Per-dimension analysis with evidence for each winner.

**Verify:** Each dimension has explanation with line citations.

---

### Test C5: Synthesis Recommendations

**Input:** Two plans with complementary strengths

**Expected:** Recommendations for combining best elements.

**Verify:** "Synthesis Recommendations" section present.

---

## META-REVIEW Mode Tests

### Test M1: Score Variance Calculated

**Input:**
```text
target_files: [reviews/r1.md, reviews/r2.md, reviews/r3.md]
review_mode: META-REVIEW
```
Where r1=87/100, r2=73/100, r3=83/100

**Expected:** Score variance = 14 points (87-73)

**Verify:** "Score Variance: 14 points" in output.

---

### Test M2: Issue Detection Comparison

**Input:** Multiple reviews of same document

**Expected:** Table showing which review found which issues.

**Verify:** Issue Detection Comparison table present with consensus counts.

---

### Test M3: Meta-Review Scores Assigned

**Input:** Multiple reviews in META-REVIEW mode

**Expected:** Each review scored on:
- Thoroughness (5)
- Evidence Quality (5)
- Calibration (5)
- Actionability (5)
Total: /20

**Verify:** Meta-Review Scores table with 4 dimensions per review.

---

### Test M4: Consensus Score Calculated

**Input:** Reviews with different scores

**Expected:** Weighted consensus score calculated.

**Verify:** Consensus Determination section with calculation shown.

---

### Test M5: Most Reliable Review Identified

**Input:** Multiple reviews in META-REVIEW mode

**Expected:** One review identified as most reliable with rationale.

**Verify:** "Most Reliable Review" declared with meta-score.

---

### Test M6: Calibration Issues Flagged

**Input:** Review that scored 5/5 on dimension despite findings that should cap it lower

**Expected:** Calibration issue noted in assessment.

**Verify:** "Calibration Issues Found" section lists specific problems.

---

### Test M7: High Variance Warning

**Input:** Reviews with >15 point variance

**Expected:** High variance warning with investigation recommendation.

**Verify:** ⚠️ warning icon and "investigate" recommendation.

---

## Cross-Mode Tests

### Test X1: Same Plan, Different Modes

**Input:** Run FULL mode on a plan, then include that review in META-REVIEW

**Expected:** Both modes complete successfully; META-REVIEW can parse FULL output.

**Verify:** No parsing errors; scores extracted correctly.

---

### Test X2: Mode Parameter Validation

**Input:** Invalid mode "QUICK"

**Expected:** Error before any processing.

**Verify:** Error message; no output file created.

---

### Test X3: Empty Target Files

**Input:** Empty target_files array

**Expected:** Error for insufficient files.

**Verify:** Appropriate error message per mode requirements.

