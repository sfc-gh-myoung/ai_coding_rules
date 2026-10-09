---
schema_version: v4.0
rule_version: v5.0.0
description: "Python code quality standards with Ruff as the recommended tool for linting and formatting. Covers command patterns for multiple toolchains (uv, poetry, pip), pyproject.toml configuration, pydocstyle"
last_updated: 2026-10-06
keywords:
  - kw:Ruff
  - kw:pyproject.toml configuration
  - kw:uvx ruff
  - kw:pydocstyle D rules
  - kw:pre-commit hooks
  - kw:zero-error validation gate
token_budget: ~900
context_tier: High
depends:
  required:
    - 200-python-core.md  # Python foundation patterns and toolchain detection
  optional:
    - 203-python-project-setup.md  # Project structure and configuration
    - 204-python-docs.md  # Documentation standards
---
# Python Linting and Formatting

## Scope

**What This Rule Covers:**
Project-configured lint/format checks, Ruff recommendations for new projects, scoped suppressions, tool pinning and safe fixes.

**When to Load This Rule:**
When modifying Python, configuring code-quality tools, integrating hooks or diagnosing lint/format failures.

## Contract

### Inputs and Prerequisites

- Current pyproject/tool configs, Python support, dependency manager and lockfile.
- Modified files, existing exceptions and actual automation/CI/hook contracts.

### Mandatory

- Inspect existing Ruff/Black/Flake8/Pylint configuration before running or recommending tools. Respect project choice; migrate only for authorized justified needs, not preference alone.
- Ruff is the recommended new-project lint/format default, not permission to replace an established formatter. Use one authoritative formatter and coherent import-sort behavior.
- Centralize configured rules/line length/Python target/docstring convention in the project's actual config. Match minimum supported Python; do not hard-code py311 or old tool releases.
- Use locked project tools when specified. uvx isolates installation but is not version pinning by itself; exact tool versions must be bound in the command/dependency/hook config when reproducibility requires.
- Lint and formatting check must pass before completion. Run affected tests after fixes; editor-only annotations are not validation evidence.
- Enable agreed docstring rules/convention when configuring a new project; preserve existing exemptions rather than silently enabling unrelated rules across the repository.
- No blanket noqa/type-ignore. Specific suppression needs explanation and review; prefer fixing actual import/type/logic problems.
- Separate check-only from auto-fix commands. Review diffs, never apply unsafe fixes or whole-tree formatting blindly over staged/unrelated changes.
- Fallback tools require a deliberate project decision and documented rule coverage gaps; do not call Black+Flake8 equivalent to every Ruff rule or silently substitute them on tool failure.
- Use existing hooks/CI and keep versions/options consistent; adding/installing hooks or committing requires authorization. Never bypass checks to get a commit through.

### Execution Steps

1. Read tool configuration, automation/hook definitions and current diff; identify actual linter/formatter/version and exceptions.
2. Run configured check-only lint and formatting on changed scope, then required project-wide targets.
3. Diagnose exact codes; apply minimal reviewed safe fixes or manual changes. Preserve behavior and unrelated changes.
4. Recheck formatting/lint/types and affected tests; use specific justified suppressions only for unavoidable cases.
5. Document changed tool config or user-facing behavior and actual verification, including unavailable tools and unresolved errors.

### Validation

- Lint zero errors and format check clean under actual project config/version.
- Target Python matches support; docstrings/imports/exclusions consistent with established policy.
- Fix diffs minimal and tests demonstrate behavior preserved; no unsafe or blanket suppression.
- Hook/CI/local tool versions aligned and commands correct for manager; no false isolation-equals-pin claim.
- No task completion on failed/unexecuted gates; no unauthorized commit/install/tool replacement.

## References

- [Ruff configuration](https://docs.astral.sh/ruff/configuration/)
- [Ruff rules](https://docs.astral.sh/ruff/rules/)
- [Ruff formatter](https://docs.astral.sh/ruff/formatter/)
- [Black](https://black.readthedocs.io/en/stable/)
- [Flake8](https://flake8.pycqa.org/en/latest/)
