---
name: doc-reviewer
description: Review project documentation for accuracy, completeness, clarity, and structure. Verifies file references, tests commands, validates links. Use for documentation audits, README reviews, or staleness checks. Triggers on "review docs", "audit documentation", "check README".
version: 1.0.0
---

# Documentation Reviewer

## Overview

Review project documentation for accuracy with codebase, completeness of coverage, clarity for users, consistency with conventions, staleness of references, and logical structure. Uses a 6-dimension rubric optimized for user success.

### When to Use

- Review documentation (README, CONTRIBUTING, docs/*.md)
- Conduct FULL / FOCUSED / STALENESS documentation review
- Verify documentation is current with the codebase
- Check for broken links or outdated references

### Inputs

**Required:**
- **review_date**: `YYYY-MM-DD`
- **review_mode**: `FULL` | `FOCUSED` | `STALENESS`
- **model**: Model slug (e.g., `claude-sonnet-45`)

**Optional:**
- **target_files**: List of file paths (defaults to project docs if not specified)
- **review_scope**: `single` | `collection` (default: `single`)
- **focus_area**: Required if `review_mode` is `FOCUSED`

### Default Target Files

When `target_files` not specified, reviews:
- `./README.md` - Project overview and setup
- `./CONTRIBUTING.md` - Contribution guidelines  
- `./docs/*.md` - All documentation files in docs/ folder

### Output

**Single scope (per-file):** `reviews/<doc-name>-<model>-<YYYY-MM-DD>.md`

**Collection scope (all files):** `reviews/_docs-collection-<model>-<YYYY-MM-DD>.md` with consolidated report

## Review Rubric

### Scoring Formula

**Total: 100 points weighted across 6 dimensions:**

| Dimension | Raw | Weight | Points | Category |
|-----------|-----|--------|--------|----------|
| Accuracy | X/5 | ×5 | Y/25 | Critical |
| Completeness | X/5 | ×5 | Y/25 | Critical |
| Clarity | X/5 | ×4 | Y/20 | Important |
| Structure | X/5 | ×3 | Y/15 | Important |
| Staleness | X/5 | ×2 | Y/10 | Standard |
| Consistency | X/5 | ×1 | Y/5 | Standard |

**Critical dimensions:** 50 points (wrong/missing info blocks users)
**Important dimensions:** 35 points (affects usability)
**Standard dimensions:** 15 points (polish)

### Dimension Summaries

**1. Accuracy (25 points) - Is documentation current with codebase?**
- Measures: File paths exist, commands work, code examples current
- Key gate: <60% references valid caps at 1/5
- **Requires:** Cross-Reference Verification Table

**2. Completeness (25 points) - Are all features documented?**
- Measures: Feature coverage, setup steps, API docs, troubleshooting
- Key gate: Incomplete setup caps at 2/5

**3. Clarity (20 points) - Is it user-friendly?**
- Measures: New user test, unexplained jargon, missing examples
- Key gate: Impenetrable to new users caps at 1/5

**4. Structure (15 points) - Is it well-organized?**
- Measures: Logical flow, navigation, heading hierarchy
- Key gate: No structure caps at 1/5

**5. Staleness (10 points) - Are references current?**
- Measures: Tool versions, broken links, deprecated patterns
- Key gate: Most links broken caps at 1/5
- **Requires:** Link Validation Table

**6. Consistency (5 points) - Does it follow conventions?**
- Measures: Formatting style, naming consistency, terminology alignment
- If project has rules/801-project-readme.md or rules/802-project-contributing.md, verify compliance

**See:** `workflows/review-execution.md` for complete rubric details, scoring criteria, and verification tables.

### Mandatory Verification Tables

**Required for scoring justification:**

1. **Cross-Reference Verification** (Accuracy) - Verify file paths, commands, function names
2. **Link Validation** (Staleness) - Test external links, check tool versions
3. **Coverage Checklist** (Completeness) - Track documented vs undocumented features

**See:** `workflows/review-execution.md` section "Verification Tables"

### Verdict Thresholds

| Score | Verdict | Meaning |
|-------|---------|---------|
| 90-100 | EXCELLENT | High-quality documentation |
| 80-89 | GOOD | Minor improvements needed |
| 60-79 | NEEDS_IMPROVEMENT | Significant updates required |
| 40-59 | POOR | Major revision needed |
| <40 | INADEQUATE | Rewrite from scratch |

**Critical dimension overrides:**
- Accuracy ≤2/5 → Minimum NEEDS_IMPROVEMENT
- Completeness ≤2/5 → Minimum NEEDS_IMPROVEMENT
- Both ≤2/5 → POOR

## Workflow

### 1. Input Validation

Validate review_date, review_mode, model, target_files, review_scope.

**See:** `workflows/input-validation.md`

### 2. Model Slugging

Convert model name to lowercase-hyphenated slug for filenames.

**See:** `workflows/model-slugging.md`

### 3. Review Execution

Execute complete review per rubric. This is the core workflow.

**FULL mode:** Score all 6 dimensions
**FOCUSED mode:** Score specified focus_area dimension(s) only
**STALENESS mode:** Score Staleness dimension only (fast maintenance check)

**See:** `workflows/review-execution.md` (detailed rubric, verification tables, scoring criteria)

### 4. File Write

Write review to `reviews/` with appropriate filename per scope.

**See:** `workflows/file-write.md`

### 5. Error Handling

Handle validation failures, file write errors, broken links, missing files.

**See:** `workflows/error-handling.md`

## Review Modes

**FULL Mode (default):**
- All 6 dimensions evaluated
- Complete verification tables
- Use for comprehensive documentation audits

**FOCUSED Mode:**
- Specific dimension(s) only
- Targeted improvements
- Use when specific areas need attention (e.g., focus_area: "Accuracy,Completeness")

**STALENESS Mode:**
- Staleness dimension only
- Fast check for outdated content
- Use for quarterly/annual maintenance

## Review Scope

**Single Scope (default):**
- One review file per documentation file
- Format: `reviews/<doc-name>-<model>-<date>.md`
- Use for detailed per-file analysis

**Collection Scope:**
- One consolidated review for all documentation files
- Format: `reviews/_docs-collection-<model>-<date>.md`
- Use for holistic documentation assessment

## Cross-Reference Verification

Verifies documentation matches codebase: file paths exist, commands work, function/class names accurate.

**See:** `workflows/review-execution.md` section "Cross-Reference Verification"

## Link Validation

Tests external URLs for 200 status, identifies redirects and 404s, checks tool version references.

**See:** `workflows/review-execution.md` section "Link Validation"

## Hard Requirements

- Do NOT ask user to manually copy/paste review
- Do NOT print entire review if file writing succeeds
- Verify file references against actual project structure
- Test commands shown in documentation (when safe to execute)
- Test external links for 404s
- If file write fails: Print `OUTPUT_FILE: <path>` then full review

## Examples

- `examples/full-review.md` - Complete FULL mode README review
- `examples/focused-review.md` - FOCUSED mode (Accuracy only)
- `examples/staleness-review.md` - STALENESS mode maintenance check
- `examples/edge-cases.md` - Handling unusual scenarios

## Related Skills

- **rule-creator** - Create rules (documentation follows similar quality standards)
- **plan-reviewer** - Review plans (complementary)

## References

### Rules

- `rules/801-project-readme.md` - README standards
- `rules/802-project-contributing.md` - CONTRIBUTING standards
- `rules/000-global-core.md` - Foundation patterns
