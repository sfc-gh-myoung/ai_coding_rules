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

### Task Counting Standard

**Purpose:** Eliminate variance in task counts between reviewers (resolves 18 vs 40 disagreement).

#### Definition: What Is a Task?

**Task (countable):**
- Top-level work unit with deliverable
- Typically marked with `### Task X.Y` or equivalent heading
- Contains multiple steps but counts as ONE task
- Has clear completion criteria
- Independent unit of work that produces observable output

**Sub-step (NOT countable):**
- Numbered step within a task (1, 2, 3...)
- Implementation detail within larger work unit
- No independent deliverable
- Cannot be completed in isolation

#### Counting Protocol

**Step 1: Identify Task Markers**
```bash
grep -E "^###\s+(Task|Phase|Step)" plan.md
```

**Step 2: Count Only Major Work Units**
```markdown
Phase 1: Split Rules (3 tasks)
  - Task 1.1: Split rule A → 1 task
  - Task 1.2: Split rule B → 1 task  
  - Task 1.3: Split rule C → 1 task

# Sub-steps within Task 1.1 (NOT counted):
# 1. Read file
# 2. Analyze sections
# 3. Create split files
# 4. Update references
# These are implementation details, not tasks
```

**Step 3: Calculate Total**
- Sum task headings across all phases
- **Total: 9 tasks** (NOT 45 sub-steps)

#### Examples from Actual Reviews

**INCORRECT Counting (40 tasks):**
```markdown
Phase 0: Prerequisites
  1. Read AGENTS.md ← counted as task (WRONG)
  2. Read 000-global-core.md ← counted as task (WRONG)
  3. Verify understanding ← counted as task (WRONG)
  ...
Phase 1: Split Rules  
  1. Read rules/100-snowflake-core.md ← counted as task (WRONG)
  2. Analyze split points ← counted as task (WRONG)
  ...
```
**Result:** 40 "tasks" (counted every numbered step)

**CORRECT Counting (18 tasks):**
```markdown
Phase 0: Prerequisites → 4 tasks (Task 0.1, 0.2, 0.3, 0.4)
Phase 1: Split Rules → 3 tasks (Task 1.1, 1.2, 1.3)
Phase 2: Update References → 6 tasks (Task 2.1-2.6)
Phase 3: Validation → 3 tasks (Task 3.1, 3.2, 3.3)
Phase 4: Documentation → 2 tasks (Task 4.1, 4.2)
```
**Total: 18 tasks** ✓

#### Rule Summary

| Element | Countable? | Example |
|---------|------------|---------|
| `### Task X.Y: [Name]` | YES | Task 1.1: Split core rules |
| `### Phase X: [Name]` | NO (container) | Phase 1: Split Rules |
| `1. [Step description]` | NO (sub-step) | 1. Read file contents |
| `- [Bullet item]` | NO (detail) | - Check for errors |
| `**Step X:** [Name]` in bold | MAYBE* | **Step 1:** Setup |

*Bold steps: Count as task ONLY if they have independent deliverables and completion criteria.

#### Task Counting Worksheet

Use during review:

| Task ID | Line | Task Name | Deliverable | Countable? |
|---------|------|-----------|-------------|------------|
| 1.1 | 45 | Split core rules | 3 split files | YES |
| 1.1.1 | 47 | Read file | (none) | NO (sub-step) |
| 1.1.2 | 49 | Analyze | (none) | NO (sub-step) |
| 1.2 | 67 | Update imports | Updated files | YES |

**Total countable tasks:** ___

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

## Scoring Thresholds (Clarified)

**Threshold Boundaries:**
- "≥90%" means 90.0% qualifies (inclusive)
- "91% coverage" = 10/10 (exceeds 90%)
- "89.9% coverage" = 9/10 (below 90% threshold)
- "90.0% coverage" = 10/10 (meets threshold exactly)

**Edge Case Rules:**
- Round to 1 decimal place before comparing to thresholds
- Document calculation method in worksheet
- When exactly on boundary (e.g., 90.0%), award higher tier

