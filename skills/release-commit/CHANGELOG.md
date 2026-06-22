# Changelog

All notable changes to the `release-commit` skill are documented in this file.
Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## [1.1.1] - 2026-06-21

### Changed

- Standardize combined dry-run preview formatting per [ADR 0007](../../docs/adr/0007-skill-style-guide.md): three labeled blocks (`PROPOSED CHANGELOG ENTRY`, `PROPOSED COMMIT MESSAGE`, `FILES TO BE STAGED ON APPROVAL`) with double `═` outer frame, single `─` inner separator, **two-blank-line gaps between blocks**, metadata-hint suffix on the files block. Resolves audit finding RC-1.

## [1.1.0] - 2026-06-21

### Added

- Auto-invoke `stage-changes` when nothing is staged on entry. Combined preview separates "already staged" from "staged via stage-changes this invocation".
- `skip_stage` input (default: `false`) preserves the prior fail-fast behavior.

### Changed

- On commit failure, files staged via the auto-invoked `stage-changes` step are left in the index so the user can retry without re-staging. The changelog edit is still reverted.

## [1.0.0] - 2026-06-21

### Added

- Initial orchestrator skill combining `update-changelog` and `commit-changes`.
- Single combined dry-run gate with `Commit / Edit changelog / Edit commit message / Cancel`.
- Atomic apply: changelog edit reverted if commit step fails.
- `skip_changelog` input to degrade to commit-only behavior.
