# Workflow: Input Validation

## Inputs (required)

- `target_file`: must end in `.md`
- `review_date`: must match `YYYY-MM-DD`
- `review_mode`: must be one of `FULL`, `FOCUSED`, `STALENESS`
- `model`: slug preferred (example: `claude-sonnet45`) or raw model name

## Steps

1. Verify `target_file` ends with `.md`.
2. Verify `review_date` matches `YYYY-MM-DD` exactly.
3. Verify `review_mode` is one of `FULL`, `FOCUSED`, `STALENESS`.
4. Verify `target_file` exists and is readable.

## Output

Validated inputs ready for downstream workflows.
