# Workflow: File Write

## Inputs

- `resolved_targets`: list of reviewed file paths
- `review_date`: validated date string
- `review_mode`: `FULL` | `FOCUSED` | `STALENESS`
- `review_scope`: `single` | `collection`
- `model_slug`: normalized model identifier
- `review_markdown`: full review content (or list of contents for single scope)

## Steps

### Step 1: Ensure reviews/ Directory Exists

```bash
mkdir -p reviews/
```

If directory creation fails, proceed to fallback output.

### Step 2: Compute Output Filename(s)

**For collection scope:**

```
output_file = reviews/docs-collection-<model_slug>-<review_date>.md
```

**For single scope:**

For each target file:

```
doc_name = base filename without extension
output_file = reviews/<doc_name>-<model_slug>-<review_date>.md
```

Examples:
- `README.md` → `reviews/README-claude-sonnet45-2025-12-16.md`
- `docs/ARCHITECTURE.md` → `reviews/ARCHITECTURE-claude-sonnet45-2025-12-16.md`

### Step 3: Check for Existing Files (No-Overwrite)

For each output_file:

1. If `output_file` does not exist → use it
2. If `output_file` exists → find next available suffix:
   - `reviews/<name>-<model>-<date>-01.md`
   - `reviews/<name>-<model>-<date>-02.md`
   - ... up to `-99.md`

```python
from pathlib import Path

def get_safe_output_path(base_name: str, model_slug: str, date: str) -> str:
    """Returns next available filename without overwriting"""
    base = f"reviews/{base_name}-{model_slug}-{date}"
    
    if not Path(f"{base}.md").exists():
        return f"{base}.md"
    
    for i in range(1, 100):
        suffixed = f"{base}-{i:02d}.md"
        if not Path(suffixed).exists():
            return suffixed
    
    # Fallback: use timestamp
    import time
    ts = int(time.time())
    return f"{base}-{ts}.md"
```

### Step 4: Write Review Content

Write `review_markdown` to `output_file`.

**For single scope with multiple targets:**
Write each review to its respective output file.

**For collection scope:**
Write consolidated review to single output file.

### Step 5: Confirm Success

Print confirmation message:

```
✓ Review complete

OUTPUT_FILE: reviews/<filename>.md
Target(s): <list of reviewed files>
Mode: <review_mode>
Scope: <review_scope>
Model: <model_slug>
```

## Fallback Behavior

If file write fails (permission denied, disk full, etc.):

1. Print `OUTPUT_FILE: <intended_path>`
2. Print the full Markdown review content
3. Instruct user to manually save

```
⚠️ Review completed but file write failed.

OUTPUT_FILE: reviews/<filename>.md

--- BEGIN REVIEW CONTENT ---
[Full review markdown]
--- END REVIEW CONTENT ---

To save manually:
1. Copy content between markers above
2. Create file: touch reviews/<filename>.md
3. Paste content into file
```

## Output

- `output_file`: path to written review file (or intended path if fallback)
- Success/failure status