**Calculation Example:**
```
Tasks with criteria: 18
Total tasks: 20
Coverage = 18/20 × 100 = 90.0%
Round to 1 decimal: 90.0%
Threshold check: ≥90% → YES
Score: 10/10 (meets 90% threshold)
```

## Score Decision Matrix (ENHANCED)

**Purpose:** Convert task coverage and criteria quality into dimension score. No interpretation needed - just look up the tier.

### Input Values

From completed worksheet:
- **Task Coverage %:** Tasks with criteria / Total tasks × 100
- **Measurable %:** Measurable criteria / Tasks with criteria × 100
- **Agent-Testable %:** Agent-testable criteria / Tasks with criteria × 100

### Scoring Table

| Coverage % | Measurable | Testable | Tier | Raw Score | × Weight | Points |
|------------|------------|----------|------|-----------|----------|--------|
| 100% | 100% | 100% | Perfect | 10/10 | × 2 | 20 |
| 95-99% | 100% | 100% | Near-Perfect | 9/10 | × 2 | 18 |
| 90-94% | 95%+ | 95%+ | Excellent | 8/10 | × 2 | 16 |
| 85-89% | 90-94% | 90-94% | Good | 7/10 | × 2 | 14 |
| 75-84% | 85-89% | 85-89% | Acceptable | 6/10 | × 2 | 12 |
| 65-74% | 75-84% | 75-84% | Borderline | 5/10 | × 2 | 10 |
| 55-64% | 65-74% | 65-74% | Below Standard | 4/10 | × 2 | 8 |
| 45-54% | 55-64% | 55-64% | Poor | 3/10 | × 2 | 6 |
| 35-44% | 45-54% | 45-54% | Very Poor | 2/10 | × 2 | 4 |
| 25-34% | 35-44% | 35-44% | Critical | 1/10 | × 2 | 2 |
| <25% | <35% | <35% | No Criteria | 0/10 | × 2 | 0 |

**Critical Gate:** If <50% of tasks have criteria, cap at 4/10 (8 points)

### Tie-Breaking Algorithm (Deterministic)

**When coverage falls exactly on tier boundary (e.g., exactly 90%):**

Execute this algorithm in order. STOP at first decisive result.

1. **Check Measurable %:** If measurable > tier requirement → HIGHER tier
2. **Check Agent-Testable %:** If testable > tier requirement → HIGHER tier
3. **Check Criteria Quality:**
   - Count tasks with BOTH measurable AND testable criteria: `Q = ___`
   - If Q ≥ 80% of tasks with criteria → HIGHER tier
   - If Q < 60% of tasks with criteria → LOWER tier
4. **Default:** HIGHER tier (coverage % is primary metric)

### Edge Cases

**Edge Case 1: High coverage but low measurability**
- **Example:** 95% coverage, but only 60% measurable (vague criteria)
- **Rule:** Use LOWER of coverage tier or measurable tier
- **Rationale:** Vague criteria = no real verification

**Edge Case 2: Phase-level criteria only (no task-level)**
- **Example:** All tasks verified via single phase verification
- **Rule:** Count as 100% coverage IF phase verification is comprehensive
- **Rationale:** Phase verification covers all constituent tasks

**Edge Case 3: Human-required tasks in otherwise testable plan**
- **Example:** 1 task requires "code review approval" in 18-task plan
- **Rule:** Don't penalize agent-testable % for inherently human tasks
- **Rationale:** Some tasks genuinely need humans (but flag as limitation)

### Worked Example

**Scenario:** 18 tasks, 16 have criteria, 15 measurable, 14 agent-testable

**Step 1:** Calculate percentages
- Task coverage: 16/18 = 88.9% → round to 89.0%
- Measurable: 15/16 = 93.75% → round to 93.8%
- Agent-testable: 14/16 = 87.5%

**Step 2:** Look up in scoring table
- 89.0% coverage falls in range 85-89%
- Tier: Good
- Raw score: 7/10

**Step 3:** Check tie-breaking (on boundary at 89%)
- Measurable 93.8% > 90% requirement → could support HIGHER
- Agent-testable 87.5% < 90% requirement → stays at current tier
- No tier adjustment

