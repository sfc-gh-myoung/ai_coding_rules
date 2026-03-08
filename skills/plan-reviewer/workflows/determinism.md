# Determinism Requirements

**Purpose:** This skill MUST produce consistent results across multiple runs. Variance >±2 points indicates implementation error.

## Mandatory Behaviors (ALWAYS DO)

1. **Batch Load Rubrics:** Read ALL 9 files (8 rubrics + _overlap-resolution.md) BEFORE reading plan
   - Why: Locks in interpretation before encountering plan content
   - Result: Same definitions applied consistently

2. **Create Worksheets First:** Prepare ALL 8 empty worksheets BEFORE reading plan
   - Why: Forces systematic enumeration
   - Result: No skipped sections

3. **Systematic Enumeration:** Read plan from line 1 to END (no skipping)
   - Why: Prevents missing issues in "boring" sections
   - Result: Complete coverage

4. **Use Pattern Lists:** Only count patterns from rubric inventories (don't invent)
   - Why: Eliminates interpretation variance
   - Result: Same patterns matched every time

5. **Check Non-Issues:** ALWAYS filter false positives before final count
   - Why: Reduces false positive rate
   - Result: More accurate scores

6. **Apply Overlap Resolution:** ALWAYS check `_overlap-resolution.md` for ambiguous issues
   - Why: Ensures same issue counted in same dimension
   - Result: No dimension overlap

7. **Include Worksheets:** ALWAYS copy completed worksheets into review output
   - Why: Provides audit trail for scoring decisions
   - Result: Verifiable reviews

8. **Use Score Matrices:** Look up scores in decision tables (no interpretation)
   - Why: Eliminates subjective scoring
   - Result: Same raw count → same score

## Prohibited Behaviors (NEVER DO)

1. ❌ **Scoring without worksheets:** Skipping worksheet creation
   - Problem: Incomplete enumeration, items missed
   - Consequence: False negatives, score variance

2. ❌ **Skipping sections:** "This section looks good, moving on"
   - Problem: Missing issues in skipped sections
   - Consequence: False negatives

3. ❌ **Double-counting:** Same issue counted in multiple dimensions
   - Problem: Inflated scores, dimension overlap
   - Consequence: Artificially low overall score

4. ❌ **Inventing patterns:** Flagging issues not in pattern inventory
   - Problem: Inconsistent interpretation
   - Consequence: Variance between runs

5. ❌ **Subjective judgment:** Using "looks like" or "seems like" for borderline cases
   - Problem: Non-deterministic decisions
   - Consequence: Score variance on same plan

6. ❌ **Progressive disclosure:** Reading rubrics one-at-a-time during review
   - Problem: Interpretation drift across dimensions
   - Consequence: Overlapping ownership, inconsistent severity

7. ❌ **Omitting worksheets:** Not including worksheets in review output
   - Problem: No audit trail, can't verify scoring
   - Consequence: Unverifiable reviews

8. ❌ **Ignoring decision matrices:** Making up scores based on "feel"
   - Problem: Subjective scoring
   - Consequence: Variance in score for same raw counts

## Expected Variance Tolerance

**Between multiple runs on same plan (no changes):**
- Blocking issues count: ±1 issue (acceptable, borderline cases may vary)
- Dimension raw scores: ±1 point (acceptable, tie-breaking may differ)
- Overall score: ±2 points (acceptable, cumulative rounding)

**If variance exceeds tolerance:**
1. Check if worksheets were created for BOTH runs
2. Check if Non-Issues lists were applied
3. Check if overlap resolution was followed
4. Check if same pattern lists were used
5. Report discrepancy with evidence from both runs

## Self-Verification Checklist

**Before submitting review, verify:**
- [ ] All 9 files read (8 rubrics + overlap resolution)?
- [ ] All 8 worksheets created and filled?
- [ ] Plan read from line 1 to END (no skipping)?
- [ ] Only patterns from inventories used (no invented patterns)?
- [ ] Non-Issues list applied to filter false positives?
- [ ] Overlap resolution applied to ambiguous issues?
- [ ] All 8 worksheets included in review output?
- [ ] Scores looked up in decision matrices (not invented)?

**If ANY checkbox is NO:** Review is INVALID, must be regenerated.

## Quality Signals

**High-quality review (deterministic):**
- ✅ Worksheets included for all 8 dimensions
- ✅ Line numbers referenced throughout
- ✅ Issues tied to specific pattern inventory items
- ✅ Overlap resolution rules cited
- ✅ Non-Issues patterns referenced for skipped items
- ✅ Score calculation shown with matrix lookup

**Low-quality review (non-deterministic):**
- ❌ No worksheets included
- ❌ Vague references ("several issues found")
- ❌ Invented patterns not in inventory
- ❌ Same issue counted in multiple dimensions
- ❌ No explanation for skipped borderline cases
- ❌ Scores without calculation shown
