# Token Efficiency Rubric

> **STATUS: INFORMATIONAL ONLY - NOT SCORED**
>
> As of Scoring Rubric v2.0, Token Efficiency has been **merged into Rule Size** and is no longer a scored dimension. This rubric is retained for:
> - Historical reference
> - Informational reporting in reviews
> - Guidance on reducing line count
>
> **Findings from this rubric appear in the recommendations section, not in the score.**

---

## Redundancy Analysis (Informational)

When reviewing rules, note redundancy issues to inform Rule Size recommendations:

| Redundancy Count | Recommendation |
|------------------|----------------|
| 0 instances | No action needed |
| 1-2 instances | Note in recommendations |
| 3+ instances | Prioritize in remediation |

---

## Original Rubric (Historical Reference)

The following content is preserved for historical reference and to guide redundancy analysis.

---

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

### Why This Is Required

- **Eliminates counting variance:** Same rule → same inventory → same score
- **Prevents false negatives:** Systematic tracking catches all redundancies
- **Provides evidence:** Inventory shows exactly what was measured
- **Enables verification:** Users can audit scoring decisions

### Inventory Template

**Token Budget Check:**

| Metric | Value |
|--------|-------|
| Declared budget | ~NNNN |
| Actual tokens | NNNN |
| Variance | N.N% |
| Variance tier | X/5 |

**Redundancy Instances:**

| First Occurrence | Repeated At | Content (first 30 chars) | Word Count |
|------------------|-------------|--------------------------|------------|
| Line 36 | Line 86 | "Large table: >10M rows..." | 28 |
| Line 100 | Line 200 | "Error handling example..." | 45 |

**Structure Assessment:**

| Metric | Count |
|--------|-------|
| Total content lines | NNN |
| Structured lines (lists, tables, code) | NNN |
| Prose lines | NNN |
| Structure ratio | NN% |

### Counting Protocol (5 Steps)

**Step 1: Create Empty Inventory**
- Copy templates above into working document
- Do NOT start reading rule yet

**Step 2: Run Token Validator (if available)**
- Execute: `uv run ai-rules tokens [target_file]`
- Record declared, actual, and variance
- If unavailable: Estimate using formula (Words × 1.3 + Code lines × 4)

**Step 3: Read Rule Systematically**
- Start at line 1, read to END (no skipping)
- Track each definition/example with line number
- Note any repetitions in Redundancy table
- Count structured vs prose lines

**Step 4: Check Non-Issues List**
- Review EACH flagged redundancy
- Check against "Non-Issues" section below
- Remove intentional repetitions (marked as such)
- Recalculate totals

**Step 5: Look Up Score**
- Use adjusted totals in Score Decision Matrix
- Record score with inventory evidence

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 2
**Points:** Raw × (2/2) = Raw × 1.0

## Scoring Criteria

### 10/10 (10 points): Perfect
- TokenBudget variance: ≤3%
- 0 redundancy instances
- 95%+ structured format (lists over prose)
- References used instead of duplication

### 9/10 (9 points): Near-Perfect
- TokenBudget variance: 4-5%
- 0-1 redundancy instances
- 93-94% structured format

### 8/10 (8 points): Excellent
- TokenBudget variance: 6-7%
- 1-2 redundancy instances
- 90-92% structured format

### 7/10 (7 points): Good
- TokenBudget variance: 8-10%
- 2-3 redundancy instances
- 85-89% structured format

### 6/10 (6 points): Acceptable
- TokenBudget variance: 11-15%
- 3-4 redundancy instances
- 80-84% structured format

### 5/10 (5 points): Borderline
- TokenBudget variance: 16-20%
- 4-5 redundancy instances
- 70-79% structured format

### 4/10 (4 points): Needs Work
- TokenBudget variance: 21-30%
- 5-6 redundancy instances
- 60-69% structured format

### 3/10 (3 points): Poor
- TokenBudget variance: 31-40%
- 7-8 redundancy instances
- 50-59% structured format

### 2/10 (2 points): Very Poor
- TokenBudget variance: 41-50%
- 9-10 redundancy instances
- 40-49% structured format

### 1/10 (1 point): Inadequate
- TokenBudget variance: >50%
- >10 redundancy instances
- 30-39% structured format

### 0/10 (0 points): Not Token Efficient
- TokenBudget not declared
- Pervasive redundancy
- <30% structured format

## Counting Definitions

### Token Budget Variance

**Step 1:** Get declared budget from metadata
```
TokenBudget: ~5250  (Declared = 5250)
```

**Step 2:** Run token counter
```bash
uv run ai-rules tokens [target_file]
```

