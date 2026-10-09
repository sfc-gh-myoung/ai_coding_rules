---
schema_version: v4.0
rule_version: v5.0.0
description: "Maintaining high-signal, audit-friendly CHANGELOG.md following Keep a Changelog standard with feature-focused Conventional Commits-style entries for consistent project change documentation."
last_updated: 2026-10-06
keywords:
  - kw:CHANGELOG.md
  - kw:Keep a Changelog
  - kw:Conventional Commits style
  - kw:Unreleased section
  - kw:changelog entry consolidation
  - kw:release notes workflow
token_budget: ~900
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
  optional:
    - 801-project-readme.md  # README documentation standards
    - 802-project-contributing.md  # Contributing guidelines and workflow
    - 803-project-git-workflow.md  # Git workflow and branch management
---
# Changelog Governance Directives

## Scope

**What This Rule Covers:**
Human-readable, auditable change history using Keep a Changelog categories and the project's conventional-entry style.

**When to Load This Rule:**
When editing a changelog, documenting a project change, preparing release notes or reviewing release-history quality.

## Contract

### Inputs and Prerequisites

- Existing changelog, actual change evidence, project version/release conventions and repository URL.
- Current contribution guidelines and explicit release authorization when finalizing a version.

### Mandatory

- Read existing history and scopes before adding entries. Maintain a root CHANGELOG for cross-cutting changes; use the closest package changelog for package-specific work in established monorepos.
- Record code, configuration, rule and documentation changes under `## [Unreleased]` before task completion; changes solely to changelog formatting/history do not need a self-referential entry. An explicit user override must be disclosed.
- Use Added, Changed, Deprecated, Removed, Fixed or Security, at most one heading per category per version. Keep summaries concise, human-readable and focused on user impact, not raw commit dumps, filenames or internal inventories.
- Prefer existing `**type(scope):** summary` conventions. This supplements Keep a Changelog, not a claim that Conventional Commits mandates release-note bullets.
- Preserve every existing logical concept when restyling; do not collapse or delete release history without explicit consolidation scope.
- Consolidate new iterative micro-fixes supporting one feature/version into a meaningful entry when appropriate, without hiding distinct breaking/security/deprecation impacts.
- Mark breaking changes clearly with migration implications; Security gets prominent category and real CVE links only when verified. Deprecation states the agreed removal event/version, never an invented deadline.
- Do not include secrets, raw stack traces, unnecessary personal names or jargon. Link verified relevant issues/PRs where useful.
- Release finalization requires authorization: move Unreleased entries to the actual version/date, reset Unreleased and update comparison links from verified repository/tag identities. Do not tag/push/publish merely because a changelog is edited.

### Execution Steps

1. Read changelog/contribution standards and review actual changes; identify the appropriate changelog location and scope.
2. Choose the standard category and write a concise user-facing entry matching the file's style.
3. Check duplicates, preserve existing concepts and ensure breaking/security/deprecation guidance remains explicit.
4. For an authorized release, move entries to the verified version/date and maintain Unreleased/compare links; otherwise leave them unreleased.
5. Run project Markdown/structure/link checks and report unavailable verification honestly. Review generated changelog tooling output rather than trusting raw commit extraction.

### Validation

- Unreleased exists and new entries sit under standard nonduplicated categories.
- History concepts remain intact, entries are user-impactful and no secret/private diagnostic content leaks.
- Version/date/compare links match actual approved release state; no fictional CVE, PR or tag.
- Related changes consolidated only within scope, distinct migration/security outcomes retained.
- Markdown and project changelog checks pass; release/source-control actions remain separately authorized.

## References

- [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [CommonMark](https://spec.commonmark.org/)
