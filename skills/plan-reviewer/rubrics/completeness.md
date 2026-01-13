# Completeness Rubric (20 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 4
**Points:** Raw × (4/2) = Raw × 2.0

## Scoring Criteria

### 10/10 (20 points): Perfect
- Setup: 5/5 required elements present
- Validation: 3/3 phases documented
- Error recovery: 5+ scenarios with steps
- Cleanup: Complete with verification
- Edge cases: 90%+ coverage

### 9/10 (18 points): Near-Perfect
- Setup: 5/5 elements present
- Validation: 3/3 phases documented
- Error recovery: 4+ scenarios with steps
- Cleanup: Complete with verification
- Edge cases: 85-89% coverage

### 8/10 (16 points): Excellent
- Setup: 5/5 elements present
- Validation: 3/3 phases documented
- Error recovery: 4 scenarios with steps
- Cleanup: Complete
- Edge cases: 80-84% coverage

### 7/10 (14 points): Good
- Setup: 4/5 elements present
- Validation: 2-3/3 phases documented
- Error recovery: 3 scenarios with steps
- Cleanup: Present but partial
- Edge cases: 70-79% coverage

### 6/10 (12 points): Acceptable
- Setup: 4/5 elements present
- Validation: 2-3/3 phases documented
- Error recovery: 2-3 scenarios
- Cleanup: Present but partial
- Edge cases: 60-69% coverage

### 5/10 (10 points): Borderline
- Setup: 3/5 elements present
- Validation: 2/3 phases documented
- Error recovery: 2 scenarios
- Cleanup: Minimal
- Edge cases: 50-59% coverage

### 4/10 (8 points): Needs Work
- Setup: 3/5 elements present
- Validation: 1-2/3 phases documented
- Error recovery: 1 scenario
- Cleanup: Minimal
- Edge cases: 40-49% coverage

### 3/10 (6 points): Poor
- Setup: 2/5 elements present
- Validation: 1/3 phase documented
- Error recovery: 0-1 scenarios
- Cleanup: Missing
- Edge cases: 30-39% coverage

### 2/10 (4 points): Very Poor
- Setup: 2/5 elements present
- Validation: 0-1/3 phases documented
- Error recovery: 0 scenarios
- Cleanup: Missing
- Edge cases: 20-29% coverage

### 1/10 (2 points): Inadequate
- Setup: 1/5 elements present
- Validation: Not documented
- Error recovery: Not documented
- Cleanup: Not documented
- Edge cases: 10-19% coverage

### 0/10 (0 points): Not Complete
- Setup: 0/5 elements present
- Validation: Not documented
- Error recovery: Not documented
- Cleanup: Not documented
- Edge cases: <10% coverage

## Counting Definitions

### Setup Phase Elements

**Required elements (count 0-5):**

**Setup Element Checklist:**
- Prerequisites verification: Present? Commands provided?
- Environment preparation: Present? Steps specified?
- Dependency installation: Present? Commands provided?
- Configuration setup: Present? Values/files specified?
- Initial state verification: Present? Verification command?

**Scoring by count:**
- 5/5 elements: Full credit
- 4/5 elements: -1 point
- 3/5 elements: -3 points
- 2/5 elements: -5 points
- 0-1/5 elements: -8 points

### Validation Phases

**Required phases (count 0-3):**

**Validation Phase Checklist:**
- Pre-execution: Present? Commands? Expected output?
- During execution: Present? Commands? Expected output?
- Post-execution: Present? Commands? Expected output?

**Scoring by count:**
- 3/3 phases: Full credit
- 2/3 phases: -1 point
- 1/3 phases: -3 points
- 0/3 phases: -5 points

### Error Recovery Scenarios

**Count documented scenarios with recovery steps:**

**Error Recovery Checklist:**
- Input validation failures: Documented? Has recovery steps?
- Execution errors (timeout, crash): Documented? Has recovery steps?
- External dependency failures: Documented? Has recovery steps?
- Permission/access errors: Documented? Has recovery steps?
- Resource exhaustion: Documented? Has recovery steps?
- State corruption: Documented? Has recovery steps?

