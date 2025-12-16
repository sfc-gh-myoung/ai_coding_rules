# Input Validation Workflow

## Purpose

Validate all required inputs before executing a plan review.

## Validation Steps

### Step 1: Check review_mode

```python
VALID_MODES = {'FULL', 'COMPARISON', 'META-REVIEW'}

if mode.upper() not in VALID_MODES:
    ERROR: f"Invalid review_mode: {mode}. Must be one of: FULL, COMPARISON, META-REVIEW"
```

### Step 2: Check review_date

```python
from datetime import datetime

try:
    datetime.strptime(date_str, '%Y-%m-%d')
except ValueError:
    ERROR: f"Invalid date format: {date_str}. Must be YYYY-MM-DD"
```

### Step 3: Check target_file(s)

**FULL mode:**
- Exactly 1 `target_file` required
- File must exist
- File must be `.md`

**COMPARISON mode:**
- At least 2 files in `target_files`
- All files must exist
- All files must be `.md`
- `task_description` required

**META-REVIEW mode:**
- At least 2 files in `target_files`
- All files must be review files (in `reviews/` directory)
- `original_document` optional but recommended

### Step 4: Check model

- Must be provided
- Will be normalized in model-slugging workflow

## Error Messages

| Error | Resolution |
|-------|------------|
| "File not found: X" | Verify path is correct relative to workspace root |
| "Not a markdown file: X" | Ensure file ends with `.md` |
| "COMPARISON mode requires at least 2 files" | Provide 2+ plan files |
| "META-REVIEW mode requires at least 2 review files" | Provide 2+ review files |
| "task_description required for COMPARISON mode" | Add brief task description |

## Validation Complete

If all checks pass, proceed to `model-slugging.md`.

