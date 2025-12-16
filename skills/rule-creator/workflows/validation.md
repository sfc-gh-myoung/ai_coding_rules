# Phase 4: Validation Loop Workflow

## Purpose

Execute `schema_validator.py` iteratively to validate the populated rule against schema, fix any CRITICAL/HIGH errors, and continue until achieving 0 CRITICAL errors (exit code 0).

## Inputs

From Phase 3:
- Fully populated rule file: `rules/NNN-technology-aspect.md`
- All sections filled with real content
- No placeholder text remaining

## Outputs

- Validated rule with 0 CRITICAL errors
- Exit code 0 from `schema_validator.py`
- All CRITICAL and HIGH errors resolved
- MEDIUM warnings addressed or documented

## Step-by-Step Instructions

### Step 4.1: Initial Validation

**Command:**
```bash
python scripts/schema_validator.py rules/[NNN]-[technology]-[aspect].md
```

**Example:**
```bash
python scripts/schema_validator.py rules/422-daisyui-core.md
```

### Step 4.2: Capture Exit Code

```bash
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "✓ Validation PASSED - proceed to Phase 5"
  exit 0
else
  echo "✗ Validation FAILED - analyzing errors..."
  # Continue to error analysis
fi
```

**Exit code meanings:**
- `0`: PASS - No CRITICAL or HIGH errors
- `1`: FAIL - One or more CRITICAL or HIGH errors present

### Step 4.3: Parse Validation Output

**Output structure:**
```
================================================================================
VALIDATION REPORT: rules/422-daisyui-core.md
================================================================================

SUMMARY:
  ❌ CRITICAL: 2
  ⚠️  HIGH: 1
  ℹ️  MEDIUM: 0
  ✓ Passed: 445 checks

❌ CRITICAL ISSUES (2):
────────────────────────────────────────────────────────────────────────────────
[Metadata] Keywords count: 8 (expected 10-15)
  Line: 5
  Fix: Add 2 more keywords to reach minimum of 10

[Contract] Missing XML tag: <validation>
  Line: 78
  Fix: Add <validation> tag in Contract section

⚠️  HIGH ISSUES (1):
────────────────────────────────────────────────────────────────────────────────
[Structure] Section order: Contract should appear before Key Principles
  Fix: Reorder sections per schema

================================================================================
RESULT: ❌ FAILED
================================================================================
```

### Step 4.4: Common Error Patterns and Fixes

#### Error Type 1: Keywords Count Wrong

**Error:**
```
[Metadata] Keywords count: 8 (expected 10-15)
  Line: 5
  Fix: Add 2 more keywords to reach minimum of 10
```

**Fix:**
```markdown
# Before (8 keywords)
**Keywords:** daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables

# After (12 keywords)
**Keywords:** daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization, utility-first, design system
```

**Verification:**
- Count commas + 1 = keyword count
- Must be between 10-15 (inclusive)

---

#### Error Type 2: TokenBudget Format Invalid

**Error:**
```
[Metadata] TokenBudget format invalid: expected ~NUMBER format
  Line: 7
  Fix: Change to ~1200 format (with tilde prefix)
```

**Fix:**
```markdown
# Wrong formats
**TokenBudget:** 1200         ❌ Missing tilde
**TokenBudget:** small        ❌ Text label forbidden
**TokenBudget:** ~medium      ❌ Text with tilde still wrong

# Correct format
**TokenBudget:** ~1200        ✓ Tilde + number
```

---

#### Error Type 3: Missing Contract XML Tag

**Error:**
```
[Contract] Missing XML tag: <validation>
  Line: 78
  Fix: Add <validation> tag in Contract section
```

**Fix:**
Add missing tag to Contract section:
```markdown
## Contract

<inputs_prereqs>
...
</inputs_prereqs>

<mandatory>
...
</mandatory>

<forbidden>
...
</forbidden>

<steps>
...
</steps>

<output_format>
...
</output_format>

<validation>
How to verify success - specific checks agent should run
</validation>
```

