# Test Cases: Input Validation

## Test 1: Valid Inputs (All Required)

**Inputs:**

```text
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- All inputs accepted
- Default targets discovered (README.md, CONTRIBUTING.md, docs/*.md)
- Review proceeds

---

## Test 2: Valid Inputs (With Target Files)

**Inputs:**

```text
target_files: [README.md, CONTRIBUTING.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- All inputs accepted
- Only specified files reviewed
- Review proceeds

---

## Test 3: Invalid Date Format (MM/DD/YYYY)

**Inputs:**

```text
review_date: 12/16/2025
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- Error: Invalid date format
- Message shows expected format (YYYY-MM-DD)
- Review does not proceed

---

## Test 4: Invalid Date Format (No Dashes)

**Inputs:**

```text
review_date: 20251216
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- Error: Invalid date format
- Message shows expected format (YYYY-MM-DD)
- Review does not proceed

---

## Test 5: Invalid Review Mode

**Inputs:**

```text
review_date: 2025-12-16
review_mode: PARTIAL
model: claude-sonnet45
```

**Expected:**

- Error: Invalid review_mode
- Message lists valid modes (FULL, FOCUSED, STALENESS)
- Review does not proceed

---

## Test 6: Invalid Review Scope

**Inputs:**

```text
review_date: 2025-12-16
review_mode: FULL
review_scope: combined
model: claude-sonnet45
```

**Expected:**

- Error: Invalid scope
- Message lists valid scopes (single, collection)
- Review does not proceed

---

## Test 7: FOCUSED Mode Without Focus Area

**Inputs:**

```text
review_date: 2025-12-16
review_mode: FOCUSED
model: claude-sonnet45
```

**Expected:**

- Error: FOCUSED mode requires focus_area
- Message lists valid focus areas
- Review does not proceed

---

## Test 8: FOCUSED Mode With Invalid Focus Area

**Inputs:**

```text
review_date: 2025-12-16
review_mode: FOCUSED
focus_area: grammar
model: claude-sonnet45
```

**Expected:**

- Error: Invalid focus_area
- Message lists valid areas (accuracy, completeness, clarity, consistency, staleness, structure)
- Review does not proceed

---

## Test 9: FOCUSED Mode With Valid Focus Area

**Inputs:**

```text
review_date: 2025-12-16
review_mode: FOCUSED
focus_area: accuracy
model: claude-sonnet45
```

**Expected:**

- All inputs accepted
- Review proceeds with accuracy focus only
- Output contains Cross-Reference Verification table

---

## Test 10: Target File Not Found

**Inputs:**

```text
target_files: [README.md, docs/NONEXISTENT.md]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- Error: File not found: docs/NONEXISTENT.md
- Review does not proceed
- Suggests checking file path

---

## Test 11: Non-Markdown Target File

**Inputs:**

```text
target_files: [README.md, src/main.py]
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- Warning: Non-markdown file in target list
- Options presented: proceed with markdown only or cancel
- If proceed: reviews README.md only

---

## Test 12: No Documentation Found (Empty Project)

**Inputs:**

```text
# In a project with no README.md, CONTRIBUTING.md, or docs/
review_date: 2025-12-16
review_mode: FULL
model: claude-sonnet45
```

**Expected:**

- Error: No documentation files found
- Message lists checked locations
- Suggests specifying target_files explicitly

---

## Validation Summary

- **1** - Input Type: Valid (minimal), Expected Result: Pass
- **2** - Input Type: Valid (with targets), Expected Result: Pass
- **3** - Input Type: Invalid date (MM/DD/YYYY), Expected Result: Fail with message
- **4** - Input Type: Invalid date (no dashes), Expected Result: Fail with message
- **5** - Input Type: Invalid mode, Expected Result: Fail with message
- **6** - Input Type: Invalid scope, Expected Result: Fail with message
- **7** - Input Type: FOCUSED without focus_area, Expected Result: Fail with message
- **8** - Input Type: FOCUSED with invalid focus_area, Expected Result: Fail with message
- **9** - Input Type: FOCUSED with valid focus_area, Expected Result: Pass
- **10** - Input Type: Target not found, Expected Result: Fail with message
- **11** - Input Type: Non-markdown target, Expected Result: Warn, offer options
- **12** - Input Type: No docs found, Expected Result: Fail with message

