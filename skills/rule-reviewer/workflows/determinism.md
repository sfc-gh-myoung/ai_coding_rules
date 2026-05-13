# Workflow: Determinism Requirements

**Purpose:** Reduce score variance from ±5-8 points to <±2 points across runs.

Full determinism contract for the `rule-reviewer` skill. SKILL.md carries the summary; this file is authoritative.

## Mandatory Behaviors (ALWAYS DO)

1. **Batch-load all rubrics BEFORE reading target rule** — see `workflows/review-execution.md` Phase 1.
2. **Create ALL 8 inventories BEFORE reading target rule** — empty templates from each rubric.
3. **Read target rule from line 1 to END** — no skipping sections.
4. **Fill inventories systematically** — one dimension at a time, in order.
5. **Check Non-Issues list for EACH flagged item** — remove false positives with notes.
6. **Apply overlap resolution rules** — assign each issue to ONE dimension only.
7. **Use Score Decision Matrix for EVERY score** — look up tier from count/percentage.
8. **Include completed inventories in review output** — as evidence for scoring.

## Prohibited Behaviors (NEVER DO)

1. **NEVER read target rule before loading rubrics** — anchors interpretation incorrectly.
2. **NEVER skip inventory creation** — leads to inconsistent counting.
3. **NEVER estimate scores without counting** — creates variance.
4. **NEVER double-count issues across dimensions** — use overlap resolution.
5. **NEVER flag items without checking Non-Issues list** — creates false positives.
6. **NEVER omit inventories from review output** — prevents verification.
7. **NEVER score on "feel" or "impression"** — use decision matrices only.
8. **NEVER start scoring before completing all inventories** — order matters.

## Expected Variance Tolerance

| Component | Expected Variance |
|-----------|-------------------|
| Issue counts per dimension | ±1 item |
| Dimension scores | ±1 point |
| Overall score | ±2 points |

**If variance exceeds tolerance:** Review inventory counting, check Non-Issues application, verify overlap resolution.

## Self-Verification Checklist

Before submitting ANY review, verify:

- [ ] All 9 rubric files read BEFORE reading target rule?
- [ ] All 8 inventories created (even if empty)?
- [ ] Line count measured (`wc -l`) for Rule Size?
- [ ] Target rule read line 1 to END (no skipping)?
- [ ] Each inventory filled using only rubric-defined patterns?
- [ ] Non-Issues list checked for EVERY flagged item?
- [ ] Overlap resolution applied to multi-dimension issues?
- [ ] All inventories included in review output?
- [ ] All scores from Score Decision Matrix lookups?

**If ANY checkbox is NO:** Review is INVALID. Regenerate from Phase 1.
