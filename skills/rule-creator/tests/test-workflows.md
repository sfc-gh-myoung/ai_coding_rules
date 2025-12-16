# Test Cases: Workflow Execution

## Phase 1: Discovery Tests

### Test 1.1: Domain Discovery - Clear Match

**Input:**
```
technology: FastAPI
```

**Expected:**
- Search RULES_INDEX.md for "fastapi", "python", "api"
- Find Python domain (200-299)
- Identify next available number

**Verification:**
```bash
grep -i "fastapi\|python" RULES_INDEX.md
```

**Pass Criteria:**
- [ ] Domain: 200-299
- [ ] Number: Next available after existing Python rules
- [ ] Core rule loaded: rules/200-python-core.md

---

### Test 1.2: Domain Discovery - Ambiguous Match

**Input:**
```
technology: GraphQL
```

**Expected:**
- Could be: API (general), JavaScript (Apollo), Python (Strawberry)
- User clarification requested

**Pass Criteria:**
- [ ] Ambiguity detected
- [ ] Options presented with rationale
- [ ] User selection captured

---

### Test 1.3: Web Research Execution

**Input:**
```
technology: Pydantic
constraints: online research allowed
```

**Expected Searches:**
1. "2024 2025 Pydantic best practices"
2. "Pydantic official documentation"
3. "Pydantic common mistakes"

**Pass Criteria:**
- [ ] 3+ searches executed
- [ ] Results summarized
- [ ] Keywords extracted (10-15)
- [ ] Anti-patterns identified (2+)

---

## Phase 2: Template Generation Tests

### Test 2.1: Successful Template Generation

**Input:**
```bash
python scripts/template_generator.py 210-python-pydantic-core \
    --context-tier Medium \
    --output-dir rules/
```

**Expected:**
- File created: `rules/210-python-pydantic-core.md`
- Contains 9 required sections
- Contains 6 Contract XML tags
- Contract before line 160

**Verification:**
```bash
# Check file exists
ls rules/210-python-pydantic-core.md

# Count sections
grep -c "^## " rules/210-python-pydantic-core.md
# Expected: 9+

# Check Contract placement
grep -n "## Contract" rules/210-python-pydantic-core.md
# Expected: Line < 160
```

**Pass Criteria:**
- [ ] File created
- [ ] 9+ sections present
- [ ] Contract before line 160
- [ ] All 6 XML tags present

---

### Test 2.2: Template Generation - Invalid Filename

**Input:**
```bash
python scripts/template_generator.py InvalidName \
    --output-dir rules/
```

**Expected:**
- Error: Invalid filename format
- Expected format: NNN-technology-aspect

**Pass Criteria:**
- [ ] Error message clear
- [ ] No file created
- [ ] Format requirements shown

---

### Test 2.3: Template Generation - Existing File

**Input:**
```bash
python scripts/template_generator.py 200-python-core \
    --output-dir rules/
```

**Expected:**
- Warning: File already exists
- Option to overwrite or abort

**Pass Criteria:**
- [ ] Existing file not overwritten without confirmation
- [ ] Clear warning message

---

## Phase 3: Content Population Tests

### Test 3.1: Metadata Population

**Input:**
```
Keywords from research: pydantic, validation, data models, type hints,
  serialization, deserialization, settings, BaseModel, Field, validators
```

**Expected:**
```markdown
**Keywords:** pydantic, validation, data models, type hints, serialization, deserialization, settings, BaseModel, Field, validators
**TokenBudget:** ~1200
**ContextTier:** Medium
**Depends:** rules/000-global-core.md, rules/200-python-core.md
```

**Pass Criteria:**
- [ ] Keywords: 10-15 count
- [ ] TokenBudget: ~NUMBER format
- [ ] ContextTier: Valid value
- [ ] Depends: Includes foundation + domain core

---

### Test 3.2: Anti-Pattern Population

**Expected Structure:**
```markdown
### Anti-Pattern 1: [Name]

**Problem:** [Description]

```python
# Wrong approach
[code example]
```

**Why It Fails:** [Explanation]

**Correct Pattern:**
```python
# Right approach
[code example]
```
```

