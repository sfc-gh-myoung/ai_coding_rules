# Consistency Rubric (10 points)

> **Weight:** 2 | **Max:** 10 points | **Formula:** Raw × 1.0

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

### Why This Is Required

- **Eliminates counting variance:** Same rule → same inventory → same score
- **Prevents false negatives:** Systematic tracking catches all inconsistencies
- **Provides evidence:** Inventory shows exactly what was found
- **Enables verification:** Users can audit scoring decisions

### Inventory Template

**Contradictions:**

| Line A | Line B | Statement A | Statement B | Type |
|--------|--------|-------------|-------------|------|
| 45 | 200 | "Always use X" | "Never use X" | Direct |
| 36 | 150 | "Large = >10M" | "Large = >5M" | Threshold |

**Terminology Variations:**

| Term 1 | Lines | Term 2 | Lines | Same Concept? |
|--------|-------|--------|-------|---------------|
| surgical edits | 45, 120 | minimal changes | 200 | Y/N |
| task | 30, 60 | action item | 150 | Y/N |

**Example Compliance:**

| Line | Example Type | Mandate | Compliant? |
|------|--------------|---------|------------|
| 67 | SQL query | No SELECT * | Y/N |
| 134 | Python | Use ruff | Y/N |

**Dependency Status:**

| Dependency | Exists? | Referenced? | Valid? |
|------------|---------|-------------|--------|
| 000-global-core.md | Y/N | Y/N | Y/N |

### Counting Protocol (5 Steps)

**Step 1: Create Empty Inventory**
- Copy all four templates above into working document
- Do NOT start reading rule yet

**Step 2: Read Rule Systematically**
- Start at line 1, read to END (no skipping)
- Track each key term with all line numbers
- Note each code example with line number
- Record each threshold/value definition

**Step 3: Calculate Raw Totals**
- Contradictions: Count direct conflicts
- Terminology: Count variations without defined equivalence
- Examples: Calculate compliance percentage
- Dependencies: Count issues

**Step 4: Check Non-Issues List**
- Review EACH flagged item in inventory
- Check against "Non-Issues" section below
- Remove false positives with note
- Recalculate totals

**Step 5: Look Up Score**
- Use adjusted totals in Score Decision Matrix
- Record score with inventory evidence

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 2
**Points:** Raw × 1.0

## Scoring Criteria

### 10/10 (10 points): Perfect
- 0 internal contradictions
- 0 terminology inconsistencies
- 100% example-mandate alignment
- All dependencies valid and referenced
- All cross-references accurate

### 9/10 (9 points): Near-Perfect
- 0 internal contradictions
- 1 terminology variation
- 99%+ example-mandate alignment
- All dependencies valid

### 8/10 (8 points): Excellent
- 0 internal contradictions
- 2 terminology variations
- 97-98% example-mandate alignment
- 1 minor dependency issue

### 7/10 (7 points): Good
- 0 internal contradictions
- 3 terminology variations
- 95-96% example-mandate alignment
- 1-2 minor dependency issues

### 6/10 (6 points): Acceptable
- 1 internal contradiction
- 4 terminology variations
- 90-94% example-mandate alignment
- 2 dependency issues

### 5/10 (5 points): Borderline
- 1 internal contradiction
- 5 terminology variations
- 85-89% example-mandate alignment
- 2-3 dependency issues

### 4/10 (4 points): Needs Work
- 2 internal contradictions
- 6 terminology variations
- 80-84% example-mandate alignment
- 3 dependency issues

### 3/10 (3 points): Poor
- 2-3 internal contradictions
- 7 terminology variations
- 70-79% example-mandate alignment
- 4 dependency issues

### 2/10 (2 points): Very Poor
- 3-4 internal contradictions
- 8-9 terminology variations
- 60-69% example-mandate alignment
- 5+ dependency issues

### 1/10 (1 point): Inadequate
- 4-5 internal contradictions
- 10+ terminology variations
- 50-59% example-mandate alignment
- Dependencies broken or circular

### 0/10 (0 points): Not Consistent
- 6+ internal contradictions
- Pervasive terminology issues
- <50% example-mandate alignment
- Cannot reliably execute

## Counting Definitions

### Internal Contradictions

**Definition:** Two statements in the rule that cannot both be true.

**Count as 1 contradiction:**
- Direct conflict: "Always do X" vs "Never do X"
- Threshold conflict: "Large = >10M rows" vs "Large = >5M rows"
- Scope conflict: "Applies to all tables" vs "Skip temporary tables"

