# Executability Rubric (20 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 4
**Points:** Raw × (4/2) = Raw × 2.0

## Scoring Criteria

### 10/10 (20 points): Perfect
- 0 blocking issues
- All steps have explicit commands
- All conditionals specify exact conditions with else branches
- 0 judgment calls required

### 9/10 (18 points): Near-Perfect
- 1-2 blocking issues
- 99%+ steps explicit
- 99%+ conditionals complete

### 8/10 (16 points): Excellent
- 3-4 blocking issues
- 97-98% steps explicit
- 97-98% conditionals complete

### 7/10 (14 points): Good
- 5-6 blocking issues
- 95-96% steps explicit
- 95-96% conditionals complete

### 6/10 (12 points): Acceptable
- 7-8 blocking issues
- 90-94% steps explicit
- 90-94% conditionals complete

### 5/10 (10 points): Borderline
- 9-10 blocking issues
- 85-89% steps explicit
- 85-89% conditionals complete

### 4/10 (8 points): Needs Work
- 11-13 blocking issues
- 70-84% steps explicit
- 70-84% conditionals complete

### 3/10 (6 points): Poor
- 14-16 blocking issues
- 60-69% steps explicit
- 60-69% conditionals complete

### 2/10 (4 points): Very Poor
- 17-19 blocking issues
- 50-59% steps explicit
- 50-59% conditionals complete

### 1/10 (2 points): Inadequate
- 20-25 blocking issues
- 40-49% steps explicit
- Requires constant human input

### 0/10 (0 points): Not Executable
- >25 blocking issues
- <40% steps explicit
- Cannot execute without major rewrite

## Counting Definitions

### What Counts as ONE Blocking Issue

**Category 1: Conditional Qualifiers (1 issue each)**
- "if appropriate"
- "if necessary"
- "as needed"
- "when suitable"
- "if required"
- "where applicable"

**Category 2: Vague Actions (1 issue each)**
- "consider doing X"
- "you may want to Y"
- "optionally do Z"
- "review and decide"
- "evaluate whether"

**Category 3: Undefined Thresholds (1 issue each)**
- "large file" (how large?)
- "significant changes" (how significant?)
- "many errors" (how many?)
- "slow performance" (how slow?)
- "too complex" (complexity threshold?)

**Category 4: Implicit Commands (1 issue each)**
- "Ensure X is configured" (how?)
- "Make sure Y works" (how to verify?)
- "Verify Z is correct" (verification method?)
- "Set up the environment" (specific steps?)

**Category 5: Missing Branches (1 issue each)**
- `if X` without explicit else
- `when Y` without alternative case
- Decision point without all paths defined

### Counting Compound Phrases

**Examples:**
- "Deploy the application": 0 issues (explicit action)
- "Deploy if ready": 1 issue ("if ready" undefined)
- "Deploy if appropriate": 1 issue ("if appropriate" vague)
- "Consider deploying if needed": 2 issues ("Consider" + "if needed")
- "Ensure proper deployment as needed": 3 issues ("Ensure" + "proper" + "as needed")

## Blocking Issue Classification Matrix

### Decision Tree: Context vs Executability

Use this decision tree to determine if an issue is a **blocking issue** (Executability) or a **context issue** (Context dimension).

**Question 1: Can an autonomous agent execute without additional information?**
- YES → Not a blocking issue (may be Context issue)
- NO → Continue to Question 2

**Question 2: Is the missing information defined within ±10 lines OR under same section header?**
- YES → Context issue (deduct from Context dimension, not Executability)
- NO → Continue to Question 3

**Question 3: Does the plan provide ≥3 sentences of rationale for this action?**
- YES → Weak context, not blocking (Context: -1 point)
- NO → Blocking issue (Executability: -2 points)

### Classification Examples from Actual Reviews

**Example 1: "Monitor (near threshold)" - Line 186**
- Q1: Can execute? NO (threshold undefined)
- Q2: Defined within ±10 lines? NO (no threshold value in lines 176-196)
- Q3: ≥3 sentences rationale? NO (0 sentences)
- **Classification:** BLOCKING ISSUE ✓

**Example 2: "Phase 4 documented but not executed"**
- Q1: Can execute? YES (explicitly marked out-of-scope)
- **Classification:** NOT AN ISSUE ✓

