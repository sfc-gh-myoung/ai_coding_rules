# Bulk Rule Reviewer — Changelog

All notable changes to the `bulk-rule-reviewer` skill. Current version is tracked in `SKILL.md` frontmatter.

## v2.4.0 (2026-04-21) — Per-rule and per-dimension timing as the universal default

- `timing_enabled` default flipped from `false` to `true`.
- `workflows/parameter-collection.md` continues to prompt the user — no silent auto-apply.
- Master summary Timing Breakdown is always generated; column non-blocking-flags `unavailable` / `not-requested` rows so opt-out and failures remain visible.
- Propagates `timing_enabled=true` to every per-rule rule-reviewer invocation; parallel sub-agents carry the same default.
- Byte caps raised 12000 → 13500 where present.
- Depends on rule-reviewer v2.9.0 and skill-timing v1.5.0.

## v2.3.0 (2026-04-21) — Per-rule and per-dimension timing propagation

Introduced per-rule and per-dimension timing propagation with Quick Reference, mandatory `rule_{slug}_start/end` checkpoint pairs (steps 4a/15a), master-summary Timing Breakdown section, parallel sub-agent reporting contract, Gate enforcement in per-rule verification, Common Timing Mistakes anti-pattern block, and `[OPTIONAL]` → `(Required when timing_enabled: true)` tag demotion. Depends on skill-timing v1.5.0 and rule-reviewer v2.8.0.

## v2.2.0 (2026-03-23) — Context preservation, shortcut prevention, silent processing
