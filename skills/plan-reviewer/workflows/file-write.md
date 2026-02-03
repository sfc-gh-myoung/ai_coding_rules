# File Write Workflow

## Purpose

Write review output to the correct location with no-overwrite safety and collision avoidance.

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

## Filename Collision Avoidance

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `overwrite` | `true` \| `false` | `false` | If true, overwrite existing file. If false, use sequential numbering |
| `full_rescore` | `true` \| `false` | `false` | If true, re-score from scratch. If false, verify prior issues only |
| `compare_to` | path string | `null` | Path to previous review for consistency check |

### Algorithm

```python
def get_next_available_filename(base_path: str, base_filename: str, overwrite: bool = False) -> str:
    """
    Get the next available filename with collision avoidance.
    
    Args:
        base_path: Directory path for output
        base_filename: Desired filename (e.g., "plan-X-model-2026-01-21.md")
        overwrite: If True, always return base_filename (overwrite existing)
    
    Returns:
        Available filename (may have -01, -02, etc. suffix)
    
    Raises:
        ValueError: If 100+ reviews exist for this plan-model-date
    """
    import os
    
    # If overwrite enabled, always use base filename
    if overwrite:
        return base_filename
    
    name, ext = os.path.splitext(base_filename)
    full_base = os.path.join(base_path, base_filename)
    
    # If file doesn't exist, use base filename
    if not os.path.exists(full_base):
        return base_filename
    
    # Sequential numbering: -01, -02, ..., -99
    for i in range(1, 100):
        seq_num = f"-{i:02d}"
        new_filename = f"{name}{seq_num}{ext}"
        if not os.path.exists(os.path.join(base_path, new_filename)):
            return new_filename
    
    # Error if 100+ reviews exist
    raise ValueError(f"Too many reviews (100+) for this plan-model-date: {name}")
```

### Behavior by Parameter Combination

**`overwrite: false` (default):**
- If file doesn't exist: Use base filename
- If file exists: Try `-01`, `-02`, etc.
- If 100+ files exist: Error with message

**`overwrite: true`:**
- Always use base filename (replaces existing)
- Use when intentionally re-running a review

**`full_rescore: true` (with existing review):**
- Re-score all dimensions from scratch
- Ignore prior scores completely
- Use when rubric definitions changed

**`full_rescore: false` (with existing review):**
- Load prior scores as baseline
- Verify prior issues still fixed
- Score options: Same, +1 (improvement), -1 (regression with evidence)
- Changes >±1 require documented justification

**`compare_to: <path>`:**
- Load prior review from specified path
- Enable DELTA comparison mode
- Track issue resolution between reviews

### Sequential Numbering Examples

```
Base: plan-IMPROVE_RULE_LOADING-claude-sonnet45-2026-01-21.md

If exists: plan-IMPROVE_RULE_LOADING-claude-sonnet45-2026-01-21-01.md
If -01 exists: plan-IMPROVE_RULE_LOADING-claude-sonnet45-2026-01-21-02.md
...
If -99 exists: ERROR "Too many reviews (100+)"
```

### Filename Collision Check Procedure

**Step 1:** Construct base filename from inputs
```
base_filename = f"plan-{plan_name}-{model}-{date}.md"
```

**Step 2:** Check for collision
```bash
# Check if file exists
if [ -f "$output_path/$base_filename" ]; then
    echo "Collision detected: $base_filename"
fi
```

**Step 3:** Apply collision avoidance (if `overwrite: false`)
```python
filename = get_next_available_filename(output_path, base_filename, overwrite=False)
```

**Step 4:** Write file with resolved filename
```python
full_path = os.path.join(output_path, filename)
with open(full_path, 'w') as f:
    f.write(review_content)
```

### Error Handling

**Too many reviews error:**
```
ERROR: Too many reviews (100+) for this plan-model-date
Plan: IMPROVE_RULE_LOADING
Model: claude-sonnet45
Date: 2026-01-21

Resolution options:
1. Use different date (tomorrow)
2. Use overwrite: true to replace existing
3. Archive old reviews to different directory
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

