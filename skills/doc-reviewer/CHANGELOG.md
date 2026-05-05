# Doc Reviewer — Changelog

All notable changes to the `doc-reviewer` skill. Current version is tracked in `SKILL.md` frontmatter.

## v2.2.0 (2026-04-21) — Per-dimension timing as a first-class workflow step

- New Step 4a mandates `dim_<name>_start` / `dim_<name>_end` checkpoint pairs around every scored dimension (accuracy, completeness, clarity, structure, staleness, consistency).
- Quick Reference expanded with all 6 dimension pairs and `--auto-dimension-timings` invocation.
- Anti-Pattern block covers fabricated epochs, missing schema fields, ignored `VALIDATION ERROR`, and silent `--dimension-timings` / `--auto-dimension-timings` omission.
- New `workflows/review-verification.md` defines Quality Gate 7 which rejects reviews missing `### Per-Dimension Timing` when `timing_enabled: true` (single `unavailable` row with reason is acceptable).
- New `references/REVIEW-OUTPUT-TEMPLATE.md` authoritative skeleton with 6-row Per-Dimension Timing table.
- Parallel mode contract: sub-agents self-report `{dimension, duration_seconds, mode, start_epoch, end_epoch}`; coordinator assembles `--dimension-timings` JSON (no `--auto-dimension-timings`).
- Depends on skill-timing v1.5.0+.

## v2.1.0 — 6-dimension rubric, parallel execution default