**Example 3: "±5-10% variance acceptable" - Line 1068**
- Q1: Can execute? NO (range ambiguous - is 5% or 10% the threshold?)
- Q2: Defined within ±10 lines? NO (lines 1058-1078 contain no resolution)
- Q3: ≥3 sentences rationale? YES (4 sentences explain why variance exists)
- **Classification:** BLOCKING ISSUE ✓ (rationale doesn't resolve ambiguity)

**Example 4: "Add comprehensive validation" without specifics**
- Q1: Can execute? YES (agent can determine what "comprehensive" means for context)
- **Classification:** NOT A BLOCKING ISSUE ✓

**Example 5: "If tests fail, handle appropriately"**
- Q1: Can execute? NO ("appropriately" undefined)
- Q2: Defined within ±10 lines? NO
- Q3: ≥3 sentences rationale? NO
- **Classification:** BLOCKING ISSUE ✓

**Example 6: "Verify database connection works"**
- Q1: Can execute? NO (how to verify?)
- Q2: Defined within ±10 lines? Check for verification command nearby
- IF verification command exists within 10 lines: Context issue
- IF no verification command: BLOCKING ISSUE ✓

### Dimension Ownership Rules

| Issue Pattern | Primary Dimension | NOT Counted In |
|---------------|-------------------|----------------|
| Ambiguous condition ("if appropriate") | Executability | Context, Scope |
| Missing information nearby (±10 lines) | Context | Executability |
| Undefined threshold ("large", "many") | Executability | Scope |
| Out-of-scope items mentioned | Scope | Executability |
| Missing else/default branch | Executability | Completeness |
| Missing error recovery | Completeness | Executability |

### Decision Tree Verification

**Self-check after classification:**
1. Did you check all three questions in order?
2. Did you verify ±10 line context?
3. Did you count rationale sentences?
4. Is classification consistent with examples above?

**If uncertain:** Apply Question 4 (default conservative)
- **Question 4:** When still uncertain after Q1-Q3 → Count as BLOCKING ISSUE

## Score Decision Matrix (ENHANCED)

**Purpose:** Convert raw blocking issue count into dimension score. No interpretation needed - just look up the tier.

### Input Values

From completed worksheet:
- **Total Blocking Issues:** Sum from worksheet after filtering false positives

### Scoring Table

| Blocking Issues | Tier | Raw Score | × Weight | Points | Interpretation |
|-----------------|------|-----------|----------|--------|----------------|
| 0 | Perfect | 10/10 | × 2 | 20 | Agent executes end-to-end without clarification |
| 1-2 | Near-Perfect | 9/10 | × 2 | 18 | Negligible issues, excellent executability |
| 3-4 | Excellent | 8/10 | × 2 | 16 | High executability, few blockers |
| 5-6 | Good | 7/10 | × 2 | 14 | Good, minor clarifications needed |
| 7-8 | Acceptable | 6/10 | × 2 | 12 | Several steps need refinement |
| 9-10 | Borderline | 5/10 | × 2 | 10 | Significant ambiguity |
| 11-13 | Below Standard | 4/10 | × 2 | 8 | Pervasive issues, needs rework |
| 14-16 | Poor | 3/10 | × 2 | 6 | Major rewrite needed |
| 17-19 | Very Poor | 2/10 | × 2 | 4 | Plan mostly unexecutable |
| 20-25 | Critical | 1/10 | × 2 | 2 | Requires near-complete rewrite |
| >25 | Not Executable | 0/10 | × 2 | 0 | Massive clarification needed |

### Tie-Breaking Algorithm (Deterministic)

**When raw count falls exactly on tier boundary (e.g., exactly 2 issues):**

Execute this algorithm in order. STOP at first decisive result.

1. **Count CRITICAL issues** (blocks execution entirely): `C = ___`
2. **Count MINOR issues** (clarity only, not blocking): `M = ___`
3. **Calculate:** `severity_score = (C × 2) + (M × 1) = ___`
4. **Calculate:** `median = boundary_value × 1.5 = ___`
5. **IF** severity_score > median → LOWER tier
6. **IF** severity_score < median → HIGHER tier
7. **IF** equal → Count unique sections with issues
   - If issues in 1 section: HIGHER tier (single root cause)
   - If issues in 80%+ of sections: LOWER tier (pervasive)
8. **IF** still equal → LOWER tier (default conservative)

### Edge Cases

**Edge Case 1: All issues low-severity (clarity, not blocking)**
- **Example:** 8 issues found, but all are style improvements (e.g., "consider" that has obvious answer)
- **Rule:** Move UP 1 tier (8 issues normally 6/10 → 7/10)
- **Rationale:** Rubric targets BLOCKING issues. Clarity issues are nice-to-fix, not must-fix.

**Edge Case 2: Single catastrophic issue**
- **Example:** 2 issues found (normally 9/10), but one is "No specification for ANY task"
- **Rule:** Move DOWN 1-2 tiers (2 issues normally 9/10 → 7/10)
- **Rationale:** Catastrophic issues have outsized impact beyond their count.

**Edge Case 3: Many duplicate issues (same pattern repeated)**
- **Example:** Same vague phrase "as needed" used 10 times (counted as 10 issues)
- **Rule:** Count as SINGLE issue pattern (same phrase = one fix)
- **Rationale:** Same pattern = same root cause = one fix resolves all

### Worked Example

**Scenario:** Plan has 6 blocking issues from worksheet

**Step 1:** Extract raw count
- Total blocking issues: 6

**Step 2:** Look up in scoring table
- 6 falls in range 5-6
- Tier: Good
- Raw score: 7/10

**Step 3:** Check tie-breaking (on boundary at 6)
- Count CRITICAL: 4 issues block execution
- Count MINOR: 2 issues are clarity only
- severity_score = (4 × 2) + (2 × 1) = 10
- median = 6 × 1.5 = 9
- 10 > 9 → LOWER tier

**Step 4:** Apply edge case check
- No single catastrophic issue
- Not all low-severity
- Not duplicate pattern
- No edge case adjustment

**Step 5:** Final score
- Base: 7/10 (tier lookup)
- Tie-break: -1 (severity > median)
- Final: 6/10
- Points: 6 × 2 = 12/20

## Pre-Scoring Gate: Agent Execution Test

**Before scoring, count total blocking issues across all categories.**

**Score caps based on blocking issues:**
- 0-9 blocking issues: 100/100 possible
- 10-14 blocking issues: 60/100 maximum (NEEDS_WORK)
- 15-19 blocking issues: 50/100 maximum (POOR_PLAN)
- 20-25 blocking issues: 40/100 maximum (INADEQUATE_PLAN)
- >25 blocking issues: 30/100 maximum

## Blocking Issue Tracking

Use this checklist during review:

**Blocking Issue Inventory (example):**
- Line 23: "if necessary" (Conditional) - 1 issue
- Line 45: "large table" (Threshold) - 1 issue
- Line 67: "ensure configured" (Implicit) - 1 issue
- Line 89: "consider adding" (Vague action) - 1 issue
- Line 110: if/no else (Missing branch) - 1 issue

**Total:** ___

## Ambiguous Phrase Detection

### Conditional Qualifiers to Flag

```markdown
BAD: "Update dependencies if necessary"
GOOD: "Update dependencies if package.json was modified"

BAD: "Add tests as needed"
GOOD: "Add tests for all new functions in src/"

BAD: "Scale resources when appropriate"
GOOD: "Scale resources when CPU usage exceeds 80% for 5 minutes"
```

### Vague Actions to Flag

```markdown
BAD: "Consider adding tests"
GOOD: "Add unit tests for functions: login(), logout(), refresh_token()"

BAD: "Review the code"
GOOD: "Run: ruff check src/ --fix"

BAD: "Optimize performance"
GOOD: "Reduce p95 latency from 800ms to <500ms"
```

### Undefined Thresholds to Flag

```markdown
BAD: "If file is large, split it"
GOOD: "If file is >500 lines, split into modules of <=200 lines each"

BAD: "Handle slow queries"
GOOD: "Optimize queries with execution time >5 seconds"

BAD: "For complex functions"
GOOD: "For functions with cyclomatic complexity >10"
```

### Implicit Commands to Flag

```markdown
BAD: "Ensure database is running"
GOOD: "Start database: docker-compose up -d postgres
    Verify: psql -c 'SELECT 1' returns 1"

BAD: "Make sure tests pass"
GOOD: "Run: pytest tests/ -v
    Expected: Exit code 0, all tests pass"
```

## Conditional Completeness

### Incomplete (1 blocking issue)

```markdown
If tests pass:
  - Deploy to production
```
Question: What if tests fail? Missing else branch

### Complete (0 blocking issues)

```markdown
If tests pass (exit code 0):
  - Deploy to production
  - Notify team on Slack #deploys
Else (exit code non-zero):
  - Review failures in CI logs
  - Fix failing tests
  - Re-run: pytest
  - Do NOT deploy until passing
```

## Command Explicitness

### Implicit (Multiple blocking issues)

```markdown
1. Set up the database
2. Configure the application
3. Start the server
```

### Explicit (0 blocking issues)

```markdown
1. Set up the database:
   ```bash
   createdb myapp_dev
   psql myapp_dev < schema.sql
   ```
   Verify: psql -c "\dt" shows 5 tables

2. Configure the application:
   ```bash
   cp .env.example .env
   ```
   Edit .env: Set DATABASE_URL=postgresql://localhost/myapp_dev

3. Start the server:
   ```bash
   python manage.py runserver
   ```
   Verify: curl localhost:8000/health returns 200
```

## Worked Example

**Target:** Deployment plan

### Step 1: Identify Blocking Issues

```markdown
Line 10: "Review changes and deploy if appropriate"
Line 25: "Scale resources as needed"
Line 40: "If deployment succeeds, notify team"
Line 55: "Ensure monitoring is configured"
Line 70: "Run tests" (no verification specified)
```

### Step 2: Count by Category

**Issue Inventory:**
- Line 10: "if appropriate" (Conditional) - 1 issue
- Line 25: "as needed" (Conditional) - 1 issue
- Line 40: no else branch (Missing branch) - 1 issue
- Line 55: "Ensure...configured" (Implicit) - 1 issue
- Line 70: no verification (Implicit) - 1 issue

**Total:** 5 blocking issues

### Step 3: Determine Score

5 blocking issues = **7/10 (14 points)**

### Step 4: Document in Review

```markdown
## Executability: 7/10 (14 points)

**Blocking issues:** 5

**Issue Summary:**
- Conditional qualifiers: 2 (lines 10, 25)
- Missing branches: 1 (line 40)
- Implicit commands: 2 (lines 55, 70)

**Examples:**
- Line 10: "if appropriate" - Specify deployment criteria
- Line 40: No else branch - Add failure handling
- Line 55: "Ensure configured" - Provide config commands

**Recommended fixes:**
1. Line 10: "Deploy if all tests pass AND staging verified"
2. Line 40: Add "Else: rollback and page on-call"
3. Line 55: Provide monitoring setup commands
```

## Executability Checklist

During review, verify:

- [ ] All actions have explicit commands
- [ ] All conditionals specify exact conditions
- [ ] All if/when has corresponding else/default
- [ ] All thresholds quantified (sizes, counts, durations)
- [ ] No "consider", "if appropriate", "as needed"
- [ ] No implicit commands ("ensure", "make sure" without how)
- [ ] Agent could execute without asking for clarification
- [ ] No judgment calls required

## Non-Issues (Do NOT Count)

**Purpose:** Eliminate false positives by explicitly defining what is NOT an executability blocking issue.

### Pattern 1: Action Verb WITH Verification Following (Within 10 Lines)

**Example:** 
```markdown
Line 45: "Ensure database is running"
Line 48: "Verify: psql -c 'SELECT 1' returns 1"
```
**Why NOT an issue:** Implicit command has explicit verification within ±10 lines  
**Overlap check:** N/A - resolved within Executability  
**Correct action:** Do not flag line 45, do not count

### Pattern 2: Quantified Threshold Defined Elsewhere in Plan

**Example:**
```markdown
Line 23: "If file is large, split it"
Line 156: "Large file threshold: >500 lines"
```
**Why NOT an issue:** "Large" is quantified in Thresholds section  
**Overlap check:** N/A - threshold exists  
**Correct action:** Do not flag line 23, do not count

### Pattern 3: Explicit Skip/Default Case Provided

**Example:**
```markdown
Line 67: "If tests pass, deploy"
Line 68: "Default: Do not deploy if tests fail"
```
**Why NOT an issue:** Default/else case explicitly stated  
**Overlap check:** N/A - branch complete  
**Correct action:** Do not flag as missing branch

### Pattern 4: Standard Command with Known Exit Codes

**Example:**
```markdown
Line 89: "Run pytest"
```
**Why NOT an issue:** pytest is standard command with well-known exit code semantics (0=pass, non-0=fail)  
**Overlap check:** N/A  
**Correct action:** Do not flag as implicit, do not count

### Pattern 5: Conditional with Implicit "Continue" Semantics (Low-Risk)

**Example:**
```markdown
Line 110: "If cache exists, use cached version"
(no else - continues to generate fresh version)
```
**Why NOT an issue:** Low-risk operation, implicit "else continue" is safe default  
**Overlap check:** Not a Completeness issue either (no error scenario)  
**Correct action:** Do not flag as missing branch for low-risk optionals

### Pattern 6: Reference to External Standard

**Example:**
```markdown
Line 134: "Configure per Snowflake best practices"
Line 135: "(See: https://docs.snowflake.com/...)"
```
**Why NOT an issue:** External reference provides the specifics  
**Overlap check:** May be Context issue if link broken, but not Executability  
**Correct action:** Do not flag as implicit if reference provided

### Pattern 7: Phase-Level Verification Covering Multiple Tasks

**Example:**
```markdown
Task 1.1: Edit file A
Task 1.2: Edit file B
Phase 1 Verification: "Run task validate && echo 'Phase 1 complete'"
```
**Why NOT an issue:** Phase-level verification covers individual tasks  
**Overlap check:** Not a Success Criteria issue - verification exists  
**Correct action:** Do not flag tasks lacking individual verification if phase-level exists

### Pattern 8: Industry Standard Defaults

**Example:**
```markdown
Line 178: "Deploy to production environment"
```
**Why NOT an issue:** "Production" is understood environment (not vague like "appropriate environment")  
**Overlap check:** N/A - standard terminology  
**Correct action:** Do not flag industry-standard terms as undefined

## Complete Pattern Inventory

**Purpose:** Eliminate interpretation variance by providing exhaustive lists. If it's not in this list, don't invent it. Match case-insensitive.

### Category 1: Conditional Qualifiers (20 Phrases)

**Exact Phrases:**
1. "if necessary"
2. "as needed"
3. "when appropriate"
4. "if desired"
5. "where suitable"
6. "as required"
7. "when suitable"
8. "if warranted"
9. "when feasible"
10. "if applicable"
11. "as appropriate"
12. "when needed"
13. "if relevant"
14. "where appropriate"
15. "when required"
16. "if practical"
17. "as feasible"
18. "when applicable"
19. "if possible"
20. "as possible"

**Regex Patterns:**
```regex
\b(if|when|where|as)\s+(necessary|needed|appropriate|suitable|desired|required|warranted|feasible|applicable|relevant|practical|possible)\b
```

**Context Rules:**
- Match found → Check ±10 lines for quantification
- If quantified → NOT an issue (skip)
- If not quantified → Count as 1 issue

### Category 2: Vague Actions (25 Phrases)

**Exact Phrases:**
1. "consider doing"
2. "you may want to"
3. "could potentially"
4. "might want to"
5. "think about"
6. "evaluate whether"
7. "review and decide"
8. "assess if"
9. "determine whether"
10. "possibly do"
11. "perhaps do"
12. "optionally"
13. "at your discretion"
14. "as you see fit"
15. "if you think"
16. "should you wish"
17. "may wish to"
18. "consider whether"
19. "you might"
20. "potentially"
21. "maybe"
22. "possibly"
23. "if desired"
24. "if preferred"
25. "alternatively consider"

**Regex Patterns:**
```regex
\b(consider|think about|evaluate|assess|determine)\s+(doing|whether|if)\b
\b(you\s+)?(may|might|could)\s+(want|wish|potentially)\s+to\b
\b(optionally|possibly|perhaps|maybe|potentially)\b
\bat\s+your\s+discretion\b
\bas\s+you\s+see\s+fit\b
```

**Context Rules:**
- Match found → Check if action is quantified with specific criteria
- If specific criteria follow → NOT an issue
- If no criteria → Count as 1 issue

### Category 3: Undefined Thresholds (40 Adjectives)

**Quantitative Adjectives (22):**
1. "large"
2. "small"
3. "big"
4. "tiny"
5. "huge"
6. "massive"
7. "significant"
8. "substantial"
9. "considerable"
10. "minimal"
11. "moderate"
12. "extensive"
13. "limited"
14. "ample"
15. "sufficient"
16. "adequate"
17. "excessive"
18. "many"
19. "few"
20. "several"
21. "numerous"
22. "multiple"

**Qualitative Adjectives (18):**
23. "appropriate"
24. "suitable"
25. "reasonable"
26. "acceptable"
27. "satisfactory"
28. "optimal"
29. "ideal"
30. "good"
31. "better"
32. "best"
33. "poor"
34. "worse"
35. "worst"
36. "high-quality"
37. "low-quality"
38. "decent"
39. "adequate"
40. "proper"

**Regex Patterns:**
```regex
\b(large|small|big|tiny|huge|massive|significant|substantial|considerable|minimal|moderate|extensive|limited|ample|sufficient|adequate|excessive)\s+(file|table|dataset|query|change|update|number|amount|volume)\b
\b(many|few|several|numerous|multiple)\s+(files|tables|records|rows|errors|warnings|issues)\b
\b(appropriate|suitable|reasonable|acceptable|satisfactory|optimal|ideal|proper)\s+(size|length|duration|amount|level|threshold)\b
```

**Context Rules:**
- Match found → Check ±10 lines for numeric definition
- Check same section (up to 50 lines) for contextual definition
- If found in either → NOT an issue
- If not found → Count as 1 issue

### Category 4: Implicit Commands (30 Verbs)

**Exact Verbs:**
1. "ensure"
2. "verify"
3. "make sure"
4. "check"
5. "validate"
6. "confirm"
7. "guarantee"
8. "assure"
9. "establish"
10. "maintain"
11. "preserve"
12. "uphold"
13. "enforce"
14. "secure"
15. "protect"
16. "prevent"
17. "avoid"
18. "eliminate"
19. "remove"
20. "fix"
21. "resolve"
22. "correct"
23. "repair"
24. "restore"
25. "recover"
26. "handle"
27. "manage"
28. "control"
29. "monitor"
30. "track"

**Regex Patterns:**
```regex
\b(ensure|verify|make\s+sure|check|validate|confirm|guarantee)\s+(?:that\s+)?[a-zA-Z]+\b
\b(maintain|preserve|establish|enforce|secure|protect)\s+[a-zA-Z]+\b
\b(prevent|avoid|eliminate|remove|fix|resolve|correct)\s+[a-zA-Z]+\b
\b(handle|manage|control|monitor|track)\s+[a-zA-Z]+\b
```

**Context Rules:**
- Match found → Check ±10 lines for HOW (specific command/verification)
- If explicit method provided → NOT an issue
- If no method → Count as 1 issue

### Category 5: Missing Branches (Structural Patterns)

**Patterns to Detect:**
1. `if X` without corresponding `else`
2. `when Y` without alternative case
3. Decision point without all paths defined
4. Conditional with only success path
5. Error scenario without recovery path

**Regex Patterns:**
```regex
^[\s]*[Ii]f\s+.+:[\s]*$  # Line ending with "If X:" 
^[\s]*[Ww]hen\s+.+:[\s]*$  # Line ending with "When X:"
```

**Context Rules:**
- Match found → Scan next 20 lines for else/default/otherwise/alternative
- If branch found → NOT an issue
- If no branch → Count as 1 issue
- Exception: Low-risk operations with obvious default (see Non-Issues Pattern 5)

### Ambiguous Cases Resolution

**Case 1: "Ensure X" with verification following**

**Pattern:** Action verb "ensure", "verify", "check", "make sure" + noun phrase

**Ambiguity:** Is verification method required immediately?

**Resolution Rule:**
- Look within +10 lines for verification command
- If verification present: NOT an issue
- If verification absent: Executability issue
- If verification at +11 to +20 lines: Count as issue with note "(distant verification)"

**Examples:**
```
Line 83: "Ensure database backup exists"
Line 87: "Check: ls backups/*.sql" (within 10 lines)
→ NOT AN ISSUE

Line 83: "Ensure database backup exists"
Line 150: "Verification: Check backups/" (67 lines away)
→ EXECUTABILITY ISSUE (too far, agent might miss connection)
```

**Case 2: "Large file" with quantification nearby**

**Pattern:** Adjective ("large", "small", "significant") + noun

**Ambiguity:** How close must quantification be?

**Resolution Rule:**
- Check ±10 lines for numeric definition
- Check same section (up to 50 lines) for contextual definition
- If found in either: NOT an issue
- If not found: Scope issue (undefined threshold)

**Examples:**
```
Line 22: "Optimize large files"
Line 15: "Files over 500 lines" (same section, 7 lines up)
→ NOT AN ISSUE (quantified in context)

Line 22: "Optimize large files"
Line 215: "Large = >500 lines" (different section, 193 lines away)
→ SCOPE ISSUE (definition too far, agent unlikely to connect)
```

**Case 3: Optional action with implicit skip**

**Pattern:** "Optionally X" or "If desired, X" without else

**Ambiguity:** Is missing else a blocking issue?

**Resolution Rule:**
- If action is additive/enhancement: NOT an issue (default = skip)
- If action affects correctness: Count as 1 issue (default unclear)

**Examples:**
```
Line 45: "Optionally add verbose logging"
→ NOT AN ISSUE (enhancement, default = no logging)

Line 45: "Optionally validate input schema"
→ ISSUE (validation affects correctness, unclear when to skip)
```

**Case 4: Standard tool with implicit semantics**

**Pattern:** Tool name without explicit success criteria (pytest, npm, docker, etc.)

**Ambiguity:** Does tool need explicit success definition?

**Resolution Rule:**
- Standard tools with well-known exit codes: NOT an issue
- Custom scripts or unknown tools: Count as 1 issue

**Standard tools (NOT issues):** pytest, npm, yarn, docker, git, make, cargo, go, pip, poetry

**Case 5: Conditional with context-dependent threshold**

**Pattern:** "If X is slow/large/complex" where context defines threshold elsewhere

**Ambiguity:** How far can definition be?

**Resolution Rule:**
- Same section (≤50 lines): NOT an issue
- Different section but same phase: NOT an issue if cross-referenced
- Different phase or file: Count as 1 issue

**Case 6: Action verb with object implying method**

**Pattern:** "Verify [specific object]" where object implies verification method

**Ambiguity:** Does object provide sufficient specificity?

**Resolution Rule:**
- Object is testable state (e.g., "server is running"): NOT an issue if method obvious
- Object is abstract (e.g., "configuration is correct"): Count as 1 issue

**Examples:**
```
Line 67: "Verify server is running"
→ NOT AN ISSUE (curl/ping/health check is obvious)

Line 67: "Verify configuration is correct"
→ ISSUE (what makes configuration "correct"?)
```

**Case 7: Compound phrase with mixed signals**

**Pattern:** Phrase contains both blocking and non-blocking elements

**Ambiguity:** Which element dominates?

**Resolution Rule:**
- Count EACH blocking element separately
- Non-blocking elements don't cancel blocking ones

**Examples:**
```
"Run pytest to verify tests pass"
→ NOT AN ISSUE (pytest is standard, "verify tests pass" = exit code 0)

"Consider running pytest if appropriate"
→ 2 ISSUES ("Consider" + "if appropriate")
```

**Case 8: Reference to external documentation**

**Pattern:** Action with link/reference to external docs

**Ambiguity:** Does external reference count as specification?

**Resolution Rule:**
- Inline link to specific page: NOT an issue
- General reference ("see docs"): Count as 1 issue
- Broken/invalid link: Count as 1 issue

**Case 9: Phase-level vs task-level verification**

**Pattern:** Individual tasks without verification, but phase has verification

**Ambiguity:** Is task-level verification required?

**Resolution Rule:**
- Phase verification covers tasks: NOT an issue for individual tasks
- Phase verification doesn't cover task: Count as 1 issue

**Case 10: Implicit time-based conditions**

**Pattern:** "Wait until X" or "After Y completes"

**Ambiguity:** How to detect completion?

**Resolution Rule:**
- Specific duration provided: NOT an issue
- Observable state provided: NOT an issue
- Neither provided: Count as 1 issue

**Examples:**
```
"Wait 30 seconds for service startup"
→ NOT AN ISSUE (specific duration)

"Wait until database is ready"
→ ISSUE (how to detect "ready"?)

"Wait until health check passes (curl localhost:8080/health returns 200)"
→ NOT AN ISSUE (observable state provided)
```

## Anti-Pattern Examples (Common Mistakes)

**❌ WRONG (False Positive):**
- Flagged line 45: "Ensure database is running"
- Rationale given: "Implicit command - no specific steps"
- Problem: Verification at line 48 was not checked (±10 line rule)
- Impact: +1 blocking issue incorrectly counted

**✅ CORRECT:**
- Line 45 NOT flagged
- Rationale: Verification command "psql -c 'SELECT 1'" at line 48
- Condition: Would be flagged IF no verification within ±10 lines

**❌ WRONG (False Positive):**
- Flagged line 89: "Run pytest"
- Rationale given: "No success/failure criteria"
- Problem: pytest is standard command with known exit semantics
- Impact: +1 blocking issue incorrectly counted

**✅ CORRECT:**
- Line 89 NOT flagged
- Rationale: Standard command, exit code 0 = success is well-known
- Condition: Would be flagged IF custom test runner with unknown semantics

## Ambiguous Case Resolution Rules (REQUIRED)

**Purpose:** Provide deterministic scoring when patterns are borderline.

### Rule 1: Same-File Context
**Count as 0 if:** Line number provided AND referenced content within ±10 lines is explicit  
**Count as 1 if:** Reference vague OR referenced content itself is ambiguous

### Rule 2: Adjectives Without Quantifiers
**Count as 0 if:** Context provides ≥80% constraint AND variance <20%  
**Count as 1 if:** Context <80% constraining OR variance >20%

### Rule 3: Pattern Variations
**Count as 1 if:** Matches blocking pattern spirit with same ambiguity level  
**Count as 0 if:** Wording is different but meaning is explicit

### Rule 4: Default Resolution
**Still uncertain after Rules 1-3?** → Count as 1 (conservative scoring)

### Borderline Cases Template

Document borderline decisions in your worksheet:

```markdown
### Line [X]: "[Quote]"
- **Decision:** Count [0/1]
- **Rule Applied:** [1/2/3/4]
- **Reasoning:** [Explain why this rule applies]
- **Alternative:** [Other interpretation and why rejected]
- **Confidence:** [HIGH/MEDIUM/LOW]
```

## Mandatory Counting Worksheet (REQUIRED)

**CRITICAL:** You MUST create and fill this worksheet BEFORE calculating score.

### Why This Is Required
- **Eliminates counting variance:** Same plan → same worksheet → same score
- **Prevents false negatives:** Line-by-line enumeration catches all matches
- **Provides evidence:** Worksheet shows exactly what was counted
- **Enables verification:** Users can audit scoring decisions
- **Forces systematic approach:** No skipping sections that "look good"

### Worksheet Template

| Pass | Line | Quote (first 50 chars) | Category | Pattern | Count |
|------|------|------------------------|----------|---------|-------|
| 1 | ___ | "..." | Conditional | if necessary | 1 |
| 2 | ___ | "..." | Vague Action | consider | 1 |
| 3 | ___ | "..." | Threshold | large | 1 |
| 4 | ___ | "..." | Implicit | ensure | 1 |
| 5 | ___ | "..." | Missing Branch | if/no else | 1 |
| **TOTAL** | | | | | **___** |

### Counting Protocol (6 Steps)

**Step 1: Create Empty Worksheet**
- Copy template above into working document
- Do NOT start reading plan yet
- Prepare to fill systematically

**Step 2: Read Plan Systematically (No Scoring Yet)**
- Start at line 1 of plan
- Read to END (no skipping)
- For EACH match: Add row to worksheet with line number
- Complete 5 passes (one per category):
  - Pass 1: Conditional qualifiers (if necessary, as needed, when appropriate, etc.)
  - Pass 2: Vague actions (consider, may want to, optionally, etc.)
  - Pass 3: Undefined thresholds (large, significant, many, slow, etc.)
  - Pass 4: Implicit commands (ensure, verify, make sure, etc.)
  - Pass 5: Missing branches (if without else, when without alternative)
- Record ALL matches (filter false positives later)

**Step 3: Calculate Totals**
- Sum counts from worksheet
- This is your RAW count (before filtering)

**Step 4: Check Non-Issues List (Filter False Positives)**
- Review EACH flagged item in worksheet
- Check against "Non-Issues" section (to be added in Phase 2)
- Remove false positives
- Mark removed items: "~~Line 83: Implicit (verification at 89)~~"
- Recalculate totals with false positives removed

**Step 5: Look Up Score**
- Use adjusted totals in Score Decision Matrix above
- Find tier matching your count
- Record raw score (0-10)

**Step 6: Include in Review Output**
- Copy completed worksheet into review document
- Required for verification and future comparisons
- Format: Markdown table in review's dimension section

### Common Mistakes to Avoid

**❌ Mistake 1: Starting scoring before completing worksheet**
- Problem: Incomplete enumeration, items skipped
- Solution: Fill ENTIRE worksheet first, then calculate score

**❌ Mistake 2: Skipping ahead to "important" sections**
- Problem: Missing issues in "boring" prerequisite sections
- Solution: Read line 1 to END systematically

**❌ Mistake 3: Counting same issue in multiple dimensions**
- Problem: Inflated overall score, dimension overlap
- Solution: Check Blocking Issue Classification Matrix for primary ownership

**❌ Mistake 4: Forgetting to filter false positives**
- Problem: Non-Issues counted as real issues
- Solution: Always execute Step 4 (check Non-Issues list)

**❌ Mistake 5: Not including worksheet in review output**
- Problem: No audit trail, can't verify scoring
- Solution: Always copy completed worksheet into review

## Inter-Run Consistency Target

**Expected variance:** ±2 blocking issues

**Verification method:**
1. Use counting table with line numbers
2. Categorize each issue explicitly
3. Count compound phrases per breakdown rules

**If counts differ by >3:**
- Re-read Counting Definitions
- Check compound phrase handling
- Document ambiguous cases