**Step 3:** Calculate variance
```
Variance = |Actual - Declared| / Declared × 100%

Example:
  Declared: 5250
  Actual: 5450
  Variance: |5450 - 5250| / 5250 × 100% = 3.8%
```

**Variance bands (mutually exclusive):**
- 0-5% variance: 5/5 eligible
- 6-10% variance: 4/5 maximum
- 11-20% variance: 3/5 maximum
- 21-40% variance: 2/5 maximum
- >40% variance: 1/5 maximum
- Not declared: 1/5 maximum

### Redundancy Instances

**Definition:** Same content repeated without reference.

**Count as 1 redundancy:**
- Definition repeated verbatim (>10 words)
- Example repeated with same code
- Concept explained twice without cross-reference

**NOT redundancy (do not count):**
- Intentional repetition for emphasis (marked as such)
- Summary that references detailed section
- Brief re-statement with "see X for details"

**Redundancy Inventory (fill in during review):**
- "Large table: >10M rows...": First at line 36, repeated at line 86 (28 words)
- Error handling example: First at line 100, repeated at line 200 (45 words)

**Count:** Total redundancy instances

### Structured Format Ratio

**Definition:** Percentage of content in structured vs prose format.

**Structured formats:**
- Bulleted lists
- Numbered lists
- Tables
- Code blocks
- Definition lists

**Prose format:**
- Paragraphs >3 sentences
- Flowing text without structure

**Calculation:**
```
Structured % = (structured lines / total content lines) × 100
```

**Quick estimation method:**
1. Count total content lines (excluding headers, blank lines)
2. Count lines in lists, tables, code blocks
3. Calculate ratio

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (10 pts):** ≤3% variance, 0 redundancy instances, 95%+ structured format
- **9/10 (9 pts):** 4-5% variance, 0-1 redundancy instances, 93-94% structured format
- **8/10 (8 pts):** 6-7% variance, 1-2 redundancy instances, 90-92% structured format
- **7/10 (7 pts):** 8-10% variance, 2-3 redundancy instances, 85-89% structured format
- **6/10 (6 pts):** 11-15% variance, 3-4 redundancy instances, 80-84% structured format
- **5/10 (5 pts):** 16-20% variance, 4-5 redundancy instances, 70-79% structured format
- **4/10 (4 pts):** 21-30% variance, 5-6 redundancy instances, 60-69% structured format
- **3/10 (3 pts):** 31-40% variance, 7-8 redundancy instances, 50-59% structured format
- **2/10 (2 pts):** 41-50% variance, 9-10 redundancy instances, 40-49% structured format
- **1/10 (1 pt):** >50% variance, >10 redundancy instances, 30-39% structured format
- **0/10 (0 pts):** Not declared, pervasive redundancy, <30% structured format

**Primary determinant:** Token variance (overrides other factors if in lower tier)

## Token Budget Verification

### With Validator Tool

```bash
uv run ai-rules tokens rules/example.md

Output:
  Declared: 5250 tokens
  Actual: 5450 tokens
  Variance: 3.8%
  Status: PASS (within ±5%)
```

### Without Validator Tool (Fallback)

Estimate tokens manually:
```
Approximate formula:
  Tokens ≈ Words × 1.3 + Code lines × 4

Example:
  2000 words × 1.3 = 2600
  200 code lines × 4 = 800
  Estimated tokens = 3400
```

**Document limitation:**
```markdown
Note: Token validator unavailable. Manual estimate used.
Recommend running: uv run ai-rules tokens [file]
```

## Redundancy Analysis

### Pattern 1: Repeated Definitions

**Inefficient (1 redundancy):**
```markdown
Line 36: **Large table:** >10M rows OR >5GB uncompressed OR ...
Line 86: **Large table:** >10M rows OR >5GB uncompressed OR ... [DUPLICATE]
```

**Efficient (0 redundancy):**
```markdown
Line 36: **Large table:** >10M rows OR >5GB (see Quantification Standards)
Line 86: For large tables (see definition above), use Streams...
```

### Pattern 2: Repeated Examples

**Inefficient (1 redundancy):**
```markdown
Line 100: [45-line error handling example]
Line 200: [Same 45-line example repeated]
```

**Efficient (0 redundancy):**
```markdown
Line 100: [45-line error handling example]
Line 200: Apply error handling pattern (see Line 100 example)
```

### Pattern 3: Verbose Prose

**Inefficient:**
```markdown
Here is an example of how to use this pattern. First, you need to create
a connection to the database. Then, you should validate the input data
to ensure it meets the requirements. After validation completes successfully,
proceed with processing the data.
```
Token cost: ~70 tokens

