# Parsability Rubric (15 points)

## Scoring Criteria

### 5/5 (15 points): Excellent
- Schema validation: 0 errors
- All 7 metadata fields present and correct
- Markdown structure valid (proper heading hierarchy)
- 0 visual formatting issues (no ASCII art, arrows, box drawing)

### 4/5 (12 points): Good
- Schema validation: 0-2 LOW severity issues only
- 6-7 metadata fields present
- Markdown mostly valid (1-2 minor issues)
- 0-1 visual formatting issues

### 3/5 (9 points): Acceptable
- Schema validation: 1-2 MEDIUM errors
- 5-6 metadata fields present
- Markdown has 3-5 issues
- 2-3 visual formatting issues

### 2/5 (6 points): Needs Work
- Schema validation: 1-2 HIGH errors OR 3+ MEDIUM
- 3-4 metadata fields present
- Significant markdown problems (6+ issues)
- 4+ visual formatting issues

### 1/5 (3 points): Poor
- Schema validation: ≥1 CRITICAL error
- <3 metadata fields present
- Malformed markdown
- Extensive visual formatting

## Counting Definitions

### Schema Validation Errors

Run schema validator first:
```bash
uv run python scripts/schema_validator.py [target_file]
```

**Error severity levels:**
- **CRITICAL:** Prevents agent parsing (e.g., missing required section, invalid YAML)
- **HIGH:** Major structural issue (e.g., section out of order, missing Depends)
- **MEDIUM:** Moderate issue (e.g., missing optional field, minor format error)
- **LOW:** Minor issue (e.g., whitespace, style inconsistency)

**Count by severity (fill in during review):**
- CRITICAL errors: ___ (lines: ___)
- HIGH errors: ___ (lines: ___)
- MEDIUM errors: ___ (lines: ___)
- LOW errors: ___ (lines: ___)

### Metadata Field Checklist

**Required fields (v3.2 schema) - check Y/N:**

**Metadata Field Checklist:**
- SchemaVersion: Present? Valid format (v3.2)?
- RuleVersion: Present? Valid format (vX.Y.Z semver)?
- LastUpdated: Present? Valid format (YYYY-MM-DD)?
- Keywords: Present? Valid format (3+ comma-separated)?
- TokenBudget: Present? Valid format (~NNNN)?
- ContextTier: Present? Valid value (Critical/High/Medium/Low)?
- Depends: Present? Valid format (list or "None")?

**Count:** ___/7 fields present and valid

### Markdown Structure Issues

**Check each category (fill in during review):**

**Markdown Issue Checklist:**
- Heading hierarchy skips (H1 to H3): ___ (lines: ___)
- Mixed list markers (- and *): ___ (lines: ___)
- Unclosed code fences: ___ (lines: ___)
- Missing language tags: ___ (lines: ___)
- Malformed tables: ___ (lines: ___)
- Broken links: ___ (lines: ___)

**Total markdown issues:** ___

### Visual Formatting Issues

**Forbidden patterns (count each occurrence):**

**Visual Formatting Checklist:**
- ASCII art/diagrams: ___ (lines: ___)
- Arrow characters (-> => >): ___ (lines: ___)
- Box drawing (lines, corners): ___ (lines: ___)
- Unicode decorations: ___ (lines: ___)

**Total visual formatting issues:** ___

## Score Decision Matrix

**Score Tier Criteria:**
- **5/5 (15 pts):** 0 schema errors, 7/7 metadata, 0-2 markdown issues, 0 visual issues
- **4/5 (12 pts):** LOW schema errors only, 6-7/7 metadata, 3-4 markdown issues, 0-1 visual issues
- **3/5 (9 pts):** 1-2 MEDIUM schema errors, 5-6/7 metadata, 5-6 markdown issues, 2-3 visual issues
- **2/5 (6 pts):** 1-2 HIGH or 3+ MEDIUM schema errors, 3-4/7 metadata, 7-10 markdown issues, 4-5 visual issues
- **1/5 (3 pts):** 1+ CRITICAL schema errors, <3/7 metadata, 10+ markdown issues, 6+ visual issues

**Critical override:** Any CRITICAL schema error caps score at 2/5 (6 points)

## Schema Compliance Checklist

### Required Section Order (v3.2 schema)

Check order (mark sequence violations):

**Section Order Checklist:**
1. Title and preamble: Present? Correct order?
2. ## Metadata: Present? Correct order?
3. ## Scope: Present? Correct order?
4. ## References: Present? Correct order?
5. ## Contract: Present? Correct order?
6. Content sections: Present? Correct order?
7. Post-Execution Checklist: Present? Correct order?

**Sequence violations:** ___

## Fallback Scoring (Without Schema Validator)

If `schema_validator.py` is unavailable:

1. **Manual metadata check:**
   - Verify all 7 fields present
   - Check format compliance manually
   - Score metadata component only

2. **Manual structure check:**
   - Verify section order
   - Check heading hierarchy
   - Scan for visual formatting

3. **Document limitation:**
   ```markdown
   Note: Schema validation unavailable. Manual assessment performed.
   Recommend running: uv run python scripts/schema_validator.py [file]
   ```

4. **Scoring adjustment:**
   - Cap at 4/5 maximum without validator
   - Recommend manual schema check in review

## Markdown Structure Validation

### Heading Hierarchy

Must be properly nested (no skips):

```markdown
GOOD:
# Title (H1)
## Section (H2)
### Subsection (H3)
#### Detail (H4)

BAD (1 issue):
# Title (H1)
### Subsection (H3) -- Skipped H2!
```

### List Formatting

Use consistent markers:
```markdown
GOOD:
- Item 1
- Item 2
  - Nested item

BAD (1 issue):
- Item 1
* Item 2  -- Mixed markers
```

### Code Block Fencing

Must include language tag:
````markdown
GOOD:
```python
code here
```

BAD (1 issue):
```
code without language tag
```
````

### Table Formatting

Must have separator row:
```markdown
GOOD:
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |

BAD (1 issue):
| Column 1 | Column 2 |
| Value 1  | Value 2  |  -- Missing separator
```

## Visual Formatting Issues

### Forbidden Patterns

Agents cannot interpret these (count each occurrence):

**ASCII Art / Diagrams:**
```
FORBIDDEN (box diagrams):
    +----------+
    |  Start   |
    +----+-----+
         |
         v
```

**Arrow Characters:**
```
FORBIDDEN (unicode arrows):
Input -> Process -> Output (use text: "Input, then Process, then Output")
```

**Box Drawing:**
```
FORBIDDEN (unicode box drawing):
+===========+
|  Header   |
+===========+
```

### Acceptable Alternatives

```markdown
GOOD (text-based alternative):
Workflow:
1. Input
2. Process
3. Output

Or as list:
- Step 1: Input
- Step 2: Process
- Step 3: Output
```

## Worked Example

**Target:** Rule with parsability issues

### Step 1: Run Schema Validator

```bash
$ uv run python scripts/schema_validator.py rules/example.md

[HIGH] Missing metadata field: Depends (line 10)
[MEDIUM] Section order violation: Contract before References (line 45)
[LOW] Inconsistent list markers (line 78)
```

**Count:** 1 HIGH, 1 MEDIUM, 1 LOW

### Step 2: Check Metadata

**Metadata Assessment:**
- SchemaVersion: Yes, valid (v3.2)
- RuleVersion: Yes, valid (v1.0.0)
- LastUpdated: Yes, valid (2026-01-06)
- Keywords: Yes, valid (5 terms)
- TokenBudget: Yes, valid (~3500)
- ContextTier: Yes, valid (High)
- Depends: No - Missing

**Count:** 6/7 fields

### Step 3: Check Markdown Structure

**Issue Inventory:**
- Heading skips: 0
- Mixed list markers: 1 (line 78)
- Unclosed fences: 0
- Missing language tags: 2 (lines 90, 120)
- Malformed tables: 0

**Total:** 3 markdown issues

### Step 4: Check Visual Formatting

**Pattern Inventory:**
- ASCII art: 0
- Arrows: 1 (line 150: unicode arrow)
- Box drawing: 0

**Total:** 1 visual issue

### Step 5: Calculate Score

**Component Assessment:**
- Schema errors: 1 HIGH = 2/5 cap
- Metadata: 6/7 = 4/5 range
- Markdown: 3 issues = 4/5 range
- Visual: 1 issue = 4/5 range

**Final:** 2/5 (6 points) - HIGH schema error caps score

### Step 6: Document in Review

```markdown
## Parsability: 2/5 (6 points)

**Schema validation:**
- [HIGH] Missing Depends field (line 10) - CAPS SCORE
- [MEDIUM] Section order: Contract before References (line 45)
- [LOW] Mixed list markers (line 78)

**Metadata:** 6/7 fields
- Missing: Depends

**Markdown issues:** 3
- Mixed list markers (line 78)
- Missing language tags (lines 90, 120)

**Visual formatting:** 1
- Arrow character (line 150)

**Priority fixes:**
1. Add Depends field to metadata
2. Reorder: References before Contract
3. Add language tags to code blocks
```

## Inter-Run Consistency Target

**Expected variance:** 0 (schema errors are objective)

**Verification:**
- Run schema_validator.py (deterministic output)
- Count metadata fields against checklist
- Count markdown issues by category
- Count visual patterns by type

**If results differ between runs:**
- Schema validator version may differ
- Manual counting error - re-verify with checklists
