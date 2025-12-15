# Workflow: File Write

## Inputs

- `target_file`
- `review_date`
- `review_mode`
- `model_slug`
- `review_markdown`

## Steps

1. Compute:
   - `rule_name` = base filename of `target_file` without extension
2. Ensure `reviews/` exists (create if missing).
3. Compute:
   - `output_file = reviews/<rule_name>-<model_slug>-<review_date>.md`
4. Write `review_markdown` to `output_file` (overwrite if it exists).

## Output

- `output_file`
