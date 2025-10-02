**Description:** Core Python engineering policies for a consistent, reliable, and performant codebase using modern tools like `uv` and Ruff.
**AppliesTo:** `**/*.py`, `streamlit/**/*`, `scripts/**/*`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.3
**LastUpdated:** 2025-09-22

# Python Core Engineering Directives

## Contract
- **Inputs/Prereqs:** Python 3.11+; `uv` installed; `pyproject.toml` present
- **Allowed Tools:** `uv run`, `uvx` for tools; Taskfile tasks
- **Forbidden Tools:** Bare `python`, `pytest`, `ruff` without `uv run`/`uvx`
- **Required Steps:**
  1. Pin and sync environment with `uv`
  2. Execute Python and tests via `uv run`
  3. Lint/format via `uvx ruff`
  4. Centralize config in `pyproject.toml`
- **Output Format:** Commands, diffs, or code snippets only (no narrative unless requested)
- **Validation Steps:** `uvx ruff check .` passes; `uvx ruff format --check .` passes; `uv run pytest` passes

## Purpose
Establish foundational Python development practices using modern tooling like `uv` and Ruff to ensure consistent, reliable, and performant codebases with proper dependency management, linting, formatting, and project structure.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Foundational Python development practices with modern tooling (uv, Ruff) and project structure


## Key Principles
- Use `uv` for all dependency and environment management; `uvx` for isolated tool execution
- Pin Python 3.11+ and centralize configuration in `pyproject.toml`
- Apply Ruff linting and formatting on every file modification
- Structure code with clear modules, proper error handling, and modern Python patterns
- Integrate with Taskfile for consistent automation across projects

## 1. Environment & Tooling
- **Requirement:** Use `uv` for all dependency and environment management.
- **Requirement:** Pin Python to 3.11+ in `.python-version` and `pyproject.toml`.
- **Requirement:** Use `uvx` for isolated tool execution (ruff, pytest, safety, etc.).
- **Requirement:** Use `uv run` for all project scripts and Python execution.
- **Requirement:** Use `uv sync --all-groups` for dependency installation.
- **Requirement:** Use `uv lock` for dependency resolution and updates.
- **Requirement:** Use an authoritative linter and formatter.
- **Requirement:** Centralize dependencies and configuration in `pyproject.toml`.
- **Consider:** If `uv` is unavailable, use `pip` + `pip-tools` or `poetry`. Provide equivalent commands when giving setup instructions.

## 2. Virtual Environment Activation
- **Critical:** Always use `uv run` to execute Python code in projects. Never run `python` directly.
- **Critical:** All Python execution must go through the proper virtual environment to avoid `ModuleNotFoundError`.
- **Requirement:** Use `uv run python` instead of bare `python` for all scripts, imports, and testing.
- **Requirement:** Use `uv run uvicorn` instead of bare `uvicorn` for FastAPI/ASGI servers.
- **Requirement:** Use `uv run pytest` instead of bare `pytest` for testing.
- **Requirement:** Use `uv run mypy` instead of bare `mypy` for type checking.

### 2.1 Tool Isolation vs Project Environment (uv run vs uvx)

- **Rule:** Use `uv run` when the command needs access to the project environment (installed dependencies, project package imports, or plugins declared in `pyproject.toml`).
- **Rule:** Use `uvx` for standalone tools that do not import your project code and do not require project-installed plugins.

When to use `uv run` (project venv):
- The command imports your project package/modules (e.g., `pytest`, `uvicorn app.main:app`, `python -m yourpkg`).
- The tool relies on plugins or integrations defined in `pyproject.toml` or installed in the project venv (e.g., `pytest` plugins, `mypy` plugins, Sphinx extensions).
- You need the exact dependency set and versions pinned by your project lockfile.

Examples (project environment):
- `uv run pytest tests/`  # discovers and loads project/third-party pytest plugins
- `uv run mypy src/`      # uses mypy plugins/config from project dependencies
- `uv run uvicorn app.main:app --reload`  # imports your app package
- `uv run python -m yourpkg.tool`         # runs code that imports your package

When to use `uvx` (isolated tool context):
- The tool is self-contained and does not import your project code.
- The tool does not require project-installed plugins; any needed integrations are provided by the tool itself.

Examples (isolated tools):
- `uvx ruff check .` and `uvx ruff format .`  # linter/formatter runs independently
- `uvx black .`                               # formatter without importing project code
- `uvx safety check`                          # dependency vulnerability scan

Common pitfalls and guidance:
- **Important:** `uvx` runs tools in an isolated context. It does not automatically include your project venv or its extra modules/plugins. If a tool fails to find a plugin or cannot import your package, switch to `uv run`.
- If a command needs both a standalone tool and project imports, prefer `uv run` to ensure your project environment is available.
- Keep configuration centralized in `pyproject.toml`, but remember that only `uv run` guarantees access to project-installed integrations referenced there.

