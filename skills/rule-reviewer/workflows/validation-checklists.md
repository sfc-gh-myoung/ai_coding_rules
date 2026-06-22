# Validation Checklists

Consolidated pre/during/post checks for every review. See also `workflows/review-verification.md`.

## Pre-execution

- [ ] `target_file` exists.
- [ ] `review_date` matches YYYY-MM-DD format.
- [ ] `review_mode` is valid enum (`FULL` | `FOCUSED` | `STALENESS`).
- [ ] `model` slug is lowercase-hyphenated.

## During execution

- [ ] Schema validation attempted (or skipped with reason for project files).
- [ ] Agent Execution Test completed.
- [ ] Line count measured (`wc -l`).
- [ ] All dimensions scored (FULL mode — 6 dimensions).
- [ ] Each score has rationale.
- [ ] Critical issues identified.
- [ ] Rule Size flags applied if applicable.
- [ ] Recommendations include line numbers and are prioritized.

## Post-execution

- [ ] Review file written to `{output_root}/rule-reviews/`.
- [ ] Path confirmed.
- [ ] No overwrites occurred.
- [ ] Review file ≥ 2500 bytes (drift check).

## Expected review size

Typical FULL mode review: 3000–8000 bytes.

- If < 2000 bytes: STOP, expand analysis with more specific findings.
- If 2000–13500 bytes: acceptable range.
- If > 13500 bytes: STOP, consolidate redundant content before writing.