**Verification:** All 6 tags must be present:
1. `<inputs_prereqs>`
2. `<mandatory>`
3. `<forbidden>`
4. `<steps>`
5. `<output_format>`
6. `<validation>`

---

#### Error Type 4: Contract Placement After Line 160

**Error:**
```
[Contract] Contract section after line 160 (current line: 185)
  Line: 185
  Fix: Move Contract section to before line 160
```

**Fix:**
1. Cut entire Contract section (from `## Contract` to next `##`)
2. Paste earlier in file (after Quick Start TL;DR, before other sections)
3. Ensure placement before line 160

**Typical order:**
```markdown
## Purpose
## Rule Scope
## Quick Start TL;DR
## Contract          ← Must be before line 160
## [Other sections]
```

---

#### Error Type 5: Missing Required Section

**Error:**
```
[Structure] Missing required section: Quick Start TL;DR
  Fix: Add '## Quick Start TL;DR' section
```

**Fix:**
Add the missing section with proper structure:
```markdown
## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Pattern 1:** Description
- **Pattern 2:** Description
- **Pattern 3:** Description

**Pre-Execution Checklist:**
- [ ] Item 1
- [ ] Item 2
- [ ] Item 3
- [ ] Item 4
- [ ] Item 5
```

---

#### Error Type 6: Section Order Wrong

**Error:**
```
[Structure] Sections out of order: Contract should come before Key Principles
  Fix: Reorder sections per schema
```

**Correct v3.0 order:**
1. Purpose
2. Rule Scope
3. Quick Start TL;DR
4. Contract
5. Key Principles (optional)
6. [Main content sections]
7. Anti-Patterns and Common Mistakes (optional)
8. Post-Execution Checklist
9. Validation
10. Output Format Examples
11. References

**Fix:** Reorder sections to match required sequence

---

#### Error Type 7: Related Rules Missing `rules/` Prefix

**Error:**
```
[References] Rule reference missing required prefix: 420-javascript-core.md
  Line: 245
  Fix: Change to rules/420-javascript-core.md
```

**Fix:**
```markdown
# Wrong
- `420-javascript-core.md` - JavaScript foundation

# Correct
- `rules/420-javascript-core.md` - JavaScript foundation
```

### Step 4.5: Apply Fixes

For each error:
1. Read error message and line number
2. Locate issue in file
3. Apply appropriate fix from error patterns above
4. Save file
5. Proceed to re-validation

### Step 4.6: Re-validate

After applying fixes:
```bash
python scripts/schema_validator.py rules/422-daisyui-core.md
EXIT_CODE=$?
```

### Step 4.7: Iteration Control

**Maximum iterations:** 3

**Iteration logic:**
```python
iteration = 1
max_iterations = 3

while iteration <= max_iterations:
    result = validate_file()
    
    if result.exit_code == 0:
        print(f"✓ Validation passed on iteration {iteration}")
        break
    
    if iteration == max_iterations:
        print(f"✗ Still failing after {max_iterations} iterations")
        print("Manual intervention required")
        break
    
    # Apply fixes
    fix_errors(result.errors)
    iteration += 1
```

**If still failing after 3 iterations:**
- Report unresolved errors to user
- Request manual review
- Reference `rules/002d-schema-validator-usage.md` for detailed error resolution

### Step 4.8: Handle Different Severity Levels

**CRITICAL (Must fix - blocks completion):**
- Missing required metadata fields
- Missing required sections
- Missing Contract XML tags
- Keywords count outside 10-15 range
- TokenBudget format invalid

**Action:** Fix immediately, cannot proceed without resolving

---

**HIGH (Strongly recommended to fix):**
- Section order violations
- Contract placement after line 160
- Missing Anti-Patterns section (if common for domain)

**Action:** Fix if possible, document if intentionally deviating

---

**MEDIUM (Optional - acceptable to proceed):**
- Missing some code examples
- Anti-Patterns could be more detailed
- Some external references missing

**Action:** Consider fixing for quality, OK to proceed with warnings

---

**INFO (Informational only):**
- Passed checks
- Suggestions for improvement

**Action:** No action required

## Complete Validation Loop Example

