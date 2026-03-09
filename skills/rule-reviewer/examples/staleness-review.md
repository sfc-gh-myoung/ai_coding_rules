# Example: STALENESS Review

> **Note:** As of Scoring Rubric v2.0, STALENESS mode performs an informational check only - no score is produced.

```text
Use the rule-reviewer skill.

target_file: rules/200-python-core.md
review_date: 2025-12-12
review_mode: STALENESS
model: claude-sonnet45
```

Expected output file:

`reviews/rule-reviews/200-python-core-claude-sonnet45-2025-12-12.md` (or `...-01.md`, `...-02.md`, etc. if the base filename already exists)

## Output Contents

STALENESS mode produces a report including:
- LastUpdated age assessment
- Deprecated tools inventory
- Deprecated patterns inventory
- External link validation
- Recommendations for updates

**No numeric score is calculated.** Findings are flagged for remediation in recommendations.
