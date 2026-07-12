# Dev CLI Reference

> **Note:** The Makefile has been removed. All commands are now reached via `ai-rules`.

The `ai-rules` CLI is the single entry point for development, rule management, deployment, and release operations. It works on macOS, Linux, and Windows without requiring shell utilities.

By default, subprocess failures are reported with concise next steps. Add `--debug` before the subcommand, for example `uv run ai-rules --debug dev validate`, to show Python tracebacks for internal command failures.

## Quick Start

```bash
# Run all quality checks
uv run ai-rules dev quality all

# Fix all auto-fixable issues
uv run ai-rules dev quality all --fix

# Run tests
uv run ai-rules dev test run

# Run tests with coverage
uv run ai-rules dev test run --coverage --open

# Full validation pipeline (CI equivalent)
uv run ai-rules dev validate
```

## Command Reference

### `ai-rules dev env`

Environment setup and dependency management.

| Command | Description |
|---|---|
| `dev env setup` | Pin Python 3.11, create `.venv` |
| `dev env sync` | Sync dev dependencies (fast) |
| `dev env lock` | Lock and sync all dependencies |

### `ai-rules dev quality`

Code quality checks using ruff, ty, and pymarkdownlnt.

`ai-rules dev quality` with no subcommand prints help. Use `quality all` to run every check at once, or call an individual subcommand.

| Command | Description |
|---|---|
| `dev quality all` | Run all checks (lint + format + typecheck + markdown) |
| `dev quality all --fix` | Run all checks; auto-fix lint, format, and markdown |
| `dev quality lint` | Lint only |
| `dev quality lint --fix` | Fix lint issues |
| `dev quality format` | Format check only |
| `dev quality format --fix` | Apply formatting |
| `dev quality typecheck` | Type check only |
| `dev quality markdown` | Markdown lint only |
| `dev quality markdown --fix` | Fix markdown |

### `ai-rules dev test`

Run pytest test suite.

| Command | Description |
|---|---|
| `dev test run` | Run all tests |
| `dev test run --coverage` | Run with coverage report |
| `dev test run --coverage --open` | Coverage + open in browser |

### `ai-rules dev clean`

Remove generated files and caches. Bare `dev clean` shows help; use a subcommand to perform an action.

| Command | Description |
|---|---|
| `dev clean all` | Remove all caches and `.venv` (prompts on TTY; pass `-f`/`--force` for non-interactive use) |
| `dev clean cache` | Remove caches only (no prompt) |
| `dev clean venv` | Remove `.venv` only (prompts on TTY; pass `-f`/`--force` for non-interactive use) |

> Per [CLIG.dev](https://clig.dev/), destructive operations require an interactive confirmation or an explicit `--force` flag. `clean cache` is exempt because Python caches regenerate trivially.

### `ai-rules dev status`

Project information and environment checks.

| Command | Description |
|---|---|
| `dev status show` | Rule/test counts, tool versions |
| `dev status preflight` | Verify environment is ready |

### `ai-rules dev validate` / `ai-rules dev ci`

Full validation pipeline (quality + tests + schema validation + index check). Both commands are identical; `ci` is an alias for `validate`.

### `ai-rules dev release`

Maintainer-only commands for cutting a release. All `bump` and `merge` commands accept `--dry-run` to preview without executing.

| Command | Description |
|---|---|
| `dev release bump VERSION` | Bump version on the current release branch and push |
| `dev release bump VERSION --dry-run` | Preview the bump |
| `dev release merge VERSION` | Squash-merge `release/vVERSION` into `main`, tag, create GitHub release |
| `dev release merge VERSION --dry-run` | Preview the merge |

The `bump` command edits `pyproject.toml` and the `README.md` version badge atomically (tempfile + os.replace), then commits and pushes.

### `ai-rules dev mirror`

Maintainer-only commands for syncing GitHub `main` to the GitLab mirror via orphan commit + force push.

| Command | Description |
|---|---|
| `dev mirror sync` | Sync current `main` to GitLab mirror |
| `dev mirror sync --dry-run` | Preview the sync |

## Top-level commands

| Command | Description |
|---|---|
| `ai-rules validate <PATH>` | Validate rule schema |
| `ai-rules deploy --agents-dest <DIR>` | Deploy rules to project / shared directory |
| `ai-rules new <FILENAME>` | Generate a new rule template |
| `ai-rules tokens <PATH>` | Update token budget metadata |
| `ai-rules keywords <PATH>` | Suggest keywords for a rule |
| `ai-rules badges` | Update README badges |
| `ai-rules refs` | Validate rule references |
| `ai-rules index generate` | Generate `rules/RULES_INDEX.md` |
| `ai-rules index check` | Check `rules/RULES_INDEX.md` is up-to-date |
| `ai-rules rule-loader` | Live-agent rule loading evaluator |

## Configuration

The `[tool.ai_rules.dev]` section in `pyproject.toml` controls markdown scan targets and clean globs:

```toml
[tool.ai_rules.dev]
markdown_rules_targets = ["rules/", "templates/..."]
markdown_docs_targets  = ["docs/", "README.md", ...]
coverage_html_dir      = "htmlcov"
clean_globs            = ["**/__pycache__", "**/*.pyc", ...]
```

## Windows Support

All `ai-rules` commands use Python's `pathlib` and `subprocess` (never shell pipes or `find`/`xargs`). They run correctly on Windows without WSL.

## Pre-commit Integration

The `rule-loader-eval` pre-commit hook (in `.pre-commit-config.yaml`) chains five `ai-rules rule-loader eval --fixture <id>` calls. Skip when Snowflake credentials are unavailable:

```bash
SKIP=rule-loader-eval git commit -m "..."
```
