# Scoring System (100 points)

> **Scoring Rubric v2.0** — 6 scored dimensions, 100 points total.

## Formula

- **Raw Score Range:** 0–10 per dimension.
- **Formula:** `Raw × Weight = Points`.

## Scored dimensions

| Dimension | Weight | Max Points | Focus |
|---|---|---|---|
| Actionability | 3.0 | 30 | Can agents execute without judgment? |
| Rule Size | 2.5 | 25 | Within 500-line target? (deterministic) |
| Parsability | 1.5 | 15 | Schema valid? |
| Completeness | 1.5 | 15 | All scenarios covered? |
| Consistency | 1.0 | 10 | Internal alignment correct? |
| Cross-Agent Consistency | 0.5 | 5 | Works across all agents? |

## Informational only (not scored)

- **Token Efficiency** — merged into Rule Size; findings appear in recommendations.
- **Staleness** — flagged in recommendations; not scored.

## Hard caps

| Condition | Effect |
|---|---|
| > 600 lines | Total score capped at 70/100 |
| > 700 lines | Total score capped at 50/100 |
| ≥ 6 blocking issues | Total score capped at 80/100 |
| ≥ 10 blocking issues | Verdict forced to NOT_EXECUTABLE |

## Example calculation (Actionability)

- Raw score: 8/10
- Weight: 3.0
- Points: `8 × 3.0 = 24`

## Detailed rubrics

Per-dimension scoring criteria live in `rubrics/<dimension>.md`:

- `rubrics/actionability.md`
- `rubrics/completeness.md`
- `rubrics/consistency.md`
- `rubrics/parsability.md`
- `rubrics/token-efficiency.md`
- `rubrics/rule-size.md` (100% deterministic — line count)
- `rubrics/staleness.md`
- `rubrics/cross-agent-consistency.md`
