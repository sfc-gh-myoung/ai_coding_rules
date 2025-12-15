# Rule Reviewer Skill (How to Use)

This skill automates running the Agent-Centric Rule Review prompt and writing the
result to `reviews/` with the required filename format.

## Load the skill

Load:

```text
@skills/rule-reviewer/prompt.md
```

## Trigger (example)

```text
Use the rule-reviewer skill.

target_file: rules/810-project-readme.md
review_date: 2025-12-12
review_mode: FULL
model: claude-sonnet45

Write the result to the required OUTPUT_FILE under reviews/ (overwrite).
```

## Examples

- `@skills/rule-reviewer/examples/full-review.md`
- `@skills/rule-reviewer/examples/focused-review.md`
- `@skills/rule-reviewer/examples/staleness-review.md`

## What you get

- A file written (overwritten if it exists):
  - `reviews/810-project-readme-claude-sonnet45-2025-12-12.md`
- A short confirmation message containing:
  - `OUTPUT_FILE` path
  - target file reviewed
  - selected review mode
  - model slug used
