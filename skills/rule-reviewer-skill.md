# Rule Reviewer Skill

## Skill Purpose

Run Agent-Centric Rule Reviews using `prompts/RULE_REVIEW_PROMPT.md` and write the
full review output to `reviews/<rule-name>-<model>-<YYYY-MM-DD>.md` (overwrite).

## Prerequisites

- Access to:
  - `@prompts/RULE_REVIEW_PROMPT.md`
  - `@docs/USING_RULE_REVIEW_PROMPT.md`
  - the rule file to review (e.g., `@rules/810-project-readme.md`)
  - write access to `reviews/`

## Inputs (required)

- **target_file:** path to the `.md` rule file to review
- **review_date:** `YYYY-MM-DD`
- **review_mode:** `FULL | FOCUSED | STALENESS`
- **model:** preferred slug (e.g., `claude-sonnet45`)

## Output (required)

Write the full review to:

`reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`

Overwrite the file if it already exists.

## Procedure

1. Validate inputs (date format, mode enum, `.md` target).
2. Compute:
   - `rule_name` from `target_file` basename (no extension)
   - `model_slug` (lowercase, hyphenated)
3. Ensure `reviews/` exists.
4. Run the review using the rubric and required structure in
   `@prompts/RULE_REVIEW_PROMPT.md`.
5. Write the full Markdown output to the required file path (overwrite).
6. Reply with a short confirmation including the output path.

## Example Invocation

```text
Load: @skills/rule-reviewer-skill.md

Use the rule-reviewer skill.

target_file: rules/810-project-readme.md
review_date: 2025-12-12
review_mode: FULL
model: claude-sonnet45
```
