# Determinism Requirements (doc-reviewer)

## Purpose

Reduce score variance from ±5–8 points to <±2 points across runs by enforcing
strict ordering and systematic counting.

## Mandatory Behaviors (ALWAYS DO)

1. **Batch-load all rubrics BEFORE reading target documentation** — See
   `workflows/review-execution.md` Phase 1
2. **Create ALL 6 verification tables BEFORE reading target** — Empty
   templates from each rubric
3. **Read target documentation from line 1 to END** — No skipping sections
4. **Fill verification tables systematically** — One dimension at a time,
   in order
5. **Check Non-Issues list for EACH flagged item** — Remove false positives
   with notes
6. **Apply overlap resolution rules** — Assign each issue to ONE dimension
   only
7. **Use Score Decision Matrix for EVERY score** — Look up tier from
   count/percentage
8. **Include completed verification tables in review output** — As evidence
   for scoring

## Prohibited Behaviors (NEVER DO)

1. **NEVER read target documentation before loading rubrics** — Anchors
   interpretation incorrectly
2. **NEVER skip table creation** — Leads to inconsistent counting
3. **NEVER estimate scores without counting** — Creates variance
4. **NEVER double-count issues across dimensions** — Use overlap resolution
5. **NEVER flag items without checking Non-Issues list** — Creates false
   positives
6. **NEVER omit verification tables from review output** — Prevents
   verification
7. **NEVER score on "feel" or "impression"** — Use decision matrices only
8. **NEVER start scoring before completing all tables** — Order matters

## Expected Variance Tolerance

| Component | Expected Variance |
|-----------|-------------------|
| Issue counts per dimension | ±1 item |
| Dimension scores | ±1 point |
| Overall score | ±2 points |

If variance exceeds tolerance: review table counting, check Non-Issues
application, verify overlap resolution.

## Self-Verification Checklist

Before submitting ANY review, verify:

- [ ] All 7 rubric files read BEFORE reading target documentation?
- [ ] All 6 verification tables created (even if empty)?
- [ ] Target documentation read line 1 to END (no skipping)?
- [ ] Each table filled using only rubric-defined criteria?
- [ ] Non-Issues list checked for EVERY flagged item?
- [ ] Overlap resolution applied to multi-dimension issues?
- [ ] All verification tables included in review output?
- [ ] All scores from Score Decision Matrix lookups?

If ANY checkbox is NO: review is INVALID. Regenerate from Phase 1.
