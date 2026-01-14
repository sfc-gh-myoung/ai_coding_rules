# File Write Workflow

## Purpose

Write review output to the correct location with no-overwrite safety.

## Output Path Generation

### FULL Mode

```
{output_root}plan-reviews/plan-<plan-name>-<model>-<YYYY-MM-DD>.md
```

Example (default `output_root: reviews/`):
- Plan: `plans/IMPROVE_RULE_LOADING.md`
- Model: `claude-sonnet45`
- Date: `2025-12-16`
- Output: `reviews/plan-reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md`

Example (with `output_root: mytest/`):
- Output: `mytest/plan-reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md`

### COMPARISON Mode

```
{output_root}summaries/_comparison-<model>-<YYYY-MM-DD>.md
```

Example (default `output_root: reviews/`):
- Model: `claude-sonnet45`
- Date: `2025-12-16`
- Output: `reviews/summaries/_comparison-claude-sonnet45-2025-12-16.md`

### META-REVIEW Mode

```
{output_root}summaries/_meta-<document-name>-<model>-<YYYY-MM-DD>.md
```

Example (default `output_root: reviews/`):
- Original: `plans/IMPROVE_RULE_LOADING.md`
- Model: `claude-sonnet45`
- Date: `2025-12-16`
- Output: `reviews/summaries/_meta-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md`

## No-Overwrite Safety

**When `overwrite: false` (default):**

If the target file already exists:

1. Append `-01` before `.md`
2. If `-01` exists, try `-02`, etc.
3. Continue until unused suffix found

**When `overwrite: true`:**

The existing file will be replaced directly. Use this when intentionally re-running a review.

```python
def get_safe_path(base_path: str, overwrite: bool = False) -> str:
    from pathlib import Path
    
    p = Path(base_path)
    
    # If overwrite, always use base path
    if overwrite:
        return base_path
    
    # If file doesn't exist, use base path
    if not p.exists():
        return base_path
    
    # Sequential numbering for no-overwrite mode
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
 Review complete

OUTPUT_FILE: reviews/plan-reviews/plan-IMPROVE_RULE_LOADING-claude-sonnet45-2025-12-16.md
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

