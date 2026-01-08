---
name: doc-reviewer
description: Review project documentation for accuracy, completeness, clarity, and structure. Verifies file references, tests commands, validates links. Use for documentation audits, README reviews, or staleness checks. Triggers on "review docs", "audit documentation", "check README".
version: 2.1.0
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
- **focus_area**: Required if `review_mode` is `FOCUSED`. If FOCUSED mode and focus_area missing: STOP, report error `Missing required input: focus_area for FOCUSED mode`
- **timing_enabled**: `true` | `false` (default: `false`) - Enable execution timing

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

**Critical Dimensions (50 points - wrong/missing info blocks users):**
- **Accuracy** - Raw: X/5, Weight: ×5, Points: Y/25
- **Completeness** - Raw: X/5, Weight: ×5, Points: Y/25

**Important Dimensions (35 points - affects usability):**
- **Clarity** - Raw: X/5, Weight: ×4, Points: Y/20
- **Structure** - Raw: X/5, Weight: ×3, Points: Y/15

**Standard Dimensions (15 points - formatting/conventions):**
- **Staleness** - Raw: X/5, Weight: ×2, Points: Y/10
- **Consistency** - Raw: X/5, Weight: ×1, Points: Y/5

### Dimension Summaries

**1. Accuracy (25 points) - Is documentation current with codebase?**
- Measures: File paths exist, commands work, code examples current
- Key gate: <60% references valid caps at 1/5 (Formula: Valid references / Total references in Cross-Reference Verification Table)
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

**Detailed rubrics:** See `rubrics/[dimension].md` for complete scoring criteria:
- `rubrics/accuracy.md` - File paths, commands, code examples
- `rubrics/completeness.md` - Feature coverage, setup, troubleshooting
- `rubrics/clarity.md` - New user accessibility, jargon, examples
- `rubrics/structure.md` - Information flow, heading hierarchy
- `rubrics/staleness.md` - Link validation, tool versions
- `rubrics/consistency.md` - Formatting, terminology, conventions

**Progressive disclosure:** Read each rubric only when scoring that dimension.

### Mandatory Verification Tables

**Required for scoring justification:**

1. **Cross-Reference Verification** (Accuracy) - Verify file paths, commands, function names
2. **Link Validation** (Staleness) - Test external links, check tool versions
3. **Coverage Checklist** (Completeness) - Track documented vs undocumented features

**See:** `rubrics/accuracy.md` and `rubrics/staleness.md` for table formats

### Verdict Thresholds

**Score Ranges:**
- **90-100** - EXCELLENT - High-quality documentation
- **80-89** - GOOD - Minor improvements needed
- **60-79** - NEEDS_IMPROVEMENT - Significant updates required
- **40-59** - POOR - Major revision needed
- **<40** - INADEQUATE - Rewrite from scratch

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

### 3. [OPTIONAL] Timing Start

**When:** Only if `timing_enabled: true` in inputs  
**MODE:** Safe in PLAN mode

**See:** `../skill-timing/workflows/timing-start.md`

**Action:** Capture `run_id` in working memory for later use.

### 4. [OPTIONAL] Checkpoint: skill_loaded

**When:** Only if timing was started  
**Checkpoint name:** `skill_loaded`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### 5. Review Execution

Execute complete review per rubric. This is the core workflow.

**FULL mode:** Score all 6 dimensions
**FOCUSED mode:** Score specified focus_area dimension(s) only
**STALENESS mode:** Score Staleness dimension only (fast maintenance check)

**See:** `workflows/review-execution.md` (detailed rubric, verification tables, scoring criteria)

### 6. [OPTIONAL] Checkpoint: review_complete

**When:** Only if timing was started  
**Checkpoint name:** `review_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### 7. [OPTIONAL] Timing End (Compute)

**When:** Only if timing was started  
**MODE:** Safe in PLAN mode (outputs to STDOUT only)

**See:** `../skill-timing/workflows/timing-end.md` (Step 1)

**Action:** Capture STDOUT output for metadata embedding.

### 8. [MODE TRANSITION: PLAN → ACT]

Request user ACT authorization before file modifications.

### 9. File Write

Write review to `reviews/` with appropriate filename per scope.

**See:** `workflows/file-write.md`

### 10. [OPTIONAL] Timing End (Embed)

**When:** Only if timing was started  
**MODE:** Requires ACT mode (appends metadata to file)

**See:** `../skill-timing/workflows/timing-end.md` (Step 2)

**Action:** Parse STDOUT from step 7, append timing metadata section to output file.

### 11. Error Handling

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
- Test commands shown in documentation if: (1) read-only (ls, cat, grep), (2) uses --dry-run flag, OR (3) targets test/sandbox directories
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
