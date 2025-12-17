# Python Core Engineering Directives

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential Python patterns. Load for Python tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Python, uv, Ruff, pyproject.toml, dependency management, virtual environments, pytest, validation, uv run, uvx, ty, type checking, mypy, type hints
**TokenBudget:** ~4050
**ContextTier:** Critical
**Depends:** rules/000-global-core.md

## Purpose
Establish foundational Python development practices using modern tooling like `uv` and Ruff to ensure consistent, reliable, and performant codebases with proper dependency management, linting, formatting, and project structure.

## Rule Scope

Foundational Python development practices with modern tooling (uv, Ruff) and project structure

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Always use `uv run`** for Python execution - never bare `python` command
- **Taskfile-first validation (project standards):** If `Taskfile.yml` exists, prefer `task validate`
  (or `task check` / `task ci`). Otherwise run the direct tool commands below.
- **Lint & format (fallback):** `uvx ruff check .` and `uvx ruff format .`
- **Type check (fallback):** `uvx ty check .` (ty is the primary type checker). If the project uses a
  Taskfile, the recommended task name is `typecheck` (aliases like `type-check`, `typing`, `types`
  are acceptable).
- **Tests (fallback):** `uv run pytest` (all tests must pass)
- **Use `datetime.now(UTC)`** not deprecated `datetime.utcnow()`
- **Never skip validation** - ruff check, ruff format, ty check, pytest must all pass

## Contract

<contract>
<inputs_prereqs>
Python 3.11+; `uv` installed; `pyproject.toml` present
</inputs_prereqs>

<mandatory>
`uv run`, `uvx` for tools; Taskfile tasks
</mandatory>

<forbidden>
Bare `python`, `pytest`, `ruff` without `uv run`/`uvx`
</forbidden>

<steps>
1. Pin and sync environment with `uv`
2. Execute Python and tests via `uv run`
3. Lint/format via `uvx ruff`
4. Centralize config in `pyproject.toml`
</steps>

<output_format>
Commands, diffs, or code snippets only (no narrative unless requested)
</output_format>

<validation>
If a Taskfile exists, project validation tasks pass (prefer: `task validate`). Otherwise:
`uvx ruff check .` passes; `uvx ruff format --check .` passes; `uvx ty check .` passes; `uv run pytest` passes
</validation>

<design_principles>
- Use `uv` for all dependency and environment management; `uvx` for isolated tool execution
- Pin Python 3.11+ and centralize configuration in `pyproject.toml`
- Apply Ruff linting and formatting on every file modification
- Apply ty type checking on every file modification for static type safety
- Structure code with clear modules, proper error handling, and modern Python patterns
- Integrate with Taskfile for consistent automation across projects
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using Bare Python Commands Without `uv run`**
```bash
# Bad: Running Python without uv run
python script.py
pytest tests/
uvicorn app.main:app --reload
```
**Problem:** Commands run outside project virtual environment; leads to `ModuleNotFoundError`; dependencies not found; inconsistent behavior across environments

**Correct Pattern:**
```bash
# Good: Always use uv run for project commands
uv run python script.py
uv run pytest tests/
uv run uvicorn app.main:app --reload
```
**Benefits:** Consistent dependency resolution; all project modules available; reproducible behavior; no environment activation needed


**Anti-Pattern 2: Skipping Validation Before Task Completion**
```python
# AI makes code changes to fix a bug
# AI: "I've fixed the bug in user_service.py. Task complete!"
# [No ruff check, no ruff format, no pytest run]
```
**Problem:** May introduce linting violations; formatting inconsistencies; broken tests; syntax errors discovered later by user

**Correct Pattern:**
```bash
# After making changes, always validate:
uvx ruff check .
uvx ruff format --check .
uv run pytest

# Only after ALL pass:
# "Changes validated: ruff clean, format clean, tests passing (12/12). Task complete."
```
**Benefits:** Catches errors immediately; ensures code quality standards; user receives working, tested code; no surprises


**Anti-Pattern 3: Using Deprecated `datetime.utcnow()`**
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


