# Changelog

All notable changes to the `stage-changes` skill are documented in this file.
Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-06-21

### Changed

- Standardize Gate 2 preview formatting per [ADR 0007](../../docs/adr/0007-skill-style-guide.md): three labeled blocks (`FILES TO BE STAGED`, `WARNINGS`, `EXCLUDED`) with double `═` outer frame, single `─` inner separator, two-blank-line gaps between blocks, metadata-hint suffix on WARNINGS/EXCLUDED. Resolves audit finding SC-1.

### Added

- Initial release.
- Two-gate flow: grouped multi-select (dir primary, change-class secondary) → resolved file-list confirmation.
- Untracked files included by default and labeled `[new]`.
- Safety scan: binary detection, size warnings (`warn_size_mb`, default 5 MB), submodule exclusion, `.gitignore` defense.
- Refuses to operate during merge / cherry-pick / rebase.
- `mode: "all"` skips group selection while preserving the confirmation gate.
- `paths` input skips both inference and group selection for scripted invocations.
