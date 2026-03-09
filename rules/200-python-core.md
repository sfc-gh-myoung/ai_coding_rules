# Python Core Engineering Directives

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Python patterns. Load for Python tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Python, uv, Ruff, pyproject.toml, dependency management, virtual environments, pytest, validation, uv run, uvx, ty, type checking, mypy, type hints
**TokenBudget:** ~2350
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
- **204-python-docs-comments.md** - Documentation and docstring standards
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

**Rule:** Match project's existing tooling. Only recommend changes when the user explicitly asks, the project has no established toolchain, or the existing toolchain causes problems.

### Mandatory (Universal Requirements)

These requirements apply regardless of tooling choice:

- Apply consistent linting and formatting to all modified Python files
- Apply type checking to all modified Python files
- Run test suite for projects with tests
- Centralize configuration in `pyproject.toml`
- Use `datetime.now(UTC)` instead of deprecated `datetime.utcnow()`
- Integrate with project's task automation (Taskfile, Makefile, etc.)
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
5. **Documentation:** Update CHANGELOG.md and README.md as required
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
3. **Never speculate about project structure** - Use list_dir to understand src/ vs flat layout
4. **Check existing tests** - Read conftest.py, test files to understand test patterns
5. **Make grounded recommendations based on investigated project setup** - Match existing patterns and tooling

### Design Principles

- **Investigation-First:** Check project's existing toolchain before prescribing tools
- **Toolchain Respect:** Match project's dependency manager (uv, poetry, pip)
- **Python Version:** Pin appropriate Python version in `pyproject.toml`
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

**Problem:** Breaks project's established conventions; may cause dependency version conflicts; ignores team's tooling decisions

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

## Code Structure and Style Guidelines

- **Rule:** Keep modules small and cohesive (target <300 lines).
- **Rule:** Use explicit, absolute imports.
- **Rule:** Avoid global mutable state; prefer immutable data flow.
- **Rule:** Manage configuration via environment variables or a config module. Never hard-code secrets.

## Error Handling and Reliability

- **Always:** Raise specific exceptions with actionable context.
- **Rule:** Avoid broad `except:` clauses or silently passing exceptions.
- **Rule:** Do not swallow exceptions; re-raise with added context when necessary.

## Modern Python Patterns

- **Critical:** Use `datetime.now(UTC)` instead of deprecated `datetime.utcnow()` for timezone-aware timestamps.
- **Always:** Import from `collections.abc` instead of `typing` for abstract base classes (e.g., `AsyncGenerator`).
- **Always:** Use `dict` and `list` for type annotations instead of `Dict` and `List` from typing.
- **Always:** Follow Python 3.11+ patterns and avoid deprecated functionality.

## Performance Optimization

- **Rule:** Separate I/O and CPU concerns. Prefer set-based SQL and vectorization over Python loops.
- **Rule:** Ensure code is idiomatic and follows PEP 8.
- **Rule:** Include comprehensive type hints.
- **Rule:** Follow Python documentation standards from `204-python-docs-comments.md` (Google-style docstrings for all public APIs, enforced via Ruff D-rules).