**Count only scenarios WITH recovery steps.**

**Scoring by count:**
- 4+ scenarios with recovery: Full credit
- 2-3 scenarios with recovery: -2 points
- 1 scenario with recovery: -4 points
- 0 scenarios with recovery: -6 points (CRITICAL)

### Cleanup Phase

**Required elements:**

**Cleanup Checklist:**
- Temporary files removal: Present?
- Resources released: Present?
- State reset (if needed): Present?
- Verification of cleanup: Present?

**Scoring:**
- Complete (4/4): Full credit
- Partial (2-3/4): -1 point
- Minimal (1/4): -2 points
- Missing (0/4): -3 points

### Edge Case Coverage

**Categories to check:**

**Edge Case Checklist:**
- Empty states (Empty DB, no users, cold cache): Count addressed out of 3
- Concurrent execution (Dual runs, locks, races): Count addressed out of 3
- Partial completion (Interrupted, resume, idempotency): Count addressed out of 3
- Resource constraints (Disk full, memory, network): Count addressed out of 3

**Coverage calculation:**
```
Coverage % = (items addressed / 12 total) × 100
```

**Scoring by coverage:**
- 80%+ (10-12/12): Full credit
- 60-79% (7-9/12): -1 point
- 40-59% (5-6/12): -2 points
- 20-39% (3-4/12): -3 points
- <20% (0-2/12): -4 points

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (20 pts):** 5/5 setup, 3/3 validation, 5+ error recovery, complete cleanup, 90%+ edge cases
- **9/10 (18 pts):** 5/5 setup, 3/3 validation, 4+ error recovery, complete cleanup, 85-89% edge cases
- **8/10 (16 pts):** 5/5 setup, 3/3 validation, 4 error recovery, complete cleanup, 80-84% edge cases
- **7/10 (14 pts):** 4/5 setup, 2-3/3 validation, 3 error recovery, partial cleanup, 70-79% edge cases
- **6/10 (12 pts):** 4/5 setup, 2-3/3 validation, 2-3 error recovery, partial cleanup, 60-69% edge cases
- **5/10 (10 pts):** 3/5 setup, 2/3 validation, 2 error recovery, minimal cleanup, 50-59% edge cases
- **4/10 (8 pts):** 3/5 setup, 1-2/3 validation, 1 error recovery, minimal cleanup, 40-49% edge cases
- **3/10 (6 pts):** 2/5 setup, 1/3 validation, 0-1 error recovery, missing cleanup, 30-39% edge cases
- **2/10 (4 pts):** 2/5 setup, 0-1/3 validation, 0 error recovery, missing cleanup, 20-29% edge cases
- **1/10 (2 pts):** 1/5 setup, 0/3 validation, 0 error recovery, missing cleanup, 10-19% edge cases
- **0/10 (0 pts):** 0/5 setup, 0/3 validation, 0 error recovery, missing cleanup, <10% edge cases

**Critical gate:** If error recovery = 0, cap at 4/10 (8 points)

## Required Components Checklist

### Setup Phase

```markdown
## Setup (Example - Complete)

1. Verify prerequisites:
   - Python 3.11+: python --version ≥ 3.11
   - PostgreSQL: pg_isready returns 0

2. Create environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```
   Verify: uv pip list shows flask==3.0.0

4. Configure:
   ```bash
   cp .env.example .env
   ```
   Edit: Set DATABASE_URL=postgresql://localhost/myapp

5. Verify setup:
   ```bash
   pytest tests/smoke/test_connection.py
   ```
   Expected: 1 passed
```

### Validation Checks

```markdown
## Validation (Example - Complete)

