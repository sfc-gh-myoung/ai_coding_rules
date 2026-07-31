---
name: rule-reviewer
description: Execute agent-centric rule reviews (FULL/FOCUSED/STALENESS modes) using 6-dimension rubric and write results to reviews/rule-reviews/ with no-overwrite safety. Use when reviewing rule files, auditing rule quality, checking rule staleness, validating rule compliance, or analyzing agent executability.
version: 2.10.0
---

# Rule Reviewer

## Purpose

Execute comprehensive agent-centric reviews evaluating whether autonomous agents can execute rules without judgment calls.

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

Output: `reviews/rule-reviews/200-python-core-claude-sonnet-4-6-2026-01-06.md`

(With `output_root: mytest/` → `mytest/rule-reviews/200-python-core-claude-sonnet-4-6-2026-01-06.md`)

## Scoring System (100 points)

6 scored dimensions, 100 points total. Hard caps apply for size (> 600 lines / > 700 lines) and blocking issues (≥ 6 / ≥ 10).

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

1. **Validate inputs** — date format YYYY-MM-DD, file exists, mode in {FULL, FOCUSED, STALENESS}. See `workflows/input-validation.md`.

1a. **Collect ALL parameters** (use `ask_user_question`). See `workflows/parameter-collection.md`. **MANDATORY:** batched questions (max 4 per call); do NOT silently apply defaults. If `ask_user_question` unavailable, fall back to text-based prompting.

1b. **Detect file type.** Run the `target_basename` / `FILE_TYPE` / `SKIP_SCHEMA` detection from `workflows/input-validation.md` (File-Type Detection section). Outcomes: `rule` → full schema validation; `project` (PROJECT.md) → schema validation skipped.

2. **Pre-Review Canary Check (SILENT).** See Canary Checks below.

3. **Run schema validation (conditional).** If `FILE_TYPE == "rule"`, execute `uv run ai-rules validate <target_file>` and parse CRITICAL/HIGH/MEDIUM errors. If `FILE_TYPE == "project"`, skip and set `schema_validation_result = "SKIPPED (project file)"`. Full procedure, file-type gating, and error handling: `workflows/schema-validation.md`.

4. **Agent Execution Test (SILENT - results go to review file).** Count blocking issues (≥6 caps score at 80/100, ≥10 forces NOT_EXECUTABLE):
   - Undefined thresholds ("large", "significant", "appropriate")
   - Missing conditional branches (no explicit else)
   - Ambiguous actions (multiple interpretations)
   - Visual formatting (ASCII art, arrows, diagrams)

5. **Post-Read Canary Check (SILENT).** See Canary Checks below.

6. **Score dimensions.** Read rubrics as needed for each dimension:
   - `rubrics/actionability.md`
   - `rubrics/completeness.md`
   - `rubrics/consistency.md`
   - `rubrics/parsability.md`
   - `rubrics/token-efficiency.md`
   - `rubrics/rule-size.md` (100% deterministic - line count)
   - `rubrics/staleness.md`
   - `rubrics/cross-agent-consistency.md` — includes documentation currency check via `web_fetch`; see `workflows/doc-currency-check.md`

6a. **(When `timing_enabled: true` — default) Bracket EACH dimension with a checkpoint pair.**

   Required checkpoint names (one pair per scored dimension):
   - `dim_actionability_start` / `dim_actionability_end`
   - `dim_rule_size_start` / `dim_rule_size_end`
   - `dim_parsability_start` / `dim_parsability_end`
   - `dim_completeness_start` / `dim_completeness_end`
   - `dim_consistency_start` / `dim_consistency_end`
   - `dim_cross_agent_start` / `dim_cross_agent_end`

   On `timing-end`, pass `--auto-dimension-timings` (**preferred**) to derive the `dimension_timings` array from the captured checkpoint pairs automatically. Only assemble `--dimension-timings` JSON manually if you are aggregating sub-agent output (parallel mode).

   **FAILURE TO DO THIS:** The `### Per-Dimension Timing` subsection will be absent and the review will fail post-write Quality Gate 7 (see `workflows/review-verification.md`). Requires skill-timer v1.5.0+.

7. **Mid-Review Canary (after dimension 3) (SILENT).** See Canary Checks below.

8. **Generate recommendations** — specific line numbers, quantified fixes, expected score improvements.

9. **Verify review authenticity.** Before writing, verify review contains ≥15 line references (FULL mode), direct quotes with line numbers, rule-specific findings (not generic); output matches `references/REVIEW-OUTPUT-TEMPLATE.md` structure. See `workflows/review-verification.md`. **FAILURE → Trigger reset: Re-read SKILL.md completely.**

10. **Write review.** Path: `{output_root}/rule-reviews/[rule-name]-[model]-[date].md`. Auto-increment `-01.md`, `-02.md` if exists (when `overwrite=false`). See `workflows/file-write.md`.