**NOT contradictions (do not count):**
- Scoped exceptions: "Always do X, except when Y"
- Contextual variations: "In production do X, in development do Y"

### Terminology Variations

**Definition:** Same concept referred to by different terms without explicit equivalence.

**Count as 1 variation:**
- "surgical edits" vs "minimal changes" (same concept, different terms)
- "task" vs "to-do" vs "action item" (same concept)
- "must" vs "required" vs "mandatory" (same severity)

**NOT variations (do not count):**
- Defined synonyms: "surgical edits (also called minimal changes)"
- Intentional distinctions: "error" (recoverable) vs "failure" (fatal)

### Example-Mandate Alignment

**Calculation:**
```
Alignment % = (compliant examples / total examples) × 100
```

**Count as misalignment:**
- Example uses `SELECT *` when mandate says "no SELECT *"
- Example omits error handling when mandate requires it
- Example uses deprecated tool when mandate specifies current tool

**Tracking checklist (for each example):**
- Example at line 45: Mandate "No SELECT *" - Compliant?
- Example at line 78: Mandate "Use ruff" - Compliant?
- Example at line 120: Mandate "Error handling required" - Compliant?

### Dependency Issues

**Count as 1 issue:**
- Listed dependency file doesn't exist
- Dependency exists but isn't referenced in rule body
- Circular dependency (A depends on B, B depends on A)
- External link returns 404 or redirect
- Description doesn't match actual content

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (10 pts):** 0 contradictions, 0 term variations, 100% example alignment, 0 dependency issues
- **9/10 (9 pts):** 0 contradictions, 1 term variation, 99%+ example alignment, 0 dependency issues
- **8/10 (8 pts):** 0 contradictions, 2 term variations, 97-98% example alignment, 1 dependency issue
- **7/10 (7 pts):** 0 contradictions, 3 term variations, 95-96% example alignment, 1-2 dependency issues
- **6/10 (6 pts):** 1 contradiction, 4 term variations, 90-94% example alignment, 2 dependency issues
- **5/10 (5 pts):** 1 contradiction, 5 term variations, 85-89% example alignment, 2-3 dependency issues
- **4/10 (4 pts):** 2 contradictions, 6 term variations, 80-84% example alignment, 3 dependency issues
- **3/10 (3 pts):** 2-3 contradictions, 7 term variations, 70-79% example alignment, 4 dependency issues
- **2/10 (2 pts):** 3-4 contradictions, 8-9 term variations, 60-69% example alignment, 5+ dependency issues
- **1/10 (1 pt):** 4-5 contradictions, 10+ term variations, 50-59% example alignment, broken dependencies
- **0/10 (0 pts):** 6+ contradictions, pervasive issues, <50% alignment

**Tie-breaker:** If scores span tiers, use the contradiction count as primary determinant.

## Internal Consistency Check

### 1. Terminology Tracking

Create tracking list during review:

**Terminology Inventory:**
- "surgical edits" (line 45, also 120, 200): OK - Consistent
- "minimal changes" (line 180): ISSUE - Same as "surgical edits"?
- "task" (line 30, also 60, 90): OK - Consistent
- "action item" (line 150): ISSUE - Same as "task"?

**Count:** 2 terminology variations

### 2. Mandate vs Example Verification

For each example code block:
1. Identify relevant mandates
2. Check compliance
3. Record findings

**Example Compliance Inventory:**
- SQL query (line 67): Mandates "No SELECT *, explicit columns" - Yes, compliant
- Python snippet (line 134): Mandates "Use ruff, error handling" - No (uses black)
- Config example (line 200): Mandate "Version specified" - Yes, compliant

### 3. Value Consistency

Track specific values/thresholds:

**Value Consistency Inventory:**
- Large table: First defined line 36 as ">10M rows", also line 86 ">10M rows" - Consistent
- Timeout: First defined line 50 as "30s", but line 150 says "60s" - NOT consistent

## Dependency Alignment Check

### 1. Verify Depends Field

For each dependency in `Depends:` metadata:

**Dependency Verification Checklist:**
- 000-global-core.md: File exists? Referenced in body? Content used?
- 100-snowflake-core.md: File exists? Referenced in body? Content used?

### 2. Verify External Links

**External Link Inventory:**
- https://docs.snowflake.com/...: Status 200 - Valid
- https://example.com/old-docs: Status 404 - Broken

## Worked Example

**Target:** Rule with consistency issues

### Step 1: Scan for Contradictions

```markdown
Line 45: "Always use explicit column selection (no SELECT *)"
Line 200: Example shows "SELECT * FROM staging_table"
= CONTRADICTION between mandate and example
```

