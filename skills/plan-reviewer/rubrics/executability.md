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

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (20 pts):** 0 blocking issues - Agent can execute end-to-end
- **9/10 (18 pts):** 1-2 blocking issues - Near-perfect
- **8/10 (16 pts):** 3-4 blocking issues - Excellent
- **7/10 (14 pts):** 5-6 blocking issues - Minor clarifications needed
- **6/10 (12 pts):** 7-8 blocking issues - Several steps need refinement
- **5/10 (10 pts):** 9-10 blocking issues - Borderline
- **4/10 (8 pts):** 11-13 blocking issues - Significant rewrite needed
- **3/10 (6 pts):** 14-16 blocking issues - Poor
- **2/10 (4 pts):** 17-19 blocking issues - Very poor
- **1/10 (2 pts):** 20-25 blocking issues - Inadequate
- **0/10 (0 pts):** >25 blocking issues - Not executable

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
