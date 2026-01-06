# Bulk Rule Reviewer Skill

---
name: bulk-rule-reviewer
description: Execute agent-centric reviews on all rules in rules/ directory and generate prioritized improvement report
version: 1.1.0
author: AI Coding Rules Project
tags: [bulk-review, rule-audit, batch-processing, quality-report, prioritization]
dependencies: [rule-reviewer]
---

## Purpose

Execute comprehensive agent-centric reviews on all rule files in the `rules/` directory, then generate a consolidated priority report showing which rules need attention. Designed for periodic quality audits, pre-release validation, and technical debt tracking.

## Execution Contract (CRITICAL - NON-NEGOTIABLE)

**MANDATORY ENFORCEMENT:**

This skill MUST invoke the `rule-reviewer` skill exactly once for each rule file. The agent executing bulk-rule-reviewer is **FORBIDDEN** from:

❌ **FORBIDDEN ACTIONS (Protocol Violations):**
1. **Reimplementing review logic** - Do NOT recreate rule-reviewer's workflow in Python/bash/any language
2. **Batch optimization** - Do NOT aggregate multiple rules into single review
3. **Parallel shortcuts** - Do NOT run reviews concurrently unless max_parallel explicitly set
4. **Token-saving shortcuts** - Do NOT skip review steps to save tokens
5. **Time-saving shortcuts** - Do NOT abbreviate reviews to save time
6. **Cached/precomputed reviews** - Do NOT generate reviews without invoking rule-reviewer
7. **Summary-only reviews** - Do NOT create lightweight reviews; FULL reviews required

✅ **REQUIRED ACTIONS (Protocol Compliance):**
1. **Invoke rule-reviewer skill** - Exactly once per rule file
2. **Pass all parameters** - target_file, review_date, review_mode, model
3. **Wait for completion** - Do NOT proceed until review file written
4. **Parse output path** - Extract review file path from rule-reviewer response
5. **Validate output** - Confirm review file exists before continuing

**Enforcement Mechanism:**

Each review invocation MUST produce this exact pattern:
```
Use the rule-reviewer skill.

target_file: rules/XXX-YYY.md
review_date: YYYY-MM-DD
review_mode: FULL
model: <model>
```

**Verification:** Each invocation MUST return: `"Review written to: reviews/<filename>.md"`

**Violation Consequences:**
- Invalid reviews rejected from summary
- Execution halted with protocol violation error
- User notified of shortcut attempt

**Why This Matters:**
- rule-reviewer contains domain expertise (scoring rubrics, priority checks, dimension analysis)
- Reimplementation loses review quality and consistency
- Token/time optimization sacrifices accuracy
- Each rule deserves full evaluation per rule-reviewer standards

## Scope

**What This Skill Does:**
- Discovers all rule files in `rules/` directory (113 files expected)
- Invokes `rule-reviewer` skill for each file
- Collects scores, verdicts, and critical issues from all reviews
- Generates master summary report with prioritized improvement recommendations
- Supports filtering, resume capability, and progress tracking

**When to Use This Skill:**
- Periodic quality audits of entire rule repository (quarterly/monthly)
- Pre-release validation before major version releases
- Technical debt tracking and prioritization
- Baseline quality measurement for improvement initiatives

## Input Contract

### Required Parameters

**review_date:**
- Format: YYYY-MM-DD
- Description: Date stamp for review files
- Default: Today's date
- Example: `2026-01-06`

**review_mode:**
- Format: FULL | FOCUSED | STALENESS
- Description: Review depth (passed to rule-reviewer)
- Default: FULL
- Values:
  - FULL: Complete evaluation (all 6 dimensions)
  - FOCUSED: Actionability and completeness only
  - STALENESS: Freshness check only

**model:**
- Format: Lowercase-hyphenated slug
- Description: Model identifier for review execution
- Default: claude-sonnet-45
- Examples: `claude-sonnet-45`, `gpt-4`, `gemini-pro`

### Optional Parameters

