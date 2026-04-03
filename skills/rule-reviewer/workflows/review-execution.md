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

**Read these 9 files completely before reading target rule:**

> **Scoring Rubric v2.0:** 6 scored dimensions (100 points), 2 informational-only

**Scored Dimensions:**
1. `rubrics/_overlap-resolution.md` (prerequisite for all dimensions)
2. `rubrics/actionability.md` (30 points, weight 3.0)
3. `rubrics/rule-size.md` (25 points, weight 2.5) - 100% deterministic
4. `rubrics/parsability.md` (15 points, weight 1.5)
5. `rubrics/completeness.md` (15 points, weight 1.5)
6. `rubrics/consistency.md` (10 points, weight 1.0)
7. `rubrics/cross-agent-consistency.md` (5 points, weight 0.5)

**Informational Only (not scored):**
8. `rubrics/token-efficiency.md` - merged into Rule Size
9. `rubrics/staleness.md` - findings reported, not scored

### Step 1.2: Extract Key Information

From EACH rubric, record:
- **Pattern definitions:** What to look for
- **Non-Issues list:** What NOT to count
- **Counting protocol:** How to enumerate
- **Score decision matrix:** Count → tier → score

### Step 1.3: Create All 6 Empty Inventories

**Prepare inventories BEFORE reading target rule.**

Copy the Mandatory Issue Inventory template from each scored rubric:

1. Actionability Inventory (blocking issues table)
2. Rule Size Inventory (line count assessment table)
3. Parsability Inventory (schema errors, metadata, markdown tables)
4. Completeness Inventory (error/edge case/prerequisite/validation checklist)
5. Consistency Inventory (contradictions, terminology, examples tables)
6. Cross-Agent Consistency Inventory (considerations, conditionals tables)

**Informational inventories (if time permits):**
- Token Efficiency Inventory (budget, redundancy, structure tables) - findings only
- Staleness Inventory (LastUpdated, tools, patterns, links tables) - findings only

### Step 1.4: Verification Checkpoint

Before proceeding, verify:

- [ ] All 9 rubric files read completely?
- [ ] Pattern definitions extracted?
- [ ] Non-Issues lists recorded?
- [ ] All 6 scored inventories created (empty)?

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
2. Rule Size (line count - 100% deterministic)
3. Actionability (blocking issues)
4. Completeness (coverage gaps)
5. Consistency (internal alignment)
6. Token Efficiency (budget/redundancy)
7. Staleness (currency checks)
8. Cross-Agent Consistency (universal compatibility)

### Step 2.2a: Per-Dimension Timing (IF timing_enabled)

When `timing_enabled: true`, wrap each dimension evaluation with checkpoint pairs:

| Before Dimension | After Dimension |
|-----------------|-----------------|
| checkpoint `dim_parsability_start` | checkpoint `dim_parsability_end` |
| checkpoint `dim_rule_size_start` | checkpoint `dim_rule_size_end` |
| checkpoint `dim_actionability_start` | checkpoint `dim_actionability_end` |
| checkpoint `dim_completeness_start` | checkpoint `dim_completeness_end` |
| checkpoint `dim_consistency_start` | checkpoint `dim_consistency_end` |
| checkpoint `dim_token_efficiency_start` | checkpoint `dim_token_efficiency_end` |
| checkpoint `dim_staleness_start` | checkpoint `dim_staleness_end` |
| checkpoint `dim_cross_agent_start` | checkpoint `dim_cross_agent_end` |

**After all dimensions scored:** Compute per-dimension durations from checkpoint pairs and construct `_dimension_timings` JSON array:

```
_dimension_timings = []
for each dimension:
    start_cp = checkpoint where name == f"dim_{dimension}_start"
    end_cp = checkpoint where name == f"dim_{dimension}_end"
    duration = end_cp.elapsed_seconds - start_cp.elapsed_seconds
    _dimension_timings.append({
        "dimension": dimension,
        "duration_seconds": round(duration, 2),
        "mode": "checkpoint"
    })
```

**Pass to timing-end:** Include `--dimension-timings '{{_dimension_timings_json}}'` in the end command.

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
Total = (Actionability × 3.0) + (Rule Size × 2.5) + 
        (Parsability × 1.5) + (Completeness × 1.5) + 
        (Consistency × 1.0) + (Cross-Agent Consistency × 0.5)

Maximum: 100 points (v2.0)
```

### Step 3.2a: Load Output Template

Read `references/REVIEW-OUTPUT-TEMPLATE.md` before generating review content.

**Purpose:** Lock in output structure to prevent cross-model structural drift.

**GATE:** Do NOT generate review markdown until template is loaded.

### Step 3.3: Generate Review (Using Output Template)

Populate `references/REVIEW-OUTPUT-TEMPLATE.md` section by section:
1. Fill File Header placeholders
2. Fill Executive Summary score table (6 rows + Total)
3. Fill Schema Validation Results
4. Fill Agent Executability Verdict
5. Fill Dimension Analysis (6 subsections, each with inventory)
6. Fill Critical Issues
7. Fill Recommendations with inline Staleness
8. Fill Post-Review Checklist (11 fixed items)
9. Fill Conclusion
10. Fill Timing Metadata (if timing_enabled)

**Do NOT deviate from section order, heading names, or table column headers.**

---

## Output

- `review_markdown`: Full Markdown review content with:
  - Score summary
  - All 6 scored dimension inventories
  - Rule Size flags (if applicable)
  - Issue details with line numbers
  - Priority fix recommendations
  - Verdict

---

## Quality Assurance

### Self-Verification Checklist

Before submitting review, verify:

- [ ] All 9 rubric files read (before target)?
- [ ] All 8 inventories created and filled?
- [ ] Line count measured (`wc -l`) for Rule Size?
- [ ] Target read line 1 to END?
- [ ] Only inventory patterns used?
- [ ] Non-Issues list applied?
- [ ] Overlap resolution applied?
- [ ] Inventories included in output?
- [ ] Scores from decision matrices?
- [ ] Rule Size flags applied if >500 lines?

**If ANY checkbox NO:** Review is INVALID, regenerate from Phase 1.

### Pre-Write Output Verification (MANDATORY)

**Before writing review file, verify these structural requirements:**

| Requirement | Check |
|-------------|-------|
| Score table present | 6 rows (all scored dimensions) with scores |
| Line count included | Rule Size inventory with `wc -l` result |
| Line references | ≥15 distinct line citations |
| Direct quotes | ≥3 with line numbers |
| Verdict section | One of: EXECUTABLE, EXECUTABLE_WITH_REFINEMENTS, NEEDS_REFINEMENT, NOT_EXECUTABLE |
| Rule Size flag | SPLIT_RECOMMENDED, SPLIT_REQUIRED, NOT_DEPLOYABLE, BLOCKED, or None |
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