**Pass Criteria:**
- [ ] 2+ anti-patterns included
- [ ] Each has Problem, Wrong code, Why It Fails, Correct code
- [ ] Code examples are syntactically correct

---

## Phase 4: Validation Tests

### Test 4.1: Validation Pass on First Try

**Input:**
```bash
python scripts/schema_validator.py rules/210-python-pydantic-core.md
```

**Expected:**
```
SUMMARY:
  ❌ CRITICAL: 0
  ⚠️  HIGH: 0
  ℹ️  MEDIUM: 0
  ✓ Passed: 458 checks

RESULT: ✅ PASSED (exit code 0)
```

**Pass Criteria:**
- [ ] Exit code: 0
- [ ] CRITICAL: 0
- [ ] HIGH: 0

---

### Test 4.2: Validation Failure - Keywords Count

**Scenario:** Rule has only 8 keywords

**Expected:**
```
❌ CRITICAL ISSUES (1):
[Metadata] Keywords count: 8 (expected 10-15)
  Line: 5
  Fix: Add 2 more keywords to reach minimum of 10
```

**Pass Criteria:**
- [ ] Error correctly identified
- [ ] Line number provided
- [ ] Fix suggestion clear

---

### Test 4.3: Validation Loop - Fix and Retry

**Scenario:** First validation fails, fixes applied, second passes

**Expected Sequence:**
1. Iteration 1: FAIL (2 CRITICAL)
2. Apply fixes
3. Iteration 2: PASS (0 CRITICAL)

**Pass Criteria:**
- [ ] Errors fixed correctly
- [ ] Re-validation executed
- [ ] Exit code 0 on retry

---

### Test 4.4: Validation Loop - Max Iterations

**Scenario:** Errors persist after 3 iterations

**Expected:**
```
✗ Still failing after 3 iterations
Manual intervention required

Unresolved errors:
- [Error 1]
- [Error 2]

Reference: rules/002d-schema-validator-usage.md
```

**Pass Criteria:**
- [ ] Stopped at 3 iterations
- [ ] Errors clearly listed
- [ ] Reference to help documentation

---

## Phase 5: Indexing Tests

### Test 5.1: Successful Indexing

**Input:**
```
Rule: rules/210-python-pydantic-core.md
```

**Expected Entry:**
```markdown
| 210-python-pydantic-core | Pydantic validation and data modeling | pydantic, validation, data models, type hints, ... | rules/200-python-core.md |
```

**Verification:**
```bash
grep "210-python-pydantic" RULES_INDEX.md
```

**Pass Criteria:**
- [ ] Entry added to RULES_INDEX.md
- [ ] Correct numeric position (after 209, before 211)
- [ ] All columns populated
- [ ] Table formatting preserved

---

### Test 5.2: Indexing - Maintain Sort Order

**Scenario:** Adding rule 215 when 210 and 220 exist

**Expected:**
```markdown
| 210-python-... | ... |
| 215-python-... | ... |  ← NEW (correct position)
| 220-python-... | ... |
```

**Pass Criteria:**
- [ ] Inserted in correct numeric order
- [ ] No duplicate entries
- [ ] Table structure intact

---

## End-to-End Tests

### Test E2E.1: Complete Workflow - Python Library

**Input:**
```
Create a new rule for httpx best practices following v3.0 schema
```

**Expected Timeline:**
- Discovery: ~5 min
- Template: ~1 min
- Content: ~10 min
- Validation: ~2 min (1-2 iterations)
- Indexing: ~1 min
- **Total: ~19 min**

**Pass Criteria:**
- [ ] File exists: rules/2XX-python-httpx-core.md
- [ ] Validation: exit code 0
- [ ] Indexed in RULES_INDEX.md
- [ ] Total time < 30 min

---

### Test E2E.2: Complete Workflow - Frontend Framework

**Input:**
```
Create a new rule for Svelte best practices following v3.0 schema
```

**Expected:**
- Domain: 420-449 (JavaScript/Frontend)
- Dependencies: rules/420-javascript-core.md

**Pass Criteria:**
- [ ] Correct domain assignment
- [ ] Dependencies include JS core
- [ ] Keywords include "svelte", "components", "reactivity"

