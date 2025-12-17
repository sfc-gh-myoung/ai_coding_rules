# Python Project Setup and Packaging

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Python packaging, project structure, setup.py, pyproject.toml, dependencies, package distribution, __init__.py, hatchling, uv, src layout
**TokenBudget:** ~2200
**ContextTier:** High
**Depends:** rules/200-python-core.md

## Purpose
Provide essential Python project setup and packaging guidance to avoid common build and dependency issues, covering package structure, pyproject.toml configuration, and proper dependency management practices.

## Rule Scope

Python project setup, packaging, and dependency management with modern build tools

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Always create __init__.py** - Even if empty, required for package recognition
- **Use pyproject.toml** - Modern build configuration, centralize all metadata
- **Specify package location** - `packages = ["app"]` in hatchling config
- **Create structure before install** - mkdir + __init__.py BEFORE `uv pip install -e .`
- **Use uv for dependency management** - `uv add package` not manual pyproject.toml edits
- **Never use bare pip** - Always use `uv` for consistency

**Quick Checklist:**
- [ ] All package directories have __init__.py
- [ ] pyproject.toml exists with [project] section
- [ ] [tool.hatch.build.targets.wheel] specifies packages
- [ ] Package structure created before installation
- [ ] Dependencies added via `uv add`
- [ ] Optional dependencies in [project.optional-dependencies]
- [ ] Package installable with `uv pip install -e .`

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Requirements.txt Without Version Pinning

**Problem:** Using unpinned dependencies (`requests`) or loose pins (`requests>=2.0`) in requirements.txt, allowing arbitrary version upgrades.

**Why It Fails:** Builds become non-reproducible. A dependency update can break production without any code changes. "Works on my machine" issues proliferate. Security vulnerabilities harder to track.

**Correct Pattern:**
```txt
# BAD: requirements.txt with loose versions
requests
pandas>=1.0
numpy

# GOOD: Fully pinned with hashes (use uv pip compile)
requests==2.31.0
pandas==2.1.4
numpy==1.26.3

# BEST: Use pyproject.toml + uv.lock for reproducible builds
# pyproject.toml defines ranges, uv.lock pins exact versions
```

### Anti-Pattern 2: Missing pyproject.toml in Modern Python Projects

**Problem:** Using setup.py or setup.cfg for project configuration instead of the modern pyproject.toml standard (PEP 517/518/621).

**Why It Fails:** setup.py is legacy and requires executing Python to read metadata. Tool configuration scattered across multiple files. Incompatible with modern build backends (hatch, flit, pdm). Package managers like uv expect pyproject.toml.

**Correct Pattern:**
```toml
# pyproject.toml - Single source of truth
[project]
name = "my-project"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "pandas>=2.0.0",
]

[tool.ruff]
line-length = 120

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

> **Investigation Required**
> When applying this rule:
> 1. **Read pyproject.toml BEFORE making packaging changes** - Check existing build system, package config
> 2. **Verify project structure** - Use list_dir to understand if src/ layout or flat layout
> 3. **Never assume package name** - Read pyproject.toml [project] name field
> 4. **Check for existing __init__.py files** - Don't duplicate or break existing structure
> 5. **Test installation** - Try `uv pip install -e .` after making changes
>
> **Anti-Pattern:**
> "Creating standard FastAPI structure... (without checking existing)"
> "Adding to pyproject.toml... (without reading it first)"
>
> **Correct Pattern:**
> "Let me check your project structure and pyproject.toml first."
> [reads files, checks layout, verifies build config]
> "I see you use a flat layout with 'app' as the package. Adding the new module following this pattern..."

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

## References

### External Documentation
- [Python Packaging User Guide](https://packaging.python.org/) - Official Python packaging documentation
- [pyproject.toml Specification](https://peps.python.org/pep-0621/) - PEP 621 specification for project metadata
- [Hatchling Documentation](https://hatch.pypa.io/latest/) - Modern Python build system and package manager

### Related Rules
- **Python Core**: `rules/200-python-core.md`
- **Python Linting**: `rules/201-python-lint-format.md`
- **YAML Config**: `rules/202-markup-config-validation.md`

## 1. Package Structure Requirements

### Critical Package Setup
- **Critical:** Always create `__init__.py` files for Python packages, even if empty.
- **Critical:** For projects using `pyproject.toml` with hatchling, ensure package directories exist before installation.
- **Critical:** Use `[tool.hatch.build.targets.wheel]` with `packages = ["app"]` to specify package location.
- **Always:** Create the main package directory structure before running `uv pip install -e .`.

### Example FastAPI Structure

Directory structure for `fastapi-project/`:
- `pyproject.toml`
- **app/** - Application package
  - `__init__.py` - Required for package recognition
  - `main.py`
  - **routers/** - `__init__.py` (Required for subpackages)
  - **models/** - `__init__.py`
  - **services/** - `__init__.py`
- **tests/** - `__init__.py`

### Example Command-Line App Structure

Directory structure for `cli-project/`:
- `pyproject.toml`
- **src/myapp/** - Source package
  - `__init__.py` - Required for package recognition
  - `main.py` - Entry point with click/argparse
  - **cli/** - `__init__.py`, `commands.py` (CLI command definitions)
  - **core/** - `__init__.py`, `logic.py` (Business logic)
  - **utils/** - `__init__.py`, `helpers.py` (Utility functions)
- **tests/** - `__init__.py`

## 2. pyproject.toml Configuration

### Build System Configuration
- **Critical:** Include `[tool.hatch.build.targets.wheel]` section when using hatchling.
- **Always:** Specify appropriate package list: `packages = ["app"]` for FastAPI or `packages = ["src/myapp"]` for CLI apps.
- **Always:** Use consistent naming between project name and main package.

### Dependency Management with uv
- **Critical:** Quote complex pip install arguments: `uv pip install -e ".[dev]"` not `uv pip install -e .[dev]`.
- **Always:** Use optional dependencies for development tools: `[project.optional-dependencies]`.
- **Always:** Group related dependencies logically (dev, test, docs).

## 3. Virtual Environment Setup

### uv Best Practices
- **Always:** Use `uv venv --clear` to ensure clean environment setup.
- **Always:** Activate virtual environment before installing packages.
- **Critical:** Install main package first, then optional dependencies: `uv pip install -e .` then `uv pip install -e ".[dev]"`.

### Common Installation Sequence
```bash
uv venv --clear
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
uv pip install -e ".[dev]"
```

## 4. Dependency Configuration

### Tool Configuration in pyproject.toml
- **Always:** Configure development tools (ruff, ty, mypy, pytest) in `[tool.TOOLNAME]` sections.
- **Always:** Use modern ruff configuration: `[tool.ruff.lint]` not deprecated top-level settings.
- **Always:** Include comprehensive tool configuration to avoid CLI arguments.

### Example Tool Configuration
```toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = []

# ty - Primary type checker (Astral toolchain)
# Configuration options expanding as ty matures
# See: https://docs.astral.sh/ty/
[tool.ty]
python-version = "3.11"

# mypy - Fallback type checker (when mypy plugins needed)
[tool.mypy]
python_version = "3.11"
disallow_untyped_defs = true
check_untyped_defs = true
```

## 5. Common Build Errors Prevention

### Hatchling Package Discovery
- **Critical:** Create package directories before running `uv pip install -e .`.
- **Critical:** Include `[tool.hatch.build.targets.wheel]` with explicit package list.
- **Always:** Verify package structure with `find . -name "__init__.py"` before installation.

### Shell Escaping Issues
- **Critical:** Always quote arguments with special characters in shell commands.
- **Critical:** Use double quotes for arguments containing brackets: `".[dev]"`.
- **Always:** Test shell commands independently before adding to automation tools.

## 6. Application-Specific Setup

### FastAPI Applications
- **Always:** Use application factory pattern (see `210-python-fastapi-core.md` for detailed patterns).
- **Always:** Separate main application module from entry point script.
- **Always:** Use proper import paths: `from app.main import app` not relative imports.
- **Always:** Use module execution for uvicorn (following `200-python-core.md` uv patterns).

### Command-Line Applications
- **Always:** Use `src/` layout for CLI apps to avoid import conflicts.
- **Always:** Define console scripts in `pyproject.toml`: `[project.scripts]` section.
- **Always:** Use Click or argparse for command-line interface parsing.
- **Always:** Separate CLI parsing from business logic (keep in different modules).
- **Consider:** Use `uv run python -m myapp` for module execution.

#### Console Scripts Configuration
```toml
[project.scripts]
myapp = "myapp.main:main"
myapp-dev = "myapp.cli.dev:dev_main"
```

## 7. Testing Setup

### Test Structure
- **Always:** Create `tests/` directory with `__init__.py`.
- **Always:** Use `pytest` configuration in `pyproject.toml`.
- **Always:** Configure test paths and coverage in `[tool.pytest.ini_options]`.

### Test Configuration Example
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = [
    "--strict-markers",
    "--cov=app",              # For FastAPI: --cov=app
    "--cov=src/myapp",        # For CLI apps: --cov=src/myapp
    "--cov-report=term-missing",
]
```

## 8. Troubleshooting Common Issues

### Build Failures
1. **"Unable to determine which files to ship"**: Add `[tool.hatch.build.targets.wheel]` with `packages` list.
2. **"No module named 'app'"** or **"No module named 'myapp'"**: Ensure `__init__.py` files exist and package is installed with `-e` flag.
3. **Shell escaping errors**: Quote all arguments with special characters.
4. **YAML parsing errors**: Avoid Unicode characters in automation files.

### Quick Fixes
- **Always:** Run `task --list` or equivalent to validate automation syntax.
- **Always:** Test package installation with `uv run python -c "import app"` (FastAPI) or `uv run python -c "import myapp"` (CLI) after setup.
- **Always:** Verify all `__init__.py` files exist with `find . -name "__init__.py"`.
- **Always:** For CLI apps, test console scripts: `uv run myapp --help` after installation.
