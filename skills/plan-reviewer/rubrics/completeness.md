# Completeness Rubric (20 points)

## Scoring Criteria

### 5/5 (20 points): Excellent
- Setup steps complete
- Validation checks present
- Error recovery defined
- Cleanup steps included
- Edge cases addressed

### 4/5 (16 points): Good
- Setup mostly complete (1 step missing)
- Most validation present
- Basic error recovery
- Cleanup mostly present

### 3/5 (12 points): Acceptable
- Setup has gaps (2-3 steps missing)
- Some validation present
- Limited error recovery
- Some cleanup missing

### 2/5 (8 points): Needs Work
- Setup incomplete (4+ steps missing)
- Little validation
- Minimal error recovery
- Cleanup mostly missing

### 1/5 (4 points): Poor
- Setup missing
- No validation
- No error recovery
- No cleanup

## Required Components Checklist

### Setup Phase

Must include:
- [ ] Prerequisites verification
- [ ] Environment preparation
- [ ] Dependency installation
- [ ] Configuration setup
- [ ] Initial state verification

**Example:**
```markdown
## Setup

1. Verify prerequisites:
   - Python 3.11+: python --version
   - PostgreSQL running: pg_isready

2. Create virtual environment:
   uv venv

3. Install dependencies:
   uv pip install -r requirements.txt

4. Configure:
   cp .env.example .env
   # Edit DATABASE_URL

5. Verify setup:
   pytest tests/smoke/test_connection.py
```

### Validation Checks

Plans must include verification steps:

**After each major action:**
- [ ] Command execution verified
- [ ] Output validated
- [ ] State confirmed

**Example:**
```markdown
## Step 3: Apply Migrations

Command: python manage.py migrate

Validation:
- Exit code: 0
- Output: "Applied X migrations"
- Verify: psql -c "\dt" shows all tables
```

### Error Recovery

Must address failures:

- [ ] What can go wrong
- [ ] How to detect failures
- [ ] Recovery steps
- [ ] Rollback procedures

**Example:**
```markdown
## Error Recovery

### Migration Failure

Detection: Exit code non-zero OR "Error:" in output

Recovery:
1. Check logs: tail -f logs/migrate.log
2. Identify failed migration
3. Manual fix: psql myapp_dev < migrations/XXX_fix.sql
4. Re-run: python manage.py migrate
5. If still fails: Rollback to previous version

Rollback:
git checkout v1.2.3
python manage.py migrate --fake-initial
```

### Cleanup Phase

Must include:
- [ ] Temporary files removed
- [ ] Resources released
- [ ] State reset (if needed)
- [ ] Verification of cleanup

**Example:**
```markdown
## Cleanup

1. Remove temp files:
   rm -rf /tmp/build-*

2. Stop services:
   docker-compose down

3. Clear cache:
   rm -rf .cache/

4. Verify:
   ls /tmp/build-* (should error: No such file)
```

## Edge Cases Coverage

### Common Edge Cases

Plans should address:

**Empty states:**
- [ ] What if database is empty?
- [ ] What if no users exist?
- [ ] What if cache is cold?

**Concurrent execution:**
- [ ] What if plan runs twice simultaneously?
- [ ] Lock files needed?
- [ ] Race condition handling?

**Partial completion:**
- [ ] What if plan interrupted mid-execution?
- [ ] Resume from checkpoint?
- [ ] Idempotency guaranteed?

**Resource constraints:**
- [ ] What if disk full?
- [ ] What if memory limited?
- [ ] What if network unreliable?

## Scoring Formula

```
Base score = 5/5 (20 points)

Missing components:
  Setup incomplete: -1 per missing step (up to -4)
  No validation: -2 points
  No error recovery: -3 points (CRITICAL)
  No cleanup: -1 point
  Edge cases ignored: -0.5 each (up to -2)

Minimum score: 1/5 (4 points)
```

## Critical Gate

If error recovery is missing:
- Cap score at 2/5 (8 points) maximum
- Mark as CRITICAL issue
- Plan fails on first error

## Completeness Tracking Table

Use during review:

| Component | Present? | Coverage | Missing Items |
|-----------|----------|----------|---------------|
| Setup | ✅ Yes | 100% | - |
| Validation | ⚠️  Partial | 60% | 2 steps missing checks |
| Error recovery | ❌ No | 0% | No recovery defined |
| Cleanup | ✅ Yes | 100% | - |
| Edge cases | ⚠️  Partial | 40% | 3 cases not addressed |

**Score calculation:**
- Setup: ✅ (0 deduction)
- Validation: -1 point (partial)
- Error recovery: -3 points (CRITICAL MISSING)
- Cleanup: ✅ (0 deduction)
- Edge cases: -1 point (3 missing)
- Total deductions: -5 points
- Score: 0/5 → But CRITICAL issue caps at 2/5 (8 points)
