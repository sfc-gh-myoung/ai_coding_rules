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
4. Write `review_markdown` to `output_file` if it does not already exist.
5. If `output_file` already exists, write to a suffixed path instead (no overwrites):
   - `reviews/<rule_name>-<model_slug>-<review_date>-01.md`
   - then `-02.md`, `-03.md`, etc. until an unused filename is found.

## Output

- `output_file`
