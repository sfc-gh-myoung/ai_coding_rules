# Parsability Rubric (15 points)

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

> **Why inventories are required:** Eliminates counting variance (same rule → same inventory → same score), prevents false negatives, provides auditable evidence, enables verification.

### Inventory Template

**Schema Validation Errors:**

| Line | Severity | Error Description |
|------|----------|-------------------|
| 10 | HIGH | Missing Depends field |
| 45 | MEDIUM | Section order violation |
| 78 | LOW | Inconsistent list markers |

**Metadata Field Checklist:**

| Field | Present? | Valid Format? | Notes |
|-------|----------|---------------|-------|
| SchemaVersion | Y/N | Y/N | Expected: v3.2 |
| RuleVersion | Y/N | Y/N | Expected: vX.Y.Z |
| LastUpdated | Y/N | Y/N | Expected: YYYY-MM-DD |
| Keywords | Y/N | Y/N | Expected: 3+ terms |
| TokenBudget | Y/N | Y/N | Expected: ~NNNN |
| ContextTier | Y/N | Y/N | Expected: Critical/High/Medium/Low |
| Depends | Y/N | Y/N | Expected: list or "None" |

**Markdown Issues:**

| Line | Issue Type | Description |
|------|------------|-------------|
| 45 | Heading skip | H1 to H3 |
| 90 | Missing lang tag | Code block |

**Visual Formatting Issues:**

| Line | Pattern Type | Description |
|------|--------------|-------------|
| 150 | Arrow | Unicode arrow character |

### Counting Protocol

> **Standard 5-Step Counting Protocol:**
> 1. **Create Empty Inventory** — Copy template above into working document. Do NOT start reading rule yet.
> 2. **Read Rule Systematically** — Start at line 1, read to END (no skipping). Record all matches with line numbers.
> 3. **Calculate Raw Totals** — Sum counts by category using dimension-specific definitions.
> 4. **Check Non-Issues List** — Review EACH flagged item against this dimension's Non-Issues section. Remove false positives with note. Recalculate totals.
> 5. **Look Up Score** — Use adjusted totals in Score Decision Matrix. Record score with inventory evidence.
>
> **Inter-run consistency:** Use inventory tables with line numbers for evidence. If variance exceeds threshold documented below, re-count using checklists and document ambiguous cases.
>
> **Dimension-specific:** Run schema validator in Step 2, check metadata fields, scan for markdown and visual formatting issues.

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 3
**Points:** Raw × (3/2) = Raw × 1.5

## Counting Definitions

### Schema Validation Errors

Run schema validator first:
```bash
uv run ai-rules validate [target_file]
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

If `ai-rules validate` is unavailable:

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
   Recommend running: uv run ai-rules validate [file]
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
$ uv run ai-rules validate rules/example.md

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
- Run ai-rules validate (deterministic output)
- Count metadata fields against checklist
- Count markdown issues by category
- Count visual patterns by type

**If results differ between runs:**
- Schema validator version may differ
- Manual counting error - re-verify with checklists

---

## Parsability for Project Files

**Applies to:** AGENTS.md, PROJECT.md

**When FILE_TYPE == "project":**

### What to Evaluate

**Evaluate ONLY:**
- ✓ Markdown structure (heading hierarchy, lists, code blocks)
- ✓ No visual formatting (ASCII art, arrows, box drawing)
- ✓ No broken external links
- ✓ Code blocks properly fenced with language tags
- ✓ Consistent list markers
- ✓ Tables properly formatted

**Do NOT evaluate:**
- ✗ Schema validation (different schema than rules)
- ✗ Metadata fields (SchemaVersion, RuleVersion, TokenBudget, etc.)
- ✗ Section order (Scope, Contract, References)
- ✗ Required rule sections

### Scoring for Project Files

**Start at 10/10 (15 points), deduct for markdown issues:**

| Issue Type | Deduction | Max Penalty |
|------------|-----------|-------------|
| Heading hierarchy skips | -1 point each | -3 points |
| Mixed list markers | -0.5 points each | -2 points |
| Unclosed code fences | -2 points each | -4 points |
| Missing language tags | -0.5 points each | -2 points |
| Malformed tables | -1 point each | -2 points |
| Broken external links | -1 point each | -3 points |
| Visual formatting (ASCII art, arrows) | -1 point each | -3 points |

**Score Ranges:**
- 10/10 (15 pts): Perfect markdown, no issues
- 9/10 (13.5 pts): 1-2 minor issues
- 8/10 (12 pts): 3-4 minor issues OR 1 major issue
- 7/10 (10.5 pts): 5-6 minor issues OR 2 major issues
- 6/10 (9 pts): 7-8 minor issues OR 3 major issues
- 5/10 (7.5 pts): 9-10 minor issues OR 4 major issues
- <5/10: Extensive markdown problems

**Major issues:** Unclosed code fences, extensive visual formatting
**Minor issues:** Missing language tags, mixed list markers

### Example: Project File Review

```markdown
## Parsability: 9/10 (13.5 points)

