# Dev task reference

The repository uses [Task](https://taskfile.dev/) for development automation. Run commands from the repository root.

Install Task 3.45.0 or later. Install `uv`, ShellCheck, and `shfmt` before you run the complete validation pipeline.

## Find a task

Run `task` for categorized help. Run `task --list --json` for machine-readable output. Maintainer tasks provide more detail through `task --summary <task>`.

## Set up the environment

| Command | Result |
|---|---|
| `task env:setup` | Installs and pins Python 3.12, then creates `.venv` |
| `task env:sync` | Syncs locked development dependencies without the `live-agent` group |
| `task env:sync:live` | Syncs locked dependencies and includes the optional `live-agent` group |
| `task env:lock` | Updates `uv.lock`, then syncs development dependencies |

Set `PYTHON_VERSION=3.13` to run a task with Python 3.13. Task passes the version through `uv --python`, so an inherited `UV_PYTHON` value does not override it.

## Run quality and tests

| Command | Result |
|---|---|
| `task quality:all` | Runs Ruff, ty, Markdown, Task schema, ShellCheck, and shfmt checks |
| `task quality:all:fix` | Applies safe Python and Markdown fixes, then runs all quality checks |
| `task test:run` | Runs all non-live pytest tests |
| `task test:coverage` | Runs tests and enforces the configured coverage threshold |
| `task test:automation` | Tests Task, cleanup, version, release, and mirror behavior in disposable repositories |
| `task validate` or `task ci` | Runs the full local validation pipeline without Task fingerprint skips |

`task validate` includes coverage, schema validation, the rule-loader fixture and reachability gates, trigger-count validation, and plugin fidelity. It validates the Cortex plugin loader when the `cortex` command exists. Run `task plugin:verify:strict` when absence of `cortex` must fail.

GitHub Actions uses the same Task entry points. It also tests Python 3.12 and 3.13, macOS and Linux, Task 3.45.0, and Task 3.53.1.

## Remove local artifacts

| Command | Result |
|---|---|
| `task clean:cache` | Removes project caches, coverage output, and `.task`; preserves virtual environments |
| `task clean:venv` | Confirms before removing `.venv` |
| `task clean:all` | Confirms once before removing caches and `.venv` |

For unattended cleanup, use `task clean:venv FORCE=1` or `task clean:all FORCE=1`. Invalid `FORCE` values fail without deleting files.

## Cut a release

Release commands accept stable `X.Y.Z` versions only. They require signed Git commits and tags.

1. Create and check out `release/vX.Y.Z`.
2. Commit or move every tracked and untracked change.
3. Run `task release:bump VERSION=X.Y.Z DRY_RUN=1`.
4. Run `task release:bump VERSION=X.Y.Z`.
5. Review the pushed release branch.
6. Run `task release:merge VERSION=X.Y.Z DRY_RUN=1`.
7. Run `task release:merge VERSION=X.Y.Z`.

`release:bump` updates `pyproject.toml`, `src/ai_rules/__init__.py`, the README version badge, and `uv.lock`. It runs `task ci` before it creates a signed commit or pushes the branch.

`release:merge` fetches `origin`, verifies that the local and remote release commits match, and creates an isolated Git worktree from `origin/main`. It applies the squash without conflict overrides, validates the result, signs the commit and tag, atomically pushes both refs, and creates a draft GitHub release. It does not switch the active checkout or update local `main`.

### Recover a stopped release

Do not rerun a failed release command until you identify its last successful external action.

- If `release:bump` fails before the commit, review the four version files and the validation output. The command does not push.
- If the commit succeeds but the branch push fails, inspect `git log -1` and push the existing commit. Do not create another version commit.
- If `release:merge` stops before the atomic push, inspect the retained worktree path printed by the command. Resolve the cause or remove it with `git worktree remove <path>`.
- If the atomic push succeeds but draft creation fails, run `gh release create vX.Y.Z --verify-tag --title vX.Y.Z --draft --generate-notes`.

## Sync the GitLab mirror

Run `task mirror:sync DRY_RUN=1`, then `task mirror:sync`. The command mirrors the committed local `main` tree, not the active branch. Synchronize and review local `main` first.

The command creates a signed parentless commit with a temporary Git index. It pushes to the single configured `gitlab` push URL with an explicit lease. Concurrent changes to `gitlab/main` cause the push to fail. The command does not switch branches or alter the working tree.

## Scripts reference

The `scripts/` folder holds only long-lived project scripts. Put plan-scoped or one-off scripts in `.workbench/scripts/` instead (see `rules/806-workbench-folder-policy.md`).

### Called by Task

Run these through their Task entry points, not directly.

| Script | Task entry point | Purpose |
|---|---|---|
| `dev_info.py` | `task`, `task status:show` | Prints grouped Task help, or interpreter and project counts |
| `clean.sh` | `task clean:cache`, `clean:venv`, `clean:all` | Removes caches and, with confirmation or `FORCE=1`, `.venv` |
| `plugin-verify.sh` | `task plugin:verify`, `plugin:verify:strict` | Checks replica sync, builds the plugin to a temp directory, and verifies it |
| `release.sh` | `task release:bump`, `release:merge` | Runs the guarded release flow described in [Cut a release](#cut-a-release) |
| `bump_version.py` | Called by `release.sh bump` | Updates the four version files and restores them on failure |
| `mirror.sh` | `task mirror:sync` | Pushes the local `main` tree to the GitLab mirror |
| `maintainer-common.sh` | Sourced by `release.sh` and `mirror.sh` | Shared guards: clean tree, repo root, version format, single push URL |

### Called by pre-commit hooks

These run from `.pre-commit-config.yaml` after `uv run pre-commit install`.

| Script | Purpose |
|---|---|
| `sync_plugin_replicas.sh` | Regenerates and stages plugin replicas when they drift from their primaries, then blocks the commit for review |
| `entro_secret_scan.sh` | Runs the Entro secret scan. Set `git config entro.skipSecretScan true` to skip it |

### Run by hand

| Script | Command | Purpose |
|---|---|---|
| `run-eval.sh` | `bash scripts/run-eval.sh [--effort LEVEL] [--label TEXT]` | Runs `rule-loader eval` for every model in its `MODELS` list. Each model incurs live Cortex token costs |
| `eval_precision.py` | `uv run python scripts/eval_precision.py` | Reports matcher precision (missing and extra rules) across all rule-loader fixtures, without calling an agent |
| `verify_report_browser.py` | `uvx --with playwright python scripts/verify_report_browser.py` | Checks the sorting and tabs in `reports/llm-protocol-compliance-report.html` in a headless browser |

## Top-level CLI commands

Task does not replace the `ai-rules` product CLI. Run `uv run --locked ai-rules --help` for commands that validate, generate, deploy, or evaluate rules and plugins.

## Supported platforms

The Taskfile supports macOS and Linux. Windows is not supported.
