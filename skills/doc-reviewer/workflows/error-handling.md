# Workflow: Error Handling

## Purpose

Define deterministic fallback behavior when validation, review, or file writing fails. This workflow captures common failure patterns and their resolutions.

## Error Categories

| Category | Severity | Action |
|----------|----------|--------|
| Input validation failure | BLOCKING | Stop, report, request correction |
| No documentation found | BLOCKING | Report, suggest creating docs |
| Review generation failure | BLOCKING | Report step that failed, no partial output |
| File write failure | RECOVERABLE | Print OUTPUT_FILE + full content |
| Permission error | RECOVERABLE | Suggest alternative path or print content |

## Input Validation Errors

### Error 1: No Documentation Files Found

**Symptom:**

```
Error: No documentation files found to review
```

**Resolution:**

```
Input validation failed: No documentation files found.

Checked locations:
- ./README.md (not found)
- ./CONTRIBUTING.md (not found)
- ./docs/*.md (directory empty or missing)

Options:
A. Specify target_files explicitly: target_files: [path/to/doc.md]
B. Create documentation first, then re-run review
C. Check if documentation is in a non-standard location

Common documentation locations to check:
- ./README.md, ./readme.md
- ./docs/, ./documentation/
- ./wiki/, ./guides/
```

---

### Error 2: Invalid Review Mode

**Symptom:**

```
Error: Invalid review_mode: PARTIAL
Valid modes: FULL, FOCUSED, STALENESS
```

**Resolution:**

```
Input validation failed: Invalid review mode.

Mode provided: PARTIAL
Valid modes: FULL | FOCUSED | STALENESS

Mode descriptions:
- FULL: Complete rubric evaluation (all 6 dimensions)
- FOCUSED: Specific area deep-dive (requires focus_area parameter)
- STALENESS: Check for outdated content, broken links

Please specify a valid mode.
```

---

### Error 3: Invalid Date Format

**Symptom:**

```
Error: Invalid date format: 12/16/2025
Expected: YYYY-MM-DD
```

**Resolution:**

```
Input validation failed: Invalid date format.

Date provided: 12/16/2025
Expected format: YYYY-MM-DD (e.g., 2025-12-16)

Please provide the date in ISO 8601 format.
```

---

### Error 4: FOCUSED Mode Without Focus Area

**Symptom:**

```
Error: FOCUSED mode requires focus_area parameter
```

**Resolution:**

```
Input validation failed: Missing focus_area for FOCUSED mode.

FOCUSED review requires specifying which dimension to analyze.

Available focus areas:
- accuracy: Cross-reference verification
- completeness: Coverage analysis
- clarity: Readability assessment
- consistency: Style compliance check
- staleness: Link validation and version checking
- structure: Organization review

Please specify: focus_area: [accuracy|completeness|clarity|consistency|staleness|structure]

Or switch to FULL mode for comprehensive evaluation.
```

---

### Error 5: Target File Not Found

**Symptom:**

```
Error: File not found: docs/MISSING.md
```

**Resolution:**

```
Input validation failed: Target file not found.

Path provided: docs/MISSING.md

Did you mean one of these?
- docs/ARCHITECTURE.md
- docs/MEMORY_BANK.md

To list available documentation:
  ls *.md docs/*.md 2>/dev/null

Please provide the correct path.
```

---

### Error 6: Invalid Review Scope

**Symptom:**

```
Error: Invalid scope: combined
Valid scopes: single, collection
```

**Resolution:**

```
Input validation failed: Invalid review scope.

Scope provided: combined
Valid scopes: single | collection

Scope descriptions:
- single: One review output per document (default)
- collection: Single consolidated review for all docs

Please specify a valid scope.
```

## Review Generation Errors

### Error 7: Prompt File Not Found

**Symptom:**

```
Error: Could not read skills/doc-reviewer/PROMPT.md
```

**Resolution:**

```
Review generation failed: Prompt file not accessible.

Missing: skills/doc-reviewer/PROMPT.md

Actions:
1. Verify file exists: ls skills/doc-reviewer/PROMPT.md
2. Check permissions: ls -la skills/doc-reviewer/
3. If missing, restore from version control:
   git checkout skills/doc-reviewer/PROMPT.md
```

---

### Error 8: Baseline Rule Parsing Failed

**Symptom:**

```
Warning: Could not parse rules/801-project-readme.md for baseline comparison
```

**Resolution:**

```
Baseline comparison warning: Rule file has invalid structure.

Issue: Could not parse rules/801-project-readme.md
Impact: Review will proceed without baseline comparison

Options:
A. Proceed with review using general best practices only
B. Fix the rule file first, then re-run review
C. Skip baseline comparison explicitly

Recommendation: Option A
The review will note "Baseline: General best practices (rule parsing failed)"
```

---

### Error 9: Very Large Documentation Collection

**Symptom:**

```
Warning: Large documentation set detected (15 files, ~25,000 words)
```

**Resolution:**

```
Large documentation collection detected:

Files: 15
Estimated words: ~25,000
Estimated review time: 5-10 minutes

Options:
A. Proceed with FULL review (may be slow)
B. Use STALENESS mode for quick health check
C. Review subset of files: target_files: [README.md, CONTRIBUTING.md]
D. Use collection scope for consolidated output

Recommendation: 
- For initial review: Option A or D
- For periodic maintenance: Option B
```

