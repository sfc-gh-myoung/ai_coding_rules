# Workflow: Input Validation

## Inputs

### Required

- `review_date`: must match `YYYY-MM-DD`
- `review_mode`: must be one of `FULL`, `FOCUSED`, `STALENESS`
- `model`: slug preferred (example: `claude-sonnet45`) or raw model name

### Optional

- `target_files`: list of file paths (defaults to project docs if not specified)
- `review_scope`: must be one of `single`, `collection` (default: `single`)
- `focus_area`: required if `review_mode` is `FOCUSED`

## Steps

1. **Validate review_date** matches `YYYY-MM-DD` exactly.

2. **Validate review_mode** is one of `FULL`, `FOCUSED`, `STALENESS`.

3. **If review_mode is FOCUSED**, verify `focus_area` is provided and valid:
   - Valid values: `accuracy`, `completeness`, `clarity`, `consistency`, `staleness`, `structure`

4. **Validate review_scope** (if provided) is one of `single`, `collection`.

5. **Resolve target_files:**
   - If `target_files` provided: validate each file exists and ends with `.md`
   - If `target_files` not provided: use defaults:
     - `./README.md` (if exists)
     - `./CONTRIBUTING.md` (if exists)
     - `./docs/*.md` (all markdown files in docs/)

6. **Verify at least one target file** exists and is readable.

7. **Check for project documentation rules** (optional baseline):
   - `rules/801-project-readme.md`
   - `rules/802-project-contributing.md`
   - Note which are available for baseline comparison.

## Validation Logic

```python
from pathlib import Path
from datetime import datetime
from typing import Optional

def validate_inputs(
    review_date: str,
    review_mode: str,
    model: str,
    target_files: Optional[list[str]] = None,
    review_scope: str = 'single',
    focus_area: Optional[str] = None
) -> tuple[bool, list[str], list[str]]:
    """
    Returns (is_valid, errors, resolved_targets)
    """
    errors = []
    resolved_targets = []
    
    # 1. Validate date
    try:
        datetime.strptime(review_date, '%Y-%m-%d')
    except ValueError:
        errors.append(f"Invalid date format: {review_date} (expected YYYY-MM-DD)")
    
    # 2. Validate mode
    valid_modes = {'FULL', 'FOCUSED', 'STALENESS'}
    if review_mode.upper() not in valid_modes:
        errors.append(f"Invalid mode: {review_mode} (valid: {', '.join(valid_modes)})")
    
    # 3. Validate focus_area if FOCUSED mode
    if review_mode.upper() == 'FOCUSED':
        valid_areas = {'accuracy', 'completeness', 'clarity', 
                       'consistency', 'staleness', 'structure'}
        if not focus_area:
            errors.append("FOCUSED mode requires focus_area parameter")
        elif focus_area.lower() not in valid_areas:
            errors.append(f"Invalid focus_area: {focus_area} (valid: {', '.join(valid_areas)})")
    
    # 4. Validate scope
    valid_scopes = {'single', 'collection'}
    if review_scope.lower() not in valid_scopes:
        errors.append(f"Invalid scope: {review_scope} (valid: {', '.join(valid_scopes)})")
    
    # 5. Resolve target files
    if target_files:
        for path in target_files:
            p = Path(path)
            if not p.exists():
                errors.append(f"File not found: {path}")
            elif not path.endswith('.md'):
                errors.append(f"Not a markdown file: {path}")
            else:
                resolved_targets.append(path)
    else:
        # Use defaults
        defaults = ['README.md', 'CONTRIBUTING.md']
        for doc in defaults:
            if Path(doc).exists():
                resolved_targets.append(doc)
        
        docs_dir = Path('docs')
        if docs_dir.exists():
            resolved_targets.extend(str(f) for f in docs_dir.glob('*.md'))
    
    # 6. Verify at least one target
    if not resolved_targets:
        errors.append("No documentation files found to review")
    
    return (len(errors) == 0, errors, resolved_targets)
```

## Output

- Validated inputs ready for downstream workflows
- `resolved_targets`: list of file paths to review
- `baseline_rules`: list of available documentation rules for comparison