**filter_pattern:**
- Format: Glob pattern
- Description: Filter rules by pattern
- Default: `rules/*.md` (all rules)
- Examples:
  - `rules/100-*.md` (Snowflake rules only)
  - `rules/200-*.md` (Python rules only)
  - `rules/*-core.md` (Core rules only)

**skip_existing:**
- Format: Boolean
- Description: Skip files with existing reviews for date
- Default: true
- Usage: Set to false to force re-review

**max_parallel:**
- Format: Integer (1-10)
- Description: Max concurrent reviews
- Default: 1 (sequential)
- Note: Higher values risk context overflow

## Output Contract

### Individual Review Files

**Location:** `reviews/<rule-name>-<model>-<date>.md`
**Count:** One per rule file (up to 113)
**Format:** Standard rule-reviewer output format
**Example:** `reviews/100-snowflake-core-claude-sonnet-45-2026-01-06.md`

### Master Summary Report

**Location:** `reviews/_bulk-review-<model>-<date>.md`
**Format:** Consolidated report with sections:
1. Executive Summary (score distribution, dimension analysis)
2. Priority 1: Urgent (score <60, NOT_EXECUTABLE)
3. Priority 2: High (score 60-79, NEEDS_REFINEMENT)
4. Priority 3: Medium (score 80-89, EXECUTABLE_WITH_REFINEMENTS)
5. Priority 4: Excellent (score 90-100, EXECUTABLE)
6. Failed Reviews (errors during execution)
7. Top 10 Improvement Recommendations (prioritized by impact × effort)
8. Next Steps (immediate, short-term, long-term)
9. Appendix: All Rules by Score (sorted table)

**No-overwrite:** If file exists, increment suffix (`-01.md`, `-02.md`)

### Progress Output

**Format:** Console output during execution
**Content:**
- Current progress: "Reviewing 45/113: rules/200-python-core.md"
- Running totals: Average score, verdict distribution
- Estimated time remaining (based on average review time)
- Error summary (failed reviews logged immediately)

## Execution Workflow

The skill follows a 4-stage workflow (see `workflows/` directory for details):

### Stage 1: Discovery (workflows/01-discovery.md)
- Find all `.md` files in `rules/` directory
- Apply filter_pattern if specified
- Sort alphabetically
- Output: List of rule file paths

### Stage 2: Review Execution (workflows/02-review-execution.md)
- For each rule file:
  - Extract rule name from path
  - Check if review exists (if skip_existing=true)
  - Invoke rule-reviewer skill with parameters
  - Parse output path from response
  - Store (rule_name, score, verdict, review_path) in results list
  - Continue to next file (error handling: log and continue)
- Output: Results list with metadata for all reviews

### Stage 3: Aggregation (workflows/03-aggregation.md)
- For each review file:
  - Read first 100 lines only (context management)
  - Extract: overall score, verdict, critical issues count, dimension scores
  - Build lightweight data structure (no full content)
- Calculate statistics: average, median, distribution
- Output: Summary data structure

### Stage 4: Summary Report (workflows/04-summary-report.md)
- Generate master summary report with prioritized sections
- Sort rules by score within priority tiers
- Calculate impact × effort ratios for recommendations
- Write to `reviews/_bulk-review-<model>-<date>.md`
- Output: File path of master summary

## Workflow References

**Detailed Implementation:**
- `workflows/01-discovery.md` - File discovery logic
- `workflows/02-review-execution.md` - Rule-reviewer orchestration
- `workflows/03-aggregation.md` - Score extraction and statistics
- `workflows/04-summary-report.md` - Master report generation

**Examples:**
- `examples/full-bulk-review.md` - Complete walkthrough

**Validation:**
- `VALIDATION.md` - Input validation rules
- `tests/validation-tests.md` - Test cases

## Critical Design Decisions

### Context Management Strategy

**Problem:** 113 full reviews exceed context token limits

