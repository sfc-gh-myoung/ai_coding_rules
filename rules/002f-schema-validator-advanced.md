# Schema Validator Advanced: Automation and CI/CD Integration

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule covers advanced automation patterns for schema validation.
> Load when setting up CI/CD pipelines or programmatic validation workflows.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.2.0
**LastUpdated:** 2026-03-09
**Keywords:** schema validator, CI/CD integration, automation workflow, JSON parsing, programmatic validation, pre-commit hooks, GitHub Actions, batch validation, error automation, validation scripts
**TokenBudget:** ~3350
**ContextTier:** Medium
**Depends:** 002e-schema-validator-usage.md, 002-rule-governance.md, 000-global-core.md

## Scope

**What This Rule Covers:**
Advanced automation patterns for schema validation including programmatic output parsing, CI/CD integration, automated fix workflows, and batch validation strategies.

**When to Load This Rule:**
- Setting up CI/CD validation pipelines
- Parsing validation output programmatically
- Automating rule fixes in scripts
- Integrating validation with issue trackers or dashboards
- Building custom validation workflows

## References

### Dependencies

**Must Load First:**
- **002e-schema-validator-usage.md** - Core validation commands and error resolution
- **002-rule-governance.md** - Schema requirements and v3.2 standards
- **000-global-core.md** - Foundation for all rules

### External Documentation

- **Schema Definition:** `schemas/rule-schema.yml` - Authoritative v3.2 schema
- **Validator CLI:** `uv run ai-rules validate` - Validation command

## Contract

### Inputs and Prerequisites

- Familiarity with 002e-schema-validator-usage.md (core commands)
- Python 3.8+ environment with PyYAML
- CI/CD platform access (GitHub Actions, GitLab CI, etc.)
- Shell scripting basics

### Mandatory

- `ai-rules validate` CLI command
- `schemas/rule-schema.yml`
- Python 3 with PyYAML
- CI/CD configuration files

### Forbidden

- Bypassing validation in CI/CD with `|| true` or `continue-on-error`
- Modifying validator to pass invalid rules
- Ignoring CRITICAL errors in automation

### Execution Steps

1. Choose integration pattern (pre-commit, CI/CD, custom script)
2. Configure validation command with appropriate flags (--json for parsing)
3. Implement error handling and reporting
4. Set up iteration limits for automated fixes
5. Configure notifications for failures
6. Test pipeline with intentionally broken rules

### Output Format

- JSON validation results for programmatic parsing
- Exit codes for CI/CD pass/fail determination
- Structured error reports for dashboards

### Validation

**Pre-Task-Completion Checks:**
- CI/CD pipeline configured with validation step
- Exit code handling implemented correctly
- JSON parsing tested with sample output
- Automated fixes limited to safe patterns

**Success Criteria:**
- Pipeline fails on CRITICAL/HIGH errors (exit code 1)
- Pipeline passes on clean or warnings-only (exit code 0)
- JSON output parses correctly
- Automated fixes apply without breaking content

### Post-Execution Checklist

- [ ] CI/CD validation step configured without error suppression
- [ ] Exit code handling implemented (0 = pass, 1 = fail)
- [ ] JSON parsing tested and working
- [ ] Automated fix workflow limited to 3 iterations
- [ ] Failure notifications configured
- [ ] Pipeline tested with intentionally broken rules

## Parsing Validation Output

### JSON Output Parsing (Preferred)

Verify `--json` support: `uv run ai-rules validate --help | grep json`. If unsupported, use text parsing fallback below.

Use `--json` flag for structured output that's easy to parse:

```python
import json
import subprocess

result = subprocess.run(
    ['uv', 'run', 'ai-rules', 'validate', 'rules/', '--json'],
    capture_output=True,
    text=True
)

data = json.loads(result.stdout)

# Access summary
total_files = data['summary']['total_files']
failed = data['summary']['failed']

# Process failed files
for file_info in data['failed_files']:
    file_path = file_info['path']
    for error in file_info['errors']:
        print(f"[{error['severity']}] {file_path}: {error['message']}")
        if error['line']:
            print(f"  Line: {error['line']}")
        print(f"  Fix: {error['fix']}")
```

### JSON Structure Reference

