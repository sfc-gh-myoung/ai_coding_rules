# Token Efficiency Rubric (10 points)

## Scoring Criteria

### 5/5 (10 points): Excellent
- TokenBudget variance: ≤5%
- 0-1 redundancy instances
- 90%+ structured format (lists over prose)
- References used instead of duplication

### 4/5 (8 points): Good
- TokenBudget variance: 6-10%
- 2-3 redundancy instances
- 80-89% structured format

### 3/5 (6 points): Acceptable
- TokenBudget variance: 11-20%
- 4-6 redundancy instances
- 60-79% structured format

### 2/5 (4 points): Needs Work
- TokenBudget variance: 21-40%
- 7-10 redundancy instances
- 40-59% structured format

### 1/5 (2 points): Poor
- TokenBudget variance: >40% OR not declared
- >10 redundancy instances
- <40% structured format

## Counting Definitions

### Token Budget Variance

**Step 1:** Get declared budget from metadata
```
TokenBudget: ~5250  (Declared = 5250)
```

**Step 2:** Run token counter
```bash
uv run python scripts/token_validator.py [target_file]
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
- **5/5 (10 pts):** ≤5% variance, 0-1 redundancy instances, 90%+ structured format
- **4/5 (8 pts):** 6-10% variance, 2-3 redundancy instances, 80-89% structured format
- **3/5 (6 pts):** 11-20% variance, 4-6 redundancy instances, 60-79% structured format
- **2/5 (4 pts):** 21-40% variance, 7-10 redundancy instances, 40-59% structured format
- **1/5 (2 pts):** >40% variance, >10 redundancy instances, <40% structured format

**Primary determinant:** Token variance (overrides other factors if in lower tier)

## Token Budget Verification

### With Validator Tool

```bash
uv run python scripts/token_validator.py rules/example.md

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
Recommend running: uv run python scripts/token_validator.py [file]
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
$ uv run python scripts/token_validator.py rules/example.md

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

**Final:** 2/5 (4 points) - variance is primary determinant

### Step 5: Document in Review

```markdown
## Token Efficiency: 2/5 (4 points)

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
