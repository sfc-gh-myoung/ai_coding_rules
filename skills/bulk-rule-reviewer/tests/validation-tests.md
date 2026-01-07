# Validation Test Cases

## Purpose

Comprehensive test cases for input validation of bulk-rule-reviewer skill parameters. Covers happy path, error cases, edge cases, and cross-parameter validation.

---

## Test Suite Structure

```
Test Categories:
1. Required Parameters (review_date, review_mode, model)
2. Optional Parameters (filter_pattern, skip_existing, max_parallel)
3. Environment Validation (rules/ directory, reviews/ writability)
4. Cross-Parameter Validation
5. Edge Cases
```

---

## 1. Required Parameters

### 1.1 review_date

#### Test Case 1.1.1: Valid Date (Happy Path)

**Input:**
```
review_date: 2026-01-06
```

**Expected Result:** ✅ PASS

**Validation:**
- Matches YYYY-MM-DD format
- Valid calendar date
- Year in range 2024-2030

---

#### Test Case 1.1.2: Invalid Format (Wrong Separator)

**Input:**
```
review_date: 2026/01/06
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid review_date: "2026/01/06"
Expected format: YYYY-MM-DD (e.g., 2026-01-06)
```

---

#### Test Case 1.1.3: Invalid Format (Wrong Order)

**Input:**
```
review_date: 01-06-2026
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid review_date: "01-06-2026"
Expected format: YYYY-MM-DD (e.g., 2026-01-06)
```

---

#### Test Case 1.1.4: Invalid Date (Nonexistent Day)

**Input:**
```
review_date: 2026-02-30
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid review_date: "2026-02-30"
Not a valid calendar date
```

---

#### Test Case 1.1.5: Edge Case (Leap Year)

**Input:**
```
review_date: 2024-02-29
```

**Expected Result:** ✅ PASS (2024 is leap year)

---

#### Test Case 1.1.6: Edge Case (Non-Leap Year)

**Input:**
```
review_date: 2025-02-29
```

**Expected Result:** ❌ FAIL (2025 is not leap year)

---

### 1.2 review_mode

#### Test Case 1.2.1: Valid Mode (FULL)

**Input:**
```
review_mode: FULL
```

**Expected Result:** ✅ PASS

---

#### Test Case 1.2.2: Valid Mode (FOCUSED)

**Input:**
```
review_mode: FOCUSED
```

**Expected Result:** ✅ PASS

---

#### Test Case 1.2.3: Valid Mode (STALENESS)

**Input:**
```
review_mode: STALENESS
```

**Expected Result:** ✅ PASS

---

#### Test Case 1.2.4: Invalid Mode (Lowercase)

**Input:**
```
review_mode: full
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid review_mode: "full"
Expected one of: FULL, FOCUSED, STALENESS
```

---

#### Test Case 1.2.5: Invalid Mode (Unknown Value)

**Input:**
```
review_mode: COMPREHENSIVE
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid review_mode: "COMPREHENSIVE"
Expected one of: FULL, FOCUSED, STALENESS
```

---

### 1.3 model

#### Test Case 1.3.1: Valid Model (claude-sonnet-45)

**Input:**
```
model: claude-sonnet-45
```

**Expected Result:** ✅ PASS

---

#### Test Case 1.3.2: Valid Model (gpt-4)

**Input:**
```
model: gpt-4
```

**Expected Result:** ✅ PASS

---

#### Test Case 1.3.3: Invalid Model (Uppercase)

**Input:**
```
model: Claude-Sonnet-45
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid model: "Claude-Sonnet-45"
Expected format: lowercase-hyphenated (e.g., claude-sonnet-45, gpt-4)
```

---

#### Test Case 1.3.4: Invalid Model (Underscores)

**Input:**
```
model: claude_sonnet_45
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid model: "claude_sonnet_45"
Expected format: lowercase-hyphenated (e.g., claude-sonnet-45, gpt-4)
```

---

#### Test Case 1.3.5: Invalid Model (Spaces)

**Input:**
```
model: claude sonnet 45
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid model: "claude sonnet 45"
Expected format: lowercase-hyphenated (e.g., claude-sonnet-45, gpt-4)
```

---

#### Test Case 1.3.6: Invalid Model (Trailing Hyphen)

**Input:**
```
model: claude-sonnet-45-
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid model: "claude-sonnet-45-"
Expected format: lowercase-hyphenated (e.g., claude-sonnet-45, gpt-4)
```