**Step 4:** Calculate points
- Raw score: 7/10
- Points: 7 × 2 = 14/20

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

## Non-Issues (Do NOT Count)

**Purpose:** Eliminate false positives by explicitly defining what is NOT a success criteria issue.

### Pattern 1: Sub-Task Inheriting Parent Criteria

**Example:**
```markdown
Task 1.1: Implement login (Success: "pytest tests/auth/ passes")
  - Step 1: Create route ← no individual criteria needed
  - Step 2: Add validation ← inherits parent criteria
```
**Why NOT an issue:** Sub-steps inherit Task 1.1's success criteria  
**Overlap check:** See Task Counting Standard - sub-steps not countable  
**Correct action:** Do not flag sub-steps lacking criteria

### Pattern 2: Standard Command with Implicit Success (pytest, ruff, etc.)

**Example:**
```markdown
Task 2.1: Run linting
"Run: ruff check src/"
```
**Why NOT an issue:** ruff exit code 0 = success is well-understood  
**Overlap check:** Not an Executability issue (command is explicit)  
**Correct action:** Do not flag standard commands lacking explicit criteria

### Pattern 3: Phase-Level Criteria Covering Multiple Tasks

**Example:**
```markdown
Task 3.1: Edit config
Task 3.2: Update schema
Phase 3 Success: "task validate returns 0"
```
**Why NOT an issue:** Phase-level verification covers individual tasks  
**Overlap check:** N/A - criteria exist at phase level  
**Correct action:** Count phase criteria coverage, not individual task gaps

### Pattern 4: Verification Command in Different Section

**Example:**
```markdown
Task 4.1: Implement feature
...
## Validation Section
Task 4.1 verification: pytest tests/feature_test.py
```
**Why NOT an issue:** Verification exists, just in separate section  
**Overlap check:** N/A - structure choice, not missing criteria  
**Correct action:** Search entire plan before flagging as missing

### Pattern 5: Negative Criteria (What Should NOT Happen)

**Example:**
```markdown
Success: "grep -r 'TODO' src/ returns empty"
```
**Why NOT an issue:** Negative criteria ("no TODOs") is valid measurable criteria  
**Overlap check:** N/A - measurable and agent-testable  
**Correct action:** Count as valid criteria (measurable: empty output)

## Complete Pattern Inventory

**Purpose:** Eliminate interpretation variance by providing exhaustive lists. If it's not in this list, don't invent it. Match case-insensitive.

### Category 1: Vague Success Terms (25 Phrases)

**Exact Phrases - NOT Measurable:**
1. "looks good"
2. "code is clean"
3. "works correctly"
4. "functions properly"
5. "is complete"
6. "is ready"
7. "meets requirements"
8. "performs well"
9. "is acceptable"
10. "is appropriate"
11. "is satisfactory"
12. "is successful"
13. "is effective"
14. "is efficient"
15. "is optimized"
16. "is improved"
17. "is better"
18. "is professional"
19. "is user-friendly"
20. "is intuitive"
21. "is elegant"
22. "is sound"
23. "is robust"
24. "is stable"
25. "is production-ready"

**Regex Patterns:**
```regex
\b(looks|appears|seems)\s+(good|fine|okay|correct|complete|ready)\b
\b(is|are)\s+(clean|appropriate|acceptable|satisfactory|successful|effective|efficient|optimized|improved|better|professional|friendly|intuitive|elegant|sound|robust|stable)\b
\b(works|functions|performs|operates)\s+(correctly|properly|well|fine)\b
\bmeets\s+(requirements|expectations|standards)\b
```

**Context Rules:**
- Match found → Check for quantified alternative in same section
- If quantified criteria present → NOT an issue
- If only vague term → Count as unmeasurable

### Category 2: Human-Only Criteria (20 Phrases)

**Exact Phrases - NOT Agent-Testable:**
1. "approved by"
2. "reviewed by"
3. "signed off"
4. "user confirms"
5. "stakeholder accepts"
6. "team agrees"
7. "manager approves"
8. "looks correct to"
9. "seems right to"
10. "satisfies stakeholder"
11. "meets user expectations"
12. "passes code review"
13. "design approved"
14. "architecture accepted"
15. "UX validated"
16. "customer satisfied"
17. "client accepts"
18. "PM approves"
19. "QA sign-off"
20. "manual verification"

