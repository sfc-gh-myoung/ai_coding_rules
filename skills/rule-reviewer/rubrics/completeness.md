# Completeness Rubric (15 points)

> **Weight:** 3 | **Max:** 15 points | **Formula:** Raw × 1.5

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

### Why This Is Required

- **Eliminates counting variance:** Same rule → same inventory → same score
- **Prevents false negatives:** Systematic enumeration catches all gaps
- **Provides evidence:** Inventory shows exactly what was evaluated
- **Enables verification:** Users can audit scoring decisions

### Inventory Template

| Line | Category | Item | Present? | Recovery Steps? | Notes |
|------|----------|------|----------|-----------------|-------|
| - | Error Scenarios | Input validation | Y/N | Y/N | |
| - | Error Scenarios | Execution errors | Y/N | Y/N | |
| - | Error Scenarios | External dependencies | Y/N | Y/N | |
| - | Error Scenarios | State inconsistencies | Y/N | Y/N | |
| - | Error Scenarios | Resource exhaustion | Y/N | Y/N | |
| - | Edge Cases | Boundary conditions | Y/N | - | Count: /4 |
| - | Edge Cases | Concurrency | Y/N | - | Count: /3 |
| - | Edge Cases | State transitions | Y/N | - | Count: /3 |
| - | Edge Cases | Data anomalies | Y/N | - | Count: /4 |
| - | Prerequisites | Tools required | Y/N | Versioned? | |
| - | Prerequisites | Permissions needed | Y/N | - | |
| - | Prerequisites | Environment state | Y/N | - | |
| - | Prerequisites | Data requirements | Y/N | - | |
| - | Validation | Pre-execution | Y/N | Commands? | |
| - | Validation | During execution | Y/N | Commands? | |
| - | Validation | Post-execution | Y/N | Commands? | |

### Counting Protocol (5 Steps)

**Step 1: Create Empty Inventory**
- Copy template above into working document
- Do NOT start reading rule yet

**Step 2: Read Rule Systematically**
- Start at line 1, read to END (no skipping)
- For EACH category item: Mark Y/N with line reference
- Note partial coverage with line numbers

**Step 3: Calculate Raw Totals**
- Error scenarios: Count present with recovery (max 5)
- Edge cases: Calculate coverage percentage
- Prerequisites: Count present with versions (max 4)
- Validation: Count phases present (max 3)

**Step 4: Check Non-Issues List**
- Review EACH "N" item in inventory
- Check against "Non-Issues" section below
- Mark justified absences
- Recalculate totals

**Step 5: Look Up Score**
- Use adjusted totals in Score Decision Matrix
- Record score with inventory evidence

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 3
**Points:** Raw × 1.5

## Scoring Criteria

### 10/10 (15 points): Perfect
- 5+ error scenarios with recovery steps
- All edge cases documented (boundary, concurrency, state)
- Prerequisites with version numbers
- Validation steps for pre/during/post execution
- Fallback strategies for critical operations

### 9/10 (13.5 points): Near-Perfect
- 5 error scenarios with recovery
- 95%+ edge cases covered
- All prerequisites stated with versions
- All validation phases present

### 8/10 (12 points): Excellent
- 4 error scenarios with recovery
- 90-94% edge cases covered
- Prerequisites stated with versions
- 3 validation phases present

### 7/10 (10.5 points): Good
- 3-4 error scenarios with recovery
- 85-89% edge cases covered
- Prerequisites stated (most versions)
- 3 validation phases present

### 6/10 (9 points): Acceptable
- 3 error scenarios with recovery
- 80-84% edge cases covered
- Most prerequisites stated
- 2-3 validation phases

### 5/10 (7.5 points): Borderline
- 2 error scenarios with recovery
- 70-79% edge cases covered
- Some prerequisites stated
- 2 validation phases

### 4/10 (6 points): Needs Work
- 2 error scenarios (partial recovery)
- 60-69% edge cases covered
- Prerequisites vague
- 1-2 validation phases

