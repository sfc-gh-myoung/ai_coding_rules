# Changelog

All notable changes to the `update-changelog` skill are documented in this file.
Format: [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/).

## [1.1.1] - 2026-06-21

### Changed

- Standardize dry-run preview formatting per [ADR 0007](../../docs/adr/0007-skill-style-guide.md): single labeled block with double `═` outer frame, single `─` inner separator, all-caps `PROPOSED CHANGELOG ENTRY` label, source-mode subtitle. Resolves audit finding UC-1.

## [1.1.0] - 2026-06-21

### Added

- Recent-commits fallback mode. When `source: "auto"` (default) and nothing is staged, the skill offers to backfill `[Unreleased]` from the last N commits via an explicit `Use recent commits / Cancel` gate.
- `source` input: `"staged"` | `"recent-commits"` | `"auto"` (default `"auto"`).
- `commit_count` input (default `5`, range 1–20) for recent-commits mode.
- `since_ref` input for "since last tag" backfills (e.g., `since_ref: "v1.0.0"`).
- Conventional Commits type inference for recent-commits mode (feat / fix / breaking / etc. → KaC categories).
- Short-hash traceability suffix on recent-commits bullets.

### Changed

- Frame header now indicates the source mode and (for recent-commits) the commit range.
- Merge commits are excluded from recent-commits source (`--no-merges`).
- "Use this skill when" now lists backfill from recent commits as a supported use case.

## [1.0.0] - 2026-06-21

### Added

- Initial conversion from `prompts/update-changelog.md`.
- Keep-a-Changelog 1.1.0 entry drafting from staged diff.
- Category inference (Added / Changed / Fixed / Removed / Security).
- Dry-run gate with `Apply / Edit / Cancel` options.
- Idempotence: duplicate bullets are skipped with a warning.
- Skeleton creation flow when `CHANGELOG.md` is missing (approval-gated).
