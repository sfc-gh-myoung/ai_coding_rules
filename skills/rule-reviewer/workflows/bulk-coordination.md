# Workflow: Bulk Review Coordination

Context preservation contract for when `rule-reviewer` is invoked by `bulk-rule-reviewer`.

## Problem

When invoked repeatedly in a bulk run, the rule-reviewer skill may experience context drift after 10–20 rules. Symptoms: reviews shrink in byte size, line references become less specific, recommendations become generic.

## Structural Safeguards

1. **Pre-write verification.** Check review has ≥15 line refs, score table, verdict before writing. (See `workflows/review-verification.md`.)
2. **Post-write size check.** If <2500 bytes, flag potential drift and do NOT accept the review.
3. **Periodic refresh.** Every 10 rules, re-read `bulk-rule-reviewer/CRITICAL_CONTEXT.md` to re-anchor context.

## Interaction Contract

- `bulk-rule-reviewer` invokes this skill **once per rule file**.
- This skill **never** implements batch/loop logic itself; bulk orchestration is the caller's responsibility.
- If a rule review fails inside a bulk run, this skill reports failure for that rule and continues processing is controlled by `bulk-rule-reviewer`.

**See:** `workflows/review-execution.md` Pre-Write Output Verification section.