**Regex Patterns:**
```regex
\b(approved|reviewed|signed\s+off|accepted|confirmed)\s+(by|from)\b
\b(stakeholder|manager|team|user|customer|client|PM|QA)\s+(approves?|accepts?|confirms?|validates?|signs?\s+off)\b
\bmanual\s+(verification|review|testing|check|inspection)\b
\b(human|manual)\s+(judgment|assessment|evaluation)\b
```

**Context Rules:**
- Match found → Count as NOT agent-testable
- Exception: API-based approval checks (e.g., "GitHub PR approved status")

### Category 3: Measurable Criteria Indicators (30 Patterns)

**Exact Phrases - ARE Measurable:**
1. "exit code 0"
2. "exit code non-zero"
3. "returns 200"
4. "HTTP 200"
5. "status code"
6. "file exists"
7. "directory exists"
8. "output contains"
9. "output matches"
10. "grep returns"
11. "returns empty"
12. "returns non-empty"
13. "count equals"
14. "count greater than"
15. "count less than"
16. "≥ X" (numeric threshold)
17. "≤ X" (numeric threshold)
18. "< X" (numeric threshold)
19. "> X" (numeric threshold)
20. "= X" (exact value)
21. "size > X"
22. "latency < X"
23. "coverage ≥ X%"
24. "X tests pass"
25. "0 errors"
26. "0 warnings"
27. "checksum matches"
28. "hash equals"
29. "diff empty"
30. "no output"

**Regex Patterns:**
```regex
\bexit\s+code\s+\d+\b
\b(returns?|status\s+code)\s+\d{3}\b
\b(file|directory|path)\s+exists?\b
\b(output|result)\s+(contains?|matches?|equals?)\b
\b(count|number)\s+(equals?|>|<|>=|<=)\s+\d+\b
\b[≥≤><]=?\s*\d+(\.\d+)?%?\b
\b\d+\s+(tests?|checks?|items?)\s+(pass|fail)\b
\b0\s+(errors?|warnings?|failures?|issues?)\b
```

**Context Rules:**
- Match found → Count as measurable
- Absence of these patterns + vague term → Count as unmeasurable

### Category 4: Standard Command Success (Implicit Criteria) (20 Tools)

**Tools with Well-Known Exit Semantics (exit 0 = success):**
1. pytest
2. ruff
3. mypy
4. black
5. npm test
6. npm build
7. yarn test
8. cargo test
9. cargo build
10. go test
11. make
12. docker build
13. git commit
14. pip install
15. poetry install
16. tox
17. coverage
18. eslint
19. prettier
20. jest

**Regex Patterns:**
```regex
\b(pytest|ruff|mypy|black|jest|eslint|prettier)\b
\b(npm|yarn)\s+(test|build|install)\b
\bcargo\s+(test|build|check)\b
\bgo\s+(test|build)\b
\bmake(\s+\w+)?\b
\bdocker\s+build\b
\b(pip|poetry|uv)\s+(install|sync)\b
```

**Context Rules:**
- Standard tool mentioned without explicit criteria → Count as measurable (implicit exit code 0)
- Unknown tool without criteria → Count as unmeasurable

### Ambiguous Cases Resolution

**Case 1: Task with verification in different section**

**Pattern:** Task definition in Phase X, verification in "Validation" section

**Ambiguity:** Does the task "have" criteria if verification is elsewhere?

**Resolution Rule:**
- Search entire plan for task verification before marking "No criteria"
- If verification exists anywhere referencing task ID → Y (has criteria)
- If no reference found → N (no criteria)

**Case 2: Phase-level vs task-level coverage**

**Pattern:** Individual tasks have no criteria, but phase has comprehensive verification

**Ambiguity:** Does phase verification count as task coverage?

**Resolution Rule:**
- If phase verification explicitly tests each task's output → Y for all covered tasks
- If phase verification is single end-to-end test → Y for final integration, N for intermediate tasks
- Document decision: "Task X.Y inherits Phase X verification"

