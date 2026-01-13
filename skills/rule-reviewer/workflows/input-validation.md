# Workflow: Input Validation

## Inputs (required)

- `target_file`: must end in `.md`
- `review_date`: must match `YYYY-MM-DD`
- `review_mode`: must be one of `FULL`, `FOCUSED`, `STALENESS`
- `model`: slug preferred (example: `claude-sonnet45`) or raw model name

## Inputs (optional)

- `output_root`: root directory for output files (default: `reviews/`)
  - Trailing slash auto-normalized (both `reviews` and `reviews/` accepted)
  - Supports relative paths including `../`
  - Subdirectory `rule-reviews/` appended automatically

## Steps

1. Verify `target_file` ends with `.md`.
2. Verify `review_date` matches `YYYY-MM-DD` exactly.
3. Verify `review_mode` is one of `FULL`, `FOCUSED`, `STALENESS`.
4. Verify `target_file` exists and is readable.
5. Normalize `output_root`:
   - Add trailing `/` if missing
   - Auto-create `{output_root}/rule-reviews/` directory if it doesn't exist

## Output

- Validated inputs ready for downstream workflows
- `output_root`: normalized path with trailing slash (e.g., `reviews/` or `../mytest/`)
