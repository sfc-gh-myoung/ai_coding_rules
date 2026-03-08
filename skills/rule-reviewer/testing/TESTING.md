# Skill Testing Guide: rule-reviewer

> ** AUDIENCE:** This document is for **skill maintainers** (humans), not for Claude.
> It provides testing procedures, troubleshooting guides, and health checks for the skill itself.

This document describes how to verify that the rule-reviewer skill is functioning correctly.

## Quick Health Check

Run these checks to verify basic functionality:

```bash
# 1. Verify skill files exist
ls skills/rule-reviewer/SKILL.md
ls skills/rule-reviewer/README.md
ls skills/rule-reviewer/workflows/*.md
ls skills/rule-reviewer/examples/*.md

# 2. Verify skill file exists (contains review rubric)
ls skills/rule-reviewer/SKILL.md

# 3. Verify reviews directory exists (or can be created)
ls reviews/ || mkdir -p reviews/
```

**Expected:** All files exist, no errors.

## Functional Validation

### Test 1: Input Validation

**Trigger:**
```
Use the rule-reviewer skill.

target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FULL
model: claude-sonnet-45
```

**Verify:**
- [ ] All inputs accepted
- [ ] No validation errors
- [ ] Review proceeds

### Test 2: Invalid Input Handling

**Trigger (invalid date):**
```
target_file: rules/200-python-core.md
review_date: 12/15/2025
review_mode: FULL
model: claude-sonnet-45
```

**Verify:**
- [ ] Error detected
- [ ] Clear message: "Invalid date format"
- [ ] Expected format shown
- [ ] Review does not proceed

### Test 3: Review Execution

**Verify during review:**
- [ ] Skill file read: `SKILL.md` (contains review rubric)
- [ ] Target file read: `rules/200-python-core.md`
- [ ] Review generated with all sections

### Test 4: File Output

**Verify:**
```bash
ls reviews/200-python-core-claude-sonnet-45-2025-12-15.md
head -30 reviews/200-python-core-claude-sonnet-45-2025-12-15.md
```

- [ ] File created at expected path
- [ ] Contains review header
- [ ] Contains scores
- [ ] Contains recommendations

### Test 5: No-Overwrite Safety

**Pre-condition:** Run same review twice

**Verify:**
```bash
ls reviews/200-python-core-claude-sonnet-45-2025-12-15*.md
# Expected: Two files (base and -01)
```

- [ ] Second file has -01 suffix
- [ ] First file unchanged
- [ ] Both files complete

## Regression Checklist

Run after any skill modifications:

- [ ] SKILL.md YAML frontmatter parses correctly
- [ ] All workflow files accessible
- [ ] All example files accessible
- [ ] FULL mode works
- [ ] FOCUSED mode works (with focus_area)
- [ ] STALENESS mode works
- [ ] No-overwrite logic works
- [ ] Error handling works (see `workflows/error-handling.md`)

## Mode-Specific Validation

### FULL Mode

```
review_mode: FULL
```

**Verify output contains:**
- [ ] All dimension scores
- [ ] Overall score
- [ ] Issues by severity
- [ ] Recommendations
- [ ] Checklist

### FOCUSED Mode

```
review_mode: FOCUSED
focus_area: metadata
```

**Verify output contains:**
- [ ] Deep analysis of focus area only
- [ ] Single dimension score
- [ ] Focused recommendations

### STALENESS Mode

```
review_mode: STALENESS
```

**Verify output contains:**
- [ ] Version references table
- [ ] Deprecated patterns section
- [ ] Staleness risk assessment

## Performance Baseline

- **Review time (FULL)** - Target: ~2 min (90-120s), Acceptable: < 3 min
- **Review time (FOCUSED)** - Target: ~1 min (60-90s), Acceptable: < 2 min
- **File write** - Target: < 1 sec, Acceptable: < 5 sec

## Troubleshooting

### Skill Not Recognized

**Symptom:** Agent doesn't recognize "review rule" request

**Check:**
1. SKILL.md exists and has valid YAML frontmatter
2. Description contains trigger keywords
3. File is in `skills/rule-reviewer/` directory

### Review Generation Fails

**Symptom:** Error during review execution

**Check:**
1. `skills/rule-reviewer/SKILL.md` exists and is readable
2. Target rule file exists
3. Target rule has valid structure

### File Write Fails

**Symptom:** Review completes but file not created

**Check:**
1. `reviews/` directory exists
2. Directory is writable
3. Filename doesn't exceed system limits

### No-Overwrite Not Working

