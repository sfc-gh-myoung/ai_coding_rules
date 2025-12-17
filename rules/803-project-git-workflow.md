# Git Workflow Management

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** git, workflow, branching strategy, GitHub, pull requests, feature branches, protected branches, git validation, branch naming, PR workflow, Conventional Commits
**TokenBudget:** ~5200
**ContextTier:** Medium
**Depends:** rules/800-project-changelog.md, rules/802-project-contributing.md

## Purpose
Establish comprehensive git workflow best practices for managing project updates on GitHub, ensuring consistent branching strategies, proper workflows, and robust validation before integration.

## Rule Scope
Git workflow management including branching strategies, pull requests, protected branches, and pre-merge validation for GitHub

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Feature branch workflow** - Create branch from main with proper naming
- **Conventional Commits REQUIRED** - `type(scope): description` per https://www.conventionalcommits.org/en/v1.0.0/#specification
- **Conventional Branch REQUIRED** - `type/description` per https://conventional-branch.github.io/#specification
- **Update CHANGELOG** - Add entries under ## [Unreleased]
- **Clean git state** - Validate before push (no uncommitted changes)
- **PR required** - Never commit directly to protected branches
- **Pre-merge validation** - Run all checks before creating PR
- **Never force push to main** - Breaks history for team
- **Pre-commit aware** - Request elevated permissions when hooks are configured

**Quick Checklist:**
- [ ] Feature branch created
- [ ] Conventional Commits used
- [ ] CHANGELOG.md updated
- [ ] Git state clean
- [ ] Validation checks passed
- [ ] Pre-commit hooks pass (or permissions granted)
- [ ] PR created with description
- [ ] CI checks passing

## Contract

<contract>
<inputs_prereqs>
Git repository initialized; remote configured on GitHub; understanding of Conventional Commits; access to Pre-Task-Completion Validation Gate requirements; awareness of pre-commit hooks and their permission requirements in sandboxed environments
</inputs_prereqs>

<mandatory>
Git commands (`git branch`, `git checkout`, `git commit`, `git push`, `git status`); GitHub CLI (`gh`); validation commands
</mandatory>

<forbidden>
Direct commits to protected branches without PR; force push to `main`/`master` without override; git commands that bypass validation
</forbidden>

<steps>
1. Create feature branch from `main` with proper naming convention
2. Make changes following project standards
3. Run Pre-Task-Completion Validation Gate checks
4. Update CHANGELOG.md under `## [Unreleased]`
5. Commit with Conventional Commits format
6. Validate git state (clean working directory, proper branch)
7. Push and create PR on GitHub
8. Await review and status checks before merge
</steps>

<output_format>
Clean git history with semantic commits; properly named branches; complete PR descriptions
</output_format>

<validation>
Git state validation passes; branch name follows convention; CHANGELOG.md updated; all status checks pass; code review approved
</validation>

<design_principles>
- **Feature Branch Workflow:** All changes go through feature branches and PR review
- **Protected Branches:** `main`/`master` branches require status checks and approvals
- **Conventional Commits:** All commits follow standardized format for automated changelog generation
- **Clean State:** No uncommitted changes before creating PR
- **Platform Agnostic:** Patterns work across different Git hosting platforms
- **Validation First:** All Pre-Task-Completion Validation Gate checks must pass before merge
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Committing Directly to Main**
```bash
git checkout main
# ... make changes ...
git commit -m "quick fix"
git push origin main # WRONG: Bypasses review and validation
```
**Problem:** Skips code review, status checks, and validation; breaks audit trail; can introduce bugs to production.

**Correct Pattern:**
```bash
git checkout main
git pull origin main
git checkout -b fix/critical-bug
# ... make changes ...
git commit -m "fix(core): resolve critical validation bug"
# Run Pre-Task-Completion Validation Gate
task validate  # Preferred (Taskfile-first). If no Taskfile targets exist, run tool commands directly.
git push origin fix/critical-bug
gh pr create --title "fix(core): resolve critical validation bug"
# Wait for review and merge
```
**Benefits:** Maintains code quality, enables peer review, preserves audit trail, catches issues before production.


