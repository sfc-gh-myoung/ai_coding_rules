# Python Core Engineering Directives

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Python patterns. Load for Python tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** Python, uv, Ruff, pyproject.toml, dependency management, virtual environments, pytest, validation, uv run, uvx, ty, type checking, mypy, type hints
**TokenBudget:** ~6500
**ContextTier:** Critical
**Depends:** 000-global-core.md
**LoadTrigger:** ext:.py, ext:.pyi, file:pyproject.toml

## Scope

**What This Rule Covers:**
Foundational Python development practices using modern tooling (uv, Ruff, pytest, ty) to ensure consistent, reliable, and performant codebases with proper dependency management, linting, formatting, type checking, and project structure.

**When to Load This Rule:**
- Modifying Python files (.py)
- Python project setup and configuration
- Dependency management with uv
- Virtual environment management
- Testing with pytest
- Type checking with ty or mypy
- Linting and formatting with Ruff
- pyproject.toml configuration
- Implementing Python best practices and modern patterns
- Setting up Python development workflows

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates

**Recommended:**
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

**Best Practices Guides:**
- [Python Packaging User Guide](https://packaging.python.org/) - Authoritative packaging guidelines
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/) - Python style guide

## Contract

### Inputs and Prerequisites

- Python 3.11+ available (or project's specified version)
- Project's dependency manager installed (uv, poetry, pip, pipenv)
- `pyproject.toml` present (or creating new project)
- Target Python files or project structure identified

### Tooling Approach (Investigation-First)

**Before prescribing tools, investigate project's existing toolchain:**

1. **Read pyproject.toml** for existing dependencies and tool configurations
2. **Check for tool lock files:**
   - `uv.lock`  - Project uses **uv**
   - `poetry.lock`  - Project uses **poetry**
   - `Pipfile.lock`  - Project uses **pipenv**
   - `requirements.txt` only  - Project uses **pip**
3. **Look for tool configuration sections:**
   - `[tool.uv]`  - uv project
   - `[tool.poetry]`  - poetry project
   - `[tool.black]` or `[tool.ruff]`  - linter/formatter choice
4. **Respect project's existing choices** unless explicitly asked to change

**Recommended Tooling (Modern Python Projects):**

**Preferred for NEW projects:**
- **Runtime:** uv/uvx (fast, modern, Astral ecosystem)
  - `uv run python script.py` (project execution)
  - `uvx ruff check .` (isolated linting)
  - `uvx ty check .` (isolated type checking)
- **Linting/Formatting:** Ruff (fast, comprehensive)
- **Type Checking:** ty (fast, Astral ecosystem)

**Alternative Tooling (Respect for EXISTING projects):**
- **poetry:** `poetry run python`, `poetry run pytest`
- **pipenv:** `pipenv run python`, `pipenv run pytest`
- **pip + venv:** `python script.py`, `pytest` (after activation)
- **Linting:** black + flake8, pylint
- **Type Checking:** mypy (mature, plugin ecosystem)

**Rule:** Match project's existing tooling. Only recommend changes when:
- User explicitly asks for modernization
- Project has no established toolchain
- Existing toolchain causes problems

### Mandatory (Universal Requirements)

These requirements apply regardless of tooling choice:

- Apply consistent linting and formatting to all modified Python files
- Apply type checking to all modified Python files
- Run test suite for projects with tests
- Centralize configuration in `pyproject.toml`
- Use `datetime.now(UTC)` instead of deprecated `datetime.utcnow()`
- Integrate with project's task automation (Taskfile, Makefile, etc.)

### Forbidden

- Never skip Pre-Task-Completion Validation Gate (lint, format, type check, tests)
- Never use deprecated `datetime.utcnow()` (use `datetime.now(UTC)`)
- Never hard-code secrets or credentials
- Never use broad `except:` clauses that swallow exceptions
- Never ignore project's established toolchain without justification
- Never prescribe specific tools (uv, poetry) without checking existing setup

### Execution Steps

1. **Investigation:** Read `pyproject.toml` and check for lock files to identify project's toolchain (uv, poetry, pip)
2. **Environment Setup:** Use project's dependency manager to ensure environment is ready
   - **uv:** `uv python pin 3.11` and `uv sync --all-groups`
   - **poetry:** `poetry install --with dev`
   - **pip:** `pip install -r requirements.txt` (or requirements-dev.txt)
3. **Implementation:** Write or modify Python code following modern patterns (type hints, clear error handling, modular structure)
4. **Validation:** Run comprehensive validation suite using project's toolchain:
   - **uv:** `uvx ruff check .`, `uvx ruff format --check .`, `uvx ty check .`, `uv run pytest`
   - **poetry:** `poetry run ruff check .`, `poetry run mypy .`, `poetry run pytest`
   - **pip/venv:** `ruff check .`, `mypy .`, `pytest` (assumes tools installed in venv)
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

```bash
# Validation commands (adjust for project's toolchain)

# If project uses uv (check for uv.lock):
uvx ruff check .
uvx ruff format --check .
uvx ty check .
uv run pytest tests/

# If project uses poetry (check for poetry.lock):
poetry run ruff check .
poetry run mypy .
poetry run pytest tests/

# If project uses pip (no lock file):
ruff check .
mypy .
pytest tests/
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**CRITICAL:** Before marking any Python task as complete, ALL of the following checks MUST pass:

**Code Quality (use project's toolchain):**
- **CRITICAL:** Linting check - Must pass with zero errors
  - **uv:** `uvx ruff check .`
  - **poetry:** `poetry run ruff check .` (or `poetry run flake8 .`)
  - **pip:** `ruff check .` (or `flake8 .`)
- **CRITICAL:** Format check - Must pass, code properly formatted
  - **uv:** `uvx ruff format --check .`
  - **poetry:** `poetry run ruff format --check .` (or `poetry run black --check .`)
  - **pip:** `ruff format --check .` (or `black --check .`)
- **CRITICAL:** Type check - Must pass with zero type errors
  - **uv:** `uvx ty check .` (primary) or `uv run mypy .` (fallback)
  - **poetry:** `poetry run mypy .`
  - **pip:** `mypy .`
- **CRITICAL:** Syntax validation - All Python files compile without syntax errors
  - **All toolchains:** `python -m py_compile -q .` (using project's Python)

**Test Execution (use project's toolchain):**
- **CRITICAL:** All tests must pass (for projects with test suites)
  - **uv:** `uv run pytest`
  - **poetry:** `poetry run pytest`
  - **pip:** `pytest`
- **Rule:** Never skip tests unless user explicitly requests override

**Documentation:**
- **CRITICAL:** Update `CHANGELOG.md` with entry under `## [Unreleased]` for code changes
- **CRITICAL:** Review and update `README.md` when triggers apply (see `000-global-core.md` section 6)

**Validation Protocol:**
- **Rule:** Run validation immediately after modifications, not in batches
- **Rule:** Do not mark tasks complete if ANY check fails
- **Rule:** Fix all failures before responding to user
- **Exception:** Only skip with explicit user override - acknowledge risks

**Success Criteria:**
- All code quality checks pass (ruff, ty, py_compile)
- All tests pass
- Documentation updated
- Pre-Task-Completion Validation Gate passed

**Investigation Required:**
1. **Read pyproject.toml BEFORE making recommendations** - Check existing dependencies, Python version, tool configurations
2. **Verify uv is available** - Check if project uses uv or needs setup instructions
3. **Never speculate about project structure** - Use list_dir to understand src/ vs flat layout
4. **Check existing tests** - Read conftest.py, test files to understand test patterns
5. **Make grounded recommendations based on investigated project setup** - Match existing patterns and tooling

**Anti-Pattern Examples:**
- "Based on typical Python projects, you probably use this structure..."
- "Let me add this dependency - it should work..."
- "I've fixed the bug. Task complete!" (without running validation)

**Correct Pattern:**
- "Let me check your Python project setup first."
- [reads pyproject.toml, checks for lock files (uv.lock, poetry.lock)]
- "I see you're using poetry with Python 3.11 and pytest. Here's how to add the new feature following your existing structure..."
- [makes changes, runs validation with poetry run]
- "Changes validated: ruff clean, format clean, types clean, tests passing (12/12). Task complete."

### Design Principles

- **Investigation-First:** Check project's existing toolchain before prescribing tools
- **Toolchain Respect:** Match project's dependency manager (uv, poetry, pip)
- **Python Version:** Pin appropriate Python version in `pyproject.toml`
- **Code Quality:** Apply consistent linting and formatting on every file modification
- **Type Safety:** Apply type checking on every file modification for static type safety
- **Code Structure:** Structure code with clear modules, proper error handling, and modern Python patterns
- **Task Integration:** Integrate with project's task automation (Taskfile, Makefile, etc.)
- **Validation First:** Never mark tasks complete without passing Pre-Task-Completion Validation Gate

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (000-global-core.md)
- [ ] Python available (version determined by project)
- [ ] Project's dependency manager identified (uv, poetry, pip)
- [ ] Target files or project structure identified
- [ ] pyproject.toml exists or ready to create

**After Completion:**

**Environment Setup (varies by toolchain):**
- [ ] Python version pinned appropriately for project
- [ ] Dependencies managed through project's chosen tool
- [ ] Virtual environment created/verified
- [ ] Dependencies installed/synced
- [ ] Linter/formatter configured in pyproject.toml

**Code Quality (commands vary by toolchain):**
- [ ] **CRITICAL:** Linting passed with zero errors
- [ ] **CRITICAL:** Formatting check passed
- [ ] **CRITICAL:** Type checking passed with zero type errors
- [ ] **CRITICAL:** Syntax validation passed (all Python files compile)
- [ ] **CRITICAL:** All tests passed (if test suite exists)

**Documentation:**
- [ ] **CRITICAL:** CHANGELOG.md updated for code changes
- [ ] README.md reviewed and updated if triggers apply

**Project Standards:**
- [ ] Appropriate dependency management commands used (no mixing of pip/poetry/uv)
- [ ] Import paths use absolute imports where possible
- [ ] Project follows modern Python packaging standards
- [ ] All Python execution uses project's standard method

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Ignoring Project's Existing Toolchain

```bash
# Bad: Forcing uv on a poetry project
# Found poetry.lock in project
# Still running: uv run python script.py
```

**Problem:** Breaks project's established conventions; may cause dependency version conflicts; ignores team's tooling decisions; creates inconsistent developer experience

**Correct Pattern:**
```bash
# Good: Detect and respect project's toolchain

# Step 1: Check for lock files
ls -la | grep -E '(uv.lock|poetry.lock|Pipfile.lock)'

# Step 2: Use appropriate commands
# If poetry.lock exists:
poetry run python script.py
poetry run pytest tests/

# If uv.lock exists:
uv run python script.py
uv run pytest tests/

# If only requirements.txt:
python script.py  # Assumes venv active
pytest tests/
```

**Benefits:** Respects project conventions; maintains consistency; works with existing CI/CD; follows team decisions

### Anti-Pattern 2: Skipping Validation Before Task Completion

```python
# AI makes code changes to fix a bug
# AI: "I've fixed the bug in user_service.py. Task complete!"
# [No ruff check, no ruff format, no pytest run]
```

**Problem:** May introduce linting violations; formatting inconsistencies; broken tests; syntax errors discovered later by user

**Correct Pattern:**
```bash
# After making changes, always validate using project's toolchain:

# If uv project:
uvx ruff check .
uvx ruff format --check .
uvx ty check .
uv run pytest

# If poetry project:
poetry run ruff check .
poetry run mypy .
poetry run pytest

# If pip project:
ruff check .
mypy .
pytest

# Only after ALL pass:
# "Changes validated: linting clean, formatting clean, types clean, tests passing (12/12). Task complete."
```

**Benefits:** Catches errors immediately; ensures code quality standards; user receives working, tested code; no surprises

### Anti-Pattern 3: Using Deprecated `datetime.utcnow()`

```python
# Bad: Using deprecated datetime API
from datetime import datetime
timestamp = datetime.utcnow()  # Deprecated in Python 3.12+
```

**Problem:** Deprecated API; will be removed in future Python versions; naive datetime (no timezone info); timezone-aware best practice

**Correct Pattern:**
```python
# Good: Use timezone-aware datetime with UTC
from datetime import datetime, UTC
timestamp = datetime.now(UTC)  # Modern, timezone-aware
```

**Benefits:** Future-proof code; explicit timezone handling; follows Python 3.11+ best practices; no deprecation warnings

### Anti-Pattern 4: Skipping Type Checking Before Task Completion

```python
# AI makes code changes
# AI: "I've updated the data processing function. Task complete!"
# [No type checking run - potential type errors undetected]
```

**Problem:** Type errors discovered later; runtime crashes from type mismatches; IDE warnings ignored; inconsistent type annotations

**Correct Pattern:**
```bash
# After making changes, always validate types using project's toolchain:

# If uv project:
uvx ty check .

# If poetry/pip project:
poetry run mypy .  # or: mypy .

# Only after ALL checks pass (including type checking):
# "Changes validated: linting clean, formatting clean, types clean, tests passing. Task complete."
```

**Benefits:** Catches type errors at development time; prevents runtime type crashes; ensures type annotations are correct and complete; maintains type safety across codebase

## Environment and Tooling Requirements

### Toolchain Selection (Investigation-First)

**Before prescribing tooling, detect project's existing setup:**

1. **Check for dependency manager lock files:**
   - `uv.lock`  - Project uses **uv**
   - `poetry.lock`  - Project uses **poetry**
   - `Pipfile.lock`  - Project uses **pipenv**
   - Only `requirements.txt`  - Project uses **pip**

2. **Check pyproject.toml for tool sections:**
   - `[tool.uv]`  - uv configuration
   - `[tool.poetry]`  - poetry configuration
   - `[tool.black]` or `[tool.ruff]`  - formatter preference

3. **Match project's existing toolchain consistently**

### Recommended Tooling (For NEW Projects)

**Python Runtime and Dependency Management:**
- **Preferred:** uv (fast, modern, comprehensive)
  - `uv python pin 3.11` - Pin Python version
  - `uv sync --all-groups` - Install dependencies
  - `uv run python` - Execute in project environment
  - `uvx ruff` - Run isolated tools
- **Alternative:** poetry (mature, widely adopted)
  - `poetry install --with dev` - Install dependencies
  - `poetry run python` - Execute in project environment
- **Alternative:** pip + venv (simple, universal)
  - `pip install -r requirements.txt` - Install dependencies
  - `python` - Execute (assumes venv active)

**Linting and Formatting:**
- **Preferred:** Ruff (fast, comprehensive, replaces multiple tools)
- **Alternative:** black + flake8 + isort (established ecosystem)

**Type Checking:**
- **Preferred:** ty (fast, Astral ecosystem) or mypy (mature, plugins)
- **Configuration:** Use `pyproject.toml` for all tool settings

### Virtual Environment Management

**Critical Principle:** Always use project's dependency manager to execute code

**If project uses uv:**
- `uv run python script.py` - Execute scripts
- `uv run pytest` - Run tests
- `uvx ruff check .` - Isolated linting

**If project uses poetry:**
- `poetry run python script.py` - Execute scripts
- `poetry run pytest` - Run tests
- `poetry run ruff check .` - Run linting (if ruff is a dev dependency)

**If project uses pip:**
- Activate venv first OR prefix with path to venv python
- `python script.py` - Execute scripts (venv active)
- `pytest` - Run tests (venv active)

### Tool Isolation Patterns

**Isolated Tool Execution (No Project Dependencies):**

Tools that don't import project code can run in isolation:

**uv projects:** Use `uvx` for isolated execution
```bash
uvx ruff check .      # Linter (no project imports)
uvx ruff format .     # Formatter (no project imports)
uvx ty check .        # Type checker (no project imports)
```

**poetry/pip projects:** Install tools as dev dependencies or use pipx
```bash
poetry run ruff check .    # If ruff in dev dependencies
pipx run ruff check .      # Isolated execution via pipx
```

**Project Environment Execution (Needs Project Dependencies):**

Commands that import project code MUST use project environment:

**uv projects:**
```bash
uv run pytest tests/               # Imports project code and plugins
uv run uvicorn app.main:app        # Imports app package
uv run python -m mypackage         # Runs module from project
```

**poetry projects:**
```bash
poetry run pytest tests/           # Imports project code and plugins
poetry run uvicorn app.main:app    # Imports app package
poetry run python -m mypackage     # Runs module from project
```

**pip projects:**
```bash
pytest tests/                      # Venv must be active
uvicorn app.main:app               # Venv must be active
python -m mypackage                # Venv must be active
```
- Pure external tool, no project imports/plugins? Use `uvx ...`

### Command Patterns

**Pattern Selection Based on Project Toolchain:**

**uv projects (uv.lock present):**
```bash
# Project execution
uv run python script.py
uv run python -c "import app; print('success')"
uv run uvicorn app.main:app --reload
uv run pytest tests/

# Isolated tools
uvx ruff check .
uvx ruff format .
uvx ty check .

# Environment management
uv python pin 3.11
uv sync --all-groups
uv lock --upgrade
```

**poetry projects (poetry.lock present):**
```bash
# Project execution
poetry run python script.py
poetry run python -c "import app; print('success')"
poetry run uvicorn app.main:app --reload
poetry run pytest tests/

# Tools (if in dev dependencies)
poetry run ruff check .
poetry run mypy .

# Environment management
poetry install --with dev
poetry update
poetry lock
```

**pip projects (requirements.txt only):**
```bash
# Project execution (venv must be active)
python script.py
python -c "import app; print('success')"
uvicorn app.main:app --reload
pytest tests/

# Tools (if installed in venv)
ruff check .
mypy .

# Environment management
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Environment Setup Best Practices

**Toolchain-Specific Setup:**

**uv projects:**
- Start with `uv python pin 3.11` to set Python version
- Use `uv sync --all-groups` to install dependencies
- Use `uv lock` before `uv sync` for consistency

**poetry projects:**
- Use `poetry install --with dev` to install dependencies
- Use `poetry lock` to update lock file

**pip projects:**
- Create venv: `python -m venv .venv`
- Activate: `source .venv/bin/activate` (Unix) or `.venv\Scripts\activate` (Windows)
- Install: `pip install -r requirements.txt`

### Troubleshooting Environment Issues

**ModuleNotFoundError diagnosis:**

1. **Check toolchain being used:**
   - uv project: Are you using `uv run`?
   - poetry project: Are you using `poetry run`?
   - pip project: Is venv activated?

2. **Verify dependencies installed:**
   - uv: `uv sync`
   - poetry: `poetry install`
   - pip: `pip install -r requirements.txt`

3. **Test module availability:**
   - uv: `uv run python -c "import module_name"`
   - poetry: `poetry run python -c "import module_name"`
   - pip: `python -c "import module_name"` (venv active)

## Code Structure and Style Guidelines

- **Requirement:** Keep modules small and cohesive (target <300 lines).
- **Requirement:** Use explicit, absolute imports.
- **Requirement:** Avoid global mutable state; prefer immutable data flow.
- **Requirement:** Manage configuration via environment variables or a config module. Never hard-code secrets.

## Error Handling and Reliability

- **Always:** Raise specific exceptions with actionable context.
- **Requirement:** Avoid broad `except:` clauses or silently passing exceptions.
- **Requirement:** Do not swallow exceptions; re-raise with added context when necessary.

### Syntax Validation

- **Requirement:** Before completing any task involving Python code changes, verify that all modified files are syntactically correct.
- **Rule:** Use `python -m py_compile` as a definitive check for syntax errors, in addition to linter feedback.
- **Command (use project's Python):**
  - **uv:** `uv run python -m py_compile -q <path>`
  - **poetry:** `poetry run python -m py_compile -q <path>`
  - **pip:** `python -m py_compile -q <path>` (venv active)

### Type Checking

**Recommended Type Checkers:**

**Primary (Modern, Fast):**
- **ty** - Extremely fast type checker from Astral (uv/ruff creators), written in Rust
- Best for new projects and Astral toolchain users
- Isolated execution via `uvx ty check .`

**Alternative (Mature, Plugins):**
- **mypy** - Mature type checker with extensive plugin ecosystem
- Required for Django, SQLAlchemy, and other frameworks needing plugins
- Execution via project environment: `poetry run mypy .` or `uv run mypy .`

**Core Policy:**
- **NEW projects:** Prefer `ty` for speed and simplicity
- **EXISTING projects:** Respect existing type checker (likely mypy)
- **Django/SQLAlchemy:** Use `mypy` (ty doesn't support plugins)
- **CRITICAL:** Run type checking before marking any Python task complete

**Command Patterns by Toolchain:**

**uv projects:**
```bash
# Preferred: ty via uvx (isolated, no project deps)
uvx ty check .
uvx ty check src/

# Fallback: mypy when plugins needed
uv run mypy src/
uv run mypy --strict src/
```

**poetry projects:**
```bash
# mypy (standard for poetry projects)
poetry run mypy .
poetry run mypy --strict src/
```

**pip projects:**
```bash
# mypy (must be in requirements)
mypy .
mypy --strict src/
```

**When to Use ty vs mypy:**

**Use ty (isolated via uvx or pipx) for:**
- NEW projects without legacy mypy configuration
- Standard type checking (fast, no setup required)
- CI/CD pipelines (consistent, isolated execution)
- Projects using Astral toolchain (uv + ruff + ty)

**Use mypy (via project environment) for:**
- EXISTING projects already using mypy
- Projects with mypy plugins (ty doesn't support plugins yet)
- Django/SQLAlchemy projects (mypy has better stub support)
- Maximum strictness needed (mypy has more configuration options)

**Configuration in pyproject.toml:**
```toml
# ty configuration (for new ty projects)
[tool.ty]
python-version = "3.11"

# mypy configuration (for existing mypy projects)
[tool.mypy]
python_version = "3.11"
strict = true
```

**Note:** ty is under active development. For latest features, see [ty documentation](https://docs.astral.sh/ty/).

**Integration with Validation Gate:**
- **CRITICAL:** Type checking (ty or mypy) is part of mandatory Pre-Task-Completion Validation Gate
- **Rule:** Type errors must be resolved before marking tasks complete
- **Rule:** Do not use `# type: ignore` without documenting the reason

## Performance Optimization

- **Requirement:** Separate I/O and CPU concerns. Prefer set-based SQL and vectorization over Python loops.
- **Requirement:** Ensure code is idiomatic and follows PEP 8.
- **Requirement:** Include comprehensive type hints.
- **Requirement:** Follow Python documentation standards from `204-python-docs-comments.md` (Google-style docstrings for all public APIs, enforced via Ruff D-rules).

## Modern Python Patterns

- **Critical:** Use `datetime.now(UTC)` instead of deprecated `datetime.utcnow()` for timezone-aware timestamps.
- **Always:** Import from `collections.abc` instead of `typing` for abstract base classes (e.g., `AsyncGenerator`).
- **Always:** Use `dict` and `list` for type annotations instead of `Dict` and `List` from typing.
- **Always:** Follow Python 3.11+ patterns and avoid deprecated functionality.

## Project Integration

- **Requirement:** Use project's toolchain consistently in Taskfile tasks and documentation
- **Pattern for Taskfile tasks:**
  - Detect toolchain: Check for uv.lock, poetry.lock, or Pipfile.lock
  - Use appropriate prefix: `uv run`, `poetry run`, or bare commands (pip)
- **Development tools:** Use isolated execution when possible (uvx, pipx) or install as dev dependencies
- **Always:** Include environment setup tasks with status checks to avoid redundant operations
- **Always:** Prefer `task validate` (or `task check` / `task ci`) when Taskfile.yml exists, falling back to direct tool commands otherwise
- **Documentation:** Provide setup instructions appropriate for project's chosen toolchain
