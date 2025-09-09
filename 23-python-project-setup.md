**Description:** Python project setup and packaging best practices to avoid common build and dependency issues.
**Applies to:** `**/pyproject.toml`, `**/setup.py`, `**/requirements*.txt`, `**/__init__.py`
**Auto-attach:** false


# Python Project Setup and Packaging

## 1. Package Structure Requirements

### Critical Package Setup
- **Critical:** Always create `__init__.py` files for Python packages, even if empty.
- **Critical:** For projects using `pyproject.toml` with hatchling, ensure package directories exist before installation.
- **Critical:** Use `[tool.hatch.build.targets.wheel]` with `packages = ["app"]` to specify package location.
- **Always:** Create the main package directory structure before running `uv pip install -e .`.

### Example Structure
```
project/
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

## 2. pyproject.toml Configuration

### Build System Configuration
- **Critical:** Include `[tool.hatch.build.targets.wheel]` section when using hatchling.
- **Always:** Specify `packages = ["app"]` or appropriate package list.
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
python_version = "3.12"
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

## 6. FastAPI Specific Setup

### Application Structure
- **Always:** Use application factory pattern for FastAPI apps.
- **Always:** Separate main application module from entry point script.
- **Always:** Use proper import paths: `from app.main import app` not relative imports.

### Entry Point Configuration
- **Recommended:** Create separate `main.py` entry point that imports from package.
- **Always:** Use module execution for uvicorn: `python -m uvicorn app.main:app`.
- **Always:** Configure application in package, not in root entry point.

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
    "--cov=app",
    "--cov-report=term-missing",
]
```

## 8. Troubleshooting Common Issues

### Build Failures
1. **"Unable to determine which files to ship"**: Add `[tool.hatch.build.targets.wheel]` with `packages` list.
2. **"No module named 'app'"**: Ensure `app/__init__.py` exists and package is installed with `-e` flag.
3. **Shell escaping errors**: Quote all arguments with special characters.
4. **YAML parsing errors**: Avoid Unicode characters in automation files.

### Quick Fixes
- **Always:** Run `task --list` or equivalent to validate automation syntax.
- **Always:** Test package installation with `python -c "import app"` after setup.
- **Always:** Verify all `__init__.py` files exist with `find . -name "__init__.py"`.