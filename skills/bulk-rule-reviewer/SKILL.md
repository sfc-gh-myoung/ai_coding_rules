---
name: bulk-rule-reviewer
description: Execute agent-centric reviews on all rules in rules/ directory and generate prioritized improvement report
version: 1.1.0
---

# Bulk Rule Reviewer

## Overview

Execute comprehensive agent-centric reviews on all rule files in `rules/` directory, then generate consolidated priority report. Designed for periodic quality audits, pre-release validation, and technical debt tracking.

### When to Use

- Periodic quality audits (quarterly/monthly)
- Pre-release validation before major version releases
- Technical debt tracking and prioritization
- Baseline quality measurement for improvement initiatives

### Inputs

**Required:**
- **review_date**: `YYYY-MM-DD` (default: today)
- **review_mode**: `FULL` | `FOCUSED` | `STALENESS` (default: FULL)
- **model**: Lowercase-hyphenated slug (default: `claude-sonnet-45`)

**Optional:**
- **filter_pattern**: Glob pattern (default: `rules/*.md`)
  - Examples: `rules/100-*.md` (Snowflake only), `rules/*-core.md` (cores only)
- **skip_existing**: Boolean (default: true) - Resume capability
- **max_parallel**: Integer 1-10 (default: 1) - Concurrent reviews
- **timing_enabled**: `true` | `false` (default: `false`) - Enable execution timing

### Outputs

**Individual reviews:** `reviews/<rule-name>-<model>-<date>.md` (up to 113 files)

**Master summary:** `reviews/_bulk-review-<model>-<date>.md` with sections:
1. Executive Summary (score distribution, dimension analysis)
2. Priority 1: Urgent (score <60, NOT_EXECUTABLE)
3. Priority 2: High (score 60-79, NEEDS_REFINEMENT)
4. Priority 3: Medium (score 80-89, EXECUTABLE_WITH_REFINEMENTS)
5. Priority 4: Excellent (score 90-100, EXECUTABLE)
6. Failed Reviews (execution errors)
7. Top 10 Recommendations (impact × effort prioritization)
8. Next Steps (immediate/short-term/long-term)
9. Appendix: All Rules by Score (sorted table)

## Critical Execution Protocol

### 🚨 MANDATORY ENFORCEMENT

This skill MUST execute the complete rule-reviewer workflow for each rule file.

### How Skills Work Together

**IMPORTANT:** Skills cannot "invoke" other skills programmatically. Skills are documentation that guides agent behavior, not callable subroutines.

**Correct pattern:**
1. Load `skills/rule-reviewer/SKILL.md` to understand the review workflow
2. Load `skills/rule-reviewer/rubrics/*.md` as needed for each dimension
3. Execute the review workflow for each rule file
4. Write review to `reviews/` following rule-reviewer's output format
5. Continue to next rule

**Why this matters:**
- The rule-reviewer skill documents a proven, high-quality review process
- Following its workflow ensures consistency and completeness
- Progressive disclosure (loading rubrics as needed) manages context efficiently
- Each rule deserves full evaluation per the documented process

### Protocol Violations (FORBIDDEN)

Agents commonly attempt these shortcuts. **ALL ARE FORBIDDEN:**

- ❌ **Skipping rubric consultation** - Scoring without reading dimension rubrics
- ❌ **Batch optimization** - Aggregating multiple rules into single review
- ❌ **Parallel shortcuts** - Running concurrently unless max_parallel set
- ❌ **Token-saving shortcuts** - Generating abbreviated reviews
- ❌ **Time-saving shortcuts** - Estimating scores without proper analysis
- ❌ **Template-based reviews** - Using examples/ as templates without actual analysis
- ❌ **Skipping schema validation** - Not running schema_validator.py

### Required Actions

