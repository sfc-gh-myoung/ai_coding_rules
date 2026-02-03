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

## Out-of-Scope Handling Rule

**DO NOT score as unbounded if:**
- Explicitly marked "not in scope" or "out of scope"
- Documented as "Phase X - Not executed in this plan"
- Listed under "Future Work" or "Not Included"
- Explicitly deferred with ticket reference ("Ticket #457")

**DO score as unbounded if:**
- Mentioned without exclusion qualifier
- Boundary unclear ("may include..." without limit)
- Open-ended language ("and more", "etc.", "as needed")
- No termination condition for the item

**Examples:**

```markdown
# NOT unbounded (correctly excluded):
"Social login - out of scope for this phase"
"Performance optimization - Future Work (Ticket #460)"
"Admin features - Phase 2, not this plan"

# IS unbounded (needs fixing):
"Improve performance as needed"
"Handle edge cases appropriately"  
"Update documentation and more"
```

## Scoring Thresholds (Clarified)

**Threshold Boundaries:**
- Unbounded phrase counts use exclusive boundaries for penalties
- "0 unbounded" = full credit, "1 unbounded" = -1 tier
- Round counts to nearest integer (no fractional unbounded phrases)

**Edge Case Rules:**
- When phrase is borderline, apply Ambiguous Case Resolution Rules
- Document reasoning for borderline classifications in worksheet

## Score Decision Matrix (ENHANCED)

**Purpose:** Convert boundary counts, scope items, and unbounded phrases into dimension score. No interpretation needed - just look up the tier.

### Input Values

From completed worksheet:
- **Boundaries Defined:** Count of 4 boundary types (what/how much/when/what NOT)
- **In-Scope Items:** Count of explicit items
- **Out-of-Scope Items:** Count of explicit exclusions
- **Unbounded Phrases:** Count of vague/open-ended language
- **Termination Quality:** Measurable/Vague/Missing

### Scoring Table

| Boundaries | Unbounded | In-Scope | Out-Scope | Termination | Tier | Raw Score | × Weight | Points |
|------------|-----------|----------|-----------|-------------|------|-----------|----------|--------|
| 4/4 | 0 | 6+ | 4+ | Measurable | Perfect | 10/10 | × 1.5 | 15 |
| 4/4 | 1 | 5+ | 3+ | Measurable | Near-Perfect | 9/10 | × 1.5 | 13.5 |
| 4/4 | 1-2 | 5+ | 3+ | Present | Excellent | 8/10 | × 1.5 | 12 |
| 3/4 | 2-3 | 4+ | 2+ | Present | Good | 7/10 | × 1.5 | 10.5 |
| 3/4 | 3-4 | 3-4 | 1-2 | Present | Acceptable | 6/10 | × 1.5 | 9 |
| 2/4 | 4-5 | 2-3 | 1 | Vague | Borderline | 5/10 | × 1.5 | 7.5 |
| 2/4 | 5-6 | 1-2 | 0-1 | Vague | Below Standard | 4/10 | × 1.5 | 6 |
| 1/4 | 6-7 | Vague | 0 | Missing | Poor | 3/10 | × 1.5 | 4.5 |
| 1/4 | 7-8 | Vague | 0 | Missing | Very Poor | 2/10 | × 1.5 | 3 |
| 0/4 | >8 | None | 0 | Missing | Critical | 1/10 | × 1.5 | 1.5 |
| 0/4 | Unbounded | None | 0 | Missing | No Scope | 0/10 | × 1.5 | 0 |

**Critical Gate:** If termination conditions missing, cap at 4/10 (6 points)

### Tie-Breaking Algorithm (Deterministic)

**When metrics fall on tier boundary:**

Execute this algorithm in order. STOP at first decisive result.

1. **Check Boundaries:** If boundaries > tier minimum → HIGHER tier
2. **Check Unbounded Phrases:** If unbounded < tier maximum → HIGHER tier
3. **Check Termination Quality:**
   - Measurable + verifiable → HIGHER tier
   - Present but vague → Stay at tier
   - Missing → LOWER tier
4. **Default:** LOWER tier (conservative - scope issues are serious)

