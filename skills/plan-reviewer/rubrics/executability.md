# Executability Rubric (20 points)

## Scoring Criteria

### 5/5 (20 points): Excellent
- All steps have explicit commands
- No ambiguous phrases
- All conditionals specify exact conditions
- No judgment calls required
- Agent can execute end-to-end

### 4/5 (16 points): Good
- Most steps explicit (1-3 ambiguous phrases)
- Most conditionals clear
- Minimal judgment needed

### 3/5 (12 points): Acceptable
- Some steps explicit (4-6 ambiguous phrases)
- Some conditionals clear
- Some judgment calls required

### 2/5 (8 points): Needs Work
- Few steps explicit (7-10 ambiguous phrases)
- Many conditionals unclear
- Frequent judgment calls

### 1/5 (4 points): Poor
- Most steps ambiguous (>10 phrases)
- Conditionals missing/unclear
- Requires constant human input

## Ambiguous Phrase Detection

Count phrases that require judgment:

### Category 1: Conditional Qualifiers

**Ambiguous:**
- "if appropriate"
- "if necessary"
- "as needed"
- "when suitable"
- "if required"

**Fix with explicit conditions:**
```diff
- Update dependencies if necessary
+ Update dependencies if package.json was modified
```

### Category 2: Vague Actions

**Ambiguous:**
- "consider doing X"
- "you may want to Y"
- "optionally do Z"
- "review and decide"

**Fix with explicit instructions:**
```diff
- Consider adding tests
+ Add tests for all new functions in src/
```

### Category 3: Undefined Thresholds

**Ambiguous:**
- "large file" (how large?)
- "significant changes" (how significant?)
- "many errors" (how many?)
- "slow performance" (how slow?)

**Fix with quantified thresholds:**
```diff
- If file is large, split it
+ If file is >500 lines, split it
```

### Category 4: Implicit Commands

**Ambiguous:**
- "Ensure X is configured" (how?)
- "Make sure Y works" (how?)
- "Verify Z is correct" (how?)

**Fix with explicit commands:**
```diff
- Ensure database is running
+ Start database: docker-compose up -d postgres
+ Verify: psql -c "SELECT 1"
```

## Ambiguity Tracking Table

Use during review:

| Line | Ambiguous Phrase | Type | Fix Needed |
|------|------------------|------|------------|
| 23 | "if necessary" | Conditional | Specify when necessary |
| 45 | "large table" | Threshold | Define size (>1M rows?) |
| 67 | "ensure configured" | Implicit | Provide config command |
| 89 | "consider adding" | Vague action | Make directive or remove |

**Count:** Total ambiguous phrases

## Conditional Completeness

Check that all conditionals have else branches:

**Incomplete:**
```markdown
If tests pass:
  - Deploy to production
```
→ What if tests fail? (no else branch)

**Complete:**
```markdown
If tests pass:
  - Deploy to production
Else:
  - Review test failures in CI logs
  - Fix failing tests
  - Re-run: pytest
```

## Command Explicitness

Every action should have an executable command:

**Bad (implicit):**
```markdown
1. Set up the database
2. Configure the application
3. Start the server
```

**Good (explicit):**
```markdown
1. Set up the database:
   ```bash
   createdb myapp_dev
   psql myapp_dev < schema.sql
   ```
2. Configure the application:
   ```bash
   cp .env.example .env
   vim .env  # Set DATABASE_URL
   ```
3. Start the server:
   ```bash
   python manage.py runserver
   ```
```

## Scoring Formula

```
Base score = 5/5 (20 points)

Ambiguous phrases:
  0-3: 5/5 (20 points)
  4-6: 4/5 (16 points)
  7-10: 3/5 (12 points)
  11-15: 2/5 (8 points)
  >15: 1/5 (4 points)

Additional deductions:
  Missing else branches: -0.5 per instance (up to -3)
  Implicit commands: -0.5 per instance (up to -3)

Minimum score: 1/5 (4 points)
```

## Pre-Scoring Gate: Agent Execution Test

Before scoring, count **blocking issues**:
1. Ambiguous phrases
2. Implicit commands
3. Missing conditional branches
4. Undefined thresholds

**Impact:**
- Blocking issues ≥10: Cap at 60/100 (NEEDS_REFINEMENT)
- Blocking issues ≥20: Cap at 40/100 (NOT_EXECUTABLE)

## Common Executability Issues

### Issue 1: Missing Conditions

**Problem:**
```markdown
If deployment succeeds, notify team
```

**Fix:**
```markdown
If deployment succeeds (exit code 0):
  - Post to Slack: #deploys channel
  - Message: "✓ Production deployed: v1.2.3"
Else (exit code non-zero):
  - Post to Slack: #incidents channel
  - Message: "❌ Deployment failed: see CI logs"
  - Do NOT merge PR
```

### Issue 2: Vague Actions

**Problem:**
```markdown
Review the code and make improvements
```

**Fix:**
```markdown
Run linter: ruff check src/
Fix all HIGH severity issues
Run formatter: ruff format src/
Verify: git diff shows only whitespace changes
```

### Issue 3: Undefined Thresholds

**Problem:**
```markdown
If performance is slow, optimize
```

**Fix:**
```markdown
Run benchmark: pytest tests/bench --benchmark-only
If p95 latency >500ms:
  - Profile with py-spy: py-spy record -o profile.svg -- python app.py
  - Optimize top 3 hotspots
  - Re-run benchmark to verify <500ms
```

### Issue 4: Implicit Commands

**Problem:**
```markdown
Make sure tests pass
```

**Fix:**
```markdown
Run tests: pytest tests/ -v
Expected: All tests pass (exit code 0)
If failures: Review output and fix issues
```

## Executability Checklist

During review, verify:

- [ ] All actions have explicit commands
- [ ] All conditionals specify exact conditions
- [ ] All if/when has corresponding else/default
- [ ] All thresholds quantified
- [ ] No "consider", "if appropriate", "as needed"
- [ ] No implicit commands ("ensure", "make sure", "verify" without how)
- [ ] Agent could execute without asking for clarification
- [ ] No judgment calls required
