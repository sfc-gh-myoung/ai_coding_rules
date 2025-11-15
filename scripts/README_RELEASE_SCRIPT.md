# Release Script Documentation

## Overview

The `create-release.sh` script automates the git release workflow following best practices from:
- `300-bash-scripting-core.mdc` - Shell scripting foundations
- `300a-bash-security.mdc` - Input validation and security
- `806-git-workflow-management.mdc` - Git workflow patterns

## Prerequisites

1. **Clean git state**: No uncommitted changes
2. **On main branch**: Script must start from `main`
3. **Staged files**: Changes must be staged before running (use `git add`)

## Usage

```bash
# 1. Stage your changes
git add .

# 2. Run the release script
./scripts/create-release.sh
```

## Workflow

The script follows this sequence:

```
1. Validate git state (on main, clean working directory)
2. Check for staged files
3. Prompt for branch name (with validation)
4. Prompt for commit message (Conventional Commits format)
5. Prompt for tag name (semantic versioning)
6. Show summary and confirm
7. Execute release:
   - Create and checkout feature branch
   - Commit staged files
   - Checkout main
   - Merge feature branch
   - Create annotated tag
   - Push main and tags to origin
```

## Input Validation

### Branch Name Format

**Required Pattern:** `(feature|fix|docs|refactor|chore)/description-in-kebab-case`

**Valid Examples:**
```
feature/add-semantic-views
fix/changelog-validation
chore/update-dependencies
docs/improve-readme
refactor/split-large-rules
```

**Invalid Examples:**
```
myfeature              ✗ Missing prefix
feature-add-rule       ✗ Wrong separator (use /)
feature/Add_Rule       ✗ Not kebab-case
add-new-feature        ✗ Missing prefix
```

### Commit Message Format

**Recommended Pattern:** `type(scope): description`

**Valid Examples:**
```
feat(rules): enhance Snowflake Semantic Views documentation
fix(scripts): correct branch validation logic
chore(deps): update ruff to v0.2.0
docs(readme): clarify installation steps
refactor(core): simplify validation functions
```

The script allows non-conforming messages but warns and prompts for confirmation.

### Tag Name Format

**Required Pattern:** `vX.Y.Z` (semantic versioning)

**Valid Examples:**
```
v2.4.0
v1.0.1
v3.12.5
```

**Invalid Examples:**
```
2.4.0      ✗ Missing 'v' prefix
v2.4       ✗ Missing patch version
release-2  ✗ Not semantic versioning
v2.4.0-rc  ✗ No pre-release tags
```

## Example Session

```bash
$ ./scripts/create-release.sh

════════════════════════════════════════════════════════════
              GIT RELEASE AUTOMATION SCRIPT
════════════════════════════════════════════════════════════

ℹ Checking git repository state...
✓ Git state validated (on main, clean working directory)
ℹ Checking for staged files...
✓ Found 8 staged file(s)
ℹ Staged files:
  - CHANGELOG.md
  - templates/106a-snowflake-semantic-views-querying.md
  - templates/106b-snowflake-semantic-views-integration.md
  - generated/cursor/rules/106a-snowflake-semantic-views-querying.mdc
  - generated/cursor/rules/106b-snowflake-semantic-views-integration.mdc
  - generated/universal/106a-snowflake-semantic-views-querying.md
  - generated/universal/106b-snowflake-semantic-views-integration.md
  - discovery/RULES_INDEX.md

ℹ Enter branch name following convention: (feature|fix|docs|refactor|chore)/description
Examples:
  - feature/add-semantic-views
  - fix/changelog-validation
  - chore/update-dependencies

Branch name: feature/semantic-views-rules
✓ Branch name validated: feature/semantic-views-rules

ℹ Enter commit message (Conventional Commits format recommended)
Format: type(scope): description
Example: feat(rules): enhance Snowflake Semantic Views documentation

Commit message: feat(rules): add Semantic Views querying and integration rules
✓ Commit message accepted

ℹ Enter git tag following semantic versioning: vX.Y.Z
Examples: v2.4.0, v1.0.1, v3.2.5

ℹ Recent tags:
  - v2.3.2
  - v2.3.1
  - v2.3.0
  - v2.2.2
  - v2.2.1

Tag name: v2.4.0
✓ Tag name validated: v2.4.0

════════════════════════════════════════════════════════════
                    RELEASE SUMMARY
════════════════════════════════════════════════════════════

Branch:         feature/semantic-views-rules
Commit Message: feat(rules): add Semantic Views querying and integration rules
Tag:            v2.4.0

Operations to perform:
  1. Create and checkout branch: feature/semantic-views-rules
  2. Commit staged files with message
  3. Checkout main branch
  4. Merge feature/semantic-views-rules into main
  5. Create tag: v2.4.0
  6. Push main and tags to origin

════════════════════════════════════════════════════════════

Proceed with release? (y/N): y
ℹ Starting release process...

ℹ Step 1/6: Creating and checking out branch: feature/semantic-views-rules
✓ Branch created and checked out: feature/semantic-views-rules

ℹ Step 2/6: Committing staged files
✓ Changes committed successfully

ℹ Step 3/6: Checking out main branch
✓ Switched to main branch

ℹ Step 4/6: Merging feature/semantic-views-rules into main
✓ Branch merged successfully

ℹ Step 5/6: Creating annotated tag: v2.4.0
✓ Tag created: v2.4.0

ℹ Step 6/6: Pushing main branch and tags to origin
✓ Changes and tags pushed to origin


════════════════════════════════════════════════════════════
               RELEASE COMPLETED SUCCESSFULLY
════════════════════════════════════════════════════════════

Branch:  feature/semantic-views-rules
Tag:     v2.4.0
Status:  Pushed to origin

✓ Release v2.4.0 created successfully!

Delete local branch feature/semantic-views-rules? (y/N): y
✓ Branch feature/semantic-views-rules deleted
```

