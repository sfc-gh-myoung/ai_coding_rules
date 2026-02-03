# DELTA Review Workflow

**Purpose:** Compare current plan version against a prior baseline review to track improvements and regressions.

## Phase 0: Validate Baseline (MANDATORY)

**Check baseline_review file exists:**

```bash
if [ ! -f "$baseline_review" ]; then
    echo "ERROR: Baseline file not found: $baseline_review"
    echo "FALLBACK: Executing FULL mode instead of DELTA"
    exit 0
fi
```

**On missing baseline:**
- Log: "DELTA requested but baseline not found at: [path]"
- Execute FULL mode workflow instead
- Include in output: "Note: DELTA requested, executed as FULL (baseline missing)"

**Validation Checklist:**
- [ ] baseline_review file exists at specified path
- [ ] baseline_review is a valid review file (contains score breakdown)
- [ ] target_file exists and is readable

**If validation fails:** Fall back to FULL mode, document fallback in output.

## Phase 1: Load Baseline

### Step 1.1: Parse Baseline Review

Extract from baseline_review file:
- Overall score (e.g., "78/100")
- Dimension scores (8 values)
- Issue list with IDs

### Step 1.2: Extract Issue Inventory

Parse Issue IDs using these prefixes:
- `E###` = Executability issues
- `C###` = Completeness issues  
- `S###` = Success Criteria issues
- `SC###` = Scope issues
- `D###` = Dependencies issues
- `DC###` = Decomposition issues
- `CX###` = Context issues
- `R###` = Risk Awareness issues

**Build baseline inventory:**

| Issue ID | Line | Description | Baseline Status |
|----------|------|-------------|-----------------|
| E001 | 186 | Undefined threshold "near" | OPEN |
| E002 | 245 | Missing else branch | OPEN |
| C001 | 89 | No error recovery for API call | OPEN |

### Step 1.3: Record Baseline Scores

```markdown
## Baseline Scores (from {baseline_date})

| Dimension | Raw | Points |
|-----------|-----|--------|
| Executability | X/10 | Y/20 |
| Completeness | X/10 | Y/20 |
| Success Criteria | X/10 | Y/20 |
| Scope | X/10 | Y/15 |
| Dependencies | X/10 | Y/10 |
| Decomposition | X/10 | Y/5 |
| Context | X/10 | Y/5 |
| Risk Awareness | X/10 | Y/5 |
| **TOTAL** | | **ZZ/100** |
```

## Phase 2: Review Current Plan

Execute full 8-dimension review of target_file using standard workflow.

**Use same process as FULL mode:**
1. Load all rubric definitions (Phase 1 from review-execution.md)
2. Fill all worksheets systematically (Phase 2 from review-execution.md)
3. Calculate scores (Phase 3 from review-execution.md)

**Important:** Use identical rubrics and counting methods as baseline review for fair comparison.

**Output:** Complete dimension scores and new issue inventory for current version.

## Phase 3: Compare Results

### Step 3.1: Match Issues

For each issue in baseline inventory:
1. Check if issue still exists in current plan
2. If same line number: Direct match
3. If line shifted: Match by description/pattern
4. If not found: Potentially FIXED

For each new issue found:
1. Check if it existed in baseline
2. If not in baseline: NEW issue
3. Assign new Issue ID

### Step 3.2: Build Comparison Table

| Issue ID | Line | Description | Baseline | Current | Delta |
|----------|------|-------------|----------|---------|-------|
| E001 | 186 | Undefined threshold | OPEN | FIXED | ✓ Resolved |
| E002 | 245 | Missing else branch | OPEN | OPEN | - No change |
| E003 | 312 | Vague "as needed" | - | NEW | ⚠ New issue |
| C001 | 89 | No error recovery | OPEN | FIXED | ✓ Resolved |
| C002 | 156 | Missing cleanup | OPEN | REGRESSION | ⚠ Was fixed, now broken |

### Step 3.3: Status Definitions

