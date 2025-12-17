# Schema Validator Usage: Validation Commands and Error Resolution

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** schema validator, validation errors, error resolution, CI/CD integration, exit codes, command selection, output parsing, automation workflow, JSON output, quiet mode, programmatic integration, regex patterns, error categorization
**TokenBudget:** ~4800
**ContextTier:** High
**Depends:** rules/002-rule-governance.md, rules/000-global-core.md

## Purpose

Comprehensive guide for running schema_validator.py, interpreting validation output, resolving common errors, and integrating validation into CI/CD workflows.

## Rule Scope

All AI agents validating rule files against schemas/rule-schema.yml.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Basic command** - `python3 scripts/schema_validator.py rules/NNN-rule.md`
- **Verbose mode** - Add `--verbose` for detailed check output
- **Directory validation** - `python3 scripts/schema_validator.py rules/` to validate all rules
- **Success criteria** - 0 CRITICAL errors required, HIGH/MEDIUM errors review and fix
- **Common errors** - Missing metadata, wrong Keywords count, Contract missing XML tags

**Pre-Execution Checklist:**
- [ ] Python 3.8+ installed with PyYAML library
- [ ] schema_validator.py accessible in scripts/ directory
- [ ] schemas/rule-schema.yml file present
- [ ] Rule file exists and is readable
- [ ] Ready to fix errors if validation fails

## Contract

<inputs_prereqs>
Rule file to validate; schemas/rule-schema.yml; Python 3.8+ environment; PyYAML installed
</inputs_prereqs>

<mandatory>
scripts/schema_validator.py; schemas/rule-schema.yml; Python 3 with PyYAML; text editor for fixes
</mandatory>

<forbidden>
Committing rules with CRITICAL errors; skipping validation; modifying schema_validator.py to pass invalid rules
</forbidden>

<steps>
1. Run schema_validator.py on rule file
2. Review validation output (CRITICAL, HIGH, MEDIUM, INFO)
3. Fix CRITICAL errors (required for passing)
4. Review and fix HIGH errors (strongly recommended)
5. Consider MEDIUM errors (optional improvements)
6. Re-run validation until 0 CRITICAL errors
</steps>

<output_format>
Validation report showing passed checks and error counts by severity
</output_format>

<validation>
- schema_validator.py runs without Python errors
- Validation report generated successfully
- CRITICAL error count displayed accurately
- Error messages include line numbers and fix suggestions
</validation>

## Running the Validator

### Basic Commands

```bash
# Validate single rule file
python3 scripts/schema_validator.py rules/002-rule-governance.md

# Validate all rules in directory
python3 scripts/schema_validator.py rules/

# Verbose output with detailed checks
python3 scripts/schema_validator.py rules/002-rule-governance.md --verbose

# Validate specific subdirectory
python3 scripts/schema_validator.py rules/snowflake/

# Use custom schema file
python3 scripts/schema_validator.py rules/002-rule-governance.md --schema schemas/custom-schema.yml

# Test new schema version
python3 scripts/schema_validator.py rules/ --schema schemas/rule-schema-v4-draft.yml
```

### Command Options

**Available Options:**
- **`[file/dir]`** - Path to validate (e.g., `002-rule-governance.md`)
- **`--schema SCHEMA`** - Custom schema file path
- **`--verbose`, `-v`** - Show all check details
- **`--quiet`, `-q`** - Show only summary, suppress individual file reports
- **`--json`** - Output results in JSON format
- **`--strict`** - Treat warnings as errors
- **`--debug`** - Enable debug logging

### Exit Code Behavior

The validator uses standard shell exit codes to indicate validation status. AI agents must check exit codes to determine success/failure programmatically.

**Exit Codes:**
- **Exit 0 (PASS):** No CRITICAL or HIGH errors
- **Exit 0 (WARN):** Only MEDIUM errors (without --strict)
- **Exit 1 (FAIL):** One or more CRITICAL errors
- **Exit 1 (FAIL):** One or more HIGH errors
- **Exit 1 (FAIL):** Any errors with --strict flag
- **Exit 1 (FAIL):** Invalid path or schema error

