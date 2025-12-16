# Skill Validation: doc-reviewer

This document describes how to verify that the doc-reviewer skill is functioning correctly.

## Quick Health Check

Run these checks to verify basic functionality:

```bash
# 1. Verify skill files exist
ls skills/doc-reviewer/SKILL.md
ls skills/doc-reviewer/README.md
ls skills/doc-reviewer/PROMPT.md
ls skills/doc-reviewer/workflows/*.md
ls skills/doc-reviewer/examples/*.md
ls skills/doc-reviewer/tests/*.md

# 2. Verify reviews directory exists (or can be created)
ls reviews/ || mkdir -p reviews/

# 3. Verify default documentation exists
ls README.md CONTRIBUTING.md docs/*.md 2>/dev/null
```

**Expected:** All skill files exist, no errors.

## Functional Validation

### Test 1: Input Validation

**Trigger:**

```text
Use the doc-reviewer skill.

target_files: [README.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Verify:**

- [ ] All inputs accepted
- [ ] No validation errors
- [ ] Review proceeds

### Test 2: Invalid Input Handling

**Trigger (invalid date):**

```text
target_files: [README.md]
review_date: 12/16/2025
review_mode: FULL
model: claude-sonnet45
```

**Verify:**

- [ ] Error detected
- [ ] Clear message: "Invalid date format"
- [ ] Expected format shown (YYYY-MM-DD)
- [ ] Review does not proceed

### Test 3: Default Target Discovery

**Trigger:**

```text
Use the doc-reviewer skill.

review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Verify:**

