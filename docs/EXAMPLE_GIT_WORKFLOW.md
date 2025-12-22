# Example Git Workflow: Feature Development to Release

This document provides a complete example of the git workflow for developing a feature, preparing a release, and merging changes into release branches for multiple remotes.

## Scenario

- **Feature branch:** `feat/improve-rule-loading`
- **Release version:** v3.4.3
- **Remotes:**
  - `origin` — GitHub (primary)
  - `gitlab` — GitLab (secondary, protected `main` branch)

## Important Notes

- **GitHub** (`origin`) is the primary repository where development occurs
- **GitLab** (`gitlab`) mirrors releases from GitHub
- **GitLab's `main` branch is protected** — direct pushes are not allowed; changes must go through a Merge Request
- Due to diverged histories between GitHub and GitLab, special handling is required when syncing releases

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

### 2.3 Create GitHub Release Branch

Create the release branch from GitHub's main:

```bash
# Fetch latest from origin
git fetch origin

# Create GitHub release branch
git checkout -b release/v3.4.3 origin/main
```

> **Note:** The GitLab release branch is created later in Phase 4, after the GitHub release is complete and pushed. This ensures `origin/main` contains the final release before syncing to GitLab.

## Phase 3: Merge Feature into Release Branches

### 3.1 Squash Merge into GitHub Release Branch

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

### 3.2 Squash Merge into Main and Tag (GitHub)

After the feature is merged into the release branch:

```bash
# Switch to main
git checkout main

# Squash merge the release branch into main
git merge --squash release/v3.4.3

# Commit with conventional commit message
git commit -m "feat(release): v3.4.3 - rule loading improvements and agent optimization

SUMMARY:
- Rule Design Priorities hierarchy for agent-first authoring
- Agent optimization patterns (002e-agent-optimization.md)
- RULES_INDEX.md converted to structured list format
- Schema validator Priority 1 violation detection
- Lazy loading strategy in AGENTS.md
- Plan-reviewer skill added (107 total rules)"

# Create annotated tag
git tag -a v3.4.3 -m "chore: release v3.4.3"

# Push main and tag to GitHub
git push origin main --tags
```

### 3.3 Cleanup Stash

```bash
# Drop the stash after GitHub release is complete
git stash drop

# Verify stash is empty (or only has unrelated stashes)
git stash list
```

## Phase 4: Sync Release to GitLab (Protected Branch Workflow)

GitLab's `main` branch is protected and requires a Merge Request. Since the histories between GitHub and GitLab have diverged, we need to:

1. Create a release branch based on `gitlab/main`
2. Squash merge `origin/main` (GitHub) into it
3. Resolve conflicts by accepting GitHub's version
4. Push the branch and create a Merge Request

### 4.1 Create GitLab Release Branch

```bash
# Fetch latest from GitLab
git fetch gitlab

# Create release branch from gitlab/main
git checkout -b release/v3.4.3-gitlab gitlab/main
```

### 4.2 Squash Merge GitHub Changes

```bash
# Squash merge origin/main (GitHub v3.4.3) with unrelated histories flag
git merge --squash origin/main --allow-unrelated-histories

# This will likely show many conflicts due to diverged histories
# Resolve ALL conflicts by accepting GitHub's version (theirs)
git checkout --theirs .
git add .

# Commit the squash merge
git commit -m "feat(release): v3.4.3 - rule loading improvements and agent optimization

SUMMARY:
- Rule Design Priorities hierarchy for agent-first authoring
- Agent optimization patterns (002e-agent-optimization.md)
- RULES_INDEX.md converted to structured list format
- Schema validator Priority 1 violation detection
- Lazy loading strategy in AGENTS.md
- Plan-reviewer skill added (107 total rules)

Squash merge of origin/main (GitHub v3.4.3)"
```

### 4.3 Push and Create Merge Request

```bash
# Push to GitLab (use --force if branch already exists from previous attempt)
git push gitlab release/v3.4.3-gitlab --force

# GitLab will provide a URL to create the Merge Request
# Example output:
# remote: To create a merge request for release/v3.4.3-gitlab, visit:
# remote:   https://snow.gitlab-dedicated.com/.../merge_requests/new?...
```

Then in GitLab UI:
1. Open the Merge Request URL
2. Set target branch to `main`
3. Review the changes (should show single squash commit)
4. Submit for approval and merge

### 4.4 Return to Working Branch

```bash
# Return to main (tracks origin/main by default)
git checkout main
git pull origin main

# Or start your next feature branch
git checkout -b feat/your-next-feature
```

## Handling Merge Conflicts

### Standard Conflicts (Same History)

If conflicts occur during squash merge within the same remote:

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

### Diverged History Conflicts (GitHub to GitLab)

When merging from GitHub to GitLab with diverged histories, you'll see many `CONFLICT (add/add)` errors. Since GitHub is the authoritative source:

```bash
# Accept ALL changes from GitHub (theirs = origin/main)
git checkout --theirs .
git add .

# Then commit
git commit -m "feat(release): vX.Y.Z - description

Squash merge of origin/main (GitHub vX.Y.Z)"
```

**Why `--theirs`?** In a squash merge with `--allow-unrelated-histories`, "theirs" refers to the branch being merged in (`origin/main`), which contains the authoritative GitHub release.

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

**GitHub Release (Primary):**

```
1. git checkout -b feat/your-feature main
2. [develop, commit, push to origin]
3. git stash push -u -m "release docs"
4. git checkout -b release/vX.Y.Z origin/main
5. git merge --squash feat/your-feature
6. git commit -m "feat: description"
7. git stash apply && git add . && git commit -m "chore(release): prepare vX.Y.Z"
8. task validate
9. git checkout main && git merge --squash release/vX.Y.Z
10. git commit -m "feat(release): vX.Y.Z - description"
11. git tag -a vX.Y.Z -m "chore: release vX.Y.Z"
12. git push origin main --tags
13. git stash drop
```

**GitLab Sync (Protected Branch):**

```
14. git fetch gitlab
15. git checkout -b release/vX.Y.Z-gitlab gitlab/main
16. git merge --squash origin/main --allow-unrelated-histories
17. git checkout --theirs . && git add .
18. git commit -m "feat(release): vX.Y.Z - description (squash merge from GitHub)"
19. git push gitlab release/vX.Y.Z-gitlab --force
20. [Create Merge Request in GitLab UI: release/vX.Y.Z-gitlab → main]
```

## Related Documentation

- [CONTRIBUTING.md](../CONTRIBUTING.md) — Development guidelines
- [rules/803-project-git-workflow.md](../rules/803-project-git-workflow.md) — Git workflow rules
- [Conventional Commits](https://www.conventionalcommits.org/) — Commit message standard
- [Conventional Branch](https://conventional-branch.github.io/) — Branch naming standard

