# Contribution Workflow

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.2
**LastUpdated:** 2026-01-20
**LoadTrigger:** kw:contributing, file:CONTRIBUTING.md
**Keywords:** CONTRIBUTING, pull requests, code review, contribution guidelines, branching strategy, Conventional Commits, rule authoring, PR templates, project governance, git workflow
**TokenBudget:** ~1750
**ContextTier:** Medium
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Professional contribution workflow directives covering commits, pull requests, changelog discipline, and rule authoring standards to ensure consistent project collaboration and quality.

**When to Load This Rule:**
- Creating or reviewing CONTRIBUTING.md files
- Establishing contribution workflows
- Implementing Conventional Commits standards
- Defining PR and code review processes
- Setting up rule authoring guidelines

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **800-project-changelog.md** - Changelog management standards
- **801-project-readme.md** - README best practices
- **803-project-git-workflow.md** - Git workflow management
- **002-rule-governance.md** - Rule authoring standards

### External Documentation
- [GitHub Contributing Guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) - GitHub's guide for contribution workflows
- [Open Source Guides](https://opensource.guide/) - Best practices for open source project management
- [Conventional Commits](https://www.conventionalcommits.org/) - Standardized commit message format
- [CommonMark Spec](https://spec.commonmark.org/) - Authoritative Markdown specification (CONTRIBUTING.md MUST comply)

## Contract

### Inputs and Prerequisites
- Forked repository with feature branch
- Development environment set up (Python 3.11+, Task, uv, Ruff)
- Understanding of rule numbering scheme and governance standards
- Access to CONTRIBUTING.md and 002-rule-governance.md

### Mandatory
- MUST validate with `task rules:validate` before committing any rule changes
- MUST follow Conventional Commits format for all commit messages
- MUST create feature branch before committing (never commit directly to main)
- MUST update CHANGELOG.md under `## [Unreleased]` for user-facing changes
- MUST run `task lint` and `task format` before submitting PR

### Forbidden
- Direct editing of deployed rule files outside rules/ directory
- Committing without validation (task rules:validate)
- Force push to main/master branches
- Amending commits authored by others

### Execution Steps
1. Fork repository and create feature branch following naming conventions
2. Edit rules/ directory files directly (production-ready rules)
3. Follow Conventional Commits format for all commit messages
4. Update CHANGELOG.md under ## [Unreleased] for user-facing changes
5. Validate with task rules:validate and task lint
6. Submit PR with descriptive title and complete description
7. Address all code review feedback before merge

### Output Format
Well-structured pull request with:
- Conventional Commit title
- Clear description of changes and motivation
- Links to related issues
- Validation checklist completed
- Before/after examples (if applicable)

### Validation
**Pre-Task-Completion Checks:**
- CONTRIBUTING.md read before making changes
- Rule numbering scheme verified
- Tool availability checked in Taskfile.yml
- Conventional Commits format understood

**Success Criteria:**
- task rules:validate passes without critical errors
- task lint passes cleanly
- task format passes without changes
- CHANGELOG.md updated (if user-facing change)
- All commits follow Conventional Commits format
- Generated files included in PR (task rule:all run)

### Design Principles
- **Investigation-First** - Read CONTRIBUTING.md before making changes
- **Conventional Commits** - Standardized commit message format
- **Changelog Discipline** - Update CHANGELOG.md for user-facing changes
- **Validation-First** - Run validation before committing
- **Code Review** - Address all feedback before merge

### Post-Execution Checklist
- [ ] CONTRIBUTING.md read and understood
- [ ] Feature branch created with proper naming
- [ ] Development environment set up correctly
- [ ] Rule numbering scheme verified (if creating rules)
- [ ] Conventional Commits format used for all commits
- [ ] CHANGELOG.md updated under ## [Unreleased]
- [ ] Validation passed (task rules:validate, task lint)
- [ ] PR created with descriptive title and description
- [ ] All code review feedback addressed

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Editing Deployed Rules Without Validation
```bash
# Bad: Direct edit without validation
vim /some/project/.cursor/rules/100-snowflake-core.md
git add /some/project/.cursor/rules/100-snowflake-core.md
```
**Problem:** Changes to deployed rules should be made in source rules/ directory, not in deployment locations.

**Correct Pattern:**
```bash
# Good: Edit source rules
vim rules/100-snowflake-core.md
task rules:validate  # Validate changes
git add rules/100-snowflake-core.md
```
**Benefits:** Changes in canonical source location, validated before deployment

### Anti-Pattern 2: Vague Commit Messages
```bash
# Bad: No context or type
git commit -m "updated stuff"
git commit -m "WIP"
git commit -m "fixed bug"
```
**Problem:** Unclear change type, no scope, breaks changelog automation, unhelpful for code review

**Correct Pattern:**
```bash
# Good: Conventional Commits with clear scope
git commit -m "feat(snowflake): add Snowpipe continuous ingestion patterns"
git commit -m "fix(python): correct FastAPI async route examples"
git commit -m "docs(readme): update Quick Start with dual-platform git clone"
```
**Benefits:** Clear change type, automated changelog generation, searchable commit history

### Anti-Pattern 3: Skipping Validation
```bash
# Bad: Commit without validation
git add rules/<your-new-rule>.md
git commit -m "feat(rule): add new rule"
git push
```
**Problem:** May contain structural errors, invalid metadata, broken references, fails CI checks

**Correct Pattern:**
```bash
# Good: Validate before commit
vim rules/<your-new-rule>.md
task rules:validate  # Ensure compliance
task lint           # Check code quality
git add rules/<your-new-rule>.md
git commit -m "feat(rule): add new rule"
```
**Benefits:** Catch errors early, ensure governance compliance, pass CI checks

### Anti-Pattern 4: Mixing User and Contributor Content in README
```markdown
# Bad: Detailed development commands in README
```
**Problem:** README should focus on users, not development setup
**Correct Pattern:** Move development setup, build instructions, and contributor guidelines to CONTRIBUTING.md

## Output Format Examples

### Example 1: Conventional Commit Message
```
feat(python): add FastAPI async route patterns rule

- Add rule 210-python-fastapi-core.md with async best practices
- Include anti-patterns for sync-in-async mixing
- Reference existing Python rules (200, 201)

Closes #42
```

### Example 2: PR Description
```markdown
## Summary
Add Django framework patterns rule (215) covering models, views, ORM optimization,
and security guidelines (CSRF, XSS, SQL injection).

## Validation
- [x] `task rules:validate` passes
- [x] `task lint` passes
- [x] CHANGELOG.md updated under ## [Unreleased]
- [x] Follows 002-rule-governance.md v3.2 structure

Closes #123
```

### Example 3: Changelog Entry
```markdown
## [Unreleased]
### Added
- New rule 210-python-fastapi-core.md for FastAPI async patterns
### Fixed
- Corrected metadata schema references in 802-project-contributing.md
```
