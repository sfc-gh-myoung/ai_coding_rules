# Example: STALENESS Review

```text
Use the rule-reviewer skill.

target_file: rules/200-python-core.md
review_date: 2025-12-12
review_mode: STALENESS
model: claude-sonnet45
```

Expected output file:

`reviews/rule-reviews/200-python-core-claude-sonnet45-2025-12-12.md` (or `...-01.md`, `...-02.md`, etc. if the base filename already exists)