**Efficient:**
```markdown
Example workflow:
1. Create database connection
2. Validate input data
3. Process data
```
Token cost: ~20 tokens
Savings: 50 tokens (71% reduction)

## Structured Format Examples

### Inefficient (Prose)

```markdown
The validation step should check several things. First, it should verify
that the input file exists and is readable. Second, it needs to confirm
that the required columns are present in the expected format. Third, the
data types should be validated to ensure compatibility.
```
~85 tokens, ~30% structured

### Efficient (Structured)

```markdown
Validation checks:
- File exists and readable
- Required columns present
- Data types compatible
- Business rules satisfied
```
~25 tokens, 100% structured
Savings: 60 tokens (71% reduction)

## Worked Example

**Target:** Rule with efficiency issues

### Step 1: Check Token Budget

```bash
$ uv run ai-rules tokens rules/example.md

Declared: 5250 tokens
Actual: 6800 tokens
Variance: 29.5%
```

**Variance:** 29.5% = 2/5 cap

### Step 2: Count Redundancies

**Redundancy Inventory:**
- Large table definition: First L36, repeated L86, L150 (28×3 words)
- Error example: First L100, repeated L200 (45 words)
- Mandate text: First L50, repeated L180 (20 words)

**Count:** 4 redundancy instances (L86, L150, L200, L180)

### Step 3: Assess Structure

```
Total content lines: 200
Structured lines: 120 (lists, tables, code)
Prose lines: 80

Structure ratio: 120/200 = 60%
```

### Step 4: Calculate Score

**Component Assessment:**
- Variance: 29.5% = 2/5 cap
- Redundancy: 4 instances = 3/5
- Structure: 60% = 3/5

**Final:** 4/10 (4 points) - variance is primary determinant

### Step 5: Document in Review

```markdown
## Token Efficiency: 4/10 (4 points)

**Token budget:**
- Declared: ~5250
- Actual: 6800
- Variance: 29.5% (exceeds ±20% threshold)

**Redundancy instances:** 4
- Large table definition repeated (lines 36, 86, 150)
- Error handling example duplicated (lines 100, 200)
- Mandate text repeated (lines 50, 180)

**Structure ratio:** 60% structured

**Estimated savings:**
- Remove redundancies: ~300 tokens
- Convert prose to lists: ~200 tokens
- Potential reduction: ~500 tokens (7.4%)

**Priority fixes:**
1. Define "large table" once, reference elsewhere
2. Consolidate error examples
3. Update TokenBudget after fixes
```

## Efficiency Best Practices

### 1. Front-Load Critical Information

Place most important content early:
```markdown
GOOD:
## Quick Start
Run: `uv run python script.py`
Required: Python 3.11+, uv installed

BAD:
## Background
Python is a programming language... [500 tokens of history]
...eventually gets to usage
```

### 2. Use References Over Duplication

```markdown
GOOD:
Section A: [Full explanation - 200 tokens]
Section B: For details, see Section A

BAD:
Section A: [Full explanation - 200 tokens]
Section B: [Same explanation - 200 tokens]
```

### 3. Progressive Disclosure

Split large rules into focused files:
```markdown
GOOD:
Core patterns: [Essential content]
For advanced patterns: see advanced/README.md

BAD:
[9000 tokens including rarely-needed advanced content]
```

## Inter-Run Consistency Target

**Expected variance:** 0% for token count (objective measurement)

**Redundancy count variance:** ±1 instance

**Verification:**
- Token count: Use validator tool (deterministic)
- Redundancy: Use tracking table with line numbers
- Structure: Use line counting method

**If results differ:**
- Token validator version may differ
- Redundancy counting method inconsistent - use table

---

## Token Efficiency for Project Files

**Applies to:** AGENTS.md, PROJECT.md

**When FILE_TYPE == "project":**

### What to Evaluate

**Evaluate (same as rules):**
- ✓ Redundancy instances (repeated definitions, duplicated examples)
- ✓ Structured format ratio (lists/tables vs prose)
- ✓ Use of references over duplication
- ✓ Front-loaded critical information
- ✓ Progressive disclosure patterns

**Skip:**
- ✗ TokenBudget variance (no declared budget to compare against)

**Report:** Actual token count for reference (not scored)

### Scoring for Project Files

**Since no TokenBudget is declared, score based on:**

**Primary Factor: Redundancy Instances**