- [ ] Default files discovered (README.md, CONTRIBUTING.md, docs/*.md)
- [ ] Message shows which files will be reviewed
- [ ] Review proceeds with discovered files

### Test 4: Review Execution

**Verify during review:**

- [ ] Prompt file read: `PROMPT.md` (colocated in skill folder)
- [ ] Target files read successfully
- [ ] Cross-reference verification performed
- [ ] Link validation performed
- [ ] Baseline rules checked (if exist)
- [ ] Review generated with all sections

### Test 5: File Output

**Verify:**

```bash
ls reviews/README-claude-sonnet45-2025-12-16.md
head -30 reviews/README-claude-sonnet45-2025-12-16.md
```

- [ ] File created at expected path
- [ ] Contains review header
- [ ] Contains scores table
- [ ] Contains verification tables
- [ ] Contains recommendations

### Test 6: No-Overwrite Safety

**Pre-condition:** Run same review twice

**Verify:**

```bash
ls reviews/README-claude-sonnet45-2025-12-16*.md
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
- [ ] All test files accessible
- [ ] FULL mode works
- [ ] FOCUSED mode works (with focus_area)
- [ ] STALENESS mode works
- [ ] Single scope works
- [ ] Collection scope works
- [ ] No-overwrite logic works
- [ ] Error handling works (see `workflows/error-handling.md`)

## Mode-Specific Validation

### FULL Mode

```text
review_mode: FULL
```

**Verify output contains:**

- [ ] All 6 dimension scores
- [ ] Overall score (X/100)
- [ ] Cross-Reference Verification table
- [ ] Link Validation table
- [ ] Baseline Compliance Check (if rules exist)
- [ ] Issues by severity
- [ ] Documentation Perspective Checklist

### FOCUSED Mode

```text
review_mode: FOCUSED
focus_area: accuracy
```

**Verify output contains:**

- [ ] Single dimension score (Accuracy)
- [ ] Cross-Reference Verification table (detailed)
- [ ] Accuracy-specific recommendations
- [ ] NO other dimension scores

### STALENESS Mode

```text
review_mode: STALENESS
```

**Verify output contains:**

- [ ] Staleness and Structure scores only
- [ ] Link Validation table
- [ ] Version References table
- [ ] Deprecated Patterns section
- [ ] Staleness Risk Assessment

## Scope-Specific Validation

### Single Scope (Default)

```text
target_files: [README.md, CONTRIBUTING.md]
review_scope: single
```

**Verify:**

- [ ] Two output files created
- [ ] Each file contains complete review
- [ ] Filenames match document names

### Collection Scope

```text
target_files: [README.md, CONTRIBUTING.md]
review_scope: collection
```

**Verify:**

- [ ] Single output file: `docs-collection-...`
- [ ] Contains Overview section
- [ ] Contains Summary Scores table
- [ ] Contains individual review sections

## Verification Table Validation

### Cross-Reference Verification

**Verify table contains:**

- [ ] Reference column (file paths, commands, etc.)
- [ ] Type column (file, directory, command, function)
- [ ] Location column (doc:line)
- [ ] Exists? column (✅/❌)
- [ ] Notes column

### Link Validation

**Verify table contains:**

- [ ] Link column (URL or path)
- [ ] Type column (internal, anchor, external)
- [ ] Source column (doc:line)
- [ ] Status column (✅/⚠️/❌)
- [ ] Notes column

### Baseline Compliance

**Verify (if rules exist):**

- [ ] Shows which rules were checked
- [ ] Lists requirements from rules
- [ ] Shows compliance status
- [ ] Notes non-compliance issues

## Performance Baseline

| Metric | Target | Acceptable |
|--------|--------|------------|
| Review time (FULL, single doc) | < 2 min | < 5 min |
| Review time (FULL, 5 docs) | < 5 min | < 10 min |
| Review time (STALENESS) | < 1 min | < 2 min |
| File write | < 1 sec | < 5 sec |

## Troubleshooting

### Skill Not Recognized

**Symptom:** Agent doesn't recognize "review docs" request

**Check:**

1. SKILL.md exists and has valid YAML frontmatter
2. Description contains trigger keywords
3. File is in `skills/doc-reviewer/` directory

### Review Generation Fails

**Symptom:** Error during review execution

**Check:**

1. `skills/doc-reviewer/PROMPT.md` exists and is readable
2. Target documentation files exist
3. Target files are valid markdown

### No Default Files Found

**Symptom:** "No documentation files found" error

**Check:**

1. README.md exists in project root
2. CONTRIBUTING.md exists (optional)
3. docs/ directory exists with .md files

### File Write Fails

**Symptom:** Review completes but file not created

**Check:**

1. `reviews/` directory exists
2. Directory is writable
3. Filename doesn't exceed system limits

### Verification Tables Empty

**Symptom:** Cross-reference or link tables have no entries

**Check:**

1. Documentation contains backticked references
2. Documentation contains markdown links
3. Regex patterns in review-execution.md match content format

## Deployment Verification

After deployment to another project:

```bash
# Verify skill deployed
ls skills/doc-reviewer/SKILL.md

# Verify can review that project's docs
# (trigger doc-reviewer skill)
```

**Expected:**

- Skill files present in deployed project
- Can review deployed project's documentation
- Output written to deployed project's reviews/

## Output Format Validation

### Required Sections

Every review output must contain:

```markdown
## Documentation Review: <doc-name>

### Scores
| Criterion | Score | Notes |
...

**Overall:** X/100

**Reviewing Model:** [model name]

### Critical Issues (Must Fix)
...

### Improvements (Should Fix)
...

### Documentation Perspective Checklist
...
```

### Table Format

Score table must be valid markdown:

```markdown
| Criterion | Max | Raw | Points | Notes |
|-----------|-----|-----|--------|-------|
| Accuracy | 25 | X/5 | Y/25 | ... |
| ... | ... | ... | ... | ... |
```

## Version Compatibility

| Component | Minimum Version |
|-----------|-----------------|
| PROMPT.md | Current |
| reviews/ directory | Writable |
| Target docs | Valid markdown |

## Validation Schedule

| Frequency | Checks |
|-----------|--------|
| After skill edit | Full regression |
| After prompt edit | All modes test |
| Weekly | Quick health check |
| Monthly | Performance baseline |