**See `workflows/error-handling.md` for detailed error handling across all steps.**

### Canary Checks (SILENT — never output)

All three canaries are internal self-tests. If any fails, re-read the referenced file and resume silently.

- **Pre-Review (before reading target):** "What will I find?" → "I don't know yet." "How long?" → "However long it takes." "Can I reuse previous work?" → "No, different rule." Wrong answer → re-read Execution Discipline.
- **Post-Read (after reading, before scoring):** Can name 3 specific things unique to THIS file; can cite a specific line number with content; know the exact `TokenBudget` value (rule files) OR file purpose (project files). Unable to verify → re-read the target file.
- **Mid-Review (after dimension 3):** Loaded the rubric for EACH dimension scored? First 3 dimensions have distinct line references? If NO on either → go back and gather evidence.

## Verdicts

**Score Ranges (100-point scale):**
- **90-100** — EXECUTABLE — Production-ready
- **75-89** — EXECUTABLE_WITH_REFINEMENTS — Good, minor fixes
- **50-74** — NEEDS_REFINEMENT — Needs work
- **<50** — NOT_EXECUTABLE — Major issues

**Critical dimension override:** If both Actionability ≤4/10 AND Completeness ≤4/10 → NOT_EXECUTABLE regardless of total score.

**Rule Size flags:**
- `SPLIT_RECOMMENDED` (501-550 lines) — Review for split opportunities
- `SPLIT_REQUIRED` (551-600 lines) — Mandatory split plan required
- `NOT_DEPLOYABLE` (601-700 lines) — Block deployment, hard cap 70/100
- `BLOCKED` (>700 lines) — Reject review, hard cap 50/100

**Hard caps:** See Scoring System above (single source of truth).

## Supported File Types

