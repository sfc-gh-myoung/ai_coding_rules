# Actionability Rubric (25 points)

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

### Why This Is Required

- **Eliminates counting variance:** Same rule → same inventory → same score
- **Prevents false negatives:** Line-by-line enumeration catches all matches
- **Provides evidence:** Inventory shows exactly what was counted
- **Enables verification:** Users can audit scoring decisions

### Inventory Template

| Line | Quote (first 50 chars) | Issue Type | Category | Count |
|------|------------------------|------------|----------|-------|
| 45 | "Use appropriate timeout..." | Undefined threshold | Actionability | 1 |
| 67 | "If error occurs" (no else) | Missing branch | Actionability | 1 |
| 89 | "Consider adding indexes..." | Ambiguous action | Actionability | 1 |
| 150 | "should be verified" | Passive voice | Actionability | 0.5 |

### Counting Protocol (5 Steps)

**Step 1: Create Empty Inventory**
- Copy template above into working document
- Do NOT start reading rule yet

**Step 2: Read Rule Systematically**
- Start at line 1, read to END (no skipping)
- For EACH potential issue: Add row with line number
- Record ALL matches (filter false positives later)

**Step 3: Calculate Raw Totals**
- Sum counts by category (undefined thresholds, missing branches, ambiguous actions, passive voice)
- This is your RAW count (before filtering)

**Step 4: Check Non-Issues List**
- Review EACH flagged item in inventory
- Check against "Non-Issues" section below
- Remove false positives with note
- Recalculate totals

**Step 5: Look Up Score**
- Use adjusted totals in Score Decision Matrix
- Record score with inventory evidence

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 5
**Points:** Raw × (5/2) = Raw × 2.5

## Scoring Criteria

### 10/10 (25 points): Perfect
- 0 blocking issues
- All conditionals have explicit branches (if X then Y; else Z)
- All actions use imperative voice
- Quantified examples for all ambiguous terms

### 9/10 (22.5 points): Near-Perfect
- 1 blocking issue
- 99%+ conditionals have explicit branches
- 99%+ imperative voice

### 8/10 (20 points): Excellent
- 2-3 blocking issues
- 97-98% conditionals have explicit branches
- 97-98% imperative voice

### 7/10 (17.5 points): Good
- 4-5 blocking issues
- 95-96% conditionals have explicit branches
- 95-96% imperative voice

### 6/10 (15 points): Acceptable
- 6-7 blocking issues
- 90-94% conditionals have explicit branches
- 90-94% imperative voice

### 5/10 (12.5 points): Borderline
- 8-9 blocking issues
- 85-89% conditionals have explicit branches
- 85-89% imperative voice

### 4/10 (10 points): Needs Work
- 10-11 blocking issues
- 80-84% conditionals have explicit branches
- 80-84% imperative voice

### 3/10 (7.5 points): Poor
- 12-14 blocking issues
- 70-79% conditionals have explicit branches
- 70-79% imperative voice

### 2/10 (5 points): Very Poor
- 15-17 blocking issues
- 60-69% conditionals have explicit branches
- 60-69% imperative voice

### 1/10 (2.5 points): Inadequate
- 18-20 blocking issues
- 50-59% conditionals have explicit branches
- 50-59% imperative voice

### 0/10 (0 points): Not Actionable
- >20 blocking issues
- <50% conditionals have explicit branches
- Agent cannot execute without judgment calls

## Counting Definitions

### What Counts as ONE Blocking Issue

**Undefined Thresholds (1 issue each):**
- Single subjective term: "large", "significant", "appropriate" = 1 issue each
- Compound phrase: "large and significant" = 2 issues (count each term)
- Partial definition: Defines some cases but not all = 0.5 issue

**Missing Conditional Branches (1 issue each):**
- `if X` without explicit else/default = 1 issue
- `when X` without alternative = 1 issue
- Multiple missing branches in same block = count each

**Ambiguous Actions (1 issue each):**
- "Consider X" = 1 issue
- "You may want to X" = 1 issue
- "Optionally X" without criteria = 1 issue
- "Ensure X" without how = 1 issue
- "Make sure X" without command = 1 issue

