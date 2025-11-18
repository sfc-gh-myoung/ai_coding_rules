# GitLab Release Workflow

This document describes the complete workflow for creating a new release version in GitLab from the command line.


## Prerequisites

- Git configured and authenticated
- Access to the GitLab repository
- `uv` installed for Python dependency management
- (Optional) `glab` CLI tool for GitLab operations
- (Optional) Personal Access Token for GitLab API


## Release Preparation Checklist

Before creating a release:

- [ ] All changes merged to `main` branch
- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated with release notes
- [ ] Version number decided (following semantic versioning)


## Step-by-Step Workflow

### Step 1: Prepare the Release

```bash
# 1. Ensure you're on main branch and up to date
git checkout main
git pull origin main

# 2. Update version in pyproject.toml
# Edit: version = "X.Y.Z"
vim pyproject.toml

# 3. Update CHANGELOG.md
# Move changes from [Unreleased] to [X.Y.Z] - YYYY-MM-DD
vim CHANGELOG.md

# 4. Create release notes (optional but recommended)
# Create docs/RELEASE_NOTES_vX.Y.Z.md
vim docs/RELEASE_NOTES_vX.Y.Z.md

# 5. Update uv.lock to reflect new version
uv sync

# 6. Commit version changes
git add pyproject.toml CHANGELOG.md uv.lock docs/RELEASE_NOTES_vX.Y.Z.md
git commit -m "chore: bump version to X.Y.Z"
git push origin main
```

### Step 2: Create and Push Git Tag

```bash
# Create annotated tag with descriptive message
git tag -a vX.Y.Z -m "vX.Y.Z: Brief description of release"

# Examples:
# git tag -a v2.2.0 -m "v2.2.0: Quality standards and workflow improvements"
# git tag -a v2.1.0 -m "v2.1.0: Project structure migration"

# Push tag to GitLab
git push origin vX.Y.Z

# Or push all tags at once:
git push origin --tags
```

### Step 3: Create GitLab Release

You have three options for creating the release in GitLab:

#### Option A: Using GitLab CLI (`glab`) - Recommended

```bash
# Install glab if needed (macOS)
brew install glab

# Authenticate (first time only)
glab auth login

# Create release with release notes file
glab release create vX.Y.Z \
  --name "AI Coding Rules vX.Y.Z" \
  --notes-file docs/RELEASE_NOTES_vX.Y.Z.md

# Or with inline notes
glab release create vX.Y.Z \
  --name "AI Coding Rules vX.Y.Z" \
  --notes "Brief description. See RELEASE_NOTES_vX.Y.Z.md for details."

# View the created release
glab release view vX.Y.Z
```

#### Option B: Using GitLab API with `curl`

```bash
# Set variables
GITLAB_HOST="snow.gitlab-dedicated.com"
PROJECT_ID="snowflakecorp%2FSE%2Fsales-engineering%2Fai_coding_rules"
TAG_NAME="vX.Y.Z"
RELEASE_NAME="AI Coding Rules vX.Y.Z"
GITLAB_TOKEN="your-personal-access-token"  # Get from GitLab Settings → Access Tokens

# Read release notes from file
RELEASE_NOTES=$(cat docs/RELEASE_NOTES_vX.Y.Z.md)

# Create release via API
curl --request POST \
  --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
  --header "Content-Type: application/json" \
  --data "{
    \"name\": \"${RELEASE_NAME}\",
    \"tag_name\": \"${TAG_NAME}\",
    \"description\": \"${RELEASE_NOTES}\"
  }" \
  "https://${GITLAB_HOST}/api/v4/projects/${PROJECT_ID}/releases"
```

**Getting a Personal Access Token:**
1. Go to GitLab Settings → Access Tokens
2. Create token with scopes: `api`, `write_repository`
3. Store securely (password manager)

#### Option C: Using GitLab Web UI

1. Navigate to: `https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules/-/releases`
2. Click **"New release"** button
3. **Tag name:** Select `vX.Y.Z` from dropdown
4. **Release title:** `AI Coding Rules vX.Y.Z`
5. **Release notes:** Copy/paste from `docs/RELEASE_NOTES_vX.Y.Z.md`
6. Click **"Create release"**

### Step 4: Verify Release

```bash
# List all releases using glab
glab release list

# View specific release
glab release view vX.Y.Z

# Or check via web browser
# https://snow.gitlab-dedicated.com/snowflakecorp/SE/sales-engineering/ai_coding_rules/-/releases
```


## Complete Example: Creating v2.2.0

```bash
# 1. Start from clean main branch
git checkout main
git pull origin main

# 2. Update version files (already done for this example)
# - pyproject.toml: version = "2.2.0"
# - CHANGELOG.md: [2.2.0] section added
# - docs/RELEASE_NOTES_v2.2.0.md: created

# 3. Sync dependencies
uv sync

# 4. Commit version changes
git add pyproject.toml CHANGELOG.md uv.lock docs/RELEASE_NOTES_v2.2.0.md
git commit -m "chore: bump version to 2.2.0"
git push origin main

# 5. Create and push annotated tag
git tag -a v2.2.0 -m "v2.2.0: Quality standards, token budget accuracy, emoji removal, workflow automation"
git push origin v2.2.0

# 6. Create GitLab release using glab
glab release create v2.2.0 \
  --name "AI Coding Rules v2.2.0" \
  --notes-file docs/RELEASE_NOTES_v2.2.0.md

# 7. Verify release created successfully
glab release view v2.2.0
```


