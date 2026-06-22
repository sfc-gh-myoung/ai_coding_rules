# Verdict Thresholds (doc-reviewer)

Mapping of total score to verdict label.

## Score ranges

| Range | Verdict | Meaning |
|---|---|---|
| 90–100 | EXCELLENT | High-quality documentation |
| 80–89 | GOOD | Minor improvements needed |
| 60–79 | NEEDS_IMPROVEMENT | Significant updates required |
| 40–59 | POOR | Major revision needed |
| < 40 | INADEQUATE | Rewrite from scratch |

## Critical dimension overrides

- Accuracy ≤ 4/10 → minimum NEEDS_IMPROVEMENT.
- Completeness ≤ 4/10 → minimum NEEDS_IMPROVEMENT.
- Both ≤ 4/10 → POOR.
