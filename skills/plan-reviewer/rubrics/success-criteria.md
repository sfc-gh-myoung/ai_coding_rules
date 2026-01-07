# Success Criteria Rubric (20 points)

## Scoring Criteria

### 5/5 (20 points): Excellent
- All tasks have completion signals
- All criteria are measurable
- All criteria are agent-testable
- Clear "done" definition
- Verification steps explicit

### 4/5 (16 points): Good
- Most tasks have criteria (90%+)
- Most measurable
- Most agent-testable

### 3/5 (12 points): Acceptable
- Some tasks have criteria (70-89%)
- Some measurable
- Some agent-testable

### 2/5 (8 points): Needs Work
- Few tasks have criteria (50-69%)
- Few measurable
- Few agent-testable

### 1/5 (4 points): Poor
- Most tasks lack criteria (<50%)
- Not measurable
- Not agent-testable

## Completion Signal Types

### Type 1: Exit Codes

**Good:**
```markdown
Task: Run tests
Success: Exit code 0
Failure: Exit code non-zero
```

### Type 2: File Existence

**Good:**
```markdown
Task: Build artifacts
Success: dist/app.tar.gz exists AND size >1MB
Failure: File missing OR size <1MB
```

### Type 3: Output Content

**Good:**
```markdown
Task: Apply migrations
Success: Output contains "Applied 5 migrations"
Failure: Output contains "Error:" OR "Failed:"
```

### Type 4: State Verification

**Good:**
```markdown
Task: Start server
Success: curl localhost:8000/health returns 200
Failure: Connection refused OR non-200 status
```

## Agent-Testable Criteria

Criteria must be verifiable by agent without human:

**Not agent-testable:**
- "Code looks good" (subjective)
- "Performance seems better" (vague)
- "UI is user-friendly" (requires human)

**Agent-testable:**
- "All tests pass (pytest exit code 0)"
- "Latency <500ms (benchmark output)"
- "All linter errors resolved (ruff exit code 0)"

## Measurable Criteria

All criteria must be quantified:

**Vague (not measurable):**
```markdown
- Code is clean
- Performance is good
- Few errors
```

**Measurable:**
```markdown
- Linter score: 10/10 (ruff check exit code 0)
- P95 latency: <500ms (benchmark output)
- Error rate: <1% (logs show <10 errors/1000 requests)
```

## Coverage Tracking

Count tasks with/without criteria:

| Task | Line | Has Criteria? | Measurable? | Agent-Testable? |
|------|------|---------------|-------------|-----------------|
| Run tests | 23 | ✅ Yes | ✅ Yes (exit code) | ✅ Yes |
| Refactor code | 45 | ❌ No | ❌ No | ❌ No |
| Deploy app | 67 | ✅ Yes | ✅ Yes (HTTP 200) | ✅ Yes |
| Improve UX | 89 | ❌ No | ❌ No | ❌ No |

**Coverage:** 2/4 tasks (50%) → Score: 2/5 (8 points)

## Scoring Formula

```
Base score = 5/5 (20 points)

Task coverage:
  90-100%: 5/5 (20 points)
  70-89%: 4/5 (16 points)
  50-69%: 3/5 (12 points)
  30-49%: 2/5 (8 points)
  <30%: 1/5 (4 points)

Additional requirements:
  <50% measurable: -2 points
  <50% agent-testable: -2 points

Minimum score: 1/5 (4 points)
```

## Critical Gate

If <50% of tasks have success criteria:
- Cap score at 2/5 (8 points) maximum
- Mark as CRITICAL issue
- Agent cannot determine completion

## Common Success Criteria Issues

### Issue 1: No Completion Signal

**Problem:**
```markdown
Task: Update dependencies
```

**Fix:**
```markdown
Task: Update dependencies

Steps:
1. Run: uv pip compile pyproject.toml -o requirements.txt
2. Run: uv pip install -r requirements.txt

Success criteria:
- requirements.txt modified (git diff shows changes)
- Install exit code: 0
- Import test: python -c "import flask; print(flask.__version__)" outputs 3.0.0+

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
- Linter score: 10/10 (ruff check src/ exit code 0)
- Test coverage: ≥90% (pytest --cov shows ≥90%)
- No TODO comments: grep -r "TODO" src/ returns empty
```

### Issue 3: Not Agent-Testable

**Problem:**
```markdown
Success: UI looks professional
```

**Fix:**
```markdown
Success:
- Lighthouse accessibility score: ≥95 (lighthouse --only-categories accessibility)
- No console errors: Browser console shows 0 errors
- All links work: linkchecker http://localhost:3000 exit code 0
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
1. Deployment script exit code: 0
2. Health check: curl https://app.com/health returns 200
3. Version check: curl https://app.com/version returns expected version
4. Error rate: <1% over 5 minutes (check monitoring dashboard)
5. Rollback ready: Previous version tagged in git

Verification steps:
for i in {1..5}; do
  curl -f https://app.com/health || exit 1
  sleep 1
done
echo "✓ Health checks passed"
```

## Success Criteria Checklist

During review, verify:

- [ ] Every task has completion criteria
- [ ] All criteria are measurable (numbers, exit codes, file existence)
- [ ] All criteria are agent-testable (no human judgment)
- [ ] Verification commands provided
- [ ] Both success AND failure conditions defined
- [ ] Multiple criteria use AND/OR logic explicitly
- [ ] Criteria include HOW to verify, not just WHAT
