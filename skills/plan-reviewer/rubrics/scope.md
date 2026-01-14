# Scope Rubric (15 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 3
**Points:** Raw × (3/2) = Raw × 1.5

## Scoring Criteria

### 10/10 (15 points): Perfect
- 4/4 boundary types defined (what, how much, when, what not)
- Explicit in-scope list (6+ items)
- Explicit out-of-scope list (4+ items)
- Termination conditions with verification
- 0 unbounded phrases

### 9/10 (13.5 points): Near-Perfect
- 4/4 boundary types defined
- Explicit in-scope list (5+ items)
- Explicit out-of-scope list (3+ items)
- Termination conditions with verification
- 1 unbounded phrase

### 8/10 (12 points): Excellent
- 4/4 boundary types defined
- Explicit in-scope list (5+ items)
- Explicit out-of-scope list (3+ items)
- Termination conditions present
- 1-2 unbounded phrases

### 7/10 (10.5 points): Good
- 3/4 boundary types defined
- In-scope list present (4+ items)
- Some exclusions stated (2+ items)
- Termination conditions present
- 2-3 unbounded phrases

### 6/10 (9 points): Acceptable
- 3/4 boundary types defined
- In-scope list present (3-4 items)
- Some exclusions stated (1-2 items)
- Termination conditions present
- 3-4 unbounded phrases

### 5/10 (7.5 points): Borderline
- 2/4 boundary types defined
- Partial in-scope list (2-3 items)
- Few exclusions (1 item)
- Vague termination
- 4-5 unbounded phrases

### 4/10 (6 points): Needs Work
- 2/4 boundary types defined
- Partial in-scope list (1-2 items)
- Few exclusions (0-1 items)
- Vague termination
- 5-6 unbounded phrases

### 3/10 (4.5 points): Poor
- 1/4 boundary types defined
- Inclusions vague
- No exclusions
- No termination conditions
- 6-7 unbounded phrases

### 2/10 (3 points): Very Poor
- 1/4 boundary types defined
- Inclusions vague
- No exclusions
- No termination conditions
- 7-8 unbounded phrases

### 1/10 (1.5 points): Inadequate
- 0/4 boundary types defined
- Unbounded scope
- No boundaries
- Never-ending work
- >8 unbounded phrases

### 0/10 (0 points): No Scope
- 0/4 boundary types defined
- Completely unbounded
- Cannot determine completion

## Counting Definitions

### Boundary Types

**Four boundary types (count 0-4):**

**Boundary Checklist:**
- What to change: What files/components? Present? Clear?
- How much to change: What level of change? Present? Clear?
- When to stop: What are done conditions? Present? Clear?
- What NOT to change: What is excluded? Present? Clear?

**Scoring:**
- 4/4 clear: 5/5 eligible
- 3/4 clear: 4/5 maximum
- 2/4 clear: 3/5 maximum
- 1/4 clear: 2/5 maximum
- 0/4 clear: 1/5 maximum

### Unbounded Phrases

**Count each occurrence (1 issue each):**

**Unbounded Phrase Patterns:**
- "Improve X": Unbounded - improve how much?
- "Optimize Y": Unbounded - optimize to what target?
- "Refactor Z": Unbounded - refactor to what endpoint?
- "As needed": Unbounded - infinite work possible
- "Ongoing": Unbounded - no termination
- "Continue until...": Unbounded - vague condition
- "Clean up": Unbounded - clean to what standard?
- "Enhance": Unbounded - enhance to what level?

### In-Scope Clarity

**Count explicit items:**
- Named files/directories
- Specific components
- Defined deliverables

**Scoring:**
- 5+ explicit items: Full credit
- 3-4 explicit items: -1 point
- 1-2 explicit items: -2 points
- 0 explicit items: -3 points

### Out-of-Scope Clarity

**Count explicit exclusions:**
- Named items NOT being changed
- Future work items
- Related but separate concerns

**Scoring:**
- 3+ explicit exclusions: Full credit
- 1-2 explicit exclusions: -1 point
- 0 explicit exclusions: -2 points

### Termination Conditions

**Requirements:**
- Explicit "done when" list
- Measurable criteria
- Verifiable by agent

**Scoring:**
- Measurable + verifiable: Full credit
- Present but vague: -2 points
- Missing: -4 points (CRITICAL)

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (15 pts):** 4/4 boundaries, 0 unbounded, 6+ in-scope items, 4+ out-of-scope items, measurable termination
- **9/10 (13.5 pts):** 4/4 boundaries, 1 unbounded, 5+ in-scope items, 3+ out-of-scope items, measurable termination
- **8/10 (12 pts):** 4/4 boundaries, 1-2 unbounded, 5+ in-scope items, 3+ out-of-scope items, present termination
- **7/10 (10.5 pts):** 3/4 boundaries, 2-3 unbounded, 4+ in-scope items, 2+ out-of-scope items, present termination
- **6/10 (9 pts):** 3/4 boundaries, 3-4 unbounded, 3-4 in-scope items, 1-2 out-of-scope items, present termination
- **5/10 (7.5 pts):** 2/4 boundaries, 4-5 unbounded, 2-3 in-scope items, 1 out-of-scope item, vague termination
- **4/10 (6 pts):** 2/4 boundaries, 5-6 unbounded, 1-2 in-scope items, 0-1 out-of-scope items, vague termination
- **3/10 (4.5 pts):** 1/4 boundaries, 6-7 unbounded, vague in-scope, none out-of-scope, missing termination
- **2/10 (3 pts):** 1/4 boundaries, 7-8 unbounded, vague in-scope, none out-of-scope, missing termination
- **1/10 (1.5 pts):** 0/4 boundaries, >8 unbounded, none in-scope, none out-of-scope, missing termination
- **0/10 (0 pts):** 0/4 boundaries, completely unbounded, cannot determine completion

