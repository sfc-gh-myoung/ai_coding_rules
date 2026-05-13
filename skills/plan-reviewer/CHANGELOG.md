# Plan Reviewer — Changelog

All notable changes to the `plan-reviewer` skill. Current version is tracked in `SKILL.md` frontmatter.

## v2.5.0 (2026-04-21) — Per-dimension timing as the universal default

- `timing_enabled` default flipped from `false` to `true`; Gate 7 is now unconditional. Explicit `timing_enabled: false` opt-out satisfied by single `not-requested` row.
- `workflows/parameter-collection.md` still prompts explicitly — no silent auto-apply.
- Byte cap raised 12000 → 13500 where present.
- Template in `rubrics/SCORING.md` "Required when timing_enabled: true" text updated to "Required unless `timing_enabled: false`".

## v2.4.0 (2026-04-21) — Per-dimension timing capture

Introduced per-dimension timing capture with Quick Reference, Step 4a enforcement, Gate 7 verification, anti-pattern block, and parallel sub-agent schema alignment. Depends on skill-timing v1.5.0.

## v2.3.0 — Parallel execution default, parameter collection mandates
