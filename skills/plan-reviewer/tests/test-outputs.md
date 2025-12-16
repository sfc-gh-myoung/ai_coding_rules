# Output Handling Tests

## Output Path Generation Tests

### Test O1: FULL Mode Path

**Input:**
```text
target_file: plans/MY_PLAN.md
model: claude-sonnet45
review_date: 2025-12-16
review_mode: FULL
```

**Expected:** `reviews/plan-MY_PLAN-claude-sonnet45-2025-12-16.md`

**Verify:** Output file created at expected path.

---

### Test O2: COMPARISON Mode Path

**Input:**
```text
target_files: [plans/a.md, plans/b.md]
model: gpt-52
review_date: 2025-12-16
review_mode: COMPARISON
```

**Expected:** `reviews/plan-comparison-gpt-52-2025-12-16.md`

**Verify:** Output file created at expected path.

---

### Test O3: META-REVIEW Mode Path

**Input:**
```text
target_files: [reviews/r1.md, reviews/r2.md]
original_document: plans/IMPROVE_RULE_LOADING.md
model: claude-opus45
review_date: 2025-12-16
review_mode: META-REVIEW
```

**Expected:** `reviews/meta-IMPROVE_RULE_LOADING-claude-opus45-2025-12-16.md`

**Verify:** Output file created at expected path.

---

## No-Overwrite Safety Tests

### Test O4: First Write (No Conflict)

**Setup:** Ensure `reviews/plan-TEST-model-2025-12-16.md` does not exist.

**Input:** Review that would create that file.

**Expected:** File created without suffix.

**Verify:** `reviews/plan-TEST-model-2025-12-16.md` exists.

---

### Test O5: Second Write (First Conflict)

**Setup:** Create `reviews/plan-TEST-model-2025-12-16.md`.

**Input:** Another review with same parameters.

**Expected:** `reviews/plan-TEST-model-2025-12-16-01.md` created.

**Verify:** Both files exist; original unchanged.

---

### Test O6: Third Write (Second Conflict)

**Setup:** Create both:
- `reviews/plan-TEST-model-2025-12-16.md`
- `reviews/plan-TEST-model-2025-12-16-01.md`

**Input:** Another review with same parameters.

**Expected:** `reviews/plan-TEST-model-2025-12-16-02.md` created.

**Verify:** Three files exist; originals unchanged.

---

### Test O7: Many Conflicts

**Setup:** Create files -01 through -09.

**Input:** Another review with same parameters.

**Expected:** `-10.md` suffix (not `-010.md`).

**Verify:** Suffix format correct for double digits.

---

## Model Slug Normalization Tests

### Test O8: Space to Hyphen

**Input:** `model: Claude Sonnet 4.5`

**Expected slug:** `claude-sonnet-45`

**Verify:** Output filename uses normalized slug.

---

### Test O9: Special Characters Removed

**Input:** `model: GPT-5.2 (beta)`

**Expected slug:** `gpt-52-beta`

**Verify:** Parentheses and periods removed.

---

### Test O10: Already Valid Slug

**Input:** `model: claude-sonnet45`

**Expected slug:** `claude-sonnet45` (unchanged)

**Verify:** No modification to valid slug.

---

### Test O11: Multiple Spaces/Hyphens Collapsed

**Input:** `model: Claude   Sonnet---45`

**Expected slug:** `claude-sonnet-45`

**Verify:** Multiple separators collapsed to single hyphen.

---

## File Write Success/Failure Tests

### Test O12: Successful Write

**Input:** Valid review with write permissions.

**Expected:** Success message:
```
✓ Review complete

OUTPUT_FILE: reviews/plan-X-model-date.md
Target: plans/X.md
Mode: FULL
Model: model

Summary:
[scores]
Verdict: [verdict]
```

**Verify:** File exists with correct content.

---

### Test O13: Write Failure Fallback

**Input:** Review where file write fails (simulate permission error).

**Expected:**
1. `OUTPUT_FILE: reviews/plan-X-model-date.md` printed
2. Full review content printed as markdown

**Verify:** Review content available for manual save.

---

### Test O14: Reviews Directory Creation

**Setup:** Delete `reviews/` directory.

**Input:** Run a review.

**Expected:** `reviews/` directory created; file written.

**Verify:** Directory and file both exist.

---

## Content Verification Tests

### Test O15: Required Sections Present (FULL)

**Input:** FULL mode review.

**Expected sections:**
- [ ] Scores (Weighted) table
- [ ] Overall Score Interpretation table
- [ ] Agent Executability Verdict
- [ ] Executability Audit
- [ ] Completeness Audit
- [ ] Success Criteria Audit
- [ ] Plan Perspective Checklist
- [ ] Critical Issues
- [ ] Improvements
- [ ] Minor Suggestions
- [ ] Specific Recommendations

**Verify:** All sections present in output file.

---

### Test O16: Required Sections Present (COMPARISON)

**Input:** COMPARISON mode review.

**Expected sections:**
- [ ] Plans Reviewed table
- [ ] Comparative Scores table
- [ ] Verdict by Plan table
- [ ] Head-to-Head Analysis
- [ ] Recommendation with Winner

**Verify:** All sections present in output file.

---

### Test O17: Required Sections Present (META-REVIEW)

**Input:** META-REVIEW mode review.

**Expected sections:**
- [ ] Reviews Summary table
- [ ] Consistency Analysis
- [ ] Issue Detection Comparison
- [ ] Meta-Review Scores
- [ ] Calibration Assessment
- [ ] Consensus Determination
- [ ] Recommendation

**Verify:** All sections present in output file.

---

## Edge Case Tests

### Test O18: Plan Name with Special Characters

**Input:** `target_file: plans/my-plan_v2.0.md`

**Expected:** `reviews/plan-my-plan_v20-model-date.md`
(Period removed to avoid extension confusion)

**Verify:** Output path is filesystem-safe.

---

### Test O19: Very Long Plan Name

**Input:** Plan with 100+ character filename.

**Expected:** Either truncated or error gracefully.

**Verify:** Output path doesn't exceed OS limits.

---

### Test O20: Unicode in Model Name

**Input:** `model: Cläude Sönnet`

**Expected:** Unicode normalized or transliterated.

**Verify:** Output filename is ASCII-safe.