**Anti-Pattern 4: Installing Tools in Project Environment Instead of Using `uvx`**
```bash
# Bad: Installing standalone tools in project venv
uv add --dev ruff black mypy safety
uv run ruff check .
```
**Problem:** Bloats project dependencies; tool versions conflict with project deps; slower environment setup; unnecessary lockfile complexity

**Correct Pattern:**
```bash
# Good: Use uvx for isolated tool execution
uvx ruff check .
uvx ruff format .
uvx ty check .
# Tools run in isolation, no project pollution
```
**Benefits:** Clean project dependencies; no version conflicts; faster uv sync; tools always latest stable versions; simpler pyproject.toml


**Anti-Pattern 5: Skipping Type Checking Before Task Completion**
```python
# AI makes code changes
# AI: "I've updated the data processing function. Task complete!"
# [No type checking run - potential type errors undetected]
```
**Problem:** Type errors discovered later; runtime crashes from type mismatches; IDE warnings ignored; inconsistent type annotations

**Correct Pattern:**
```bash
# After making changes, always validate types:
uvx ty check .

# Only after ALL checks pass (including type checking):
# "Changes validated: ruff clean, format clean, types clean, tests passing. Task complete."
```
**Benefits:** Catches type errors at development time; prevents runtime type crashes; ensures type annotations are correct and complete; maintains type safety across codebase

## Post-Execution Checklist
- [ ] **CRITICAL: Pre-Task-Completion Validation Gate passed** (see section 4.2)
- [ ] Python 3.11+ is pinned in .python-version file
- [ ] Dependencies managed through uv (pyproject.toml with dependency-groups)
- [ ] Ruff configured in pyproject.toml with target-version = "py311"
- [ ] **CRITICAL:** `uvx ruff check .` passed with zero errors
- [ ] **CRITICAL:** `uvx ruff format --check .` passed
- [ ] **CRITICAL:** `uvx ty check .` passed with zero type errors
- [ ] **CRITICAL:** `uv run pytest` passed (all tests)
- [ ] All Python files are syntactically valid (checked with `py_compile`)
- [ ] **CRITICAL:** CHANGELOG.md updated for code changes
- [ ] README.md reviewed and updated if triggers apply
- [ ] Virtual environment created with `uv venv` (not python -m venv)
- [ ] Dependencies synced with `uv sync --all-groups`
- [ ] No bare pip install commands in documentation
- [ ] Import paths use absolute imports where possible
- [ ] Project follows modern Python packaging standards

## Validation
- **CRITICAL:** Pre-Task-Completion Validation Gate (section 4.2) must pass before task completion
- **Syntax Check:** `uv run python -m py_compile -q .` (must pass)
- **Lint & Format:** `uvx ruff check .` and `uvx ruff format --check .` (must pass with zero errors)
- **Type Check:** `uvx ty check .` (must pass with zero type errors)
- **Tests:** `uv run pytest` (all tests must pass)
- **Documentation:** CHANGELOG.md and README.md updated as required
- **Import Check:** `uv run python -c "import importlib; print('ok')"`

> **Investigation Required**
> When applying this rule:
> 1. **Read pyproject.toml BEFORE making recommendations** - Check existing dependencies, Python version, tool configurations
> 2. **Verify uv is available** - Check if project uses uv or needs setup instructions
> 3. **Never speculate about project structure** - Use list_dir to understand src/ vs flat layout
> 4. **Check existing tests** - Read conftest.py, test files to understand test patterns
> 5. **Make grounded recommendations based on investigated project setup** - Match existing patterns and tooling
>
> **Anti-Pattern:**
> "Based on typical Python projects, you probably use this structure..."
> "Let me add this dependency - it should work..."
>
> **Correct Pattern:**
> "Let me check your Python project setup first."
> [reads pyproject.toml, checks directory structure]
> "I see you're using uv with Python 3.11 and pytest. Here's how to add the new feature following your existing structure..."

## Output Format Examples

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

# Validation: Test the implementation
def test_implementation_function():
    """Test following AAA pattern."""
    # Arrange
    test_input = {"key": "value"}

    # Act
    result = implementation_function(test_input)

    # Assert
    assert result["status"] == "success"
    assert "timestamp" in result
