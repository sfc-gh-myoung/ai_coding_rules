---
schema_version: v4.0
rule_version: v3.0.0
description: "Universal best practices for organizing project documentation files, including file placement conventions, extended documentation types, cross-reference management, and GitHub community health file"
last_updated: 2026-10-06
keywords:
  - kw:docs folder structure
  - kw:community health files placement
  - kw:ARCHITECTURE.md location
  - kw:relative path cross-references
  - kw:ADR folder conventions
  - kw:GitHub Pages deployment
token_budget: ~900
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 800-project-changelog.md  # Changelog management standards
    - 801-project-readme.md  # README best practices
    - 802-project-contributing.md  # Contributing guidelines
---
# Project Documentation Organization

## Scope

**What This Rule Covers:**
Documentation placement, user/contributor/operator boundaries, cross-references, optional ADRs and published-site configuration.

**When to Load This Rule:**
When organizing or moving docs, creating architecture/deployment guides, managing internal links or preparing a documentation site.

## Contract

### Inputs and Prerequisites

- Existing structure, audiences, link consumers and actual repository hosting/site configuration.
- Approved move/create scope and current source evidence for documented behavior.
- Project Markdown/link tooling and writing standards.

### Mandatory

- Preserve established project paths unless reorganization is requested. Keep README, LICENSE and essential community entry points discoverable; GitHub supports relevant community files in root, docs or .github depending on file type, not root-only universally.
- Prefer maintained extended guides under `docs/` and short-lived evidence under `.workbench/`, honoring explicitly approved plan/evidence locations.
- Give each document a clear audience/purpose: user quick start in README, contributor workflow in CONTRIBUTING, architecture for reviewers, deployment/troubleshooting for operators.
- Keep one authoritative description and link instead of duplicating setup/config instructions across documents.
- Use relative internal links/anchors that survive forks and branch changes. Search all consumers and update references atomically with moves; validate case-sensitive paths and rendered anchors.
- Do not create empty placeholder docs or generic folder trees just because a project passes an arbitrary line-count threshold.
- ADRs are opt-in. When used, name them with the established numbered-title convention and include date, status, context, decision and consequences; preserve superseded decisions with references.
- Documentation publishing/configuration is separate authorized work. Existing docs placement does not prove GitHub Pages/site deployment exists or succeeds.
- Keep sensitive internal endpoints/access/contact details within approved audience boundaries; public docs must not expose private configuration.

### Execution Steps

1. Read the current doc structure, entry points, related source and actual hosting/site settings.
2. Identify necessary audience-specific content and canonical location; avoid speculative docs/reorganization.
3. For approved moves, search references, move without overwriting unrelated content and update all links/imports/navigation.
4. Validate internal paths/anchors and Markdown; inspect external references and report access limits.
5. If site publishing is authorized, verify actual generator/config/build and deployment source rather than prescribing a generic Pages click path.
6. Review discoverability, duplication and stale claims, and report actual completed changes/verification.

### Validation

- Documents have clear purpose, appropriate maintained/scratch location and no duplicated authoritative instructions.
- All affected links/navigation/anchors resolve after moves; source references accurate.
- Community files remain discoverable through actual hosting-supported paths.
- ADRs optional, decisions/rationale/history preserved; no empty invented architecture.
- Markdown/site builds/links checked where authorized, publishing not assumed or executed without approval.

## References

- [GitHub community health files](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)
- [GitHub Pages](https://docs.github.com/en/pages)
- [Architectural decision records](https://adr.github.io/)
- [Diataxis](https://diataxis.fr/)
- [CommonMark](https://spec.commonmark.org/)
