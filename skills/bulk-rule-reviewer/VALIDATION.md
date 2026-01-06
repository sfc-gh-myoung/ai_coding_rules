# Input Validation Rules

## Purpose

Define validation rules for all input parameters to the bulk-rule-reviewer skill. Ensures safe execution and early error detection.

---

## Required Parameters

### review_date

**Type:** String (YYYY-MM-DD format)

**Validation Rules:**
1. Must match regex: `^\d{4}-\d{2}-\d{2}$`
2. Must be a valid calendar date (no 2026-02-30)
3. Year must be ≥2024 and ≤2030 (reasonable range)
4. Month must be 01-12
5. Day must be valid for the given month/year

**Valid Examples:**
- `2026-01-06`
- `2025-12-31`
- `2024-03-15`

**Invalid Examples:**
- `01-06-2026` ❌ (wrong format)
- `2026/01/06` ❌ (wrong separator)
- `2026-13-01` ❌ (invalid month)
- `2026-02-30` ❌ (invalid day)
- `26-01-06` ❌ (2-digit year)

**Error Message:**
```
Invalid review_date: "{value}"
Expected format: YYYY-MM-DD (e.g., 2026-01-06)
```

---

### review_mode

**Type:** Enum (FULL | FOCUSED | STALENESS)

**Validation Rules:**
1. Must be one of: `FULL`, `FOCUSED`, `STALENESS`
2. Case-sensitive (uppercase only)
3. No whitespace or special characters

**Valid Examples:**
- `FULL`
- `FOCUSED`
- `STALENESS`

**Invalid Examples:**
- `full` ❌ (lowercase)
- `Full` ❌ (mixed case)
- `COMPREHENSIVE` ❌ (not in enum)
- ` FULL ` ❌ (whitespace)
- `FULL_MODE` ❌ (not in enum)

**Error Message:**
```
Invalid review_mode: "{value}"
Expected one of: FULL, FOCUSED, STALENESS
```

---

### model

**Type:** String (lowercase-hyphenated slug)

**Validation Rules:**
1. Must match regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
2. Only lowercase letters, numbers, and hyphens
3. Cannot start or end with hyphen
4. Cannot contain consecutive hyphens
5. Length: 3-50 characters

**Valid Examples:**
- `claude-sonnet-45`
- `gpt-4`
- `gemini-pro`
- `claude-3-opus`

**Invalid Examples:**
- `Claude-Sonnet-45` ❌ (uppercase)
- `claude_sonnet_45` ❌ (underscores)
- `claude-sonnet-45-` ❌ (trailing hyphen)
- `-claude-sonnet` ❌ (leading hyphen)
- `claude--sonnet` ❌ (consecutive hyphens)
- `claude sonnet` ❌ (space)

**Error Message:**
```
Invalid model: "{value}"
Expected format: lowercase-hyphenated (e.g., claude-sonnet-45, gpt-4)
```

---

## Optional Parameters

### filter_pattern

**Type:** String (glob pattern)

**Validation Rules:**
1. Must be a valid glob pattern
2. Must start with `rules/` (directory prefix)
3. Must end with `.md` (file extension)
4. Can contain wildcards: `*`, `?`, `[abc]`, `{a,b,c}`
5. Cannot contain `..` (no directory traversal)
6. Cannot be empty string

**Valid Examples:**
- `rules/*.md` (default - all rules)
- `rules/100-*.md` (Snowflake rules)
- `rules/*-core.md` (core rules)
- `rules/[12]*.md` (100-series and 200-series)
- `rules/2{0,1}*.md` (200-series and 210-series)

**Invalid Examples:**
- `*.md` ❌ (missing rules/ prefix)
- `rules/*` ❌ (missing .md extension)
- `rules/../secrets/*.md` ❌ (directory traversal)
- `../rules/*.md` ❌ (directory traversal)
- ` ` ❌ (empty/whitespace only)

**Error Message:**
```
Invalid filter_pattern: "{value}"
Expected format: rules/*.md (glob pattern within rules/ directory)
```

---

### skip_existing

**Type:** Boolean

**Validation Rules:**
1. Must be boolean value: `true` or `false`
2. Case-sensitive (lowercase only)
3. No quotes around value

**Valid Examples:**
- `true`
- `false`

**Invalid Examples:**
- `True` ❌ (uppercase)
- `TRUE` ❌ (all caps)
- `"true"` ❌ (quoted string)
- `1` ❌ (numeric)
- `yes` ❌ (string)

**Error Message:**
```
Invalid skip_existing: "{value}"
Expected: true or false (boolean)
```

---

### max_parallel

**Type:** Integer (1-10)

**Validation Rules:**
1. Must be integer (no decimals)
2. Must be ≥1 (at least sequential)
3. Must be ≤10 (context safety limit)
4. Cannot be zero or negative

**Valid Examples:**
- `1` (default - sequential)
- `5`
- `10`

