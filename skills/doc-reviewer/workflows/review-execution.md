# Workflow: Review Execution

## Purpose

Execute documentation review per specified mode using progressive rubric loading.

## Inputs

- `resolved_targets`: list of file paths to review
- `review_date`: validated date string
- `review_mode`: `FULL` | `FOCUSED` | `STALENESS`
- `review_scope`: `single` | `collection`
- `model_slug`: normalized model identifier
- `focus_area`: (optional) for FOCUSED mode
- `baseline_rules`: list of available documentation rules

## Steps

### Step 1: Read Target Documentation

For each file in `resolved_targets`:
- Read file contents completely
- Note file path and line count
- Extract existing structure (headings, sections)

### Step 2: Read Baseline Rules (if available)

If baseline rules exist, read for comparison:
- `rules/801-project-readme.md` - README standards
- `rules/802-project-contributing.md` - CONTRIBUTING standards

### Step 3: Score Dimensions (Progressive Loading)

**FULL mode:** Score all 6 dimensions
**FOCUSED mode:** Score only `focus_area` dimensions
**STALENESS mode:** Score only Staleness dimension

**For each dimension, read corresponding rubric and score:**

1. **Accuracy (25 points):**
   - Read `../rubrics/accuracy.md`
   - Verify file paths, commands, code examples
   - Create Cross-Reference Verification Table
   - Score using rubric criteria

2. **Completeness (25 points):**
   - Read `../rubrics/completeness.md`
   - Check feature coverage, setup, troubleshooting
   - Create Coverage Checklist
   - Score using rubric criteria

3. **Clarity (20 points):**
   - Read `../rubrics/clarity.md`
   - Perform New User Test
   - Count unexplained jargon
   - Score using rubric criteria

4. **Structure (15 points):**
   - Read `../rubrics/structure.md`
   - Check information flow and heading hierarchy
   - Verify navigation aids
   - Score using rubric criteria

5. **Staleness (10 points):**
   - Read `../rubrics/staleness.md`
   - Test external links (200/404/301 status)
   - Check tool versions
   - Create Link Validation Table
   - Score using rubric criteria

6. **Consistency (5 points):**
   - Read `../rubrics/consistency.md`
   - Check formatting, terminology, conventions
   - Score using rubric criteria

**Progressive disclosure:** Only read rubric files as needed for scoring.

### Step 4: Calculate Total Score

```
Total = Accuracy + Completeness + Clarity + Structure + Staleness + Consistency
Max = 100 points
```

### Step 5: Apply Critical Dimension Overrides

Check critical dimensions (Accuracy, Completeness):
- If Accuracy ≤2/5: Minimum verdict = NEEDS_IMPROVEMENT
- If Completeness ≤2/5: Minimum verdict = NEEDS_IMPROVEMENT
- If both ≤2/5: Verdict = POOR

### Step 6: Determine Verdict

- **90-100** - Verdict: EXCELLENT, Meaning: High-quality documentation
- **80-89** - Verdict: GOOD, Meaning: Minor improvements needed
- **60-79** - Verdict: NEEDS_IMPROVEMENT, Meaning: Significant updates required
- **40-59** - Verdict: POOR, Meaning: Major revision needed
- **<40** - Verdict: INADEQUATE, Meaning: Rewrite from scratch

### Step 7: Generate Recommendations

For each dimension with score <4/5:
- List specific issues found
- Reference line numbers
- Provide concrete fixes
- Prioritize by dimension weight

**Format:**
```markdown
### [Dimension] (Score: X/Y)

**Issues:**
1. [Specific issue] (Line X)
2. [Specific issue] (Lines X-Y)

**Recommendations:**
1. [Concrete fix with example]
2. [Concrete fix with example]
```

### Step 8: Format Review Output

Structure review file per review mode:

**Single scope:** One review per documentation file

**Collection scope:** Consolidated review for all files

**Output sections:**
1. Review metadata (date, model, mode, file(s))
2. Executive summary
3. Total score and verdict
4. Dimension-by-dimension breakdown
5. Verification tables (Cross-Reference, Link Validation, Coverage)
6. Recommendations (prioritized)
7. Conclusion

## Mode-Specific Behavior

### FULL Mode
- Score all 6 dimensions
- Complete verification tables
- Comprehensive recommendations

### FOCUSED Mode
- Score only dimensions in `focus_area`
- Targeted verification
- Focused recommendations

### STALENESS Mode
- Score only Staleness dimension
- Link validation only
- Quick maintenance check

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

## Output

Returns populated review structure ready for file write.
