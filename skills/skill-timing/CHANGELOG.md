# Skill Timing — Changelog

All notable changes to the `skill-timing` skill. Current version is tracked in `SKILL.md` frontmatter.

## v1.5.0 (2026-04-21) — Per-dimension timing enforcement

- New `--auto-dimension-timings` flag on `end`: derives `dimension_timings` from `dim_<name>_start` / `dim_<name>_end` checkpoint pairs.
- New `PER_DIMENSION_STATUS={present|derived|missing}` stdout marker (grep-able from orchestrators).
- Silent-omission guard: stderr WARNING when `dim_*` checkpoints exist but neither `--dimension-timings` nor `--auto-dimension-timings` is supplied.
- `mode: "checkpoint"` added as a first-class value in the `dimension_timings` schema.
- Paired pytest regression suite in `tests/test_per_dimension_timing.py`.
- **Migration note:** [`plans/per-dimension-timing-enforcement-MIGRATION.md`](../../plans/per-dimension-timing-enforcement-MIGRATION.md)
