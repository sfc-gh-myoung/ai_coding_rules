# Example: FOCUSED Review

```text
Use the rule-reviewer skill.

target_file: rules/202-markup-config-validation.md
review_date: 2025-12-12
review_mode: FOCUSED
model: claude-sonnet45

Focus Areas: Actionability, Completeness
```

Expected output file:

`reviews/rule-reviews/202-markup-config-validation-claude-sonnet45-2025-12-12.md` (or `...-01.md`, `...-02.md`, etc. if the base filename already exists)

## Scoring (Scoring Rubric v2.0)

FOCUSED mode scores only Actionability and Completeness:

| Dimension | Weight | Max Points |
|-----------|--------|------------|
| Actionability | 6 | 30 |
| Completeness | 3 | 15 |
| **Total** | - | **45** |

**Verdict thresholds for FOCUSED mode:**
- 40-45: EXECUTABLE
- 34-39: EXECUTABLE_WITH_REFINEMENTS
- 23-33: NEEDS_REFINEMENT
- <23: NOT_EXECUTABLE
