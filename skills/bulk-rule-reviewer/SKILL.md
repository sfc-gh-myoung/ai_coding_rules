---
name: bulk-rule-reviewer
description: Execute agent-centric reviews on all rules in rules/ directory and generate prioritized improvement report
version: 2.4.0
---

# Bulk Rule Reviewer

## Purpose

Execute comprehensive agent-centric reviews on all rule files in `rules/` directory, then generate consolidated priority report. Designed for periodic quality audits, pre-release validation, and technical debt tracking.

## Use this skill when

- Periodic quality audits (quarterly/monthly)
- Pre-release validation before major version releases
- Technical debt tracking and prioritization
- Baseline quality measurement for improvement initiatives

## Inputs

**Required:**
- **review_date**: `YYYY-MM-DD` (default: today)
- **review_mode**: `FULL` | `FOCUSED` | `STALENESS` (default: FULL)
- **model**: Lowercase-hyphenated slug (default: `claude-sonnet-45`)

**Optional:**
- **filter_pattern**: Glob pattern (default: `rules/*.md`)
  - Examples: `rules/100-*.md` (Snowflake only), `rules/*-core.md` (cores only)
- **skip_existing**: Boolean (default: true) - Resume capability
- **overwrite**: Boolean (default: false) - If true, overwrite existing review files. If false, use sequential numbering (-01, -02, etc.) for conflicts
- **max_parallel**: Integer 1-10 (default: 5) - Concurrent sub-agent workers. Set to 1 for sequential execution (legacy behavior)
- **output_root**: Root directory for output files (default: `reviews/`). Subdirectories `rule-reviews/` and `summaries/` appended automatically. Supports relative paths including `../`.
- **timing_enabled**: `true` | `false` (default: `true` — v2.4.0 universal default; set `false` to opt out; per-rule reviews use `not-requested` row)

## Outputs

**Individual reviews:** `{output_root}/rule-reviews/<rule-name>-<model>-<date>.md` (up to 187 files)

**Master summary:** `{output_root}/summaries/_bulk-review-<model>-<date>.md` with sections:

(Default `output_root: reviews/`. With `output_root: mytest/` → `mytest/rule-reviews/...` and `mytest/summaries/...`)
1. Executive Summary (score distribution, dimension analysis)
2. Priority 1: Urgent (score <50, NOT_EXECUTABLE)
3. Priority 2: High (score 50-74, NEEDS_REFINEMENT)
4. Priority 3: Medium (score 75-89, EXECUTABLE_WITH_REFINEMENTS)
5. Priority 4: Excellent (score 90-100, EXECUTABLE)
6. Failed Reviews (execution errors)
7. Top 10 Recommendations (impact × effort prioritization)
8. Next Steps (immediate/short-term/long-term)
9. Appendix: All Rules by Score (sorted table)

## Critical Execution Protocol

This skill prioritizes ACCURACY over efficiency. The full anti-optimization protocol, shortcut detection, evidence requirements, and self-correction procedure are mandatory reading **before each run**:

- **See:** `workflows/anti-optimization.md` — Foundational principle, forbidden thoughts, One Rule At A Time rule, canary checks, shortcut detection, self-correction protocol, verification requirements, evidence rules.

### Must-Remember Rules (Context Anchor)

Keep these in active context throughout execution — NEVER summarize away:

1. **One rule at a time.** Never batch. Read one file, score it, write it, move on.
2. **Read the actual rule file** before scoring. Reviews without `read_file()` fail verification.
3. **Load rubrics** from `../rule-reviewer/rubrics/*.md` for each dimension before scoring.
4. **Run schema validation** (`ai-rules validate`) per rule; include output.
5. **Evidence minimums:** ≥15 line references, ≥3 direct quotes, review size 3000–8000 bytes.
6. **Progress output format:** `[N/<total>] Complete: {filename} → {score}/100` after each review.
7. **Skills ≠ Rules.** Token efficiency does not apply to skill execution.
8. **No mid-stream questions.** Once user types ACT, do not ask about time/scope/tradeoffs.

**Drift prevention:** Re-read `../rule-reviewer/examples/TEMPLATE.md` every 5 rules. If any review <2500 bytes OR format deviates, re-read TEMPLATE.md and SKILL.md, then regenerate.

**See also:**
- `workflows/context-anchor.md` — Context preservation + inter-rule gate
- `workflows/proactive-canary.md` — Pre/Post/Mid canary questions
- `workflows/per-rule-verification.md` — Evidence gate + reset trigger
- `workflows/inter-rule-gate.md` — Every-5-rules structural re-anchor
- `workflows/reset-trigger.md` — What to do when verification fails

### How Skills Work Together

Skills cannot invoke other skills programmatically. Skills are documentation that guides agent behavior.

Correct pattern:
1. Load `skills/rule-reviewer/SKILL.md` to understand the review workflow
2. Load `skills/rule-reviewer/rubrics/*.md` as needed for each dimension
3. Execute the review workflow for each rule file
4. Write review to `reviews/rule-reviews/` following rule-reviewer's output format
5. Continue to next rule

## Workflow

### Parameter Collection

