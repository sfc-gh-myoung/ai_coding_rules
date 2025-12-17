# Example Git Workflow: Feature Development to Release

This document provides a complete example of the git workflow for developing a feature, preparing a release, and merging changes into release branches for multiple remotes.

## Scenario

- **Feature branch:** `feat/improve-rule-loading`
- **Release version:** v3.4.3
- **Remotes:**
  - `origin` — GitHub (primary)
  - `gitlab` — GitLab (secondary)

## Prerequisites

Ensure you have both remotes configured:

```bash
git remote -v
# Expected output:
# gitlab  git@snow.gitlab-dedicated.com:snowflakecorp/SE/sales-engineering/ai_coding_rules.git (fetch)
# gitlab  git@snow.gitlab-dedicated.com:snowflakecorp/SE/sales-engineering/ai_coding_rules.git (push)
# origin  git@github.com:sfc-gh-myoung/ai_coding_rules.git (fetch)
# origin  git@github.com:sfc-gh-myoung/ai_coding_rules.git (push)
```

## Phase 1: Feature Development

### 1.1 Create Feature Branch (Conventional Branch)

Following [Conventional Branch](https://conventional-branch.github.io/) guidelines:

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create feature branch using conventional naming
# Format: type/description-in-kebab-case
# Types: feature/, feat/, fix/, docs/, refactor/, chore/, test/
git checkout -b feat/improve-rule-loading
```

**Branch naming examples:**

| Type | Example | Use Case |
|------|---------|----------|
| `feat/` | `feat/improve-rule-loading` | New feature |
| `fix/` | `fix/schema-validation-errors` | Bug fix |
| `docs/` | `docs/update-architecture` | Documentation only |
| `refactor/` | `refactor/token-validator` | Code refactoring |
| `chore/` | `chore/update-dependencies` | Maintenance tasks |

### 1.2 Develop and Commit Changes

Make your changes following [Conventional Commits](https://www.conventionalcommits.org/):

```bash
# Make changes to files...
vim rules/000-global-core.md
vim rules/002e-agent-optimization.md

# Stage and commit with conventional commit message
git add rules/000-global-core.md rules/002e-agent-optimization.md
git commit -m "feat(rules): add priority hierarchy for agent-first authoring

- Added Rule Design Priorities section to 000-global-core.md
- Priority 1: Agent understanding and execution reliability
- Priority 2: Token and context window efficiency
- Priority 3: Human readability"

# Push feature branch to origin
git push -u origin feat/improve-rule-loading
```

### 1.3 Continue Development

Continue making commits as needed:

```bash
# Additional changes
git add RULES_INDEX.md
git commit -m "refactor(index): convert to structured list format

- Replaced ASCII tables with agent-friendly list format
- Groups rules by domain for easier navigation"

git push
```

## Phase 2: Release Preparation

### 2.1 Prepare Release Documentation

Before creating release branches, prepare version-specific documentation changes:

```bash
# Ensure you're on your feature branch with all changes committed
git checkout feat/improve-rule-loading
git status  # Should show clean working tree

# Make release documentation updates
# - Update version in pyproject.toml
# - Update version badge in README.md
# - Move CHANGELOG.md [Unreleased] to new version section
# - Update rule counts if changed
# - Add new features to documentation

# Example changes:
vim pyproject.toml          # version = "3.4.3"
vim README.md               # Update version badge, rule counts
vim CHANGELOG.md            # Move Unreleased to [3.4.3] - YYYY-MM-DD
vim docs/ARCHITECTURE.md    # Update rule counts, document history
vim CONTRIBUTING.md         # Update rule counts if needed
```

### 2.2 Stash Documentation Changes

Stash these changes to apply after squash merge:

```bash
git stash push -m "v3.4.3 release documentation updates"
```

### 2.3 Create Release Branches

Create release branches from each remote's main:

```bash
# Fetch latest from both remotes
git fetch origin
git fetch gitlab

# Create GitHub release branch
git checkout -b release/v3.4.3 origin/main

# Create GitLab release branch
git checkout -b release/v3.4.3-gitlab gitlab/main

# Verify branches exist
git branch -l | grep release/v3.4.3
# release/v3.4.3
# release/v3.4.3-gitlab
```

## Phase 3: Merge Feature into Release Branches

### 3.1 Merge into GitHub Release Branch

```bash
# Switch to GitHub release branch
git checkout release/v3.4.3

# Squash merge the feature branch
git merge --squash feat/improve-rule-loading

# Commit the squash merge
git commit -m "feat: improve rule loading with priority hierarchy and agent optimization

- Added Rule Design Priorities hierarchy to 000-global-core.md
- Added 002e-agent-optimization.md for agent-first authoring patterns
- Converted RULES_INDEX.md to structured list format
- Updated schema_validator.py with Priority 1 violation detection
- Added lazy loading strategy to AGENTS.md"

# Apply the stashed documentation changes
git stash apply

# Stage and commit documentation updates
git add README.md CONTRIBUTING.md docs/ARCHITECTURE.md CHANGELOG.md pyproject.toml
git commit -m "chore(release): prepare v3.4.3 release documentation

- Updated version to 3.4.3
- Updated rule count to 107
- Moved CHANGELOG Unreleased to [3.4.3]
- Added plan-reviewer skill documentation"

# Validate the release
task validate
```

### 3.2 Merge into GitLab Release Branch

```bash
# Switch to GitLab release branch
git checkout release/v3.4.3-gitlab

# Squash merge the feature branch
git merge --squash feat/improve-rule-loading

# Commit the squash merge
git commit -m "feat: improve rule loading with priority hierarchy and agent optimization

- Added Rule Design Priorities hierarchy to 000-global-core.md
- Added 002e-agent-optimization.md for agent-first authoring patterns
- Converted RULES_INDEX.md to structured list format
- Updated schema_validator.py with Priority 1 violation detection
- Added lazy loading strategy to AGENTS.md"

# Apply the stashed documentation changes (stash still available)
git stash apply

# Stage and commit documentation updates
git add README.md CONTRIBUTING.md docs/ARCHITECTURE.md CHANGELOG.md pyproject.toml
git commit -m "chore(release): prepare v3.4.3 release documentation

- Updated version to 3.4.3
- Updated rule count to 107
- Moved CHANGELOG Unreleased to [3.4.3]
- Added plan-reviewer skill documentation"

# Validate the release
task validate
```

### 3.3 Cleanup

```bash
# Drop the stash after both branches are done
git stash drop

# Return to feature branch or main
git checkout feat/improve-rule-loading
# or
git checkout main
```

## Phase 4: Push Release Branches (Optional)

When ready to publish:

```bash
# Push GitHub release branch
git push origin release/v3.4.3

# Push GitLab release branch
git push gitlab release/v3.4.3-gitlab
```

## Handling Merge Conflicts

If conflicts occur during squash merge:

```bash
# After git merge --squash shows conflicts
git status  # See conflicted files

# Resolve conflicts in each file
vim CHANGELOG.md  # Resolve conflicts, keep both changes appropriately

# Mark as resolved
git add CHANGELOG.md

# Continue with commit
git commit -m "feat: improve rule loading with priority hierarchy and agent optimization"
```

**Common conflict locations:**

- `CHANGELOG.md` — Multiple entries in same section
- `README.md` — Version badges, rule counts
- `RULES_INDEX.md` — Rule entries

## Quick Reference

### Branch Naming (Conventional Branch)

```
type/description-in-kebab-case

Examples:
  feat/improve-rule-loading
  fix/schema-validation-errors
  docs/update-architecture
  refactor/token-validator
  chore/update-dependencies
```

### Commit Messages (Conventional Commits)

```
type(scope): description

[optional body]

[optional footer]

Examples:
  feat(rules): add priority hierarchy for agent-first authoring
  fix(schema): correct validation for nested code blocks
  docs(readme): update installation instructions
  chore(release): prepare v3.4.3 release documentation
```

### Release Workflow Summary

```
1. git checkout -b feat/your-feature main
2. [develop, commit, push]
3. git stash push -m "release docs"
4. git checkout -b release/vX.Y.Z origin/main
5. git merge --squash feat/your-feature
6. git commit -m "feat: description"
7. git stash apply
8. git add . && git commit -m "chore(release): prepare vX.Y.Z"
9. task validate
10. [repeat for other remotes]
11. git stash drop
```

## Related Documentation

- [CONTRIBUTING.md](../CONTRIBUTING.md) — Development guidelines
- [rules/803-project-git-workflow.md](../rules/803-project-git-workflow.md) — Git workflow rules
- [Conventional Commits](https://www.conventionalcommits.org/) — Commit message standard
- [Conventional Branch](https://conventional-branch.github.io/) — Branch naming standard

