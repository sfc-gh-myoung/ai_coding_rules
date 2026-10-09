---
schema_version: v4.0
rule_version: v6.0.0
description: 'Python core: toolchain detection, datetime UTC, collections.abc imports, error handling, and mandatory validation gate.'
last_updated: 2026-10-06
keywords:
  - kw:pyproject.toml
  - kw:toolchain detection
  - kw:datetime.now(UTC)
  - kw:collections.abc imports
  - kw:dict list annotations
  - kw:pathlib file operations
  - ext:.py
token_budget: ~2200
context_tier: Critical
depends:
  required:
    - 000-global-core.md
  optional:
    - 200a-python-validation-gate.md
    - 206-python-pytest.md
    - 201-python-lint-format.md
---
# Python Core Engineering Directives

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Python patterns. Load for Python tasks.
> Specialized rules depend on this foundation.

## Scope

**What This Rule Covers:**
Foundational Python development practices: investigation-first toolchain detection, modern Python patterns (`datetime.now(UTC)`, `collections.abc`, `dict`/`list` annotations, `pathlib`), error handling, and the mandatory validation gate reference. For detailed validation commands see `200a`; for environment and tooling details see `200b`.

**When to Load This Rule:**
- Modifying Python files (`.py`)
- Python project setup, dependency management (uv, poetry, pip, pipenv)
- `pyproject.toml` configuration
- Testing with pytest; linting/formatting with Ruff; type checking with ty, mypy, or pyright

## Contract

### Inputs and Prerequisites

- Python 3.11+ (or project's pinned version from `requires-python` in `pyproject.toml`)
- Project dependency manager installed (uv, poetry, pip, or pipenv)
- `pyproject.toml` present or being created
- Target Python files or project structure identified

### Mandatory

**Toolchain detection (investigation-first) — before prescribing tools:**

1. Read `pyproject.toml` for existing tool configurations and `requires-python`
2. Check for lock files to identify the dependency manager:
   - `uv.lock` present: use uv (`uv run` prefix; `uvx` for tools)
   - `poetry.lock` present: use poetry (`poetry run` prefix)
   - `Pipfile.lock` present: use pipenv (`pipenv run` prefix)
   - `requirements.txt` only: use pip (active venv, `python` prefix)
3. Respect the project's existing toolchain; recommend changes only when explicitly asked, no toolchain exists, or the existing one causes problems
4. If supplied files cannot establish a dependency manager, report it unknown; do not assume pip/venv or invent a lock file. Read-only design never authorizes environment creation or installation.
5. Missing pytest configuration does not prove tests are absent. If test files were not supplied or inspected, report suite presence unknown and require test discovery before implementation completion.

**Recommended for new projects:** uv + Ruff + ty (Astral ecosystem)

**Universal requirements — apply to all modified Python files:**
- Apply linting, formatting, and type checking to all modified `.py` files
- Run the test suite when one exists
- Centralize all tool configuration in `pyproject.toml`
- Use `datetime.now(UTC)` — never `datetime.utcnow()` (deprecated in Python 3.12+)
- Import abstract base classes from `collections.abc`, not `typing`
- Use `dict` and `list` for type annotations — not `Dict` or `List` from `typing`
- Use `pathlib.Path` for all file operations — not `os.path.join()` or bare `open()` with string paths
- Detect type checker: `ty.toml`/`[tool.ty]` present: `ty check`; `mypy.ini`/`[tool.mypy]`: `mypy`; `pyrightconfig.json`: `pyright`; none found: `ty check`
- Pass the Pre-Task-Completion Validation Gate before marking any task complete (see **200a-python-validation-gate.md**)

### Forbidden

- Skipping the Pre-Task-Completion Validation Gate (lint, format, type check, tests)
- Using `datetime.utcnow()` (deprecated — use `datetime.now(UTC)` with `from datetime import UTC`)
- Hard-coding secrets or credentials
- Broad `except:` or `except Exception:` clauses that swallow exceptions silently
- Prescribing specific tools (uv, poetry) without first detecting the project's existing toolchain
- Using `os.path.join()` or bare `open(path_str)` instead of `pathlib.Path` operations

### Execution Steps

1. **Detect toolchain:** read `pyproject.toml` and check for lock files to identify the dependency manager and Python version
2. **Prepare environment:** activate or create virtualenv; install dependencies using the detected manager (see **200b-python-environment-tooling.md**)
3. **Inspect before recovery:** If a write was interrupted, read the source/ownership beforeimage and call the authorized state-inspection tool before any edit, including a syntax repair. Do not perform step 4 first; later inspection cannot establish the pre-edit state.
4. **Implement:** write or modify Python code using modern patterns — type hints, `datetime.now(UTC)`, `collections.abc`, pathlib, specific exceptions
5. **Validate:** run full validation via the project's automation entrypoint; if none, run tools directly (see **200a-python-validation-gate.md**)
6. **Recover from validation failures:** inspect the current file and staged diff before changing anything; parse Python with `ast.parse` using the configured interpreter. Restore only bytes owned by this task from a verified beforeimage, then rerun applicable checks. If ownership or the outcome is uncertain, stop and report; never overwrite staged or unrelated edits with a whole-file Git restore.
   - When an interrupted-write task provides an authorized `inspect_state` tool, call it after required source/ownership reads and before any recovery edit. Reading the truncated source alone does not establish the outcome of the uncertain write.
   - Distinguish observed output from inferred cause. A fixed synthetic check does not execute the repaired code; report its exact failure and keep verification unresolved. Do not blame unrelated staged work or claim runtime correctness from a plausible edit without executing an authorized real check.
7. **Document:** update `CHANGELOG.md` for user-facing behavior changes, dependency bumps, or API modifications; update `README.md` when CLI usage, setup, or configuration options change

### Validation

See **200a-python-validation-gate.md** for the full Pre-Task-Completion Validation Gate.

**Required checks before marking any task complete:**
- [ ] Project toolchain identified (lock file detected or `pyproject.toml` inspected)
- [ ] Linting passed (zero errors)
- [ ] Formatting check passed
- [ ] Type checking passed (zero errors)
- [ ] All tests passed (if test suite exists)
- [ ] `pyproject.toml` is the authoritative configuration source
- [ ] No deprecated patterns introduced (`datetime.utcnow()`, `typing.Dict`/`List`, etc.)

**Example — modern Python module combining mandatory patterns:**

```python
from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def load_users(config_path: Path) -> list[dict[str, Any]]:
    """Load users from a TOML config file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    import tomllib

    with config_path.open("rb") as f:
        data = tomllib.load(f)
    if "users" not in data:
        raise ValueError("Missing 'users' key in configuration")
    return [
        {"name": u["name"], "created_at": datetime.now(UTC), "active": u.get("active", True)}
        for u in data["users"]
        if isinstance(u.get("name"), str)
    ]


def filter_active(users: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return only active users."""
    return [u for u in users if u.get("active", False)]
```

**Starter `pyproject.toml` for new projects:**

```toml
[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.4.0"]

[tool.ruff]
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "D"]
```

## References

### External Documentation

- [Python Official Documentation](https://docs.python.org/3/) — Language reference and standard library
- [uv Documentation](https://github.com/astral-sh/uv) — Fast Python package manager
- [Ruff Documentation](https://docs.astral.sh/ruff/) — Fast Python linter and formatter
- [ty Documentation](https://docs.astral.sh/ty/) — Fast Python type checker (Astral)