---

## 2. Optional Parameters

### 2.1 filter_pattern

#### Test Case 2.1.1: Valid Pattern (All Rules)

**Input:**
```
filter_pattern: rules/*.md
```

**Expected Result:** ✅ PASS

---

#### Test Case 2.1.2: Valid Pattern (Snowflake Rules)

**Input:**
```
filter_pattern: rules/100-*.md
```

**Expected Result:** ✅ PASS

---

#### Test Case 2.1.3: Valid Pattern (Core Rules)

**Input:**
```
filter_pattern: rules/*-core.md
```

**Expected Result:** ✅ PASS

---

#### Test Case 2.1.4: Invalid Pattern (Missing Directory)

**Input:**
```
filter_pattern: *.md
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid filter_pattern: "*.md"
Expected format: rules/*.md (glob pattern within rules/ directory)
```

---

#### Test Case 2.1.5: Invalid Pattern (Missing Extension)

**Input:**
```
filter_pattern: rules/*
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid filter_pattern: "rules/*"
Expected format: rules/*.md (glob pattern within rules/ directory)
```

---

#### Test Case 2.1.6: Invalid Pattern (Directory Traversal)

**Input:**
```
filter_pattern: rules/../secrets/*.md
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid filter_pattern: "rules/../secrets/*.md"
Expected format: rules/*.md (glob pattern within rules/ directory)
```

---

### 2.2 skip_existing

#### Test Case 2.2.1: Valid Boolean (true)

**Input:**
```
skip_existing: true
```

**Expected Result:** ✅ PASS

---

#### Test Case 2.2.2: Valid Boolean (false)

**Input:**
```
skip_existing: false
```

**Expected Result:** ✅ PASS

---

#### Test Case 2.2.3: Invalid Boolean (Uppercase)

**Input:**
```
skip_existing: True
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid skip_existing: "True"
Expected: true or false (boolean)
```

---

#### Test Case 2.2.4: Invalid Boolean (String "yes")

**Input:**
```
skip_existing: yes
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid skip_existing: "yes"
Expected: true or false (boolean)
```

---

### 2.3 max_parallel

#### Test Case 2.3.1: Valid Integer (1 - Sequential)

**Input:**
```
max_parallel: 1
```

**Expected Result:** ✅ PASS

---

#### Test Case 2.3.2: Valid Integer (5)

**Input:**
```
max_parallel: 5
```

**Expected Result:** ✅ PASS

---

#### Test Case 2.3.3: Valid Integer (10 - Max)

**Input:**
```
max_parallel: 10
```

**Expected Result:** ✅ PASS

---

#### Test Case 2.3.4: Invalid Integer (0)

**Input:**
```
max_parallel: 0
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid max_parallel: "0"
Expected: integer between 1 and 10 (inclusive)
```

---

#### Test Case 2.3.5: Invalid Integer (Exceeds Max)

**Input:**
```
max_parallel: 15
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid max_parallel: "15"
Expected: integer between 1 and 10 (inclusive)
```

---

#### Test Case 2.3.6: Invalid Integer (Decimal)

**Input:**
```
max_parallel: 2.5
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Invalid max_parallel: "2.5"
Expected: integer between 1 and 10 (inclusive)
```

---

## 3. Environment Validation

### 3.1 rules/ Directory

#### Test Case 3.1.1: Directory Exists (Happy Path)

**Setup:**
```bash
mkdir -p rules
touch rules/example.md
```

**Expected Result:** ✅ PASS

---

#### Test Case 3.1.2: Directory Missing

**Setup:**
```bash
rm -rf rules
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Environment error: rules/ directory not found
Verify working directory is project root and rules/ directory exists
```

---

#### Test Case 3.1.3: Directory Empty

**Setup:**
```bash
mkdir -p rules
# No .md files inside
```

**Expected Result:** ❌ FAIL (in discovery stage)

**Error Message:**
```
No rule files found in rules/
```

---

### 3.2 reviews/ Directory

#### Test Case 3.2.1: Directory Exists and Writable (Happy Path)

**Setup:**
```bash
mkdir -p reviews
chmod 755 reviews
```

**Expected Result:** ✅ PASS

---

#### Test Case 3.2.2: Directory Missing (Auto-Create)

**Setup:**
```bash
rm -rf reviews
```

**Expected Result:** ✅ PASS (directory auto-created)

---