**Passive Voice (0.5 issue each):**
- "Should be validated" = 0.5 issue
- "May be configured" = 0.5 issue
- Cap at 5 issues total for passive voice

### Counting Compound Phrases

**Examples:**
- "configure the database": 0 issues (imperative, specific)
- "configure appropriately": 1 issue ("appropriately" undefined)
- "configure if necessary": 1 issue ("if necessary" ambiguous)
- "configure appropriately if needed": 2 issues ("appropriately" + "if needed")
- "Use appropriate timeout for large tables": 2 issues ("appropriate" + "large")

## Score Decision Matrix

**Blocking Issues to Score:**
- 0 issues: 10/10 (25 pts) - No agent judgment required
- 1 issue: 9/10 (22.5 pts) - Near-perfect
- 2-3 issues: 8/10 (20 pts) - Excellent
- 4-5 issues: 7/10 (17.5 pts) - Minor refinements needed
- 6-7 issues: 6/10 (15 pts) - Several clarifications needed
- 8-9 issues: 5/10 (12.5 pts) - Borderline
- 10-11 issues: 4/10 (10 pts) - Needs work
- 12-14 issues: 3/10 (7.5 pts) - Poor
- 15-17 issues: 2/10 (5 pts) - Very poor
- 18-20 issues: 1/10 (2.5 pts) - Inadequate
- >20 issues: 0/10 (0 pts) - Not actionable

**Critical Override:**
- If blocking issues ≥10: Cap overall rule score at 60/100 regardless of other dimensions

## Undefined Threshold Patterns

Search for these patterns (each occurrence = 1 blocking issue):

**Size/Volume:**
- "large", "small", "big", "huge", "tiny"
- "many", "few", "several", "multiple"
- "high volume", "low volume"

**Complexity:**
- "complex", "simple", "complicated", "straightforward"
- "difficult", "easy", "trivial"

**Quality:**
- "significant", "minor", "major"
- "important", "critical", "essential"
- "appropriate", "suitable", "reasonable"

**Performance:**
- "fast", "slow", "quick"
- "efficient", "inefficient"
- "responsive", "laggy"

## Quantification Examples

**Vague Term Replacements:**
- "large file": >10MB OR >10000 lines
- "significant changes": >100 lines modified OR >10 files changed
- "complex function": >50 lines OR >5 branches OR cyclomatic complexity >10
- "many requests": >1000 requests/minute
- "high error rate": >5% of requests fail OR >100 errors/hour
- "slow query": >5 seconds execution time
- "frequent updates": >10 updates/day OR >100 updates/month

## Conditional Branch Completeness

**Incomplete (1 blocking issue):**
```python
if error_occurs:
    retry()
# What if error doesn't occur? Missing else branch!
```

**Complete (0 blocking issues):**
```python
if error_occurs:
    retry()
else:
    continue_processing()
```

**Complete with explicit no-op (0 blocking issues):**
```python
if error_occurs:
    retry()
# If no error: continue with next step (explicit no-op documented)
```

## Imperative Voice Check

**Passive/Conditional (0.5 issue each):**
- "The file should be validated"
- "It would be good to check permissions"
- "Consider running tests"

**Imperative (0 issues):**
- "Validate the file"
- "Check permissions"
- "Run tests"

## Worked Example

**Target:** Example rule with mixed actionability

### Step 1: Identify and Count Issues

```markdown
Line 45: "Use appropriate clustering for large tables"
Line 67: "If performance is slow, optimize the query"
Line 89: "Consider adding indexes if necessary"
Line 120: "Validate inputs" (no else branch after conditional on line 118)
Line 150: "The configuration should be verified"
```

### Step 2: Count by Category

**Issue Inventory:**
- Line 45: "appropriate" - Undefined threshold (1 issue)
- Line 45: "large" - Undefined threshold (1 issue)
- Line 67: "slow" - Undefined threshold (1 issue)
- Line 89: "Consider" - Ambiguous action (1 issue)
- Line 89: "if necessary" - Ambiguous conditional (1 issue)
- Line 120: Missing else - Incomplete conditional (1 issue)
- Line 150: "should be" - Passive voice (0.5 issue)