- ✅ Load rule-reviewer/SKILL.md to understand complete workflow
- ✅ Load rubrics/*.md files as needed for each dimension being scored
- ✅ Run schema_validator.py for each rule
- ✅ Perform Agent Execution Test (count blocking issues)
- ✅ Score all dimensions according to review_mode (FULL/FOCUSED/STALENESS)
- ✅ Generate specific recommendations with line numbers
- ✅ Write complete review to reviews/ with proper formatting
- ✅ Follow workflows sequentially (discovery → review-execution → aggregation → summary-report)
- ✅ Show progress every 10 reviews (not more frequently)

### Execution Acknowledgment

**Before proceeding, agent must confirm:**
- [ ] Will follow rule-reviewer workflow for each rule (complete process)
- [ ] Will load and consult rubrics for dimension scoring
- [ ] Will run schema validation for each rule
- [ ] Will perform Agent Execution Test for each rule
- [ ] Will NOT optimize for time/tokens at expense of quality
- [ ] Understands process takes 5-10 hours for 113 rules
- [ ] Will use resume capability (skip_existing) if interrupted

**If cannot commit: STOP and report error.**

### Verification

Each review must contain:
- Executive Summary with scores table (all 6 dimensions for FULL mode)
- Schema Validation Results (from schema_validator.py output)
- Agent Executability Verdict (based on Agent Execution Test)
- Dimension Analysis sections (detailed scoring rationale)
- Critical Issues list (specific line numbers)
- Recommendations (prioritized with expected score improvements)
- Post-Review Checklist
- Conclusion

**Violation consequences:**
- Invalid reviews rejected from summary
- Execution halted with protocol violation error
- User notified of shortcut attempt

**Quality gate:**
- Review file size 3000-8000 bytes (typical for FULL mode)
- < 2000 bytes = too abbreviated (VIOLATION)
- All required sections present (VIOLATION if missing)

## Workflow

### [OPTIONAL] Timing Start

**When:** Only if `timing_enabled: true` in inputs  
**MODE:** Safe in PLAN mode

**See:** `../skill-timing/workflows/timing-start.md`

**Action:** Capture `run_id` in working memory for later use.

**Note:** Timing tracks the entire bulk review process (all stages), not individual rule-reviewer calls.

### [OPTIONAL] Checkpoint: skill_loaded

**When:** Only if timing was started  
**Checkpoint name:** `skill_loaded`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Stage 1: Discovery

Find all `.md` files in `rules/` directory, apply filter_pattern, sort alphabetically.

**See:** `workflows/discovery.md`

### [OPTIONAL] Checkpoint: discovery_complete

**When:** Only if timing was started  
**Checkpoint name:** `discovery_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Stage 2: Review Execution

For each rule file:
1. Extract rule name from path
2. Check if review exists (if skip_existing=true)
3. Invoke rule-reviewer skill with parameters
4. Parse output path from response
5. Store (rule_name, score, verdict, review_path)
6. Show progress every 10 reviews

**See:** `workflows/review-execution.md` for orchestration details, resume capability, error handling.

### [OPTIONAL] Checkpoint: reviews_complete

**When:** Only if timing was started  
**Checkpoint name:** `reviews_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Stage 3: Aggregation

For each review file:
1. Read first 150 lines only (context management)
2. Extract: overall score, verdict, critical issues, dimension scores
3. Build lightweight data structure (no full content)
4. Calculate statistics: average, median, distribution

**See:** `workflows/aggregation.md` for parsing strategy and statistics calculations.

### [OPTIONAL] Checkpoint: aggregation_complete

**When:** Only if timing was started  
**Checkpoint name:** `aggregation_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### Stage 4: Summary Report

Generate master summary with:
- Prioritized sections (Priority 1-4)
- Rules sorted by score within tiers
- Impact × effort ratios for recommendations
- Write to `reviews/_bulk-review-<model>-<date>.md`

**See:** `workflows/summary-report.md` for report format and section generation.

### [OPTIONAL] Checkpoint: summary_complete

**When:** Only if timing was started  
**Checkpoint name:** `summary_complete`

**See:** `../skill-timing/workflows/timing-checkpoint.md`

### [OPTIONAL] Timing End (Compute)

**When:** Only if timing was started  
**MODE:** Safe in PLAN mode (outputs to STDOUT only)

**See:** `../skill-timing/workflows/timing-end.md` (Step 1)

**Action:** Capture STDOUT output for metadata embedding.

### [MODE TRANSITION: PLAN → ACT]

Authorization required for file modifications.

### [OPTIONAL] Timing End (Embed)

**When:** Only if timing was started  
**MODE:** Requires ACT mode (appends metadata to file)

**See:** `../skill-timing/workflows/timing-end.md` (Step 2)

**Action:** Parse STDOUT, append timing metadata section to summary report file.

## Critical Design Decisions

**Context Management:** Parse only first 150 lines of each review (scores/verdicts only). Full details remain in individual files.

**Stateless Execution:** Review failures don't stop batch. Resume via skip_existing parameter.

**See:** `workflows/aggregation.md` for complete strategy.

## Error Handling

**Review failure:** Continue with next file, log error, mark FAILED in summary.

**Context overflow:** Switch to minimal output mode, report warning, continue.

**File write failure:** Print OUTPUT_FILE directive for manual save, continue.

**Empty rules directory:** Report error, exit gracefully without empty summary.

**Partial completion:** Resume capability allows continuation using existing reviews.

## Usage Examples

### Basic Invocation (All Rules, Full Review)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
```

### Filtered Review (Snowflake Rules Only)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
filter_pattern: rules/100-*.md
```

### Force Re-Review (Overwrite Existing)

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-45
skip_existing: false
```

### Staleness Check Only

```
Use the bulk-rule-reviewer skill.

review_date: 2026-01-06
review_mode: STALENESS
model: claude-sonnet-45
```

## Success Criteria

- ✅ All matching rules reviewed (or filtered subset)
- ✅ Individual review files written to `reviews/`
- ✅ Master summary report generated with valid path
- ✅ Prioritized improvement list included
- ✅ No context overflow during execution
- ✅ Resume capability functional (existing reviews skipped)
- ✅ Error handling graceful (failed reviews don't stop batch)

## Expected Outcomes

**Score distribution:** Average, median, distribution by priority tier.

**Dimension analysis:** Average scores for all 6 dimensions.

**Critical issues summary:** Count of rules with 0, 1-2, 3+ critical issues.

**Prioritized recommendations:** Top 10 rules to improve (impact × effort), estimated effort, expected score improvement.

**Next steps:** Immediate actions, short-term goals, long-term strategy.

## Installation Requirements

**Dependency:** rule-reviewer skill (required)

**Skill location resolution supports two patterns:**

1. **Installed Skill (Recommended):** Install `rule-reviewer` via agent tool's skill management
2. **Local Skill (Fallback):** Ensure `skills/rule-reviewer/` exists in project

**Auto-detection:** Automatically detects which pattern is available.

**Error handling:** If neither found, execution stops with installation guidance.

## Validation

**See:** `workflows/input-validation.md` for validation workflow and code patterns.

**Key Requirements:**
- `review_date`: YYYY-MM-DD format (valid calendar date)
- `review_mode`: FULL | FOCUSED | STALENESS (uppercase)
- `model`: lowercase-hyphenated (e.g., claude-sonnet-45)
- `filter_pattern`: rules/*.md glob (optional, must match ≥1 file)
- `skip_existing`: boolean true/false (optional, default: true)
- `max_parallel`: integer 1-10 (optional, default: 1)
- Environment: rules/ exists and readable, reviews/ writable

**Execution:** Validate inputs before Stage 1 (Discovery). Fail fast on errors.

## Examples

- `examples/full-bulk-review.md` - Complete walkthrough with 113 rules

## Related Skills

- **rule-reviewer** - Single rule review (required dependency)
- **rule-creator** - Create new rules (complementary)

## References

### Rules

- `rules/002f-claude-code-skills.md` - Skill authoring best practices
- `rules/002-rule-governance.md` - Rule schema and standards
- `rules/000-global-core.md` - Foundation patterns