**Anti-Pattern 2: Vague Branch Names**
```bash
git checkout -b fix-bug # Too vague
git checkout -b update # What update?
git checkout -b john-changes # No context
git checkout -b temp # Temporary what?
```
**Problem:** Unclear purpose; difficult to track work; hard to understand git history; confusion in PR lists.

**Correct Pattern:**
```bash
git checkout -b fix/changelog-validation-error
git checkout -b feature/add-cortex-search-patterns
git checkout -b docs/update-contributing-guidelines
git checkout -b refactor/split-large-streamlit-rule
```
**Benefits:** Clear purpose at a glance; easy to find related work; meaningful git history; self-documenting workflow.


**Anti-Pattern 3: Skipping CHANGELOG.md Updates**
```bash
git checkout -b feature/new-rule
# ... create new rule file ...
git commit -m "feat(rules): add new rule"
git push origin feature/new-rule
gh pr create # WRONG: No CHANGELOG entry
```
**Problem:** Changes not documented; users unaware of new features; incomplete audit trail; breaks governance.

**Correct Pattern:**
```bash
git checkout -b feature/new-rule
# ... create new rule file ...

# Update CHANGELOG.md under ## [Unreleased]
cat >> CHANGELOG.md << 'EOF'

### Added
- **feat(rules):** Added Rule XXX: New Feature (~Y00 tokens)
 - Description of new feature
 - Key capabilities and benefits
EOF

git add .
git commit -m "feat(rules): add new rule with comprehensive examples"
# Verify CHANGELOG entry
grep -A 5 "## \[Unreleased\]" CHANGELOG.md
git push origin feature/new-rule
gh pr create
```
**Benefits:** Complete documentation; users know what changed; audit trail maintained; governance compliance.


**Anti-Pattern 4: Creating PR with Uncommitted Changes**
```bash
# ... make changes to multiple files ...
git add some-file.md
git commit -m "feat(rules): partial work"
# ... more changes not committed ...
git push origin feature/my-work
gh pr create # WRONG: Uncommitted changes in working directory
```
**Problem:** PR doesn't reflect actual local state; reviewers see incomplete work; risk of losing uncommitted changes.

**Correct Pattern:**
```bash
# ... make changes to multiple files ...
git status # Check what changed
git add . # Stage all changes
git commit -m "feat(rules): add comprehensive git workflow patterns"

# Validate clean state
git status --porcelain # Should be empty
if [[ -n $(git status --porcelain) ]]; then
 echo "Uncommitted changes detected!"
 exit 1
fi

git push origin feature/my-work
gh pr create
```
**Benefits:** PR reflects exact state; reviewers see complete work; no risk of data loss; clean git history.


**Anti-Pattern 5: Force Pushing to Main**
```bash
git checkout main
git reset --hard HEAD~3 # Rewind commits
git push --force origin main # WRONG: Destroys history
```
**Problem:** Destroys commit history; breaks other developers' clones; can cause data loss; violates protected branch rules.

**Correct Pattern:**
```bash
# If you need to revert changes on main, use revert:
git checkout main
git revert HEAD~2..HEAD # Creates new commits that undo changes
git push origin main

# Or create hotfix branch:
git checkout main
git checkout -b fix/revert-problematic-change
git revert <commit-hash>
git push origin fix/revert-problematic-change
gh pr create --title "fix: revert problematic change"
# Merge after review
```
**Benefits:** Preserves history; allows rollback; follows review process; maintains team workflow.


**Anti-Pattern 6: Ignoring Pre-Commit Hook Failures**
```bash
git commit -m "feat: new feature"
# Error: PermissionError: [Errno 1] Operation not permitted
# (pre-commit hook failed due to sandbox restrictions)

git commit --no-verify -m "feat: new feature"  # WRONG: Blindly bypasses all checks
git push origin feature/my-branch
```
**Problem:** Bypassing hooks without verification skips important quality checks; may introduce linting errors, formatting issues, or security vulnerabilities; breaks team quality standards.

