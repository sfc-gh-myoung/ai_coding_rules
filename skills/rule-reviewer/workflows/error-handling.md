# Workflow: Error Handling

## Purpose

Define deterministic fallback behavior when validation, review, or file writing fails. This workflow captures common failure patterns and their resolutions.

## Error Categories

| Category | Severity | Action |
|----------|----------|--------|
| Input validation failure | BLOCKING | Stop, report, request correction |
| Review generation failure | BLOCKING | Report step that failed, no partial output |
| File write failure | RECOVERABLE | Print OUTPUT_FILE + full content |
| Permission error | RECOVERABLE | Suggest alternative path or print content |

## Input Validation Errors

### Error 1: Target File Not Found

**Symptom:**
```
Error: Target file not found: rules/999-nonexistent.md
```

**Resolution:**
1. Verify path spelling and case sensitivity
2. Check if file exists: `ls rules/ | grep -i "<partial-name>"`
3. List available rules: `ls rules/*.md | head -20`

**Response template:**
```
Input validation failed: Target file not found.

Path provided: rules/999-nonexistent.md

Did you mean one of these?
- rules/900-demo-creation.md
- rules/920-data-science-analytics.md

Please provide the correct path.
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
- FULL: Complete rubric evaluation (all dimensions)
- FOCUSED: Specific area deep-dive (requires focus_area parameter)
- STALENESS: Check for outdated content, deprecated patterns

Please specify a valid mode.
```

---

### Error 3: Invalid Date Format

**Symptom:**
```
Error: Invalid date format: 12/15/2025
Expected: YYYY-MM-DD
```

**Resolution:**
```
Input validation failed: Invalid date format.

Date provided: 12/15/2025
Expected format: YYYY-MM-DD (e.g., 2025-12-15)

Please provide the date in ISO 8601 format.
```

---

### Error 4: Target Not a Rule File

**Symptom:**
```
Error: Target must be under rules/ directory
Path: docs/README.md
```

**Resolution:**
```
Input validation failed: Target is not a rule file.

Path provided: docs/README.md
Required: File must be under rules/ directory

This skill reviews rule files only. For other file types:
- README files: Use standard code review
- Prompts: Use prompt review workflow
```

## Review Generation Errors

### Error 5: Skill File Not Found

**Symptom:**
```
Error: Could not read skills/rule-reviewer/SKILL.md
```

**Resolution:**
1. Verify skill file exists
2. Check file permissions
3. Report to user with fallback

**Response:**
```
Review generation failed: Skill file not accessible.

Missing: skills/rule-reviewer/SKILL.md

Actions:
1. Verify file exists: ls skills/rule-reviewer/SKILL.md
2. Check permissions: ls -la skills/rule-reviewer/
3. If missing, restore from version control: git checkout skills/rule-reviewer/SKILL.md
```

---

### Error 6: Rule Content Parsing Failed

**Symptom:**
```
Error: Could not parse rule metadata
Line 5: Invalid YAML in frontmatter
```

**Resolution:**
```
Review generation failed: Rule file has invalid structure.

Issue: Could not parse metadata block
Location: Line 5

Common causes:
- Missing closing `---` for YAML frontmatter
- Invalid YAML syntax (tabs instead of spaces)
- Unescaped special characters in values

Recommendation: Run schema_validator.py first:
  python scripts/schema_validator.py rules/<file>.md
```

---

### Error 7: Review Timeout

**Symptom:**
```
Error: Review generation timed out after 120s
```

**Resolution:**
```
Review generation failed: Operation timed out.

This may occur with very large rule files (>500 lines).

Options:
1. Use FOCUSED mode instead of FULL
2. Split review into multiple sessions
3. Retry with increased timeout
```

## File Write Errors

### Error 8: Permission Denied

**Symptom:**
```
Error: Permission denied writing to reviews/
```

**Fallback behavior:**
```
OUTPUT_FILE: reviews/810-project-readme-claude-sonnet45-2025-12-15.md

[Full Markdown review content follows...]

---
Note: File write failed due to permission error.
Please manually save the above content to the indicated path.
```

---

### Error 9: Directory Does Not Exist

**Symptom:**
```
Error: Directory reviews/ does not exist
```

**Resolution:**
1. Create directory: `mkdir -p reviews/`
2. Retry file write
3. If still failing, use fallback output

---

### Error 10: Disk Full

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
3. Manual review using skills/rule-reviewer/SKILL.md rubric

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
- target_file: [current value] → [suggested fix or "OK"]
- review_date: [current value] → [suggested fix or "OK"]
- review_mode: [current value] → [suggested fix or "OK"]
- model: [current value] → [suggested fix or "OK"]
```

## Quick Validation Snippet

Run this before starting review to catch common issues:

```python
from pathlib import Path
from datetime import datetime

def validate_review_inputs(target_file: str, review_date: str, 
                           review_mode: str, model: str) -> list[str]:
    """Returns list of error messages (empty if all valid)"""
    errors = []
    
    # Check target file
    if not Path(target_file).exists():
        errors.append(f"Target file not found: {target_file}")
    elif not target_file.endswith('.md'):
        errors.append(f"Target must be .md file: {target_file}")
    elif 'rules/' not in target_file:
        errors.append(f"Target must be under rules/: {target_file}")
    
    # Check date format
    try:
        datetime.strptime(review_date, '%Y-%m-%d')
    except ValueError:
        errors.append(f"Invalid date format: {review_date} (expected YYYY-MM-DD)")
    
    # Check review mode
    valid_modes = {'FULL', 'FOCUSED', 'STALENESS'}
    if review_mode.upper() not in valid_modes:
        errors.append(f"Invalid mode: {review_mode} (valid: {', '.join(valid_modes)})")
    
    # Check reviews directory
    if not Path('reviews').exists():
        errors.append("Directory 'reviews/' does not exist - will be created")
    
    return errors

# Usage
errors = validate_review_inputs(target_file, review_date, review_mode, model)
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
| File not found | High | Tab-complete paths, verify before starting |
| Invalid date | Medium | Use ISO 8601 consistently |
| Invalid mode | Low | Copy from examples |
| Write permission | Low | Check reviews/ exists and is writable |
| Prompt missing | Rare | Keep prompts/ in version control |

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