**Case 3: Implicit success from standard tool**

**Pattern:** "Run pytest" without explicit "exit code 0"

**Ambiguity:** Is implicit exit code sufficient?

**Resolution Rule:**
- Standard tools (see Category 4 list) → Y (measurable, agent-testable)
- Custom scripts without criteria → N (needs explicit criteria)

**Case 4: Multiple criteria with mixed measurability**

**Pattern:** Task has 3 criteria: 2 measurable, 1 vague

**Ambiguity:** Is task measurable or not?

**Resolution Rule:**
- ≥80% criteria measurable → Y (task is measurable)
- <80% criteria measurable → N (task needs improvement)
- Document: "Task X.Y: 2/3 criteria measurable, 1 vague ('looks good')"

**Case 5: Boolean success vs numeric threshold**

**Pattern:** "Tests pass" vs "90% tests pass"

**Ambiguity:** Is boolean (pass/fail) measurable?

**Resolution Rule:**
- Boolean from standard tool → Y (exit code is numeric)
- Boolean from vague assessment ("seems to work") → N
- Numeric threshold always → Y

**Case 6: Verification command without success criteria**

**Pattern:** "Run: curl localhost:8080" (no expected output specified)

**Ambiguity:** Is command without expected output a valid criterion?

**Resolution Rule:**
- Command alone → N (what makes it "pass"?)
- Command + expected output → Y
- Flag: "Task X.Y has verification command but no success definition"

**Case 7: Success criteria referencing external system**

**Pattern:** "Monitoring dashboard shows no errors"

**Ambiguity:** Is external system check agent-testable?

**Resolution Rule:**
- If API/CLI access specified → Y (agent can query)
- If UI-only access → N (requires human observation)
- If access method unclear → N (conservative)

**Case 8: Conditional success criteria**

**Pattern:** "If using database A, check X; if using database B, check Y"

**Ambiguity:** How to count conditional criteria?

**Resolution Rule:**
- All branches have criteria → Y
- Any branch missing criteria → N
- Document: "Task X.Y has conditional criteria, branch Z missing"

**Case 9: Success implied by next step**

**Pattern:** Task 1 has no criteria, but Task 2 says "After Task 1 succeeds..."

**Ambiguity:** Does forward reference imply criteria?

**Resolution Rule:**
- Forward reference without definition → N (criteria must be explicit)
- Forward reference with "Task 1 success = X" → Y

**Case 10: Percentage threshold ambiguity**

**Pattern:** "Coverage should be high" vs "Coverage ≥90%"

**Ambiguity:** Where's the threshold for "measurable"?

**Resolution Rule:**
- Specific number/percentage → Y
- Relative term ("high", "good", "sufficient") → N
- Range with clear bounds ("between 85-95%") → Y

## Anti-Pattern Examples (Common Mistakes)

**❌ WRONG (False Positive):**
- Flagged Task 1.1 step 3: "No success criteria for step 3"
- Rationale given: "Missing completion signal"
- Problem: Step 3 is sub-step, inherits Task 1.1 criteria
- Impact: Task count inflated, coverage % deflated

