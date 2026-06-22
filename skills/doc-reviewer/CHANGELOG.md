# Doc Reviewer — Changelog

All notable changes to the `doc-reviewer` skill. Current version is tracked in `SKILL.md` frontmatter.

## v2.3.0 (2026-06-21) — Audit remediation (progressive disclosure)

Per [skills audit 2026-06-21](../../docs/audits/skills-audit-2026-06-21.md) findings DR-1, DR-2:

### Added

- `references/verdict-thresholds.md` — extracted score-range table and critical-dimension overrides. Finding DR-1.
- `references/performance.md` — extracted parallel-vs-sequential performance comparison table. Finding DR-1.
- `references/gate-8.md` — extracted Gate 8 verbatim contract (mirrored across reviewer skills per [ADR 0007](../../docs/adr/0007-skill-style-guide.md)). Finding DR-2.

### Changed

- SKILL.md body trimmed from 347 to ≤315 lines via progressive-disclosure extraction; cross-references replace full content.
- Added **Gate 8** to SKILL.md: when `skill_timer.py end` returns `status ∈ {dimension_invalid, instrumentation_failed}`, refuse to publish the Per-Dimension Timing markdown table. Replace with a banner pointing at the rejected JSON in `reviews/.timing-data/`. No code changes in this skill; the gate is enforced at the markdown-emit step. See `skills/skill-timer/CHANGELOG.md` v2.0.0 for the underlying mechanism (new exit code 4, status enum extensions, distribution validator).

## v2.2.0 (2026-04-21) — Per-dimension timing as a first-class workflow step

- New Step 4a mandates `dim_<name>_start` / `dim_<name>_end` checkpoint pairs around every scored dimension (accuracy, completeness, clarity, structure, staleness, consistency).
- Quick Reference expanded with all 6 dimension pairs and `--auto-dimension-timings` invocation.
- Anti-Pattern block covers fabricated epochs, missing schema fields, ignored `VALIDATION ERROR`, and silent `--dimension-timings` / `--auto-dimension-timings` omission.
- New `workflows/review-verification.md` defines Quality Gate 7 which rejects reviews missing `### Per-Dimension Timing` when `timing_enabled: true` (single `unavailable` row with reason is acceptable).
- New `references/REVIEW-OUTPUT-TEMPLATE.md` authoritative skeleton with 6-row Per-Dimension Timing table.
- Parallel mode contract: sub-agents self-report `{dimension, duration_seconds, mode, start_epoch, end_epoch}`; coordinator assembles `--dimension-timings` JSON (no `--auto-dimension-timings`).
- Depends on skill-timing v1.5.0+.

## v2.1.0 — 6-dimension rubric, parallel execution default
