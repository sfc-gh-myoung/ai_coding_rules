# Rule Creator Tests

This folder contains test cases for validating the rule-creator skill functionality.

## Test Categories

| Category | Purpose | Files |
|----------|---------|-------|
| Input Validation | Verify input parsing and validation | `test-inputs.md` |
| Workflow Execution | Verify each phase executes correctly | `test-workflows.md` |
| Edge Cases | Verify edge case handling | `test-edge-cases.md` |

## Running Tests

### Manual Test Execution

Each test file contains scenarios that can be executed manually:

1. Read the test scenario
2. Execute the skill with provided inputs
3. Compare actual output to expected output
4. Record pass/fail status

### Automated Validation

For structural validation, use:

```bash
# Validate a created rule passes schema
python scripts/schema_validator.py rules/<created-rule>.md

# Expected: exit code 0
```

## Test Scenarios

### Quick Smoke Test

```
Input:
  technology: pytest-example
  aspect: core
  
Expected:
  1. Discovery finds Python domain (200-299)
  2. Template generates successfully
  3. Validation passes (exit code 0)
  4. RULES_INDEX.md updated
```

### Full Regression Suite

See individual test files for complete scenarios.