**Invalid Examples:**
- `0` ❌ (zero not allowed)
- `-1` ❌ (negative not allowed)
- `15` ❌ (exceeds limit)
- `2.5` ❌ (decimal not allowed)
- `"5"` ❌ (string not integer)

**Error Message:**
```
Invalid max_parallel: "{value}"
Expected: integer between 1 and 10 (inclusive)
```

---

## Environment Validation

### rules/ Directory Exists

**Validation Rule:**
- `rules/` directory must exist in current working directory
- Directory must be readable
- Directory must contain at least 1 `.md` file

**Error Message:**
```
Environment error: rules/ directory not found
Verify working directory is project root and rules/ directory exists
```

---

### reviews/ Directory Writable

**Validation Rule:**
- `reviews/` directory must exist or be creatable
- Directory must be writable
- Sufficient disk space for output files

**Error Message:**
```
Environment error: Cannot write to reviews/ directory
Check permissions and disk space
```

---

## Validation Sequence

Execute validation in this order (fail fast):

1. **Environment checks** (rules/ exists, reviews/ writable)
2. **Required parameters** (review_date, review_mode, model)
3. **Optional parameters** (filter_pattern, skip_existing, max_parallel)
4. **Cross-parameter checks** (see below)

---

## Cross-Parameter Validation

### filter_pattern × rules/ Contents

**Rule:** If filter_pattern specified, must match at least 1 file

**Check:**
```bash
matching_files=$(find rules -name "<pattern>" -type f | wc -l)
if [ "$matching_files" -eq 0 ]; then
  echo "ERROR: No files match filter_pattern: <pattern>"
  exit 1
fi
```

**Error Message:**
```
No rule files found matching pattern: {filter_pattern}
Try: rules/*.md (all rules) or rules/100-*.md (Snowflake rules)
```

---

### max_parallel × Review Count

**Rule:** If max_parallel >1, warn about context overflow risk

**Check:**
```python
if max_parallel > 1:
    print("WARNING: Parallel execution increases context overflow risk")
    print("Recommended: max_parallel=1 (sequential) for batches >50 rules")
```

**Warning Message:**
```
WARNING: max_parallel={value} may cause context overflow for large batches
Recommended: max_parallel=1 (sequential) for stability
```

---

## Validation Code Pattern

```python
def validate_inputs(review_date, review_mode, model, filter_pattern=None, 
                    skip_existing=True, max_parallel=1):
    """Validate all input parameters before execution."""
    import re
    import os
    from datetime import datetime
    
    errors = []
    
    # Validate review_date
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', review_date):
        errors.append(f"Invalid review_date: '{review_date}' - Expected format: YYYY-MM-DD")
    else:
        try:
            datetime.strptime(review_date, '%Y-%m-%d')
        except ValueError:
            errors.append(f"Invalid review_date: '{review_date}' - Not a valid calendar date")
    
    # Validate review_mode
    if review_mode not in ['FULL', 'FOCUSED', 'STALENESS']:
        errors.append(f"Invalid review_mode: '{review_mode}' - Expected: FULL, FOCUSED, or STALENESS")
    
    # Validate model
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', model):
        errors.append(f"Invalid model: '{model}' - Expected: lowercase-hyphenated (e.g., claude-sonnet-45)")
    
    # Validate filter_pattern (if provided)
    if filter_pattern is not None:
        if not filter_pattern.startswith('rules/'):
            errors.append(f"Invalid filter_pattern: '{filter_pattern}' - Must start with 'rules/'")
        if not filter_pattern.endswith('.md'):
            errors.append(f"Invalid filter_pattern: '{filter_pattern}' - Must end with '.md'")
        if '..' in filter_pattern:
            errors.append(f"Invalid filter_pattern: '{filter_pattern}' - Directory traversal not allowed")
    
    # Validate skip_existing
    if not isinstance(skip_existing, bool):
        errors.append(f"Invalid skip_existing: '{skip_existing}' - Expected: true or false (boolean)")
    
    # Validate max_parallel
    if not isinstance(max_parallel, int) or max_parallel < 1 or max_parallel > 10:
        errors.append(f"Invalid max_parallel: '{max_parallel}' - Expected: integer between 1 and 10")
    
    # Environment checks
    if not os.path.isdir('rules'):
        errors.append("Environment error: rules/ directory not found")
    
    if not os.path.exists('reviews'):
        try:
            os.makedirs('reviews')
        except OSError:
            errors.append("Environment error: Cannot create reviews/ directory")
    
    # If errors found, report and exit
    if errors:
        print("VALIDATION FAILED:\n")
        for error in errors:
            print(f"  ❌ {error}")
        print("\nAbort execution. Fix validation errors and retry.")
        return False
    
    print("✓ Input validation passed")
    return True
```

---

## Testing Validation

**Test Cases:** See `tests/validation-tests.md`

