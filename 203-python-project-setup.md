**Description:** Python project setup and packaging best practices to avoid common build and dependency issues.
**AppliesTo:** `**/pyproject.toml`, `**/setup.py`, `**/requirements*.txt`, `**/__init__.py`
**AutoAttach:** false
**Type:** Agent Requested
**Keywords:** Python packaging, project structure, setup.py, pyproject.toml, dependencies, package distribution
**Version:** 1.3
**LastUpdated:** 2025-10-13


**TokenBudget:** ~500
**ContextTier:** High

# Python Project Setup and Packaging

## Purpose
Provide essential Python project setup and packaging guidance to avoid common build and dependency issues, covering package structure, pyproject.toml configuration, and proper dependency management practices.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Python project setup, packaging, and dependency management with modern build tools


## 1. Package Structure Requirements

### Critical Package Setup
- **Critical:** Always create `__init__.py` files for Python packages, even if empty.
- **Critical:** For projects using `pyproject.toml` with hatchling, ensure package directories exist before installation.
- **Critical:** Use `[tool.hatch.build.targets.wheel]` with `packages = ["app"]` to specify package location.
- **Always:** Create the main package directory structure before running `uv pip install -e .`.

### Example FastAPI Structure
```
fastapi-project/
├── pyproject.toml
├── app/
│   ├── __init__.py          # Required for package recognition
│   ├── main.py
│   ├── routers/
│   │   └── __init__.py      # Required for subpackages
│   ├── models/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
└── tests/
    └── __init__.py
```

### Example Command-Line App Structure
```
cli-project/
├── pyproject.toml
├── src/
│   └── myapp/
│       ├── __init__.py      # Required for package recognition
│       ├── main.py          # Entry point with click/argparse
│       ├── cli/
│       │   ├── __init__.py
│       │   └── commands.py  # CLI command definitions
│       ├── core/
│       │   ├── __init__.py
│       │   └── logic.py     # Business logic
│       └── utils/
│           ├── __init__.py
│           └── helpers.py   # Utility functions
└── tests/
    └── __init__.py
```

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
- **Always:** Configure development tools (ruff, mypy, pytest) in `[tool.TOOLNAME]` sections.
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

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Python Packaging User Guide](https://packaging.python.org/) - Official Python packaging documentation
- [pyproject.toml Specification](https://peps.python.org/pep-0621/) - PEP 621 specification for project metadata                                                                                                        
- [Hatchling Documentation](https://hatch.pypa.io/latest/) - Modern Python build system and package manager

### Related Rules
- **Python Core**: `200-python-core.md`
- **Python Linting**: `201-python-lint-format.md`
- **YAML Config**: `202-yaml-config-best-practices.md`
