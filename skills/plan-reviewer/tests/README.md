# Plan Reviewer Tests

## Overview

This directory contains test cases for validating the plan-reviewer skill.

## Test Files

| File | Purpose |
|------|---------|
| `test-inputs.md` | Input validation test cases |
| `test-modes.md` | Review mode execution test cases |
| `test-outputs.md` | Output handling and file writing test cases |

## Running Tests

### Manual Testing

1. Load the plan-reviewer skill
2. Execute each test case in the test files
3. Verify output matches expected results

### Test Input Files

Test plans are located in:
- `tests/fixtures/` (if created)
- Or use actual plans in `plans/` directory

## Test Categories

### 1. Input Validation Tests (`test-inputs.md`)

Tests for:
- Valid/invalid review modes
- Date format validation
- File existence checks
- File extension validation
- Mode-specific requirements

### 2. Mode Execution Tests (`test-modes.md`)

Tests for:
- FULL mode scoring accuracy
- COMPARISON mode ranking
- META-REVIEW mode variance analysis
- Verification table generation
- Verdict assignment

### 3. Output Handling Tests (`test-outputs.md`)

Tests for:
- Output path generation
- No-overwrite safety
- Model slug normalization
- File write success/failure handling

## Expected Results

Each test case includes:
- **Input:** Parameters for the test
- **Expected:** What should happen
- **Verify:** How to confirm the test passed

## Adding New Tests

When adding tests:

1. Identify the category (input, mode, output)
2. Add to the appropriate test file
3. Include input, expected result, and verification steps
4. Document any fixtures needed

## Test Coverage Goals

| Area | Target |
|------|--------|
| Input validation | 100% of error cases |
| FULL mode | All 8 dimensions scored |
| COMPARISON mode | Winner determination |
| META-REVIEW mode | Variance calculation |
| Output paths | All 3 modes |
| No-overwrite | Suffix increment |