Collect ALL parameters (required AND optional) using `ask_user_question` tool.

**See:** `workflows/parameter-collection.md`

**MANDATORY:** Prompt for ALL parameters in batched questions (max 4 per call):
- Do NOT silently apply defaults for optional parameters
- User must explicitly confirm each setting
- If `ask_user_question` unavailable, fall back to text-based prompting

### Timing Start (Required when `timing_enabled: true`; skip when `false`)

**When:** Only if `timing_enabled: true` in inputs
**MODE:** Safe in PLAN mode

**See:** `../skill-timing/workflows/timing-start.md` and `workflows/timing-integration.md` for the canonical copy-paste Quick Reference block and anti-pattern guide.

**Action:** Capture `run_id` in working memory as `BULK_RUN_ID` for later use.

**Note:** Timing tracks the entire bulk review process (all stages) AND per-rule durations via `rule_{slug}_start/end` checkpoint pairs. Each rule-reviewer invocation also captures its OWN per-dimension timings under its own child run_id — these are embedded in each review's `## Timing Metadata` section and aggregated by `workflows/aggregation.md`.

### Checkpoint: skill_loaded (when `timing_enabled: true`)

Emit `skill_loaded` on `$BULK_RUN_ID`. See `workflows/timing-integration.md`.

### Stage 1: Discovery

Find all `.md` files in `rules/` directory, apply `filter_pattern`, sort alphabetically.

**See:** `workflows/discovery.md`

### Checkpoint: discovery_complete (when `timing_enabled: true`)

Emit `discovery_complete` on `$BULK_RUN_ID`.

### Stage 2: Review Execution (Parallel or Sequential)

Execution mode depends on `max_parallel` parameter.

#### Parallel Execution (default: max_parallel ≥ 2)

When `max_parallel >= 2`, use parallel sub-agents:

1. Partition rules into N groups (N = max_parallel)
2. Launch N sub-agents in background, each assigned a group
3. Each sub-agent loads rule-reviewer skill and processes its rules independently
4. Monitor progress via `agent_output` polling
5. Aggregate results when all sub-agents complete

Benefits: ~5× speedup, fresh context per sub-agent (eliminates drift), isolated failures.

**See:** `workflows/parallel-execution.md` and `workflows/subagent-prompt-template.md`.

File writes: All sub-agents write directly to `{output_root}/rule-reviews/`. No conflicts because each sub-agent reviews different rules (unique filenames).

#### Sequential Execution (max_parallel = 1)

Use for debugging, very small rule sets (<10 rules), or explicit user preference.

#### Per-Rule Steps

For each rule file:

1. **INTER-RULE GATE (every 5 rules):** If `rule_number % 5 == 0`, execute `workflows/inter-rule-gate.md`.
2. **PRE-RULE CANARY:** Execute 3 canary questions from `workflows/proactive-canary.md`.
3. Extract rule name from path; compute `RULE_SLUG=$(basename "$rule_file" .md)`.
4. Check if review exists (if `skip_existing=true`).
4a. If `timing_enabled: true`: emit `rule_${RULE_SLUG}_start` checkpoint on `$BULK_RUN_ID` BEFORE step 5.
5. **READ the actual rule file** into working memory.
6. **POST-READ CANARY:** Verify you can name 3 specific things unique to THIS rule.
7. Load `rule-reviewer/SKILL.md` if not already loaded.
8. Load relevant rubrics for dimensions being scored.
9. Run `ai-rules validate` on the rule file.
10. Perform Agent Execution Test (count blocking issues).
11. **MID-REVIEW CANARY (after dimension 3):** Check rubric loading and reference reuse.
12. Score each dimension per rubric, citing line numbers and quotes.
13. Generate specific recommendations with line numbers.
14. **VERIFY review authenticity** (`workflows/per-rule-verification.md`):
    - ≥15 line references
    - ≥3 direct quotes from rule
    - Rule-specific findings
    - **FAILURE triggers `workflows/reset-trigger.md`**
15. Write complete review to `{output_root}/rule-reviews/` (respects `overwrite`).
15a. If `timing_enabled: true`: emit `rule_${RULE_SLUG}_end` checkpoint on `$BULK_RUN_ID`. Missing end-checkpoints drop the rule from the auto-derived Timing Breakdown.
16. Store (rule_name, score, verdict, review_path).
17. Show progress every 10 reviews.

**CRITICAL:** Step 5 MUST happen BEFORE steps 10–13. Reviews without reading the file fail verification at step 14.

**DRIFT PREVENTION:** Steps 1, 2, 6, 11 are canary/gate checks that detect optimization drift BEFORE it produces compromised output. These are NOT optional.

**See:** `workflows/review-execution.md` for orchestration details, resume capability, error handling.

### Checkpoint: reviews_complete (when `timing_enabled: true`)

Emit `reviews_complete` on `$BULK_RUN_ID`.

### Stage 3: Aggregation

For each review file:

1. Read first 150 lines only (context management)
2. Extract: overall score, verdict, critical issues, dimension scores
3. Build lightweight data structure (no full content)
4. Calculate statistics: average, median, distribution

