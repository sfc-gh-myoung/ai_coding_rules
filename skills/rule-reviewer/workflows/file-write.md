# Workflow: File Write

## Inputs

- `target_file`
- `review_date`
- `review_mode`
- `model_slug`
- `review_markdown`
- `overwrite` (optional, default: false)

## Steps

1. Compute:
   - `rule_name` = base filename of `target_file` without extension
2. Ensure `reviews/` exists (create if missing).
3. Compute:
   - `output_file = reviews/<rule_name>-<model_slug>-<review_date>.md`
4. Check if `output_file` already exists:
   - **If `overwrite: true`:** Overwrite the existing file directly
   - **If `overwrite: false` (default):** Use sequential numbering to avoid conflicts:
     - `reviews/<rule_name>-<model_slug>-<review_date>-01.md`
     - then `-02.md`, `-03.md`, etc. until an unused filename is found
5. Write `review_markdown` to the determined path.

## Overwrite Parameter Logic

```python
from pathlib import Path

def get_output_path(rule_name: str, model_slug: str, review_date: str, overwrite: bool = False) -> str:
    """Determine output path based on overwrite setting."""
    base_path = f"reviews/{rule_name}-{model_slug}-{review_date}.md"
    
    # If overwrite is true, always use base path (will overwrite if exists)
    if overwrite:
        return base_path
    
    # If file doesn't exist, use base path
    if not Path(base_path).exists():
        return base_path
    
    # Sequential numbering for no-overwrite mode
    for i in range(1, 100):
        suffixed_path = f"reviews/{rule_name}-{model_slug}-{review_date}-{i:02d}.md"
        if not Path(suffixed_path).exists():
            return suffixed_path
    
    raise ValueError(f"Maximum versions (99) exceeded for {rule_name}")
```

## Output

- `output_file`
