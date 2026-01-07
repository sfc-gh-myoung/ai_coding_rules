# Completeness Rubric (25 points)

## Scoring Criteria

### 5/5 (25 points): Excellent
- 5+ error scenarios with recovery steps
- All edge cases documented (boundary, concurrency, state)
- Prerequisites with version numbers
- Validation steps for pre/during/post execution
- Fallback strategies for critical operations

### 4/5 (20 points): Good
- 3-4 error scenarios with recovery
- 80%+ edge cases covered
- Prerequisites stated (versions optional)
- Most validation steps present

### 3/5 (15 points): Acceptable
- 2 error scenarios with recovery
- 60-79% edge cases covered
- Some prerequisites stated
- Some validation steps

### 2/5 (10 points): Needs Work
- 1 error scenario (or partial coverage)
- 40-59% edge cases covered
- Prerequisites vague
- Minimal validation

### 1/5 (5 points): Poor
- 0 error scenarios
- <40% edge cases covered
- Prerequisites missing
- No validation guidance

## Counting Definitions

### Error Scenario Coverage

**Minimum required scenarios (count presence):**
1. Input validation failures (malformed data, missing files)
2. Execution errors (timeouts, permission denied)
3. External dependencies (network, API, tools)
4. State inconsistencies (concurrent modifications)
5. Resource exhaustion (disk, memory, connections)

**Scoring by count:**
- 5+ scenarios documented: Full credit
- 3-4 scenarios documented: -2 points
- 2 scenarios documented: -5 points
- 1 scenario documented: -8 points
- 0 scenarios documented: -10 points

### Edge Case Categories

**Required categories (count coverage percentage):**

1. **Boundary conditions:**
   - Empty inputs
   - Maximum sizes
   - Null/missing values
   - Zero values

2. **Concurrency:**
   - Multiple users
   - Simultaneous modifications
   - Race conditions

3. **State transitions:**
   - Initialization
   - Updates
   - Cleanup/teardown

4. **Data anomalies:**
   - Duplicates
   - Missing fields
   - Format issues
   - Encoding problems

**Coverage calculation:**
```
Coverage % = (categories addressed / 4 categories) × 100
```

### Prerequisites Completeness

**Required elements (count presence):**
- Tools required: Check if present (Y/N), check if versioned (Y/N)
- Permissions needed: Check if present (Y/N)
- Environment state: Check if present (Y/N)
- Data requirements: Check if present (Y/N)

**Scoring:**
- All 4 elements with versions where applicable: Full credit
- 3 elements: -1 point
- 2 elements: -3 points
- 1 element: -5 points
- 0 elements: -8 points

### Validation Steps

**Required validation phases:**
1. Pre-execution (prerequisites met, inputs valid)
2. During execution (progress, intermediate checks)
3. Post-execution (output verification, state consistency)

**Scoring:**
- All 3 phases: Full credit
- 2 phases: -1 point
- 1 phase: -3 points
- 0 phases: -5 points

## Score Decision Matrix

**Score Tier Criteria:**
- **5/5 (25 pts):** 5+ error scenarios, 80%+ edge cases, complete prerequisites, 3 validation phases
- **4/5 (20 pts):** 3-4 error scenarios, 80%+ edge cases, partial prerequisites, 2+ validation phases
- **3/5 (15 pts):** 2 error scenarios, 60-79% edge cases, partial prerequisites, 2+ validation phases
- **2/5 (10 pts):** 1 error scenario, 40-59% edge cases, minimal prerequisites, 1 validation phase
- **1/5 (5 pts):** 0 error scenarios, <40% edge cases, missing prerequisites, 0 validation phases

**Note:** Use lowest qualifying tier when scores span multiple tiers.

## Required Coverage Areas

### 1. Error Handling

Must address these scenarios (check Y/N for each):

**Error Scenario Checklist:**
- Input validation failures: Documented? Has recovery steps?
- Execution errors (timeout, permission): Documented? Has recovery steps?
- External dependencies (network, API): Documented? Has recovery steps?
- State inconsistencies: Documented? Has recovery steps?
- Resource exhaustion: Documented? Has recovery steps?

