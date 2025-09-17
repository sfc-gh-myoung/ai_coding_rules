**Description:** Directives for maintaining a high-signal, audit-friendly `CHANGELOG.md` using Conventional Commits.
**AppliesTo:** `CHANGELOG.md`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-14

# Changelog Governance Directives

## Purpose
Establish directives for maintaining a high-signal, audit-friendly CHANGELOG.md using Conventional Commits, ensuring consistent documentation of project changes for stakeholders and maintainers.

## 1. Required Structure & Format
- **Requirement:** Maintain a single `CHANGELOG.md` at the project root.
- **Requirement:** Keep a top-level `## [Unreleased]` section for new changes.
- **Requirement:** On release, move entries from Unreleased to `## [x.y.z] - YYYY-MM-DD`.
- **Requirement:** Group entries under: Added/Features, Fixed/Bugfixes, Changed/Refactored, Documentation/Content, Styling/UI, Chore/Tooling, Deployment/CI, Data/Enhancements.
- **Requirement:** Each entry is a single line in Conventional Commit format: `<type>(<scope>): <summary>`.
- **Rule:** Use consistent scope patterns aligned with project structure:
  - Core: `core`, `governance`, `memory-bank`
  - Snowflake: `snowflake`, `sql`, `streamlit`, `spcs`
  - Python: `python`, `fastapi`, `lint`, `setup`, `cli`, `typer`, `pydantic`, `faker`, `flask`
  - Shell: `bash`, `zsh`, `shell`
  - Project: `changelog`, `readme`, `contributing`, `taskfile`
  - Analytics: `data-science`, `governance`, `business`
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

## 4. Scope Examples for New Domains

### CLI Application Changes
```
feat(cli): add progress bars for long-running operations
feat(typer): implement async command support
fix(cli): handle keyboard interrupts gracefully
docs(typer): add CLI testing examples
```

### Data Validation and Testing Changes
```
feat(pydantic): add comprehensive model validation patterns
feat(faker): implement localized data generation providers
fix(pydantic): resolve serialization issues with nested models
test(faker): add performance benchmarks for large datasets
docs(pydantic): add FastAPI integration examples
```

### Web Framework Changes
```
feat(flask): add application factory pattern with blueprints
feat(flask): implement comprehensive security middleware
fix(flask): resolve CSRF token validation in AJAX requests
perf(flask): optimize database query patterns in services
docs(flask): add deployment and production configuration examples
```

### Rule File Changes
```
feat(rules): add comprehensive Typer CLI development patterns
docs(contributing): update with new numbering scheme patterns
refactor(rules): split oversized bash rule into focused components
```

### Cross-Domain Changes
```
feat(python,cli): integrate Typer with uv project setup patterns
chore(rules): update all Python rules for CLI consistency
```

## 5. Documentation
- **Always:** Reference Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/#specification
- **Always:** Follow contributing guidelines: `@805-project-contributing-rules.md`
