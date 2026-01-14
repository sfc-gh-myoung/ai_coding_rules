# Python Project Setup and Packaging

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** Python packaging, project structure, setup.py, pyproject.toml, dependencies, package distribution, __init__.py, hatchling, uv, src layout
**TokenBudget:** ~3600
**ContextTier:** High
**Depends:** 200-python-core.md

## Scope

**What This Rule Covers:**
Essential Python project setup and packaging guidance covering package structure, pyproject.toml configuration, dependency management, and build error prevention. Includes __init__.py requirements, hatchling build system configuration, uv-based dependency management, virtual environment setup, and modern packaging patterns (src layout, optional dependencies, entry points).

**When to Load This Rule:**
- Setting up new Python projects
- Creating Python packages or distributions
- Configuring pyproject.toml for builds
- Troubleshooting build or import errors
- Managing project dependencies with uv
- Encountering "package not found" or "module not found" errors
- Converting legacy setup.py to pyproject.toml

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Python foundation patterns

**Related:**
- **201-python-lint-format.md** - Code quality configuration in pyproject.toml
- **204-python-docs-comments.md** - Documentation standards
- **206-python-pytest.md** - Type checking configuration

### External Documentation

- [PEP 621](https://peps.python.org/pep-0621/) - pyproject.toml project metadata
- [Hatchling](https://hatch.pypa.io/latest/config/build/) - Modern Python build backend
- [uv Documentation](https://docs.astral.sh/uv/) - Fast Python package manager

## Contract

### Inputs and Prerequisites

- Python project directory
- Understanding of package structure concepts
- uv installed for dependency management
- Basic knowledge of pyproject.toml format

### Mandatory

- **Always create __init__.py** files (even if empty) for package recognition
- Use pyproject.toml for modern build configuration
- Specify package location in hatchling config: `packages = ["app"]`
- Create structure before install (mkdir + __init__.py BEFORE `uv pip install -e .`)
- Use `uv add package` for dependency management (not manual edits)
- Never use bare `pip` (always use `uv`)

### Forbidden

- Using bare `pip` commands (use `uv` instead)
- Manual pyproject.toml dependency edits (use `uv add`)
- Missing __init__.py files in packages
- Unpinned dependencies in production
- Legacy setup.py in new projects

### Execution Steps

1. Create project structure with package directories
2. Add __init__.py to all package directories
3. Create pyproject.toml with [project] section
4. Configure [tool.hatch.build.targets.wheel] with packages
5. Add dependencies using `uv add package`
6. Install package in editable mode: `uv pip install -e .`
7. Verify package is importable

### Output Format

Project setup produces:
- Structured package directories with __init__.py files
- pyproject.toml with complete project metadata
- Virtual environment with dependencies installed
- Installable package (editable or distribution)

### Validation

**Pre-Task-Completion Checks:**
- [ ] All package directories have __init__.py
- [ ] pyproject.toml exists with [project] section
- [ ] [tool.hatch.build.targets.wheel] specifies packages
- [ ] Package structure created before installation
- [ ] Dependencies added via `uv add`

**Success Criteria:**
- Package installable with `uv pip install -e .`
- Imports work correctly: `python -c "import mypackage"`
- Dependencies resolve without conflicts
- Build succeeds: `uv build`

**Negative Tests:**
- Missing __init__.py should cause import errors
- Incorrect package specification should fail build
- Circular dependencies should be detected

### Design Principles

- **Modern tooling:** Use pyproject.toml and uv, not legacy setup.py
- **Explicit structure:** Always include __init__.py for clarity
- **Reproducible builds:** Pin dependencies, use lock files
- **Isolation:** Use virtual environments, never global installs
- **Build-first:** Validate package structure before distribution

### Post-Execution Checklist

- [ ] All package directories have __init__.py
- [ ] pyproject.toml exists with [project] section
- [ ] [tool.hatch.build.targets.wheel] specifies packages
- [ ] Package structure created before installation
- [ ] Dependencies added via `uv add`
- [ ] Optional dependencies in [project.optional-dependencies]
- [ ] Package installable with `uv pip install -e .`
- [ ] Imports verified with test script

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

## Package Structure Requirements

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

## pyproject.toml Configuration

### Build System Configuration
- **Critical:** Include `[tool.hatch.build.targets.wheel]` section when using hatchling.
- **Always:** Specify appropriate package list: `packages = ["app"]` for FastAPI or `packages = ["src/myapp"]` for CLI apps.
- **Always:** Use consistent naming between project name and main package.

### Dependency Management with uv
- **Critical:** Quote complex pip install arguments: `uv pip install -e ".[dev]"` not `uv pip install -e .[dev]`.
- **Always:** Use optional dependencies for development tools: `[project.optional-dependencies]`.
- **Always:** Group related dependencies logically (dev, test, docs).

## Virtual Environment Setup

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

## Dependency Configuration

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

## Common Build Errors Prevention

### Hatchling Package Discovery
- **Critical:** Create package directories before running `uv pip install -e .`.
- **Critical:** Include `[tool.hatch.build.targets.wheel]` with explicit package list.
- **Always:** Verify package structure with `find . -name "__init__.py"` before installation.

### Shell Escaping Issues
- **Critical:** Always quote arguments with special characters in shell commands.
- **Critical:** Use double quotes for arguments containing brackets: `".[dev]"`.
- **Always:** Test shell commands independently before adding to automation tools.

## Application-Specific Setup

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

## Testing Setup

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

## Troubleshooting Common Issues

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