### Edge Cases

**Edge Case 1: Narrow scope with implicit exclusions**
- **Example:** "Update only src/auth/login.py" (no explicit out-of-scope)
- **Rule:** Count narrow focus as implicit out-of-scope if unambiguous
- **Rationale:** Extremely narrow scope = everything else excluded

**Edge Case 2: Measurable phrases that appear unbounded**
- **Example:** "Improve performance" followed by "<500ms p95" on next line
- **Rule:** Check ±5 lines for quantification before flagging
- **Rationale:** Target may be specified nearby

**Edge Case 3: "Future Work" section instead of "Out-of-Scope"**
- **Example:** "Future Work: Social login, Admin dashboard"
- **Rule:** Count Future Work items as out-of-scope equivalents
- **Rationale:** Same function (exclusion), different label

### Worked Example

**Scenario:** Plan with 3/4 boundaries, 2 unbounded phrases, 5 in-scope, 2 out-of-scope, present termination

**Step 1:** Extract metrics
- Boundaries: 3/4
- Unbounded: 2
- In-scope: 5
- Out-of-scope: 2
- Termination: Present (not measurable)

**Step 2:** Look up in scoring table
- 3/4 boundaries + 2 unbounded + present termination → "Good" tier
- Raw score: 7/10

**Step 3:** Check tie-breaking
- Boundaries 3/4 = tier requirement (no boost)
- Unbounded 2 < tier max of 3 → supports HIGHER
- Termination present but not measurable → stays at tier
- No adjustment

**Step 4:** Calculate points
- Raw score: 7/10
- Points: 7 × 1.5 = 10.5/15

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

## Non-Issues (Do NOT Count)

**Purpose:** Eliminate false positives by explicitly defining what is NOT a scope issue.

### Pattern 1: Action Bounded by Measurable Target

**Example:**
```markdown
Line 45: "Optimize query performance to <500ms p95"
```
**Why NOT an issue:** "Optimize" has explicit measurable target  
**Overlap check:** Not Executability - execution is clear  
**Correct action:** Do not flag as unbounded

### Pattern 2: Implicit Out-of-Scope from Narrow Focus

**Example:**
```markdown
"Scope: Update only src/auth/ module"
```
**Why NOT an issue:** Narrow scope implicitly excludes other modules  
**Overlap check:** N/A - exclusion is implicit but clear  
**Correct action:** Do not require explicit out-of-scope for highly focused plans

### Pattern 3: Termination Condition in Different Section

**Example:**
```markdown
## Phase 3: Implementation
...
## Validation (later in plan)
Done when: All tests pass, coverage >90%
```
**Why NOT an issue:** Termination exists, just not inline with scope section  
**Overlap check:** N/A - structure choice  
**Correct action:** Search entire plan for termination conditions

### Pattern 4: Out-of-Scope Documented as "Future Work"

**Example:**
```markdown
Future Work (Ticket #457):
- Social login integration
- Admin dashboard improvements
```
**Why NOT an issue:** "Future Work" section is equivalent to out-of-scope  
**Overlap check:** N/A - same function, different label  
**Correct action:** Count "Future Work" items as out-of-scope

## Complete Pattern Inventory

**Purpose:** Eliminate interpretation variance by providing exhaustive lists. If it's not in this list, don't invent it. Match case-insensitive.

### Category 1: Unbounded Phrases (30 Phrases)

**Action Verbs Without Targets:**
1. "improve"
2. "optimize"
3. "refactor"
4. "enhance"
5. "clean up"
6. "fix up"
7. "tidy"
8. "streamline"
9. "modernize"
10. "upgrade"
11. "update"
12. "revise"
13. "rework"
14. "restructure"
15. "reorganize"

**Open-Ended Qualifiers:**
16. "as needed"
17. "as required"
18. "as appropriate"
19. "as necessary"
20. "ongoing"
21. "continuous"
22. "iterative"
23. "incremental"
24. "and more"
25. "etc."
26. "et cetera"
27. "and so on"
28. "and similar"
29. "continue until"
30. "keep doing"

