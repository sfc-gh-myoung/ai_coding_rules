# Completeness Rubric (25 points)

## Scoring Criteria

### 5/5 (25 points): Excellent
- Comprehensive error handling with recovery steps
- All edge cases documented
- Clear prerequisites and assumptions
- Explicit validation steps
- Fallback strategies for failures
- Example outputs provided

### 4/5 (20 points): Good
- Error handling present but 1-2 scenarios missing
- Most edge cases covered
- Prerequisites stated
- Validation steps present
- Some recovery procedures missing

### 3/5 (15 points): Acceptable
- Basic error handling (3-4 scenarios missing)
- Major edge cases covered, minor ones missing
- Some prerequisites stated
- Validation steps incomplete
- Limited fallback strategies

### 2/5 (10 points): Needs Work
- Minimal error handling (>5 scenarios missing)
- Edge cases rarely addressed
- Prerequisites vague or missing
- Validation steps sparse
- No fallback strategies

### 1/5 (5 points): Poor
- No error handling
- Edge cases not considered
- Prerequisites unstated
- No validation guidance
- No recovery procedures

## Required Coverage Areas

### 1. Error Handling

Must address:
- **Input validation failures** (malformed data, missing files)
- **Execution errors** (timeouts, permission denied, resource exhausted)
- **External dependencies** (network failures, API errors, missing tools)
- **State inconsistencies** (concurrent modifications, race conditions)

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

Must cover:
- **Boundary conditions** (empty inputs, maximum sizes, null values)
- **Concurrency** (multiple users, simultaneous modifications)
- **State transitions** (initialization, updates, cleanup)
- **Data anomalies** (duplicates, missing values, format issues)

### 3. Prerequisites and Assumptions

Must document:
- **Tools required** (with version numbers)
- **Permissions needed** (specific privileges)
- **Environment state** (files exist, services running)
- **Data requirements** (format, size, structure)

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

Must specify:
- **Pre-execution checks** (prerequisites met, inputs valid)
- **During execution** (progress monitoring, intermediate validation)
- **Post-execution** (output verification, state consistency)

### 5. Fallback Strategies

For critical operations, provide:
- **Alternative approaches** if primary method fails
- **Rollback procedures** for reversible operations
- **Manual intervention steps** when automation fails

## Scoring Formula

```
Base score = 5/5 (25 points)

Missing error handling scenarios: -1 point each (up to -10)
Missing edge cases: -0.5 points each (up to -5)
Vague prerequisites: -1 point
Incomplete validation: -1 point each step (up to -3)
No fallback strategies: -2 points

Minimum score: 1/5 (5 points)
```

## Critical Dimension Override

If **both** Actionability ≤2/5 **and** Completeness ≤2/5:
- Overall verdict: **NOT_EXECUTABLE** (regardless of total score)
- Rule requires major rewrite
- Document as critical issue

## Common Completeness Gaps

### Gap 1: No Error Recovery
```markdown
❌ BAD:
"Run the script"

✅ GOOD:
"Run: python script.py
If exits with code 1: Check logs at /var/log/app.log
If timeout: Increase timeout parameter --timeout 60
If permission denied: Request sudo access or change file ownership"
```

### Gap 2: Missing Prerequisites
```markdown
❌ BAD:
"Configure the database connection"

✅ GOOD:
"Prerequisites:
- PostgreSQL 15+ installed
- User account with CREATEDB privilege
- Network access to host:5432
- Environment variable DB_PASSWORD set"
```

### Gap 3: No Validation Steps
```markdown
❌ BAD:
"Deploy the application"

✅ GOOD:
"Deploy the application:
1. Build: task build
2. Validate: task validate (linting + tests must pass)
3. Deploy: task deploy
4. Verify: curl https://app.example.com/health (expect 200 OK)"
```

## Edge Case Coverage Examples

**Good Coverage:**
- Handles empty inputs, null values, and missing fields
- Documents behavior for concurrent modifications
- Specifies cleanup for partial failures
- Addresses timezone and locale differences
- Covers maximum size/count limits

**Poor Coverage:**
- Only happy-path documented
- No mention of failure scenarios
- Assumes ideal conditions
- No boundary condition testing