**Shell Usage Pattern:**
```bash
python3 scripts/schema_validator.py rules/002-rule-governance.md
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "[PASS] Validation passed"
else
    echo "[FAIL] Validation failed (exit code: $EXIT_CODE)"
    exit 1
fi
```

**Python Usage Pattern:**
```python
import subprocess

result = subprocess.run(
    ['python3', 'scripts/schema_validator.py', 'rules/002-rule-governance.md'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("[PASS] Validation passed")
else:
    print(f"[FAIL] Validation failed (exit code: {result.returncode})")
    print(result.stdout)  # Parse validation output
```

### Command Selection Logic

AI agents should select the appropriate command and options based on the validation scenario.

#### Decision Tree

**Scenario 1: Validate Single Newly Created/Edited Rule**
- Command: `python3 scripts/schema_validator.py [file]`
- When: Creating new rule, editing existing rule
- Output: Detailed validation report with all errors
- Exit Code: 0 if no CRITICAL/HIGH, 1 if failed

**Scenario 2: Interactive Directory Validation (Default)**
- Command: `python3 scripts/schema_validator.py [dir]`
- When: Manual validation, need to see individual file details
- Output: Individual file reports + enhanced summary with failed files list
- Exit Code: 0 if no files have CRITICAL/HIGH, 1 if any failed

**Scenario 3: CI/CD Quick Check (Quiet Mode)**
- Command: `python3 scripts/schema_validator.py [dir] --quiet`
- When: CI/CD pipeline, only need summary stats
- Output: Summary + failed/warning file lists only (no individual reports)
- Exit Code: 0 if no files have CRITICAL/HIGH, 1 if any failed
- Use Case: Pre-commit hooks, GitHub Actions status checks

**Scenario 4: Programmatic Integration (JSON Mode)**
- Command: `python3 scripts/schema_validator.py [dir] --json`
- When: Need structured output for parsing, CI/CD integration
- Output: JSON only (no text output)
- Exit Code: 0 if no files have CRITICAL/HIGH, 1 if any failed
- Use Case: Custom dashboards, issue tracker integration, metrics collection

**Scenario 5: Strict Validation (Treat Warnings as Errors)**
- Command: `python3 scripts/schema_validator.py [file/dir] --strict`
- When: Pre-commit validation, must have zero errors
- Output: Same as base command, but MEDIUM errors cause exit code 1
- Exit Code: 0 only if completely clean, 1 if ANY errors
- Use Case: Release validation, production rule checks

**Scenario 6: Debugging Validation Issues (Verbose Mode)**
- Command: `python3 scripts/schema_validator.py [file] --verbose`
- When: Validation behaving unexpectedly, need detailed check info
- Output: Shows all passed checks + errors with detailed context
- Exit Code: Same as base command
- Use Case: Troubleshooting validation logic, understanding check behavior

**Scenario 7: Custom Schema Validation**
- Command: `python3 scripts/schema_validator.py [file/dir] --schema [schema_path]`
- When: Testing new schema versions, alternate schema sets
- Default: schemas/rule-schema.yml (if --schema omitted)
- Output: Same as base command
- Exit Code: Same as base command
- Use Case: Schema development, multi-version validation

#### Option Combinations

**Valid Combinations:**
- `--json --strict` - JSON output with strict mode (warnings = failure)
- `--verbose --strict` - Detailed output with strict mode
- `--debug --json` - Debug logging to stderr + JSON to stdout
- `--schema [path] --strict` - Custom schema with strict mode

