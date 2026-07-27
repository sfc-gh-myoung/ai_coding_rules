# Rule Creator — Changelog

All notable changes to the `rule-creator` skill. Current version is tracked in `SKILL.md` frontmatter.

## v1.1.3 (2026-07-11) — Remove obsolete human-only framing

### Changed

- docs: remove all `human-only` qualifiers from SKILL.md, workflows, examples, and tests now that `rule frontmatter` is the single agent-discovery index (dual-index collapse). References to `rule frontmatter` are now unqualified. `rule-matcher_COMPACT.md` was deleted; all occurrences updated to `rule frontmatter`.

## v1.1.2 (2026-07-11) — Audit human-only rule frontmatter labeling

### Changed

- docs: label all `rule frontmatter` references throughout skill, workflows, examples, and tests as `human-only` to distinguish the generated full index from the agent-discovery `rule-matcher_COMPACT.md`. No behavioral changes; documentation and comments only.

## v1.1.1 (2026-06-21) — Audit P3 remediation

### Changed

- docs: remove decorative heading suffixes — `## Inputs (recommended)` → `## Inputs`; `## Workflow (progressive disclosure)` → `## Workflow`. The qualifiers moved into the section body.

## v1.1.0 (2025-12-15) — Enhanced skill structure

- Added `version`, `author`, `tags`, `dependencies` to frontmatter.
- Improved description with trigger keywords and domain coverage.
- Added inline validation snippets for quick checks.
- Added version history section.
- Added cross-reference to `rule-reviewer` skill.

## v1.0.0 (2024-12-11) — Initial release

- 5-phase workflow with script orchestration.
- Claude Code-compliant structured skill format.
- Complete examples for 3 domains.
- Phase-specific workflow guides.