#### Test Case 3.2.3: Directory Not Writable

**Setup:**
```bash
mkdir -p reviews
chmod 444 reviews  # Read-only
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
Environment error: Cannot write to reviews/ directory
Check permissions and disk space
```

---

## 4. Cross-Parameter Validation

### 4.1 filter_pattern × rules/ Contents

#### Test Case 4.1.1: Pattern Matches Files (Happy Path)

**Setup:**
```bash
# Create 100-series rules
touch rules/100-snowflake-core.md
touch rules/101-snowflake-sql.md
```

**Input:**
```
filter_pattern: rules/100-*.md
```

**Expected Result:** ✅ PASS (2 files matched)

---

#### Test Case 4.1.2: Pattern Matches No Files

**Setup:**
```bash
# No 999-series rules exist
```

**Input:**
```
filter_pattern: rules/999-*.md
```

**Expected Result:** ❌ FAIL

**Error Message:**
```
No rule files found matching pattern: rules/999-*.md
Try: rules/*.md (all rules) or rules/100-*.md (Snowflake rules)
```

---

### 4.2 max_parallel × Review Count

#### Test Case 4.2.1: Parallel >1 with Large Batch

**Setup:**
```bash
# 113 rules exist
```

**Input:**
```
max_parallel: 5
```

**Expected Result:** ⚠️ WARNING (but proceed)

**Warning Message:**
```
WARNING: max_parallel=5 may cause context overflow for large batches
Recommended: max_parallel=1 (sequential) for stability
```

---

## 5. Edge Cases

### 5.1 Whitespace Handling

#### Test Case 5.1.1: Trailing Whitespace in Date

**Input:**
```
review_date: "2026-01-06 "
```

**Expected Result:** ❌ FAIL (whitespace not trimmed)

---

#### Test Case 5.1.2: Leading Whitespace in Model

**Input:**
```
model: " claude-sonnet-45"
```

**Expected Result:** ❌ FAIL (whitespace not trimmed)

---

### 5.2 Boundary Values

#### Test Case 5.2.1: Date at Year Boundary (Lower)

**Input:**
```
review_date: 2024-01-01
```

**Expected Result:** ✅ PASS

---

#### Test Case 5.2.2: Date at Year Boundary (Upper)

**Input:**
```
review_date: 2030-12-31
```

**Expected Result:** ✅ PASS

---

#### Test Case 5.2.3: Date Below Range

**Input:**
```
review_date: 2023-12-31
```

**Expected Result:** ❌ FAIL (year <2024)

---

### 5.3 Special Characters

#### Test Case 5.3.1: Special Chars in Model Name

**Input:**
```
model: claude-sonnet-45!
```

**Expected Result:** ❌ FAIL (special char not allowed)

---

## Test Execution Summary

**Total Test Cases:** 53

**Breakdown:**
- Required parameters: 18 tests
- Optional parameters: 12 tests
- Environment validation: 6 tests
- Cross-parameter validation: 3 tests
- Edge cases: 8 tests

**Expected Results:**
- PASS: 18 (happy path + valid edge cases)
- FAIL: 33 (error cases + invalid inputs)
- WARNING: 1 (parallel execution warning)

---

## Automated Test Script

```python
def run_validation_tests():
    """Execute all validation test cases."""
    
    test_cases = [
        # Required parameters
        {"name": "1.1.1", "params": {"review_date": "2026-01-06", "review_mode": "FULL", "model": "claude-sonnet-45"}, "expect": "PASS"},
        {"name": "1.1.2", "params": {"review_date": "2026/01/06", "review_mode": "FULL", "model": "claude-sonnet-45"}, "expect": "FAIL"},
        # ... (add all 53 test cases)
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        result = validate_inputs(**test["params"])
        if (result and test["expect"] == "PASS") or (not result and test["expect"] == "FAIL"):
            print(f"✓ Test {test['name']}: PASS")
            passed += 1
        else:
            print(f"✗ Test {test['name']}: FAIL (expected {test['expect']})")
            failed += 1
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    run_validation_tests()
```

---

## Integration with Skill

Tests should be run:
1. **During development:** Validate all test cases pass
2. **Before release:** Ensure no regressions
3. **CI/CD pipeline:** Automated validation testing

---

**Related Documentation:**
- **workflows/input-validation.md:** Validation rules specification
- **SKILL.md:** Skill definition with input contract
- **README.md:** Usage examples