**Regex Patterns:**
```regex
\b(improve|optimize|refactor|enhance|clean\s+up|streamline|modernize)\b(?!\s+(to|until|by)\s+\d)
\b(as|when|if)\s+(needed|required|appropriate|necessary)\b
\b(ongoing|continuous|iterative|incremental)\b
\b(and\s+more|etc\.?|et\s+cetera|and\s+so\s+on)\b
\bcontinue\s+until\b
```

**Context Rules:**
- Unbounded phrase found → Check ±5 lines for quantification
- If quantified ("improve to <500ms") → NOT unbounded
- If not quantified → Count as unbounded

### Category 2: Boundary Definition Patterns (4 Types)

**Type 1 - What to Change:**
- "scope:", "in scope:", "included:"
- "files:", "components:", "modules:"
- "targets:", "affected:"
- File paths (e.g., "src/auth/", "tests/")
- Component names (e.g., "LoginModule", "UserService")

**Type 2 - How Much to Change:**
- "level of change:", "depth:"
- "migrate X to Y"
- "replace A with B"
- "add N features"
- Quantified change ("update 5 endpoints")

**Type 3 - When to Stop (Termination):**
- "done when:", "complete when:"
- "success criteria:", "acceptance criteria:"
- "finished when:", "exit criteria:"
- "termination:", "completion:"
- Measurable outcomes ("all tests pass")

**Type 4 - What NOT to Change:**
- "out of scope:", "not in scope:"
- "excluded:", "not included:"
- "future work:", "deferred:"
- "phase 2:", "later:"
- "will not:", "does not include:"

**Regex Patterns:**
```regex
\b(in|out\s+of)\s*scope\b
\b(included|excluded|affected)\s*:\b
\b(done|complete|finished|success|exit|termination)\s*(when|criteria)\b
\b(future\s+work|deferred|phase\s+\d+)\b
\bwill\s+not\b
```

### Category 3: In-Scope Item Patterns (20 Types)

**Specific Items (COUNT as in-scope):**
1. File paths ("src/auth/login.py")
2. Directory paths ("tests/unit/")
3. Component names ("LoginController")
4. Function names ("authenticate()")
5. Class names ("UserService")
6. API endpoints ("/api/v1/users")
7. Database tables ("users", "orders")
8. Configuration files (".env", "config.yaml")
9. Documentation paths ("docs/api/")
10. Test files ("test_auth.py")
11. Specific features ("OAuth integration")
12. Numbered tasks ("Task 1.1: Implement X")
13. Named deliverables ("authentication module")
14. Version numbers ("migrate to v2.0")
15. Ticket references ("#123", "JIRA-456")
16. Named environments ("staging", "production")
17. Specific users/roles ("admin users")
18. Data ranges ("orders from 2023")
19. Numeric targets ("10,000 users")
20. Time bounds ("Q1 2024")

**Vague Items (do NOT count):**
- "relevant files"
- "necessary changes"
- "appropriate updates"
- "various components"
- "multiple systems"

**Regex Patterns:**
```regex
\b(src|tests?|docs?|config|lib)/[\w/]+\.(py|js|ts|md|yaml|json)\b
\b(Task|Step)\s+\d+\.\d+\b
\b#\d+\b|\b[A-Z]+-\d+\b  # ticket references
\b(staging|production|development)\s+(environment|server)\b
```

### Category 4: Out-of-Scope Indicators (15 Patterns)

**Explicit Exclusion Language:**
1. "out of scope"
2. "not in scope"
3. "excluded"
4. "not included"
5. "will not"
6. "does not include"
7. "future work"
8. "deferred"
9. "phase 2" (or later)
10. "separate ticket"
11. "not this release"
12. "post-MVP"
13. "backlog"
14. "later iteration"
15. "out of band"

**Regex Patterns:**
```regex
\b(out\s+of|not\s+in)\s+scope\b
\b(excluded|not\s+included)\b
\bwill\s+not\b
\b(future\s+work|deferred|backlog)\b
\bphase\s+[2-9]\b
\bseparate\s+(ticket|issue|pr)\b
```

### Category 5: Termination Quality Indicators