**Example (complete):**
```markdown
### Error Handling

**If file not found:**
1. Check path: `ls -la [path]`
2. Verify permissions: `stat [path]`
3. If missing: report "File [path] not found. Create it or correct path."

**If timeout (>30s):**
1. Increase warehouse size: `ALTER WAREHOUSE SET SIZE='MEDIUM'`
2. Reduce batch size: Process 1000 rows at a time
3. If still fails: Split into multiple operations

**If permission denied:**
1. Check grants: `SHOW GRANTS ON TABLE [table]`
2. Request access from admin
3. Document required privileges in Prerequisites
```

### 2. Edge Cases

Must cover (check Y/N per category):

**Edge Case Checklist:**
- Boundary conditions (empty, max, null, zero): Count addressed out of 4
- Concurrency (multi-user, simultaneous, race): Count addressed out of 3
- State transitions (init, update, cleanup): Count addressed out of 3
- Data anomalies (duplicates, missing, format, encoding): Count addressed out of 4

### 3. Prerequisites and Assumptions

Must document (check Y/N):

**Prerequisites Checklist:**
- Tools required: Documented? Version specified?
- Permissions needed: Documented?
- Environment state: Documented?
- Data requirements: Documented?

**Example (complete):**
```markdown
### Inputs and Prerequisites

- Python 3.11+ with uv installed
- Snowflake connection configured in ~/.snowflake/connections.toml
- Target table exists with SELECT privilege
- Warehouse available with USAGE privilege
- At least 1GB disk space available
```

### 4. Validation Steps

Must specify (check Y/N):

**Validation Phase Checklist:**
- Pre-execution checks: Documented? Commands provided?
- During execution monitoring: Documented? Commands provided?
- Post-execution verification: Documented? Commands provided?

### 5. Fallback Strategies

For critical operations, must provide:
- Alternative approaches if primary method fails
- Rollback procedures for reversible operations
- Manual intervention steps when automation fails

## Worked Example

**Target:** Rule with partial completeness

### Step 1: Assess Error Handling

```markdown
Rule documents:
- File not found error: YES (with recovery)
- Timeout handling: YES (with recovery)
- Network failures: NO
- Permission errors: YES (partial - no recovery steps)
- Resource exhaustion: NO
```

**Count:** 2.5 scenarios with recovery (round to 2)

### Step 2: Assess Edge Cases

```markdown
Boundary: Empty inputs covered, max sizes NOT covered = 1/4
Concurrency: Not addressed = 0/3
State: Init and cleanup covered, updates NOT = 2/3
Data: Duplicates and format covered = 2/4

Total: 5/14 items = 36%
```

### Step 3: Assess Prerequisites

```markdown
Tools: Listed but no versions = Partial
Permissions: Listed = Yes
Environment: Listed = Yes
Data requirements: Not documented = No

Count: 3/4 elements, versions missing
```

### Step 4: Assess Validation

```markdown
Pre-execution: YES
During execution: NO
Post-execution: YES

Count: 2/3 phases
```

### Step 5: Calculate Score

**Component Assessment:**
- Error scenarios: 2 with recovery = 3/5 baseline
- Edge cases: 36% = Confirms 2/5
- Prerequisites: 3/4 partial = -1 point
- Validation: 2/3 phases = -1 point

**Final:** 2/5 (10 points) - Needs Work

### Step 6: Document in Review

```markdown
## Completeness: 2/5 (10 points)

**Error scenarios:** 2/5 documented with recovery
- [YES] File not found
- [YES] Timeout handling
- [NO] Network failures (missing)
- [PARTIAL] Permission errors (no recovery steps)
- [NO] Resource exhaustion (missing)

**Edge cases:** 36% coverage
- Boundary: 1/4
- Concurrency: 0/3
- State: 2/3
- Data: 2/4

**Prerequisites:** Partial (missing versions)
**Validation:** 2/3 phases (missing during-execution)

**Priority fixes:**
1. Add network failure handling
2. Add concurrency edge cases
3. Add tool version requirements
```

## Critical Dimension Override

If **both** Actionability ≤2/5 **and** Completeness ≤2/5:
- Overall verdict: **NOT_EXECUTABLE** (regardless of total score)
- Rule requires major rewrite
- Document as critical issue

## Inter-Run Consistency Target

**Expected variance:** ±1 point (within same tier)

**Counting verification:**
- Error scenarios: Count explicitly documented scenarios with recovery steps
- Edge cases: Use category checklist, count items addressed
- Prerequisites: Use 4-element checklist
- Validation: Use 3-phase checklist

**If variance exceeds threshold:**
- Re-count using checklists above
- Document ambiguous cases