**Symptom:** Existing file overwritten

**Check:**
1. File existence check logic in `workflows/file-write.md`
2. Suffix generation logic
3. Path construction

## Integration Verification

### With rule-creator

Validate rule-creator output quality:

1. Create rule using rule-creator
2. Run FULL review on created rule
3. Verify:
   - Overall score ≥ 75/100
   - No CRITICAL issues
   - Actionability and Completeness dimensions score ≥ 60%

### Cross-Validation Workflow

```
# Step 1: Create rule
Use rule-creator skill to create rules/999-test-rule.md

# Step 2: Validate creation
uv run ai-rules validate rules/999-test-rule.md
# Expected: exit code 0

# Step 3: Review created rule
Use rule-reviewer skill:
  target_file: rules/999-test-rule.md
  review_mode: FULL
  
# Step 4: Verify quality
# Expected: score ≥ 75/100, no CRITICAL issues
```

## Output Format Validation

### Required Sections

Every review output must contain:

```markdown
# Rule Review: <rule-name>

## Review Metadata
## Overall Score: X/100
## Dimension Scores
## Issues Found
## Recommendations
```

### Table Format

Dimension scores table must be valid markdown:

```markdown
- **Actionability** - Max: 25, Raw: X/5, Points: Y/25, Notes: ...
- **...** - Max: ..., Raw: ..., Points: ..., Notes: ...
```

## Version Compatibility

- **SKILL.md (with rubric)** - Current
- **Rule schema** - v3.0
- **reviews/ directory** - Writable

## Validation Schedule

- **After skill edit** - Full regression
- **After prompt edit** - All modes test
- **Weekly** - Quick health check
- **Monthly** - Performance baseline

---

## Post-Execution Validation (Quality Assurance)

### Review Output Quality Check

After review execution, validate output wasn't abbreviated:

**Check 1: Review File Size**
```python
def validate_review_size(review_path):
    """Ensure review meets minimum quality standards."""
    import os
    
    file_size = os.path.getsize(review_path)
    
    # Legitimate FULL reviews are typically 3000-8000 bytes
    # Suspiciously small = likely abbreviated
    if file_size < 2000:
        return False, f"Suspiciously small ({file_size} bytes) - likely abbreviated review"
    
    return True, f"Valid size ({file_size} bytes)"
```

**Check 2: Required Sections Present**
```python
def validate_review_structure(review_path):
    """Verify review contains all required sections."""
    
    required_sections = [
        "### Agent Execution Test",
        "### Dimension Scores",
        "**Overall:**",
        "**Actionability:**",
        "**Completeness:**",
        "**Consistency:**",
        "**Parsability:**",
        "**Token Efficiency:**",
        "**Staleness:**",
        "### Agent Executability Verdict",
        "### Critical Issues",
        "### Recommendations"
    ]
    
    with open(review_path, 'r') as f:
        content = f.read()
    
    missing = [s for s in required_sections if s not in content]
    
    if missing:
        return False, f"Missing sections: {missing}"
    
    return True, "All required sections present"
```

**Check 3: Dimension Score Rationales**
```python
def validate_dimension_rationales(review_path):
    """Verify dimensions have rationales, not just scores."""
    
    with open(review_path, 'r') as f:
        content = f.read()
    
    # Check for dimension scores with explanations
    # Each dimension should have score + rationale text
    dimensions = [
        "Actionability",
        "Completeness", 
        "Consistency",
        "Parsability",
        "Token Efficiency",
        "Staleness"
    ]
    
    issues = []
    for dim in dimensions:
        # Look for pattern: **Dimension:** N/5 followed by explanation text
        import re
        pattern = f"\\*\\*{dim}:\\*\\* \\d/5(.{{50,}}?)(?=\\*\\*|###|$)"
        if not re.search(pattern, content, re.DOTALL):
            issues.append(f"{dim} missing rationale (score without explanation)")
    
    if issues:
        return False, f"Incomplete dimension scoring: {issues}"
    
    return True, "All dimensions have rationales"
```

**Protocol Violation Report:**

If validation fails, generate report:
```
PROTOCOL VIOLATION DETECTED

Review quality issues found:
  - Review file size: 1,234 bytes (expected: 3000-8000)
  - Missing sections: ['### Critical Issues']
  - Missing rationales: ['Actionability', 'Completeness']

Likely cause: Agent abbreviated review instead of following SKILL.md rubric

Required action:
  1. Delete incomplete review file
  2. Re-run review with full rubric compliance
  3. Verify review file meets quality checks
```

