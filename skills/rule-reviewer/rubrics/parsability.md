# Parsability Rubric (15 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 3
**Points:** Raw × (3/2) = Raw × 1.5

## Scoring Criteria

### 10/10 (15 points): Perfect
- Schema validation: 0 errors
- All 7 metadata fields present and correct
- Markdown structure valid (proper heading hierarchy)
- 0 visual formatting issues (no ASCII art, arrows, box drawing)

### 9/10 (13.5 points): Near-Perfect
- Schema validation: 0 errors
- All 7 metadata fields present
- 1 minor markdown issue
- 0 visual formatting issues

### 8/10 (12 points): Excellent
- Schema validation: 1 LOW severity issue
- 7/7 metadata fields present
- 2 minor markdown issues
- 0 visual formatting issues

### 7/10 (10.5 points): Good
- Schema validation: 2 LOW severity issues
- 6-7 metadata fields present
- 3 markdown issues
- 0-1 visual formatting issues

### 6/10 (9 points): Acceptable
- Schema validation: 1 MEDIUM error
- 6/7 metadata fields present
- 4 markdown issues
- 1 visual formatting issue

### 5/10 (7.5 points): Borderline
- Schema validation: 2 MEDIUM errors
- 5-6 metadata fields present
- 5 markdown issues
- 2 visual formatting issues

### 4/10 (6 points): Needs Work
- Schema validation: 1 HIGH error OR 3 MEDIUM
- 4-5 metadata fields present
- 6-7 markdown issues
- 3 visual formatting issues

### 3/10 (4.5 points): Poor
- Schema validation: 2 HIGH errors
- 3-4 metadata fields present
- 8-9 markdown issues
- 4 visual formatting issues

### 2/10 (3 points): Very Poor
- Schema validation: 3+ HIGH errors
- 2-3 metadata fields present
- 10+ markdown issues
- 5+ visual formatting issues

### 1/10 (1.5 points): Inadequate
- Schema validation: 1 CRITICAL error
- 1-2 metadata fields present
- Malformed markdown
- Extensive visual formatting

### 0/10 (0 points): Not Parsable
- Schema validation: Multiple CRITICAL errors
- Metadata missing or invalid
- Cannot be parsed by agents

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
- **10/10 (15 pts):** 0 schema errors, 7/7 metadata, 0 markdown issues, 0 visual issues
- **9/10 (13.5 pts):** 0 schema errors, 7/7 metadata, 1 markdown issue, 0 visual issues
- **8/10 (12 pts):** 1 LOW schema error, 7/7 metadata, 2 markdown issues, 0 visual issues
- **7/10 (10.5 pts):** 2 LOW schema errors, 6-7/7 metadata, 3 markdown issues, 0-1 visual issues
- **6/10 (9 pts):** 1 MEDIUM schema error, 6/7 metadata, 4 markdown issues, 1 visual issue
- **5/10 (7.5 pts):** 2 MEDIUM schema errors, 5-6/7 metadata, 5 markdown issues, 2 visual issues
- **4/10 (6 pts):** 1 HIGH or 3 MEDIUM schema errors, 4-5/7 metadata, 6-7 markdown issues, 3 visual issues
- **3/10 (4.5 pts):** 2 HIGH schema errors, 3-4/7 metadata, 8-9 markdown issues, 4 visual issues
- **2/10 (3 pts):** 3+ HIGH schema errors, 2-3/7 metadata, 10+ markdown issues, 5+ visual issues
- **1/10 (1.5 pts):** 1 CRITICAL schema error, 1-2/7 metadata, malformed markdown, extensive visual
- **0/10 (0 pts):** Multiple CRITICAL errors, metadata invalid, not parsable

**Critical override:** Any CRITICAL schema error caps score at 2/10 (3 points)

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
- **Value 1** - Value 2

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

**Final:** 4/10 (6 points) - HIGH schema error caps score

### Step 6: Document in Review

```markdown
## Parsability: 4/10 (6 points)

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