## Best Practices

### Tag Naming Convention

- **Always use `v` prefix:** `v2.2.0` (not `2.2.0`)
- **Follow semantic versioning:** `vMAJOR.MINOR.PATCH`
  - **MAJOR:** Breaking changes
  - **MINOR:** New features (backward compatible)
  - **PATCH:** Bug fixes (backward compatible)

### Annotated vs Lightweight Tags

- **Always use annotated tags** (`-a` flag) for releases
- Annotated tags include:
  - Tagger name and email
  - Date and time
  - Tag message
- GitLab treats annotated tags as proper releases

### Release Notes

- **Location:** Store in `docs/RELEASE_NOTES_vX.Y.Z.md`
- **Structure:** Include:
  - Overview and highlights
  - Breaking changes (if any)
  - New features
  - Bug fixes
  - Migration guide
  - Upgrade instructions
- **Reference:** Link from CHANGELOG.md
- **Include:** Add to GitLab release description

### Version Updates

Files to update for each release:

1. `pyproject.toml` - Project version
2. `CHANGELOG.md` - Release notes
3. `uv.lock` - Lock file (via `uv sync`)
4. `docs/RELEASE_NOTES_vX.Y.Z.md` - Detailed release notes


## Troubleshooting

### Rollback a Release

If you need to undo a release:

```bash
# 1. Delete local tag
git tag -d vX.Y.Z

# 2. Delete remote tag
git push origin :refs/tags/vX.Y.Z

# 3. Delete GitLab release
glab release delete vX.Y.Z
# Or delete via GitLab web UI
```

### Tag Already Exists

```bash
# Error: tag 'vX.Y.Z' already exists

# Option 1: Use a different version number
git tag -a vX.Y.Z+1 -m "..."

# Option 2: Delete and recreate (if not pushed)
git tag -d vX.Y.Z
git tag -a vX.Y.Z -m "..."

# Option 3: Force update (if already pushed - use cautiously)
git tag -fa vX.Y.Z -m "..."
git push origin vX.Y.Z --force
```

### Release Notes File Not Found

```bash
# Error: file not found when creating release

# Verify file exists
ls -la docs/RELEASE_NOTES_vX.Y.Z.md

# Use absolute path
glab release create vX.Y.Z \
  --name "..." \
  --notes-file "$(pwd)/docs/RELEASE_NOTES_vX.Y.Z.md"
```


## Automation with Task

For convenience, consider adding to `Taskfile.yml`:

```yaml
tasks:
  release:prepare:
    desc: "Prepare release (update version, sync dependencies)"
    cmds:
      - echo "Update pyproject.toml version manually"
      - echo "Update CHANGELOG.md manually"
      - uv sync
      - git status

  release:tag:
    desc: "Create and push release tag"
    cmds:
      - git tag -a {{.VERSION}} -m "{{.VERSION}}: {{.MESSAGE}}"
      - git push origin {{.VERSION}}
    vars:
      VERSION: '{{.VERSION | default "v0.0.0"}}'
      MESSAGE: '{{.MESSAGE | default "Release"}}'

  release:create:
    desc: "Create GitLab release"
    cmds:
      - glab release create {{.VERSION}} --name "AI Coding Rules {{.VERSION}}" --notes-file docs/RELEASE_NOTES_{{.VERSION}}.md
    vars:
      VERSION: '{{.VERSION | default "v0.0.0"}}'
```

Usage:
```bash
task release:prepare
task release:tag VERSION=v2.2.0 MESSAGE="Quality improvements"
task release:create VERSION=v2.2.0
```


## Additional Resources

- **GitLab Releases Documentation:** https://docs.gitlab.com/ee/user/project/releases/
- **GitLab API - Releases:** https://docs.gitlab.com/ee/api/releases/
- **glab CLI Documentation:** https://gitlab.com/gitlab-org/cli
- **Semantic Versioning:** https://semver.org/
- **Git Tagging:** https://git-scm.com/book/en/v2/Git-Basics-Tagging


## Quick Reference

```bash
# Complete workflow
git checkout main && git pull
# Update: pyproject.toml, CHANGELOG.md
uv sync
git add pyproject.toml CHANGELOG.md uv.lock docs/RELEASE_NOTES_vX.Y.Z.md
git commit -m "chore: bump version to X.Y.Z"
git push origin main
git tag -a vX.Y.Z -m "vX.Y.Z: Description"
git push origin vX.Y.Z
glab release create vX.Y.Z --name "AI Coding Rules vX.Y.Z" --notes-file docs/RELEASE_NOTES_vX.Y.Z.md
```
