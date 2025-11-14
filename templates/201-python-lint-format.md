**Description:** Authoritative Python linting and formatting policy using Ruff for code quality and consistency.
**Type:** Agent Requested
**AppliesTo:** `**/*.py`, `streamlit/**/*`
**AutoAttach:** false
**Keywords:** Ruff, linting, formatting, code quality, style checking, uvx ruff, lint errors, ruff check, ruff format, pyproject.toml configuration
**TokenBudget:** ~1550
**ContextTier:** High
**Version:** 1.3
**LastUpdated:** 2025-11-07
**Depends:** 200-python-core

# Python Linting & Formatting (uvx ruff-first, with fallbacks)

## Purpose
Establish authoritative Python code quality standards using Ruff as the primary tool for linting and formatting, with fallback strategies to ensure consistent code style, quality, and maintainability across all Python projects.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Python code linting and formatting with Ruff for consistent code quality and style



## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Start TL;DR (Read First - 30 Seconds)

**MANDATORY:**
**Essential Patterns:**
- **Always use `uvx ruff check .` and `uvx ruff format .`** - MANDATORY before task completion
- **Configure in pyproject.toml** - Centralize all Ruff settings
- **Set target-version = "py311"** - Minimum Python version
- **Enable pydocstyle (D rules)** - Enforce docstring standards
- **All checks must pass with 0 errors** - Non-negotiable validation gate
- **Never use `uv run ruff`** - Always use isolated `uvx ruff` for consistency

**Quick Checklist:**
- [ ] Run `uvx ruff check .` (must pass with 0 errors)
- [ ] Run `uvx ruff format --check .` (must pass)
- [ ] pyproject.toml has [tool.ruff] config
- [ ] target-version = "py311" set
- [ ] pydocstyle rules enabled (D)
- [ ] Use `uvx ruff check --fix .` to auto-fix
- [ ] Use `uvx ruff format .` to format

## 1. Core Policy
- **Requirement:** Ruff is the authoritative default for linting and formatting.
- **Requirement:** Centralize Ruff configuration in `pyproject.toml`.
- **Requirement:** Set `target-version = "py311"` and exclude directories like `.venv`, `notebooks`, and `output`.
- **Always:** If Ruff is unavailable, fall back to `flake8` (lint) and `black` + `isort` (format/imports) with equivalent configuration. Document the chosen fallback in the PR.
 - **Requirement:** Enable pydocstyle (D) rules and set a single convention (`google` or `numpy`) consistent with `204-python-docs-comments.md`.

## 2. Agent Workflow

**CRITICAL:** Lint and format checks are MANDATORY before task completion (see Pre-Task-Completion Validation Gate).

- **MANDATORY:** On every Python file modification or creation, run the linter and formatter.
- **MANDATORY:** Use `uvx ruff check .` and `uvx ruff format --check .` for isolated tool execution.
- **MANDATORY:** All checks must pass with zero errors before marking task complete.
- **MANDATORY:** Use `uvx ruff check --fix .` and `uvx ruff format .` to apply fixes.
- **Consider:** If Ruff is unavailable, use `flake8 .` and `black --check .`; fix with `black .` and `isort .`.
- **Requirement:** Ensure imports are organized and unused code is removed.
- **Rule:** Never use project-installed ruff via `uv run`; always use isolated `uvx ruff` for consistency.

### 2.1 Docstring Lint Configuration (Ruff)
Add the following to `pyproject.toml`:
```toml
[tool.ruff]
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "D"]
ignore = []

[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy"
```

## 3. Compliance Checklist (MANDATORY)

**CRITICAL:** These checks are MANDATORY and must pass before task completion.

- **MANDATORY:** Before finalizing any Python code and after any Python file edit, run repo-wide checks that verify:
  - `uvx ruff check .` passes with zero errors (CRITICAL).
  - `uvx ruff format --check .` passes (CRITICAL).
  - If a `Taskfile.yml` exists:
    - `task lint` passes (should use `uvx ruff` internally).
    - `task format` passes (should use `uvx ruff` internally).
  - Fix ALL failures before reporting success; do not rely on editor-only lints.
  - The final code is idiomatic and correctly formatted.
- **CRITICAL:** Do NOT mark tasks complete if any check fails.
- **CRITICAL:** Reference Pre-Task-Completion Validation Gate in `000-global-core.md` and `AGENTS.md`.

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

## Quick Compliance Checklist
- [ ] **CRITICAL:** `uvx ruff check .` passed with zero errors
- [ ] **CRITICAL:** `uvx ruff format --check .` passed
- [ ] **CRITICAL:** All lint/format failures fixed before task completion
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** All Python files pass `uvx ruff check .` with zero errors; `uvx ruff format --check .` passes; code is idiomatic and properly formatted; Pre-Task-Completion Validation Gate passed
- **Negative tests:** Files with syntax errors fail lint checks; improperly formatted code fails format check; task completion attempted with failing checks is blocked

> **Investigation Required**  
> When applying this rule:
> 1. **Read pyproject.toml BEFORE running lint/format** - Check existing Ruff configuration, rules, ignores
> 2. **Verify Ruff is available** - Check if `uvx ruff --version` works or needs installation instructions
> 3. **Never assume rule configuration** - Always check [tool.ruff.lint] section for enabled/disabled rules
> 4. **Check for existing lint exceptions** - Read `# noqa` comments and understand why they exist
> 5. **Validate fixes don't break functionality** - Run tests after auto-fixing lint/format issues
>
> **Anti-Pattern:**
> "Running ruff check... (without checking if it's configured)"
> "Auto-fixing all issues... (without understanding what they are)"
>
> **Correct Pattern:**
> "Let me check your Ruff configuration first."
> [reads pyproject.toml, checks [tool.ruff] section]
> "I see you have pydocstyle enabled with Google convention. Running ruff check with these settings..."

## Response Template

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
uv run pytest tests/
```

## References

### External Documentation
- [Ruff Documentation](https://docs.astral.sh/ruff/) - Complete linter and formatter configuration guide
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/) - Comprehensive list of linting rules and error codes                                                                                                      
- [Python Code Style PEP 8](https://peps.python.org/pep-0008/) - Official Python style guide standards

### Related Rules
- **Python Core**: `200-python-core.md`
- **Project Setup**: `203-python-project-setup.md`
 - **Python Docs & Comments**: `204-python-docs-comments.md`
