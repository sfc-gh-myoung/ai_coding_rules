# Changelog

All notable changes to the `update-project-docs` skill are documented in this file.
Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## [1.0.1] - 2026-06-21

### Changed

- Standardize per-file remediation preview formatting per [ADR 0007](../../docs/adr/0007-skill-style-guide.md): two labeled blocks (`PROPOSED FILE EDIT (path)` + `RATIONALE`) with double `═` outer frame, single `─` inner separator, two-blank-line gap. Resolves audit finding UPD-1.

## [1.0.0] - 2026-06-21

### Added

- Initial conversion from `prompts/update-project-docs.md`.
- Discovery-based file selection (`./*.md` + `docs/**/*.md` with exclusion list).
- Overlap matrix, contradiction detection, staleness check.
- Diátaxis and GitHub community standards heuristics.
- Read-only by default; `apply_remediation` opt-in with per-file dry-run gates.