**Count:** 1 contradiction (example violates mandate)

### Step 2: Track Terminology

**Terminology Inventory:**
- "surgical edits" (lines 45, 120): OK
- "minimal changes" (line 200): ISSUE - Variation of "surgical edits"
- "mutable table" (lines 30, 60): OK
- "updatable table" (line 90): ISSUE - Variation of "mutable table"

**Count:** 2 terminology variations

### Step 3: Check Example Alignment

**Example Compliance:**
- Line 67 SQL query: Mandate "No SELECT *" - Yes, compliant
- Line 134 Python: Mandate "Use ruff" - Yes, compliant
- Line 200 SQL: Mandate "No SELECT *" - No, uses SELECT *

**Alignment:** 2/3 = 67%

### Step 4: Verify Dependencies

**Dependency Status:**
- 000-global-core.md: Exists, referenced, valid
- 202-python-old.md: Does not exist - File missing

**Issues:** 1 (missing dependency file)

### Step 5: Calculate Score

**Component Assessment:**
- Contradictions: 1 = 3/5 baseline
- Term variations: 2 = Within 4/5 range
- Example alignment: 67% = Confirms 2/5
- Dependency issues: 1 = Minor

**Final:** 4/10 (4 points) - example alignment is the determining factor

### Step 6: Document in Review

```markdown
## Consistency: 4/10 (4 points)

**Internal contradictions:** 1
- Line 45 mandate "no SELECT *" violated by Line 200 example

**Terminology variations:** 2
- "surgical edits" (45, 120) vs "minimal changes" (200)
- "mutable table" (30, 60) vs "updatable table" (90)

**Example alignment:** 67% (2/3 compliant)
- Line 200: Uses SELECT * despite mandate

**Dependency issues:** 1
- 202-python-old.md listed but file doesn't exist

**Priority fixes:**
1. Fix Line 200 example to use explicit columns
2. Standardize "surgical edits" terminology
3. Update dependency to current file path
```

## Common Consistency Issues

### Issue 1: First Mention vs Later Use

**Pattern:**
```
Line 50: "mutable large tables (>10M rows OR >5GB...)" [full definition]
Line 100: "mutable large tables" [no definition, assumes memory]
Line 150: "mutable large tables (>5GB)" [partial - INCONSISTENT]
```

**Fix:** Define once with anchor, reference later:
```
Line 50: **Large table:** >10M rows OR >5GB (see Quantification Standards)
Line 100: Use Streams for large tables (see "Large table" definition)
```

### Issue 2: Conflicting Guidance

**Pattern:**
```
Section A: "Never use SELECT * in production"
Section B: "Use SELECT * for initial exploration"
CONFLICT: Is SELECT * ever allowed?
```

**Fix:** Add explicit scoping:
```
Section A: "Never use SELECT * in production code"
Section B: "In development only: SELECT * for exploration, replace before commit"
```

## Inter-Run Consistency Target

**Expected variance:** ±1 issue count per category

**Verification checklist:**
- [ ] Scanned all code examples against mandates
- [ ] Tracked all key terms with line numbers
- [ ] Verified all dependency files exist
- [ ] Checked all external links

**If variance exceeds threshold:**
- Use tracking tables (provided above)
- Document each issue with line numbers
- Note ambiguous cases

## Non-Issues (Do NOT Count)

**Review EACH flagged item against this list before counting.**

### Pattern 1: Defined Synonyms
**Pattern:** Two terms used, but explicitly defined as equivalent
**Example:** "surgical edits (also called minimal changes)" - then uses both terms
**Why NOT an issue:** Equivalence is explicitly stated
**Action:** Remove from inventory with note "Explicitly defined as synonyms"

### Pattern 2: Intentional Distinctions
**Pattern:** Different terms for intentionally different concepts
**Example:** "error" (recoverable) vs "failure" (fatal) used consistently
**Why NOT an issue:** Terms have different meanings in context
**Action:** Remove from inventory with note "Intentional distinction"

### Pattern 3: Severity Levels
**Pattern:** "must", "should", "may" used at different severity levels
**Example:** "must" for critical, "should" for recommended, "may" for optional
**Why NOT an issue:** RFC 2119 style usage is intentional
**Action:** Remove from inventory with note "Severity levels"

### Pattern 4: Anti-Examples
**Pattern:** Example shows what NOT to do
**Example:** Example marked "BAD:" uses SELECT * to show incorrect usage
**Why NOT an issue:** Example demonstrates the violation intentionally
**Action:** Remove from inventory with note "Anti-example (intentional)"
