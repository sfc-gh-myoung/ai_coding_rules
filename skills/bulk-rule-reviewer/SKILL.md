---
name: bulk-rule-reviewer
description: Reviews every rule file under rules/ using the rule-reviewer 6-dimension rubric, aggregates per-file scores into a single weighted backlog, and emits a prioritized improvement report. Use for periodic rule-system audits, before major rule-set releases, or to surface drift across the catalog. Triggers on "audit all rules", "bulk rule review", "rule system audit", "review rules directory", "score every rule".
version: 2.6.1
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
- **model**: Lowercase-hyphenated slug (default: `claude-sonnet-4-6`)

**Optional:**
- **filter_pattern**: Glob pattern (default: `rules/*.md`)
  - Examples: `rules/100-*.md` (Snowflake only), `rules/*-core.md` (cores only)
- **skip_existing**: Boolean (default: true) - Resume capability
- **overwrite**: Boolean (default: false) - If true, overwrite existing review files. If false, use sequential numbering (-01, -02, etc.) for conflicts. Algorithm: [`../rule-reviewer/workflows/file-write.md`](../rule-reviewer/workflows/file-write.md)
- **max_parallel**: Integer 1-10 (default: 5) - Concurrent sub-agent workers. Set to 1 for sequential execution (legacy behavior)
- **output_root**: Root directory for output files (default: `reviews/`). Subdirectories `rule-reviews/` and `summaries/` appended automatically. Supports relative paths including `../`.
- **timing_enabled**: `true` | `false` (default: `true`). Opt-out semantics: [`../shared/reviewer-contract.md`](../shared/reviewer-contract.md#timing-opt-out-reviewers-only)

## Outputs

**Individual reviews:** `{output_root}/rule-reviews/<rule-name>-<model>-<date>.json` (canonical) + `.md` (derived via `ai-rules review-artifact render`). Orphan Markdown files (`.md` without same-stem `.json`) are diagnostic artifacts, not accepted reviews.

**Master summary:** `{output_root}/summaries/_bulk-review-<model>-<date>.md` with sections:

(Default `output_root: reviews/`. With `output_root: mytest/` → `mytest/rule-reviews/...` and `mytest/summaries/...`)
1. Executive Summary (score distribution, dimension analysis)
2. Priority 1: Urgent (score <60, NOT_EXECUTABLE)
3. Priority 2: High (score 60-79, NEEDS_REFINEMENT)
4. Priority 3: Medium (score 80-89, EXECUTABLE_WITH_REFINEMENTS)
5. Priority 4: Excellent (score 90-100, EXECUTABLE)
6. Failed Reviews (execution errors)
7. Top 10 Recommendations (impact × effort prioritization)
8. Next Steps (immediate/short-term/long-term)
9. Appendix: All Rules by Score (sorted table)

> Band boundaries (score <60 / 60-79 / 80-89 / 90-100) are defined by [`../rule-reviewer/references/reviewer-defaults.yml`](../rule-reviewer/references/reviewer-defaults.yml) (`verdicts:` block); the tiers above are this skill's report layout over those bands.

## Execution Protocol

Before each run, read `workflows/anti-optimization.md`. It is the authoritative
contract for one-rule-at-a-time processing, source reading, rubric loading,
schema validation, evidence minimums, progress reporting, and drift recovery.

Use the supporting workflows when their condition applies:

- `workflows/context-anchor.md` and `workflows/inter-rule-gate.md` for periodic re-anchoring.
- `workflows/proactive-canary.md` and `workflows/per-rule-verification.md` for evidence gates.
- `workflows/reset-trigger.md` when a verification gate fails.

Skills document agent behavior; they do not invoke one another. For each rule,
load `skills/rule-reviewer/SKILL.md` and only the rubrics required for the
selected review mode before writing the review.

## Workflow

### Parameter Collection

Collect ALL parameters (required AND optional) using `ask_user_question` tool.

**See:** `workflows/parameter-collection.md` for this skill's question sets. Shared collection rules (batched max-4, no silent defaults, text fallback): [`../shared/reviewer-contract.md`](../shared/reviewer-contract.md#parameter-collection).

### Timing Start (when `timing_enabled: true`)

**MODE:** PLAN safe. Start the timer and capture `run_id` as `BULK_RUN_ID`. Shared skill-timer mechanism (commands, marker validation, working-memory contract, anti-patterns): [`../shared/reviewer-contract.md`](../shared/reviewer-contract.md#timing-integration-skill-timer). Bulk Quick Reference + per-rule specifics: `workflows/timing-integration.md`. Per-rule durations use `rule_{slug}_start/end` pairs; child run_ids capture per-dimension timings, aggregated by `workflows/aggregation.md`.

### Timing Checkpoints (when `timing_enabled: true`)

Emit each checkpoint on `$BULK_RUN_ID` at the indicated stage boundary. See `workflows/timing-integration.md`.

| Stage boundary | Checkpoint name |
|----------------|-----------------|
| After skill loaded | `skill_loaded` |
| After Stage 1 | `discovery_complete` |
| After Stage 2 | `reviews_complete` |
| After Stage 3 | `aggregation_complete` |
| After Stage 4 | `summary_complete` |

### Stage 1: Discovery

Find all `.md` files in `rules/` directory, apply `filter_pattern`, sort alphabetically.

**See:** `workflows/discovery.md`

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

Execute `workflows/review-execution.md` for each selected rule. The workflow
owns canaries, timing checkpoints, schema validation, rubric scoring, evidence
verification, output naming, resume behavior, and progress reporting. Read the
target rule before assessing it; a review without direct source evidence fails.

### Stage 3: Aggregation

Discover all `.json` review artifacts in `{output_root}/rule-reviews/`. Ignore any `.md` file that has no same-stem `.json` sibling (orphan diagnostic — report count but do not include in statistics).

Use `ai-rules review-artifact aggregate` to summarize the discovered JSON artifacts:

```
uv run ai-rules review-artifact aggregate --input <review1.json> --input <review2.json> ...
```

Extract from each canonical JSON: `score`, `verdict`, `blocking_issue_count`, `rule_name`, `dimensions[]`. Build the priority tiers and statistics from the structured data. Never parse Markdown for scores (JSON-is-authority: [`../../docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) §3.6).

**See:** `workflows/aggregation.md` for parallel-mode merge and statistics.

### Stage 4: Summary Report

Generate master summary with:
- Prioritized sections (Priority 1–4)
- Rules sorted by score within tiers
- Impact × effort ratios for recommendations
- Write to `{output_root}/summaries/_bulk-review-<model>-<date>.md`

**See:** `workflows/summary-report.md` for report format and section generation.

### Timing End (when `timing_enabled: true`)

**Compute (PLAN safe):** `skill_timer.py end --auto-dimension-timings`. Capture STDOUT. Check `PER_DIMENSION_STATUS=` marker; `missing` triggers warnings in the Timing Breakdown. See `workflows/timing-integration.md`.

### [MODE TRANSITION: PLAN → ACT]

Request user ACT authorization before file modifications.

**Embed (ACT):** Append timing metadata + Timing Breakdown to the master summary file. See `workflows/summary-report.md`.

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

All matching rules reviewed; individual review files in `{output_root}/rule-reviews/`; master summary with score distribution, dimension analysis, top-10 recommendations, and next steps. Resume and error handling functional.

**Full walkthrough:** `examples/full-bulk-review.md`

## Version History

See `CHANGELOG.md`.

## Dependencies

- rule-reviewer skill v2.12.0+
- skill-timer v2.0.0+ (when `timing_enabled: true`)

Requires `skills/rule-reviewer/` in project or installed via agent skill management.

## Validation

**See:** `workflows/input-validation.md` for validation workflow, code patterns, and environment requirements.

Validate all inputs before Stage 1. Fail fast on errors.

## Gate 8: Per-Dimension Timing rejection (skill-timer v2.0.0+)

Full verbatim contract (mirrored across reviewer skills): [`../rule-reviewer/references/gate-8.md`](../rule-reviewer/references/gate-8.md).

## Examples

- `examples/full-bulk-review.md` - Complete walkthrough example
- `examples/usage-examples.md` - Invocation recipes

## Related Skills

- **rule-reviewer**: Single rule review (required dependency)
- **rule-creator**: Create new rules (complementary)
- **skill-timer**: Timing instrumentation (required when `timing_enabled: true`)
