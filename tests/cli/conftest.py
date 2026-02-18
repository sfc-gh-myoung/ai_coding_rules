"""Shared fixtures for ai-rules CLI tests."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules import cli as _cli_mod
from ai_rules._shared import console as _console_mod
from ai_rules.cli import app

# Disable ALL ANSI escape sequences (colors, bold, dim, etc.) from Rich
# Console singletons used by CLI commands.  NO_COLOR only strips colors but
# preserves style codes like \x1b[1m (bold), which still break plain-text
# assertions in CliRunner output.  Setting color_system=None on each Console
# instance disables every kind of ANSI output.
for _c in (_console_mod.console, _console_mod.err_console, _cli_mod.console):
    _c._color_system = None


@pytest.fixture
def runner() -> CliRunner:
    """Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def cli_app():
    """The ai-rules Typer app instance."""
    return app


@pytest.fixture
def sample_rules_dir(tmp_path: Path) -> Path:
    """Create a temporary rules directory with sample rule files."""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    rule = rules_dir / "000-test-rule.md"
    rule.write_text(
        """**Keywords:** test, example, validation
**TokenBudget:** ~500
**ContextTier:** High
**Depends:** none

# Test Rule

## Purpose
A sample rule for CLI testing.

## Rule Scope
Testing CLI commands

## Contract
- **Inputs/Prereqs:** Test environment
- **Allowed Tools:** All testing tools
- **Forbidden Tools:** None
- **Required Steps:**
  1. Validate input
  2. Execute test
  3. Verify output
- **Output Format:** Test results
- **Validation Steps:** Check assertions

## Quick Start TL;DR
**MANDATORY:**
**Essential Patterns:**
- Always validate
- Use proper isolation

## Anti-Patterns and Common Mistakes
**Anti-Pattern 1: Skipping Validation**
```python
# Bad
def process():
    return result
```
**Problem:** No input validation

**Correct Pattern:**
```python
# Good
def process(data):
    validate(data)
    return result
```
**Benefits:** Prevents errors

## Quick Compliance Checklist
- [ ] Tests isolated
- [ ] Assertions clear

## Validation
- **Success Checks:** All tests pass
- **Negative Tests:** Errors handled

## Response Template
```bash
pytest tests/
```

## References
### Related Rules
- `000-global-core.md`
"""
    )

    return rules_dir


@pytest.fixture
def sample_project(tmp_path: Path, sample_rules_dir: Path) -> Path:
    """Create a minimal project structure for CLI testing."""
    # pyproject.toml for project root detection
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "test-project"\nversion = "1.0.0"\n')

    # schemas dir
    schemas_dir = tmp_path / "schemas"
    schemas_dir.mkdir()

    return tmp_path
