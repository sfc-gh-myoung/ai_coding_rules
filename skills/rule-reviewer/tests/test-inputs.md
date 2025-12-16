# Test Cases: Input Validation

## Test 1: Valid Complete Input

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FULL
model: claude-sonnet-45
```

**Expected Behavior:**
- All inputs validated successfully
- Review proceeds immediately

**Pass Criteria:**
- [ ] No validation errors
- [ ] Review execution starts
- [ ] All parameters captured correctly

---

## Test 2: Missing Required Field - target_file

**Input:**
```
review_date: 2025-12-15
review_mode: FULL
model: claude-sonnet-45
```

**Expected Behavior:**
- Input validation fails
- Error: "Required field missing: target_file"
- Review does not proceed

**Pass Criteria:**
- [ ] Error message clear
- [ ] Missing field identified
- [ ] Workflow halted

---

## Test 3: Missing Required Field - review_date

**Input:**
```
target_file: rules/200-python-core.md
review_mode: FULL
model: claude-sonnet-45
```

**Expected Behavior:**
- Input validation fails
- Error: "Required field missing: review_date"

**Pass Criteria:**
- [ ] Error identifies missing field
- [ ] Expected format shown (YYYY-MM-DD)

---

## Test 4: Invalid Date Format

**Input:**
```
target_file: rules/200-python-core.md
review_date: 12/15/2025
review_mode: FULL
model: claude-sonnet-45
```

**Expected Behavior:**
- Validation fails
- Error: "Invalid date format: 12/15/2025"
- Expected format: YYYY-MM-DD

**Pass Criteria:**
- [ ] Format error detected
- [ ] Correct format shown
- [ ] Example provided

---

## Test 5: Invalid Review Mode

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: PARTIAL
model: claude-sonnet-45
```

**Expected Behavior:**
- Validation fails
- Error: "Invalid review_mode: PARTIAL"
- Valid modes listed: FULL, FOCUSED, STALENESS

**Pass Criteria:**
- [ ] Invalid mode rejected
- [ ] Valid options listed
- [ ] No partial execution

---

## Test 6: Target File Not Found

**Input:**
```
target_file: rules/999-nonexistent.md
review_date: 2025-12-15
review_mode: FULL
model: claude-sonnet-45
```

**Expected Behavior:**
- Validation fails
- Error: "Target file not found: rules/999-nonexistent.md"
- Suggestions for similar files (if any)

**Pass Criteria:**
- [ ] File existence checked
- [ ] Clear error message
- [ ] Suggestions provided if applicable

---

## Test 7: Target File Not in rules/ Directory

**Input:**
```
target_file: docs/README.md
review_date: 2025-12-15
review_mode: FULL
model: claude-sonnet-45
```

**Expected Behavior:**
- Validation fails
- Error: "Target must be under rules/ directory"

**Pass Criteria:**
- [ ] Path validation enforced
- [ ] Clear error message
- [ ] Correct path format shown

---

## Test 8: Target File Not Markdown

**Input:**
```
target_file: rules/some-script.py
review_date: 2025-12-15
review_mode: FULL
model: claude-sonnet-45
```

**Expected Behavior:**
- Validation fails
- Error: "Target must be a .md file"

**Pass Criteria:**
- [ ] Extension validation
- [ ] Only .md files accepted

---

## Test 9: Model Slug Normalization

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FULL
model: Claude Sonnet 4.5
```

**Expected Behavior:**
- Model slug normalized to: claude-sonnet-45
- Review proceeds with normalized slug

**Pass Criteria:**
- [ ] Slug normalized correctly
- [ ] Spaces removed
- [ ] Case normalized
- [ ] Output filename uses normalized slug

---

## Test 10: FOCUSED Mode Without focus_area

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: FOCUSED
model: claude-sonnet-45
```

**Expected Behavior:**
- Validation warns about missing focus_area
- Prompts for focus_area selection
- Lists available focus areas

**Pass Criteria:**
- [ ] Warning issued
- [ ] Focus areas listed
- [ ] User prompted for selection

---

## Test 11: Case Insensitive Review Mode

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2025-12-15
review_mode: full
model: claude-sonnet-45
```

**Expected Behavior:**
- Mode normalized to uppercase: FULL
- Review proceeds normally

**Pass Criteria:**
- [ ] Case insensitive matching
- [ ] Normalized internally
- [ ] No validation error

---

## Test 12: Future Date

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2030-01-01
review_mode: FULL
model: claude-sonnet-45
```

**Expected Behavior:**
- Warning: "Review date is in the future"
- Proceeds with warning (not blocking)

**Pass Criteria:**
- [ ] Warning issued
- [ ] Not blocking error
- [ ] Date used as provided

---

## Test 13: Past Date (Very Old)

**Input:**
```
target_file: rules/200-python-core.md
review_date: 2020-01-01
review_mode: FULL
model: claude-sonnet-45
```

**Expected Behavior:**
- Warning: "Review date is unusually old"
- Proceeds with warning

**Pass Criteria:**
- [ ] Warning issued
- [ ] Proceeds anyway
- [ ] Date used as provided

