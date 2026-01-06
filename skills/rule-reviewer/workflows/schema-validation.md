# Schema Validation Workflow

## Purpose

Integrate automated schema validation into the rule review process to provide objective, deterministic Parsability scoring based on compliance with `schemas/rule-schema.yml` v3.2 standards.

## When to Use

This workflow is executed as **MANDATORY STEP 2** in every FULL and FOCUSED review mode (after reading the rule file, before scoring dimensions). STALENESS mode may skip this workflow.

## Prerequisites

- Rule file has been read completely
- `scripts/schema_validator.py` is available in project root
- Python 3.11+ environment is active

## Execution Steps

### Step 1: Run Schema Validator

Execute the schema validator and capture both stdout and exit code:

```python
import subprocess
from pathlib import Path

def run_schema_validation(target_file: str) -> tuple[str, int, dict]:
    """
    Run schema validator and parse results.
    
    Returns:
        (output_text, exit_code, error_counts)
    """
    result = subprocess.run(
        ['python', 'scripts/schema_validator.py', target_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    output = result.stdout + result.stderr
    exit_code = result.returncode
    
    # Count error severities
    error_counts = {
        'CRITICAL': output.count('[CRITICAL]'),
        'HIGH': output.count('[HIGH]'),
        'MEDIUM': output.count('[MEDIUM]'),
        'INFO': output.count('[INFO]')
    }
    
    return (output, exit_code, error_counts)
```

### Step 2: Parse Error Messages

Extract specific error messages with line numbers for the Critical Issues section:

```python
import re

def parse_schema_errors(output: str) -> dict[str, list[str]]:
    """
    Parse validator output into categorized error lists.
    
    Returns:
        {
            'CRITICAL': ['Error message 1', 'Error message 2'],
            'HIGH': [...],
            'MEDIUM': [...],
            'INFO': [...]
        }
    """
    errors = {'CRITICAL': [], 'HIGH': [], 'MEDIUM': [], 'INFO': []}
    
    # Pattern: [SEVERITY] Message (may span multiple lines)
    # Look for lines starting with severity markers
    pattern = r'\[(CRITICAL|HIGH|MEDIUM|INFO)\]\s+(.+?)(?=\n\[|$)'
    
    for match in re.finditer(pattern, output, re.DOTALL):
        severity = match.group(1)
        message = match.group(2).strip()
        
        # Extract line number if present
        line_match = re.search(r'Line:\s+(\d+)', message)
        line_num = line_match.group(1) if line_match else 'N/A'
        
        # Format message
        formatted = f"{message} (line {line_num})" if line_num != 'N/A' else message
        errors[severity].append(formatted)
    
    return errors
```

### Step 3: Apply Scoring Caps

Determine maximum Parsability score based on schema validation results:

```python
def calculate_parsability_cap(error_counts: dict) -> int:
    """
    Calculate maximum allowed Parsability score based on schema errors.
    
    Returns:
        Maximum score (1-5)
    """
    critical_count = error_counts.get('CRITICAL', 0)
    high_count = error_counts.get('HIGH', 0)
    
    if critical_count >= 1:
        return 2  # Cap at 2/5 (6/15)
    elif high_count >= 3:
        return 3  # Cap at 3/5 (9/15)
    else:
        return 5  # No cap
```

### Step 4: Generate Review Output Section

Format schema validation results for inclusion in review:

```python
def format_schema_section(error_counts: dict, parsed_errors: dict, 
                          parsability_score: int) -> str:
    """
    Generate formatted schema validation section for review.
    
    Returns:
        Markdown-formatted section
    """
    section = f"""#### Parsability Score: {parsability_score}/5 ({parsability_score * 3}/15)

**Schema Validation Results:**
- CRITICAL: {error_counts['CRITICAL']} errors
- HIGH: {error_counts['HIGH']} errors
- MEDIUM: {error_counts['MEDIUM']} errors

"""
    
    # Add rationale
    if error_counts['CRITICAL'] >= 1:
        section += "**Rationale:** Schema validation detected CRITICAL errors, capping this score at 2/5 per rubric.\n\n"
    elif error_counts['HIGH'] >= 3:
        section += "**Rationale:** Schema validation detected 3+ HIGH errors, capping this score at 3/5 per rubric.\n\n"
    else:
        section += "**Rationale:** Schema validation passed with no critical violations.\n\n"
    
    # Add critical schema violations if present
    if error_counts['CRITICAL'] > 0 or error_counts['HIGH'] > 0:
        section += "**Critical Schema Violations:**\n"
        
        for i, error in enumerate(parsed_errors['CRITICAL'], 1):
            section += f"{i}. [CRITICAL] {error}\n"
        
        for i, error in enumerate(parsed_errors['HIGH'], len(parsed_errors['CRITICAL']) + 1):
            section += f"{i}. [HIGH] {error}\n"
        
        section += "\n"
    
    return section
```

### Step 5: Document in Critical Issues

Add schema violations to the overall Critical Issues section:

```python
def add_schema_to_critical_issues(critical_issues: list, parsed_errors: dict) -> list:
    """
    Merge schema violations into Critical Issues list.
    
    Returns:
        Updated critical_issues list
    """
    schema_issues = []
    
    # CRITICAL errors always go to Critical Issues
    for error in parsed_errors['CRITICAL']:
        schema_issues.append(f"**Schema Violation (CRITICAL):** {error}")
    
    # HIGH errors with count ≥3 also go to Critical Issues
    if len(parsed_errors['HIGH']) >= 3:
        for error in parsed_errors['HIGH']:
            schema_issues.append(f"**Schema Violation (HIGH):** {error}")
    
    return critical_issues + schema_issues
```

## Error Handling

### Validator Not Found

```python
if not Path('scripts/schema_validator.py').exists():
    print("WARNING: schema_validator.py not found. Skipping schema validation.")
    print("Parsability will be scored manually without schema validation caps.")
    return None
```

### Validator Execution Failed

```python
try:
    result = subprocess.run([...], timeout=30)
except subprocess.TimeoutExpired:
    print("WARNING: Schema validation timed out after 30s.")
    print("Proceeding with manual Parsability scoring.")
    return None
except Exception as e:
    print(f"WARNING: Schema validation failed: {e}")
    print("Proceeding with manual Parsability scoring.")
    return None
```

### Invalid Output Format

```python
if not output or exit_code not in [0, 1]:
    print(f"WARNING: Unexpected validator output (exit code {exit_code})")
    print("Proceeding with manual Parsability scoring.")
    return None
```

## Integration Points

This workflow integrates with:

1. **review-execution.md** - Called as Step 2 (after file read, before dimension scoring)
2. **PROMPT.md** - Provides scoring caps and format requirements
3. **file-write.md** - Schema results included in final review output

## Expected Output

The workflow produces three outputs:

1. **error_counts** - Dictionary of counts by severity (used for scoring caps)
2. **parsed_errors** - Dictionary of error messages by severity (used for Critical Issues)
3. **schema_section** - Formatted markdown section (inserted into Parsability dimension)

## Success Criteria

- Schema validator executed successfully
- Error counts extracted correctly
- Parsability cap applied per rubric rules
- All CRITICAL/HIGH errors documented in review
- Schema section formatted per PROMPT.md requirements

## Example Output

```markdown
#### Parsability Score: 2/5 (6/15)

**Schema Validation Results:**
- CRITICAL: 1 errors
- HIGH: 2 errors
- MEDIUM: 3 errors

**Rationale:** Schema validation detected CRITICAL errors, capping this score at 2/5 per rubric.

**Critical Schema Violations:**
1. [CRITICAL] Missing metadata field: Depends (line 10)
2. [HIGH] Section order violation: Contract appears before References (line 45)
3. [HIGH] Metadata field order incorrect: TokenBudget before Keywords (line 8)
```

## Review Mode Considerations

- **FULL mode:** Always run schema validation (mandatory)
- **FOCUSED mode:** Run if Parsability is one of the evaluated dimensions
- **STALENESS mode:** Skip schema validation (not relevant for staleness checks)