## File Write Errors

### Error 10: Permission Denied

**Symptom:**

```
Error: Permission denied writing to reviews/
```

**Fallback behavior:**

```
OUTPUT_FILE: reviews/README-claude-sonnet45-2025-12-16.md

[Full Markdown review content follows...]

---
Note: File write failed due to permission error.
Please manually save the above content to the indicated path.

To fix permissions:
  mkdir -p reviews && chmod 755 reviews
```

---

### Error 11: Directory Does Not Exist

**Symptom:**

```
Error: Directory reviews/ does not exist
```

**Resolution:**

1. Create directory: `mkdir -p reviews/`
2. Retry file write
3. If still failing, use fallback output

---

### Error 12: Disk Full

**Symptom:**

```
Error: No space left on device
```

**Fallback:**

Print full content to chat with OUTPUT_FILE path for manual save.

## Recovery Procedures

### Procedure A: Partial Recovery (File Write Failed)

When file writing fails but review completed successfully:

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
4. Verify: cat reviews/<filename>.md | head -20
```

### Procedure B: Full Recovery (Review Failed)

When review generation fails:

```
❌ Review generation failed at step: [step name]

Error details:
- [specific error message]

Recovery options:
1. Fix input error and retry
2. Use alternative review mode
3. Manual review using skills/doc-reviewer/PROMPT.md rubric

No partial file was written.
```

### Procedure C: Input Correction Loop

When input validation fails:

```
❌ Input validation failed.

Issues found:
1. [Issue 1 with fix suggestion]
2. [Issue 2 with fix suggestion]

Please provide corrected inputs:
- target_files: [current value] → [suggested fix or "OK"]
- review_date: [current value] → [suggested fix or "OK"]
- review_mode: [current value] → [suggested fix or "OK"]
- review_scope: [current value] → [suggested fix or "OK"]
- model: [current value] → [suggested fix or "OK"]
```

## Quick Validation Snippet

Run this before starting review to catch common issues:

```python
from pathlib import Path
from datetime import datetime

def validate_docs_review_inputs(
    review_date: str,
    review_mode: str,
    model: str,
    target_files: list[str] | None = None,
    review_scope: str = 'single',
    focus_area: str | None = None
) -> list[str]:
    """Returns list of error messages (empty if all valid)"""
    errors = []
    
    # Check date format
    try:
        datetime.strptime(review_date, '%Y-%m-%d')
    except ValueError:
        errors.append(f"Invalid date format: {review_date} (expected YYYY-MM-DD)")
    
    # Check review mode
    valid_modes = {'FULL', 'FOCUSED', 'STALENESS'}
    if review_mode.upper() not in valid_modes:
        errors.append(f"Invalid mode: {review_mode} (valid: {', '.join(valid_modes)})")
    
    # Check focus_area if FOCUSED mode
    if review_mode.upper() == 'FOCUSED':
        valid_areas = {'accuracy', 'completeness', 'clarity', 
                       'consistency', 'staleness', 'structure'}
        if not focus_area:
            errors.append("FOCUSED mode requires focus_area parameter")
        elif focus_area.lower() not in valid_areas:
            errors.append(f"Invalid focus_area: {focus_area}")
    
    # Check scope
    valid_scopes = {'single', 'collection'}
    if review_scope.lower() not in valid_scopes:
        errors.append(f"Invalid scope: {review_scope}")
    
    # Check target files
    if target_files:
        for path in target_files:
            if not Path(path).exists():
                errors.append(f"File not found: {path}")
            elif not path.endswith('.md'):
                errors.append(f"Not a markdown file: {path}")
    else:
        # Check defaults exist
        defaults_found = []
        for doc in ['README.md', 'CONTRIBUTING.md']:
            if Path(doc).exists():
                defaults_found.append(doc)
        if Path('docs').exists():
            defaults_found.extend(str(f) for f in Path('docs').glob('*.md'))
        
        if not defaults_found:
            errors.append("No documentation files found (specify target_files)")
    
    # Check reviews directory
    if not Path('reviews').exists():
        errors.append("Directory 'reviews/' does not exist - will be created")
    
    return errors

# Usage
errors = validate_docs_review_inputs(
    review_date='2025-12-16',
    review_mode='FULL',
    model='claude-sonnet45'
)
if errors:
    print("Validation errors:")
    for e in errors:
        print(f"  - {e}")
else:
    print("All inputs valid, proceeding with review...")
```

## Error Frequency and Prevention

| Error | Frequency | Prevention |
|-------|-----------|------------|
| No docs found | Medium | Check project structure first |
| Invalid date | Medium | Use ISO 8601 consistently |
| Invalid mode | Low | Copy from examples |
| Missing focus_area | Medium | Remember FOCUSED requires it |
| Write permission | Low | Check reviews/ exists and is writable |
| Prompt missing | Rare | Keep skill files in version control |

## Escalation Path

If errors persist after following this guide:

1. **Check related documentation:**
   - `workflows/input-validation.md`
   - `workflows/file-write.md`

2. **Verify environment:**
   - Working directory is project root
   - Required files exist
   - Permissions are correct

3. **Request assistance:**
   - Provide exact error message
   - Include input values used
   - Note any recent changes to environment

