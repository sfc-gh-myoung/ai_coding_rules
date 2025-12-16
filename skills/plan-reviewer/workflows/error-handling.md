# Error Handling Workflow

## Purpose

Handle errors gracefully and provide actionable recovery guidance.

## Error Categories

### 1. Input Validation Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| `Invalid review_mode` | Mode not FULL/COMPARISON/META-REVIEW | Correct mode spelling |
| `Invalid date format` | Date not YYYY-MM-DD | Use correct format |
| `File not found` | Target file doesn't exist | Verify path |
| `Not a markdown file` | File doesn't end with .md | Use markdown file |
| `Insufficient files for mode` | COMPARISON/META-REVIEW needs 2+ files | Add more files |

### 2. Content Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| `Cannot parse plan structure` | Malformed markdown | Fix plan formatting |
| `Empty plan file` | File has no content | Add plan content |
| `Review file missing scores table` | META-REVIEW target isn't a review | Use actual review files |

### 3. File System Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| `Cannot create reviews directory` | Permission issue | Check write permissions |
| `Cannot write output file` | Disk full or permission issue | Free space or fix permissions |
| `Path too long` | Generated filename exceeds OS limit | Use shorter model name |

### 4. Review Execution Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| `Cannot complete verification table` | Plan lacks required structure | Note limitation in review |
| `Scoring Impact Rules conflict` | Edge case in rubric | Document and use judgment |

## Error Response Format

```
❌ Error: [error type]

Problem: [specific issue]
Location: [file/line if applicable]
Recovery: [actionable steps]

If this error persists, see workflows/error-handling.md for detailed guidance.
```

## Fallback Procedures

### File Write Failure

If unable to write to `reviews/`:

1. Output the intended path:
   ```
   OUTPUT_FILE: reviews/plan-<name>-<model>-<date>.md
   ```

2. Output full review content as markdown

3. User can manually create file

### Partial Review Completion

If review cannot be fully completed:

1. Complete as many dimensions as possible
2. Mark incomplete dimensions with:
   ```
   | Dimension | Weight | Raw | Weighted | Notes |
   | X | 2× | N/A | N/A | Could not assess: [reason] |
   ```

3. Note limitations in recommendations section

### META-REVIEW with Inconsistent Reviews

If reviews being analyzed use different rubrics:

1. Note the inconsistency
2. Compare only common dimensions
3. Flag incompatible dimensions as "not comparable"

## Error Logging

For persistent issues, capture:

1. Input parameters used
2. Error message
3. Stack trace if available
4. Timestamp

Report to project maintainers if error appears to be a skill bug.

## Prevention Tips

1. **Validate inputs early** - Run input-validation workflow first
2. **Use absolute paths** - Reduces "file not found" errors
3. **Check disk space** - Before large reviews
4. **Verify review format** - Before META-REVIEW mode

