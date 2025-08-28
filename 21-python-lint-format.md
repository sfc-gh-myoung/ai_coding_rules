**Description:** Authoritative Python linting and formatting policy using Ruff for code quality and consistency.
**Applies to:** `**/*.py`, `streamlit/**/*`
**Auto-attach:** false

# Python Linting & Formatting (Ruff-first, with fallbacks)

## 1. Core Policy
- **Requirement:** Ruff is the authoritative default for linting and formatting.
- **Requirement:** Centralize Ruff configuration in `pyproject.toml`.
- **Requirement:** Set `target-version = "py311"` and exclude directories like `.venv`, `notebooks`, and `output`.
- **Always:** If Ruff is unavailable, fall back to `flake8` (lint) and `black` + `isort` (format/imports) with equivalent configuration. Document the chosen fallback in the PR.

## 2. Agent Workflow
- **Always:** On every Python file modification or creation, run the linter and formatter.
- **Always:** Prefer `uvx ruff check .` and `uvx ruff format --check .`. If Ruff is unavailable, use `flake8 .` and `black --check .`; fix with `black .` and `isort .`.
- **Requirement:** Ensure imports are organized and unused code is removed.

## 3. Compliance Checklist
- **Always:** Before finalizing any Python code and after any Python file edit, run repo-wide checks that verify:
  - `uvx ruff check .` passes without errors.
  - `uvx ruff format --check .` passes.
  - If a `Taskfile.yml` exists:
    - `task lint` passes.
    - `task format` passes.
  - Fix before reporting success; do not rely on editor-only lints.
  - The final code is idiomatic and correctly formatted.