**✅ CORRECT:**
- Step 3 NOT counted as separate task
- Rationale: Sub-step per Task Counting Standard
- Condition: Would be flagged IF it were a Task heading (### Task X.Y)

**❌ WRONG (False Positive):**
- Flagged Task 2.1: "Criteria not measurable"
- Actual criteria: "ruff check src/ passes"
- Problem: Standard command success = exit code 0 is measurable
- Impact: Measurable % incorrectly reduced

**✅ CORRECT:**
- Task 2.1 criteria counted as measurable
- Rationale: Exit code 0 is numeric, agent-verifiable
- Condition: Would be flagged IF criteria were "code is clean"

## Ambiguous Case Resolution Rules (REQUIRED)

**Purpose:** Provide deterministic scoring when task/criteria classification is borderline.

### Rule 1: Same-File Context
**Count as Y (has criteria) if:** Task has verification command within same task section  
**Count as N (no criteria) if:** No verification command in task section AND no phase-level verification

### Rule 2: Adjectives Without Quantifiers
**Count as measurable if:** Exit code, count, percentage, or file existence check present  
**Count as NOT measurable if:** Only subjective terms ("good", "clean", "appropriate")

### Rule 3: Pattern Variations
**Count as agent-testable if:** Command can be executed programmatically  
**Count as NOT agent-testable if:** Requires human judgment ("review", "approve", "looks good")

### Rule 4: Default Resolution
**Still uncertain after Rules 1-3?** → Count as N/No (conservative - criteria missing/not measurable/not testable)

### Borderline Cases Template

Document borderline decisions in your worksheet:

```markdown
### Task [X]: "[Task Name]"
- **Decision:** Has criteria [Y/N], Measurable [Y/N], Testable [Y/N]
- **Rule Applied:** [1/2/3/4]
- **Reasoning:** [Explain why this classification]
- **Alternative:** [Other interpretation and why rejected]
- **Confidence:** [HIGH/MEDIUM/LOW]
```

## Mandatory Counting Worksheet (REQUIRED)

**CRITICAL:** You MUST create and fill this worksheet BEFORE calculating score.

### Why This Is Required
- **Eliminates counting variance:** Same plan → same worksheet → same score
- **Prevents false negatives:** Task-by-task enumeration catches all gaps
- **Provides evidence:** Worksheet shows exactly what was counted
- **Enables verification:** Users can audit scoring decisions
- **Forces systematic approach:** No skipping tasks that "look complete"

### Worksheet Template

| Task # | Task Name | Has Criteria? | Measurable? | Agent-Testable? | Verification |
|--------|-----------|---------------|-------------|-----------------|--------------|
| 1.1 | [Name] | Y/N | Y/N | Y/N | [command or "human review"] |
| 1.2 | [Name] | Y/N | Y/N | Y/N | [command or "human review"] |
| **TOTALS** | | ___/total | ___/with-criteria | ___/with-criteria | |
| **PERCENTAGES** | | ___% | ___% | ___% | |

### Counting Protocol (6 Steps)

**Step 1: Create Empty Worksheet**
- Copy template above into working document
- Do NOT start reading plan yet
- Prepare to fill systematically

**Step 2: Read Plan Systematically (List All Tasks)**
- Start at line 1 of plan
- Read to END (no skipping)
- For EACH task heading (per Task Counting Standard): Add row to worksheet
- Use Task Counting Standard to identify countable tasks vs sub-steps
- Record task name and line number

**Step 3: Assess Each Task**
- For EACH task row, check:
  - Has Criteria? (Y/N): Is there ANY completion signal?
  - Measurable? (Y/N): Numbers, exit codes, file existence?
  - Agent-Testable? (Y/N): Can agent verify without human judgment?
  - Verification: What command/check proves completion?

**Step 4: Calculate Percentages**
```
Task coverage % = (tasks with criteria / total tasks) × 100
Measurable % = (measurable criteria / tasks with criteria) × 100
Agent-testable % = (agent-testable criteria / tasks with criteria) × 100
```

**Step 5: Look Up Score**
- Use percentages in Score Decision Matrix above
- Find tier matching your coverage percentage
- Record raw score (0-10)

**Step 6: Include in Review Output**
- Copy completed worksheet into review document
- Required for verification and future comparisons
- Format: Markdown table in review's dimension section

### Common Mistakes to Avoid

**❌ Mistake 1: Counting sub-steps as tasks**
- Problem: Inflated task count, incorrect percentages
- Solution: Use Task Counting Standard (task headings only)

**❌ Mistake 2: Accepting vague criteria as "measurable"**
- Problem: "Code is clean" counted as having criteria
- Solution: Only Y for numbers, exit codes, file existence, string matches

**❌ Mistake 3: Counting human-review criteria as "agent-testable"**
- Problem: "UI looks professional" counted as testable
- Solution: Only Y for criteria agent can verify programmatically

**❌ Mistake 4: Not including worksheet in review output**
- Problem: No audit trail, can't verify scoring
- Solution: Always copy completed worksheet into review

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
