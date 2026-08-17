# Dev Task Reference

> **Note:** The `ai-rules dev` Python CLI has been removed. All development commands are now reached via [Task](https://taskfile.dev/) (`Taskfile.yml` at project root).

Task is a cross-platform task runner. Install it via `brew install go-task` (macOS) or see [taskfile.dev/installation](https://taskfile.dev/installation/).

## Quick Start

```bash
# Run all quality checks
task quality:all

# Fix all auto-fixable issues
task quality:all:fix

# Run tests
task test:run

# Run tests with coverage
task test:coverage

# Full validation pipeline (CI equivalent)
task validate
```

## Command Reference

### `env:*`

Environment setup and dependency management.

| Command | Description |
|---|---|
| `task env:setup` | Pin Python 3.12, create `.venv` |
| `task env:sync` | Sync dev dependencies (fast) |
| `task env:lock` | Lock and sync all dependencies |

### `quality:*`

Code quality checks using ruff, ty, and pymarkdownlnt.

| Command | Description |
|---|---|
| `task quality:all` | Run all checks (lint + format + typecheck + markdown) |
| `task quality:all:fix` | Run all checks with auto-fix |
| `task quality:lint` | Lint only |
| `task quality:lint:fix` | Fix lint issues |
| `task quality:format` | Format check only |
| `task quality:format:fix` | Apply formatting |
| `task quality:typecheck` | Type check only |
| `task quality:markdown` | Lint markdown only |
| `task quality:markdown:fix` | Fix markdown |

### `test:*`

Run pytest test suite.

| Command | Description |
|---|---|
| `task test:run` | Run all tests |
| `task test:coverage` | Run with coverage report |
| `task test:coverage:open` | Coverage + open in browser (macOS) |

### `clean:*`

Remove generated files and caches.

| Command | Description |
|---|---|
| `task clean:cache` | Remove caches only (no prompt) |
| `task clean:venv` | Remove `.venv` (prompts on TTY; pass `FORCE=1` for non-interactive use) |
| `task clean:all FORCE=1` | Remove all caches and `.venv` |

### `status:*`

Project information and environment checks.

| Command | Description |
|---|---|
| `task status:show` | Rule/test counts, tool versions |
| `task status:preflight` | Verify environment is ready |

### `validate` / `ci`

Full validation pipeline (quality + tests + schema validation of `rules/`, `rules/examples/`, and `templates/`). Both commands are identical; `ci` is an alias for `validate`.

**Note:** This is the local validation surface. CI additionally runs rule-loader validate/audit/trigger-contract and plugin-build checks via direct `uv run ai-rules ...` calls. The two are complementary, not equivalent.

### `release:*`

Maintainer-only commands for cutting a release. Pass `DRY_RUN=1` to preview without executing.

| Command | Description |
|---|---|
| `task release:bump VERSION=X.Y.Z` | Bump version on the current release branch and push |
| `DRY_RUN=1 task release:bump VERSION=X.Y.Z` | Preview the bump |
| `task release:merge VERSION=X.Y.Z` | Squash-merge `release/vX.Y.Z` into `main`, tag, create GitHub release |
| `DRY_RUN=1 task release:merge VERSION=X.Y.Z` | Preview the merge |

The `bump` command edits `pyproject.toml` and the `README.md` version badge atomically (via `scripts/bump_version.py` using tempfile + os.replace), then commits and pushes.

### `mirror:*`

Maintainer-only commands for syncing GitHub `main` to the GitLab mirror via orphan commit + force push.

| Command | Description |
|---|---|
| `task mirror:sync` | Sync current `main` to GitLab mirror |
| `DRY_RUN=1 task mirror:sync` | Preview the sync |

## Top-level `ai-rules` commands (unchanged)

| Command | Description |
|---|---|
| `ai-rules validate <PATH>` | Validate rule schema |
| `ai-rules new <FILENAME>` | Generate a new rule template |
| `ai-rules tokens <PATH>` | Update token budget metadata |
| `ai-rules rule-loader keywords <PATH>` | Suggest keywords for a rule |
| `ai-rules badges` | Update README badges |
| `ai-rules plugin build` | Build the distributable `ai-coding-rules-plugin/` |
| `ai-rules rule-loader` | Live-agent rule loading evaluator |

## Configuration

Markdown targets and clean globs are defined in `Taskfile.yml` vars section:

```yaml
vars:
  MARKDOWN_RULES_TARGETS: 'rules/'
  MARKDOWN_DOCS_TARGETS: 'docs/ README.md CONTRIBUTING.md CHANGELOG.md'
```

## Supported Platforms

macOS (darwin) and Linux. Windows is not supported.

## Pre-commit Integration

The `rule-loader-eval` pre-commit hook (in `.pre-commit-config.yaml`) chains `ai-rules rule-loader eval --fixture <id>` calls. Skip when Snowflake credentials are unavailable:

```bash
SKIP=rule-loader-eval git commit -m "..."
```
