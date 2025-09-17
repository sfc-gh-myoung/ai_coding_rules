**Description:** Authoritative Python linting and formatting policy using Ruff for code quality and consistency.
**AppliesTo:** `**/*.py`, `streamlit/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

# Python Linting & Formatting (uvx ruff-first, with fallbacks)

## Purpose
Establish authoritative Python code quality standards using Ruff as the primary tool for linting and formatting, with fallback strategies to ensure consistent code style, quality, and maintainability across all Python projects.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Python code linting and formatting with Ruff for consistent code quality and style


## 1. Core Policy
- **Requirement:** Ruff is the authoritative default for linting and formatting.
- **Requirement:** Centralize Ruff configuration in `pyproject.toml`.
- **Requirement:** Set `target-version = "py311"` and exclude directories like `.venv`, `notebooks`, and `output`.
- **Always:** If Ruff is unavailable, fall back to `flake8` (lint) and `black` + `isort` (format/imports) with equivalent configuration. Document the chosen fallback in the PR.

## 2. Agent Workflow
- **Always:** On every Python file modification or creation, run the linter and formatter.
- **Always:** Use `uvx ruff check .` and `uvx ruff format --check .` for isolated tool execution.
- **Always:** Use `uvx ruff check --fix .` and `uvx ruff format .` to apply fixes.
- **Consider:** If Ruff is unavailable, use `flake8 .` and `black --check .`; fix with `black .` and `isort .`.
- **Requirement:** Ensure imports are organized and unused code is removed.
- **Rule:** Never use project-installed ruff via `uv run`; always use isolated `uvx ruff` for consistency.

## 3. Compliance Checklist
- **Always:** Before finalizing any Python code and after any Python file edit, run repo-wide checks that verify:
  - `uvx ruff check .` passes without errors.
  - `uvx ruff format --check .` passes.
  - If a `Taskfile.yml` exists:
    - `task lint` passes (should use `uvx ruff` internally).
    - `task format` passes (should use `uvx ruff` internally).
  - Fix before reporting success; do not rely on editor-only lints.
  - The final code is idiomatic and correctly formatted.

## 4. Taskfile Integration
- **Requirement:** Taskfile lint tasks must use `uvx ruff` for tool isolation.
- **Requirement:** Separate check and fix tasks for better workflow control.
- **Pattern:** Structure linting tasks to provide both check-only and fix modes.

### Taskfile Example Pattern
```yaml
lint-ruff:
  desc: "Run ruff linter and formatter checks"
  cmds:
    - uvx ruff check .
    - uvx ruff format --check .

format:
  desc: "Auto-format code with ruff"
  cmds:
    - uvx ruff format .
    - uvx ruff check --fix .

lint:
  desc: "Run all code quality checks"
  cmds:
    - task: lint-ruff
    - task: lint-mypy  # uv run mypy for project dependencies
```

## 5. Tool Isolation Benefits
- **Benefit:** `uvx ruff` ensures consistent tool versions across environments.
- **Benefit:** Avoids conflicts with project dependencies.
- **Benefit:** Faster execution without project environment overhead.
- **Rule:** Use `uvx` for development tools, `uv run` for project code execution.

## References

### External Documentation
- [Ruff Documentation](https://docs.astral.sh/ruff/) - Complete linter and formatter configuration guide
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/) - Comprehensive list of linting rules and error codes                                                                                                      
- [Python Code Style PEP 8](https://peps.python.org/pep-0008/) - Official Python style guide standards

### Related Rules
- **Python Core**: `200-python-core.md`
- **Project Setup**: `203-python-project-setup.md`