Quick decision guide:
- Imports project code or needs project plugins? → Use `uv run ...`
- Pure external tool, no project imports/plugins? → Use `uvx ...`

### Command Patterns
**CORRECT:**
```bash
# Project execution
uv run python script.py
uv run python -c "import app; print('success')"
uv run uvicorn app.main:app --reload
uv run pytest tests/
uv run mypy src/

# Isolated tools
uvx ruff check .
uvx ruff format .
uvx safety check
uvx black .

# Environment management
uv python pin 3.11
uv sync --all-groups
uv lock --upgrade
```

**INCORRECT:**
```bash
python script.py                    # Missing uv run
python -c "import app"              # Missing uv run  
uvicorn app.main:app --reload       # Missing uv run
pytest tests/                       # Missing uv run
ruff check .                        # Should use uvx for isolation
```

### Environment Setup Best Practices
- **Always:** Start projects with `uv python pin 3.11` to set Python version.
- **Always:** Use `uv sync --all-groups` to install all dependencies including dev tools.
- **Always:** Use status checks in automation to avoid redundant environment setup.
- **Rule:** Use `uv lock` before `uv sync` to ensure consistent dependency resolution.

### Troubleshooting Environment Issues
- **Rule:** If you encounter `ModuleNotFoundError`, always check if `uv run` was used.
- **Rule:** Use `uv run python -c "import module_name"` to test module availability.
- **Rule:** Use `uv sync` to ensure dependencies are installed before running code.
- **Rule:** For Taskfile automation, use preconditions to check for `.venv` directory existence.

## 3. Code Structure & Style
- **Requirement:** Keep modules small and cohesive (target <300 lines).
- **Requirement:** Use explicit, absolute imports.
- **Requirement:** Avoid global mutable state; prefer immutable data flow.
- **Requirement:** Manage configuration via environment variables or a config module. Never hard-code secrets.

## 4. Reliability & Exceptions
- **Always:** Raise specific exceptions with actionable context.
- **Requirement:** Avoid broad `except:` clauses or silently passing exceptions.
- **Requirement:** Do not swallow exceptions; re-raise with added context when necessary.

### 4.1 Syntax Validation
- **Requirement:** Before completing any task involving Python code changes, verify that all modified files are syntactically correct.
- **Rule:** Use `python -m py_compile` as a definitive check for syntax errors, in addition to linter feedback. This ensures the Python interpreter can parse the file without error. If a file fails to compile, the issue must be resolved.
- **Command:** `uv run python -m py_compile -q <path-to-file-or-dir>`

## 5. Performance & Best Practices
- **Requirement:** Separate I/O and CPU concerns. Prefer set-based SQL and vectorization over Python loops.
- **Requirement:** Ensure code is idiomatic and follows PEP 8.
- **Requirement:** Include comprehensive type hints.
- **Requirement:** Use Google-style docstrings for public modules, classes, and methods.

## 6. Modern Python Patterns
- **Critical:** Use `datetime.now(UTC)` instead of deprecated `datetime.utcnow()` for timezone-aware timestamps.
- **Always:** Import from `collections.abc` instead of `typing` for abstract base classes (e.g., `AsyncGenerator`).
- **Always:** Use `dict` and `list` for type annotations instead of `Dict` and `List` from typing.
- **Always:** Follow Python 3.11+ patterns and avoid deprecated functionality.

## 7. Taskfile Integration
- **Requirement:** Use `uv run` prefix for all Python commands in Taskfile tasks.
- **Requirement:** Use `uvx` for all development tools (ruff, pytest, mypy, safety).
- **Always:** Include environment setup tasks with status checks to avoid redundant operations.
- **Pattern:** Structure tasks as: `uv:pin` then `install` (with `uv sync`) then execution tasks.

## Quick Compliance Checklist
- [ ] Python 3.11+ is pinned in .python-version file
- [ ] Dependencies managed through uv (pyproject.toml with dependency-groups)
- [ ] Ruff configured in pyproject.toml with target-version = "py311"
- [ ] Code passes `uvx ruff check .` and `uvx ruff format --check .`
- [ ] Tests run with `uv run pytest` and pass
- [ ] All Python files are syntactically valid (checked with `py_compile`)
- [ ] Virtual environment created with `uv venv` (not python -m venv)
- [ ] Dependencies synced with `uv sync --all-groups`
- [ ] No bare pip install commands in documentation
- [ ] Import paths use absolute imports where possible
- [ ] Project follows modern Python packaging standards

## Validation
- **Syntax Check:** `uv run python -m py_compile -q .` (must pass)
- **Lint & Format:** `uvx ruff check .` and `uvx ruff format --check .` (must pass)
- **Tests:** `uv run pytest`
- **Import Check:** `uv run python -c "import importlib; print('ok')"`

## Response Template
```