# Workflow: Review Execution

## Inputs

- `target_file`
- `review_date`
- `review_mode`
- `model_slug`

## Steps

1. Read `SKILL.md` (colocated in this skill folder, contains review rubric).
2. Read the contents of `target_file`.
3. Perform the review using the rubric and required structure from
   `SKILL.md`.
4. Produce the final review Markdown content (scores, issues, checklist, tables)
   appropriate to `review_mode`.

## Output

- `review_markdown` (full Markdown review content)
