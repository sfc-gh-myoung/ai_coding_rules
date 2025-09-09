**Description:** Core Python engineering policies for a consistent, reliable, and performant codebase using modern tools like `uv` and Ruff.
**Applies to:** `**/*.py`, `streamlit/**/*`, `scripts/**/*`
**Auto-attach:** false

# Python Core Engineering Directives

## 1. Environment & Tooling
- **Requirement:** Use `uv` for all dependency and environment management.
- **Requirement:** Pin Python to 3.11+ in `.python-version` and `pyproject.toml`.
- **Requirement:** Use `uvx` for one-off tools and `uv run` for project scripts.
- **Requirement:** Use an authoritative linter and formatter.
- **Requirement:** Centralize dependencies and configuration in `pyproject.toml`.
- **Recommended:** If `uv` is unavailable, use `pip` + `pip-tools` or `poetry`. Provide equivalent commands when giving setup instructions.

## 2. Virtual Environment Activation
- **CRITICAL:** Always use `uv run` to execute Python code in projects. Never run `python` directly.
- **CRITICAL:** All Python execution must go through the proper virtual environment to avoid `ModuleNotFoundError`.
- **Requirement:** Use `uv run python` instead of bare `python` for all scripts, imports, and testing.
- **Requirement:** Use `uv run uvicorn` instead of bare `uvicorn` for FastAPI/ASGI servers.
- **Requirement:** Use `uv run pytest` instead of bare `pytest` for testing.

### Command Patterns
**CORRECT:**
```bash
uv run python script.py
uv run python -c "import app; print('success')"
uv run uvicorn app.main:app --reload
uv run pytest tests/
uv run python -m pytest
```

**INCORRECT:**
```bash
python script.py                    # Missing uv run
python -c "import app"              # Missing uv run  
uvicorn app.main:app --reload       # Missing uv run
pytest tests/                       # Missing uv run
```

### Troubleshooting Environment Issues
- **Rule:** If you encounter `ModuleNotFoundError`, always check if `uv run` was used.
- **Rule:** Use `uv run python -c "import module_name"` to test module availability.
- **Rule:** Use `uv sync` to ensure dependencies are installed before running code.

## 3. Code Structure & Style
- **Requirement:** Keep modules small and cohesive (target <300 lines).
- **Requirement:** Use explicit, absolute imports.
- **Requirement:** Avoid global mutable state; prefer immutable data flow.
- **Requirement:** Manage configuration via environment variables or a config module. Never hard-code secrets.

## 4. Reliability & Exceptions
- **Always:** Raise specific exceptions with actionable context.
- **Requirement:** Avoid broad `except:` clauses or silently passing exceptions.
- **Requirement:** Do not swallow exceptions; re-raise with added context when necessary.

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

## 7. Related Specialized Rules
- **Rule:** For deeper guidance, see:
  - **Linting & Formatting:** `21-python-lint-format.md` (Ruff policy).