**Rule Files (rules/*.md):**
- Domain-specific patterns and guidelines
- Loaded on-demand by agents
- Full schema validation against `schemas/rule-schema.yml`
- All 6 dimensions scored (100 points max)
- TokenBudget variance check applies

**Project Files (PROJECT.md):**
- Bootstrap and configuration documents
- Loaded once during project initialization
- Schema validation skipped (different structure than rules)
- All 6 dimensions scored (100 points max)
- TokenBudget variance skipped (no declared budget)
- Still evaluated for actionability, completeness, consistency, markdown quality, and currency

**Key Differences:**

| Aspect | Rule Files | Project Files |
|--------|------------|---------------|
| Schema validation | Full check | Skipped |
| Parsability scoring | Schema + markdown | Markdown only |
| Token efficiency | Budget variance + redundancy | Redundancy + structure only |
| Metadata required | 7 fields (SchemaVersion, etc.) | None |
| Section structure | Scope → Contract → Content | Custom per project |
| Max score | 100 points | 100 points |

**Both file types are agent-executable documents** — they just follow different schemas optimized for their architectural roles.

## Required Sections in Review

1. File Header (H1 + 5 metadata fields)
2. Executive Summary (score table + verdict block)
3. Schema Validation Results
4. Agent Executability Verdict
5. Dimension Analysis (6 subsections for FULL mode)
6. Critical Issues
7. Recommendations (with inline Staleness)
8. Post-Review Checklist (11 fixed items)
9. Conclusion
10. Timing Metadata (conditional)

**Authoritative template:** `references/REVIEW-OUTPUT-TEMPLATE.md`

## Inputs

- **target_file:** Path to file (e.g., `rules/200-python-core.md`, `PROJECT.md`)
- **review_date:** ISO 8601 format (YYYY-MM-DD)
- **review_mode:** FULL | FOCUSED | STALENESS
- **model:** Lowercase-hyphenated slug (e.g., `claude-sonnet-4-6`)
- **output_root:** (optional) Root directory for output files (default: `reviews/`). Subdirectory `rule-reviews/` is appended automatically. Supports relative paths including `../`.
- **overwrite:** (optional) true | false (default: false) — If true, overwrite existing review file. If false, use sequential numbering (-01, -02, etc.)
- **timing_enabled:** (optional) true | false (default: true) — set to `false` to explicitly opt out; the Per-Dimension Timing section is then satisfied by a single `not-requested` row.
- **execution_mode:** (optional) `parallel` | `sequential` (default: `parallel`)
  - `parallel`: Uses 5 sub-agents for scored dimension evaluation (faster, recommended for 8GB+ RAM)
  - `sequential`: Legacy single-agent behavior (for debugging or low-resource environments)

## Outputs

Write to: `{output_root}/rule-reviews/[rule-name]-[model]-[date].md` (default `output_root` is `reviews/`).

**No overwrites:** If file exists and `overwrite: false` (default), append `-01.md`, `-02.md`, etc. Set `overwrite: true` to replace. See **No-Overwrite Safety** section below for full behavior.

**Format:** Reviews follow the structure defined in `references/REVIEW-OUTPUT-TEMPLATE.md`. See **Required Sections in Review** above for the section checklist.

## Integration with Other Skills

### With bulk-rule-reviewer

bulk-rule-reviewer invokes this skill once per rule file. **Never** implement review logic yourself when bulk-rule-reviewer calls you. Context-preservation safeguards (pre-write verification, post-write size check, periodic refresh): `workflows/bulk-coordination.md`.

### With skill-timer

**Execute IF:** `timing_enabled: true` (default).
**Skip IF:** `timing_enabled: false` (explicit opt-out) — satisfy Gate 7 with a single `not-requested` row.

When enabled, execute ALL steps below (not optional once enabled):

| When | Action | Command | Track |
|------|--------|---------|-------|
| Before review | Start timing | `$PYTHON skill_timer.py start --skill rule-reviewer --target {{target_file}} --model {{model}} --mode {{review_mode}}` | Store `_timing_run_id` |
| After schema validation | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name skill_loaded` | - |
| Before EACH dimension | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name dim_{name}_start` | - |
| After EACH dimension | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name dim_{name}_end` | - |
| After scoring complete | Checkpoint | `$PYTHON skill_timer.py checkpoint --run-id {{_timing_run_id}} --name review_complete` | - |
| Before file write | End timing | `$PYTHON skill_timer.py end --run-id {{_timing_run_id}} --output-file {{output_file}} --skill rule-reviewer --format markdown --auto-dimension-timings` | Store `_timing_stdout` |
| After file write | Embed | Append `_timing_stdout` to output file | - |

**Working memory contract:** Retain `_timing_run_id`, `_timing_stdout`, and `_dimension_timings` from start through embed.

**Per-dimension timing responsibility:** skill-timer **validates and formats** the timing data you pass in. **You are responsible for capturing** start/end markers (checkpoint pairs in sequential mode, or sub-agent self-reports in parallel mode) around each dimension. Use `--auto-dimension-timings` in sequential mode (preferred).

**Copy-paste bash quick reference, 4 common anti-patterns, and per-command validation procedure:** `workflows/timing-integration.md`.

**Schema + epoch capture reference:** `../skill-timer/SKILL.md`.

## Error Handling

**Schema validator fails:**
- Continue review
- Note validation unavailable in Parsability section
- Recommend manual schema check

**Rule file not found:**
- Report: "File not found: [path]"
- Verify path and try again

**Review write fails:**
- Print: `OUTPUT_FILE: [path]`
- Print full review content
- User must save manually

**Documentation currency check fails:**
- If `web_fetch` unavailable: skip currency check, note in review
- If >50% links timeout: skip penalty, note "Currency check incomplete"
- If all links fail: note "Unable to verify documentation currency - manual review recommended"
- Continue with remaining staleness scoring (LastUpdated, deprecated tools, patterns, link status)

**See:** `workflows/error-handling.md`

## No-Overwrite Safety

**When `overwrite: false` (default):**

If `{output_root}/rule-reviews/[rule-name]-[model]-[date].md` exists:
- Try `-01.md`
- Try `-02.md`
- Increment until available (max: `-99.md`)
- If `-99.md` exists: STOP, report error `Maximum review versions exceeded for [rule-name]`

**When `overwrite: true`:**

The existing file at `{output_root}/rule-reviews/[rule-name]-[model]-[date].md` will be replaced. Use this when intentionally re-running a review to replace a previous version.

## Validation Checklists

Pre/during/post execution checks: [`workflows/validation-checklists.md`](workflows/validation-checklists.md). Quick reminder — every review must verify schema validation, Agent Execution Test completion, all dimensions scored, recommendations include line numbers, and final review file ≥ 2500 bytes.

## Expected Review Size

Typical FULL mode review: 3000–8000 bytes. Detailed size validation thresholds: [`workflows/validation-checklists.md`](workflows/validation-checklists.md).

## Gate 8 — Per-Dimension Timing rejection (skill-timer v2.0.0+)

When `skill_timer.py end` returns `status ∈ {dimension_invalid, instrumentation_failed}`: do not publish the Per-Dimension Timing table; emit a banner pointing at the rejected JSON instead. Full verbatim contract (mirrored across reviewer skills): [`references/gate-8.md`](references/gate-8.md).

## Examples

Complete review samples in `examples/`: `full-review.md`, `focused-review.md`, `staleness-review.md`, `project-file-review.md`, `edge-cases.md`. Authoritative fill-in skeleton: `references/REVIEW-OUTPUT-TEMPLATE.md`.

## Related Skills

- **bulk-rule-reviewer:** Batch review orchestrator (uses this skill)
- **rule-creator:** Rule authoring (validated with this skill)
- **skill-timer:** Execution time measurement (optional integration)

## Determinism Requirements

Goal: reduce score variance from ±5–8 points to < ±2 points across runs. Full contract (mandatory/prohibited behaviors, variance tolerance, self-verification checklist): `workflows/determinism.md`.

## Version History

See `CHANGELOG.md`.
