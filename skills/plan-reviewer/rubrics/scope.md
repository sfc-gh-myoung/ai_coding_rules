# Scope Rubric (15 points)

## Scoring Criteria

### 5/5 (15 points): Excellent
- Clear scope boundaries
- Explicit inclusions
- Explicit exclusions
- Termination conditions defined
- Work is bounded and finite

### 4/5 (12 points): Good
- Scope mostly clear (1 boundary fuzzy)
- Most inclusions clear
- Some exclusions stated

### 3/5 (9 points): Acceptable
- Scope somewhat clear (2-3 boundaries fuzzy)
- Some inclusions clear
- Few exclusions

### 2/5 (6 points): Needs Work
- Scope unclear (4+ boundaries fuzzy)
- Inclusions vague
- No exclusions

### 1/5 (3 points): Poor
- Unbounded scope
- No boundaries
- Never-ending work

## Scope Definition Requirements

### 1. In-Scope (Inclusions)

Explicitly state what IS included:

**Good example:**
```markdown
## In-Scope

- Migrate user authentication from custom to OAuth2
- Update login/logout flows
- Migrate existing user accounts
- Update documentation
- Deploy to staging and production
```

### 2. Out-of-Scope (Exclusions)

Explicitly state what is NOT included:

**Good example:**
```markdown
## Out-of-Scope

- Social login (Google, Facebook) - Future work
- Password reset flow - Already OAuth-managed
- Admin authentication - Separate system
- Mobile app login - Separate ticket #456
```

### 3. Termination Conditions

Define when work is complete:

**Good example:**
```markdown
## Done When

1. All tests pass (pytest exit code 0)
2. OAuth login works in staging
3. All 10,000 users migrated successfully
4. Documentation updated
5. Production deployed
6. Monitoring shows 0 auth errors for 24 hours
```

## Unbounded Scope Detection

Watch for open-ended phrases:

**Red flags:**
- "Improve X" (how much? when done?)
- "Optimize Y" (to what target?)
- "Refactor Z" (what's the endpoint?)
- "As needed" (infinite work)
- "Ongoing" (no termination)
- "Continue until..." (no explicit condition)

**Fix with boundaries:**
```diff
- Improve test coverage
+ Increase test coverage from 70% to 90% for src/auth/ module
```

## Scope Boundary Verification

Create table tracking boundaries:

| Boundary | Defined? | How Defined | Clear? |
|----------|----------|-------------|--------|
| What to change | ✅ Yes | src/auth/ module only | ✅ Clear |
| How much to change | ✅ Yes | OAuth migration complete | ✅ Clear |
| When to stop | ✅ Yes | 6 done criteria listed | ✅ Clear |
| What NOT to change | ✅ Yes | Out-of-scope section | ✅ Clear |

## Scoring Formula

```
Base score = 5/5 (15 points)

Scope definition:
  All 4 boundaries clear: 5/5 (15 points)
  3/4 boundaries clear: 4/5 (12 points)
  2/4 boundaries clear: 3/5 (9 points)
  1/4 boundaries clear: 2/5 (6 points)
  0/4 boundaries clear: 1/5 (3 points)

Additional deductions:
  No termination conditions: -3 points (CRITICAL)
  Unbounded phrases present: -0.5 each (up to -2)
  No exclusions: -1 point

Minimum score: 1/5 (3 points)
```

## Critical Gate

If scope is unbounded (no termination conditions):
- Cap score at 2/5 (6 points) maximum
- Mark as CRITICAL issue
- Work never completes

## Common Scope Issues

### Issue 1: No Boundaries

**Problem:**
```markdown
Refactor the codebase to be better
```

**Fix:**
```markdown
## Goal
Refactor src/auth/ module to use OAuth2

## In-Scope
- Replace custom auth with OAuth2 library
- Update 5 authentication endpoints
- Migrate 10,000 user accounts

## Out-of-Scope
- Other modules (src/api/, src/admin/)
- Performance optimization (separate ticket)
- New features (separate tickets)

## Done When
- All src/auth/ tests pass
- OAuth working in production
- Zero custom auth code remains in src/auth/
- Documentation updated
```

### Issue 2: Vague Termination

**Problem:**
```markdown
Done when performance is good enough
```

**Fix:**
```markdown
Done when:
1. P95 latency <500ms (benchmark: pytest tests/bench/)
2. Error rate <0.1% (logs: grep ERROR | wc -l)
3. Load test passes: 1000 RPS sustained for 5 minutes
4. Monitoring shows no alerts for 24 hours
```

### Issue 3: No Exclusions

**Problem:**
```markdown
Migrate to new database
(No exclusions stated)
```

**Fix:**
```markdown
## In-Scope
- Migrate users table to PostgreSQL
- Update user queries

## Out-of-Scope (future work)
- Products table migration - Ticket #457
- Orders table migration - Ticket #458
- Analytics migration - Ticket #459
- Data warehouse sync - Separate project
```

### Issue 4: Open-Ended Work

**Problem:**
```markdown
Improve error handling throughout the application
```

**Fix:**
```markdown
## Goal
Add error handling to src/api/ module

## In-Scope
- Add try/except to all 15 API endpoints
- Return proper HTTP status codes (400/500)
- Log all errors to logs/errors.log

## Out-of-Scope
- Frontend error handling (separate ticket)
- Background job errors (separate ticket)
- Database error handling (already implemented)

## Done When
1. All 15 endpoints have error handling
2. Test suite includes error cases (100% coverage)
3. No unhandled exceptions in API layer
4. Error log format validated: grep ERROR logs/errors.log
```

## Scope Checklist

During review, verify:

- [ ] In-scope items explicitly listed
- [ ] Out-of-scope items explicitly listed
- [ ] Termination conditions defined (done when...)
- [ ] Work is bounded (not open-ended)
- [ ] No phrases like "improve", "optimize" without targets
- [ ] Clear boundaries (what/how much/when/what not)
- [ ] Exclusions prevent scope creep
- [ ] Completion is verifiable
