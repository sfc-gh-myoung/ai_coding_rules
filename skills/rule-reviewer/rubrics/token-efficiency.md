# Token Efficiency Rubric (10 points)

## Scoring Criteria

### 5/5 (10 points): Excellent
- TokenBudget within ±5% of actual
- No redundant content
- Structured lists over prose
- Efficient examples
- References used instead of duplication

### 4/5 (8 points): Good
- TokenBudget within ±6-15% of actual
- Minimal redundancy (1-2 instances)
- Mostly structured format
- Examples appropriate

### 3/5 (6 points): Acceptable
- TokenBudget within ±16-25% of actual
- Some redundancy (3-5 instances)
- Mixed structure and prose
- Examples somewhat verbose

### 2/5 (4 points): Needs Work
- TokenBudget variance >±25%
- Significant redundancy (>5 instances)
- Heavy prose paragraphs
- Verbose examples

### 1/5 (2 points): Poor
- TokenBudget not declared OR variance >±50%
- Extensive duplication
- Inefficient structure throughout
- Bloated examples

## Token Budget Verification

Run token counter:
```bash
uv run python scripts/token_validator.py [target_file]
```

### Variance Calculation

```
Declared = TokenBudget from metadata (e.g., ~5250)
Actual = Output from token_validator.py
Variance = |Actual - Declared| / Declared × 100%

Examples:
  Declared: 5250, Actual: 5450 → Variance: 3.8% → 5/5 score
  Declared: 5250, Actual: 6000 → Variance: 14.3% → 4/5 score
  Declared: 5250, Actual: 6800 → Variance: 29.5% → 2/5 score
```

### Scoring by Variance

| Variance | Score | Notes |
|----------|-------|-------|
| ±0-5% | 5/5 (10 pts) | Excellent accuracy |
| ±6-15% | 4/5 (8 pts) | Acceptable per spec |
| ±16-25% | 3/5 (6 pts) | Beyond target range |
| ±26-40% | 2/5 (4 pts) | Significant error |
| >±40% | 1/5 (2 pts) | Major inaccuracy |
| Not declared | 1/5 (2 pts) | Missing required metadata |

## Redundancy Analysis

### Pattern 1: Repeated Definitions

**Example (inefficient):**
```markdown
Line 36: **Large table:** >10M rows OR >5GB uncompressed OR ...
Line 86: **Large table:** >10M rows OR >5GB uncompressed OR ... [DUPLICATE]
Line 101: **Large table:** >10M rows OR >5GB uncompressed OR ... [DUPLICATE]
Line 150: **Large table:** >10M rows OR >5GB uncompressed OR ... [DUPLICATE]

Token cost: 28 tokens × 4 occurrences = 112 tokens
Waste: 28 tokens × 3 duplicates = 84 tokens wasted
```

**Efficient alternative:**
```markdown
Line 36: **Large table:** >10M rows OR >5GB uncompressed OR ... [DEFINE ONCE]
Line 86: Use Streams for large tables (see "Large table" in Quantification Standards)
Line 101: For large tables (see definition), design incremental pattern...
Line 150: Apply to large tables (see Quantification Standards)...

Token cost: 28 + (8 × 3) = 52 tokens
Savings: 60 tokens (54% reduction)
```

### Pattern 2: Verbose Examples

**Example (inefficient):**
```markdown
Here is an example of how to use this pattern. First, you need to create
a connection to the database. Then, you should validate the input data
to ensure it meets the requirements. After validation completes successfully,
proceed with processing the data. Finally, write the results to the output
location and verify they were written correctly.
```
Token cost: ~70 tokens

**Efficient alternative:**
```markdown
Example workflow:
1. Create database connection
2. Validate input data
3. Process data
4. Write results
5. Verify output
```
Token cost: ~20 tokens
Savings: 50 tokens (71% reduction)

### Pattern 3: Prose vs Structured Lists

**Inefficient (prose):**
```markdown
The validation step should check several things. First, it should verify
that the input file exists and is readable. Second, it needs to confirm
that the required columns are present in the expected format. Third, the
data types should be validated to ensure compatibility. Fourth, any
business rules should be applied to check for invalid combinations.
Finally, a summary report should be generated showing the validation results.
```
Token cost: ~85 tokens

**Efficient (structured):**
```markdown
Validation checks:
- File exists and readable
- Required columns present in expected format
- Data types compatible
- Business rules satisfied
- Generate summary report
```
Token cost: ~25 tokens
Savings: 60 tokens (71% reduction)

## Efficiency Best Practices

### 1. Front-Load Critical Information

Place most important content early:
```markdown
✅ GOOD:
## Quick Start

Run: `uv run python script.py --input data.csv`

Required: Python 3.11+, uv installed

[Details follow...]

❌ BAD:
## Background

Python is a programming language... [500 tokens of history]

## Installation

First, understand the architecture... [300 tokens]

## Usage

Eventually gets to: Run `uv run python script.py`
```

### 2. Use References Over Duplication

```markdown
✅ GOOD:
Section A: [Full explanation of concept X - 200 tokens]
Section B: For concept X details, see Section A
Section C: Concept X (see Section A) applies here

❌ BAD:
Section A: [Full explanation - 200 tokens]
Section B: [Same explanation - 200 tokens]
Section C: [Same explanation again - 200 tokens]
Total waste: 400 tokens
```

### 3. Progressive Disclosure

Split large rules into focused files:
```markdown
✅ GOOD (Main file ~3000 tokens):
## Core Patterns
[Essential content]

For advanced patterns, see: advanced/README.md
For troubleshooting, see: troubleshooting/README.md

❌ BAD (Single file ~9000 tokens):
## Core Patterns
[Essential content]

## Advanced Patterns
[Rarely-needed content loaded every time]

## Troubleshooting
[Edge cases loaded every time]
```

## Scoring Formula

```
Step 1: Calculate token budget variance
  ±0-5%: 5/5 (10 points)
  ±6-15%: 4/5 (8 points)
  ±16-25%: 3/5 (6 points)
  ±26-40%: 2/5 (4 points)
  >±40% or missing: 1/5 (2 points)

Step 2: Identify redundancy instances
  Count:
  - Repeated definitions (>2 occurrences)
  - Duplicate examples
  - Verbose prose where lists would work

Step 3: Calculate final score
  Start with variance score
  Deduct for redundancy:
    - Minor (1-2 instances): -0 points
    - Moderate (3-5 instances): -1 point
    - Significant (6-10 instances): -2 points
    - Extensive (>10 instances): -3 points

Minimum score: 1/5 (2 points)
```

## Common Efficiency Issues

### Issue 1: No TokenBudget Declared

**Impact:** Cannot assess accuracy
**Recommendation:** Add to metadata: `**TokenBudget:** ~NNNN`

### Issue 2: Repeated Threshold Definitions

**Impact:** Major token waste (50-200+ tokens)
**Recommendation:** Define once, reference elsewhere

### Issue 3: Verbose Anti-Pattern Examples

**Impact:** Medium token waste (100-300 tokens)
**Recommendation:** Use table format or consolidated structure

### Issue 4: Extensive Prose Paragraphs

**Impact:** 30-70% token overhead vs structured lists
**Recommendation:** Convert to bulleted lists with headers