**Measurable Termination (GOOD):**
- "exit code 0"
- "all tests pass"
- "100% coverage"
- "0 errors"
- "HTTP 200"
- Numeric thresholds
- File existence checks

**Vague Termination (BAD):**
- "when complete"
- "when done"
- "when ready"
- "when finished"
- "when working"
- "when satisfied"
- "when appropriate"

**Regex Patterns:**
```regex
# Good termination
\b(exit\s+code|tests?\s+pass|coverage|errors?)\s*[=<>≤≥]\s*\d+\b
\bHTTP\s+\d{3}\b

# Bad termination
\bwhen\s+(complete|done|ready|finished|working|satisfied|appropriate)\b
```

### Ambiguous Cases Resolution

**Case 1: "Optimize" with nearby target**

**Pattern:** "Optimize database queries" (line 45), "<500ms p95" (line 47)

**Ambiguity:** How close must target be?

**Resolution Rule:**
- Check ±5 lines for quantification
- Same section (up to 20 lines) acceptable
- If quantified → NOT unbounded
- If not quantified → Count as unbounded

**Case 2: Narrow scope implying exclusions**

**Pattern:** "Update only src/auth/login.py"

**Ambiguity:** Is explicit out-of-scope section needed?

**Resolution Rule:**
- Extremely narrow scope (single file) → implicit exclusion acceptable
- Broader scope (module, system) → explicit exclusions recommended
- Don't penalize narrow-focus plans for missing out-of-scope

**Case 3: "Future Work" vs "Out-of-Scope"**

**Pattern:** "Future Work: Social login, Admin dashboard"

**Ambiguity:** Does Future Work count as exclusions?

**Resolution Rule:**
- "Future Work" = functional equivalent of "Out-of-Scope"
- Count Future Work items as out-of-scope items
- Same scoring treatment

**Case 4: Termination in validation section**

**Pattern:** Scope section has no termination, but Validation section does

**Ambiguity:** Is separated termination acceptable?

**Resolution Rule:**
- Search entire plan for termination conditions
- Termination in any section = termination present
- Quality assessed wherever found

**Case 5: Partially quantified phrase**

**Pattern:** "Improve performance significantly"

**Ambiguity:** Is "significantly" a quantifier?

**Resolution Rule:**
- Relative terms (significantly, substantially) ≠ quantified
- Need numeric target ("improve by 50%", "reduce to <500ms")
- Count as unbounded if no numeric target

**Case 6: Multiple scope sections**

**Pattern:** Each phase has its own in-scope list

**Ambiguity:** Sum or use highest count?

**Resolution Rule:**
- Count UNIQUE in-scope items across entire plan
- Duplicates don't increase count
- Global + phase-level items combined

**Case 7: Implied termination from task structure**

**Pattern:** "Task 1.1, Task 1.2... Task 3.3" with no explicit "done when"

**Ambiguity:** Does completing all tasks = termination?

**Resolution Rule:**
- Task list without explicit termination = vague termination
- Prefer explicit "Done when all tasks complete"
- Partial credit for implied termination

**Case 8: Scope boundary from task type**

**Pattern:** "Migration plan" (implies migrate-only, no new features)

**Ambiguity:** Is task type a boundary?

**Resolution Rule:**
- Task type provides weak implicit boundary
- Still need explicit boundaries for full credit
- Document: "Implicit boundary from task type"

## Anti-Pattern Examples (Common Mistakes)

**❌ WRONG (False Positive):**
- Flagged: "Optimize database queries"
- Rationale given: "Unbounded - optimize to what level?"
- Problem: Plan specifies "to <500ms p95" on next line
- Impact: +1 unbounded phrase incorrectly counted

**✅ CORRECT:**
- Not flagged as unbounded
- Rationale: Measurable target "<500ms p95" follows
- Condition: Would be flagged IF no target specified

**❌ WRONG (False Positive):**
- Flagged: "No out-of-scope section"
- Rationale given: "Missing explicit exclusions"
- Problem: Plan has narrow focus on single file/module
- Impact: Incorrectly penalized for implicit exclusion