## Error Handling

The script validates inputs and git state at each step:

### Common Errors

**Not on main branch:**
```
✗ Must start on 'main' branch (currently on: feature/old-work)
✗ Run: git checkout main
```

**Uncommitted changes:**
```
✗ Uncommitted changes detected in working directory:
 M templates/some-file.md
?? new-file.txt
✗ Please commit or stash changes before creating a release
```

**No staged files:**
```
✗ No files staged for commit
✗ Please stage your changes first:
  git add <files>
  or
  git add .
```

**Invalid branch name:**
```
✗ Invalid branch name format: myfeature
✗ Must match: (feature|fix|docs|refactor|chore)/description-in-kebab-case
```

**Tag already exists:**
```
✗ Tag 'v2.4.0' already exists
⚠ To recreate an existing tag, delete it first:
  git tag -d v2.4.0
  git push origin :refs/tags/v2.4.0
```

## Rollback

If the script fails mid-execution, you may need to clean up manually:

```bash
# If merge failed
git merge --abort

# If commit succeeded but merge failed
git checkout main
git branch -D <branch-name>

# If tag was created but push failed
git tag -d <tag-name>
git push origin main --tags
```

## Differences from Manual Workflow

The script **automates** the pattern shown in `git-commands.md`:

**Manual workflow (from git-commands.md):**
```bash
git checkout -b feat-rule-updates
git commit -m "feat: enhance Snowflake Semantic Views..."
git checkout main
git merge feat-rule-updates
git tag -a v2.4.0 -m "v2.4.0: Feature: enhance Snowflake..."
git push origin main --tags
```

**Script workflow:**
```bash
git add .
./scripts/create-release.sh
# Follow interactive prompts
```

## Security Features

- **Input validation**: Branch name, commit message, and tag name patterns validated
- **State validation**: Ensures clean git state and correct branch before proceeding
- **Confirmation prompt**: Shows summary and requires explicit confirmation
- **Error recovery**: Provides cleanup instructions if operations fail
- **No eval**: Uses safe command execution patterns (no `eval` of user input)

## Bash Best Practices Applied

- ✅ `set -euo pipefail` - Strict error handling
- ✅ `IFS=$'\n\t'` - Safe word splitting
- ✅ Input validation with regex patterns
- ✅ Quoted variables throughout
- ✅ Descriptive function names
- ✅ Color-coded logging (info, success, warning, error)
- ✅ Comprehensive error messages
- ✅ Cleanup on failure
- ✅ `printf` instead of `echo` for return values (prevents newline/formatting issues in command substitution)

## Related Documentation

- `300-bash-scripting-core.mdc` - Bash scripting foundations
- `300a-bash-security.mdc` - Security and input validation
- `806-git-workflow-management.mdc` - Git workflow patterns
- `git-commands.md` - Manual release workflow examples