**Correct Pattern:**
```bash
git commit -m "feat: new feature"
# Error: PermissionError from pre-commit (sandbox restriction)

# Solution 1: Request elevated permissions and retry (preferred)
# For AI agents: use required_permissions: ['all'] or ['git_write']
git commit -m "feat: new feature"  # With proper permissions granted

# Solution 2: If permissions unavailable, verify checks passed first
task validate  # Preferred (Taskfile-first). If no Taskfile targets exist, run tool commands directly.
# Only after ALL checks pass manually:
git commit --no-verify -m "feat: new feature"
# Document why --no-verify was used in PR description
```
**Benefits:** Maintains code quality; hooks run as intended; catches issues before push; provides audit trail when bypass is necessary.

## Conventional Commits Specification Compliance

**Strong Preference:** All commits should follow [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification) as the preferred standard.

### Commit Message Structure

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Required Types
- `feat:` - New feature (correlates with MINOR in SemVer)
- `fix:` - Bug fix (correlates with PATCH in SemVer)

### Optional Types (Recommended)
- `docs:` - Documentation only changes
- `style:` - Formatting, missing semicolons, etc (no code change)
- `refactor:` - Code change that neither fixes bug nor adds feature
- `perf:` - Performance improvements
- `test:` - Adding or correcting tests
- `build:` - Build system or external dependency changes
- `ci:` - CI configuration changes
- `chore:` - Maintenance tasks

### Breaking Changes
Must be indicated by:
1. Appending `!` after type: `feat!: remove deprecated API`
2. Footer: `BREAKING CHANGE: description of what broke`

### Examples
```bash
# Feature with scope
git commit -m "feat(snowflake): add clustering optimization patterns"

# Bug fix
git commit -m "fix(validation): resolve schema parsing error"

# Breaking change with !
git commit -m "feat(python)!: require Python 3.11+ for type hints"

# Breaking change with footer
git commit -m "refactor(api): simplify authentication flow

BREAKING CHANGE: Auth tokens now use JWT format. Previous tokens are invalid."

# Documentation
git commit -m "docs(readme): update installation instructions"
```

### AI Agent Guidance Protocol

Agents should follow this validation approach:

1. **Strongly recommended:** Verify commit message matches pattern: `^(feat|fix|docs|style|refactor|perf|test|build|ci|chore)(\(.+\))?!?: .+`
2. **Preferred:** Ensure description is lowercase and concise
3. **Best practice:** Validate scope matches project patterns (check existing commits)
4. **Required for breaking changes:** Verify `!` or `BREAKING CHANGE:` footer present
5. **When deviating:** Document reason for non-standard format in commit body

**Flexibility:** If user explicitly requests different format or context requires deviation, document the reason and proceed.

## Conventional Branch Specification Compliance

