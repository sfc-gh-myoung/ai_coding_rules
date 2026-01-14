# Skill Testing Guide: rule-creator

> ** AUDIENCE:** This document is for **skill maintainers** (humans), not for Claude.
> It provides testing procedures, troubleshooting guides, and health checks for the skill itself.

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

- **Total time** - Target: < 20 min, Acceptable: < 30 min
- **Validation iterations** - Target: 1-2, Acceptable: ≤ 3
- **User interventions** - Target: 0, Acceptable: ≤ 1

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

- **Python** - 3.11+
- **PyYAML** - 6.0+
- **Schema** - v3.0
- **RULES_INDEX** - Current

## Validation Schedule

- **After skill edit** - Full regression
- **Weekly** - Quick health check
- **Monthly** - Performance baseline
- **After schema update** - Full regression + all examples

---

## Post-Execution Validation (Quality Assurance)

### Rule Output Quality Check

After rule creation, validate output wasn't incomplete:

**Check 1: Rule File Size**
```python
def validate_rule_size(rule_path):
    """Ensure rule meets minimum completeness standards."""
    import os
    
    file_size = os.path.getsize(rule_path)
    
    # Production rules are typically 4000-12000 bytes
    # Suspiciously small = likely incomplete
    if file_size < 3000:
        return False, f"Suspiciously small ({file_size} bytes) - likely incomplete content"
    
    return True, f"Valid size ({file_size} bytes)"
```

**Check 2: Required Sections Present**
```python
def validate_rule_structure(rule_path):
    """Verify rule contains all required sections."""
    
    required_sections = [
        "## Metadata",
        "## Scope",
        "## References",
        "## Contract",
        "### Inputs and Prerequisites",
        "### Mandatory",
        "### Forbidden",
        "### Execution Steps",
        "### Output Format",
        "### Validation"
    ]
    
    with open(rule_path, 'r') as f:
        content = f.read()
    
    missing = [s for s in required_sections if s not in content]
    
    if missing:
        return False, f"Missing sections: {missing}"
    
    return True, "All required sections present"
```

**Check 3: No Placeholder Text**
```python
def validate_no_placeholders(rule_path):
    """Verify rule has no placeholder text."""
    
    placeholders = [
        "TODO",
        "[Add content]",
        "[Fill in]",
        "[Example]",
        "[TBD]",
        "...",  # Ellipsis indicating incomplete content
        "placeholder"
    ]
    
    with open(rule_path, 'r') as f:
        content = f.read().lower()
    
    found = [p for p in placeholders if p.lower() in content]
    
    if found:
        return False, f"Placeholder text found: {found}"
    
    return True, "No placeholders"
```

**Check 4: Schema Validation Clean**
```python
def validate_schema_clean(rule_path):
    """Verify schema_validator.py returns exit code 0."""
    import subprocess
    
    result = subprocess.run(
        ["python", "scripts/schema_validator.py", rule_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return False, f"Schema validation failed: {result.stdout}"
    
    # Check for CRITICAL errors in output
    if "CRITICAL" in result.stdout:
        return False, f"CRITICAL errors present"
    
    return True, "Schema validation clean (exit code 0)"
```

**Check 5: RULES_INDEX Entry Present**
```python
def validate_indexed(rule_name):
    """Verify rule is indexed in RULES_INDEX.md."""
    
    with open("RULES_INDEX.md", 'r') as f:
        content = f.read()
    
    if f"rules/{rule_name}.md" not in content:
        return False, f"Rule not found in RULES_INDEX.md"
    
    return True, "Rule properly indexed"
```

**Protocol Violation Report:**

If validation fails, generate report:
```
PROTOCOL VIOLATION DETECTED

Rule creation issues found:
  - Rule file size: 1,856 bytes (expected: 4000-12000)
  - Missing sections: ['### Anti-Patterns', '### Post-Execution Checklist']
  - Placeholder text found: ['TODO', '[Add content]']
  - Schema validation: FAILED (3 CRITICAL errors)
  - RULES_INDEX entry: MISSING

Likely cause: Agent skipped phases or left rule incomplete

Required action:
  1. Delete incomplete rule file
  2. Re-run rule-creator skill from Phase 1
  3. Verify all 5 phases executed
  4. Confirm schema validation passes (exit code 0)
```

