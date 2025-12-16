# Tests: Documentation Reviewer Skill

This directory contains test cases for validating the doc-reviewer skill functionality.

## Test Organization

| File | Purpose | Test Count |
|------|---------|------------|
| `test-inputs.md` | Input validation test cases | 12 |
| `test-modes.md` | Review mode test cases | 9 |
| `test-outputs.md` | Output handling test cases | 10 |

## Running Tests

Tests are manual verification scenarios. To run:

1. **Load the skill:**

   ```text
   Open: skills/doc-reviewer/SKILL.md
   ```

2. **Execute test case:**

   ```text
   Use the doc-reviewer skill.
   
   [paste test inputs from test file]
   ```

3. **Verify expected behavior** matches documented expectations

## Test Categories

### Input Validation Tests (`test-inputs.md`)

Tests for:

- Valid/invalid date formats
- Valid/invalid review modes
- Valid/invalid review scopes
- Target file existence
- Default file discovery
- Focus area validation

### Mode Tests (`test-modes.md`)

Tests for:

- FULL mode behavior
- FOCUSED mode with each focus area
- STALENESS mode behavior
- Single vs collection scope
- Mode-specific output structure

### Output Tests (`test-outputs.md`)

Tests for:

- File naming conventions
- No-overwrite behavior
- Fallback output on write failure
- Verification table generation
- Score calculation

## Test Coverage Matrix

| Feature | Input Tests | Mode Tests | Output Tests |
|---------|-------------|------------|--------------|
| Date validation | ✅ | — | — |
| Mode validation | ✅ | ✅ | — |
| Scope validation | ✅ | ✅ | — |
| Target file discovery | ✅ | — | — |
| Focus area validation | ✅ | ✅ | — |
| FULL mode | — | ✅ | ✅ |
| FOCUSED mode | — | ✅ | ✅ |
| STALENESS mode | — | ✅ | ✅ |
| Single scope | — | ✅ | ✅ |
| Collection scope | — | ✅ | ✅ |
| Cross-reference table | — | ✅ | ✅ |
| Link validation table | — | ✅ | ✅ |
| Baseline compliance | — | ✅ | ✅ |
| No-overwrite safety | — | — | ✅ |
| Fallback output | — | — | ✅ |

## Expected Test Results

All tests should:

1. **Pass validation** - No unexpected errors
2. **Match expected behavior** - Output matches documented expectations
3. **Handle edge cases** - Graceful handling of unusual inputs

## Regression Testing

Run these tests after any skill modifications:

1. All input validation tests
2. At least one test from each mode
3. No-overwrite safety test
4. Fallback output test

## Adding New Tests

When adding tests:

1. Choose appropriate test file based on category
2. Follow existing test format
3. Include:
   - Test ID
   - Inputs
   - Expected behavior
   - Verification steps
4. Update test count in this README

