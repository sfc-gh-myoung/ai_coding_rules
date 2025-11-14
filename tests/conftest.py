"""Shared pytest fixtures for all test modules.

This module provides reusable fixtures following pytest best practices:
- Function-scoped fixtures by default
- Small, focused, single-responsibility fixtures
- Clear fixture composition
- Deterministic test execution with fixed seeds
"""

import random
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _seed_rng() -> None:
    """Seed random number generator for deterministic tests.

    This fixture runs automatically for all tests to ensure reproducibility.
    """
    random.seed(1337)


@pytest.fixture
def sample_rule_content() -> str:
    """Complete valid rule file content with all required sections.

    Returns:
        Rule content as string with proper metadata and sections
    """
    return """**Keywords:** test, example, sample, pytest
**TokenBudget:** ~500
**ContextTier:** High
**Version:** 1.0.0
**LastUpdated:** 2025-01-13
**Depends:** 000-global-core.md

# Test Rule

## Purpose
Test rule for validating rule processing and generation.

## Rule Type and Scope
- **Type:** Agent Requested
- **Scope:** Testing and validation

## Contract
- **Inputs/Prereqs:** None
- **Allowed Tools:** All
- **Forbidden Tools:** None
- **Required Steps:**
  1. Step one
  2. Step two
- **Output Format:** Text
- **Validation Steps:** Check output

## Quick Start TL;DR (Read First - 30 Seconds)
**Essential Patterns:**
- Pattern one
- Pattern two

## Quick Compliance Checklist
- [ ] Item 1
- [ ] Item 2

## Validation
- **Success Checks:** All checks pass
- **Negative Tests:** Error handling

## Response Template
```
Example template
```

## References
### External Documentation
- Example link
"""


@pytest.fixture
def minimal_rule_content() -> str:
    """Minimal rule file content with only required fields.

    Returns:
        Minimal rule content as string
    """
    return """**Keywords:** minimal, test
**TokenBudget:** ~100

# Minimal Rule

## Purpose
Minimal test rule.

## Rule Type and Scope
- **Type:** Agent Requested

## Contract
- **Inputs/Prereqs:** None

## Quick Compliance Checklist
- [ ] Item

## Validation
Success checks

## Response Template
Template

## References
Links
"""


@pytest.fixture
def rule_without_token_budget() -> str:
    """Rule file content missing TokenBudget metadata.

    Returns:
        Rule content without TokenBudget field
    """
    return """**Keywords:** test, no-budget
**ContextTier:** Medium

# Rule Without Budget

Content here.
"""


@pytest.fixture
def mock_template_dir(tmp_path: Path) -> Path:
    """Create a mock templates directory with sample rule files.

    Args:
        tmp_path: pytest tmp_path fixture

    Returns:
        Path to created templates directory
    """
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Create sample rule files
    (templates_dir / "000-global-core.md").write_text(
        """**Keywords:** core, foundation
**TokenBudget:** ~900

# Global Core
Foundation rule.
"""
    )

    (templates_dir / "200-python-core.md").write_text(
        """**Keywords:** Python, uv, ruff
**TokenBudget:** ~2400
**Depends:** 000-global-core.md

# Python Core
Python development standards.
"""
    )

    (templates_dir / "206-python-pytest.md").write_text(
        """**Keywords:** pytest, testing, fixtures
**TokenBudget:** ~2500
**Depends:** 200-python-core.md

# Python pytest
Testing best practices.
"""
    )

    # Create documentation file (should be skipped)
    (templates_dir / "README.md").write_text("# Documentation\nNot a rule.")

    return templates_dir


@pytest.fixture
def mock_project_root(tmp_path: Path) -> Path:
    """Create a mock project root with standard structure.

    Args:
        tmp_path: pytest tmp_path fixture

    Returns:
        Path to created project root directory
    """
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create standard directories
    (project_root / "scripts").mkdir()
    (project_root / "templates").mkdir()
    (project_root / "discovery").mkdir()

    # Create Taskfile.yml
    (project_root / "Taskfile.yml").write_text(
        """version: '3'
tasks:
  test:
    desc: Run tests
    cmds:
      - pytest
"""
    )

    # Create generator script placeholder
    (project_root / "scripts" / "generate_agent_rules.py").write_text("# Generator script\n")

    # Create AGENTS.md template in discovery/
    (project_root / "discovery" / "AGENTS.md").write_text(
        """# AGENTS.md Template
Path: {rule_path}

## Rule Loading Examples
- Load `{rule_path}/000-global-core.md` (foundation)
- Load `{rule_path}/200-python-core.md` (Python domain)
- Load `{rule_path}/206-python-pytest.md` (testing)

## Placeholder Examples
- `{rule_path}/[domain]-core.md` (e.g., 100-snowflake-core, 200-python-core)
- `{rule_path}/[specialized].md` (task-specific rules)

## References Section
- **@{rule_path}/000-global-core.md** - Foundational principles
- **@{rule_path}/002-rule-governance.md** - How rules are structured

## Non-Rule Files (should keep .md)
See RULES_INDEX.md and README.md for more information.
"""
    )

    # Create RULES_INDEX.md in discovery/
    (project_root / "discovery" / "RULES_INDEX.md").write_text(
        """# Rules Index

| File | Keywords |
|------|----------|
| 000-global-core.md | core |
"""
    )

    return project_root


@pytest.fixture
def sample_rule_file(tmp_path: Path, sample_rule_content: str) -> Path:
    """Create a sample rule file with complete content.

    Args:
        tmp_path: pytest tmp_path fixture
        sample_rule_content: Complete rule content from fixture

    Returns:
        Path to created rule file
    """
    rule_file = tmp_path / "100-test-rule.md"
    rule_file.write_text(sample_rule_content)
    return rule_file


@pytest.fixture
def mock_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Create isolated environment variables for testing.

    Args:
        monkeypatch: pytest monkeypatch fixture

    Returns:
        Dictionary of environment variables
    """
    env_vars = {
        "TEST_MODE": "true",
        "CI": "false",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def capture_output(capsys: pytest.CaptureFixture[str]) -> pytest.CaptureFixture[str]:
    """Fixture alias for capturing stdout/stderr.

    Args:
        capsys: pytest capsys fixture

    Returns:
        CaptureFixture for reading output
    """
    return capsys