**✅ CORRECT:**
- Not flagged if scope is narrowly defined
- Rationale: Narrow scope implies exclusion of everything else
- Condition: Would be flagged IF scope is broad without exclusions

## Ambiguous Case Resolution Rules (REQUIRED)

**Purpose:** Provide deterministic scoring when scope boundaries are borderline.

### Rule 1: Same-File Context
**Count boundary as present if:** Explicit boundary statement exists anywhere in plan  
**Count boundary as missing if:** No explicit boundary for that type (what/how much/when/what NOT)

### Rule 2: Adjectives Without Quantifiers
**Count as unbounded if:** Phrase has no measurable target ("improve", "optimize", "enhance")  
**Count as bounded if:** Phrase has measurable target ("improve to <500ms", "reduce by 50%")

### Rule 3: Pattern Variations
**Count as in-scope item if:** Specific named deliverable, file, or component  
**Count as NOT in-scope item if:** Vague reference ("relevant files", "necessary changes")

### Rule 4: Default Resolution
**Still uncertain after Rules 1-3?** → Count as unbounded/missing (conservative scoring)

### Borderline Cases Template

Document borderline decisions in your worksheet:

```markdown
### Line [X]: "[Quote]"
- **Decision:** Boundary [Present/Missing] OR Phrase [Bounded/Unbounded]
- **Rule Applied:** [1/2/3/4]
- **Reasoning:** [Explain why this classification]
- **Alternative:** [Other interpretation and why rejected]
- **Confidence:** [HIGH/MEDIUM/LOW]
```

## Mandatory Counting Worksheet (REQUIRED)

**CRITICAL:** You MUST create and fill this worksheet BEFORE calculating score.

### Why This Is Required
- **Eliminates counting variance:** Same plan → same worksheet → same score
- **Prevents false negatives:** Systematic boundary check catches all gaps
- **Provides evidence:** Worksheet shows exactly what was counted
- **Enables verification:** Users can audit scoring decisions

### Worksheet Template

| Boundary Type | Present? | Description | Lines | Score |
|---------------|----------|-------------|-------|-------|
| What to change | Y/N | | | 0/1 |
| How much | Y/N | | | 0/1 |
| When to stop | Y/N | | | 0/1 |
| What NOT | Y/N | | | 0/1 |
| **BOUNDARIES** | | | | **___/4** |

| Scope Items | Count | Lines |
|-------------|-------|-------|
| In-scope items | ___ | |
| Out-of-scope items | ___ | |

| Unbounded Phrases | Line | Quote | Fix Suggestion |
|-------------------|------|-------|----------------|
| 1. | ___ | "..." | |
| 2. | ___ | "..." | |
| **TOTAL UNBOUNDED** | | | **___** |

| Termination | Quality | Description |
|-------------|---------|-------------|
| Conditions present? | Y/N | |
| Measurable? | Y/N | |
| Verifiable by agent? | Y/N | |

### Counting Protocol (6 Steps)

**Step 1: Create Empty Worksheet**
- Copy template above into working document
- Do NOT start reading plan yet

**Step 2: Check Boundaries (4 types)**
- Scan plan for each boundary type
- Record Y/N and description for each
- Note line numbers where boundaries defined

**Step 3: Count Scope Items**
- Count explicit in-scope items (named files, components, deliverables)
- Count explicit out-of-scope items (exclusions, future work)

**Step 4: Scan for Unbounded Phrases**
- Read plan line 1 to END
- Flag: improve, optimize, refactor, as needed, ongoing, continue until, clean up, enhance
- Record each with line number and suggested fix

**Step 5: Assess Termination Conditions**
- Check if "done when" conditions exist
- Check if conditions are measurable
- Check if agent can verify completion

**Step 6: Include in Review Output**
- Copy completed worksheet into review document
- Calculate score using Score Decision Matrix

## Inter-Run Consistency Target

**Expected variance:** ±1 boundary count

**Verification:**
- Use 4-boundary checklist
- Count unbounded phrases with line numbers
- Count in-scope/out-of-scope items explicitly

**If variance exceeds threshold:**
- Re-verify using boundary table
- Apply phrase definitions strictly
