# Skill Timer — Changelog

All notable changes to the `skill-timer` skill. Current version is tracked in `SKILL.md` frontmatter.

## v2.0.0 (2026-06-21) — Robustness redesign, skill rename, audit remediation

This release combines the 2026-05-14 skill rename (`skill-timing` → `skill-timer`), the v2.0.0 robustness redesign, and the 2026-06-21 audit remediation. The rename was authored on this branch but never released, so its breaking changes ship as part of v2.0.0.

### Breaking changes (rename)

- Renamed skill from `skill-timing` to `skill-timer` to align with the `<noun>-<agent-noun>` naming convention used across this skill collection. Any caller pinning `name: skill-timing` must update to `name: skill-timer`.
- Python module renamed `skill_timing.py` → `skill_timer.py`.
- Package name changed `skill-timing` → `skill-timer` in `pyproject.toml`.
- Runtime data file prefix changed `skill-timing-*.json` → `skill-timer-*.json`. Existing local `skill-timing-*.json` files are intentionally invisible to the renamed code.

### Breaking changes (robustness redesign)

- New exit code `4` (`EXIT_INSTRUMENTATION_FAILED`) emitted when the v2.0.0 distribution validator escalates status to `instrumentation_failed` (any error-severity alert OR ≥3 warning-severity alerts) or per-row schema rejection occurs (`dimension_invalid`).
- Status enum extended from 4 to 6 values: adds `dimension_invalid` and `instrumentation_failed`.
- Mode enum extended from 7 to 10 values: adds `wrap`, `unavailable`, `not-requested`.
- Per-dimension array is **stripped** to `dimension_timings_rejected` when status escalates to `instrumentation_failed`. Callers that previously read `dimension_timings` unconditionally will see an empty array; check `status` first.
- `scripts/validate_timing.py` (repo root) **moved** to `skills/skill-timer/scripts/validate_timing.py` and reimplemented as a thin wrapper around `skill_timer.py replay`. The original CLI (`python validate_timing.py [--fixture <path>] [files…]`) is preserved on the new path. The repo-root file is deleted.

### Added

- `skill_timer.py wrap --run-id <id> --dimension <name> --evidence <path|->` — atomic per-dimension capture; server-side end timestamp; `--evidence` ≥100 bytes (configurable).
- `skill_timer.py finalize --run-id <id> --stage {pre_write|post_write} [--review-artifact <path>]` — replaces caller-defined `review_complete` semantics.
- `skill_timer.py replay --fixture <path>` — re-run distribution validator against a completed JSON; useful for CI gates and post-hoc audit.
- Distribution validator with 11 alerts:

  | Alert id | Severity |
  |---|---|
  | `dim_uniformity_suspect` | warning |
  | `dim_floor_violation` | warning |
  | `dim_coverage_low` | warning |
  | `dim_coverage_severe` | error |
  | `dim_coverage_overrun` | error |
  | `dim_total_short` | warning |
  | `checkpoint_burst` | warning |
  | `post_review_gap` | warning |
  | `clock_skew` | warning |
  | `missing_expected_dimension` | warning |
  | `duplicate_dim_checkpoints` | warning |

- Per-row `validation_status` annotation on every `dimension_timings` entry: `valid | warning | failed | not_requested | unavailable`.
- Run-level `work_window_seconds` and `work_window_source` (denominator for coverage / post-review-gap math) computed via fallback hierarchy: `work_started→work_complete > skill_loaded→finalize.pre_write > skill_loaded→review_complete > start→finalize.pre_write > start→review_complete > start→end`.
- Per-skill expected-dimension map for plan-reviewer (8 dims), rule-reviewer (6 dims), doc-reviewer (6 dims).
- Environment overrides: `TIMING_TEST_MODE=1` (bypasses floor / coverage / total-short / post-review-gap / uniformity validators; other validators stay live) and `TIMING_DISABLE_DISTRIBUTION_VALIDATOR=1` (fully disables the v2.0.0 distribution validator; soft rollback to v1.5.0 behavior).
- `workflows/validation-checkpoints.md` — extracted mandatory validation gates from SKILL.md (audit finding ST-4).
- `workflows/advanced-operations.md` — extracted baseline, analyze, wrap, finalize, replay commands from SKILL.md (audit finding ST-4).