**Iteration 1:**
```bash
$ python scripts/schema_validator.py rules/422-daisyui-core.md

SUMMARY:
  ❌ CRITICAL: 2
  ⚠️  HIGH: 0
  ℹ️  MEDIUM: 0

❌ CRITICAL ISSUES (2):
[Metadata] Keywords count: 9 (expected 10-15)
  Fix: Add 1 more keyword

[Metadata] TokenBudget format invalid
  Fix: Change "1200" to "~1200"

RESULT: ❌ FAILED (exit code 1)

Fixing errors...
  ✓ Added keyword "design-patterns" (now 10 keywords)
  ✓ Changed TokenBudget to ~1200

Re-validating...
```

**Iteration 2:**
```bash
$ python scripts/schema_validator.py rules/422-daisyui-core.md

SUMMARY:
  ❌ CRITICAL: 0
  ⚠️  HIGH: 0
  ℹ️  MEDIUM: 1
  ✓ Passed: 458 checks

ℹ️  MEDIUM ISSUES (1):
[Anti-Patterns] Could include more code examples

RESULT: ⚠️  WARNINGS ONLY (exit code 0)

✓ Validation PASSED - 0 CRITICAL errors
✓ Ready for Phase 5: Indexing
```

## Using Verbose Mode for Debugging

If errors are unclear:
```bash
python scripts/schema_validator.py rules/422-daisyui-core.md --verbose
```

**Verbose output includes:**
- All passed checks (not just errors)
- Detailed context for each validation
- Line previews for errors
- Full diff for section order issues

## Using JSON Mode for Programmatic Parsing

For automated workflows:
```bash
python scripts/schema_validator.py rules/422-daisyui-core.md --json > validation.json
```

**Parse JSON output:**
```python
import json

with open('validation.json') as f:
    result = json.load(f)

critical_count = result['summary']['failed']
if critical_count > 0:
    for file_info in result['failed_files']:
        for error in file_info['errors']:
            if error['severity'] == 'CRITICAL':
                print(f"Line {error['line']}: {error['message']}")
                print(f"Fix: {error['fix']}")
```

## Validation Checklist

Before proceeding to Phase 5:

- [x] `schema_validator.py` executed successfully
- [x] Exit code is 0 (no CRITICAL or HIGH errors)
- [x] All CRITICAL errors resolved
- [x] HIGH errors addressed or documented
- [x] MEDIUM warnings reviewed (optional to fix)
- [x] Iteration count ≤ 3
- [x] File ready for indexing

## Troubleshooting

### Issue: Validator Not Found

**Symptom:**
```
python: can't open file 'scripts/schema_validator.py'
```

**Fix:**
```bash
# Check current directory
pwd

# Should be in project root
cd /Users/myoung/Development/ai_coding_rules

# Verify script exists
ls scripts/schema_validator.py
```

### Issue: Validation Passes But Rule Seems Incomplete

**Symptom:** Exit code 0 but rule content appears minimal

**Investigation:**
```bash
# Check file size
ls -lh rules/422-daisyui-core.md

# Count sections
grep -c "^## " rules/422-daisyui-core.md
# Should be 9+ sections

# Check for placeholder text
grep -i "placeholder\|\[.*\]" rules/422-daisyui-core.md
```

### Issue: Persistent CRITICAL Errors After 3 Iterations

**Action:**
1. Review `rules/002d-schema-validator-usage.md` Section: "Common Errors and Fixes"
2. Check similar rules in same domain for structure examples
3. Run with `--verbose` flag for detailed output
4. Request user assistance with specific error details

## Success Criteria

Validation complete when:
- ✅ `schema_validator.py` returns exit code 0
- ✅ 0 CRITICAL errors
- ✅ 0 HIGH errors (or documented exceptions)
- ✅ MEDIUM warnings acceptable
- ✅ Iterations ≤ 3

## Next Phase

Proceed to **Phase 5: Indexing** (`workflows/indexing.md`)

**Preparation:**
- Rule file validated and ready
- No more modifications needed
- Ready to add to RULES_INDEX.md

