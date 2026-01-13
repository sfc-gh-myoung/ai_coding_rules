# Success Criteria Rubric (20 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 4
**Points:** Raw × (4/2) = Raw × 2.0

## Scoring Criteria

### 10/10 (20 points): Perfect
- 100% of tasks have completion signals
- 100% of criteria are measurable (numbers, exit codes, file existence)
- 100% of criteria are agent-testable (no human judgment)
- Verification commands provided for all

### 9/10 (18 points): Near-Perfect
- 95-99% of tasks have completion signals
- 100% criteria measurable
- 100% criteria agent-testable

### 8/10 (16 points): Excellent
- 90-94% of tasks have completion signals
- 95%+ criteria measurable
- 95%+ criteria agent-testable

### 7/10 (14 points): Good
- 85-89% of tasks have completion signals
- 90-94% criteria measurable
- 90-94% criteria agent-testable

### 6/10 (12 points): Acceptable
- 75-84% of tasks have completion signals
- 85-89% criteria measurable
- 85-89% criteria agent-testable

### 5/10 (10 points): Borderline
- 65-74% of tasks have completion signals
- 75-84% criteria measurable
- 75-84% criteria agent-testable

### 4/10 (8 points): Needs Work
- 55-64% of tasks have completion signals
- 65-74% criteria measurable
- 65-74% criteria agent-testable

### 3/10 (6 points): Poor
- 45-54% of tasks have completion signals
- 55-64% criteria measurable
- 55-64% criteria agent-testable

### 2/10 (4 points): Very Poor
- 35-44% of tasks have completion signals
- 45-54% criteria measurable
- 45-54% criteria agent-testable

### 1/10 (2 points): Inadequate
- 25-34% of tasks have completion signals
- 35-44% criteria measurable
- 35-44% criteria agent-testable

### 0/10 (0 points): No Success Criteria
- <25% of tasks have completion signals
- <35% criteria measurable
- <35% criteria agent-testable

## Counting Definitions

### Task Coverage

**Step 1:** Count total tasks in plan
**Step 2:** Count tasks with explicit completion criteria
**Step 3:** Calculate coverage percentage

```
Coverage % = (tasks with criteria / total tasks) × 100
```

### Measurable Criteria

**Definition:** Criteria that can be expressed as numbers, exit codes, or boolean checks.

**Measurable (count as 1):**
- Exit codes: "exit code 0"
- Numeric thresholds: "latency <500ms", "coverage ≥90%"
- File existence: "output.json exists"
- String matching: "output contains 'SUCCESS'"
- Counts: "5 tests pass", "0 errors"

**NOT measurable (count as 0):**
- "Code looks good"
- "Performance is acceptable"
- "UI is user-friendly"
- "Changes are appropriate"

### Agent-Testable Criteria

**Definition:** Criteria that an agent can verify without human judgment.

**Agent-testable (count as 1):**
- `pytest exit code 0`
- `curl localhost:8000/health returns 200`
- `grep ERROR logs.txt returns empty`
- `wc -l output.csv ≥ 1000`

**NOT agent-testable (count as 0):**
- "Code is clean"
- "Design is elegant"
- "User experience is good"
- "Architecture is sound"

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (20 pts):** 100% task coverage, 100% measurable, 100% agent-testable
- **9/10 (18 pts):** 95-99% task coverage, 100% measurable, 100% agent-testable
- **8/10 (16 pts):** 90-94% task coverage, 95%+ measurable, 95%+ agent-testable
- **7/10 (14 pts):** 85-89% task coverage, 90-94% measurable, 90-94% agent-testable
- **6/10 (12 pts):** 75-84% task coverage, 85-89% measurable, 85-89% agent-testable
- **5/10 (10 pts):** 65-74% task coverage, 75-84% measurable, 75-84% agent-testable
- **4/10 (8 pts):** 55-64% task coverage, 65-74% measurable, 65-74% agent-testable
- **3/10 (6 pts):** 45-54% task coverage, 55-64% measurable, 55-64% agent-testable
- **2/10 (4 pts):** 35-44% task coverage, 45-54% measurable, 45-54% agent-testable
- **1/10 (2 pts):** 25-34% task coverage, 35-44% measurable, 35-44% agent-testable
- **0/10 (0 pts):** <25% task coverage, <35% measurable, <35% agent-testable

**Critical gate:** If <50% of tasks have criteria, cap at 4/10 (8 points)

## Completion Signal Types

### Type 1: Exit Codes

```markdown
GOOD (agent-testable):
Task: Run tests
Success: pytest exit code 0
Failure: pytest exit code non-zero
```

### Type 2: File Existence

```markdown
GOOD (agent-testable):
Task: Build artifacts
Success: dist/app.tar.gz exists AND size >1MB
Failure: File missing OR size <1MB
```

### Type 3: Output Content

```markdown
GOOD (agent-testable):
Task: Apply migrations
Success: Output contains "Applied 5 migrations"
Failure: Output contains "Error:" OR "Failed:"
```

### Type 4: State Verification

```markdown
GOOD (agent-testable):
Task: Start server
Success: curl localhost:8000/health returns HTTP 200
Failure: Connection refused OR non-200 status
```

### Type 5: Numeric Thresholds