### 3/10 (4.5 points): Poor
- 1 error scenario with recovery
- 50-59% edge cases covered
- Prerequisites incomplete
- 1 validation phase

### 2/10 (3 points): Very Poor
- 1 error scenario (no recovery)
- 40-49% edge cases covered
- Prerequisites minimal
- Minimal validation

### 1/10 (1.5 points): Inadequate
- 0 error scenarios
- 25-39% edge cases covered
- Prerequisites missing
- No validation guidance

### 0/10 (0 points): Not Complete
- 0 error scenarios
- <25% edge cases covered
- No prerequisites
- No validation
- Not executable

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
- **10/10 (15 pts):** 5+ error scenarios, 95%+ edge cases, complete prerequisites, 3 validation phases
- **9/10 (13.5 pts):** 5 error scenarios, 95%+ edge cases, complete prerequisites, 3 validation phases
- **8/10 (12 pts):** 4 error scenarios, 90-94% edge cases, prerequisites with versions, 3 validation phases
- **7/10 (10.5 pts):** 3-4 error scenarios, 85-89% edge cases, most prerequisites, 3 validation phases
- **6/10 (9 pts):** 3 error scenarios, 80-84% edge cases, most prerequisites, 2-3 validation phases
- **5/10 (7.5 pts):** 2 error scenarios, 70-79% edge cases, some prerequisites, 2 validation phases
- **4/10 (6 pts):** 2 error scenarios (partial), 60-69% edge cases, vague prerequisites, 1-2 validation phases
- **3/10 (4.5 pts):** 1 error scenario, 50-59% edge cases, incomplete prerequisites, 1 validation phase
- **2/10 (3 pts):** 1 error (no recovery), 40-49% edge cases, minimal prerequisites, minimal validation
- **1/10 (1.5 pts):** 0 error scenarios, 25-39% edge cases, missing prerequisites, no validation
- **0/10 (0 pts):** 0 error scenarios, <25% edge cases, no prerequisites, no validation

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

**Final:** 4/10 (6 points) - Needs Work

### Step 6: Document in Review

```markdown
## Completeness: 4/10 (6 points)

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

If **both** Actionability ≤4/10 **and** Completeness ≤4/10:
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

## Non-Issues (Do NOT Count as Missing)

**Review EACH flagged gap against this list before counting.**

### Pattern 1: Intentionally Out of Scope
**Pattern:** Coverage area explicitly marked as out of scope
**Example:** Rule states "This rule does not cover error recovery for network failures"
**Why NOT an issue:** Scope is intentionally limited
**Action:** Remove from inventory with note "Explicitly out of scope"

### Pattern 2: Covered by Referenced Rule
**Pattern:** Coverage area is handled by a dependency
**Example:** Error handling covered by 000-global-core.md listed in Depends
**Why NOT an issue:** Dependency provides the coverage
**Action:** Remove from inventory with note "Covered by [dependency]"

### Pattern 3: Not Applicable to Domain
**Pattern:** Coverage area doesn't apply to rule's domain
**Example:** Concurrency edge cases for a single-threaded CLI tool
**Why NOT an issue:** Domain doesn't require this coverage
**Action:** Remove from inventory with note "Not applicable to domain"

### Pattern 4: Implicit in Examples
**Pattern:** Coverage is demonstrated in examples but not explicit prose
**Example:** Error handling shown in code example but not in dedicated section
**Why NOT an issue:** Coverage exists in alternative form (count as partial)
**Action:** Mark as "Partial" in inventory, not "Missing"

### Pattern 5: Version Agnostic by Design
**Pattern:** Tool references intentionally omit versions
**Example:** "Python 3.x" where any 3.x version works
**Why NOT an issue:** Version flexibility is intentional
**Action:** Remove from inventory with note "Version agnostic by design"

### Pattern 6: Self-Evident Prerequisites
**Pattern:** Prerequisites that are obvious from context
**Example:** "Snowflake account required" for a Snowflake-specific rule
**Why NOT an issue:** Prerequisite is self-evident from rule title/scope
**Action:** Remove from inventory with note "Self-evident from context"
