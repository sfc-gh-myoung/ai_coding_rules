---
schema_version: v4.0
rule_version: v3.0.0
description: "Virtual environment management, tool isolation patterns (uvx vs uv run), detailed command patterns for each toolchain (uv, poetry, pip), environment setup best practices, troubleshooting common"
last_updated: 2026-10-06
keywords:
  - kw:venv
  - kw:uv run
  - kw:uvx
  - kw:poetry run
  - kw:toolchain detection
  - kw:ModuleNotFoundError diagnosis
token_budget: ~1100
context_tier: High
depends:
  required:
    - 200-python-core.md  # Core Python patterns and toolchain detection
  optional:
    - 200a-python-validation-gate.md  # Validation gate commands per toolchain
    - 203-python-project-setup.md  # Project structure and initialization
---
# Python Environment and Tooling

## Scope

**What This Rule Covers:**
Interpreter/environment detection, managed dependency execution, isolated tools, reproducible exports and scoped import/install troubleshooting.

**When to Load This Rule:**
When configuring environments/tool isolation, diagnosing imports or integrating Python commands into automation/containers.

## Contract

### Inputs and Prerequisites

- Existing manifests, lockfiles, Python support, .python-version and environment/container configuration.
- Actual manager/interpreter path, required dependency groups and approved install/network scope.

### Mandatory

- Use the project's established manager and interpreter. Detect uv, Poetry, pip/venv, Pipenv or conda from evidence; unknown means unknown, not an automatic uv/pip replacement.
- Project code/tests/plugins must run in an environment containing their actual dependencies. Isolated uvx/pipx tools are appropriate only when they can access needed config/types/plugins; type checking may still require the project's installed dependencies.
- Isolation is not reproducible pinning. Bind tool versions and use the project's lock-validation mode when required; do not silently upgrade/lock/update during ordinary validation.
- Environment creation/sync/install is mutation and may access networks; execute only under task authorization, never as a hidden prerequisite of a read-only check.
- Do not delete/rebuild .venv or use clear flags blindly. Inspect interpreter/dependency mismatch and ownership, preserve local changes, and require approval for destructive rebuild.
- Use intended dev/test groups, not all-groups unconditionally; keep development tools out of production runtime dependency sets unless needed at runtime.
- Keep conda/manager policies coherent; do not assume pip --no-deps is universally safe or classify all binary dependencies by guessed package rules.
- Requirements exports must reflect the selected lock/groups/extras; pip freeze captures the active environment, not necessarily the project's intended dependency graph. Review generated exports and retain them when deployment consumes them.
- Container workflows use actual supported pinned images/tool versions and deliberate environment paths; uv sync can create a venv in containers. No blanket claim that containers need no venv.
- Never redirect installs to unapproved package mirrors, alter proxy settings or transmit project credentials/data to resolve network errors.

### Execution Steps

1. Read manifests/locks/environment/container/automation and locate actual interpreter and manager.
2. Diagnose failure by checking interpreter version/path, installed package/import origin, selected groups and package layout. Do not infer absence from a different interpreter.
3. If authorized, create/sync the intended isolated environment using locked dependencies and selected groups; avoid unrequested upgrades.
4. Verify safe imports/entry points and tool availability under the configured environment; importing can have side effects, so use known test modules.
5. Configure tool isolation or dev groups appropriate to dependency needs and update automation/docs consistently.
6. On network/resolution issues, inspect exact errors and approved cache/index settings. Safe offline use requires cached artifacts; bounded retries cannot resolve unknown mutation outcomes.

### Validation

- Actual interpreter/manager matches support and installed dependency groups.
- Imports/entry points and configured validation tools work in the intended environment.
- Lock/export/CI versions consistent; no uncontrolled all-group install or silent upgrade.
- No unauthorized environment deletion, mirror/proxy change, global install or mixed-manager drift.
- Missing availability/runtime checks disclosed, not fabricated from manifest presence.

## References

- [uv projects](https://docs.astral.sh/uv/guides/projects/)
- [uv tools](https://docs.astral.sh/uv/concepts/tools/)
- [Poetry environments](https://python-poetry.org/docs/managing-environments/)
- [Python virtual environments](https://docs.python.org/3/library/venv.html)
- [Conda environments](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html)
