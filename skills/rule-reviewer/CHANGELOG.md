# Rule Reviewer — Changelog

All notable changes to the `rule-reviewer` skill. Current version is tracked in `SKILL.md` frontmatter.

## v2.10.0 (2026-06-21) — Audit remediation (progressive disclosure)

Per [skills audit 2026-06-21](../../docs/audits/skills-audit-2026-06-21.md) findings RR-1 through RR-6, plus Audit P3 follow-up and Gate 8 integration:

### Added

- `rubrics/scoring.md` — extracted scoring system (formula, weights, hard caps, example calculation). Finding RR-2.
- `workflows/execution-discipline.md` — extracted forbidden/required behaviors, self-correction triggers, pre-execution commitment. Finding RR-3.
- `workflows/validation-checklists.md` — extracted pre/during/post checks plus expected review size validation. Finding RR-4.
- `references/gate-8.md` — extracted Gate 8 verbatim contract (mirrored across reviewer skills per [ADR 0007](../../docs/adr/0007-skill-style-guide.md)). Cross-cutting finding C-GATE8.

### Changed

- SKILL.md body trimmed from 407 to ≤310 lines via progressive-disclosure extraction; cross-references replace full content. Finding RR-1.
- Quick reference scoring table retained inline in SKILL.md for at-a-glance lookup; full table and example calculation live in `rubrics/scoring.md`.
- docs: add `## Outputs` section per 002h required-sections contract. Consolidates the existing file-write path (`{output_root}/rule-reviews/[rule-name]-[model]-[date].md`) and no-overwrite behavior into a canonical Outputs block after `## Inputs`. Audit P3 follow-up.
- Added **Gate 8** to SKILL.md: when `skill_timer.py end` returns `status ∈ {dimension_invalid, instrumentation_failed}`, refuse to publish the Per-Dimension Timing markdown table. Replace with a banner pointing at the rejected JSON in `reviews/.timing-data/`. No code changes in this skill; the gate is enforced at the markdown-emit step. See `skills/skill-timer/CHANGELOG.md` v2.0.0 for the underlying mechanism (new exit code 4, status enum extensions, distribution validator).

## v2.9.0 (2026-04-21) — Per-dimension timing is the universal default

- `timing_enabled` default flipped from `false` to `true` across all invocation paths.
- Gate 7 (in `workflows/review-verification.md`) is now unconditional when `timing_enabled: true`; an explicit `timing_enabled: false` opt-out is satisfied by a single `not-requested` row.
- `parameter-collection.md` still prompts the user — no silent auto-apply.
- Byte cap raised 12000 → 13500 to accommodate the mandatory Per-Dimension Timing subsection in FULL-mode reviews.
- Output template (`references/REVIEW-OUTPUT-TEMPLATE.md`) "Conditional" labels removed; Per-Dimension Timing is required unless caller passes `timing_enabled: false`.
- Depends on skill-timing v1.5.0+.

## v2.8.0 (2026-04-21) — Per-dimension timing elevated to first-class workflow step

- New Step 6a mandates `dim_<name>_start` / `dim_<name>_end` checkpoint pairs around every scored dimension.
- Quick Reference expanded with all 6 dimension pairs and `--auto-dimension-timings` invocation.
- Anti-Pattern 4 covers silent `--dimension-timings` / `--auto-dimension-timings` omission.
- Quality Gate 7 (in `workflows/review-verification.md`) rejects reviews missing `### Per-Dimension Timing` when `timing_enabled: true`.
- Clarified misleading "skill-timing handles all capture" sentence — rule-reviewer owns capture.
- **Depends on skill-timing v1.5.0+** (`--auto-dimension-timings`, `PER_DIMENSION_STATUS` marker).
- **Migration note:** [`plans/per-dimension-timing-enforcement-MIGRATION.md`](../../plans/per-dimension-timing-enforcement-MIGRATION.md)

## v2.7.2 (2026-04-11) — dimension_timings anti-patterns and schema reference

- 3 anti-pattern pairs (fabricated timestamps, missing required fields, ignoring validation errors).
- Cross-reference to skill-timing SKILL.md dimension_timings schema.

## v2.7.1 (2026-03-27) — Standardized review output template

Created `references/REVIEW-OUTPUT-TEMPLATE.md` as authoritative fill-in skeleton (opus-4-6 structure). Integrated template loading into review-execution and file-write workflows. Fixed 11-item Post-Review Checklist. Standardized Executive Summary table columns (Raw (0-10) | Weight | Points | Max). Inline Token Efficiency and Staleness. Added structural validation gate (Step 5a) in `file-write.md`. Added template compliance check in `review-verification.md`. Removed `examples/TEMPLATE.md` (superseded). Aligned weight notation to decimal across all files. Added Per-Dimension Timing subsection to `REVIEW-OUTPUT-TEMPLATE.md` (was missing from v2.6.0 template integration).

## v2.6.0 (2026-03-27) — Per-dimension timing support

Sequential mode uses checkpoint pairs (`dim_{name}_start`/`dim_{name}_end`); parallel mode uses sub-agent self-reported `start_epoch`/`end_epoch`. New `--dimension-timings` flag on timing-end, `--per-dimension` on analyze/baseline. Requires skill-timing v1.4.0.

## v2.5.3 (2026-03-25) — Cross-model consistency improvements

Added Non-Issues Patterns 9-10 (tool names, checklists), domain applicability adjustment for completeness edge cases, expanded cross-agent "Do NOT Count" list, added overlap resolution for tool names, new calibration examples file.

## v2.5.2 (2026-03-24) — Fixed agent determinism regressions from v2.5.1 optimization

- Inlined shared preamble into all 5 scored rubrics (eliminates cross-reference dependency for sub-agents).
- Fixed Rule Size scoring table in parallel-execution.md (was using 6-tier simplified table instead of canonical 7-tier).
- Restructured staleness deprecated tools from ambiguous inline `|` format to proper tables.
- Each scored rubric is now fully self-contained for sub-agent consumption.

## v2.5.1 — Optimization pass

Compressed anti-optimization protocol, archived informational rubrics, deduplicated scoring matrices, extracted shared boilerplate, streamlined parameter collection and parallel execution.

## v2.5.0 — Parallel execution

Added parallel execution mode with 5 sub-agents for scored dimension evaluation.

## v2.4.0 — Documentation currency check

Added documentation currency check to staleness dimension.

## v2.0.0 — Progressive disclosure

Removed PROMPT.md, added progressive disclosure with `rubrics/`.

## v1.4.0 — Timing & schema integration

Added timing integration, schema validation.

## v1.3.0 — FOCUSED and STALENESS modes

## v1.2.0 — Agent Execution Test

## v1.1.0 — No-overwrite safety

## v1.0.0 — Initial release
