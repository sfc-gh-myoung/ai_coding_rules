# Plan Reviewer — Changelog

All notable changes to the `plan-reviewer` skill. Current version is tracked in `SKILL.md` frontmatter.

## v2.5.1 (2026-06-21) — Audit remediation

Per [skills audit 2026-06-21](../../docs/audits/skills-audit-2026-06-21.md) findings PR-1, PR-2, plus Audit P3 follow-up and Gate 8 integration:

### Changed

- Reordered sections so `## Purpose` and `## Use this skill when` precede `## Quick Start` (canonical order per [ADR 0007](../../docs/adr/0007-skill-style-guide.md)). Finding PR-1.
- Expanded frontmatter description (174c → ~370c): added "Do not use for" clause cross-referencing plan-creator and execute-plan; rewrote trigger phrases in the `Triggers on "phrase1", "phrase2"` shape. Finding PR-2.
- docs: add `## Outputs` section per 002h required-sections contract. Consolidates the previously inline path (`reviews/plan-reviews/<plan-name>-<model>-<date>.md`) into a canonical Outputs block after `## Inputs`, including mode-specific path table and no-overwrite behavior. Audit P3 follow-up.
- Added **Gate 8** to SKILL.md: when `skill_timer.py end` returns `status ∈ {dimension_invalid, instrumentation_failed}`, refuse to publish the Per-Dimension Timing markdown table. Replace with a banner pointing at the rejected JSON in `reviews/.timing-data/`. No code changes in this skill; the gate is enforced at the markdown-emit step. See `skills/skill-timer/CHANGELOG.md` v2.0.0 for the underlying mechanism (new exit code 4, status enum extensions, distribution validator).

## v2.5.0 (2026-04-21) — Per-dimension timing as the universal default

- `timing_enabled` default flipped from `false` to `true`; Gate 7 is now unconditional. Explicit `timing_enabled: false` opt-out satisfied by single `not-requested` row.
- `workflows/parameter-collection.md` still prompts explicitly — no silent auto-apply.
- Byte cap raised 12000 → 13500 where present.
- Template in `rubrics/SCORING.md` "Required when timing_enabled: true" text updated to "Required unless `timing_enabled: false`".

## v2.4.0 (2026-04-21) — Per-dimension timing capture

Introduced per-dimension timing capture with Quick Reference, Step 4a enforcement, Gate 7 verification, anti-pattern block, and parallel sub-agent schema alignment. Depends on skill-timing v1.5.0.

## v2.3.0 — Parallel execution default, parameter collection mandates
