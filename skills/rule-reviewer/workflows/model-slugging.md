# Workflow: Model Slugging

## Input

- `model`: either a slug (preferred) or a raw model name

## Rules

- If `model` matches: `^[a-z0-9]+(-[a-z0-9]+)*$`, use it as `model_slug`.
- Else normalize to `model_slug`:
  - lowercase
  - replace spaces and underscores with `-`
  - remove all characters other than `a-z`, `0-9`, and `-`
  - collapse repeated `-`
  - trim leading/trailing `-`

## Output

- `model_slug`
