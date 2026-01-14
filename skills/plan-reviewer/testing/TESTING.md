# Skill Testing Guide: plan-reviewer

> ** AUDIENCE:** This document is for **skill maintainers** (humans), not for Claude.
> It provides testing procedures, troubleshooting guides, and health checks for the skill itself.

## Purpose

Self-validation procedures to ensure the plan-reviewer skill is functioning correctly.

## Quick Health Check

Run these checks to verify skill integrity:

### 1. File Structure Check

```bash
# Verify all required files exist
ls -la skills/plan-reviewer/

# Expected:
# SKILL.md
# README.md
# testing/TESTING.md
# examples/
# tests/
# workflows/
```

### 2. SKILL.md Rubric Check

Verify SKILL.md contains:

- [ ] 8 review dimensions defined
- [ ] Dimension weighting table (4 critical × 2, 4 standard × 1)
- [ ] 5-level scoring scale for each dimension
- [ ] Scoring Impact Rules section
- [ ] Verification table templates
- [ ] Output format templates for all 3 modes
- [ ] Overall Score Interpretation table

### 3. Mode Coverage Check

- **FULL** - Output Template: Required, Verification Tables: All 3, Example File: examples/full-review.md
- **COMPARISON** - Output Template: Required, Verification Tables: N/A, Example File: examples/comparison-review.md
- **META-REVIEW** - Output Template: Required, Verification Tables: N/A, Example File: examples/meta-review.md

## Functional Validation

### Test 1: Input Validation (FULL Mode)

```text
Input:
  target_file: plans/nonexistent.md
  review_mode: FULL
  review_date: 2025-12-16
  model: test-model

Expected: Error - "File not found: plans/nonexistent.md"
```

### Test 2: Input Validation (COMPARISON Mode)

```text
Input:
  target_files: [plans/a.md]  # Only 1 file
  review_mode: COMPARISON
  review_date: 2025-12-16
  model: test-model

Expected: Error - "COMPARISON mode requires at least 2 files"
```

### Test 3: Dimension Scoring

Using a test plan, verify:

1. All 8 dimensions receive scores
2. Point calculations are correct:
   - Executability: raw × 4 = points/20
   - Completeness: raw × 4 = points/20
   - Success Criteria: raw × 4 = points/20
   - Scope: raw × 3 = points/15
   - Dependencies: raw × 2 = points/10
   - Decomposition: raw × 1 = points/5
   - Context: raw × 1 = points/5
   - Risk Awareness: raw × 1 = points/5
3. Total = sum of points = /100

### Test 4: Verdict Assignment

- **92/100** - EXECUTABLE
- **85/100** - EXECUTABLE_WITH_REFINEMENTS
- **70/100** - NEEDS_REFINEMENT
- **50/100** - NOT_EXECUTABLE

### Test 5: Output File Generation

```text
Input:
  target_file: plans/TEST_PLAN.md
  review_mode: FULL
  review_date: 2025-12-16
  model: test-model

Expected output path: reviews/plan-TEST_PLAN-test-model-2025-12-16.md
```

### Test 6: No-Overwrite Safety

1. Create `reviews/plan-X-test-model-2025-12-16.md`
2. Run review for same plan/model/date
3. Verify output is `reviews/plan-X-test-model-2025-12-16-01.md`

## Calibration Validation

### Inter-Model Consistency Test

Run the same plan through multiple models and verify:

1. Score variance < 10 points (acceptable)
2. Score variance < 5 points (good)
3. Verdict agreement (all models same verdict)

### Scoring Impact Rules Test

Create test plans with known characteristics:

- **plan-ambiguous.md** - Characteristic: 12 ambiguous phrases, Expected Score Cap: Executability ≤ 2/5
- **plan-incomplete.md** - Characteristic: 50% validation coverage, Expected Score Cap: Completeness ≤ 3/5
- **plan-no-criteria.md** - Characteristic: 40% success criteria, Expected Score Cap: Success Criteria ≤ 2/5

## Regression Testing

After any SKILL.md changes:

1. Re-run `examples/full-review.md` walkthrough
2. Verify scores match expected (±1 point tolerance)
3. Verify verification tables still populated correctly
4. Verify output format unchanged

## Common Validation Failures

- **Missing dimension** - Cause: SKILL.md incomplete, Fix: Add missing dimension
- **Wrong total score** - Cause: Weighting calculation error, Fix: Check × 2 vs × 1
- **Verdict mismatch** - Cause: Threshold misconfigured, Fix: Check Overall Score Interpretation
- **Output path wrong** - Cause: Slugging error, Fix: Check model-slugging workflow

## Validation Checklist

Before releasing changes to plan-reviewer:

- [ ] All 8 dimensions scorable
- [ ] Point totals correct (/100)
- [ ] All 3 modes produce valid output
- [ ] No-overwrite safety working
- [ ] Error messages actionable
- [ ] Examples execute successfully
- [ ] Tests pass

## Automated Validation (Future)

```python
# Planned: validation.py script
# Will automate the checks above
# Run with: python skills/plan-reviewer/validation.py
```