**Verify this structure matches your validator version:**
```bash
uv run ai-rules validate rules/ --json | python3 -c \
  "import json,sys; print(json.dumps(json.load(sys.stdin), indent=2))" | head -20
```

The `--json` flag outputs results in the following structure:

```json
{
  "summary": {
    "total_files": 91,
    "clean": 60,
    "warnings_only": 31,
    "failed": 0
  },
  "failed_files": [
    {
      "path": "rules/<example-rule>.md",
      "critical_count": 2,
      "high_count": 1,
      "medium_count": 0,
      "errors": [
        {
          "severity": "CRITICAL",
          "group": "Metadata",
          "message": "Missing required field: Keywords",
          "line": null,
          "fix": "Add **Keywords:** [5-20 comma-separated terms]"
        }
      ]
    }
  ],
  "warning_files": [
    {
      "path": "rules/001-memory-bank.md",
      "medium_count": 1,
      "errors": [...]
    }
  ]
}
```

### Text Output Parsing (Fallback)

When JSON is unavailable, use regex patterns:

```python
import re

# Strip ANSI escape codes first
clean = re.sub(r'\x1b\[[0-9;]*m', '', output)

# Extract counts from summary table (format: "│ CRITICAL │   3 │")
critical_match = re.search(r'CRITICAL\s*│\s*(\d+)', clean)
high_match = re.search(r'HIGH\s*│\s*(\d+)', clean)
critical_count = int(critical_match.group(1)) if critical_match else 0
high_count = int(high_match.group(1)) if high_match else 0

# Extract result status
if 'All validations passed' in clean:
    status = "PASS"
elif 'RESULT: FAILED' in clean:
    status = "FAIL"
else:
    status = "UNKNOWN"
```

### Error Recovery for Malformed JSON

When the validator produces malformed JSON (truncated output, mixed stderr/stdout, or encoding issues), handle it gracefully before falling back to text parsing:

```python
import json
import subprocess

result = subprocess.run(
    ['uv', 'run', 'ai-rules', 'validate', 'rules/', '--json'],
    capture_output=True,
    text=True
)

try:
    data = json.loads(result.stdout)
except (json.JSONDecodeError, ValueError) as e:
    # Log the parse failure for debugging
    print(f"[WARN] JSON parse failed: {e}")
    # Check if stderr was mixed into stdout
    if result.stderr:
        print(f"[WARN] Stderr present: {result.stderr[:200]}")
    # Fall back to text output parsing
    data = None

if data is None:
    # Re-run without --json and parse text output instead
    result = subprocess.run(
        ['uv', 'run', 'ai-rules', 'validate', 'rules/'],
        capture_output=True,
        text=True
    )
    # Use regex-based text parsing (see Text Output Parsing above)
```

## Automated Validation + Fix Workflow

### Workflow Steps

1. **Initial Validation:** Run validator with --json flag
2. **Check Exit Code:** 0 = pass, 1 = fail
3. **Parse Errors:** Extract from JSON output
4. **Categorize:** CRITICAL (must fix), HIGH (should fix), MEDIUM (optional)
5. **Apply Safe Fixes:** Only for well-defined patterns
6. **Re-validate:** Check if fixes resolved errors
7. **Iterate:** Max 3 attempts, then report to user

### Fix Complexity by Error Type

- **Easy (automate):** Missing Keywords, TokenBudget format, Keywords count
- **Medium (semi-automate):** Missing section with boilerplate
- **Hard (manual only):** Section reordering, content restructuring

### Example Workflow Script

