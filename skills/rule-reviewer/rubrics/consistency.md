# Consistency Rubric (10 points)

> **Weight:** 2 | **Max:** 10 points | **Formula:** Raw × 1.0

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

> **Why inventories are required:** Eliminates counting variance (same rule → same inventory → same score), prevents false negatives, provides auditable evidence, enables verification.

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

### Counting Protocol

> **Standard 5-Step Counting Protocol:**
> 1. **Create Empty Inventory** — Copy template above into working document. Do NOT start reading rule yet.
> 2. **Read Rule Systematically** — Start at line 1, read to END (no skipping). Record all matches with line numbers.
> 3. **Calculate Raw Totals** — Sum counts by category using dimension-specific definitions.
> 4. **Check Non-Issues List** — Review EACH flagged item against this dimension's Non-Issues section. Remove false positives with note. Recalculate totals.
> 5. **Look Up Score** — Use adjusted totals in Score Decision Matrix. Record score with inventory evidence.
>
> **Inter-run consistency:** Use inventory tables with line numbers for evidence. If variance exceeds threshold documented below, re-count using checklists and document ambiguous cases.
>
> **Dimension-specific:** Track contradictions, terminology variations, example-mandate compliance %, and dependency issues.

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 2
**Points:** Raw × 1.0

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

**Expected variance:** ±1 issue count per category. Verify by scanning all code examples against mandates, tracking all key terms with line numbers, verifying dependency files, and checking external links.

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
