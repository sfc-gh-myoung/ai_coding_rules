# Actionability Rubric (25 points)

## Scoring Criteria

### 5/5 (25 points): Excellent
- 0 blocking issues
- All conditionals have explicit branches (if X then Y; else Z)
- All actions use imperative voice
- Quantified examples for all ambiguous terms

### 4/5 (20 points): Good
- 1-3 blocking issues
- 90%+ conditionals have explicit branches
- 90%+ imperative voice

### 3/5 (15 points): Acceptable
- 4-6 blocking issues
- 70-89% conditionals have explicit branches
- 70-89% imperative voice

### 2/5 (10 points): Needs Work
- 7-10 blocking issues
- 50-69% conditionals have explicit branches
- 50-69% imperative voice

### 1/5 (5 points): Poor
- >10 blocking issues
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
- 0 issues: 5/5 (25 pts) - No agent judgment required
- 1-3 issues: 4/5 (20 pts) - Minor refinements needed
- 4-6 issues: 3/5 (15 pts) - Several clarifications needed
- 7-10 issues: 2/5 (10 pts) - Significant rewrite required
- 11+ issues: 1/5 (5 pts) - Not executable by agents

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

7 blocking issues = **2/5 (10 points)**

### Step 4: Document in Review

```markdown
## Actionability: 2/5 (10 points)

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
- Cap Actionability at 2/5 maximum
- Document each blocking issue with line number
- Prioritize undefined thresholds in recommendations
