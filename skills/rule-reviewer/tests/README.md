# Rule Reviewer Tests

This folder contains test cases for validating the rule-reviewer skill functionality.

## Test Categories

| Category | Purpose | Files |
|----------|---------|-------|
| Input Validation | Verify input parsing and validation | `test-inputs.md` |
| Review Modes | Verify FULL/FOCUSED/STALENESS modes | `test-modes.md` |
| Output Handling | Verify file writing and no-overwrite | `test-outputs.md` |

## Running Tests

### Manual Test Execution

Each test file contains scenarios that can be executed manually:

1. Read the test scenario
2. Execute the skill with provided inputs
3. Compare actual output to expected output
4. Record pass/fail status

### Automated Validation

For output validation:

```bash
# Check review file was created
ls reviews/<expected-filename>.md

# Verify no-overwrite worked
ls reviews/<base>*.md | wc -l
# Should show correct suffix count
```

## Test Scenarios

### Quick Smoke Test

```
Input:
  target_file: rules/200-python-core.md
  review_date: 2025-12-15
  review_mode: FULL
  model: claude-sonnet-45
  
Expected:
  1. Input validation passes
  2. Review executes successfully
  3. File written to reviews/
  4. Confirmation message shown
```

### Full Regression Suite

See individual test files for complete scenarios.

## Integration with rule-creator

The rule-reviewer skill can validate output from rule-creator:

```
1. Create rule using rule-creator skill
2. Run FULL review on created rule
3. Verify score ≥ 7.5/10
4. Check for no CRITICAL issues
```

This provides end-to-end quality assurance.