### Changed

- `cmd_start` captures `start_monotonic = time.monotonic()` alongside wall-clock `start_epoch`.
- `cmd_checkpoint` records `elapsed_seconds_raw` (full-precision monotonic delta) and `epoch` (wall-clock) in addition to the existing rounded `elapsed_seconds`.
- `cmd_end` computes `duration_seconds_monotonic` and emits `clock_source: "monotonic" | "wall"`. `duration_seconds` is monotonic when both endpoints recorded in the same process.
- Distribution-validator thresholds and per-skill floors configurable via `reviews/.timing-thresholds.json`.
- Renamed `## Core Operations` heading to `## Workflow` (canonical per [ADR 0007](../../docs/adr/0007-skill-style-guide.md)). Audit finding ST-1.
- Reordered sections so `## Purpose` precedes `## Quick Start` (canonical order). Audit finding ST-2.
- Description rewritten to include explicit trigger phrases per 002h §5.

### Removed

- Deleted inline `## v2.0.0 robustness redesign` block from SKILL.md (51 lines). Same content remains in this CHANGELOG entry. Audit finding ST-3.

### Migration notes

- **No new runtime third-party dependencies.** Pure stdlib at runtime; pytest/ruff/ty remain dev-only.
- **Legacy `dim_*` checkpoint pattern still works.** It now emits a deprecation WARNING when `--auto-dimension-timings` is set without `wrap` entries.
- **`review_complete` checkpoint still parsed** (silent fallback) but emits deprecation WARNING when no `finalize` stages observed.
- **Schema `$id`** bumped from `timing-output.schema.json` to `timing-output.schema.json#v2.0.0`. Existing v1.5.0 fixtures validate against the new schema as a subset (additive change).
- **Baseline purge:** if you have stale baselines from before v2.0.0 (which may have absorbed sub-second poisoned dimension durations), purge with `python skill_timer.py baseline set --skill <name> --mode <mode> --model <model> --days 7` (re-derives from a recent window only). Auto-purge is intentionally not provided; user controls when.
- **Caller integration (Gate 8):** plan-reviewer / rule-reviewer / doc-reviewer / bulk-rule-reviewer SKILL.md files have been updated to refuse to publish the "Per-Dimension Timing" markdown table when `status ∈ {dimension_invalid, instrumentation_failed}`. A banner pointing to the completed JSON is emitted instead.

### Known anti-patterns (Run f92f9d72f408a356)

The reference failure case is preserved at `tests/fixtures/run_f92f9d72f408a356.json`:

- 8 per-dimension durations of 1.08–1.12s (sum ≈ 8.78s)
- Wall-clock total = 246.08s; review_complete checkpoint at 67.25s
- ~178.83s elapsed *after* `review_complete` (file write / synthesis), invisible to the per-dimension table
- Coverage ratio = 47% against `skill_loaded_to_review_complete` window, but `post_review_gap` = 73% > 30% limit
- Pre-v2.0.0: `alerts: []`, `status: completed`, table published.
- Post-v2.0.0 replay: `status: instrumentation_failed`, exit 4, table replaced with banner.

### Notes

- SKILL.md body reduced from 450 lines to ≤300 (target met per audit finding ST-4).
- No external callers referenced `## Core Operations` by name (verified via repo grep); rename is safe.

## v1.5.0 (2026-04-21) — Per-dimension timing enforcement

- New `--auto-dimension-timings` flag on `end`: derives `dimension_timings` from `dim_<name>_start` / `dim_<name>_end` checkpoint pairs.
- New `PER_DIMENSION_STATUS={present|derived|missing}` stdout marker (grep-able from orchestrators).
- Silent-omission guard: stderr WARNING when `dim_*` checkpoints exist but neither `--dimension-timings` nor `--auto-dimension-timings` is supplied.
- `mode: "checkpoint"` added as a first-class value in the `dimension_timings` schema.
- Paired pytest regression suite in `tests/test_per_dimension_timing.py`.
- **Migration note:** [`plans/per-dimension-timing-enforcement-MIGRATION.md`](../../plans/per-dimension-timing-enforcement-MIGRATION.md)