**Coverage:**
- All valid input combinations (happy path)
- All invalid input variations (error cases)
- Edge cases (boundary values, empty strings, special characters)
- Cross-parameter validation
- Environment validation

---

## Error Recovery

### Invalid Input

**Action:**
1. Report all validation errors (don't fail on first)
2. Print clear error messages with examples
3. Exit without executing bulk review
4. User must fix inputs and retry

### Environment Issues

**Action:**
1. Report specific environment problem
2. Suggest resolution steps
3. Exit gracefully
4. User must fix environment and retry

---

## Success Output

When validation passes:

```
✓ Input validation passed

Parameters:
  review_date: 2026-01-06
  review_mode: FULL
  model: claude-sonnet-45
  filter_pattern: rules/*.md
  skip_existing: true
  max_parallel: 1

Environment:
  rules/ directory: ✓ (113 files found)
  reviews/ directory: ✓ (writable)

Proceeding with bulk review...
```

---

## Integration with Skill

Validation executes **before** workflow Stage 1 (Discovery):

```
Skill Invocation
    ↓
VALIDATION (this document)
    ↓
Stage 1: Discovery (01-discovery.md)
    ↓
Stage 2: Review Execution (02-review-execution.md)
    ↓
Stage 3: Aggregation (03-aggregation.md)
    ↓
Stage 4: Summary Report (04-summary-report.md)
```

**Early exit:** If validation fails, skip all workflow stages.

---

## Related Documentation

- **Skill Definition:** `SKILL.md`
- **Usage Guide:** `README.md`
- **Test Cases:** `tests/validation-tests.md`

---

## Skill Availability Check

**Rule:** rule-reviewer skill must be available (installed OR local)

**Check:**
```python
def validate_skill_availability():
    """Verify rule-reviewer is accessible."""
    # Check 1: Installed skill
    try:
        invoke_skill("rule-reviewer", test_mode=True)
        return True, "installed"
    except SkillNotFoundError:
        pass
    
    # Check 2: Local skill
    if os.path.exists("skills/rule-reviewer/PROMPT.md"):
        return True, "local"
    
    # Neither found
    return False, None

is_available, location = validate_skill_availability()
if not is_available:
    raise ValidationError(
        "rule-reviewer skill not found. "
        "Install via agent tool OR ensure skills/rule-reviewer/ exists."
    )
```

**Error Message:**
```
ERROR: rule-reviewer skill not found

Options:
  A) Install rule-reviewer via your agent tool (recommended)
  B) Clone/copy skills/rule-reviewer/ into this project
  C) Verify skills/rule-reviewer/PROMPT.md exists

Current search paths:
  - Agent installed skills: Not found
  - Local: /path/to/project/skills/rule-reviewer/ (not found)
```

---

## Post-Execution Validation (Quality Assurance)

### Review File Quality Check

After bulk execution completes, validate reviews weren't shortcuts:

**Check 1: Review File Size**
```python
def validate_review_quality(review_files):
    """Ensure reviews meet minimum quality standards."""
    
    issues = []
    
    for review_path in review_files:
        file_size = os.path.getsize(review_path)
        
        # Legitimate reviews are typically 3000-8000 bytes
        # Suspiciously small = likely shortcut
        if file_size < 2000:
            issues.append(f"{review_path}: Suspiciously small ({file_size} bytes)")
    
    return issues
```

**Check 2: Required Sections Present**
```python
def validate_review_structure(review_path):
    """Verify review contains required sections."""
    
    required_sections = [
        "### Agent Executability Verdict",
        "### Dimension Scores",
        "**Overall:** ",
        "### Critical Issues",
        "### Recommendations"
    ]
    
    with open(review_path, 'r') as f:
        content = f.read()
    
    missing = [s for s in required_sections if s not in content]
    
    if missing:
        return False, f"Missing sections: {missing}"
    
    return True, "Valid structure"
```

**Check 3: Execution Time Sanity**
```python
def validate_execution_time(start_time, end_time, rule_count):
    """Verify execution wasn't suspiciously fast."""
    
    duration_minutes = (end_time - start_time) / 60
    avg_minutes_per_rule = duration_minutes / rule_count
    
    # Expected: 3-5 minutes per rule minimum
    if avg_minutes_per_rule < 2:
        return False, f"Suspiciously fast: {avg_minutes_per_rule:.1f} min/rule (expected 3-5)"
    
    return True, f"Reasonable pace: {avg_minutes_per_rule:.1f} min/rule"
```

**Protocol Violation Report:**

If validation fails, generate report:
```
PROTOCOL VIOLATION DETECTED

Review quality issues found:
  - 15 reviews suspiciously small (<2000 bytes)
  - 8 reviews missing required sections
  - Average review time: 1.2 min/rule (expected: 3-5 min/rule)

Likely cause: Agent took shortcuts instead of invoking rule-reviewer skill

Required action:
  1. Delete suspicious review files
  2. Re-run with skip_existing=false
  3. Monitor execution for protocol compliance
```