```python
#!/usr/bin/env python3
"""Automated validation + fix workflow."""

import json
import subprocess
import sys

def validate_file(file_path):
    """Run validator and return parsed results."""
    result = subprocess.run(
        ['uv', 'run', 'ai-rules', 'validate', file_path, '--json'],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    return result.returncode, data

def fix_keywords_count(file_path, target=12):
    """Add content-derived keywords to reach target count."""
    import os
    import shutil
    backup_path = file_path + '.bak'
    shutil.copy(file_path, backup_path)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        import re
        match = re.search(r'\*\*Keywords:\*\* (.+)', content)
        if match:
            keywords = [k.strip() for k in match.group(1).split(',')]
            # Extract additional keywords from rule's section headings and key terms
            additional = extract_keywords_from_headings(content)
            keywords.extend(additional[:target - len(keywords)])
            # Example: A rule about SQL stored procedures would get
            # keywords like "procedure", "stored-procedure", "sql-body"
            new_line = f'**Keywords:** {", ".join(keywords)}'
            content = re.sub(r'\*\*Keywords:\*\* .+', new_line, content)
            with open(file_path, 'w') as f:
                f.write(content)
            return True
        return False
    finally:
        if os.path.exists(backup_path):
            os.remove(backup_path)

def main(file_path):
    """Main workflow with iteration limit."""
    max_iterations = 3
    
    for i in range(1, max_iterations + 1):
        exit_code, data = validate_file(file_path)
        
        if exit_code == 0:
            print(f"[PASS] Validation passed after {i} iteration(s)")
            return 0
        
        errors = data.get('failed_files', [{}])[0].get('errors', [])
        critical = [e for e in errors if e['severity'] == 'CRITICAL']
        
        if not critical:
            print("[WARN] Passed with warnings")
            return 0
        
        # Apply fixes for known patterns
        fixed = False
        for error in critical:
            if 'Keywords count' in error['message']:
                fixed = fix_keywords_count(file_path)
        
        if not fixed:
            print("[FAIL] No automated fix available")
            return 1
    
    print(f"[FAIL] Still failing after {max_iterations} iterations")
    return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
```

## CI/CD Integration

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

uv run ai-rules validate rules/

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
      # Update to latest stable versions at integration time
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install uv && uv sync
      - name: Validate rules
        run: uv run ai-rules validate rules/
```

### GitLab CI Configuration

```yaml
validate-rules:
  stage: test
  image: python:3.10
  script:
    - pip install uv && uv sync
    - uv run ai-rules validate rules/
  rules:
    - changes:
        - rules/**/*.md
```

### CI/CD Environment Troubleshooting

Common issues when running validation in CI/CD runners:

- **Python not found:** Ensure Python step runs before validation, or use a Python-based Docker image
- **`uv` not installed:** Add `pip install uv` before `uv sync`, or use `pipx install uv` for isolation
- **Schema file missing:** Ensure `schemas/rule-schema.yml` is included in the checkout (not excluded by sparse checkout or `.gitattributes`)
- **Wrong working directory:** Validate that `rules/` path is relative to the repository root, not a subdirectory
- **Permission denied:** CI runners may need explicit read access to rule files; check file permissions in the Docker image
- **Empty directory:** If `ai-rules validate rules/` finds no `.md` files, it returns
  exit code 0 with a summary showing `total_files: 0`. This is not an error — the
  directory simply has no rules to validate. To verify the directory path is correct,
  use `ls rules/*.md` first.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Bypassing Validation in CI/CD

**Problem:** Adding `|| true` or `continue-on-error: true` to prevent pipeline failures.

**Why It Fails:** Invalid rules merge to main, breaking rule discovery and agent effectiveness.

**Correct Pattern:**
```yaml
# BAD
- name: Validate rules
  run: uv run ai-rules validate rules/ || true

# GOOD
- name: Validate rules
  run: uv run ai-rules validate rules/
  # No error suppression - fix rules before merging
```

### Anti-Pattern 2: Unlimited Fix Iterations

**Problem:** Running automated fixes in infinite loop until passing.

**Why It Fails:** Can corrupt content, infinite loops on unfixable errors, masks real issues.

**Correct Pattern:**
```python
# BAD
while exit_code != 0:
    apply_fixes()
    exit_code = validate()

# GOOD
for i in range(3):  # Max 3 iterations
    if validate() == 0:
        break
    apply_safe_fixes()
else:
    report_to_user()  # Escalate after max attempts
```

### Anti-Pattern 3: Ignoring MEDIUM Warnings

See **002e-schema-validator-usage.md, Anti-Pattern 1** for detailed guidance on addressing MEDIUM warnings. In CI/CD contexts, track warning counts over time and schedule periodic cleanup to keep total MEDIUM warnings below 10 across all rules.

## Key Principles

- **Fail Fast:** CI/CD should fail on CRITICAL/HIGH errors, not suppress them
- **Iteration Limits:** Max 3 automated fix attempts before escalating
- **Safe Fixes Only:** Only automate well-defined patterns (keywords, format)
- **JSON Preferred:** Use --json for reliable programmatic parsing
- **Track Warnings:** MEDIUM warnings accumulate; address them periodically
