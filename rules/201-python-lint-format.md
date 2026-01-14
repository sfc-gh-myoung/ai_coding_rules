# Python Linting & Formatting (uvx ruff-first, with fallbacks)

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** Ruff, linting, formatting, code quality, style checking, uvx ruff, lint errors, ruff check, ruff format, pyproject.toml configuration
**TokenBudget:** ~3100
**ContextTier:** High
**Depends:** 200-python-core.md

## Scope

**What This Rule Covers:**
Authoritative Python code quality standards using Ruff as the primary tool for linting and formatting. Covers Ruff command patterns (`uvx ruff check`, `uvx ruff format`), pyproject.toml configuration, pydocstyle rules, pre-commit integration, and validation requirements. Includes tool isolation strategies and fallback approaches for environments without uv.

**When to Load This Rule:**
- Writing or modifying Python code
- Setting up new Python projects
- Configuring linting and formatting tools
- Reviewing code quality issues
- Troubleshooting Ruff errors or configuration
- Before completing any Python-related task (validation gate)

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Python foundation patterns

**Related:**
- **203-python-project-setup.md** - Project structure and configuration
- **204-python-docs-comments.md** - Documentation standards

### External Documentation

- [Ruff Documentation](https://docs.astral.sh/ruff/) - Official Ruff documentation
- [Ruff Rules](https://docs.astral.sh/ruff/rules/) - Complete rule reference
- [Ruff Configuration](https://docs.astral.sh/ruff/configuration/) - Configuration options

## Contract

### Inputs and Prerequisites

- Python codebase with .py files
- pyproject.toml for configuration
- uv/uvx available (or fallback to pip-installed ruff)
- Understanding of Python code quality standards

### Mandatory

- **Always use `uvx ruff check .` and `uvx ruff format .`** before task completion
- Configure Ruff in pyproject.toml
- Set `target-version = "py311"` minimum
- Enable pydocstyle (D rules) for docstring standards
- All checks must pass with 0 errors (non-negotiable validation gate)
- Use isolated `uvx ruff` (never `uv run ruff`)

### Forbidden

- Submitting code with linting errors
- Using blanket `# noqa` comments without specific codes
- Mixing formatters (use Ruff exclusively)
- Skipping pre-commit hooks in production projects
- Using `uv run ruff` instead of `uvx ruff`

### Execution Steps

1. Run `uvx ruff check .` to identify linting issues
2. Review errors and fix manually or run `uvx ruff check --fix .`
3. Run `uvx ruff format .` to apply consistent formatting
4. Verify with `uvx ruff format --check .`
5. Commit changes with formatted code
6. Validate all checks pass with 0 errors

### Output Format

Linting and formatting produces:
- Clean code passing all Ruff checks (0 errors)
- Consistently formatted Python files
- pyproject.toml with [tool.ruff] configuration
- Pre-commit hooks configured (optional but recommended)

### Validation

**Pre-Task-Completion Checks:**
- [ ] Run `uvx ruff check .` (must pass with 0 errors)
- [ ] Run `uvx ruff format --check .` (must pass)
- [ ] pyproject.toml has [tool.ruff] config
- [ ] target-version = "py311" set
- [ ] pydocstyle rules enabled (D)

**Success Criteria:**
- `uvx ruff check .` returns 0 errors
- `uvx ruff format --check .` confirms no formatting changes needed
- All code follows pydocstyle standards

**Negative Tests:**
- Ruff should catch common errors (undefined variables, unused imports)
- Ruff should reject improperly formatted code

### Design Principles

- **Ruff-first:** Use Ruff as the single source of truth for linting and formatting
- **Tool isolation:** Use `uvx ruff` for consistent, isolated execution
- **Zero tolerance:** All checks must pass with 0 errors
- **Configuration centralization:** All settings in pyproject.toml
- **Automation:** Integrate with pre-commit hooks and CI/CD

### Post-Execution Checklist

- [ ] `uvx ruff check .` passed with 0 errors
- [ ] `uvx ruff format --check .` passed
- [ ] pyproject.toml configured with [tool.ruff]
- [ ] target-version = "py311" set
- [ ] pydocstyle rules (D) enabled
- [ ] Pre-commit hooks configured (if applicable)
- [ ] No blanket `# noqa` comments without justification

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Ignoring Linter Errors with Blanket Noqa Comments

**Problem:** Adding `# noqa` or `# type: ignore` comments to silence linter errors without understanding or fixing the underlying issue.

**Why It Fails:** Hides real bugs and code quality issues. Blanket ignores accumulate technical debt. Future maintainers inherit suppressed warnings that may indicate security vulnerabilities or logic errors.

**Correct Pattern:**
```python
# BAD: Blanket ignore hides real issues
from module import *  # noqa
result = eval(user_input)  # type: ignore

# GOOD: Fix the issue or use specific ignore with justification
from module import specific_function, another_function

# If ignore is truly necessary, be specific and document why
result = legacy_api.call()  # noqa: S307 - legacy API requires eval, input is validated
```

### Anti-Pattern 2: Inconsistent Formatting Without Pre-commit Hooks

**Problem:** Relying on developers to manually run formatters before committing, leading to inconsistent code style across the codebase.

**Why It Fails:** Manual processes are forgotten. PRs contain formatting noise mixed with logic changes. Code reviews waste time on style issues instead of logic. Merge conflicts increase from formatting differences.

**Correct Pattern:**
```yaml
# .pre-commit-config.yaml - Automate formatting
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

# Install: pre-commit install
# Now formatting happens automatically on every commit
```

## Post-Execution Checklist
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
uv run pytest tests/
```

## Core Policy
- **Requirement:** Ruff is the authoritative default for linting and formatting.
- **Requirement:** Centralize Ruff configuration in `pyproject.toml`.
- **Requirement:** Set `target-version = "py311"` and exclude directories like `.venv`, `notebooks`, and `output`.
- **Always:** If Ruff is unavailable, fall back to `flake8` (lint) and `black` + `isort` (format/imports) with equivalent configuration. Document the chosen fallback in the PR.
 - **Requirement:** Enable pydocstyle (D) rules and set a single convention (`google` or `numpy`) consistent with `204-python-docs-comments.md`.

## Agent Workflow

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

## Compliance Checklist (MANDATORY)

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

## Taskfile Integration
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

lint-ty:
  desc: "Run ty type checker"
  cmds:
    - uvx ty check .

format:
  desc: "Auto-format code with ruff"
  cmds:
    - uvx ruff format .
    - uvx ruff check --fix .

lint:
  desc: "Run all code quality checks"
  cmds:
    - task: lint-ruff
    - task: lint-ty    # primary type checker (Astral toolchain)
    # - task: lint-mypy  # fallback: uv run mypy when mypy plugins needed
```

## Tool Isolation Benefits
- **Benefit:** `uvx ruff` ensures consistent tool versions across environments.
- **Benefit:** Avoids conflicts with project dependencies.
- **Benefit:** Faster execution without project environment overhead.
- **Rule:** Use `uvx` for development tools, `uv run` for project code execution.