```

```bash
# Validation commands
uvx ruff check .
uvx ruff format --check .
uvx ty check .
uv run pytest tests/
```

## References

### External Documentation
- [Python Official Documentation](https://docs.python.org/3/) - Official Python documentation
- [uv Documentation](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- [Ruff Documentation](https://docs.astral.sh/ruff/) - Extremely fast Python linter and formatter
- [ty Documentation](https://docs.astral.sh/ty/) - Extremely fast Python type checker (Astral toolchain)
- [Python Packaging User Guide](https://packaging.python.org/) - Authoritative packaging guidelines
- [PEP 8 Style Guide](https://peps.python.org/pep-0008/) - Python style guide

### Related Rules
- **Linting & Formatting**: `rules/201-python-lint-format.md`
- **Project Setup**: `rules/203-python-project-setup.md`
- **YAML Safety**: `rules/202-markup-config-validation.md`
- **Global Core**: `rules/000-global-core.md`

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
- **Requirement:** Use `uvx ty check` for type checking (primary); use `uv run mypy` as fallback when mypy plugins are needed.

### 2.1 Tool Isolation vs Project Environment (uv run vs uvx)

- **Rule:** Use `uv run` when the command needs access to the project environment (installed dependencies, project package imports, or plugins declared in `pyproject.toml`).
- **Rule:** Use `uvx` for standalone tools that do not import your project code and do not require project-installed plugins.

When to use `uv run` (project venv):
- The command imports your project package/modules (e.g., `pytest`, `uvicorn app.main:app`, `python -m yourpkg`).
- The tool relies on plugins or integrations defined in `pyproject.toml` or installed in the project venv (e.g., `pytest` plugins, mypy plugins, Sphinx extensions).
- You need the exact dependency set and versions pinned by your project lockfile.

Examples (project environment):
- `uv run pytest tests/`  # discovers and loads project/third-party pytest plugins
- `uv run mypy src/`      # fallback type checker when mypy plugins are needed
- `uv run uvicorn app.main:app --reload`  # imports your app package
- `uv run python -m yourpkg.tool`         # runs code that imports your package

When to use `uvx` (isolated tool context):
- The tool is self-contained and does not import your project code.
- The tool does not require project-installed plugins; any needed integrations are provided by the tool itself.

Examples (isolated tools):
- `uvx ruff check .` and `uvx ruff format .`  # linter/formatter runs independently
- `uvx ty check .`                            # type checker runs independently (primary)
- `uvx black .`                               # formatter without importing project code
- `uvx safety check`                          # dependency vulnerability scan

Common pitfalls and guidance:
- **Important:** `uvx` runs tools in an isolated context. It does not automatically include your project venv or its extra modules/plugins. If a tool fails to find a plugin or cannot import your package, switch to `uv run`.
- If a command needs both a standalone tool and project imports, prefer `uv run` to ensure your project environment is available.
- Keep configuration centralized in `pyproject.toml`, but remember that only `uv run` guarantees access to project-installed integrations referenced there.

Quick decision guide:
- Imports project code or needs project plugins? Use `uv run ...`
- Pure external tool, no project imports/plugins? Use `uvx ...`

### Command Patterns
**CORRECT:**
```bash
# Project execution
uv run python script.py
uv run python -c "import app; print('success')"
uv run uvicorn app.main:app --reload
uv run pytest tests/
uv run mypy src/  # fallback type checker when mypy plugins needed

# Isolated tools (Astral toolchain)
uvx ruff check .
uvx ruff format .
uvx ty check .    # primary type checker
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

## 4.2 Pre-Task-Completion Validation Gate (CRITICAL)

**Reference:** Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**CRITICAL:** Before marking any Python task as complete, ALL of the following checks MUST pass:

### Mandatory Validation Checks (No Exceptions)

#### Code Quality
- **CRITICAL:** `uvx ruff check .` - Must pass with zero errors
- **CRITICAL:** `uvx ruff format --check .` - Must pass, code properly formatted
- **CRITICAL:** `uvx ty check .` - Must pass with zero type errors
- **CRITICAL:** `uv run python -m py_compile -q .` - All Python files compile without syntax errors

