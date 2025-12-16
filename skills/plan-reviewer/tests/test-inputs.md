# Input Validation Tests

## Test 1: Valid FULL Mode Input

**Input:**
```text
target_file: plans/IMPROVE_RULE_LOADING.md
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:** Review proceeds without input errors.

**Verify:** No "Error" message at start; review output generated.

---

## Test 2: Invalid Review Mode

**Input:**
```text
target_file: plans/test.md
review_date: 2025-12-16
review_mode: PARTIAL
model: test-model
```

**Expected:** Error message:
```
❌ Error: Invalid review_mode

Problem: 'PARTIAL' is not a valid mode
Recovery: Use one of: FULL, COMPARISON, META-REVIEW
```

**Verify:** Review does not proceed; error message displayed.

---

## Test 3: Invalid Date Format

**Input:**
```text
target_file: plans/test.md
review_date: 12-16-2025
review_mode: FULL
model: test-model
```

**Expected:** Error message:
```
❌ Error: Invalid date format

Problem: '12-16-2025' does not match YYYY-MM-DD
Recovery: Use format YYYY-MM-DD (e.g., 2025-12-16)
```

**Verify:** Review does not proceed; error message displayed.

---

## Test 4: File Not Found

**Input:**
```text
target_file: plans/nonexistent.md
review_date: 2025-12-16
review_mode: FULL
model: test-model
```

**Expected:** Error message:
```
❌ Error: File not found

Problem: plans/nonexistent.md does not exist
Recovery: Verify the file path is correct relative to workspace root
```

**Verify:** Review does not proceed; error message displayed.

---

## Test 5: Non-Markdown File

**Input:**
```text
target_file: scripts/deploy.sh
review_date: 2025-12-16
review_mode: FULL
model: test-model
```

**Expected:** Error message:
```
❌ Error: Invalid file type

Problem: scripts/deploy.sh is not a markdown file
Recovery: Target file must end with .md
```

**Verify:** Review does not proceed; error message displayed.

---

## Test 6: COMPARISON Mode - Single File

**Input:**
```text
target_files: [plans/single.md]
task_description: Test task
review_date: 2025-12-16
review_mode: COMPARISON
model: test-model
```

**Expected:** Error message:
```
❌ Error: Insufficient files for COMPARISON mode

Problem: COMPARISON mode requires at least 2 plan files
Recovery: Provide 2 or more plan files to compare
```

**Verify:** Review does not proceed; error message displayed.

---

## Test 7: COMPARISON Mode - Missing Task Description

**Input:**
```text
target_files: [plans/a.md, plans/b.md]
review_date: 2025-12-16
review_mode: COMPARISON
model: test-model
```

**Expected:** Error message (or prompt for input):
```
❌ Error: Missing required field

Problem: COMPARISON mode requires task_description
Recovery: Provide a brief description of what the plans should accomplish
```

**Verify:** Review does not proceed without task_description.

---

## Test 8: META-REVIEW Mode - Single Review

**Input:**
```text
target_files: [reviews/single-review.md]
review_date: 2025-12-16
review_mode: META-REVIEW
model: test-model
```

**Expected:** Error message:
```
❌ Error: Insufficient files for META-REVIEW mode

Problem: META-REVIEW mode requires at least 2 review files
Recovery: Provide 2 or more review files to analyze
```

**Verify:** Review does not proceed; error message displayed.

---

## Test 9: META-REVIEW Mode - Non-Review Files

**Input:**
```text
target_files: [plans/a.md, plans/b.md]
review_date: 2025-12-16
review_mode: META-REVIEW
model: test-model
```

**Expected:** Warning or error:
```
⚠️ Warning: Files may not be reviews

Problem: Expected review files in reviews/ directory
Provided: plans/a.md, plans/b.md
Proceeding: Will attempt to parse as reviews; results may be incomplete
```

**Verify:** Warning displayed; review attempts to proceed.

---

## Test 10: Empty Model Name

**Input:**
```text
target_file: plans/test.md
review_date: 2025-12-16
review_mode: FULL
model:
```

**Expected:** Error message:
```
❌ Error: Missing required field

Problem: 'model' is required
Recovery: Provide a model identifier (e.g., claude-sonnet45, gpt-52)
```

**Verify:** Review does not proceed; error message displayed.

---

## Test 11: Case Insensitive Mode

**Input:**
```text
target_file: plans/test.md
review_date: 2025-12-16
review_mode: full
model: test-model
```

**Expected:** Review proceeds (mode normalized to uppercase).

**Verify:** No error; review output generated in FULL mode format.

---

## Test 12: All Fields Valid with Existing File

**Input:**
```text
target_file: [use actual existing plan file]
review_date: [today's date in YYYY-MM-DD]
review_mode: FULL
model: test-model
```

**Expected:** Review proceeds without input errors.

**Verify:**
1. No error messages
2. All 8 dimensions scored
3. Output file created

---

## Edge Case: Future Date

**Input:**
```text
target_file: plans/test.md
review_date: 2030-01-01
review_mode: FULL
model: test-model
```

**Expected:** Accept (future dates may be valid for scheduled reviews).

**Verify:** Review proceeds; no date validation error.

---

## Edge Case: Very Long Model Name

**Input:**
```text
target_file: plans/test.md
review_date: 2025-12-16
review_mode: FULL
model: this-is-an-extremely-long-model-name-that-might-cause-path-length-issues-on-some-systems
```

**Expected:** Either accept with truncation or error gracefully.

**Verify:** Output path doesn't exceed OS limits; review completes or fails cleanly.

