# Workflow: File Write

## Inputs

- `resolved_targets`: list of reviewed file paths
- `review_date`: validated date string
- `review_mode`: `FULL` | `FOCUSED` | `STALENESS`
- `review_scope`: `single` | `collection`
- `model_slug`: normalized model identifier
- `review_markdown`: full review content (or list of contents for single scope)
- `output_root`: root directory for output files (default: `reviews/`)
- `overwrite`: `true` | `false` (default: `false`)

## Steps

### Step 1: Normalize output_root and Ensure Directories Exist

```python
# Normalize trailing slash
output_root = output_root.rstrip('/') + '/'
```

```bash
mkdir -p {output_root}doc-reviews/
```

For collection scope, also ensure:
```bash
mkdir -p {output_root}summaries/
```

If directory creation fails, proceed to fallback output.

### Step 2: Compute Output Filename(s)

**For collection scope:**

```
output_file = {output_root}summaries/_docs-collection-<model_slug>-<review_date>.md
```

**For single scope:**

For each target file:

```
doc_name = base filename without extension
output_file = {output_root}doc-reviews/<doc_name>-<model_slug>-<review_date>.md
```

Examples (with default `output_root: reviews/`):
- `README.md` → `reviews/doc-reviews/README-claude-sonnet45-2025-12-16.md`
- `docs/ARCHITECTURE.md` → `reviews/doc-reviews/ARCHITECTURE-claude-sonnet45-2025-12-16.md`

Examples (with `output_root: mytest/`):
- `README.md` → `mytest/doc-reviews/README-claude-sonnet45-2025-12-16.md`

### Step 3: Check for Existing Files (Overwrite Logic)

For each output_file:

**If `overwrite: true`:**
- Use the base filename directly (will overwrite if exists)

**If `overwrite: false` (default):**
1. If `output_file` does not exist → use it
2. If `output_file` exists → find next available suffix:
   - `{output_root}doc-reviews/<name>-<model>-<date>-01.md`
   - `{output_root}doc-reviews/<name>-<model>-<date>-02.md`
   - ... up to `-99.md`

```python
from pathlib import Path

def get_safe_output_path(base_name: str, model_slug: str, date: str, 
                         output_root: str = 'reviews/', overwrite: bool = False) -> str:
    """Returns output filename based on overwrite setting."""
    # Normalize output_root
    output_root = output_root.rstrip('/') + '/'
    
    base = f"{output_root}doc-reviews/{base_name}-{model_slug}-{date}"
    
    # If overwrite, always use base path
    if overwrite:
        return f"{base}.md"
    
    # If file doesn't exist, use base
    if not Path(f"{base}.md").exists():
        return f"{base}.md"
    
    # Sequential numbering for no-overwrite mode
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
 Review complete

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
 Review completed but file write failed.

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