**Strong Preference:** All feature branches should follow [Conventional Branch v1.0.0](https://conventional-branch.github.io/#specification) as the preferred standard.

### Branch Name Structure

```
<type>/<description-in-kebab-case>
```

### Required Format Rules
1. Use lowercase letters (a-z), numbers (0-9), hyphens (-) only
2. No consecutive hyphens (no `--`)
3. No leading or trailing hyphens
4. No spaces or special characters
5. Keep descriptions clear and concise (3-5 words ideal)

### Supported Types
- `feature/` (or `feat/`) - New features
- `fix/` (or `bugfix/` or `hotfix/`) - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `chore/` - Maintenance tasks

### Examples
```bash
# Valid branch names
git checkout -b feature/add-cortex-search-patterns
git checkout -b fix/changelog-validation-error
git checkout -b docs/update-contributing-guide
git checkout -b refactor/split-large-rule-file
git checkout -b chore/update-dependencies

# With ticket numbers (optional)
git checkout -b feature/SF-123-add-cortex-agents
git checkout -b fix/GH-456-resolve-validation-bug

# Invalid branch names (violations)
git checkout -b myFeature  # Missing type prefix
git checkout -b feature/Add New Feature  # Uppercase and spaces
git checkout -b fix--bug  # Consecutive hyphens
git checkout -b update  # No type prefix, vague
```

### AI Agent Guidance Protocol

Agents should follow this validation approach:

1. **Strongly recommended:** Verify branch name matches pattern: `^(feature|feat|fix|bugfix|hotfix|docs|refactor|chore)/[a-z0-9]+(-[a-z0-9]+)*$`
2. **Preferred:** Ensure no uppercase letters or special characters
3. **Best practice:** Validate description is kebab-case
4. **Quality check:** Ensure description is meaningful (not just "update" or "fix")
5. **When deviating:** Suggest conventional format but allow user override with justification

**Flexibility:** If project conventions differ or user has specific naming requirements, adapt while documenting the rationale.

## Post-Execution Checklist

- [ ] Branch created with proper naming convention (feature/, fix/, docs/, refactor/, chore/)
- [ ] Branch created from up-to-date `main` branch
- [ ] All Pre-Task-Completion Validation Gate checks pass (lint, format, tests)
- [ ] CHANGELOG.md updated under `## [Unreleased]` section
- [ ] README.md reviewed and updated if triggers apply
- [ ] All changes committed with Conventional Commits format
- [ ] Pre-commit hooks pass (or elevated permissions granted for sandboxed environments)
- [ ] Git state validated: `git status --porcelain` returns empty
- [ ] Not on protected branch (main/master)
- [ ] Branch pushed to remote successfully
- [ ] PR created with clear title and description
- [ ] Reviewers assigned (if multi-user project)
- [ ] All status checks passing before merge
- [ ] Code review approved before merge

## Validation

- **Success Checks:** Branch name follows convention; git working directory clean (`git status --porcelain` empty); CHANGELOG.md has entry under [Unreleased]; PR created successfully; all status checks pass; code review approved; merge completes without conflicts
- **Negative Tests:** Invalid branch name rejected by validation script; uncommitted changes block PR creation; missing CHANGELOG entry causes validation failure; direct commit to main blocked by branch protection; force push to main rejected; status check failures prevent merge

> **Investigation Required**
> When applying this rule:
> 1. **Verify git repository state BEFORE making recommendations** using `git status`, `git branch`, `git log`
> 2. **Check actual branch protection settings** on GitHub before advising
> 3. **Never assume branch names or git state** - always inspect with git commands
> 4. **If uncertain about remote configuration, explicitly state:** "I need to check your GitHub settings to provide accurate guidance"
> 5. **Make grounded recommendations based on actual git state inspection**
>
> **Anti-Pattern:**
> "Based on typical patterns, you probably have feature branches..."
> "Usually projects configure branch protection..."
>
> **Correct Pattern:**
> "Let me check your git state first:"
> ```bash
> git branch -a
> git remote -v
> git status
> ```
> "After reviewing your git configuration, I found [specific facts]. Here's my recommendation..."

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

## References

### External Documentation
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow) - GitHub's lightweight branch-based workflow
- [Git Branching Strategies](https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows) - Official Git documentation on branching
- [Protected Branches (GitHub)](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches) - GitHub branch protection configuration
- [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification) - REQUIRED commit message format specification
- [Conventional Branch v1.0.0](https://conventional-branch.github.io/#specification) - REQUIRED branch naming convention specification
- [GitHub CLI](https://cli.github.com/manual/) - GitHub command-line tool documentation

### Related Rules
- **Human Developer Guidelines**: `CONTRIBUTING.md` (lines 400-449)
- **Changelog Management**: `rules/800-project-changelog.md`
- **Contributing Workflow**: `rules/802-project-contributing.md`
- **Global Core (Pre-Task-Completion Validation Gate)**: `rules/000-global-core.md`
- **Agents Workflow**: `AGENTS.md`

## 1. Branch Naming Conventions

**Specification:** This project strongly follows [Conventional Branch v1.0.0](https://conventional-branch.github.io/#specification) for all branch naming.

**Core Principle:** Branch names should use the format `type/description-in-kebab-case` where type indicates the purpose and description is concise yet meaningful.

### Standard Prefixes

**Requirement:** All feature branches must use one of these prefixes:

- **`feature/`** - New features, enhancements, or rule additions
 - Example: `feature/add-snowflake-clustering-rule`
 - Example: `feature/semantic-keyword-discovery`

- **`fix/`** - Bug fixes, error corrections
 - Example: `fix/changelog-validation-script`
 - Example: `fix/broken-cross-references`

- **`docs/`** - Documentation-only changes
 - Example: `docs/update-readme-setup-section`
 - Example: `docs/clarify-contribution-workflow`

- **`refactor/`** - Code restructuring without behavior changes
 - Example: `refactor/split-streamlit-rule`
 - Example: `refactor/consolidate-sql-patterns`

- **`chore/`** - Maintenance tasks, dependency updates, tooling
 - Example: `chore/update-ruff-version`
 - Example: `chore/cleanup-temp-files`

### Branch Naming Best Practices

- **Rule:** Use descriptive, kebab-case names after prefix
- **Rule:** Keep branch names concise but meaningful (3-5 words)
- **Avoid:** Generic names like `fix-bug`, `update`, `changes`
- **Avoid:** JIRA ticket numbers only (include description)
- **Consider:** Including ticket reference: `feature/SF-123-add-cortex-agents`

## 2. Feature Branch Workflow

### Step-by-Step Process

```bash
# 1. Ensure main is up to date
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/my-new-feature

# 3. Make changes following project standards
# ... edit files ...

# 4. Run Pre-Task-Completion Validation Gate
task validate  # Preferred (Taskfile-first). If no Taskfile targets exist, run tool commands directly.
# ... fix any failures ...

# 5. Update CHANGELOG.md under ## [Unreleased]
# ... add entry ...

# 6. Stage and commit with Conventional Commits
git add .
git commit -m "feat(rules): add git workflow management best practices"

# 7. Validate git state
git status --porcelain # Should be empty
git rev-parse --abbrev-ref HEAD # Should show feature/my-new-feature

# 8. Push to remote
git push origin feature/my-new-feature

# 9. Create PR (see section below)
```

## 3. GitHub Workflow

### Creating Pull Requests

**Using GitHub CLI:**
```bash
# Create PR with title and body
gh pr create --title "feat(rules): add git workflow management" \
 --body "Adds comprehensive git workflow patterns..."

# Create draft PR for work in progress
gh pr create --draft --title "feat(rules): add git workflow management"

# Create PR and auto-fill from commits
gh pr create --fill
```

**Using GitHub Web UI:**
1. Navigate to repository on GitHub
2. Click "Pull requests", then click "New pull request"
3. Select base: `main`, compare: `feature/my-new-feature`
4. Fill in title (Conventional Commits format)
5. Add description explaining changes
6. Assign reviewers if applicable
7. Click "Create pull request"

### Branch Protection Rules (GitHub)

**Requirement:** Configure protection for `main` branch:

```yaml
# Repository Settings > Branches > Branch protection rules
Branch name pattern: main

Protection settings:
 Require a pull request before merging
 Require approvals: 1
 Dismiss stale pull request approvals when new commits are pushed
 Require status checks to pass before merging
 Require branches to be up to date before merging
 Status checks: lint, test, format
 Require conversation resolution before merging
 Do not allow bypassing the above settings
 Allow force pushes (keep disabled)
 Allow deletions (keep disabled)
```

### GitHub Actions Status Checks

**Example `.github/workflows/validate.yml`:**
```yaml
name: Validation

on:
 pull_request:
 branches: [ main ]

jobs:
 validate:
  runs-on: ubuntu-latest
  steps:
   - uses: actions/checkout@v3
   # Ensure Task is installed/available in CI (project standard), then run the gate:
   - name: Validate (Taskfile-first)
     run: task validate
```

## 4. Protected Branch Strategy

### Configuration Requirements

**Mandatory for all projects:**
- **Always:** Protect `main` and `master` branches
- **Always:** Require pull request for changes
- **Always:** Require at least 1 approval for merges
- **Always:** Require status checks to pass before merging
- **Always:** Require all conversations resolved
- **Forbidden:** Direct commits to `main`/`master`
- **Forbidden:** Force pushes to protected branches (except emergency override with team notification)

### Branch Protection Benefits

- **Code Quality:** Automated checks catch issues before merge
- **Review Process:** Ensures peer review of all changes
- **Audit Trail:** Complete history of who approved what
- **Rollback Safety:** Easy to revert problematic merges
- **Team Collaboration:** Forces communication about changes

## 5. Pre-Merge Validation

### Git State Validation Commands

**Requirement:** Run these checks before creating PR:

```bash
# 1. Check for uncommitted changes (must be empty)
git status --porcelain

# Expected output: (empty)
# If not empty, commit or stash changes

# 2. Validate branch name format
BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo $BRANCH | grep -E "^(feature|fix|docs|refactor|chore)/"

# Expected: feature/my-new-feature
# Must match convention

# 3. Verify not on protected branch
BRANCH=$(git branch --show-current)
[[ "$BRANCH" != "main" && "$BRANCH" != "master" ]]

# Expected: exit code 0 (success)
# Should NOT be on main/master

# 4. Verify CHANGELOG.md has entry in [Unreleased]
grep -A 10 "## \[Unreleased\]" CHANGELOG.md | grep -v "^## \[Unreleased\]$" | grep -q .

# Expected: finds content after [Unreleased]
# Entry must be present
```

### Complete Validation Script

**Create `scripts/validate-git-state.sh`:**
```bash
#!/bin/bash
set -euo pipefail

echo " Validating git state..."

# Check for uncommitted changes
if [[ -n $(git status --porcelain) ]]; then
 echo "Uncommitted changes detected. Commit or stash before creating PR."
 git status --short
 exit 1
fi
echo "Working directory clean"

# Validate branch name
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if ! echo "$BRANCH" | grep -qE "^(feature|fix|docs|refactor|chore)/"; then
 echo "Invalid branch name: $BRANCH"
 echo " Must match: feature/*, fix/*, docs/*, refactor/*, chore/*"
 exit 1
fi
echo "Branch name valid: $BRANCH"

# Check not on protected branch
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
 echo "Cannot create PR from protected branch: $BRANCH"
 exit 1
fi
echo "Not on protected branch"

# Verify CHANGELOG.md entry
if ! grep -A 10 "## \[Unreleased\]" CHANGELOG.md | grep -v "^## \[Unreleased\]$" | grep -q .; then
 echo "No entry found in CHANGELOG.md under [Unreleased]"
 exit 1
fi
echo "CHANGELOG.md updated"

# Check for pre-commit hooks (warning only)
if [[ -f ".pre-commit-config.yaml" ]]; then
 echo "Pre-commit hooks configured (.pre-commit-config.yaml found)"
 echo "  Note: git commit may require elevated permissions in sandboxed environments"
fi
if [[ -d ".husky" ]]; then
 echo "Husky hooks configured (.husky/ directory found)"
fi

echo ""
echo " Git state validation passed!"
echo "Ready to create PR for branch: $BRANCH"
```

**Usage:**
```bash
# Make script executable
chmod +x scripts/validate-git-state.sh

# Run before creating PR
./scripts/validate-git-state.sh
```

### Integration with Pre-Task-Completion Validation Gate

**Reference:** See `AGENTS.md` Section 3.4: Git State Validation

**Requirement:** Git state validation is part of mandatory Pre-Task-Completion Validation Gate:

1. Project validation (preferred): `task validate` (or `task check` / `task ci`)
2. Fallback validation (if no Taskfile targets exist): run tool commands directly.
3. Documentation: CHANGELOG.md and README.md updated
4. **Git State:** Clean working directory, valid branch, CHANGELOG entry verified

## 6. Pre-Commit Hooks

### Understanding Pre-Commit Hooks

**Context:** Many projects use pre-commit hooks to enforce code quality checks automatically before commits. These hooks run on every `git commit` command.

**Common pre-commit frameworks:**
- **pre-commit** (Python-based) - Uses `.pre-commit-config.yaml`
- **husky** (Node.js-based) - Uses `.husky/` directory
- **Native git hooks** - Scripts in `.git/hooks/`

### Permission Requirements

**Critical:** Pre-commit hooks often require elevated permissions beyond basic file access:

**Permission Requirements:**
- **Network access** - Download/update hook tools (e.g., pre-commit autoupdate)
- **System calls** - Access system configuration (e.g., os.sysconf)
- **Cache directories** - Store downloaded tools (~/.cache/pre-commit)
- **Process spawning** - Run linters, formatters (ruff, black, eslint)

**AI Agent Consideration:** When running `git commit` in sandboxed environments, pre-commit hooks may fail with permission errors:
```
PermissionError: [Errno 1] Operation not permitted
```

### Handling Pre-Commit Hook Failures

**Pattern 1: Request Full Permissions (Preferred)**
```bash
# When pre-commit hooks are configured, git commit needs elevated permissions
# AI agents should request 'all' or 'git_write' permissions
git commit -m "feat(scope): description"
# If fails with PermissionError, retry with full sandbox bypass
```

**Pattern 2: Run Pre-Commit Manually First**
```bash
# Run pre-commit checks separately with proper permissions
pre-commit run --all-files

# Then commit (hooks will pass quickly on cached results)
git commit -m "feat(scope): description"
```

**Pattern 3: Skip Hooks Temporarily (Emergency Only)**
```bash
# ONLY use when:
# 1. All quality checks have already passed manually
# 2. Permission issues block commit in sandboxed environment
# 3. You understand the risks

git commit --no-verify -m "feat(scope): description"
# WARNING: This bypasses ALL pre-commit checks
# Must ensure quality checks passed before using this option
```

### Detecting Pre-Commit Configuration

```bash
# Check if pre-commit is configured
if [[ -f ".pre-commit-config.yaml" ]]; then
    echo "Pre-commit hooks configured - elevated permissions may be required"
fi

# Check for husky
if [[ -d ".husky" ]]; then
    echo "Husky hooks configured - Node.js environment required"
fi

# Check for native git hooks
if [[ -d ".git/hooks" ]] && ls .git/hooks/* 2>/dev/null | grep -qv sample; then
    echo "Native git hooks present"
fi
```

## Git Workflow Analysis
- **Current Branch:** [branch name from `git branch --show-current`]
- **Git State:** [clean/uncommitted changes]
- **Remote:** GitHub
- **Protected Branches:** [list from repo settings]

## Recommendation
[Specific workflow steps based on actual state]

## Commands to Execute
```bash
# Step 1: Create feature branch
git checkout -b [branch-name]

# Step 2: Make changes and validate
# ... your changes ...
uvx ruff check . && uvx ruff format --check . && uv run pytest

# Step 3: Commit with Conventional Commits
git add .
git commit -m "[type]([scope]): [description]"

# Step 4: Validate git state
./scripts/validate-git-state.sh

# Step 5: Push and create PR/MR
git push origin [branch-name]
gh pr create --title "[PR title]" # or glab mr create
```

## Implementation Details

### Validation Checklist
- [ ] Pre-Task-Completion Validation Gate passed
- [ ] CHANGELOG.md updated
- [ ] Git state clean
- [ ] Branch name valid
```
