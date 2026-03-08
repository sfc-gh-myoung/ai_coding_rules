"""Pytest configuration for AI coding rules tests."""

import os
import sys
from pathlib import Path

# Set NO_COLOR before any imports to ensure Rich Console instances
# are created with ANSI output disabled during tests
os.environ["NO_COLOR"] = "1"

import pytest  # noqa: E402

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_rule_content() -> str:
    """Sample rule content with TokenBudget metadata for testing."""
    return """**Keywords:** test, example, validation
**TokenBudget:** ~500
**ContextTier:** High
**Depends:** 000-global-core.md

# Sample Test Rule

## Purpose
A sample rule for testing token budget analysis and updates.

## Rule Scope
Testing token budget functionality

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


@pytest.fixture
def rule_without_token_budget() -> str:
    """Rule content missing TokenBudget metadata for testing."""
    return """**Keywords:** test, example
**ContextTier:** High
**Depends:** 000-global-core.md

# Rule Without Budget

## Purpose
Testing missing TokenBudget handling.

## Rule Scope
Missing budget test

## Contract
- **Inputs/Prereqs:** None
- **Allowed Tools:** All
- **Forbidden Tools:** None
- **Required Steps:** Test
- **Output Format:** Results
- **Validation Steps:** Check

## Quick Start TL;DR
**MANDATORY:**
**Essential Patterns:** Test patterns

## Anti-Patterns and Common Mistakes
**Anti-Pattern 1: Example**
```python
# Bad
pass
```
**Problem:** Issue

**Correct Pattern:**
```python
# Good
pass
```
**Benefits:** Better

## Quick Compliance Checklist
- [ ] Check

## Validation
- **Success Checks:** Pass

## Response Template
```bash
test
```

## References
### Related Rules
- `000-global-core.md`
"""


@pytest.fixture
def mock_template_dir(tmp_path: Path) -> Path:
    """Create a temporary directory with multiple rule files for testing batch operations."""
    rules_dir = tmp_path / "rules"
    rules_dir.mkdir()

    # Create rule with TokenBudget (000)
    rule1 = rules_dir / "000-global-core.md"
    rule1.write_text(
        """**Keywords:** test
**TokenBudget:** ~300
**ContextTier:** Medium
**Depends:** none

# Test Rule 1
Content here.
"""
    )

    # Create rule without TokenBudget (200)
    rule2 = rules_dir / "200-python-core.md"
    rule2.write_text(
        """**Keywords:** test
**ContextTier:** Low
**Depends:** 000-global-core.md

# Test Rule 2
More content.
"""
    )

    # Create rule with outdated TokenBudget (206)
    rule3 = rules_dir / "206-python-pytest.md"
    rule3.write_text(
        """**Keywords:** test
**TokenBudget:** ~100
**ContextTier:** High
**Depends:** 000-global-core.md

# Test Rule 3
"""
        + " ".join(["word"] * 500)  # ~650 tokens, much larger than declared
    )

    # Create README (not excluded by token_validator.py)
    readme = rules_dir / "README.md"
    readme.write_text(
        """# Rules Directory

This is a test README file.
"""
    )

    return rules_dir
