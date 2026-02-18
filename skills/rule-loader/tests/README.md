# Rule Loader Tests

## Overview

Test scenarios for validating the rule-loader skill's selection logic. Each test case specifies an input request and the expected rule selection output.

## How to Use

1. Provide the test input as `user_request`
2. Run the rule-loader skill
3. Compare the `## Rules Loaded` output against expected output
4. Note any discrepancies

## Test Categories

| Category | File | Description |
|----------|------|-------------|
| Selection scenarios | `test-scenarios.md` | Input/output pairs for rule selection logic |

## Validation Criteria

A test passes when:
- All expected rules are present in the output
- No unexpected rules are included
- Loading reasons match expected reasons
- Dependencies are loaded before dependents
- Deferred rules are correctly identified (when over budget)
- Foundation is always first in the list
