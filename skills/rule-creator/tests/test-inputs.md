# Test Cases: Input Validation

## Test 1: Valid Minimal Input

**Input:**
```
technology: DaisyUI
```

**Expected Behavior:**
- Aspect defaults to "core"
- Domain discovery succeeds (420-449)
- Proceeds to template generation

**Pass Criteria:**
- [ ] No input validation errors
- [ ] Domain correctly identified
- [ ] Aspect set to "core"

---

## Test 2: Valid Full Input

**Input:**
```
technology: pytest-mock
aspect: core
constraints: offline research only
context_tier: Medium
```

**Expected Behavior:**
- All inputs parsed correctly
- No web research performed (offline constraint)
- ContextTier set to Medium

**Pass Criteria:**
- [ ] All parameters captured
- [ ] Offline constraint respected
- [ ] ContextTier applied to template

---

## Test 3: Invalid Technology Name (Empty)

**Input:**
```
technology: 
aspect: core
```

**Expected Behavior:**
- Input validation fails
- Clear error message returned
- No template generation attempted

**Pass Criteria:**
- [ ] Error: "Technology name required"
- [ ] Workflow halted at validation

---

## Test 4: Invalid Aspect Value

**Input:**
```
technology: React
aspect: invalid-aspect
```

**Expected Behavior:**
- Aspect validation warning (not blocking)
- Suggest valid aspects: core, security, testing, performance
- Allow proceeding with custom aspect

**Pass Criteria:**
- [ ] Warning about non-standard aspect
- [ ] Proceeds if user confirms
- [ ] Custom aspect used in filename

---

## Test 5: Invalid ContextTier

**Input:**
```
technology: FastAPI
context_tier: SuperHigh
```

**Expected Behavior:**
- Input validation fails
- List valid tiers: Critical, High, Medium, Low
- Request correction

**Pass Criteria:**
- [ ] Error: "Invalid ContextTier"
- [ ] Valid options listed
- [ ] Workflow halted until corrected

---

## Test 6: Technology with Special Characters

**Input:**
```
technology: C++
```

**Expected Behavior:**
- Normalize to valid filename: "cpp"
- Proceed with normalized name

**Pass Criteria:**
- [ ] Filename: `NNN-cpp-core.md`
- [ ] Keywords include "C++"
- [ ] No filesystem errors

---

## Test 7: Technology with Version Number

**Input:**
```
technology: Python 3.12
```

**Expected Behavior:**
- Extract version for context
- Normalize filename: "python312" or "python-312"
- Include version in rule content

**Pass Criteria:**
- [ ] Version noted in rule metadata
- [ ] Filename is filesystem-safe
- [ ] Content references Python 3.12 specifically

---

## Test 8: Multi-Word Technology

**Input:**
```
technology: React Testing Library
```

**Expected Behavior:**
- Convert to hyphenated: "react-testing-library"
- Proceed with normalized name

**Pass Criteria:**
- [ ] Filename: `NNN-react-testing-library-core.md`
- [ ] Keywords include full name
- [ ] Spaces handled correctly

---

## Test 9: Duplicate Technology Request

**Input:**
```
technology: pytest
aspect: core
```

**Existing:**
- `rules/206-python-pytest.md` already exists

**Expected Behavior:**
- Discovery finds existing rule
- Warn user about duplicate
- Offer alternatives: different aspect, update existing

**Pass Criteria:**
- [ ] Warning: "Rule already exists"
- [ ] Existing rule path shown
- [ ] Options presented to user

---

## Test 10: Conflicting Constraints

**Input:**
```
technology: NewFramework
constraints: offline research only, must include 2024 best practices
```

**Expected Behavior:**
- Detect conflicting constraints
- Cannot get 2024 practices without web research
- Request clarification

**Pass Criteria:**
- [ ] Conflict detected
- [ ] Clear explanation provided
- [ ] User asked to resolve conflict

