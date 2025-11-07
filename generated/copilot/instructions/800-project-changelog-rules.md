---
appliesTo:
  - "CHANGELOG.md"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** CHANGELOG, changelog format, semantic versioning, release notes, conventional commits, Unreleased section, scope patterns
**TokenBudget:** ~1450
**ContextTier:** Medium
**Depends:** 000-global-core

# Changelog Governance Directives

## Purpose
Establish directives for maintaining a high-signal, audit-friendly CHANGELOG.md using Conventional Commits, ensuring consistent documentation of project changes for stakeholders and maintainers.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** High-signal, audit-friendly changelog maintenance using Conventional Commits

## Quick Start TL;DR (Read First - 30 Seconds)

**MANDATORY:**
**Essential Patterns:**
- **Maintain Unreleased section** - All new changes go here first
- **Use Conventional Commits** - type(scope): summary format
- **Group by category** - Features, Fixes, Docs, Chore, etc.
- **Consistent scopes** - Align with project structure
- **Collapse micro-fixes** - One meaningful entry, not 10 tweaks
- **Move to version on release** - ## [x.y.z] - YYYY-MM-DD
- **Never duplicate commit details** - Keep summaries concise

**Quick Checklist:**
- [ ] Unreleased section exists
- [ ] Entries use Conventional Commits format
- [ ] Grouped by category
- [ ] Scopes are consistent
- [ ] Micro-fixes collapsed
- [ ] Ready for release versioning
- [ ] User-impact oriented summaries

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

## 3. Workflow & Maintenance (MANDATORY)

**Reference:** Pre-Task-Completion Validation Gate in `000-global-core.md` and `AGENTS.md`

**CRITICAL:** CHANGELOG.md updates are MANDATORY before task completion for all code changes.

- **MANDATORY:** After making ANY code change, append a new entry under `## [Unreleased]` before marking task complete.
- **CRITICAL:** Do not mark tasks complete without updating CHANGELOG.md for code changes.
- **MANDATORY:** On release, finalize Unreleased, add the new version heading, and move entries.
- **Always:** If available, validate the structure with `scripts/validate_changelog_structure.py`.
- **Exception:** Only skip if user explicitly requests override (acknowledge that changelog will be incomplete).

### What Constitutes a Change Requiring Changelog Entry
- **MANDATORY:** Any modification to Python files (`.py`)
- **MANDATORY:** Any modification to SQL files (`.sql`)
- **MANDATORY:** Any modification to configuration files (`pyproject.toml`, `Taskfile.yml`, etc.)
- **MANDATORY:** Any modification to shell scripts (`.sh`, `.bash`, `.zsh`)
- **MANDATORY:** Any modification to rule files (`.md` in `ai_coding_rules/`)
- **MANDATORY:** Any modification to documentation files (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`)
- **MANDATORY:** New features, bug fixes, refactors, or performance improvements
- **MANDATORY:** Documentation-only changes (no longer optional - ALWAYS update CHANGELOG.md)
- **Rationale:** Documentation changes are user-facing and must be tracked for complete audit trail

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

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] **CRITICAL:** CHANGELOG.md updated with entry under `## [Unreleased]` for code changes
- [ ] **CRITICAL:** Entry follows Conventional Commit format: `<type>(<scope>): <summary>`
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** CHANGELOG.md contains entry under `## [Unreleased]` for code changes; entry follows Conventional Commit format; entry is concise and user-impact oriented; Pre-Task-Completion Validation Gate passed
- **Negative tests:** Code changes without CHANGELOG.md updates block task completion; entries with incorrect format fail validation; task completion attempted without changelog update is prevented

> **Investigation Required**
> When applying this rule:
> 1. **Read existing CHANGELOG BEFORE adding** - Check format, scope patterns
> 2. **Verify Unreleased section exists** - Create if missing
> 3. **Never assume scope conventions** - Check existing scopes in file
> 4. **Check for duplicates** - Avoid redundant entries
> 5. **Validate Conventional Commits format** - Ensure type(scope): summary
>
> **Anti-Pattern:**
> "Adding changelog entry... (without checking existing format)"
> "Using arbitrary scope... (doesn't match project patterns)"
>
> **Correct Pattern:**
> "Let me check your CHANGELOG format first."
> [reads CHANGELOG, checks scopes, reviews categories]
> "I see you use 'snowflake' and 'python' scopes. Adding entry following this pattern..."

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Conventional Commits](https://www.conventionalcommits.org/) - Standardized commit message format specification                                                                                                       
- [Keep a Changelog](https://keepachangelog.com/) - Changelog format and best practices guide
- [Semantic Versioning](https://semver.org/) - Version numbering scheme for software releases

### Related Rules
- **Global Core**: `000-global-core.md`
- **Contributing Guidelines**: `805-project-contributing-rules.md`
- **README Rules**: `801-project-readme-rules.md`
