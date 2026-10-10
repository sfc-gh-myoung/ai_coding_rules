---
name: rule-reviewer
description: Execute agent-centric rule reviews (FULL/FOCUSED/STALENESS modes) using 6-dimension rubric and write results to reviews/rule-reviews/ with no-overwrite safety. Use when reviewing rule files, auditing rule quality, checking rule staleness, validating rule compliance, or analyzing agent executability.
version: 3.1.0
---

# Rule Reviewer

## Purpose

Execute comprehensive agent-centric reviews evaluating whether autonomous agents can execute rules without judgment calls.

For v4 rules, read the active schema and governance contract before applying the rubrics. Required H2 order is Scope, Contract, References, with four non-empty Contract subsections. Do not penalize omitted optional sections, fixed step/example counts, or a missing duplicate checklist. Structural checks and semantic review remain separate.

## Use this skill when

- Reviewing rule files for agent executability (FULL mode)
- Auditing a specific dimension of a rule (FOCUSED mode)
- Checking rule staleness against the current codebase (STALENESS mode)
- Validating rule compliance with schema and conventions
- Scoring rule quality against the 6-dimension rubric

## Quick Start

```
Use the rule-reviewer skill.

target_file: rules/200-python-core.md
review_date: 2026-01-06
review_mode: FULL
model: claude-sonnet-4-6
```

Output: `reviews/rule-reviews/200-python-core-claude-sonnet-4-6-2026-01-06.json` (canonical)
        `reviews/rule-reviews/200-python-core-claude-sonnet-4-6-2026-01-06.md`  (derived)

(With `output_root: mytest/` → `mytest/rule-reviews/200-python-core-claude-sonnet-4-6-2026-01-06.{json,md}`)

## Scoring System (100 points)

6 scored dimensions, 100 points total. Hard caps apply for size (> 300 lines / > 350 lines) and blocking issues (≥ 6 / ≥ 10).

**Quick reference:**

| Dimension | Weight | Max |
|---|---|---|
| Actionability | 3.0 | 30 |
| Rule Size | 2.5 | 25 |
| Parsability | 1.5 | 15 |
| Completeness | 1.5 | 15 |
| Consistency | 1.0 | 10 |
| Cross-Agent Consistency | 0.5 | 5 |

Full scoring formula, hard-cap thresholds, per-dimension rubric file references, and example calculations: [`rubrics/scoring.md`](rubrics/scoring.md).

## Review Modes

- **FULL:** All 6 scored dimensions (100 points max)
- **FOCUSED:** Actionability + Completeness only (45 points max)
- **STALENESS:** Informational staleness check (not scored)

## Execution Discipline

**FOUNDATIONAL PRINCIPLE:** This skill prioritizes ACCURACY over efficiency. Proceed with the full process; do not propose streamlined alternatives or estimate completion time.

Full discipline contract (forbidden behaviors, required behaviors, self-correction triggers, pre-execution commitment): [`workflows/execution-discipline.md`](workflows/execution-discipline.md).

## Workflow

**Execution Mode Selection:**
```
IF execution_mode == "parallel":
    → Follow workflows/parallel-execution.md (5 sub-agents)
ELSE:
    → Follow sequential workflow below
```

**Progress Display:** Show only `Starting: [rule-name]` and `Complete: [rule-name] → score/100`. All canary checks, dimension scoring, and evidence gathering are INTERNAL (silent).

1. **Validate inputs**: date format YYYY-MM-DD, file exists, mode in {FULL, FOCUSED, STALENESS}. See `workflows/input-validation.md`.