**File Type:** Project configuration (schema validation skipped)

**Schema Validation:** SKIPPED (project file)

**Rationale:** AGENTS.md is a bootstrap/configuration file with different structure than domain rules. Schema validation against rule schema is not applicable.

**Markdown Structure:** Excellent

**Issues Found:**
- Line 234: Code block missing language tag (bash)
- Line 456: Code block missing language tag (python)

**Strengths:**
- Proper heading hierarchy (no skips)
- Consistent list markers throughout
- All tables properly formatted
- No visual formatting issues
- No broken external links

**Priority fixes:**
1. Add language tags to code blocks (lines 234, 456)

**Expected Score Improvement:** +1 point (to 10/10, 15 points)
```

### Rationale for Different Treatment

**Why project files skip schema validation:**

1. **Different architectural role:**
   - Rule files: Domain-specific patterns, loaded on-demand
   - Project files: Bootstrap/configuration, loaded once at initialization

2. **Different metadata requirements:**
   - Rule files: Need SchemaVersion, RuleVersion, TokenBudget, ContextTier, Depends
   - Project files: No standardized metadata, custom structure per project needs

3. **Different section structure:**
   - Rule files: Scope → References → Contract → Content → Checklist
   - Project files: Custom sections optimized for onboarding (Overview, Commands, Workflows, etc.)

4. **Still valuable to review:**
   - Actionability for AI agents (critical)
   - Completeness of guidance (critical)
   - Consistency (important)
   - Markdown quality (important for parsing)
   - Token efficiency (helps agents)
   - Currency (tools and patterns)

**Project files ARE agent-executable documents** - they just follow a different schema than domain rules.

## Non-Issues (Do NOT Count)

**Review EACH flagged item against this list before counting.**

### Pattern 1: Intentional Code Block Without Language
**Pattern:** Code block without language tag showing generic output
**Example:** ``` block showing command output (not source code)
**Why NOT an issue:** Output blocks don't need language tags
**Action:** Remove from inventory with note "Output block, not source"

### Pattern 2: Markdown Tables with Alignment
**Pattern:** Table using alignment syntax (`:---`, `:---:`, `---:`)
**Example:** `| Header | Another |` with `|:---|---:|` separator
**Why NOT an issue:** Valid markdown table syntax
**Action:** Remove from inventory with note "Valid alignment syntax"

### Pattern 3: Inline Code for Commands
**Pattern:** Single backticks for inline commands
**Example:** `Run the \`validate\` command`
**Why NOT an issue:** Inline code is appropriate for short commands
**Action:** Remove from inventory with note "Inline code is appropriate"

### Pattern 4: Nested Lists with Mixed Indent
**Pattern:** Nested list items with varying indentation
**Example:** Some items at 2 spaces, some at 4 spaces
**Why NOT an issue:** Most markdown parsers handle this correctly
**Action:** Remove if consistent within nesting level
