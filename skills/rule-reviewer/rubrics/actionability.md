# Actionability Rubric (30 points)

> **Weight:** 6 | **Max:** 30 points | **Formula:** Raw × 3.0

## Hard Caps (Blocking Issue Thresholds)

| Condition | Effect |
|-----------|--------|
| ≥6 blocking issues | Total score capped at 80/100 |
| ≥10 blocking issues | Verdict forced to NOT_EXECUTABLE |

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

> **Why inventories are required:** Eliminates counting variance (same rule → same inventory → same score), prevents false negatives, provides auditable evidence, enables verification.

### Inventory Template

| Line | Quote (first 50 chars) | Issue Type | Category | Count |
|------|------------------------|------------|----------|-------|
| 45 | "Use appropriate timeout..." | Undefined threshold | Actionability | 1 |
| 67 | "If error occurs" (no else) | Missing branch | Actionability | 1 |
| 89 | "Consider adding indexes..." | Ambiguous action | Actionability | 1 |
| 150 | "should be verified" | Passive voice | Actionability | 0.5 |

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
> **Dimension-specific:** Count undefined thresholds, missing branches, ambiguous actions, passive voice per category.

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 6
**Points:** Raw × 3.0

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
- 0 issues: 10/10 (30 pts) - No agent judgment required
- 1 issue: 9/10 (27 pts) - Near-perfect
- 2-3 issues: 8/10 (24 pts) - Excellent
- 4-5 issues: 7/10 (21 pts) - Minor refinements needed
- 6-7 issues: 6/10 (18 pts) - Several clarifications needed | **Hard cap: max 80/100 total**
- 8-9 issues: 5/10 (15 pts) - Borderline
- 10-11 issues: 4/10 (12 pts) - Needs work | **Forces NOT_EXECUTABLE**
- 12-14 issues: 3/10 (9 pts) - Poor
- 15-17 issues: 2/10 (6 pts) - Very poor
- 18-20 issues: 1/10 (3 pts) - Inadequate
- >20 issues: 0/10 (0 pts) - Not actionable

**Critical Override:**
- If blocking issues ≥6: Cap overall rule score at 80/100 regardless of other dimensions
- If blocking issues ≥10: Force verdict to NOT_EXECUTABLE regardless of score

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

7 blocking issues = **6/10 (18 points)**
**Hard cap triggered:** ≥6 issues caps total score at 80/100

### Step 4: Document in Review

```markdown
## Actionability: 6/10 (18 points)

**Blocking issues:** 7
**Hard Cap Applied:** Total rule score capped at 80/100

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

**Expected variance:** ±1 blocking issue count between runs. If counts differ by >2, re-read Counting Definitions, list each issue with line number, compare against compound phrase table.

## Agent Execution Test Integration

If Agent Execution Test finds ≥6 blocking issues:
- Apply hard cap: Total score max 80/100
- Document each blocking issue with line number
- Prioritize undefined thresholds in recommendations

If Agent Execution Test finds ≥10 blocking issues:
- Force verdict to NOT_EXECUTABLE
- Cap Actionability at 4/10 maximum
- Immediate remediation required

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

### Pattern 9: Standard Agent Tool Operations
**Pattern:** References to common agent file/edit/search tool names
**Example:** "Use read_file to inspect the code", "edit with old_string/new_string"
**Why NOT an issue:** These are universal agent operations (read, write, search, edit) expressed using common tool names; all agent platforms have equivalents
**Action:** Remove from inventory with note "Universal agent operation"

### Pattern 10: Status Assertion Checklists
**Pattern:** Checklist items asserting completion state as pass/fail gates
**Example:** "- [ ] Rules loaded section present" / "- [ ] Validation executed"
**Why NOT an issue:** Checklists conventionally use status assertions (verify state is true/false); the implicit action is "verify this condition holds"
**Action:** Remove from inventory with note "Status assertion checklist"