#### Test Execution
- **CRITICAL:** `uv run pytest` - All tests must pass (for projects with test suites)
- **Rule:** Never skip tests unless user explicitly requests override

#### Documentation
- **CRITICAL:** Update `CHANGELOG.md` with entry under `## [Unreleased]` for code changes
- **CRITICAL:** Review and update `README.md` when triggers apply (see `000-global-core.md` section 6)

### Validation Protocol
- **Rule:** Run validation immediately after modifications, not in batches
- **Rule:** Do not mark tasks complete if ANY check fails
- **Rule:** Fix all failures before responding to user
- **Exception:** Only skip with explicit user override - acknowledge risks

## 4.3 Type Checking with ty

**ty** is an extremely fast Python type checker from Astral (the creators of `uv` and `ruff`), written in Rust. It is the primary type checker for the Astral toolchain.

### Core Policy
- **Requirement:** Use `ty` as the primary type checker for all Python projects.
- **Requirement:** Run `uvx ty check .` before marking any Python task as complete.
- **Fallback:** If `ty` is unavailable or incompatible, use `uv run mypy` as a fallback (requires mypy in project dependencies).

### Command Patterns
```bash
# Primary: ty via uvx (isolated, no project deps needed)
uvx ty check .                    # Check entire project
uvx ty check src/                 # Check specific directory
uvx ty check src/module.py        # Check specific file

# Fallback: mypy via uv run (when ty unavailable or plugins needed)
uv run mypy src/                  # Requires mypy in pyproject.toml
uv run mypy --strict src/         # Strict mode for maximum type safety
```

### When to Use ty vs mypy

**Use `uvx ty check .` for:**
- Standard type checking (fast, no setup, Astral ecosystem)
- CI/CD pipelines (consistent, isolated execution)

**Use `uv run mypy` for:**
- Projects with mypy plugins (ty doesn't support mypy plugins)
- Django/SQLAlchemy type stubs (better ecosystem support for stubs)
- Maximum strictness needed (`uv run mypy --strict` has more strict mode options)

### Configuration in pyproject.toml
```toml
[tool.ty]
# ty configuration (when available)
python-version = "3.11"

[tool.ty.rules]
# Rule configuration as ty matures
```

**Note:** ty is under active development. Configuration options may expand. Check [ty documentation](https://docs.astral.sh/ty/) for current options.

### Integration with Validation Gate
- **CRITICAL:** `uvx ty check .` is part of the mandatory Pre-Task-Completion Validation Gate
- **Rule:** Type errors must be resolved before marking tasks complete
- **Rule:** Do not use `# type: ignore` without documenting the reason

## 5. Performance & Best Practices
- **Requirement:** Separate I/O and CPU concerns. Prefer set-based SQL and vectorization over Python loops.
- **Requirement:** Ensure code is idiomatic and follows PEP 8.
- **Requirement:** Include comprehensive type hints.
- **Requirement:** Follow Python documentation standards from `204-python-docs-comments.md` (Google-style docstrings for all public APIs, enforced via Ruff D-rules).

## 6. Modern Python Patterns
- **Critical:** Use `datetime.now(UTC)` instead of deprecated `datetime.utcnow()` for timezone-aware timestamps.
- **Always:** Import from `collections.abc` instead of `typing` for abstract base classes (e.g., `AsyncGenerator`).
- **Always:** Use `dict` and `list` for type annotations instead of `Dict` and `List` from typing.
- **Always:** Follow Python 3.11+ patterns and avoid deprecated functionality.

## 7. Taskfile Integration
- **Requirement:** Use `uv run` prefix for all Python commands in Taskfile tasks.
- **Requirement:** Use `uvx` for all development tools (ruff, ty, safety).
- **Requirement:** Use `uv run` for tools needing project plugins (pytest, mypy when plugins required).
- **Always:** Include environment setup tasks with status checks to avoid redundant operations.
- **Pattern:** Structure tasks as: `uv:pin` then `install` (with `uv sync`) then execution tasks.
