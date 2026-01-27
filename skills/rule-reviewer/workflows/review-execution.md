# Workflow: Review Execution

## Inputs

- `target_file`: Path to rule file to review
- `review_date`: Date of review (YYYY-MM-DD)
- `review_mode`: FULL, FOCUSED, or STALENESS
- `model_slug`: Model identifier for metadata

## Phase 1: Load All Rubric Definitions (MANDATORY)

**Purpose:** Lock in scoring criteria interpretation BEFORE reading target rule.

**Duration:** 5-10 minutes (one-time upfront cost)

### Step 1.1: Read Rubric Files in Order

**Read these 8 files completely before reading target rule:**

1. `rubrics/_overlap-resolution.md` (prerequisite for all dimensions)
2. `rubrics/actionability.md` (25 points, weight 5)
3. `rubrics/completeness.md` (25 points, weight 5)
4. `rubrics/consistency.md` (15 points, weight 3)
5. `rubrics/parsability.md` (15 points, weight 3)
6. `rubrics/token-efficiency.md` (10 points, weight 2)
7. `rubrics/staleness.md` (10 points, weight 2)
8. `rubrics/cross-agent-consistency.md` (5 points, weight 1)

### Step 1.2: Extract Key Information

From EACH rubric, record:
- **Pattern definitions:** What to look for
- **Non-Issues list:** What NOT to count
- **Counting protocol:** How to enumerate
- **Score decision matrix:** Count → tier → score

### Step 1.3: Create All 7 Empty Inventories

**Prepare inventories BEFORE reading target rule.**

Copy the Mandatory Issue Inventory template from each rubric:

1. Actionability Inventory (blocking issues table)
2. Completeness Inventory (error/edge case/prerequisite/validation checklist)
3. Consistency Inventory (contradictions, terminology, examples tables)
4. Parsability Inventory (schema errors, metadata, markdown tables)
5. Token Efficiency Inventory (budget, redundancy, structure tables)
6. Staleness Inventory (LastUpdated, tools, patterns, links tables)
7. Cross-Agent Consistency Inventory (considerations, conditionals tables)

### Step 1.4: Verification Checkpoint

Before proceeding, verify:

- [ ] All 8 rubric files read completely?
- [ ] Pattern definitions extracted?
- [ ] Non-Issues lists recorded?
- [ ] All 7 inventories created (empty)?

**GATE:** Do NOT proceed to Phase 2 until ALL checkboxes are YES.

---

## Phase 2: Read Target Rule and Fill Inventories

### Step 2.1: Read Target Rule Completely

- Read `target_file` from line 1 to END
- Note structure (sections, metadata, content)
- Do NOT score yet

### Step 2.2: Fill Inventories Systematically

For EACH dimension:

1. Apply its counting protocol
2. Record all matches with line numbers
3. Use the inventory template from that rubric

**Order:** Process dimensions in this sequence:
1. Parsability (schema validation first)
2. Actionability (blocking issues)
3. Completeness (coverage gaps)
4. Consistency (internal alignment)
5. Token Efficiency (budget/redundancy)
6. Staleness (currency checks)
7. Cross-Agent Consistency (universal compatibility)

### Step 2.3: Apply Non-Issues Filters

For EACH filled inventory:

1. Check each flagged item against Non-Issues list
2. Remove false positives with note
3. Recalculate totals

### Step 2.4: Resolve Overlaps

Using `rubrics/_overlap-resolution.md`:

1. Identify issues that could belong to multiple dimensions
2. Apply decision rules in order (Rule 1 highest priority)
3. Assign each issue to PRIMARY dimension only
4. Document rule applied in inventory

---

## Phase 3: Calculate Scores and Generate Review

### Step 3.1: Calculate Dimension Scores

For EACH dimension:

1. Use Score Decision Matrix from rubric
2. Look up tier based on issue count
3. Apply tie-breaking rules if on boundary
4. Record score with evidence

### Step 3.2: Calculate Total Score

```
Total = (Actionability × 2.5) + (Completeness × 2.5) + 
        (Consistency × 1.5) + (Parsability × 1.5) + 
        (Token Efficiency × 1.0) + (Staleness × 1.0) + 
        (Cross-Agent Consistency × 0.5)

Maximum: 100 points
```

### Step 3.3: Generate Review

Include in output:

1. **Header:** Target file, review date, mode, model
2. **Score Summary:** Total and per-dimension scores
3. **All Inventories:** Include completed inventory tables as evidence
4. **Priority Fixes:** Top 3-5 improvements ordered by impact
5. **Verdict:** PASS (≥80), NEEDS_WORK (60-79), FAIL (<60)

---

## Output

- `review_markdown`: Full Markdown review content with:
  - Score summary
  - All 7 dimension inventories
  - Issue details with line numbers
  - Priority fix recommendations
  - Verdict

---

## Quality Assurance

### Self-Verification Checklist

Before submitting review, verify:

- [ ] All 8 rubric files read (before target)?
- [ ] All 7 inventories created and filled?
- [ ] Target read line 1 to END?
- [ ] Only inventory patterns used?
- [ ] Non-Issues list applied?
- [ ] Overlap resolution applied?
- [ ] Inventories included in output?
- [ ] Scores from decision matrices?

**If ANY checkbox NO:** Review is INVALID, regenerate from Phase 1.

### Pre-Write Output Verification (MANDATORY)

**Before writing review file, verify these structural requirements:**

| Requirement | Check |
|-------------|-------|
| Score table present | 7 rows (all dimensions) with scores |
| Line references | ≥15 distinct line citations |
| Direct quotes | ≥3 with line numbers |
| Verdict section | One of: EXECUTABLE, EXECUTABLE_WITH_REFINEMENTS, NEEDS_REFINEMENT, NOT_EXECUTABLE |
| Recommendations | ≥1 with line numbers (even for 95+ scores) |

**If ANY requirement missing:**
1. STOP - Do not write incomplete review
2. Re-read relevant rubric(s)
3. Add missing content
4. Re-verify before write

**Post-Write Size Check:**
```python
review_size = os.path.getsize(review_path)
if review_size < 2500:
    print(f"WARNING: Review only {review_size} bytes - may indicate drift")
    print("Recommended: Re-read SKILL.md before next review")
```

### Expected Variance

- Issue counts: ±1 item
- Dimension scores: ±1 point
- Overall score: ±2 points

If variance exceeds these thresholds between runs, re-verify inventory counting.