**See:** `workflows/aggregation.md` for parsing strategy and statistics.

### Checkpoint: aggregation_complete (when `timing_enabled: true`)

Emit `aggregation_complete` on `$BULK_RUN_ID`.

### Stage 4: Summary Report

Generate master summary with:
- Prioritized sections (Priority 1–4)
- Rules sorted by score within tiers
- Impact × effort ratios for recommendations
- Write to `{output_root}/summaries/_bulk-review-<model>-<date>.md`

**See:** `workflows/summary-report.md` for report format and section generation.

### Checkpoint: summary_complete (when `timing_enabled: true`)

Emit `summary_complete` on `$BULK_RUN_ID`.

### Timing End — Compute (when `timing_enabled: true`)

**MODE:** Safe in PLAN mode (outputs to STDOUT only)

**See:** `../skill-timing/workflows/timing-end.md` (Step 1) and `workflows/timing-integration.md`.

**Action:** Invoke `skill_timing.py end --auto-dimension-timings`. Capture STDOUT for metadata embedding. Check `PER_DIMENSION_STATUS=` marker — `missing` triggers warnings aggregated into the summary Timing Breakdown.

### [MODE TRANSITION: PLAN → ACT]

Request user ACT authorization before file modifications.

### Timing End — Embed (when `timing_enabled: true`)

**MODE:** Requires ACT mode (appends metadata to file)

**See:** `../skill-timing/workflows/timing-end.md` (Step 2) and `workflows/timing-integration.md`.

**Action:** Parse STDOUT, append timing metadata section + **Timing Breakdown** section (see `workflows/summary-report.md`) to the master summary report file.

## Critical Design Decisions

**Context Management:** Parse only first 150 lines of each review (scores/verdicts only). Full details remain in individual files.

**Stateless Execution:** Review failures don't stop batch. Resume via `skip_existing` parameter.

**See:** `workflows/aggregation.md` for complete strategy.

## Error Handling

- **Review failure:** Continue with next file, log error, mark FAILED in summary.
- **Context overflow:** Switch to minimal output mode, report warning, continue.
- **File write failure:** Print `OUTPUT_FILE` directive for manual save, continue.
- **Empty rules directory:** Report error, exit gracefully without empty summary.
- **Partial completion:** Resume capability allows continuation using existing reviews.

## Usage Examples

See `examples/usage-examples.md` for all invocation recipes (basic, filtered, overwrite, sequential numbering, staleness-only).

## Success Criteria

- All matching rules reviewed (or filtered subset)
- Individual review files written to `reviews/rule-reviews/`
- Master summary report generated with valid path
- Prioritized improvement list included
- No context overflow during execution
- Resume capability functional (existing reviews skipped)
- Error handling graceful (failed reviews don't stop batch)

## Expected Outcomes

- **Score distribution:** Average, median, distribution by priority tier.
- **Dimension analysis:** Average scores for all 6 dimensions.
- **Critical issues summary:** Count of rules with 0, 1–2, 3+ critical issues.
- **Prioritized recommendations:** Top 10 rules to improve (impact × effort), estimated effort, expected score improvement.
- **Next steps:** Immediate actions, short-term goals, long-term strategy.

## Version History

See `CHANGELOG.md`.

## Installation Requirements

**Dependency:** rule-reviewer skill v2.9.0+ (required — per-dimension Gate 7 universal-default timing)
**Dependency:** skill-timing v1.5.0+ (required when `timing_enabled: true` — `--auto-dimension-timings` flag, `PER_DIMENSION_STATUS` marker)

Skill location resolution supports two patterns:

1. **Installed Skill (Recommended):** Install `rule-reviewer` via agent tool's skill management
2. **Local Skill (Fallback):** Ensure `skills/rule-reviewer/` exists in project

Auto-detection selects the available pattern. If neither found, execution stops with installation guidance.

## Validation

**See:** `workflows/input-validation.md` for validation workflow and code patterns.

**Key Requirements:**
- `review_date`: YYYY-MM-DD format (valid calendar date)
- `review_mode`: FULL | FOCUSED | STALENESS (uppercase)
- `model`: lowercase-hyphenated (e.g., claude-sonnet-45)
- `filter_pattern`: rules/*.md glob (optional, must match ≥1 file)
- `skip_existing`: boolean true/false (optional, default: true)
- `max_parallel`: integer 1-10 (optional, default: 1)
- Environment: `rules/` exists and readable, `reviews/rule-reviews/` and `reviews/summaries/` writable

**Execution:** Validate inputs before Stage 1 (Discovery). Fail fast on errors.

## Examples

- `examples/full-bulk-review.md` - Complete walkthrough example
- `examples/usage-examples.md` - Invocation recipes

## Related Skills

- **rule-reviewer** — Single rule review (required dependency)
- **rule-creator** — Create new rules (complementary)
- **skill-timing** — Timing instrumentation (required when `timing_enabled: true`)

## References

### Rules

- `rules/002h-claude-code-skills.md` — Skill authoring best practices
- `rules/002-rule-governance.md` — Rule schema and standards
- `rules/000-global-core.md` — Foundation patterns
