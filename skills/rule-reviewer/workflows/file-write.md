# Workflow: File Write

## Inputs

- `target_file`
- `review_date`
- `review_mode`
- `model_slug`
- `review_markdown`
- `output_root` (optional, default: `reviews/`)
- `overwrite` (optional, default: false)

## Steps

1. Normalize `output_root` (ensure trailing slash)
2. Compute:
   - `rule_name` = base filename of `target_file` without extension
3. Ensure `{output_root}rule-reviews/` exists (create if missing).
4. Compute:
   - `output_file = {output_root}rule-reviews/<rule_name>-<model_slug>-<review_date>.md`
5. Check if `output_file` already exists:
   - **If `overwrite: true`:** Overwrite the existing file directly
   - **If `overwrite: false` (default):** Use sequential numbering to avoid conflicts:
     - `{output_root}rule-reviews/<rule_name>-<model_slug>-<review_date>-01.md`
     - then `-02.md`, `-03.md`, etc. until an unused filename is found
6. Write `review_markdown` to the determined path.

## Overwrite Parameter Logic

```python
from pathlib import Path

def get_output_path(rule_name: str, model_slug: str, review_date: str, 
                    output_root: str = 'reviews/', overwrite: bool = False) -> str:
    """Determine output path based on overwrite setting."""
    # Normalize output_root
    output_root = output_root.rstrip('/') + '/'
    
    base_path = f"{output_root}rule-reviews/{rule_name}-{model_slug}-{review_date}.md"
    
    # If overwrite is true, always use base path (will overwrite if exists)
    if overwrite:
        return base_path
    
    # If file doesn't exist, use base path
    if not Path(base_path).exists():
        return base_path
    
    # Sequential numbering for no-overwrite mode
    for i in range(1, 100):
        suffixed_path = f"{output_root}rule-reviews/{rule_name}-{model_slug}-{review_date}-{i:02d}.md"
        if not Path(suffixed_path).exists():
            return suffixed_path
    
    raise ValueError(f"Maximum versions (99) exceeded for {rule_name}")
```

## Output

- `output_file`