**Precedence Rules:**
- `--json` overrides `--quiet` (JSON output only, no text)
- `--quiet` suppresses `--verbose` (summary only, no details)
- `--strict` works with all output modes
- `--debug` outputs to stderr (doesn't interfere with stdout)

**Invalid/Redundant Combinations:**
- `--quiet --verbose` - Quiet wins, verbose ignored
- `--json --quiet` - JSON wins, quiet ignored

### Enhanced Output Modes (NEW)

#### Quiet Mode
Perfect for CI/CD pipelines where you want a quick summary without verbose output:

```bash
python3 scripts/schema_validator.py rules/ --quiet
```

Output:
```bash
================================================================================
OVERALL SUMMARY
================================================================================
Total files: 91
Clean: 60
Warnings only: 31
Failed: 0

WARNING FILES (showing first 5):
  1. 001-memory-bank.md (1 MEDIUM)
  2. 002-rule-governance.md (1 MEDIUM)
  3. 002a-rule-creation-guide.md (1 MEDIUM)
  4. 002c-advanced-rule-patterns.md (1 MEDIUM)
  5. 002d-schema-validator-usage.md (1 MEDIUM)
  ... and 26 more

TIP: Run with filename to see details: python scripts/schema_validator.py <file>
================================================================================
```

#### JSON Output Mode
Enables programmatic parsing and CI/CD integration:

```bash
python3 scripts/schema_validator.py rules/ --json
```

Output:
```json
{
  "summary": {
    "total_files": 91,
    "clean": 60,
    "warnings_only": 31,
    "failed": 0
  },
  "failed_files": [],
  "warning_files": [
    {
      "path": "rules/001-memory-bank.md",
      "medium_count": 1,
      "errors": [
        {
          "severity": "MEDIUM",
          "group": "Anti-Patterns",
          "message": "Anti-Patterns and Common Mistakes section is strongly recommended but optional",
          "line": null,
          "fix": "Add '## Anti-Patterns and Common Mistakes' section"
        }
      ]
    }
  ]
}
```

#### Use Cases for New Modes

**Quiet Mode (`--quiet`):**
- Quick validation checks in terminals
- CI/CD status summaries
- Daily validation reports
- When you only need to know which files failed

**JSON Mode (`--json`):**
- Automated CI/CD pipelines
- Custom reporting tools
- Integration with issue trackers
- Metrics collection and dashboards
- Filtering and post-processing validation results

### Success Output

```bash
================================================================================
VALIDATION REPORT: rules/002-rule-governance.md
================================================================================

SUMMARY:
  [FAIL] CRITICAL: 0
  [WARN]  HIGH: 0
  [INFO]  MEDIUM: 2
  [PASS] Passed: 458 checks

[INFO]  MEDIUM ISSUES (2):
────────────────────────────────────────────────────────────────────────────────
[Anti-Patterns] Anti-Patterns section is strongly recommended but optional
[Links] Referenced rule file does not exist: rules/example.md

================================================================================
RESULT: [WARN]  WARNINGS ONLY
================================================================================
```

**Interpretation:** Rule passes validation (0 CRITICAL errors). MEDIUM warnings are optional improvements.

### Failure Output

```bash
================================================================================
VALIDATION REPORT: rules/bad-rule.md
================================================================================

SUMMARY:
  [FAIL] CRITICAL: 3
  [WARN]  HIGH: 2
  [INFO]  MEDIUM: 1
  [PASS] Passed: 420 checks

[FAIL] CRITICAL ISSUES (3):
────────────────────────────────────────────────────────────────────────────────
[Metadata] Missing required field: Keywords
  Fix: Add **Keywords:** [10-15 comma-separated terms]
[Metadata] Missing required field: TokenBudget
  Fix: Add **TokenBudget:** ~NUMBER (e.g., ~1200)
[Contract] Missing XML tag: <inputs_prereqs>
  Line: 45
  Fix: Add <inputs_prereqs> tag in Contract section

================================================================================
RESULT: [FAIL] FAILED
================================================================================
```

**Interpretation:** Rule fails validation (3 CRITICAL errors). Must fix all CRITICAL errors before committing.

### Parsing Validation Output

AI agents must parse validation output to extract error information programmatically.

#### Text Output Parsing

**Extract Summary Counts:**
```regex
Pattern: ^\s+\[FAIL\] CRITICAL: (\d+)$
Capture: Group 1 = CRITICAL count

Pattern: ^\s+\[WARN\]\s+HIGH: (\d+)$
Capture: Group 1 = HIGH count

Pattern: ^\s+\[INFO\]\s+MEDIUM: (\d+)$
Capture: Group 1 = MEDIUM count

Pattern: ^\s+\[PASS\] Passed: (\d+) checks$
Capture: Group 1 = Passed checks count
```

**Extract Result Status:**
```regex
Pattern: ^RESULT: .*?(PASS|WARN|FAIL).*?(.+)$
Capture: Group 1 = Status (PASS/WARN/FAIL)
         Group 2 = Result text (PASSED/WARNINGS ONLY/FAILED)
Note: Validator output may include icons/emojis in result line
Use flexible pattern to extract text regardless of decorations
```

**Extract Individual Errors:**
```regex
Pattern: ^\[(.+?)\] (.+)$
Capture: Group 1 = Error group (e.g., "Metadata", "Contract")
         Group 2 = Error message

Pattern: ^\s+Line: (\d+)$
Capture: Group 1 = Line number

Pattern: ^\s+Fix: (.+)$
Capture: Group 1 = Fix suggestion
```

**Extract Directory Summary (--quiet or default):**
```regex
Pattern: ^Total files: (\d+)$
Note: Validator output may include icons/emojis before labels (e.g., "Clean:", "Warnings only:", "Failed:")
Use case-insensitive matching and allow for optional leading characters
```

**Python Parsing Example:**
```python
import re
import subprocess

# Run validator
result = subprocess.run(
    ['python3', 'scripts/schema_validator.py', 'rules/002-rule-governance.md'],
    capture_output=True,
    text=True
)

# Parse counts
critical_match = re.search(r'\[FAIL\] CRITICAL: (\d+)', result.stdout)
high_match = re.search(r'\[WARN\]\s+HIGH: (\d+)', result.stdout)
medium_match = re.search(r'\[INFO\]\s+MEDIUM: (\d+)', result.stdout)

critical_count = int(critical_match.group(1)) if critical_match else 0
high_count = int(high_match.group(1)) if high_match else 0
medium_count = int(medium_match.group(1)) if medium_match else 0

# Parse result status
result_match = re.search(r'RESULT: \[(PASS|WARN|FAIL)\] (.+)', result.stdout)
status = result_match.group(1) if result_match else "UNKNOWN"

# Determine action
if critical_count > 0 or high_count > 0:
    print(f"[FAIL] Validation failed: {critical_count} CRITICAL, {high_count} HIGH")
    # Extract and process errors
elif medium_count > 0:
    print(f"[WARN] Validation passed with warnings: {medium_count} MEDIUM")
else:
    print("[PASS] Validation passed")
```

#### JSON Output Parsing

**When --json flag is used, output is structured JSON (preferred for AI agents):**

```python
import json
import subprocess

# Run validator with --json
result = subprocess.run(
    ['python3', 'scripts/schema_validator.py', 'rules/', '--json'],
    capture_output=True,
    text=True
)

# Parse JSON
data = json.loads(result.stdout)

# Access summary
total_files = data['summary']['total_files']
clean = data['summary']['clean']
warnings_only = data['summary']['warnings_only']
failed = data['summary']['failed']

# Process failed files
for file_info in data['failed_files']:
    file_path = file_info['path']
    critical_count = file_info['critical_count']
    high_count = file_info['high_count']

    print(f"[FAIL] {file_path}: {critical_count} CRITICAL, {high_count} HIGH")

    # Process each error
    for error in file_info['errors']:
        severity = error['severity']
        group = error['group']
        message = error['message']
        line = error['line']  # May be None
        fix = error['fix']

        print(f"  [{severity}] {group}: {message}")
        if line:
            print(f"    Line: {line}")
        print(f"    Fix: {fix}")

# Process warning files
for file_info in data['warning_files']:
    file_path = file_info['path']
    medium_count = file_info['medium_count']
    print(f"[WARN] {file_path}: {medium_count} MEDIUM")

# Determine overall status
if failed > 0:
    print(f"[FAIL] Validation failed: {failed}/{total_files} files have CRITICAL/HIGH errors")
    exit(1)
elif warnings_only > 0:
    print(f"[WARN] Validation passed with warnings: {warnings_only}/{total_files} files have MEDIUM errors")
    exit(0)
else:
    print(f"[PASS] All {total_files} files passed validation")
    exit(0)
```

**JSON Structure Reference:**
```json
{
  "summary": {
    "total_files": int,
    "clean": int,
    "warnings_only": int,
    "failed": int
  },
  "failed_files": [
    {
      "path": str,
      "critical_count": int,
      "high_count": int,
      "medium_count": int,
      "errors": [
        {
          "severity": "CRITICAL" | "HIGH" | "MEDIUM",
          "group": str,
          "message": str,
          "line": int | null,
          "fix": str
        }
      ]
    }
  ],
  "warning_files": [
    {
      "path": str,
      "medium_count": int,
      "errors": [
        {
          "severity": "MEDIUM",
          "group": str,
          "message": str,
          "line": int | null,
          "fix": str
        }
      ]
    }
  ]
}
```

## Error Severity Levels

**Severity Definitions:**
- **CRITICAL [FAIL]:** Blocks validation - MUST fix before commit
- **HIGH [WARN]:** Important issue - Strongly recommended to fix
- **MEDIUM [INFO]:** Optional improvement - Review and consider fixing
- **INFO [PASS]:** Informational - No action needed

## Common Errors and Fixes

### Error 1: Missing Keywords Field

**Error Message:**
```
[Metadata] Missing required field: Keywords
```

**Fix:**
```markdown
# Add Keywords metadata field at top of file
**Keywords:** keyword1, keyword2, keyword3, keyword4, keyword5, keyword6, keyword7, keyword8, keyword9, keyword10
```

**Validation:** Keywords field must have 10-15 comma-separated terms

### Error 2: Keywords Count Wrong

**Error Message:**
```
[Metadata] Keywords count: 8 (expected 10-15)
```

**Fix:** Add more keywords to reach 10-15 count
```markdown
# Before (8 keywords - WRONG)
**Keywords:** SQL, Snowflake, CTE, query, optimization, performance, tuning, warehouse

# After (12 keywords - CORRECT)
**Keywords:** SQL, Snowflake, CTE, query optimization, performance, tuning, warehouse sizing, clustering, partitioning, EXPLAIN, query plan, cost analysis
```

### Error 3: Missing RuleVersion Field

**Error Message:**
```
[Metadata] RuleVersion must be semantic version format (e.g., v1.0.0)
```

**Fix:** Add RuleVersion metadata field before Keywords
```markdown
## Metadata

**RuleVersion:** v1.0.0
**Keywords:** keyword1, keyword2, ...
```

**Validation:** RuleVersion must be semantic versioning format (vX.Y.Z)

### Error 4: Invalid RuleVersion Format

**Error Message:**
```
[Metadata] RuleVersion must be semantic version format (e.g., v1.0.0)
```

**Fix:** Use correct semantic version format
```markdown
# Wrong formats
**RuleVersion:** 1.0.0          # Missing v prefix
**RuleVersion:** v1             # Missing minor and patch
**RuleVersion:** v1.0           # Missing patch version
**RuleVersion:** version1.0.0   # Wrong prefix

# Correct format
**RuleVersion:** v1.0.0
**RuleVersion:** v2.1.3
```

### Error 5: TokenBudget Format Wrong

**Error Message:**
```
[Metadata] TokenBudget format invalid: expected ~NUMBER format
```

**Fix:** Add tilde prefix and use numeric value
```markdown
# Wrong formats
**TokenBudget:** 1200         # Missing tilde
**TokenBudget:** small        # Text label forbidden
**TokenBudget:** ~medium      # Text label forbidden

# Correct format
**TokenBudget:** ~1200
```

### Error 6: Missing Required Section

**Error Message:**
```
[Structure] Missing required section: Quick Start TL;DR
```

**Fix:** Add missing section in correct order
```markdown
## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- Pattern 1
- Pattern 2
- Pattern 3

**Pre-Execution Checklist:**
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3
```

### Error 7: Contract Missing XML Tag

**Error Message:**
```
[Contract] Missing XML tag: <mandatory>
  Line: 45
```

**Fix:** Add missing XML tag to Contract section
```markdown
## Contract

<inputs_prereqs>
Prerequisites here
</inputs_prereqs>

<mandatory>
Required tools and permissions
</mandatory>

<forbidden>
Prohibited actions
</forbidden>

<steps>
1. Step 1
2. Step 2
</steps>

<output_format>
Expected output
</output_format>

<validation>
Success criteria
</validation>
```

### Error 8: Section Order Wrong

**Error Message:**
```
[Structure] Sections out of order: Contract should come before Key Principles
```

**Fix:** Reorder sections per schema
```markdown
# Correct order:
1. Purpose
2. Rule Scope
3. Quick Start TL;DR
4. Contract
5. Key Principles (optional)
6. [Main content sections]
7. Anti-Patterns (optional)
8. Post-Execution Checklist
9. Validation
10. Output Format Examples
11. References
```

## Automated Validation + Fix Workflow

AI agents should follow this iterative workflow for automated rule validation and error correction.

### Workflow Steps

**Step 1: Initial Validation**
```bash
python3 scripts/schema_validator.py [file]
EXIT_CODE=$?
OUTPUT=$(python3 scripts/schema_validator.py [file] 2>&1)
```

**Step 2: Check Exit Code**
- If `EXIT_CODE == 0`: Validation passed, workflow complete
- If `EXIT_CODE == 1`: Validation failed, proceed to Step 3

**Step 3: Parse Errors (Use --json for easier parsing)**
```bash
python3 scripts/schema_validator.py [file] --json > validation_result.json
```

**Step 4: Categorize Errors by Severity**
- **CRITICAL errors**: Must fix (validation will not pass without fixing)
- **HIGH errors**: Should fix (strongly recommended)
- **MEDIUM errors**: Optional (skip unless --strict mode)

**Step 5: Map Errors to Fix Patterns**

Use "Common Errors and Fixes" section to identify fix patterns:

**Fix Complexity by Error Type:**
- **Missing Keywords (Error 1):** Easy - Add field
- **Keywords Count Wrong (Error 2):** Easy - Add keywords
- **TokenBudget Format (Error 3):** Easy - Fix format
- **Missing Section (Error 4):** Medium - Add section with structure
- **Missing XML Tag (Error 5):** Easy - Add tag
- **Section Order Wrong (Error 6):** Hard - Requires reordering

**Step 6: Apply Fixes**

**For EASY fixes (automated):**
```python
# Example: Fix Keywords count
def fix_keywords_count(file_path, current_keywords, target_count=12):
    # Read file
    with open(file_path, 'r') as f:
        content = f.read()

    # Parse current keywords
    keywords = [k.strip() for k in current_keywords.split(',')]

    # Add generic keywords to reach target
    generic_keywords = ['validation', 'best practices', 'guidelines',
                       'requirements', 'standards', 'compliance']
    while len(keywords) < target_count:
        keywords.append(generic_keywords[len(keywords) % len(generic_keywords)])

    # Replace in content
    new_keywords = ', '.join(keywords)
    content = re.sub(r'\*\*Keywords:\*\* .+', f'**Keywords:** {new_keywords}', content)

    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
```

**For MEDIUM fixes (semi-automated):**
```python
# Example: Add missing section with boilerplate
def add_missing_section(file_path, section_name):
    section_templates = {
        'Quick Start TL;DR': '''## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- Pattern 1
- Pattern 2
- Pattern 3

**Pre-Execution Checklist:**
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3
''',
        'Anti-Patterns and Common Mistakes': '''## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: [Description]

**Problem:**
[What goes wrong]

**Wrong Pattern:**
```
[Code example]
```

**Correct Pattern:**
```
[Code example]
```
'''
    }

    template = section_templates.get(section_name, f'## {section_name}\n\n[Content needed]\n')

    # Read file and insert at appropriate location
    # (Implementation depends on section order logic)
```

**For HARD fixes (require user intervention):**
- Log error with detailed context
- Request user manual fix
- Do not attempt automated fix (high risk of breaking content)

**Step 7: Re-validate**
```bash
python3 scripts/schema_validator.py [file]
EXIT_CODE=$?
```

**Step 8: Iteration Control**
- Max iterations: 3
- If still failing after 3 iterations: Report unresolved errors to user
- Track which errors were fixed vs remain

**Step 9: Report Results**

**Success:**
```
[PASS] Validation passed after [N] iterations
Fixed errors:
  - [List of fixed errors]
```

**Partial Success:**
```
[WARN] Validation passed with warnings
Fixed errors:
  - [List of fixed errors]
Remaining warnings:
  - [List of MEDIUM errors]
```

**Failure:**
```
[FAIL] Validation failed after 3 iterations
Unresolved errors:
  - [List of CRITICAL/HIGH errors]
Manual intervention required.
```

### Example Complete Workflow Script

```python
#!/usr/bin/env python3
"""Automated validation + fix workflow for AI agents."""

import json
import subprocess
import sys

def validate_file(file_path, use_json=True):
    """Run validator and return parsed results."""
    cmd = ['python3', 'scripts/schema_validator.py', file_path]
    if use_json:
        cmd.append('--json')

    result = subprocess.run(cmd, capture_output=True, text=True)

    if use_json:
        data = json.loads(result.stdout)
        return result.returncode, data
    else:
        return result.returncode, result.stdout

def fix_errors(file_path, errors):
    """Apply automated fixes for known error patterns."""
    fixed_errors = []

    for error in errors:
        if error['group'] == 'Metadata' and 'Keywords count' in error['message']:
            # Fix keywords count
            fix_keywords_count(file_path)
            fixed_errors.append(error)
        elif error['group'] == 'Metadata' and 'TokenBudget format' in error['message']:
            # Fix token budget format
            fix_token_budget_format(file_path)
            fixed_errors.append(error)
        # Add more fix patterns as needed

    return fixed_errors

def main(file_path):
    """Main workflow."""
    max_iterations = 3

    for iteration in range(1, max_iterations + 1):
        print(f"\n[INFO] Iteration {iteration}/{max_iterations}")

        # Validate
        exit_code, data = validate_file(file_path)

        if exit_code == 0:
            print(f"[PASS] Validation passed after {iteration} iteration(s)")
            return 0

        # Extract errors (assuming single file)
        if data['summary']['failed'] > 0:
            errors = data['failed_files'][0]['errors']
        else:
            errors = data['warning_files'][0]['errors'] if data['warning_files'] else []

        # Categorize errors
        critical_errors = [e for e in errors if e['severity'] == 'CRITICAL']
        high_errors = [e for e in errors if e['severity'] == 'HIGH']

        if not critical_errors and not high_errors:
            print("[WARN] Validation passed with warnings only")
            return 0

        # Apply fixes
        fixed = fix_errors(file_path, critical_errors + high_errors)

        if not fixed:
            print("[FAIL] No automated fixes available for remaining errors")
            print("Manual intervention required.")
            return 1

        print(f"[INFO] Fixed {len(fixed)} error(s):")
        for error in fixed:
            print(f"  - [{error['severity']}] {error['group']}: {error['message']}")

    print(f"[FAIL] Validation still failing after {max_iterations} iterations")
    return 1

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: validate_and_fix.py [file_path]")
        sys.exit(1)

    sys.exit(main(sys.argv[1]))
```

## CI/CD Integration

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate all rule files before commit
python3 scripts/schema_validator.py rules/

if [ $? -ne 0 ]; then
    echo "[FAIL] Validation failed. Fix errors before committing."
    exit 1
fi

echo "[PASS] All rules validated successfully."
exit 0
```

### GitHub Actions Workflow

```yaml
name: Validate Rules

on:
  pull_request:
    paths:
      - 'rules/**/*.md'
  push:
    paths:
      - 'rules/**/*.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install PyYAML
      - name: Validate rules
        run: python3 scripts/schema_validator.py rules/
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Ignoring MEDIUM Warnings Until They Accumulate

**Problem:** Treating MEDIUM severity warnings as "optional" and never addressing them, leading to gradual quality degradation across the rule set.

**Why It Fails:** MEDIUM warnings often indicate missing best practices (like Anti-Patterns sections). Accumulated warnings create technical debt, make validation output noisy, and hide new issues in the noise.

**Correct Pattern:**
```bash
# BAD: Only fix CRITICAL, ignore everything else
$ python3 scripts/schema_validator.py rules/
# "32 MEDIUM warnings? That's fine, no CRITICAL errors"

# GOOD: Track and address warnings systematically
$ python3 scripts/schema_validator.py rules/ --json | jq '.summary'
# Schedule warning cleanup sprints
# Target: 0 CRITICAL, 0 HIGH, <10 MEDIUM across all rules
```

### Anti-Pattern 2: Bypassing Validation in CI/CD

**Problem:** Adding `|| true` or `continue-on-error: true` to CI/CD validation steps to prevent pipeline failures, rather than fixing the underlying issues.

**Why It Fails:** Defeats the purpose of automated validation. Invalid rules merge to main, breaking rule discovery and agent effectiveness. Creates false confidence in rule quality.

**Correct Pattern:**
```yaml
# BAD: Bypassing validation
- name: Validate rules
  run: python3 scripts/schema_validator.py rules/ || true
  continue-on-error: true

# GOOD: Fail fast, fix forward
- name: Validate rules
  run: python3 scripts/schema_validator.py rules/
  # No error suppression - pipeline fails on CRITICAL/HIGH errors
  # Fix rules before merging, not after
```

## Post-Execution Checklist

- [ ] schema_validator.py runs without Python errors
- [ ] Validation report generated successfully
- [ ] All CRITICAL errors fixed (0 CRITICAL required)
- [ ] HIGH errors reviewed and fixed (strongly recommended)
- [ ] MEDIUM errors considered (optional)
- [ ] Rule re-validated after fixes
- [ ] CI/CD integration configured (if applicable)

## Validation

**Success Checks:**
- Command `python3 scripts/schema_validator.py rules/NNN-rule.md` runs without errors
- Validation report shows [PASS] RESULT: PASSED or [WARN] WARNINGS ONLY
- CRITICAL error count is 0
- Error messages include line numbers and fix suggestions
- Re-validation after fixes shows improvement

**Negative Tests:**
- Missing metadata field triggers CRITICAL error
- Wrong Keywords count triggers HIGH error
- Missing Contract XML tag triggers CRITICAL error
- Section order violation triggers HIGH warning
- Referenced non-existent files trigger MEDIUM warnings

## Output Format Examples

### Example 1: Validating New Rule

```bash
# Create new rule file
vim rules/101d-snowflake-streamlit-testing.md

# Add metadata and all required sections
# Fill in Keywords, TokenBudget, ContextTier, Depends

# Validate
python3 scripts/schema_validator.py rules/101d-snowflake-streamlit-testing.md

# Output (first attempt - errors):
================================================================================
VALIDATION REPORT: rules/101d-snowflake-streamlit-testing.md
================================================================================
SUMMARY:
  [FAIL] CRITICAL: 1
  [PASS] Passed: 445 checks

[FAIL] CRITICAL ISSUES (1):
────────────────────────────────────────────────────────────────────────────────
[Metadata] Keywords count: 8 (expected 10-15)

# Fix: Add 2-7 more keywords
vim rules/101d-snowflake-streamlit-testing.md

# Re-validate
python3 scripts/schema_validator.py rules/101d-snowflake-streamlit-testing.md

# Output (after fix - success):
================================================================================
RESULT: [PASS] PASSED
================================================================================
```

### Example 2: Batch Validation

```bash
# Validate all rules
python3 scripts/schema_validator.py rules/ | grep "CRITICAL:"

# Output showing rules with errors:
# rules/bad-rule-1.md: CRITICAL: 2
# rules/bad-rule-2.md: CRITICAL: 1
# [... all others passed ...]

# Fix identified rules
vim rules/bad-rule-1.md
vim rules/bad-rule-2.md

# Re-validate directory
python3 scripts/schema_validator.py rules/
```

## ContextTier Validation

The schema validator checks that ContextTier is one of: Critical, High, Medium, Low.
All four values remain valid - ContextTier is a secondary signal for fine-grained
prioritization within natural language tiers (CRITICAL/CORE/FOUNDATION markers).

The validator does NOT enforce relationships between markers and ContextTier values.

## References

### Related Rules
- **Rule Governance**: `002-rule-governance.md` - Schema requirements and validation criteria
- **Creation Guide**: `002a-rule-creation-guide.md` - Step 6 covers validation workflow
- **Global Core**: `000-global-core.md` - Foundation patterns

### Tools
- **schema_validator.py**: `scripts/schema_validator.py` - Validation script
- **token_validator.py**: `scripts/token_validator.py` - Token budget validation

### Schema Definition
- **v3.0 Schema**: `schemas/rule-schema.yml` - Authoritative validation rules