**Critical gate:** If termination conditions missing, cap at 4/10 (6 points)

## Boundary Verification Table

Use during review:

**Boundary Verification Checklist:**
- What to change: Defined? Description? Clear?
- How much to change: Defined? Description? Clear?
- When to stop: Defined? Description? Clear?
- What NOT to change: Defined? Description? Clear?

## Unbounded Phrase Tracking

**Unbounded Phrase Inventory (example):**
- "Improve performance" (line 45): Specify target - "<500ms p95"
- "Refactor code" (line 67): Specify endpoint - "extract 3 classes"
- "As needed" (line 89): Specify condition - "if >100 errors/hour"

**Count:** ___

## Scope Definition Examples

### In-Scope (Good)

```markdown
## In-Scope

- Migrate user authentication from custom to OAuth2
- Update login/logout flows in src/auth/
- Migrate existing 10,000 user accounts
- Update authentication tests in tests/auth/
- Update API documentation in docs/api/auth.md
- Deploy to staging and production
```

**Count:** 6 explicit items

### Out-of-Scope (Good)

```markdown
## Out-of-Scope

- Social login (Google, Facebook) - Future: Ticket #457
- Password reset flow - Already OAuth-managed
- Admin authentication - Separate system, Ticket #458
- Mobile app login - Separate team, Ticket #459
- API rate limiting - Separate concern
```

**Count:** 5 explicit exclusions

### Termination Conditions (Good)

```markdown
## Done When

1. All src/auth/ tests pass (pytest exit code 0)
2. OAuth login works in staging (manual verification)
3. All 10,000 users migrated (migration script output: "10000 migrated")
4. Documentation updated (docs/api/auth.md modified)
5. Production deployed (health check returns 200)
6. Monitoring shows 0 auth errors for 24 hours
```

**Quality:** Measurable, verifiable

### Unbounded Scope (Bad)

```markdown
BAD:
Refactor the codebase to be better

Issues:
- "Refactor" - unbounded (1)
- "better" - undefined target (1)
- No in-scope items
- No out-of-scope items
- No termination conditions
```

### Bounded Scope (Good)

```markdown
GOOD:
## Goal
Refactor src/auth/ module to use OAuth2

## In-Scope
- Replace custom auth with OAuth2 library
- Update 5 authentication endpoints
- Migrate 10,000 user accounts

## Out-of-Scope
- Other modules (src/api/, src/admin/)
- Performance optimization (Ticket #460)
- New features (separate tickets)

## Done When
- All src/auth/ tests pass
- OAuth working in production
- Zero custom auth code remains in src/auth/
- Documentation updated
```

## Worked Example

**Target:** Feature plan

### Step 1: Check Boundaries

**Boundary Assessment:**
- What to change: Yes - "src/auth/ module"
- How much: Yes - "OAuth2 migration"
- When to stop: Partial - "When complete" (vague)
- What NOT: No - Not stated

**Count:** 2/4 boundaries clear

### Step 2: Count Unbounded Phrases

**Unbounded Phrase Inventory:**
- "Improve performance" (line 45)
- "Clean up code" (line 67)
- "As needed" (line 89)

**Count:** 3 unbounded phrases

### Step 3: Assess In-Scope

```markdown
In-scope items:
- OAuth2 library integration
- Login endpoint
- Logout endpoint
- Token refresh
```

**Count:** 4 explicit items

### Step 4: Assess Out-of-Scope

```markdown
Out-of-scope: (none stated)
```

**Count:** 0 exclusions

### Step 5: Assess Termination

```markdown
"Complete when OAuth works"
```

**Quality:** Present but vague (-2 points)

### Step 6: Calculate Score

**Component Assessment:**
- Boundaries: 2/4 = 3/5 baseline
- Unbounded phrases: 3 = Within range
- In-scope: 4 items = -1 point
- Out-of-scope: 0 items = -2 points
- Termination: Vague = -2 points

**Total deductions:** -5 points
**Final:** 3/5 - 5 = Too low, Minimum 3/5 (9 points)

Wait, recalculate: 3/5 baseline (9 pts), no additional deductions apply within tier.

**Final:** 5/10 (7.5 points)

### Step 7: Document in Review

```markdown
## Scope: 5/10 (7.5 points)

**Boundaries defined:** 2/4
- [YES] What to change: src/auth/ module
- [YES] How much: OAuth2 migration
- [PARTIAL] When to stop: Vague ("when complete")
- [NO] What NOT: Not stated

**Unbounded phrases:** 3
- Line 45: "Improve performance"
- Line 67: "Clean up code"
- Line 89: "As needed"

**In-scope:** 4 items (partial)
**Out-of-scope:** 0 items (missing)

**Termination:** Present but vague

**Priority fixes:**
1. Add explicit out-of-scope section
2. Replace "when complete" with measurable criteria
3. Remove or quantify unbounded phrases
```

## Scope Checklist

During review, verify:

- [ ] In-scope items explicitly listed
- [ ] Out-of-scope items explicitly listed
- [ ] Termination conditions defined (done when...)
- [ ] Work is bounded (not open-ended)
- [ ] No unbounded phrases ("improve", "optimize" without targets)
- [ ] Clear boundaries (what/how much/when/what not)
- [ ] Exclusions prevent scope creep
- [ ] Completion is verifiable

## Inter-Run Consistency Target

**Expected variance:** ±1 boundary count

**Verification:**
- Use 4-boundary checklist
- Count unbounded phrases with line numbers
- Count in-scope/out-of-scope items explicitly

**If variance exceeds threshold:**
- Re-verify using boundary table
- Apply phrase definitions strictly