| Redundancy Count | Raw Score | Points |
|------------------|-----------|--------|
| 0 instances | 10/10 | 10 |
| 1-2 instances | 8/10 | 8 |
| 3-4 instances | 6/10 | 6 |
| 5-6 instances | 4/10 | 4 |
| 7-8 instances | 2/10 | 2 |
| 9+ instances | 0/10 | 0 |

**Secondary Factor: Structured Format Ratio**

Apply adjustments to redundancy-based score:

| Structure Ratio | Adjustment |
|-----------------|------------|
| 95%+ structured | +0 points (no penalty) |
| 80-94% structured | -1 point |
| 60-79% structured | -2 points |
| <60% structured | -3 points |

**Minimum score:** 0/10 (cannot go below 0)

### Example: Project File Scoring

**File:** PROJECT.md

**Step 1: Count Redundancy**
- Tool installation repeated (lines 39, 114) - 1 instance
- Validation command repeated (lines 356, 380) - 1 instance
- Total: 2 redundancy instances = 8/10 base score

**Step 2: Assess Structure**
- Total content lines: 450
- Structured lines (lists, tables, code): 395
- Structure ratio: 395/450 = 87.8%
- Adjustment: -1 point (80-94% range)

**Step 3: Calculate Final Score**
- Base: 8/10
- Structure penalty: -1
- Final: 7/10 (7 points)

**Step 4: Report Actual Tokens**
```bash
# For reference only (not scored)
Token count: ~4800 tokens
```

**Step 5: Document in Review**

```markdown
## Token Efficiency: 7/10 (7 points)

**File Type:** Project configuration (TokenBudget not declared)

**Redundancy instances:** 2
- Tool installation command repeated (lines 39, 114)
- Validation command repeated (lines 356, 380)

**Structure ratio:** 87.8% structured (395/450 lines)

**Actual token count:** ~4800 tokens (reference only - not scored)

**Rationale:** Without declared TokenBudget, score based on redundancy (primary) and structure (secondary). Two redundancy instances = 8/10 base, structure 80-94% = -1 adjustment, final 7/10.

**Strengths:**
- High use of bulleted lists and code blocks
- Good progressive disclosure (commands → workflows → troubleshooting)
- Front-loads critical validation requirements

**Recommendations:**
1. Consolidate tool installation to single section (lines 39, 114)
2. Create shared "Validation Commands" section referenced from multiple locations
3. Expected improvement: +1 point (to 8/10, 8 points)

**Note:** Project files don't declare TokenBudget as they are loaded once during initialization, not accumulated with rules in agent context windows.
```

### Why TokenBudget Variance Doesn't Apply

**Rule files:**
- Loaded together in agent context (accumulation)
- TokenBudget helps track cumulative context window usage
- Variance check ensures declared budget is accurate
- Formula: `|Actual - Declared| / Declared × 100%`

**Project files:**
- Loaded once during initialization (standalone)
- Not accumulated with other files
- No TokenBudget declared (expected)
- Token count reported for reference only

**Both file types still benefit from:**
- Minimizing redundancy
- Maximizing structure over prose
- Using references over duplication
- Front-loading critical information

### Token Count Reporting (Optional)

If token counter available, report actual count:

```bash
uv run ai-rules tokens [target_file]
```

Include in review for reference:
```markdown
**Actual token count:** ~4800 tokens (reference only)
```

This helps project maintainers understand document size without scoring against a declared budget.

## Non-Issues (Do NOT Count as Redundancy)

**Review EACH flagged item against this list before counting.**

### Pattern 1: Intentional Repetition for Emphasis
**Pattern:** Content repeated with explicit "reminder" or "important" marker
**Example:** "IMPORTANT: As noted above, always validate inputs"
**Why NOT an issue:** Intentional emphasis for critical information
**Action:** Remove from inventory with note "Intentional emphasis"

### Pattern 2: Summary That References
**Pattern:** Summary section that references detailed section
**Example:** "Overview: Use clustering (see Clustering Details section)"
**Why NOT an issue:** Summary provides navigation, not duplication
**Action:** Remove from inventory with note "Summary with reference"

### Pattern 3: Template Sections
**Pattern:** Repeated structure in template/example sections
**Example:** Multiple "## Example N" sections with similar structure
**Why NOT an issue:** Templates intentionally show repeated patterns
**Action:** Remove from inventory with note "Template structure"

### Pattern 4: Progressive Disclosure
**Pattern:** Brief mention followed by detailed section
**Example:** "Configure timeouts (detailed in Configuration section)"
**Why NOT an issue:** Progressive disclosure is good practice
**Action:** Remove from inventory with note "Progressive disclosure"
