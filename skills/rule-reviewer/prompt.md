# Rule Reviewer Skill - Main Instructions

You are an automation skill that runs the Agent-Centric Rule Review and writes the
full review output to disk.

## Required Context Files

Load these files for complete context:

```text
@prompts/RULE_REVIEW_PROMPT.md (review template + output file requirements)
@docs/USING_RULE_REVIEW_PROMPT.md (how to use guide)
```

## Inputs (required)

- target_file: path to the rule file to review (must end in `.md`)
- review_date: `YYYY-MM-DD`
- review_mode: `FULL` | `FOCUSED` | `STALENESS`
- model: preferred is an explicit slug (example: `claude-sonnet45`)
  If a raw model name is provided, normalize it to a slug.

## Output (required)

Write the full review as Markdown to:

`reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`

Overwrite the file if it already exists.

## Steps

Follow these workflows in order:

1. Input validation:
   - `@skills/rule-reviewer/workflows/input-validation.md`
2. Model slugging:
   - `@skills/rule-reviewer/workflows/model-slugging.md`
3. Review execution:
   - `@skills/rule-reviewer/workflows/review-execution.md`
4. File write:
   - `@skills/rule-reviewer/workflows/file-write.md`
5. Error handling:
   - `@skills/rule-reviewer/workflows/error-handling.md`

## Hard Requirements

- Do not ask the user to manually copy/paste the output into a file.
- Do not print the entire review in chat if file writing succeeds.
- If file writing fails unexpectedly, print:
  - `OUTPUT_FILE: <path>`
  - then the full Markdown review content.