1a. **Collect ALL parameters** (use `ask_user_question`). Question sets: `workflows/parameter-collection.md`. Shared collection rules (batched max-4, no silent defaults, text fallback): [`../shared/reviewer-contract.md`](../shared/reviewer-contract.md#parameter-collection).

1b. **Detect file type.** Run the `target_basename` / `FILE_TYPE` / `SKIP_SCHEMA` detection from `workflows/input-validation.md` (File-Type Detection section). Outcomes: `rule` → full schema validation; `project` (PROJECT.md) → schema validation skipped.

2. **Pre-Review Canary Check (SILENT).** See Canary Checks below.

3. **Run schema validation (conditional).** If `FILE_TYPE == "rule"`, execute `uv run ai-rules validate <target_file>` and parse CRITICAL/HIGH/MEDIUM errors. If `FILE_TYPE == "project"`, skip and set `schema_validation_result = "SKIPPED (project file)"`. Full procedure, file-type gating, and error handling: `workflows/schema-validation.md`.

4. **Agent Execution Test (SILENT - results go to review file).** Count blocking issues (≥6 caps score at 80/100, ≥10 forces NOT_EXECUTABLE):
   - Undefined criteria where a decision affects correctness or safety; use specification values or labeled project policy, not invented thresholds
   - Missing conditional outcomes where the alternative affects correctness or safety; harmless no-ops need no fabricated branch
   - Ambiguous actions (multiple interpretations)
   - Formatting that loses a required relationship or violates an applicable rule policy; characters alone do not prove a model limitation

5. **Post-Read Canary Check (SILENT).** See Canary Checks below.

6. **Score dimensions.** Read rubrics as needed for each dimension:
   - `rubrics/actionability.md`
   - `rubrics/completeness.md`
   - `rubrics/consistency.md`
   - `rubrics/parsability.md`
   - `rubrics/token-efficiency.md`
   - `rubrics/rule-size.md` (100% deterministic - line count)
   - `rubrics/staleness.md`
   - `rubrics/cross-agent-consistency.md` - includes documentation currency check via `web_fetch`; see `workflows/doc-currency-check.md`

6a. **(When `timing_enabled: true`: default) Bracket EACH dimension with a checkpoint pair.**

   Required checkpoint names (one pair per scored dimension):
   - `dim_actionability_start` / `dim_actionability_end`
   - `dim_rule_size_start` / `dim_rule_size_end`
   - `dim_parsability_start` / `dim_parsability_end`
   - `dim_completeness_start` / `dim_completeness_end`
   - `dim_consistency_start` / `dim_consistency_end`
   - `dim_cross_agent_start` / `dim_cross_agent_end`

   Timing mechanism (`--auto-dimension-timings`, marker validation, anti-patterns): [`../shared/reviewer-contract.md`](../shared/reviewer-contract.md#timing-integration-skill-timer).

   **FAILURE TO DO THIS:** The `### Per-Dimension Timing` subsection will be absent and the review will fail post-write Quality Gate 7 (see `workflows/review-verification.md`). Requires skill-timer v2.0.0+.

7. **Mid-Review Canary (after dimension 3) (SILENT).** See Canary Checks below.

8. **Generate recommendations**: specific line numbers, quantified fixes, expected score improvements.

9. **Validate canonical JSON.** Before writing, assemble the `rule-review-result/v1` JSON and run `ai-rules review-artifact validate --input <review.json>`. Verify the review contains ≥15 line references (FULL mode), direct quotes with line numbers, and rule-specific findings (not generic). See `workflows/review-verification.md`. **FAILURE → Trigger reset: Re-read SKILL.md completely.**

   Schema authority: `schemas/rule-review-result-v1.schema.json`. Canonical format spec: `skills/rule-reviewer/references/reviewer-defaults.yml`. Retry contract: `references/retry-contract.md`.

10. **Publish review pair.** Write the canonical JSON first: `{output_root}/rule-reviews/[rule-name]-[model]-[date].json`. Then render Markdown deterministically: `ai-rules review-artifact render --input <review.json> --output <review.md>`. Verify the pair: `ai-rules review-artifact verify-pair --input <review.json> --markdown <review.md>`. Auto-increment suffix on conflict (when `overwrite=false`). See `workflows/file-write.md`.

   **Markdown is derived output.** Never write Markdown directly as a final review artifact; the canonical JSON is the sole semantic authority. Authority model: [`../../docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md) §3.6.

**See `workflows/error-handling.md` for detailed error handling across all steps.**

### Canary Checks (SILENT: never output)

All three canaries are internal self-tests. If any fails, re-read the referenced file and resume silently.

- **Pre-Review (before reading target):** "What will I find?" → "I don't know yet." "How long?" → "However long it takes." "Can I reuse previous work?" → "No, different rule." Wrong answer → re-read Execution Discipline.
- **Post-Read (after reading, before scoring):** Can name 3 specific things unique to THIS file; can cite a specific line number with content; know the exact `TokenBudget` value (rule files) OR file purpose (project files). Unable to verify → re-read the target file.
- **Mid-Review (after dimension 3):** Loaded the rubric for EACH dimension scored? First 3 dimensions have distinct line references? If NO on either → go back and gather evidence.

## Verdicts

**Score ranges & verdict labels** (90-100 EXECUTABLE … <60 NOT_EXECUTABLE): single source of truth is [`references/reviewer-defaults.yml`](references/reviewer-defaults.yml) (`verdicts:` block).

**Critical dimension override:** If both Actionability ≤4/10 AND Completeness ≤4/10 → NOT_EXECUTABLE regardless of total score.

**Rule Size flags** (`SPLIT_RECOMMENDED`, `SPLIT_REQUIRED`, `NOT_DEPLOYABLE`, `BLOCKED`) start above the 250-line limit. Line bands and agent actions: [`rubrics/rule-size.md`](rubrics/rule-size.md#score-decision-matrix).

**Hard caps:** See Scoring System above (single source of truth).

## Supported File Types

Rule files (`rules/*.md`) and Project files (`PROJECT.md`). File-type detection logic, per-type schema behavior, and a comparison of how each type is scored: [`workflows/input-validation.md`](workflows/input-validation.md).

## Required Review Sections

10 required H2 sections, in order: File Header (H1 + 5 metadata fields), Executive Summary, Schema Validation Results, Agent Executability Verdict, Dimension Analysis (6 subsections for FULL), Critical Issues, Recommendations (with inline Staleness), Post-Review Checklist (11 fixed items), Conclusion, Timing Metadata (conditional). Authoritative JSON schema: `schemas/rule-review-result-v1.schema.json`. Rendered layout: `references/rendered-review-format.md`. Full checklist: [`workflows/review-verification.md`](workflows/review-verification.md).

## Inputs

- **target_file:** Path to file (e.g., `rules/200-python-core.md`, `PROJECT.md`)
- **review_date:** ISO 8601 format (YYYY-MM-DD)
- **review_mode:** FULL | FOCUSED | STALENESS
- **model:** Lowercase-hyphenated slug (e.g., `claude-sonnet-4-6`)
- **output_root:** (optional) Root directory for output files (default: `reviews/`). Subdirectory `rule-reviews/` is appended automatically. Supports relative paths including `../`.
- **overwrite:** (optional) true | false (default: false): If true, overwrite existing review file. If false, use sequential numbering (-01, -02, etc.)
- **timing_enabled:** (optional) true | false (default: true). Opt-out semantics: [`../shared/reviewer-contract.md`](../shared/reviewer-contract.md#timing-opt-out-reviewers-only).
- **execution_mode:** (optional) `parallel` | `sequential` (default: `parallel`)
  - `parallel`: Uses 5 sub-agents for scored dimension evaluation (faster, recommended for 8GB+ RAM)
  - `sequential`: Legacy single-agent behavior (for debugging or low-resource environments)

## Outputs

Write to: `{output_root}/rule-reviews/[rule-name]-[model]-[date].json` (canonical). Markdown rendered as same-stem `.md` via `ai-rules review-artifact render` immediately after. (Default `output_root` is `reviews/`.)

**No overwrites:** If file exists and `overwrite: false` (default), append `-01.json`, `-02.json`, etc. Set `overwrite: true` to replace. See **No-Overwrite Safety** section below.

**Format:** Canonical review artifacts are `rule-review-result/v1` JSON. Schema: `schemas/rule-review-result-v1.schema.json`. Defaults (dimensions, weights, hard caps, verdicts): `references/reviewer-defaults.yml`. Rendered Markdown layout: `references/rendered-review-format.md`. Retry behavior: `references/retry-contract.md`.

## Integration with Other Skills

### With bulk-rule-reviewer

bulk-rule-reviewer invokes this skill once per rule file. **Never** implement review logic yourself when bulk-rule-reviewer calls you. Context-preservation safeguards (pre-write verification, post-write size check, periodic refresh): `workflows/bulk-coordination.md`.

### With skill-timer

**Execute IF:** `timing_enabled: true` (default).
**Skip IF:** `timing_enabled: false` (explicit opt-out): satisfy Gate 7 with a single `not-requested` row (see [`../shared/reviewer-contract.md`](../shared/reviewer-contract.md#timing-opt-out-reviewers-only)).

When enabled, emit `skill_loaded` + the 6 dimension checkpoint pairs (`dim_<name>_start/end`) around each scored dimension. Shared mechanism (commands, marker validation, working-memory contract, anti-patterns): [`../shared/reviewer-contract.md`](../shared/reviewer-contract.md#timing-integration-skill-timer). Rule-reviewer specifics: [`workflows/timing-integration.md`](workflows/timing-integration.md).

## Error Handling

Continue the review when the schema validator reports CRITICAL/HIGH findings (report them). On a failed write, print `OUTPUT_FILE: [path]` and the full review for manual save. Full cases (validator failure, missing file, write failure, documentation currency failure): [`workflows/error-handling.md`](workflows/error-handling.md#quick-reference).

## No-Overwrite Safety

When `overwrite: false` (default): auto-increment suffix (`-01.md`, `-02.md`, …, max `-99.md`). When `overwrite: true`: replace existing file. Max-versions error and full algorithm: [`workflows/file-write.md`](workflows/file-write.md).

## Validation Checklists

Pre/during/post execution checks: [`workflows/validation-checklists.md`](workflows/validation-checklists.md). Quick reminder: every review must verify schema validation, Agent Execution Test completion, all dimensions scored, recommendations include line numbers, and final review file ≥ 2500 bytes.

## Expected Review Size

Typical FULL mode review: 3000–8000 bytes. Detailed size validation thresholds: [`workflows/validation-checklists.md`](workflows/validation-checklists.md).

## Gate 8: Per-Dimension Timing rejection (skill-timer v2.0.0+)

When `skill_timer.py end` returns `status ∈ {dimension_invalid, instrumentation_failed}`: do not publish the Per-Dimension Timing table; emit a banner pointing at the rejected JSON instead. Full verbatim contract (mirrored across reviewer skills): [`references/gate-8.md`](references/gate-8.md).

## Examples

Complete review samples in `examples/`: `full-review.md`, `focused-review.md`, `staleness-review.md`, `project-file-review.md`, `edge-cases.md`. Authoritative JSON schema: `schemas/rule-review-result-v1.schema.json`. Markdown layout: `references/rendered-review-format.md`.

## Related Skills

- **bulk-rule-reviewer:** Batch review orchestrator (uses this skill)
- **rule-creator:** Rule authoring (validated with this skill)
- **skill-timer:** Execution time measurement (optional integration)

## Determinism Requirements

Goal: reduce score variance from ±5–8 points to < ±2 points across runs. Full contract (mandatory/prohibited behaviors, variance tolerance, self-verification checklist): `workflows/determinism.md`.

## Version History

See `CHANGELOG.md`.
