# Python Core Engineering Directives

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Python patterns. Load for Python tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.1.1
**LastUpdated:** 2026-03-26
**Keywords:** Python, uv, Ruff, pyproject.toml, dependency management, virtual environments, pytest, validation, uv run, uvx, ty, type checking, mypy, type hints
**TokenBudget:** ~3600
**ContextTier:** Critical
**Depends:** 000-global-core.md
**LoadTrigger:** ext:.py, ext:.pyi, file:pyproject.toml

## Scope

**What This Rule Covers:**
Foundational Python development practices: investigation-first toolchain detection, modern Python patterns (datetime.now(UTC), collections.abc, dict/list annotations), error handling, code structure, and the mandatory validation gate reference. For detailed validation commands see 200a; for environment and tooling details see 200b.

**When to Load This Rule:**
- Modifying Python files (.py)
- Python project setup and configuration
- Dependency management with uv
- Testing with pytest
- Linting and formatting with Ruff
- pyproject.toml configuration
- Implementing Python best practices and modern patterns

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates

**Recommended:**
- **200a-python-validation-gate.md** - Pre-Task-Completion Validation Gate and type checking
- **200b-python-environment-tooling.md** - Virtual environments, tool isolation, troubleshooting
- **201-python-lint-format.md** - Detailed Ruff linting and formatting patterns
- **203-python-project-setup.md** - Project structure and initialization patterns

**Related:**
- **202-markup-config-validation.md** - YAML and configuration file validation
- **204-python-docs.md** - Documentation and docstring standards
- **206-python-pytest.md** - Comprehensive testing patterns with pytest

### External Documentation

