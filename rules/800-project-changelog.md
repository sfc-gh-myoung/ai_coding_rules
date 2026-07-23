---
schema_version: v3.5
rule_version: v4.0.0
description: "Maintaining high-signal, audit-friendly CHANGELOG.md following Keep a Changelog standard with feature-focused Conventional Commits-style entries for consistent project change documentation."
last_updated: 2026-07-15
keywords:
  - kw:CHANGELOG.md
  - kw:Keep a Changelog
  - kw:Conventional Commits style
  - kw:Unreleased section
  - kw:changelog entry consolidation
  - kw:release notes workflow
  - kw:ci/cd
token_budget: ~5350
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
Maintaining high-signal, audit-friendly CHANGELOG.md following Keep a Changelog standard with feature-focused Conventional Commits-style entries for consistent project change documentation.

**When to Load This Rule:**
- Modifying CHANGELOG.md directly
- Any code change requiring changelog entry
- Project releases (moving Unreleased to version)
- Implementing Conventional Commits workflow
- Setting up changelog standards for new projects
- Reviewing changelog compliance during pull requests

## References

### External Documentation

**Official Standards:**
- [Keep a Changelog v1.1.0](https://keepachangelog.com/) - Primary changelog format standard
- [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification) - PREFERRED commit message format (strongly recommended for changelog entries)
- [Semantic Versioning](https://semver.org/) - Version numbering scheme for software releases
- [CommonMark Spec](https://spec.commonmark.org/) - Authoritative Markdown specification (CHANGELOG.md MUST comply)

**Additional Resources:**
- Follow contributing guidelines: `802-project-contributing.md`

## Contract

### Inputs and Prerequisites

- Existing CHANGELOG.md file (or create new)
- Knowledge of changes made to codebase
- Understanding of Keep a Changelog v1.1.0 standard
- Project's version control system URL (for comparison links)

### Mandatory

- Read existing CHANGELOG.md to understand format and scope patterns
- Use Keep a Changelog v1.1.0 standard types (see canonical list in Document Structure and Format)
- Add entries under ## [Unreleased] section
- Prefer feature-focused Conventional Commits-style bullets: `**type(scope):** user-facing summary`
- Ensure human-readable, user-impact focused summaries
- Preserve existing logical changelog concepts when restyling; rewrite each concept into the preferred style unless explicitly asked to consolidate

### Forbidden

- Never add entries outside standard Keep a Changelog types
- Never skip CHANGELOG update for code changes
- Never use jargon or internal-only terminology
- Never duplicate full commit messages in changelog entries
- Never include file lists or implementation inventories in changelog entries
- Never collapse or delete existing logical entries merely to restyle them

### Execution Steps

1. Read CHANGELOG.md to check format, existing scopes, and structure
2. Identify change type: Added, Changed, Deprecated, Removed, Fixed, or Security
3. Write concise, human-readable summary focusing on user-visible behavior
4. Add entry under appropriate type heading in ## [Unreleased] section
5. Use feature-focused Conventional Commits style when practical: `**type(scope):** summary`
6. Verify entry is not duplicate, preserves logical concepts, and follows existing patterns

### Output Format

```markdown
## [Unreleased]

### Added
- New feature that users can now access

### Fixed
- Bug that was affecting user workflows
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**Documentation Requirements:**
- **CRITICAL:** Entry added under `## [Unreleased]` section
- **CRITICAL:** Entry uses standard Keep a Changelog type (see canonical list in Document Structure and Format)
- **CRITICAL:** Summary is human-readable and user-impact focused
- **Format Check:** Entry matches existing format patterns in file
- **Duplication Check:** No duplicate entries exist

**Success Criteria:**
- CHANGELOG.md contains entry under `## [Unreleased]`
- If using Conventional Commits, entry follows format: `**<type>(<scope>):** <summary>`
- Entry is concise and user-impact oriented
- Pre-Task-Completion Validation Gate passed

**Validation Protocol:**
- **Rule:** Run validation after modifications
- **Rule:** Do not mark tasks complete if checks fail
- **Exception:** Only skip with explicit user override

**Investigation Required:**
1. **Read existing CHANGELOG BEFORE adding** - Check format, scope patterns
2. **Verify Unreleased section exists** - Create if missing
3. **Never assume scope conventions** - Check existing scopes in file
4. **Check for duplicates** - Avoid redundant entries
5. **Validate Conventional Commits format (if used)** - Ensure `**type(scope):** summary`
6. **Preserve existing concepts when restyling** - Convert each logical entry to the preferred style unless the user explicitly approves consolidation

**Anti-Pattern Examples:**
- "Adding changelog entry..." (without checking existing format)
- "Using arbitrary scope..." (doesn't match project patterns)

**Correct Pattern:**
- "Let me check your CHANGELOG format first."
- [reads CHANGELOG, checks scopes, reviews categories]
- "I see you use 'snowflake' and 'python' scopes. Adding entry following this pattern..."

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (000-global-core.md)
- [ ] CHANGELOG.md file exists (or ready to create)
- [ ] Understanding of Keep a Changelog v1.1.0 standard
- [ ] Knowledge of changes made to codebase

**After Completion:**
- [ ] **CRITICAL:** CHANGELOG.md updated with entry under `## [Unreleased]`
- [ ] **If using Conventional Commits:** Entry follows format: `<type>(<scope>): <summary>`
- [ ] Entry uses standard Keep a Changelog type
- [ ] Summary is human-readable and user-impact focused
- [ ] Format matches existing entries in file
- [ ] No duplicate entries
- [ ] Micro-fixes collapsed into meaningful entries
- [ ] Version comparison links updated (if applicable)

## Anti-Patterns and Common Mistakes

### Pattern 1: Using Non-Standard Category Names

**Problem:**
Creating custom categories like "Chore", "Deployment", "Styling" instead of standard Keep a Changelog types.

**Why It Fails:**
- Breaks compatibility with Keep a Changelog standard
- Makes changelogs inconsistent across projects
- Users familiar with standard expect standard types

**Correct Pattern:**
```markdown
# ❌ WRONG - Custom categories
## [Unreleased]
### Chore
- Updated build scripts
### Styling
- Changed button colors

# ✅ CORRECT - Standard types
## [Unreleased]
### Changed
- Updated build scripts for faster compilation
- Improved button styling for better accessibility
```

### Pattern 2: Missing Security or Deprecated Entries

**Problem:**
Not using **Security** type for vulnerability fixes or **Deprecated** type for features being phased out.

**Why It Fails:**
- Security fixes are critical and must be prominent
- Users need advance warning about deprecations
- Missing these categories hides important information

**Correct Pattern:**
```markdown
# ❌ WRONG - Security fix buried in "Fixed"
## [Unreleased]
### Fixed
- Resolved authentication bypass issue

# ✅ CORRECT - Prominent Security section
## [Unreleased]
### Security
- Fixed authentication bypass vulnerability (CVE-2024-1234)

### Deprecated
- Legacy API v1 endpoints will be removed in v4.0.0 (use v2 instead)
```

### Pattern 3: Dumping Git Commit Messages

**Problem:**
Copying raw commit messages or technical details into changelog.

**Why It Fails:**
- Changelogs are for humans, not machines
- Users care about impact, not implementation details
- Technical jargon alienates non-technical users

**Correct Pattern:**
```markdown
# WRONG - Technical commit dump
## [Unreleased]
### Fixed
- refactor(auth): replace deprecated bcrypt.compare with bcrypt.verify in UserService.authenticate() method

# CORRECT - User-focused, conventional-style summary
## [Unreleased]
### Fixed
- **fix(auth):** resolve login failures for users with special characters in passwords.
```

### Pattern 4: Duplicate Category Headings

**Problem:**
Multiple instances of the same category heading (e.g., two `### Added` sections) within the same version block.

**Why It Fails:**
- Breaks Keep a Changelog structure expectations
- Confuses readers scanning for specific change types
- Complicates automated changelog parsing and tooling
- Creates inconsistent documentation that is harder to maintain

**Correct Pattern:**
```markdown
# ❌ WRONG - Duplicate category headings
## [Unreleased]
### Added
- Feature A

### Fixed
- Bug B

### Added
- Feature C

# ✅ CORRECT - Single heading per category
## [Unreleased]
### Added
- Feature A
- Feature C

### Fixed
- Bug B
```

### Pattern 5: Repetitive Scope Prefixes Within a Section

**Problem:**
Repeating the same `**type(scope):**` prefix multiple times within a single category when entries relate to the same version bump.

**Why It Fails:**
- Creates visual noise that obscures the actual changes
- Violates "one entry per version bump" principle
- Makes scanning difficult when 10+ entries share the same prefix
- Suggests entries should be consolidated into a single version-bump bullet

**Correct Pattern:**
```markdown
# [BAD] - Repetitive prefixes
### Added
- **feat(plan-reviewer):** add Step 4a for checkpoint pairs
- **feat(plan-reviewer):** add Gate 7 verification
- **feat(plan-reviewer):** add anti-pattern block
- **feat(plan-reviewer):** add Quick Reference
- **docs(plan-reviewer):** add timing walkthrough
- **test(plan-reviewer):** add Test 7 for timing

# [GOOD] - Consolidated by version bump
### Added
- **feat(plan-reviewer):** v2.4.0 — per-dimension timing capture
  - Step 4a checkpoint pairs, Gate 7 verification, anti-pattern block
  - Quick Reference, timing walkthrough example, Test 7
```

## Output Format Examples

```markdown
Project Documentation Changes:

**File Modified:** [README.md|CHANGELOG.md|CONTRIBUTING.md]
**Section Updated:** [specific section]
**Validation:** [documentation standards checklist]

Changes Made:
1. **[Section Name]**
   - Added: [specific content]
   - Updated: [what changed and why]
   - Format: [Markdown standards followed]

2. **[Another Section]**
   - Clarified: [ambiguous content]
   - Examples: [added working examples]

Validation Checklist:
- [x] Markdown lint passes
- [x] Links are valid and accessible
- [x] Code examples are tested
- [x] Formatting is consistent
- [x] Table of contents updated (if applicable)

Preview:
[Show relevant excerpt of updated documentation]
```

## Document Structure and Format

- **Requirement:** Maintain a single `CHANGELOG.md` at the project root.
- **Requirement:** Keep a top-level `## [Unreleased]` section for new changes.
- **Requirement:** On release, move entries from Unreleased to `## [x.y.z] - YYYY-MM-DD`.
- **Requirement:** Include standard Keep a Changelog v1.1.0 header:
  ```markdown
  # Changelog

  All notable changes to this project will be documented in this file.

  The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
  and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
  ```

### New CHANGELOG.md Creation Template

When creating a CHANGELOG.md for a new project, use this complete template:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.1.0] - YYYY-MM-DD

### Added
- Initial project setup

[Unreleased]: https://github.com/user/repo/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/user/repo/releases/tag/v0.1.0
```

**Notes:**
- Pre-populate all 6 standard type headings under `## [Unreleased]` as empty sections
- Include an initial version entry with project setup
- Add comparison links at the bottom
- Replace `user/repo` with actual GitHub repository path

- **Requirement:** Group entries under Keep a Changelog standard types:
  - **Added** for new features
  - **Changed** for changes in existing functionality
  - **Deprecated** for soon-to-be removed features
  - **Removed** for now removed features
  - **Fixed** for any bug fixes
  - **Security** for vulnerability fixes (with CVE references when applicable)
- **Requirement:** Maintain exactly ONE instance of each category heading (Added, Changed, Deprecated, Removed, Fixed, Security) within each version section. Consolidate all entries of the same type under a single heading.
- **Requirement:** Each entry is a single line with human-readable summary.
- **Requirement:** Prefer feature-focused Conventional Commits style for entries: `**type(scope):** summary`
  - This is the PREFERRED format per [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification)
  - Conventional Commits enhances Keep a Changelog, not replaces it
  - Entries must remain human-readable and user-impact focused regardless of format
  - The summary after the prefix should describe the released feature, behavior, fix, or user-visible impact
  - Benefits: automated tooling, consistent patterns, semantic versioning alignment
- **Consider:** Add version comparison links at bottom of CHANGELOG.md:
  ```markdown
  [Unreleased]: https://github.com/user/repo/compare/v1.1.0...HEAD
  [1.1.0]: https://github.com/user/repo/compare/v1.0.0...v1.1.0
  ```
- **Always:** Security fixes must be prominent and clearly marked under **Security** type.
- **Always:** Deprecated features must include timeline or version when deprecation becomes removal.
- **Always:** Collapse iterative micro-fixes into one meaningful entry.
- **Consider (Optional):** Use consistent scope patterns when using Conventional Commits format:
  - Core: `core`, `governance`, `memory-bank`
  - Snowflake: `snowflake`, `sql`, `streamlit`, `spcs`
  - Python: `python`, `fastapi`, `lint`, `setup`, `cli`, `typer`, `pydantic`, `faker`, `flask`
  - Shell: `bash`, `zsh`, `shell`
  - Project: `changelog`, `readme`, `contributing`, `taskfile`
  - Analytics: `data-science`, `governance`, `business`

## Content Quality Guidelines

- **Requirement:** Summaries are concise and user-impact oriented; avoid duplicating commit body details.
- **Requirement:** Changelog entries are more product/user-facing than git commit messages. Use release-note language after the `**type(scope):**` prefix.
- **Requirement:** Git commit bodies may carry more developer-facing detail; do not copy that detail into CHANGELOG.md unless it changes user-visible behavior.
- **Requirement:** Do not include raw stack traces, personal names, or internal-only jargon.
- **Requirement:** Mark breaking changes with `!` in Conventional Commits format and explain them clearly.
- **CRITICAL:** Security vulnerabilities must use **Security** type and include CVE references when applicable.
- **CRITICAL:** Deprecated features must use **Deprecated** type and include removal timeline.
- **Always:** Link to relevant PRs or issues (`[#123]`) when helpful.

## Entry Consolidation Guidelines

### One Entry Per Version Bump

When a component (skill, package, module) receives a version bump, consolidate ALL related changes into a single changelog entry with sub-bullets:

- **Primary bullet:** `**type(scope):** vX.Y.Z — short summary`
- **Sub-bullets:** Notable specifics (features, files, breaking changes)

### Fold Related Change Types

When `feat()`, `docs()`, and `test()` changes all support the same feature, consolidate under the primary `feat()` entry rather than listing separately:

```markdown
# [BAD] - Separate entries for related changes
- **feat(auth):** add OAuth2 support
- **docs(auth):** add OAuth2 configuration guide
- **test(auth):** add OAuth2 integration tests

# [GOOD] - Consolidated
- **feat(auth):** add OAuth2 support with configuration guide and integration tests
```

### Pattern 6: Over-Collapsing Existing Entries

**Problem:**
Replacing multiple existing changelog bullets with one broad summary when the user asked only to restyle the entries.

**Why It Fails:**
- Deletes release-history signal
- Makes review harder because content changes are mixed with style changes
- Violates the preservation expectation for existing changelog concepts

**Correct Pattern:**
```markdown
# WRONG - Three concepts collapsed into one vague summary
### Changed
- **feat(report):** improve benchmark reporting.

# CORRECT - Same concepts preserved in conventional style
### Changed
- **feat(benchmark):** rename the Claude CoCo harness target to `claude-coco-plugin`.
- **feat(report):** standardize compact metric labels with accessible definitions.
- **feat(report):** apply brand-correct harness colors across charts, badges, and pills.
```

### Granularity Threshold

**Too granular (avoid):**
- Individual workflow files
- Individual test cases
- Per-function changes

**Appropriate granularity:**
- Version bumps with summary of notable changes
- Features with user-visible impact
- Breaking changes requiring migration

## Workflow and Maintenance

**Reference:** Pre-Task-Completion Validation Gate in `000-global-core.md` and `AGENTS.md`

**MUST:** CHANGELOG.md updates are required before task completion for all code changes.

- **MUST** append a new entry under `## [Unreleased]` before marking task complete after ANY code change.
- **MUST NOT** mark tasks complete without updating CHANGELOG.md for code changes.
- **MUST** finalize Unreleased on release, add the new version heading, and move entries.
- **Always:** Validate CHANGELOG structure with these deterministic checks:
  1. Verify `## [Unreleased]` heading exists: `grep -c '## \[Unreleased\]' CHANGELOG.md`
  2. Verify no duplicate category headings within version blocks
  3. Verify all entries are under standard Keep a Changelog types
  4. If `scripts/validate_changelog_structure.py` exists, also run it for comprehensive validation
- **Exception:** Only skip if user explicitly requests override (acknowledge that changelog will be incomplete).

### What Constitutes a Change Requiring Changelog Entry

- **MANDATORY:** Any modification to Python files (`.py`)
- **MANDATORY:** Any modification to SQL files (`.sql`)
- **MANDATORY:** Any modification to configuration files (`pyproject.toml`, `Taskfile.yml`, `Makefile`, etc.)
- **MANDATORY:** Any modification to shell scripts (`.sh`, `.bash`, `.zsh`)
- **MANDATORY:** Any modification to rule files (`.md` in `ai_coding_rules/`)
- **MANDATORY:** Any modification to documentation files (`README.md`, `CONTRIBUTING.md`)
- **Exception:** Changes to CHANGELOG.md itself — including format fixes, backfilling entries, or correcting typos — do not require a separate changelog entry. However, adding entries for other code changes remains mandatory per lines 360-368.
- **MANDATORY:** New features, bug fixes, refactors, or performance improvements
- **MANDATORY:** Documentation-only changes (no longer optional - ALWAYS update CHANGELOG.md)
- **Rationale:** Documentation changes are user-facing and must be tracked for complete audit trail

## Usage Examples and Patterns

### Example 1: New Features and Bug Fixes (Added/Fixed)

```markdown
## [Unreleased]
### Added
- **feat(cli):** add progress bars for long-running operations.
- **feat(cli):** support asynchronous Typer commands.

### Fixed
- **fix(cli):** handle keyboard interrupts cleanly.
- **fix(pydantic):** serialize nested models without data loss.
```

### Example 2: Security Vulnerabilities (Security)

```markdown
## [Unreleased]
### Security
- **fix(security):** prevent SQL injection in user input validation (CVE-2024-1234).
- **fix(auth):** patch authentication bypass in Flask middleware (CVE-2024-5678).
- **fix(deps):** update dependencies to address known vulnerabilities.
```

### Example 3: Feature-Focused Conventional Commits Style

```markdown
## [Unreleased]
### Added
- **feat(cli):** add progress bars for long-running operations.
- **feat(flask):** support application factories with blueprints.

### Fixed
- **fix(cli):** handle keyboard interrupts cleanly.
- **fix(pydantic):** serialize nested models without data loss.
```

## Monorepo Changelog Strategy

- **Root CHANGELOG.md:** Cross-cutting changes affecting the entire project (CI/CD, shared configs, meta-releases)
- **Per-package CHANGELOG.md:** Package-specific changes (e.g., `packages/core/CHANGELOG.md`)
- **Rule:** Update the changelog closest to the change. If a change spans packages, update root.
- **Tooling:** Use `changesets` or `lerna-changelog` for automated multi-package changelog management
- **Versioning:** Each package MAY have independent version numbers following SemVer

## Automated Changelog Tools

- **`conventional-changelog`** — Generates changelog from Conventional Commits history
- **`changesets`** — Monorepo changelog management with per-package versioning
- **`git-cliff`** — Highly configurable changelog generator using commit conventions
- **Note:** Automated tools supplement human-written summaries; MUST review generated entries for user-impact clarity

## Release Workflow

When releasing a new version, follow these exact steps to move entries from Unreleased to a versioned section:

### Step 1: Create Version Heading

```markdown
## [x.y.z] - YYYY-MM-DD
```

Replace `x.y.z` with the new version number and `YYYY-MM-DD` with the release date.

### Step 2: Move Entries

Move all entries from `## [Unreleased]` to the new version heading. Remove empty type headings
(e.g., if no `### Deprecated` entries exist, omit that heading from the release).

### Step 3: Reset Unreleased Section

Leave `## [Unreleased]` empty (or with empty type headings) for future entries.

### Step 4: Update Comparison Links

```markdown
[Unreleased]: https://github.com/user/repo/compare/vx.y.z...HEAD
[x.y.z]: https://github.com/user/repo/compare/vprevious...vx.y.z
```

### Example

Before release:
```markdown
## [Unreleased]
### Added
- New CLI progress bars
### Fixed
- Login failure with special characters
```

After release:
```markdown
## [Unreleased]

## [1.2.0] - 2026-03-09
### Added
- New CLI progress bars
### Fixed
- Login failure with special characters

[Unreleased]: https://github.com/user/repo/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/user/repo/compare/v1.1.0...v1.2.0
```
