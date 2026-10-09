# Bulk Rule Reviewer: Changelog

All notable changes to the `bulk-rule-reviewer` skill. Current version is tracked in `SKILL.md` frontmatter.

## [2.6.1] - 2026-08-21

### Fixed

- Corrected `workflows/parameter-collection.md` to say "6 scored dimensions" (was "7") — aligns with rule-reviewer, `reviewer-defaults.yml`, and skill-timer `EXPECTED_DIMENSIONS`.
- Corrected the interactive Timing question, which stalely marked "No" as the default; `timing_enabled` default is `true`, so "Yes" is now the shown default in both question blocks.

### Changed

- Replaced restated passages with pointers to the new `skills/shared/reviewer-contract.md`: parameter-collection rules, skill-timer timing mechanism, and opt-out semantics.
- Priority-tier sections now annotate that band boundaries come from `../rule-reviewer/references/reviewer-defaults.yml`; no-overwrite and JSON-authority notes now point to `file-write.md` and `docs/ARCHITECTURE.md` §3.6.
- `workflows/timing-integration.md`: removed the duplicated 4 anti-patterns (now shared); kept the bulk Quick Reference block, Contract, and Responsibility Split.

## [2.6.0] - 2026-08-20

### Changed

- **Breaking:** Stage 3 Aggregation now discovers `.json` canonical review artifacts instead of parsing `.md` files. Uses `ai-rules review-artifact aggregate` to extract scores and verdicts from structured data. Orphan `.md` files (no same-stem `.json` sibling) are counted but excluded from statistics.
- Individual review output updated: `.json` is primary canonical artifact; `.md` is derived via `ai-rules review-artifact render`.
- Dependency bumped: `rule-reviewer skill v2.9.0+` → `v2.12.0+`; `skill-timer v1.5.0+` → `v2.0.0+`.
- Markdown-only fallback prohibited: aggregation never accepts `.md` input without a same-stem `.json` artifact.

## [2.5.0] - 2026-08-19

### Changed

- Progressive disclosure: consolidated 5 individual timing checkpoint subsections into a single "Timing Checkpoints" table. Replaced "Timing End: Compute" + "Timing End: Embed" + "Checkpoint: summary_complete" with a compact "Timing End" section.
- Compressed "Timing Start" (10 lines → 3 lines) with pointer to `workflows/timing-integration.md`.
- Replaced verbatim Gate 8 block (17 lines) with a pointer to the authoritative `../rule-reviewer/references/gate-8.md`.
- "Installation Requirements" compressed to "Dependencies" (4 lines).
- "Validation" section trimmed: key requirements list moved to `workflows/input-validation.md`; SKILL.md retains a 2-line pointer.
- "Success Criteria" + "Expected Outcomes" (16 lines) merged into a 3-line summary.
- "References" subsection removed (content accessible via Related Skills).
- SKILL.md reduced from 298 to 222 lines. No behavioral changes.

## [2.4.1] - 2026-06-21

### Changed

- Rewrote frontmatter description (78c → ~360c) per audit finding BRR-1: now includes verb + noun + context + 5 trigger phrases per 002h §5 discoverability criteria.

- Added **Gate 8** to SKILL.md: when `skill_timer.py end` returns
  `status ∈ {dimension_invalid, instrumentation_failed}`, refuse to
  publish the Per-Dimension Timing markdown table. Replace with a banner
  pointing at the rejected JSON in `reviews/.timing-data/`.
- No code changes in this skill; the gate is enforced at the markdown-emit
  step. See `skills/skill-timer/CHANGELOG.md` v2.0.0 for the underlying
  mechanism (new exit code 4, status enum extensions, distribution validator).

## v2.4.0 (2026-04-21): Per-rule and per-dimension timing as the universal default

- `timing_enabled` default flipped from `false` to `true`.
- `workflows/parameter-collection.md` continues to prompt the user: no silent auto-apply.
- Master summary Timing Breakdown is always generated; column non-blocking-flags `unavailable` / `not-requested` rows so opt-out and failures remain visible.
- Propagates `timing_enabled=true` to every per-rule rule-reviewer invocation; parallel sub-agents carry the same default.
- Byte caps raised 12000 → 13500 where present.
- Depends on rule-reviewer v2.9.0 and skill-timing v1.5.0.

## v2.3.0 (2026-04-21): Per-rule and per-dimension timing propagation

Introduced per-rule and per-dimension timing propagation with Quick Reference, mandatory `rule_{slug}_start/end` checkpoint pairs (steps 4a/15a), master-summary Timing Breakdown section, parallel sub-agent reporting contract, Gate enforcement in per-rule verification, Common Timing Mistakes anti-pattern block, and `[OPTIONAL]` → `(Required when timing_enabled: true)` tag demotion. Depends on skill-timing v1.5.0 and rule-reviewer v2.8.0.

## v2.2.0 (2026-03-23): Context preservation, shortcut prevention, silent processing
