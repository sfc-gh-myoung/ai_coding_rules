# Consistency Rubric (15 points)

## Scoring Criteria

### 5/5 (15 points): Excellent
- Perfect internal consistency (no contradictions)
- Terminology used uniformly throughout
- All examples comply with stated mandates
- Dependencies correctly referenced
- Cross-references accurate and current

### 4/5 (12 points): Good
- 1-2 minor inconsistencies (terminology variations)
- Most examples align with mandates
- Dependencies mostly correct
- Cross-references accurate

### 3/5 (9 points): Acceptable
- 3-4 inconsistencies (conflicting guidance)
- Some examples don't follow mandates
- 1-2 dependency errors
- Some stale cross-references

### 2/5 (6 points): Needs Work
- 5-7 major inconsistencies
- Many examples contradict mandates
- Multiple dependency errors
- Many stale or incorrect references

### 1/5 (3 points): Poor
- >7 contradictions throughout rule
- Examples don't align with mandates
- Dependencies incorrect or circular
- Cross-references broken

## Internal Consistency Check

### 1. Terminology Consistency

Track key terms used throughout rule:

**Example analysis:**
```
Line 45: "surgical edits"
Line 120: "minimal changes" ← INCONSISTENT (same concept, different term)
Line 200: "surgical edits" ← CONSISTENT
```

**Common inconsistencies:**
- "task" vs "to-do" vs "action item"
- "rule" vs "guideline" vs "directive"
- "must" vs "required" vs "mandatory"
- "forbidden" vs "prohibited" vs "not allowed"

### 2. Mandate vs Example Alignment

Check that all examples follow the rule's own requirements:

**Example (checking compliance):**

If rule says: "Always use explicit column selection (no SELECT *)"

Then examples must not contain:
```sql
❌ BAD: SELECT * FROM table  -- Violates own mandate
✅ GOOD: SELECT col1, col2 FROM table
```

### 3. Value Consistency

Track specific values/thresholds mentioned:

**Example (inconsistent thresholds):**
```
Line 36: "Large table: >10M rows"
Line 86: "Large table: >5M rows"  ← INCONSISTENT (different threshold)
Line 150: "Large table: >10M rows" ← Which one is correct?
```

## Dependency Alignment Check

### 1. Verify Depends Field

All dependencies listed in `Depends:` metadata must:
- Actually exist as files
- Be referenced in rule body
- Contain content actually used by this rule

### 2. Verify Related Rules

Check references in "Related" section:
- Files exist at specified paths
- Descriptions match actual rule content
- No circular dependencies (A depends on B, B depends on A)

### 3. Verify External Links

All external documentation links should:
- Be current and accessible
- Point to stable URLs (not version-specific unless necessary)
- Match descriptions provided

## Cross-Reference Verification

### 1. Internal References

Check all `See:` references point to:
- Sections that exist in same file
- Correct line numbers (if specified)
- Content that matches description

**Example:**
```markdown
"See: Validation section for details"
→ Verify "Validation" section exists
→ Verify it contains relevant details
```

### 2. External References

Verify references to other rules:
```markdown
"See: 100-snowflake-core.md for SQL patterns"
→ Check: Does 100-snowflake-core.md exist?
→ Check: Does it contain SQL patterns?
→ Check: Are they the patterns this rule needs?
```

## Scoring Formula

```
Base score = 5/5 (15 points)

Internal contradictions: -0.5 points each (up to -5)
Terminology inconsistencies: -0.3 points each (up to -3)
Example-mandate misalignment: -1 point each (up to -4)
Dependency errors: -0.5 points each (up to -2)
Broken cross-references: -0.3 points each (up to -2)

Minimum score: 1/5 (3 points)
```

## Common Consistency Issues

### Issue 1: First Mention vs Later Use

**Pattern:**
```
Line 50: "mutable large tables (>10M rows OR >5GB...)" [full definition]
Line 100: "mutable large tables" [no definition, assumes memory]
Line 150: "mutable large tables (>5GB)" [partial definition - INCONSISTENT]
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
→ CONFLICT: Is SELECT * ever allowed?
```

**Fix:** Add explicit scoping:
```
Section A: "Never use SELECT * in production code"
Section B: "In development only: Use SELECT * for exploration, then replace with explicit columns before commit"
```

### Issue 3: Stale Dependencies

**Pattern:**
```
Depends: 202-python-virtual-environments.md
→ File was merged into 200-python-core.md
→ Dependency now incorrect
```

**Fix:** Update dependencies to reflect actual structure.

## Verification Table Template

When reviewing, create consistency verification table:

| Element | First Use | Other Uses | Status |
|---------|-----------|------------|--------|
| "Large table" threshold | Line 36: ">10M rows" | Lines 86, 150: ">10M rows" | ✅ Consistent |
| Tool command | Line 54: `uvx ruff` | Line 120: `uv run ruff` | ❌ Inconsistent |
| Mandate example | Line 90: No SELECT * | Line 200: SELECT * shown | ❌ Violates mandate |