```markdown
GOOD (agent-testable):
Task: Optimize performance
Success: p95 latency <500ms (benchmark output)
Failure: p95 latency >=500ms
```

## Task Coverage Tracking Table

Use during review:

**Task Coverage Inventory (example):**
- Run tests (line 23): Has criteria (Yes), Measurable (Yes - exit code), Agent-testable (Yes), Verification: `pytest`
- Refactor code (line 45): Has criteria (No)
- Deploy app (line 67): Has criteria (Yes), Measurable (Yes - HTTP 200), Agent-testable (Yes), Verification: `curl`
- Improve UX (line 89): Has criteria (No)

**Summary:**
- Tasks with criteria: 2/4 = 50%
- Measurable: 2/2 = 100%
- Agent-testable: 2/2 = 100%

## Common Success Criteria Issues

### Issue 1: No Completion Signal

**Problem:**
```markdown
Task: Update dependencies
(no success criteria)
```

**Fix:**
```markdown
Task: Update dependencies

Success criteria:
- requirements.txt modified (git diff shows changes)
- uv pip install exit code: 0
- Import test: python -c "import flask" exit code 0

Completion: All 3 criteria met
```

### Issue 2: Vague Criteria

**Problem:**
```markdown
Success: Code is better
```

**Fix:**
```markdown
Success:
- Linter: ruff check src/ exit code 0
- Coverage: pytest --cov ≥90%
- Complexity: radon cc src/ --average <5
```

### Issue 3: Not Agent-Testable

**Problem:**
```markdown
Success: UI looks professional
```

**Fix:**
```markdown
Success:
- Lighthouse accessibility: ≥95 (lighthouse CLI output)
- Console errors: 0 (browser console log)
- All links valid: linkchecker exit code 0
```

### Issue 4: Incomplete Verification

**Problem:**
```markdown
Task: Deploy to production
Success: Deployment completes
```

**Fix:**
```markdown
Task: Deploy to production

Success criteria (ALL must pass):
1. Deploy script: exit code 0
2. Health check: curl https://app.com/health returns 200
3. Version check: curl https://app.com/version returns "1.2.3"
4. Error rate: <1% for 5 minutes (monitoring API)
5. Rollback ready: git tag v1.2.2 exists

Verification:
```bash
./deploy.sh && \
curl -f https://app.com/health && \
curl -s https://app.com/version | grep -q "1.2.3" && \
echo "SUCCESS"
```
```

## Worked Example

**Target:** Feature implementation plan

### Step 1: List All Tasks

```markdown
1. Set up development environment
2. Implement login endpoint
3. Write unit tests
4. Refactor authentication module
5. Deploy to staging
6. Conduct code review
```

**Total tasks:** 6

### Step 2: Assess Each Task

**Task Assessment:**
- 1. Setup env: Yes "pytest passes", Measurable (Yes), Agent-testable (Yes)
- 2. Login endpoint: Yes "returns 200", Measurable (Yes), Agent-testable (Yes)
- 3. Unit tests: Yes "100% pass", Measurable (Yes), Agent-testable (Yes)
- 4. Refactor: No "cleaner code", Measurable (No), Agent-testable (No)
- 5. Deploy staging: Yes "health check", Measurable (Yes), Agent-testable (Yes)
- 6. Code review: No "approved", Measurable (No), Agent-testable (No)

### Step 3: Calculate Metrics

- Tasks with criteria: 4/6 = 67%
- Of those with criteria:
  - Measurable: 4/4 = 100%
  - Agent-testable: 4/4 = 100%

### Step 4: Determine Score

67% coverage = **5/10 (10 points)**

### Step 5: Document in Review

```markdown
## Success Criteria: 5/10 (10 points)

**Task coverage:** 67% (4/6 tasks have criteria)

**Task Status Summary:**
- Setup env: pytest exit code 0 - OK: Measurable, testable
- Login endpoint: HTTP 200 response - OK: Measurable, testable
- Unit tests: 100% tests pass - OK: Measurable, testable
- Refactor: "cleaner code" - FAIL: Not measurable
- Deploy staging: Health check 200 - OK: Measurable, testable
- Code review: "approved" - FAIL: Not agent-testable

**Issues:**
1. Task 4 (Refactor): No measurable criteria
2. Task 6 (Code review): Requires human judgment

**Recommended fixes:**
1. Refactor: Add "ruff check exit 0, complexity <5"
2. Code review: Add "PR approved via GitHub API check"
```

## Success Criteria Checklist

During review, verify:

- [ ] Every task has completion criteria
- [ ] All criteria are measurable (numbers, exit codes, existence)
- [ ] All criteria are agent-testable (no human judgment)
- [ ] Verification commands provided
- [ ] Both success AND failure conditions defined
- [ ] Multiple criteria use explicit AND/OR logic
- [ ] Criteria include HOW to verify, not just WHAT

## Inter-Run Consistency Target

**Expected variance:** ±5% coverage

**Verification:**
- List all tasks explicitly
- Use tracking table with Y/N
- Apply measurable/agent-testable definitions strictly

**If variance exceeds threshold:**
- Re-count tasks using numbered list
- Apply definitions from this rubric
- Document borderline cases
