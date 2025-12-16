# Skill Validation: rule-creator

This document describes how to verify that the rule-creator skill is functioning correctly.

## Quick Health Check

Run these checks to verify basic functionality:

```bash
# 1. Verify skill files exist
ls skills/rule-creator/SKILL.md
ls skills/rule-creator/README.md
ls skills/rule-creator/workflows/*.md
ls skills/rule-creator/examples/*.md

# 2. Verify supporting scripts exist
ls scripts/template_generator.py
ls scripts/schema_validator.py

# 3. Verify RULES_INDEX.md is accessible
head -20 RULES_INDEX.md
```

**Expected:** All files exist, no errors.

## Functional Validation

### Test 1: Input Parsing

**Trigger:**
```
Create a new rule for TestTechnology best practices following schema
```

**Verify:**
- [ ] Technology name extracted: "TestTechnology"
- [ ] Aspect defaulted to: "core"
- [ ] Domain discovery initiated

### Test 2: Domain Discovery

**Verify:**
```bash
# Agent should search RULES_INDEX.md
grep -i "testtechnology" RULES_INDEX.md
```

- [ ] Search executed
- [ ] Domain identified or user prompted for clarification
- [ ] Next available number determined

### Test 3: Template Generation

**Verify:**
```bash
# After template generation
ls rules/NNN-testtechnology-core.md
grep -c "^## " rules/NNN-testtechnology-core.md
# Expected: 9+ sections
```

- [ ] File created
- [ ] Correct number of sections
- [ ] Contract section present

### Test 4: Schema Validation

**Verify:**
```bash
python scripts/schema_validator.py rules/NNN-testtechnology-core.md
echo $?
# Expected: 0 (after fixes)
```

- [ ] Validator runs without error
- [ ] Exit code 0 achieved
- [ ] No CRITICAL errors remain

### Test 5: Indexing

**Verify:**
```bash
grep "NNN-testtechnology" RULES_INDEX.md
```

- [ ] Entry added to index
- [ ] Correct position (sorted by number)
- [ ] All columns populated

## Regression Checklist

Run after any skill modifications:

- [ ] SKILL.md YAML frontmatter parses correctly
- [ ] All workflow files accessible
- [ ] All example files accessible
- [ ] Template generator works
- [ ] Schema validator works
- [ ] Edge cases handled (see `examples/edge-cases.md`)

## Performance Baseline

| Metric | Target | Acceptable |
|--------|--------|------------|
| Total time | < 20 min | < 30 min |
| Validation iterations | 1-2 | ≤ 3 |
| User interventions | 0 | ≤ 1 |

## Troubleshooting

### Skill Not Recognized

**Symptom:** Agent doesn't recognize "create rule" request

**Check:**
1. SKILL.md exists and has valid YAML frontmatter
2. Description contains trigger keywords
3. File is in `skills/rule-creator/` directory

### Template Generation Fails

**Symptom:** `template_generator.py` returns error

**Check:**
1. Python 3.11+ installed
2. PyYAML installed: `pip install pyyaml`
3. Filename format correct: `NNN-technology-aspect`

### Validation Never Passes

**Symptom:** Exit code 1 after 3 iterations

**Check:**
1. Review `rules/002d-schema-validator-usage.md`
2. Run with `--verbose` flag
3. Check similar rules for structure examples

## Integration Verification

### With rule-reviewer

After creating a rule, verify quality:

```
Use the rule-reviewer skill.

target_file: rules/<created-rule>.md
review_date: <today>
review_mode: FULL
model: claude-sonnet-45
```

**Expected:**
- Overall score ≥ 75/100
- No CRITICAL issues
- No HIGH issues in Actionability or Completeness dimensions

## Version Compatibility

| Component | Minimum Version |
|-----------|-----------------|
| Python | 3.11+ |
| PyYAML | 6.0+ |
| Schema | v3.0 |
| RULES_INDEX | Current |

## Validation Schedule

| Frequency | Checks |
|-----------|--------|
| After skill edit | Full regression |
| Weekly | Quick health check |
| Monthly | Performance baseline |
| After schema update | Full regression + all examples |

