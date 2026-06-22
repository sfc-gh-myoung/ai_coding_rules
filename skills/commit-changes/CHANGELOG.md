# Changelog

All notable changes to the `commit-changes` skill are documented in this file.
Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## [1.1.1] - 2026-06-21

### Changed

- Standardize dry-run preview formatting per [ADR 0007](../../docs/adr/0007-skill-style-guide.md): double `═` outer frame, single `─` inner separator, all-caps section labels, two-blank-line gap between sections. Resolves audit finding CC-1.

## [1.1.0] - 2026-06-21

### Changed

- Commit body must be feature-focused and concise; omit entirely when the subject suffices.
- Removed file-list bullet default from body composition — file inventory is recoverable via `git show --stat`.
- Added explicit anti-pattern entry forbidding file lists in commit message bodies.
- Updated example to reflect the new no-file-list contract.

## [1.0.0] - 2026-06-21

### Added

- Initial conversion from `prompts/commit-changes.md`.
- Conventional Commits 1.0.0 message drafting from staged diff.
- Dry-run gate with `Commit / Edit / Cancel` options.
- Type and scope inference from staged paths and diff signals.
- Refuses to operate during merge or cherry-pick.
