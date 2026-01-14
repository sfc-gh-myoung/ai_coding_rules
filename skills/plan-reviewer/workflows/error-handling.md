# Error Handling Workflow

## Purpose

Handle errors gracefully and provide actionable recovery guidance.

## Error Categories

### 1. Input Validation Errors

- **`Invalid review_mode`** - Cause: Mode not FULL/COMPARISON/META-REVIEW, Recovery: Correct mode spelling
- **`Invalid date format`** - Cause: Date not YYYY-MM-DD, Recovery: Use correct format
- **`File not found`** - Cause: Target file doesn't exist, Recovery: Verify path
- **`Not a markdown file`** - Cause: File doesn't end with .md, Recovery: Use markdown file
- **`Insufficient files for mode`** - Cause: COMPARISON/META-REVIEW needs 2+ files, Recovery: Add more files

### 2. Content Errors

- **`Cannot parse plan structure`** - Cause: Malformed markdown, Recovery: Fix plan formatting
- **`Empty plan file`** - Cause: File has no content, Recovery: Add plan content
- **`Review file missing scores table`** - Cause: META-REVIEW target isn't a review, Recovery: Use actual review files

### 3. File System Errors

- **`Cannot create reviews directory`** - Cause: Permission issue, Recovery: Check write permissions for output_root
- **`Cannot write output file`** - Cause: Disk full or permission issue, Recovery: Free space or fix permissions
- **`Path too long`** - Cause: Generated filename exceeds OS limit, Recovery: Use shorter model name or output_root

### 4. Review Execution Errors

- **`Cannot complete verification table`** - Cause: Plan lacks required structure, Recovery: Note limitation in review
- **`Scoring Impact Rules conflict`** - Cause: Edge case in rubric, Recovery: Document and use judgment

## Error Response Format

```
 Error: [error type]

Problem: [specific issue]
Location: [file/line if applicable]
Recovery: [actionable steps]

If this error persists, see workflows/error-handling.md for detailed guidance.
```

## Fallback Procedures

### File Write Failure

If unable to write to `{output_root}plan-reviews/`:

1. Output the intended path:
   ```
   OUTPUT_FILE: {output_root}plan-reviews/plan-<name>-<model>-<date>.md
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

