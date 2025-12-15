# Workflow: Review Execution

## Inputs

- `target_file`
- `review_date`
- `review_mode`
- `model_slug`

## Steps

1. Read `prompts/RULE_REVIEW_PROMPT.md`.
2. Read the contents of `target_file`.
3. Perform the review using the rubric and required structure from
   `prompts/RULE_REVIEW_PROMPT.md`.
4. Produce the final review Markdown content (scores, issues, checklist, tables)
   appropriate to `review_mode`.

## Output

- `review_markdown` (full Markdown review content)
