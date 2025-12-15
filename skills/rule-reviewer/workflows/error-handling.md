# Workflow: Error Handling

## Purpose

Define deterministic fallback behavior when validation, review, or file writing fails.

## Rules

- If input validation fails:
  - Explain which field is invalid and what value is expected.
  - Stop (do not run the review).
- If review generation fails:
  - Report the failure and what step failed.
  - Do not write a partial file.
- If file writing fails:
  - Print:
    - `OUTPUT_FILE: <intended path>`
    - then the full Markdown review content