**Solution:** Parse only metadata from review files
- Read first 100 lines of each review only
- Extract: overall score, verdict, critical issues count, dimension scores
- Store in lightweight data structure
- Never load full review content into context
- Full details remain in individual review files

**Trade-off:** Can't provide detailed issue analysis in bulk summary, only scores and counts

### Stateless Execution Model

**Problem:** Reviews may fail mid-batch

**Solution:** Each review is independent
- Review failure doesn't stop batch
- Log errors, continue with next file
- Failed reviews marked in summary with error reason
- Resume capability skips already-completed reviews

**Trade-off:** Must handle partial completion gracefully

### Resume and Idempotency

**Problem:** Bulk review may take hours, can't restart from scratch

**Solution:** Check for existing reviews before invoking
- Default: skip_existing = true
- If review exists for (rule, date, model): Load score from existing file
- If review doesn't exist: Invoke rule-reviewer skill
- User can force re-review with skip_existing = false

**Benefit:** Can resume after interruption without wasted work

## Error Handling

**Review Failure:**
- Continue with next file
- Log error in progress output
- Mark as FAILED in master summary with error reason

**Context Overflow:**
- Switch to minimal output mode
- Report warning to user
- Continue with remaining files

**File Write Failure:**
- Print OUTPUT_FILE directive for manual save
- Continue with execution

**Empty Rules Directory:**
- Report error: "No rule files found in rules/"
- Exit gracefully without creating empty summary

**Partial Completion:**
- Resume capability allows continuation
- Existing reviews are reused (skip_existing=true)

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

### Score Distribution
- Average score across all rules
- Median score
- Distribution by priority tier (Excellent/Good/Needs Work/Poor)

### Dimension Analysis
- Average scores for each dimension: Actionability, Completeness, Consistency, Parsability, Token Efficiency, Staleness

### Critical Issues Summary
- Count of rules with 0, 1-2, 3+ critical issues

### Prioritized Recommendations
- Top 10 rules to improve (sorted by impact × effort ratio)
- Estimated effort for each improvement
- Expected score improvement

### Next Steps
- Immediate actions (this week)
- Short-term goals (this month)
- Long-term strategy (quarterly)

## Maintenance Notes

### Version History
- v1.0.0 (2026-01-06): Initial implementation

### Future Enhancements
- v1.1.0: Trend tracking across multiple review dates (score deltas)
- v1.2.0: CI/CD integration for automated quality gates
- v1.3.0: Parallel execution support (max_parallel > 1)
- v1.4.0: Incremental reviews (only modified rules)

## Installation Requirements

**Dependencies:** [rule-reviewer]

**Skill Location Resolution:**

This skill supports two installation patterns:

1. **Installed Skill (Recommended):**
   - Install `rule-reviewer` via your agent tool's skill management
   - bulk-rule-reviewer will detect and use installed version
   - Example: Cursor/Cline skill installation

2. **Local Skill (Fallback):**
   - Ensure `skills/rule-reviewer/` exists in project
   - bulk-rule-reviewer will execute local skill manually
   - Useful for standalone projects or custom agent setups

**Auto-detection:** The skill automatically detects which pattern is available.

**Error Handling:** If neither is found, execution stops with installation guidance.

## References

### Related Skills
- **rule-reviewer** - Single rule review (required dependency)
- **rule-creator** - Create new rules (complementary)

### Related Rules
- **002f-claude-code-skills.md** - Skill authoring best practices
- **002-rule-governance.md** - Rule schema and standards
- **000-global-core.md** - Foundation patterns

## Appendix: Input Validation

See `VALIDATION.md` for complete validation rules. Key checks:

- `review_date` must match YYYY-MM-DD format
- `review_mode` must be FULL | FOCUSED | STALENESS
- `model` must be lowercase-hyphenated (no spaces, underscores)
- `filter_pattern` must be valid glob pattern
- `rules/` directory must exist and be readable
- `skip_existing` must be boolean (if provided)
- `max_parallel` must be 1-10 (if provided)
