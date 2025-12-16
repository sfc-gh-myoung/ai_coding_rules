# File Write Workflow

## Purpose

Write review output to the correct location with no-overwrite safety.

## Output Path Generation

### FULL Mode

```
reviews/plan-<plan-name>-<model>-<YYYY-MM-DD>.md
```

Example:
- Plan: `plans/IMPROVE_RULE_LOADING.md`
- Model: `claude-sonnet45`
- Date: `2025-12-16`
- Output: `reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md`

### COMPARISON Mode

```
reviews/plan-comparison-<model>-<YYYY-MM-DD>.md
```

Example:
- Model: `claude-sonnet45`
- Date: `2025-12-16`
- Output: `reviews/plan-comparison-claude-sonnet45-2025-12-16.md`

### META-REVIEW Mode

```
reviews/meta-<document-name>-<model>-<YYYY-MM-DD>.md
```

Example:
- Original: `plans/IMPROVE_RULE_LOADING.md`
- Model: `claude-sonnet45`
- Date: `2025-12-16`
- Output: `reviews/meta-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md`

## No-Overwrite Safety

If the target file already exists:

1. Append `-01` before `.md`
2. If `-01` exists, try `-02`, etc.
3. Continue until unused suffix found

```python
def get_safe_path(base_path: str) -> str:
    from pathlib import Path
    
    p = Path(base_path)
    if not p.exists():
        return base_path
    
    stem = p.stem
    suffix = p.suffix
    parent = p.parent
    
    i = 1
    while True:
        new_path = parent / f"{stem}-{i:02d}{suffix}"
        if not new_path.exists():
            return str(new_path)
        i += 1
```

## Write Procedure

1. Generate output path
2. Apply no-overwrite safety
3. Write full review content
4. Verify file written successfully
5. Report success with path

## Success Output

```
✓ Review complete

OUTPUT_FILE: reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md
Target: plans/IMPROVE_RULE_LOADING.md
Mode: FULL
Model: claude-sonnet45

Summary:
[dimension scores]
Verdict: [EXECUTABLE|NEEDS_REFINEMENT|NOT_EXECUTABLE]
```

## Failure Fallback

If file writing fails:

1. Print `OUTPUT_FILE: <intended-path>`
2. Print full review content as markdown
3. User can manually save

## Next Step

If errors occurred, proceed to `error-handling.md`.

