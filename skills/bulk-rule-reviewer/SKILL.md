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

This skill MUST invoke `rule-reviewer` skill exactly once for each rule file. 

### Protocol Violations (FORBIDDEN)

Agents commonly attempt these optimizations. **ALL ARE FORBIDDEN:**

- ❌ **Reimplementing review logic** - Creating Python/bash scoring scripts
- ❌ **Batch optimization** - Aggregating multiple rules into single review
- ❌ **Parallel shortcuts** - Running concurrently unless max_parallel set
- ❌ **Token-saving shortcuts** - Skipping review steps
- ❌ **Time-saving shortcuts** - Abbreviating reviews
- ❌ **Cached reviews** - Generating without invoking rule-reviewer
- ❌ **Summary-only reviews** - Creating lightweight reviews

### Required Actions

- ✅ Invoke `rule-reviewer` skill once per rule file
- ✅ Pass all parameters: target_file, review_date, review_mode, model
- ✅ Wait for "Review written to: ..." confirmation
- ✅ Parse output path from response
- ✅ Validate review file exists before continuing
- ✅ Follow workflows/01-04 sequentially
- ✅ Show progress every 10 reviews (not more frequently)

### Execution Acknowledgment

**Before proceeding, agent must confirm:**
- [ ] Will invoke rule-reviewer for each rule (no reimplementation)
- [ ] Will follow workflows/01-04 exactly as written
- [ ] Will NOT optimize for time/tokens at expense of quality
- [ ] Understands process takes 5-10 hours for 113 rules
- [ ] Will use resume capability (skip_existing) if interrupted

**If cannot commit: STOP and report error.**

### Enforcement Mechanism

Each review invocation must produce:
```
Use the rule-reviewer skill.

target_file: rules/XXX-YYY.md
review_date: YYYY-MM-DD
review_mode: FULL
model: <model>
```

**Verification:** Response must contain: `"Review written to: reviews/<filename>.md"`

**Violation consequences:**
- Invalid reviews rejected from summary
- Execution halted with protocol violation error
- User notified of shortcut attempt

**Why this matters:**
- rule-reviewer contains domain expertise (rubrics, priority checks)
- Reimplementation loses review quality and consistency
- Token/time optimization sacrifices accuracy
- Each rule deserves full evaluation

## Workflow

### Stage 1: Discovery

Find all `.md` files in `rules/` directory, apply filter_pattern, sort alphabetically.

**See:** `workflows/01-discovery.md`

### Stage 2: Review Execution

For each rule file:
1. Extract rule name from path
2. Check if review exists (if skip_existing=true)
3. Invoke rule-reviewer skill with parameters
4. Parse output path from response
5. Store (rule_name, score, verdict, review_path)
6. Show progress every 10 reviews

**See:** `workflows/02-review-execution.md` for orchestration details, resume capability, error handling.

### Stage 3: Aggregation

For each review file:
1. Read first 150 lines only (context management)
2. Extract: overall score, verdict, critical issues, dimension scores
3. Build lightweight data structure (no full content)
4. Calculate statistics: average, median, distribution

**See:** `workflows/03-aggregation.md` for parsing strategy and statistics calculations.

### Stage 4: Summary Report

Generate master summary with:
- Prioritized sections (Priority 1-4)
- Rules sorted by score within tiers
- Impact × effort ratios for recommendations
- Write to `reviews/_bulk-review-<model>-<date>.md`

**See:** `workflows/04-summary-report.md` for report format and section generation.

## Critical Design Decisions

**Context Management:** Parse only first 150 lines of each review (scores/verdicts only). Full details remain in individual files.

**Stateless Execution:** Review failures don't stop batch. Resume via skip_existing parameter.

**See:** `workflows/03-aggregation.md` for complete strategy.

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

**See:** `VALIDATION.md` for complete validation rules. Key checks:
- `review_date` must match YYYY-MM-DD format
- `review_mode` must be FULL | FOCUSED | STALENESS
- `model` must be lowercase-hyphenated
- `filter_pattern` must be valid glob
- `rules/` directory must exist and be readable
- `skip_existing` must be boolean
- `max_parallel` must be 1-10

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