### Pre-execution
- [ ] Prerequisites met: all checks pass
- [ ] Input files exist: ls data/*.csv returns files
- [ ] Permissions valid: test -w output/ returns 0

### During execution
- [ ] Progress logged: tail -f logs/process.log shows activity
- [ ] No errors: grep ERROR logs/process.log returns empty
- [ ] Resources stable: memory usage <2GB

### Post-execution
- [ ] Output exists: ls output/results.json returns file
- [ ] Output valid: jq . output/results.json parses successfully
- [ ] State consistent: pytest tests/integration/ passes
```

### Error Recovery

```markdown
## Error Recovery (Example - Complete)

### Input Validation Failure
Detection: Exit code 1, "ValidationError" in output
Recovery:
1. Check error message for specific field
2. Fix input file: vim data/input.csv
3. Re-run: python process.py
4. If still fails: Contact data team

### Timeout (>30 minutes)
Detection: Process killed, "Timeout" in logs
Recovery:
1. Check resource usage: htop
2. Reduce batch size: --batch-size 100
3. Re-run from checkpoint: --resume
4. If still times out: Scale up resources

### Database Connection Failed
Detection: "Connection refused" in logs
Recovery:
1. Check DB status: pg_isready
2. If down: docker-compose up -d postgres
3. Wait 30 seconds
4. Retry: python process.py
5. If still fails: Check credentials in .env
```

### Cleanup Phase

```markdown
## Cleanup (Example - Complete)

1. Remove temp files:
   ```bash
   rm -rf /tmp/process-*
   ```

2. Stop services:
   ```bash
   docker-compose down
   ```

3. Clear cache:
   ```bash
   rm -rf .cache/
   ```

4. Verify cleanup:
   ```bash
   ls /tmp/process-* 2>&1 | grep -q "No such file"
   docker ps | grep -q myapp && echo "FAIL" || echo "OK"
   ```
```

## Worked Example

**Target:** Data migration plan

### Step 1: Assess Setup

**Setup Assessment:**
- Prerequisites: Yes (Python version, DB)
- Environment: Yes (venv creation)
- Dependencies: Yes (pip install)
- Configuration: No - Missing
- Initial verification: Yes (Smoke test)

**Count:** 4/5 elements

### Step 2: Assess Validation

**Validation Assessment:**
- Pre-execution: Yes, commands provided
- During execution: No
- Post-execution: Yes, commands provided

**Count:** 2/3 phases

### Step 3: Assess Error Recovery

**Error Recovery Assessment:**
- Input validation: Yes, has recovery steps
- Timeout: No
- DB failure: Yes, has recovery steps
- Permission error: No

**Count:** 2 scenarios with recovery

### Step 4: Assess Cleanup

**Cleanup Assessment:**
- Temp files: Yes
- Resources: No
- State reset: No
- Verification: Yes

**Count:** 2/4 (Partial)

### Step 5: Assess Edge Cases

**Edge Case Coverage:**
- Empty states: 1/3
- Concurrent: 0/3
- Partial completion: 2/3
- Resources: 1/3

**Coverage:** 4/12 = 33%

### Step 6: Calculate Score

**Component Assessment:**
- Setup: 4/5 = -1 point
- Validation: 2/3 = -1 point
- Error recovery: 2 = -2 points
- Cleanup: 2/4 = -1 point
- Edge cases: 33% = -3 points

**Total deductions:** -8 points
**Final:** 12 points = 6/10 (Acceptable)

### Step 7: Document in Review

```markdown
## Completeness: 6/10 (12 points)

**Setup:** 4/5 elements
- [YES] Prerequisites, environment, dependencies, verification
- [NO] Configuration setup missing

**Validation:** 2/3 phases
- [YES] Pre-execution, post-execution
- [NO] During-execution monitoring missing

**Error recovery:** 2 scenarios
- [YES] Input validation, DB failure
- [NO] Timeout, permission errors missing

**Cleanup:** Partial (2/4)
- [YES] Temp files, verification
- [NO] Resource release, state reset missing

**Edge cases:** 33% (4/12)
- Concurrent execution: Not addressed
- Resource constraints: Partially addressed

**Priority fixes:**
1. Add configuration setup step
2. Add during-execution monitoring
3. Add timeout and permission error handling
4. Complete cleanup section
```

## Inter-Run Consistency Target

**Expected variance:** ±1 point per component

**Verification:**
- Use checklists with Y/N for each item
- Count only items explicitly documented
- Edge case coverage: use category table

**If variance exceeds threshold:**
- Re-verify using checklist tables
- Document borderline items
