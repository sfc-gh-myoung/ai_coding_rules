# Skill Validation: rule-reviewer

This document describes how to verify that the rule-reviewer skill is functioning correctly.

## Quick Health Check

Run these checks to verify basic functionality:

```bash
# 1. Verify skill files exist
ls skills/rule-reviewer/SKILL.md
ls skills/rule-reviewer/README.md
ls skills/rule-reviewer/workflows/*.md
ls skills/rule-reviewer/examples/*.md

# 2. Verify review prompt exists (colocated in skill folder)
ls skills/rule-reviewer/PROMPT.md

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
- [ ] Prompt file read: `PROMPT.md` (colocated in skill folder)
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

| Metric | Target | Acceptable |
|--------|--------|------------|
| Review time (FULL) | < 2 min | < 5 min |
| Review time (FOCUSED) | < 1 min | < 2 min |
| File write | < 1 sec | < 5 sec |

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
1. `skills/rule-reviewer/PROMPT.md` exists and is readable
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
   - Overall score ≥ 7.5/10
   - No CRITICAL issues
   - Contract and Metadata dimensions pass

### Cross-Validation Workflow

```
# Step 1: Create rule
Use rule-creator skill to create rules/999-test-rule.md

# Step 2: Validate creation
python scripts/schema_validator.py rules/999-test-rule.md
# Expected: exit code 0

# Step 3: Review created rule
Use rule-reviewer skill:
  target_file: rules/999-test-rule.md
  review_mode: FULL
  
# Step 4: Verify quality
# Expected: score ≥ 7.5, no CRITICAL issues
```

## Output Format Validation

### Required Sections

Every review output must contain:

```markdown
# Rule Review: <rule-name>

## Review Metadata
## Overall Score: X.X/10
## Dimension Scores
## Issues Found
## Recommendations
```

### Table Format

Dimension scores table must be valid markdown:

```markdown
| Dimension | Score | Notes |
|-----------|-------|-------|
| ... | X/10 | ... |
```

## Version Compatibility

| Component | Minimum Version |
|-----------|-----------------|
| RULE_REVIEW_PROMPT.md | Current |
| Rule schema | v3.0 |
| reviews/ directory | Writable |

## Validation Schedule

| Frequency | Checks |
|-----------|--------|
| After skill edit | Full regression |
| After prompt edit | All modes test |
| Weekly | Quick health check |
| Monthly | Performance baseline |

