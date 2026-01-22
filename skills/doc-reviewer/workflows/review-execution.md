# Workflow: Review Execution

## Inputs

- `resolved_targets`: list of file paths to review
- `review_date`: validated date string
- `review_mode`: FULL | FOCUSED | STALENESS
- `review_scope`: single | collection
- `model_slug`: normalized model identifier
- `focus_area`: (optional) for FOCUSED mode
- `baseline_rules`: list of available documentation rules

## Phase 1: Load All Rubric Definitions (MANDATORY)

**Purpose:** Lock in scoring criteria interpretation BEFORE reading target documentation.

**Duration:** 5-10 minutes (one-time upfront cost)

### Step 1.1: Read Rubric Files in Order

**Read these 7 files completely before reading target documentation:**

1. `rubrics/_overlap-resolution.md` (prerequisite for all dimensions)
2. `rubrics/accuracy.md` (25 points, weight 5)
3. `rubrics/completeness.md` (25 points, weight 5)
4. `rubrics/clarity.md` (20 points, weight 4)
5. `rubrics/structure.md` (15 points, weight 3)
6. `rubrics/staleness.md` (10 points, weight 2)
7. `rubrics/consistency.md` (5 points, weight 1)

### Step 1.2: Extract Key Information

From EACH rubric, record:
- **Verification criteria:** What to check
- **Non-Issues list:** What NOT to flag
- **Counting protocol:** How to enumerate
- **Score decision matrix:** Percentage/count → tier → score

### Step 1.3: Create All 6 Empty Verification Tables

**Prepare tables BEFORE reading target documentation.**

Copy the Mandatory Verification Table template from each rubric:

1. Accuracy Table (file paths, commands, functions, code examples)
2. Completeness Table (features, setup steps, troubleshooting)
3. Clarity Table (jargon audit, concept order, new user test)
4. Structure Table (section order, heading hierarchy, navigation)
5. Staleness Table (link status, tool versions, deprecated patterns)
6. Consistency Table (formatting, terminology, code style)

### Step 1.4: Verification Checkpoint

Before proceeding, verify:

- [ ] All 7 rubric files read completely?
- [ ] Verification criteria extracted?
- [ ] Non-Issues lists recorded?
- [ ] All 6 verification tables created (empty)?

**GATE:** Do NOT proceed to Phase 2 until ALL checkboxes are YES.

---

## Phase 2: Read Target Documentation and Fill Tables

### Step 2.1: Read Target Documentation Completely

For each file in `resolved_targets`:
- Read file contents from line 1 to END
- Note file path and line count
- Extract existing structure (headings, sections)
- Do NOT score yet

### Step 2.2: Read Baseline Rules (if available)

If baseline rules exist, read for comparison:
- `rules/801-project-readme.md` - README standards
- `rules/802-project-contributing.md` - CONTRIBUTING standards

### Step 2.3: Fill Verification Tables Systematically

For EACH dimension:

1. Apply its verification protocol
2. Record all findings with line numbers
3. Use the table template from that rubric

**Order:** Process dimensions in this sequence:
1. Accuracy (reference verification first)
2. Completeness (coverage gaps)
3. Clarity (accessibility check)
4. Structure (organization check)
5. Staleness (link validation)
6. Consistency (formatting check)

### Step 2.4: Apply Non-Issues Filters

For EACH filled table:

1. Check each flagged item against Non-Issues list
2. Remove false positives with note
3. Recalculate totals

### Step 2.5: Resolve Overlaps

Using `rubrics/_overlap-resolution.md`:

1. Identify issues that could belong to multiple dimensions
2. Apply decision rules in order (Rule 1 highest priority)
3. Assign each issue to PRIMARY dimension only
4. Document rule applied in table

---

## Phase 3: Calculate Scores and Generate Review

### Step 3.1: Calculate Dimension Scores

For EACH dimension:

1. Use Score Decision Matrix from rubric
2. Look up tier based on count or percentage
3. Apply tie-breaking rules if on boundary
4. Record score with evidence

### Step 3.2: Calculate Total Score

```
Total = Accuracy + Completeness + Clarity + Structure + Staleness + Consistency

Accuracy: X/10 × 2.5 = XX/25 points
Completeness: X/10 × 2.5 = XX/25 points
Clarity: X/10 × 2.0 = XX/20 points
Structure: X/10 × 1.5 = XX/15 points
Staleness: X/10 × 1.0 = XX/10 points
Consistency: X/10 × 0.5 = XX/5 points

Maximum: 100 points
```

### Step 3.3: Apply Critical Dimension Overrides

Check critical dimensions (Accuracy, Completeness):
- If Accuracy ≤4/10: Cap total at 60 maximum
- If Completeness ≤4/10: Cap total at 60 maximum
- If both ≤4/10: Cap total at 40 maximum

### Step 3.4: Determine Verdict

| Score | Verdict | Meaning |
|-------|---------|---------|
| 90-100 | EXCELLENT | High-quality documentation |
| 80-89 | GOOD | Minor improvements needed |
| 60-79 | NEEDS_IMPROVEMENT | Significant updates required |
| 40-59 | POOR | Major revision needed |
| <40 | INADEQUATE | Rewrite from scratch |

### Step 3.5: Generate Review Output

Include in output:

1. **Header:** Target file(s), review date, mode, model
2. **Score Summary:** Total and per-dimension scores
3. **All Verification Tables:** Include completed tables as evidence
4. **Priority Fixes:** Top 3-5 improvements ordered by impact
5. **Verdict:** Based on total score

---

## Mode-Specific Behavior

### FULL Mode
- Load all 6 rubrics in Phase 1
- Create and fill all 6 verification tables
- Score all 6 dimensions
- Comprehensive recommendations

### FOCUSED Mode
- Load only rubrics for `focus_area` dimensions
- Create and fill only relevant tables
- Score only specified dimensions
- Targeted recommendations

### STALENESS Mode
- Load only `rubrics/staleness.md`
- Create and fill only Staleness table (link validation)
- Score only Staleness dimension
- Quick maintenance check

---

## Output

Returns populated review structure:
- Score summary
- All verification tables (as evidence)
- Issue details with line numbers
- Priority fix recommendations
- Verdict

---

## Quality Assurance

### Self-Verification Checklist

Before submitting review, verify:

- [ ] All required rubric files read (before target)?
- [ ] All required verification tables created and filled?
- [ ] Target read line 1 to END?
- [ ] Only rubric criteria used?
- [ ] Non-Issues list applied?
- [ ] Overlap resolution applied?
- [ ] Verification tables included in output?
- [ ] Scores from decision matrices?

**If ANY checkbox NO:** Review is INVALID, regenerate from Phase 1.

### Expected Variance

- Issue counts: ±1 item
- Dimension scores: ±1 point
- Overall score: ±2 points

If variance exceeds these thresholds between runs, re-verify table counting.

---

## Error Handling

**If target file missing:**
- Error: "File not found: [path]"
- Skip to next file

**If link validation fails:**
- Note in Staleness table
- Continue review

**If baseline rule missing:**
- Warning: "Baseline rule not found"
- Proceed without baseline comparison

**If rubric file missing:**
- Error: "Rubric not found: [path]"
- Cannot score dimension
