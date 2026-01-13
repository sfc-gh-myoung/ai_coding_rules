# Changelog Governance Directives

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** CHANGELOG, changelog format, semantic versioning, release notes, conventional commits, Unreleased section, scope patterns, project governance, git workflow, version control
**TokenBudget:** ~3350
**ContextTier:** Medium
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Maintaining high-signal, audit-friendly CHANGELOG.md following Keep a Changelog standard with Conventional Commits format for consistent project change documentation.

**When to Load This Rule:**
- Modifying CHANGELOG.md directly
- Any code change requiring changelog entry
- Project releases (moving Unreleased to version)
- Implementing Conventional Commits workflow
- Setting up changelog standards for new projects
- Reviewing changelog compliance during pull requests

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates

**Related:**
- **801-project-readme.md** - README documentation standards
- **802-project-contributing.md** - Contributing guidelines and workflow
- **803-project-git-workflow.md** - Git workflow and branch management

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
- Use Keep a Changelog v1.1.0 standard types: Added, Changed, Deprecated, Removed, Fixed, Security
- Add entries under ## [Unreleased] section
- Ensure human-readable, user-impact focused summaries

### Forbidden

- Never add entries outside standard Keep a Changelog types
- Never skip CHANGELOG update for code changes
- Never use jargon or internal-only terminology
- Never duplicate full commit messages in changelog entries

### Execution Steps

1. Read CHANGELOG.md to check format, existing scopes, and structure
2. Identify change type: Added, Changed, Deprecated, Removed, Fixed, or Security
3. Write concise, human-readable summary focusing on user impact
4. Add entry under appropriate type heading in ## [Unreleased] section
5. Optionally use Conventional Commits format: type(scope): summary
6. Verify entry is not duplicate and follows existing patterns

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
- **CRITICAL:** Entry uses standard Keep a Changelog type (Added, Changed, Deprecated, Removed, Fixed, Security)
- **CRITICAL:** Summary is human-readable and user-impact focused
- **Format Check:** Entry matches existing format patterns in file
- **Duplication Check:** No duplicate entries exist

**Success Criteria:**
- CHANGELOG.md contains entry under `## [Unreleased]`
- Entry follows Conventional Commit format: `<type>(<scope>): <summary>`
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
5. **Validate Conventional Commits format** - Ensure `type(scope): summary`

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
- [ ] **CRITICAL:** Entry follows Conventional Commit format: `<type>(<scope>): <summary>`
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
# ❌ WRONG - Technical commit dump
## [Unreleased]
### Fixed
- refactor(auth): replace deprecated bcrypt.compare with bcrypt.verify in UserService.authenticate() method

# ✅ CORRECT - User-focused summary
## [Unreleased]
### Fixed
- Resolved login failures for users with special characters in passwords
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
- **Requirement:** Group entries under Keep a Changelog standard types:
  - **Added** for new features
  - **Changed** for changes in existing functionality
  - **Deprecated** for soon-to-be removed features
  - **Removed** for now removed features
  - **Fixed** for any bug fixes
  - **Security** for vulnerability fixes (with CVE references when applicable)
- **Requirement:** Each entry is a single line with human-readable summary.
- **Requirement:** Use Conventional Commit format for consistency: `type(scope): summary`
  - This is the PREFERRED format per [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification)
  - Conventional Commits enhances Keep a Changelog, not replaces it
  - Entries must remain human-readable and user-impact focused regardless of format
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
- **Requirement:** Do not include raw stack traces, personal names, or internal-only jargon.
- **Requirement:** Mark breaking changes with `!` in Conventional Commits format and explain them clearly.
- **CRITICAL:** Security vulnerabilities must use **Security** type and include CVE references when applicable.
- **CRITICAL:** Deprecated features must use **Deprecated** type and include removal timeline.
- **Always:** Link to relevant PRs or issues (`[#123]`) when helpful.

## Workflow and Maintenance

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

## Usage Examples and Patterns

### Example 1: New Features (Added)

```markdown
## [Unreleased]
### Added
- Progress bars for long-running CLI operations
- Async command support for Typer applications
- Comprehensive model validation patterns with Pydantic
- Application factory pattern with Flask blueprints
```

### Example 2: Bug Fixes (Fixed)

```markdown
## [Unreleased]
### Fixed
- Keyboard interrupt handling in CLI applications
- Pydantic serialization issues with nested models
- CSRF token validation in AJAX requests
```

### Example 3: Security Vulnerabilities (Security)

```markdown
## [Unreleased]
### Security
- Fixed SQL injection vulnerability in user input validation (CVE-2024-1234)
- Patched authentication bypass in Flask middleware (CVE-2024-5678)
- Updated dependencies to address known vulnerabilities
```

### Example 4: Deprecations (Deprecated)

```markdown
## [Unreleased]
### Deprecated
- Legacy API v1 endpoints will be removed in v4.0.0 (migrate to v2)
- Old configuration format deprecated, use YAML instead (removal in v5.0.0)
```

### Example 5: Breaking Changes (Removed)

```markdown
## [Unreleased]
### Removed
- Dropped Python 3.7 support (end of life reached)
- Removed deprecated `get_user()` function (use `fetch_user()` instead)
```

### Example 6: With Optional Conventional Commits Format

```markdown
## [Unreleased]
### Added
- feat(cli): progress bars for long-running operations
- feat(flask): application factory pattern with blueprints

### Fixed
- fix(cli): keyboard interrupt handling
- fix(pydantic): serialization issues with nested models
```