- **FIXED (✓):** Issue from baseline no longer present in current version
- **OPEN (-):** Issue exists in both baseline and current (unchanged)
- **NEW (⚠):** Issue in current that wasn't in baseline
- **REGRESSION (⚠⚠):** Issue was FIXED in an intermediate version but returned

## Phase 4: Calculate Delta

### Step 4.1: Score Changes

| Dimension | Baseline | Current | Change |
|-----------|----------|---------|--------|
| Executability | 6/10 | 8/10 | +2 ↑ |
| Completeness | 7/10 | 7/10 | 0 = |
| Success Criteria | 5/10 | 7/10 | +2 ↑ |
| Scope | 8/10 | 7/10 | -1 ↓ |
| Dependencies | 9/10 | 9/10 | 0 = |
| Decomposition | 8/10 | 8/10 | 0 = |
| Context | 6/10 | 7/10 | +1 ↑ |
| Risk Awareness | 7/10 | 8/10 | +1 ↑ |
| **TOTAL** | 72/100 | 81/100 | **+9 ↑** |

### Step 4.2: Issue Resolution Summary

```markdown
## Issue Resolution Summary

**Resolved:** X issues fixed
**Unchanged:** Y issues still open  
**New:** Z new issues introduced
**Regressions:** W issues returned

**Net change:** +X resolved, -Z new = Net {+/-}N issues
```

### Step 4.3: Explain Score Changes

For each dimension with score change ≥2 points:
- List issues resolved (contributed to increase)
- List new issues (contributed to decrease)
- Explain why score changed

## Phase 5: Generate Report

### Step 5.1: Output Filename

```
{plan-name}-delta-{baseline-date}-to-{current-date}-{model}.md
```

Example: `PLAN_RULES_SPLIT-delta-2026-01-15-to-2026-01-21-claude-sonnet-4.md`

### Step 5.2: Report Structure

```markdown
# DELTA Review: {Plan Name}

**Baseline:** {baseline_review} ({baseline_date})
**Current:** {target_file} ({current_date})
**Model:** {model}
**Mode:** DELTA

## Executive Summary

**Score Change:** {baseline_score} → {current_score} ({+/-}N points)
**Verdict Change:** {baseline_verdict} → {current_verdict}

**Key Improvements:**
- [List top 3 improvements]

**Remaining Issues:**
- [List top 3 unresolved issues]

**New Concerns:**
- [List any new issues introduced]

## Score Comparison

[Score change table from Phase 4]

## Issue Tracking

[Comparison table from Phase 3]

## Dimension-by-Dimension Analysis

### Executability: {baseline} → {current} ({change})

**Resolved Issues:**
- E001: [Description] - FIXED

**Remaining Issues:**
- E002: [Description] - OPEN

**New Issues:**
- E003: [Description] - NEW

[Repeat for each dimension with changes]

## Recommendations

### Priority 1: Address New Issues
[List new issues that need attention]

### Priority 2: Continue Existing Fixes
[Guidance on remaining open issues]

### Priority 3: Prevent Regressions
[Advice on maintaining fixes]

## Next Steps

1. [Specific action item]
2. [Specific action item]
3. [Specific action item]
```

### Step 5.3: Write File

Use `workflows/file-write.md` with DELTA-specific filename pattern.

## Error Handling

### Baseline Not Found
- Log warning
- Fall back to FULL mode
- Include note in output

### Baseline Parse Failure
- Log error with specific parse issue
- Fall back to FULL mode
- Include note in output

### Issue ID Mismatch
- If baseline uses different ID format: Adapt to baseline format
- Document any ID mapping in output

## Quality Checks

Before finalizing DELTA review:

- [ ] Baseline scores correctly extracted?
- [ ] All baseline issues accounted for (FIXED, OPEN, or REGRESSION)?
- [ ] All current issues have IDs (existing or NEW)?
- [ ] Score changes explained?
- [ ] Issue tracking table complete?
- [ ] Recommendations address open and new issues?