**Official Documentation:**
- [Python Official Documentation](https://docs.python.org/3/) - Official Python documentation
- [uv Documentation](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- [Ruff Documentation](https://docs.astral.sh/ruff/) - Extremely fast Python linter and formatter
- [ty Documentation](https://docs.astral.sh/ty/) - Extremely fast Python type checker (Astral toolchain)

## Contract

### Inputs and Prerequisites

- Python 3.11+ available (or project's specified version)
- Project's dependency manager installed (uv, poetry, pip, pipenv)
- `pyproject.toml` present (or creating new project)
- Target Python files or project structure identified

### Toolchain Detection (Investigation-First)

**Before prescribing tools, investigate project's existing toolchain:**

1. **Read pyproject.toml** for existing dependencies and tool configurations
2. **Check for lock files** to identify the dependency manager:
   - `uv.lock` — Project uses **uv** — Run prefix: `uv run` — Tool prefix: `uvx`
   - `poetry.lock` — Project uses **poetry** — Run prefix: `poetry run` — Tool prefix: `poetry run`
   - `Pipfile.lock` — Project uses **pipenv** — Run prefix: `pipenv run`
   - `requirements.txt` only — Project uses **pip** — Run prefix: `python` (venv active)
3. **Respect project's existing choices** unless explicitly asked to change

**Recommended for NEW projects:** uv + Ruff + ty (Astral ecosystem: fast, modern, comprehensive)

**Rule:** Match project's existing toolchain. Only recommend changes when the user explicitly asks, the project has no established toolchain, or the existing toolchain causes problems.

### Mandatory (Universal Requirements)

These requirements apply regardless of toolchain choice:

- Apply consistent linting and formatting to all modified Python files
- Apply type checking to all modified Python files
- Run test suite for projects with tests
- Centralize configuration in `pyproject.toml`
- Use `datetime.now(UTC)` instead of deprecated `datetime.utcnow()`
- Run validation via the project's automation entrypoint if present (see `000-global-core.md` automation-detection protocol); if no automation file exists, run tools directly
- Pass Pre-Task-Completion Validation Gate before marking any task complete (see **200a-python-validation-gate.md**)

### Forbidden

- Never skip Pre-Task-Completion Validation Gate (lint, format, type check, tests)
- Never use deprecated `datetime.utcnow()` (use `datetime.now(UTC)`)
- Never hard-code secrets or credentials
- Never use broad `except:` clauses that swallow exceptions
- Never ignore project's established toolchain without justification
- Never prescribe specific tools (uv, poetry) without checking existing setup

### Execution Steps

1. **Investigation:** Read `pyproject.toml` and check for lock files to identify project's toolchain (uv, poetry, pip)
2. **Environment Setup:** Use project's dependency manager to ensure environment is ready (see **200b-python-environment-tooling.md**)
3. **Implementation:** Write or modify Python code following modern patterns (type hints, clear error handling, modular structure)
4. **Validation:** Run comprehensive validation suite using project's toolchain (see **200a-python-validation-gate.md**)
5. **Documentation:** Update CHANGELOG.md for user-facing behavior changes, dependency version bumps, or API modifications; update README.md when CLI usage, setup instructions, or configuration options change
6. **Verification:** Confirm all validation checks pass before task completion

### Output Format

```python
# Investigation: Check current implementation
# Read existing files, understand patterns

# Implementation: Following uv + ruff + pytest standards
from typing import Protocol
from datetime import datetime, UTC

class ServiceProtocol(Protocol):
    """Clear contract for service implementations."""

    def process(self, data: dict) -> dict:
        """Process data following validation rules."""
        ...

def implementation_function(input_data: dict) -> dict:
    """
    Implement feature following project conventions.

    Args:
        input_data: Validated input following schema

    Returns:
        Processed result with metadata

    Raises:
        ValueError: If input validation fails
    """
    # Use datetime.now(UTC) not datetime.utcnow()
    timestamp = datetime.now(UTC)

    # Implement business logic
    result = {"status": "success", "timestamp": timestamp}
    return result
```

### Validation

See **200a-python-validation-gate.md** for the full Pre-Task-Completion Validation Gate.

**Investigation Required:**
1. **Read pyproject.toml BEFORE making recommendations** - Check existing dependencies, Python version, tool configurations
2. **Verify toolchain** - Check if project uses uv, poetry, or pip
3. **Never speculate about project structure** - List directory contents to understand src/ vs flat layout
4. **Check existing tests** - Read conftest.py, test files to understand test patterns
5. **Make grounded recommendations based on investigated project setup** - Match existing patterns and toolchain
6. **Check for async code** - If async/await found, reference the Async/Await Patterns section in this rule; if project uses FastAPI, also load 210-python-fastapi-core.md
7. **Check for type checking configuration** - If `ty.toml` or `[tool.ty]` found, use `ty check`; if `mypy.ini` or `[tool.mypy]` found, use `mypy .`; if `pyrightconfig.json` found, use `pyright`; if none found, default to `ty check`
8. **Verify virtual environment is active** - Run `which python` to confirm

### Design Principles

- **Investigation-First:** Check project's existing toolchain before prescribing tools
- **Toolchain Respect:** Match project's dependency manager (uv, poetry, pip)
- **Python Version:** Pin the Python version from `pyproject.toml`'s `requires-python` field; if absent, default to `>=3.11`
- **Code Quality:** Apply consistent linting and formatting on every file modification
- **Type Safety:** Apply type checking on every file modification for static type safety
- **Validation First:** Never mark tasks complete without passing Pre-Task-Completion Validation Gate

### Post-Execution Checklist

- [ ] Rule dependencies loaded (000-global-core.md)
- [ ] Project's toolchain identified (uv, poetry, pip)
- [ ] Linting passed with zero errors
- [ ] Formatting check passed
- [ ] Type checking passed with zero type errors
- [ ] All tests passed (if test suite exists)
- [ ] CHANGELOG.md updated for code changes

### Starter pyproject.toml Template (New Projects)

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

[tool.ruff.lint.pydocstyle]
convention = "google"
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Ignoring Project's Existing Toolchain

```bash
# Bad: Forcing uv on a poetry project
# Found poetry.lock in project
# Still running: uv run python script.py
```

**Problem:** Breaks project's established conventions; may cause dependency version conflicts; ignores team's toolchain decisions

**Correct Pattern:**
```bash
# Good: Detect and respect project's toolchain
# Step 1: Check for lock files
ls -la | grep -E '(uv.lock|poetry.lock|Pipfile.lock)'
# Step 2: Use appropriate commands based on detected toolchain
```

### Anti-Pattern 2: Using Deprecated `datetime.utcnow()`

```python
# Bad: Using deprecated datetime API
from datetime import datetime
timestamp = datetime.utcnow()  # Deprecated in Python 3.12+
```

**Problem:** Deprecated API; naive datetime (no timezone info)

**Correct Pattern:**
```python
# Good: Use timezone-aware datetime with UTC
from datetime import datetime, UTC
timestamp = datetime.now(UTC)  # Modern, timezone-aware
```

### File Operations with Pathlib

Always use `pathlib.Path` for file operations:

```python
from pathlib import Path

# Reading files
config = Path("config.toml")
if config.exists():
    content = config.read_text(encoding="utf-8")

# Writing files
output = Path("output") / "results.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(data), encoding="utf-8")

# Iterating files
for py_file in Path("src").rglob("*.py"):
    process(py_file)
```

**Forbidden:** `os.path.join()`, `open()` with string paths (use `Path.open()` or `Path.read_text()`).

## Code Structure and Style Guidelines

- **Rule:** Keep modules small and cohesive (target <300 lines).
- **Rule:** Use explicit, absolute imports.
- **Rule:** Avoid global mutable state; prefer immutable data flow.
- **Rule:** Manage configuration via environment variables or a config module. Never hard-code secrets.

## Error Handling and Reliability

- **Always:** Raise specific exceptions with actionable context.
- **Rule:** Avoid broad `except:` clauses or silently passing exceptions.
- **Rule:** Do not swallow exceptions; re-raise with added context when necessary.
- Use structural pattern matching (`match`/`case`) for complex conditionals:

```python
# Prefer match/case over long if/elif chains
match command:
    case {"action": "create", "name": str(name)}:
        create_resource(name)
    case {"action": "delete", "id": int(id_)}:
        delete_resource(id_)
    case {"action": action}:
        raise ValueError(f"Unknown action: {action}")
    case _:
        raise ValueError("Invalid command format")
```

### State and Resource Error Handling

**If lock file conflict** (e.g., `uv.lock` modified during operation):
1. Abort current operation
2. Re-read lock file to verify state
3. Retry operation once; if conflict persists, report to user

**If partial write** (file operation interrupted):
1. Check file integrity: `python -c "import ast; ast.parse(open('file.py').read())"`
2. If corrupt, restore from git: `git checkout -- file.py`
3. Re-apply changes surgically

**If disk space exhausted** during dependency install or file write:
1. Check available space: `df -h .`
2. Clear caches: `uv cache clean` (uv) or `pip cache purge` (pip)
3. If still insufficient, report with required space estimate

**If memory pressure** during large file processing:
1. Process files in batches (<1000 lines per chunk)
2. Use generators instead of loading full collections into memory
3. If OOM persists, reduce scope and report to user

### Async/Await Patterns

When working with async Python code:

```python
import asyncio
from collections.abc import AsyncIterator


async def fetch_data(url: str) -> dict[str, Any]:
    """Fetch data from API endpoint.

    Args:
        url: The API endpoint URL.

    Returns:
        Parsed JSON response as dictionary.

    Raises:
        httpx.HTTPStatusError: If response status is not 2xx.
    """
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def process_items(items: list[str]) -> AsyncIterator[str]:
    """Process items concurrently with controlled concurrency.

    Args:
        items: List of items to process.

    Yields:
        Processed item results.
    """
    semaphore = asyncio.Semaphore(10)

    async def _process(item: str) -> str:
        async with semaphore:
            await asyncio.sleep(0.1)  # Simulate I/O
            return item.upper()

    tasks = [asyncio.create_task(_process(item)) for item in items]
    for task in asyncio.as_completed(tasks):
        yield await task
```

**Key async rules:**
- Use `async with` for async context managers (httpx, aiofiles)
- Use `asyncio.Semaphore` to limit concurrency
- Use `collections.abc.AsyncIterator` for async generator return types
- Never use `asyncio.run()` inside an already-running event loop

## Modern Python Patterns

- **Critical:** Use `datetime.now(UTC)` instead of deprecated `datetime.utcnow()` for timezone-aware timestamps.
- **Always:** Import from `collections.abc` instead of `typing` for abstract base classes (e.g., `AsyncGenerator`).
- **Always:** Use `dict` and `list` for type annotations instead of `Dict` and `List` from typing.
- **Always:** Follow Python 3.11+ patterns and avoid deprecated functionality.

### Complete Module Example

```python
"""User management module demonstrating all core patterns.

Combines modern type annotations, proper error handling,
datetime usage, and structural patterns from this rule.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_users(config_path: Path) -> list[dict[str, Any]]:
    """Load users from configuration file.

    Args:
        config_path: Path to the user configuration file.

    Returns:
        List of user dictionaries with validated fields.

    Raises:
        FileNotFoundError: If config_path does not exist.
        ValueError: If configuration format is invalid or users list is empty.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    import tomllib
    with config_path.open("rb") as f:
        data = tomllib.load(f)

    if "users" not in data:
        raise ValueError("Missing 'users' key in configuration")

    raw_users: list[dict[str, Any]] = data["users"]
    if len(raw_users) == 0:
        return []

    return [
        {
            "name": u["name"],
            "created_at": datetime.now(UTC),
            "active": u.get("active", True),
        }
        for u in raw_users
        if u.get("name") and isinstance(u["name"], str)
    ]


def filter_active(users: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter to only active users.

    Args:
        users: Sequence of user dictionaries.

    Returns:
        List containing only users where active is True.
    """
    return [u for u in users if u.get("active", False)]
```

## Performance Optimization

- **Rule:** Separate I/O and CPU concerns. Prefer set-based SQL and vectorization over Python loops.
- **Rule:** Ensure code is idiomatic and follows PEP 8.
- **Rule:** Include comprehensive type hints.
- **Rule:** Follow Python documentation standards from `204-python-docs.md` (Google-style docstrings for all public APIs, enforced via Ruff D-rules).
