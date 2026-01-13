# Input Validation Workflow

Execute validation before Stage 1 (Discovery). Fail fast on invalid inputs.

## Validation Sequence

1. **Environment checks** - Verify rules/ exists, output directories writable
2. **Required parameters** - review_date, review_mode, model
3. **Optional parameters** - filter_pattern, skip_existing, max_parallel, output_root
4. **Cross-parameter checks** - filter_pattern matches files, etc.

## Parameter Requirements

### review_date
- Format: `YYYY-MM-DD`
- Must be valid calendar date
- Year: 2024-2030 (reasonable range)

### review_mode
- Must be: `FULL` | `FOCUSED` | `STALENESS`
- Case-sensitive (uppercase only)

### model
- Format: lowercase-hyphenated (e.g., `claude-sonnet-45`, `gpt-4`)
- Regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- Length: 3-50 characters

### output_root (optional)
- Root directory for output files
- Default: `reviews/`
- Trailing slash auto-normalized
- Supports relative paths including `../`
- Subdirectories `rule-reviews/` and `summaries/` appended automatically

### filter_pattern (optional)
- Must start with `rules/` and end with `.md`
- Cannot contain `..` (no directory traversal)
- Must match at least 1 file when expanded

### skip_existing (optional)
- Boolean: `true` or `false`
- Default: `true`

### max_parallel (optional)
- Integer: 1-10 (inclusive)
- Default: 1
- Warning: >1 increases context overflow risk

## Environment Checks

**rules/ directory:**
- Must exist in current working directory
- Must be readable
- Must contain at least 1 .md file

**{output_root}/rule-reviews/ directory:**
- Must exist or be creatable
- Must be writable

**{output_root}/summaries/ directory:**
- Must exist or be creatable
- Must be writable

(Default `output_root` is `reviews/`)

## Validation Code Pattern

```python
def validate_inputs(review_date, review_mode, model, filter_pattern=None, 
                    skip_existing=True, max_parallel=1, output_root='reviews/'):
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
    
    # Normalize output_root
    output_root = output_root.rstrip('/') + '/'
    
    # Auto-create output directories
    rule_reviews_dir = f"{output_root}rule-reviews"
    if not os.path.exists(rule_reviews_dir):
        try:
            os.makedirs(rule_reviews_dir, exist_ok=True)
        except OSError:
            errors.append(f"Environment error: Cannot create {rule_reviews_dir}/ directory")
    
    summaries_dir = f"{output_root}summaries"
    if not os.path.exists(summaries_dir):
        try:
            os.makedirs(summaries_dir, exist_ok=True)
        except OSError:
            errors.append(f"Environment error: Cannot create {summaries_dir}/ directory")
    
    # If errors found, report and exit
    if errors:
        print("VALIDATION FAILED:\n")
        for error in errors:
            print(f"   {error}")
        print("\nAbort execution. Fix validation errors and retry.")
        return False
    
    print(" Input validation passed")
    return True
```

## Post-Execution Quality Checks

After bulk execution completes, verify reviews weren't shortcuts:

### Review File Size Check

Legitimate FULL reviews: typically 3000-8000 bytes

```python
def validate_review_quality(review_files):
    """Ensure reviews meet minimum quality standards."""
    issues = []
    for review_path in review_files:
        file_size = os.path.getsize(review_path)
        if file_size < 2000:
            issues.append(f"{review_path}: Suspiciously small ({file_size} bytes)")
    return issues
```

### Required Sections Check

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
    return (True, "Valid") if not missing else (False, f"Missing: {missing}")
```

### Execution Time Sanity Check

Expected: 3-5 minutes per rule minimum

```python
def validate_execution_time(start_time, end_time, rule_count):
    """Verify execution wasn't suspiciously fast."""
    duration_minutes = (end_time - start_time) / 60
    avg_minutes_per_rule = duration_minutes / rule_count
    
    if avg_minutes_per_rule < 2:
        return False, f"Suspiciously fast: {avg_minutes_per_rule:.1f} min/rule (expected 3-5)"
    
    return True, f"Reasonable pace: {avg_minutes_per_rule:.1f} min/rule"
```

## Integration Point

Validation executes before workflow Stage 1 (Discovery):

```
Skill Invocation
    ↓
INPUT VALIDATION (this workflow)
    ↓
Stage 1: Discovery (discovery.md)
    ↓
Stage 2: Review Execution (review-execution.md)
    ↓
Stage 3: Aggregation (aggregation.md)
    ↓
Stage 4: Summary Report (summary-report.md)
```

Early exit if validation fails - skip all workflow stages.