**Total:** 6.5 (round to 7 blocking issues)

### Step 3: Determine Score

7 blocking issues = **6/10 (15 points)**

### Step 4: Document in Review

```markdown
## Actionability: 6/10 (15 points)

**Blocking issues:** 7

**Issue Summary:**
- Undefined thresholds: 3 (lines 45, 67)
- Ambiguous actions: 2 (line 89)
- Incomplete conditionals: 1 (line 120)
- Passive voice: 1 (line 150)

**Priority fixes:**
1. Line 45: Define "large tables" (e.g., >10M rows OR >5GB)
2. Line 67: Define "slow" (e.g., >5 seconds)
3. Line 89: Replace "Consider...if necessary" with explicit condition
```

## Inter-Run Consistency Target

**Expected variance:** ±1 blocking issue count between runs

**If counts differ by >2:**
1. Re-read Counting Definitions section
2. List each issue with line number
3. Compare against compound phrase table
4. Document ambiguous cases

**Acceptable variance sources:**
- Partial issues (0.5) rounding differently
- Compound phrases counted as 1 vs 2

**Unacceptable variance:**
- Skipping entire categories
- Inconsistent application of counting rules

## Agent Execution Test Integration

If Agent Execution Test finds ≥10 blocking issues:
- Cap Actionability at 4/10 maximum
- Document each blocking issue with line number
- Prioritize undefined thresholds in recommendations

## Non-Issues (Do NOT Count)

**Review EACH flagged item against this list before counting.**

### Pattern 1: Defined Terms
**Pattern:** Term appears undefined but IS defined elsewhere in rule
**Example:** "large tables" at line 100, but line 36 defines "Large table: >10M rows"
**Why NOT an issue:** Definition exists; cross-reference is appropriate
**Action:** Remove from inventory with note "Defined at line 36"

### Pattern 2: Scoped Exceptions
**Pattern:** "Always X" followed by "except when Y"
**Example:** "Always use explicit columns, except for COUNT(*) queries"
**Why NOT an issue:** Exception is explicitly scoped, not contradictory
**Action:** Remove from inventory with note "Scoped exception"

### Pattern 3: Context-Dependent Guidance
**Pattern:** Different guidance for different contexts
**Example:** "In production, use retries. In development, fail fast."
**Why NOT an issue:** Contexts are clearly distinguished
**Action:** Remove from inventory with note "Context-dependent"

### Pattern 4: Imperative with Implicit Default
**Pattern:** "If X, do Y" where NOT doing Y is the obvious default
**Example:** "If timeout occurs, retry with exponential backoff"
**Why NOT an issue:** Default (continue without retry) is implicit and obvious
**Action:** Remove from inventory with note "Implicit default is clear"

### Pattern 5: Quantified Thresholds
**Pattern:** Subjective-sounding word with explicit definition
**Example:** "significant changes (>100 lines modified)"
**Why NOT an issue:** Threshold is quantified in parentheses
**Action:** Remove from inventory with note "Quantified"

### Pattern 6: Technical Terminology
**Pattern:** Domain-specific term that has standard meaning
**Example:** "Use idempotent operations" (idempotent = produces same result on repeat)
**Why NOT an issue:** Standard technical term with known meaning
**Action:** Remove from inventory with note "Standard terminology"

### Pattern 7: Examples That Illustrate
**Pattern:** Code example that demonstrates the rule
**Example:** Example shows `SELECT *` when demonstrating what NOT to do
**Why NOT an issue:** Example is illustrative, not prescriptive
**Action:** Remove from inventory with note "Illustrative example"

### Pattern 8: Conditional Chains
**Pattern:** Multiple if-then statements covering all cases
**Example:** "If A, do X. If B, do Y. Otherwise, do Z."
**Why NOT an issue:** All branches are covered by chain
**Action:** Remove from inventory with note "Complete conditional chain"
