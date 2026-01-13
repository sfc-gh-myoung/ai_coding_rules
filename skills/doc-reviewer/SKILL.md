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
- **output_root**: Root directory for output files (default: `reviews/`). Subdirectories `doc-reviews/` or `summaries/` appended automatically. Supports relative paths including `../`.
- **overwrite**: `true` | `false` (default: `false`) - If true, overwrite existing review file. If false, use sequential numbering (-01, -02, etc.)
- **timing_enabled**: `true` | `false` (default: `false`) - Enable execution timing

### Default Target Files

When `target_files` not specified, reviews:
- `./README.md` - Project overview and setup
- `./CONTRIBUTING.md` - Contribution guidelines  
- `./docs/*.md` - All documentation files in docs/ folder

### Output

**Single scope (per-file):** `{output_root}/doc-reviews/<doc-name>-<model>-<YYYY-MM-DD>.md`

**Collection scope (all files):** `{output_root}/summaries/_docs-collection-<model>-<YYYY-MM-DD>.md` with consolidated report

(Default `output_root: reviews/`. With `output_root: mytest/` → `mytest/doc-reviews/...`)

## Review Rubric

### Scoring Formula

**Raw Score Range:** 0-10 per dimension
**Formula:** Raw (0-10) × (Weight / 2) = Points

**Total: 100 points weighted across 6 dimensions:**

**Critical Dimensions (50 points - wrong/missing info blocks users):**
- **Accuracy** - Raw: X/10, Weight: 5, Points: Y/25
- **Completeness** - Raw: X/10, Weight: 5, Points: Y/25

**Important Dimensions (35 points - affects usability):**
- **Clarity** - Raw: X/10, Weight: 4, Points: Y/20
- **Structure** - Raw: X/10, Weight: 3, Points: Y/15

**Standard Dimensions (15 points - formatting/conventions):**
- **Staleness** - Raw: X/10, Weight: 2, Points: Y/10
- **Consistency** - Raw: X/10, Weight: 1, Points: Y/5

### Dimension Summaries

**1. Accuracy (25 points) - Is documentation current with codebase?**
- Measures: File paths exist, commands work, code examples current
- Key gate: <60% references valid caps at 2/10 (Formula: Valid references / Total references in Cross-Reference Verification Table)
- **Requires:** Cross-Reference Verification Table

**2. Completeness (25 points) - Are all features documented?**
- Measures: Feature coverage, setup steps, API docs, troubleshooting
- Key gate: Incomplete setup caps at 4/10

**3. Clarity (20 points) - Is it user-friendly?**
- Measures: New user test, unexplained jargon, missing examples
- Key gate: Impenetrable to new users caps at 2/10

**4. Structure (15 points) - Is it well-organized?**
- Measures: Logical flow, navigation, heading hierarchy
- Key gate: No structure caps at 2/10

**5. Staleness (10 points) - Are references current?**
- Measures: Tool versions, broken links, deprecated patterns
- Key gate: Most links broken caps at 2/10
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
- Accuracy ≤4/10 → Minimum NEEDS_IMPROVEMENT
- Completeness ≤4/10 → Minimum NEEDS_IMPROVEMENT
- Both ≤4/10 → POOR

## Workflow

### 1. Input Validation

Validate review_date, review_mode, model, target_files, review_scope.

**See:** `workflows/input-validation.md`

### 2. Model Slugging

Convert model name to lowercase-hyphenated slug for filenames.

**See:** `workflows/model-slugging.md`

### 3. [CONDITIONAL] Timing Instrumentation

**Execute IF:** `timing_enabled: true`  
**Skip IF:** `timing_enabled: false` (default) → Proceed to step 4

**When enabled, execute ALL steps below (not optional once enabled):**

| When | Action | Command | Track |
|------|--------|---------|-------|
| Before review | Start timing | `run_timing.sh start --skill doc-reviewer --target {{target_file}} --model {{model}} --mode {{review_mode}}` | Store `_timing_run_id` |
| After rubrics loaded | Checkpoint | `run_timing.sh checkpoint --run-id {{_timing_run_id}} --name skill_loaded` | - |
| After review complete | Checkpoint | `run_timing.sh checkpoint --run-id {{_timing_run_id}} --name review_complete` | - |
| Before file write | Compute | `run_timing.sh end --run-id {{_timing_run_id}} --output-file {{output_file}} --skill doc-reviewer` | Store `_timing_stdout` |
| After file write (ACT) | Embed | Parse `_timing_stdout`, append timing metadata section to output file | - |

**Working memory contract:** Retain `_timing_run_id` and `_timing_stdout` from start through embed.

**Quick Reference:**
```bash
# 1. Start (store _timing_run_id from output)
bash skills/skill-timing/scripts/run_timing.sh start \
    --skill doc-reviewer --target README.md --model claude-sonnet-45 --mode FULL
# Output: TIMING_RUN_ID=doc-reviewer-README-20260108-abc123

# 2. Checkpoint: skill_loaded
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id doc-reviewer-README-20260108-abc123 --name skill_loaded

# 3. Checkpoint: review_complete  
bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id doc-reviewer-README-20260108-abc123 --name review_complete

# 4. End (store _timing_stdout from output)
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id doc-reviewer-README-20260108-abc123 \
    --output-file reviews/doc-reviews/README-claude-sonnet-45-2026-01-08.md \
    --skill doc-reviewer

# 5. Embed: Parse _timing_stdout, append to output file (ACT mode required)
```

**See:** `../skill-timing/workflows/` for detailed workflow documentation.

### 4. Review Execution

Execute complete review per rubric. This is the core workflow.

**FULL mode:** Score all 6 dimensions
**FOCUSED mode:** Score specified focus_area dimension(s) only
**STALENESS mode:** Score Staleness dimension only (fast maintenance check)

**See:** `workflows/review-execution.md` (detailed rubric, verification tables, scoring criteria)

### 5. [MODE TRANSITION: PLAN → ACT]

Request user ACT authorization before file modifications.

### 6. File Write

Write review to `reviews/doc-reviews/` (single) or `reviews/summaries/` (collection) with appropriate filename.

**See:** `workflows/file-write.md`

### 7. Post-Execution Validation

**Always:** Verify review file was written successfully.

**IF `timing_enabled: true`:**
1. Check timing metadata exists: `grep -q "## Timing Metadata" {{output_file}}`
2. IF missing AND `_timing_run_id` captured: Attempt recovery embed now
3. IF missing AND no `_timing_run_id`: WARN "Timing enabled but run_id not captured"

### 8. Error Handling

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
- Format: `reviews/doc-reviews/<doc-name>-<model>-<date>.md`
- Use for detailed per-file analysis

**Collection Scope:**
- One consolidated review for all documentation files
- Format: `reviews/summaries/_docs-collection-<model>-<date>.md`
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
