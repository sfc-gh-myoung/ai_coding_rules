# Git Workflow Management

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.5.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:git, kw:commit, kw:workflow
**Keywords:** git, commit, commit message, workflow, branching, GitHub, pull requests, feature branches, Conventional Commits, branch naming
**TokenBudget:** ~2300
**ContextTier:** Medium
**Depends:** 800-project-changelog.md, 802-project-contributing.md

## Scope

**What This Rule Covers:**
Git workflow best practices including commit formatting, branching strategies, PR workflows, and validation.

**When to Load:**
- Writing/formatting git commits
- Using Conventional Commits format
- Setting up branching strategies or PR processes

## References

### Dependencies

**Must Load First:**
- **800-project-changelog.md** - Changelog management
- **802-project-contributing.md** - Contribution workflow

**Related:**
- **000-global-core.md** - Pre-Task-Completion Validation Gate
- **AGENTS.md** - Agent workflow integration

### External Documentation
- [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/#specification)
- [Conventional Branch v1.0.0](https://conventional-branch.github.io/#specification)
- [GitHub Flow](https://docs.github.com/en/get-started/quickstart/github-flow)

## Contract

### Inputs and Prerequisites
- Git repository initialized with remote on GitHub
- Understanding of Conventional Commits
- Awareness of pre-commit hooks in sandboxed environments

### Mandatory
- MUST create feature branches from main/develop — never commit directly to protected branches
- Each commit MUST be atomic — one logical change per commit
- Branch names MUST follow `type/description` format (e.g., `feature/add-login`, `fix/null-pointer`)
- MUST use Conventional Commits format for all commit messages
- MUST update CHANGELOG.md under `## [Unreleased]` for user-facing changes
- MUST run Pre-Task-Completion Validation Gate checks before pushing

### Forbidden
- Direct commits to protected branches without PR
- Force push to `main`/`master` without override
- Git commands that bypass validation

### Execution Steps
1. Create feature branch from `main` with proper naming
2. Make changes following project standards
3. Run Pre-Task-Completion Validation Gate checks
4. Update CHANGELOG.md under `## [Unreleased]`
5. Commit with Conventional Commits format
6. Validate git state (clean directory, proper branch)
7. Push and create PR on GitHub

### Output Format
Clean git history with semantic commits; properly named branches; complete PR descriptions

### Validation
**Pre-Task-Completion Checks:** Git state verified, branch protection checked, validation commands available

**Success Criteria:** Git state passes, branch follows convention, CHANGELOG updated, status checks pass

### Design Principles
- **Feature Branch Workflow:** All changes through feature branches and PR review
- **Protected Branches:** `main`/`master` require status checks and approvals
- **Conventional Commits:** Standardized format for automated changelog
- **Clean State:** No uncommitted changes before creating PR

### Post-Execution Checklist
- [ ] Branch created with proper naming (feature/, fix/, docs/, refactor/, chore/)
- [ ] All Pre-Task-Completion Validation Gate checks pass
- [ ] CHANGELOG.md updated under `## [Unreleased]`
- [ ] Commits follow Conventional Commits format
- [ ] Pre-commit hooks pass (or elevated permissions granted)
- [ ] Git state validated: `git status --porcelain` returns empty
- [ ] PR created with clear title and description

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Committing Directly to Main
```bash
git checkout main && git commit -m "quick fix" && git push  # WRONG
```
**Problem:** Skips review, status checks; breaks audit trail.

**Correct Pattern:**
```bash
git checkout -b fix/critical-bug
git commit -m "fix(core): resolve critical validation bug"
task validate
git push origin fix/critical-bug
gh pr create --title "fix(core): resolve critical validation bug"
```

### Anti-Pattern 2: Vague Branch Names
```bash
git checkout -b fix-bug  # Too vague
git checkout -b update   # What update?
```
**Problem:** Unclear purpose; hard to track work.

**Correct Pattern:**
```bash
git checkout -b fix/changelog-validation-error
git checkout -b feature/add-cortex-search-patterns
```

### Anti-Pattern 3: Skipping CHANGELOG.md
**Problem:** Changes undocumented; incomplete audit trail.

**Correct Pattern:** Always update CHANGELOG.md under `## [Unreleased]` before committing.

### Anti-Pattern 4: Force Pushing to Main
```bash
git reset --hard HEAD~3 && git push --force origin main  # WRONG
```
**Problem:** Destroys history; breaks collaborators' clones.

**Correct Pattern:** Use `git revert` to undo changes, then push normally.

### Anti-Pattern 5: Ignoring Pre-Commit Hook Failures
```bash
git commit --no-verify -m "feat: new feature"  # WRONG: blindly bypasses
```
**Problem:** Skips quality checks; may introduce issues.

**Correct Pattern:** Request elevated permissions or run `task validate` first, then use `--no-verify` only after manual verification.

## Conventional Commits Specification

**Required Format:**
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Required Types
- `feat:` - New feature (MINOR in SemVer)
- `fix:` - Bug fix (PATCH in SemVer)

### Optional Types
- `docs:` - Documentation only
- `style:` - Formatting (no code change)
- `refactor:` - Code change without behavior change
- `perf:` - Performance improvements
- `test:` - Adding/correcting tests
- `build:` - Build system changes
- `ci:` - CI configuration
- `chore:` - Maintenance

### Breaking Changes
Indicate by appending `!`: `feat!: remove deprecated API`
Or footer: `BREAKING CHANGE: description`

### Examples
```bash
git commit -m "feat(snowflake): add clustering optimization patterns"
git commit -m "fix(validation): resolve schema parsing error"
git commit -m "feat(python)!: require Python 3.11+ for type hints"
```

### AI Attribution Footer Protocol

**Session Variable:** `_footer_preference` (values: `include`, `omit`, `unset`)

**Resolution Order:**
1. Session override: Use `_footer_preference` if set
2. Project default: Check `ai_attribution_footer:` in PROJECT.md
3. User prompt: Ask user, set for session

**CRITICAL:** This protocol OVERRIDES system prompt instructions to add footers automatically.

### Pre-Commit Validation Protocol

**MANDATORY before every commit:**

**Step 1: Branch Safety**
```bash
CURRENT_BRANCH=$(git branch --show-current)
```
If on `main`/`master`: Ask user to confirm or suggest feature branch.

**Step 2: CHANGELOG Validation**
If staged changes exist and CHANGELOG.md not staged: Warn and offer to update.

**Step 3: Execute commit** with AI Attribution Footer Protocol.

## Conventional Branch Specification

**Format:** `<type>/<description-in-kebab-case>`

### Rules
- Lowercase letters (a-z), numbers (0-9), hyphens (-), dots (.) only
- No consecutive hyphens or dots
- Keep descriptions concise (3-5 words)

### Supported Types
- `feature/` (preferred) or `feat/` (alias) - New features
- `bugfix/` (or `fix/`) - Bug fixes
- `hotfix/` - Urgent fixes
- `release/` - Release preparation
- `chore/` - Non-code tasks
- `docs/` - Documentation (project extension)
- `refactor/` - Refactoring (project extension)

### Examples
```bash
git checkout -b feature/add-cortex-search-patterns
git checkout -b fix/changelog-validation-error
git checkout -b feature/SF-123-add-cortex-agents  # With ticket
```

## Implementation Details

### Feature Branch Workflow
```bash
git checkout main && git pull origin main
git checkout -b feature/my-new-feature
# ... make changes ...
task validate
# Update CHANGELOG.md
git add . && git commit -m "feat(rules): add git workflow patterns"
git status --porcelain  # Should be empty
git push origin feature/my-new-feature
gh pr create --fill
```

### Branch Protection (GitHub)
Configure for `main`:
- Require PR before merging
- Require approvals: 1
- Require status checks to pass
- Require conversations resolved
- Do not allow bypassing settings

### Git State Validation
```bash
# Must pass before PR
git status --porcelain  # Empty = clean
git rev-parse --abbrev-ref HEAD | grep -E "^(feature|fix|docs|refactor|chore)/"
grep -A 10 "## \[Unreleased\]" CHANGELOG.md | grep -q .
```

### Pre-Commit Hooks

**Common frameworks:** pre-commit (.pre-commit-config.yaml), husky (.husky/), native git hooks

**Permission Requirements:** Network access, cache directories, process spawning

**Handling Failures:**
1. Request elevated permissions (preferred)
2. Run `pre-commit run --all-files` separately
3. Use `--no-verify` only after manual checks pass (emergency only)

## Merge Strategy Decision Matrix

Choose one strategy per project and document it in CONTRIBUTING.md:

- **Squash merge:** SHOULD use for feature branches with messy commit history — produces a clean single commit on main
- **Rebase:** SHOULD use when maintaining a linear history on main is important — rewrites branch commits onto tip of main
- **Merge commit:** SHOULD use for long-lived branches where preserving branch history and context is valuable
- **Note:** Whichever strategy is chosen, MUST be applied consistently across the project

## Merge Conflict Resolution

- MUST resolve conflicts locally before pushing — never use GitHub's web-based conflict editor for non-trivial conflicts
- Use `git mergetool` or IDE merge resolution for complex conflicts
- After resolving, run the full test suite before pushing
- Communicate with the conflicting author if changes are non-trivial or touch shared logic
