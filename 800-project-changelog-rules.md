**Description:** Directives for maintaining a high-signal, audit-friendly `CHANGELOG.md` using Conventional Commits.
**AppliesTo:** `CHANGELOG.md`
**AutoAttach:** false
**Version:** 1.0
**LastUpdated:** 2025-09-10

# Changelog Governance Directives

## 1. Required Structure & Format
- **Requirement:** Maintain a single `CHANGELOG.md` at the project root.
- **Requirement:** Keep a top-level `## [Unreleased]` section for new changes.
- **Requirement:** On release, move entries from Unreleased to `## [x.y.z] - YYYY-MM-DD`.
- **Requirement:** Group entries under: Added/Features, Fixed/Bugfixes, Changed/Refactored, Documentation/Content, Styling/UI, Chore/Tooling, Deployment/CI, Data/Enhancements.
- **Requirement:** Each entry is a single line in Conventional Commit format: `<type>(<scope>): <summary>`.
- **Always:** Collapse iterative micro-fixes into one meaningful entry.

## 2. Quality and Content
- **Requirement:** Summaries are concise and user-impact oriented; avoid duplicating commit body details.
- **Requirement:** Do not include raw stack traces, personal names, or internal-only jargon.
- **Requirement:** Mark breaking changes with `!` and explain them clearly.
- **Always:** Link to relevant PRs or issues (`[#123]`) when helpful.

## 3. Workflow & Maintenance
- **Always:** After merging a change, append a new entry under `## [Unreleased]`.
- **Always:** On release, finalize Unreleased, add the new version heading, and move entries.
- **Always:** If available, validate the structure with `scripts/validate_changelog_structure.py`.

## 4. Documentation
- **Always:** Reference Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/#specification
