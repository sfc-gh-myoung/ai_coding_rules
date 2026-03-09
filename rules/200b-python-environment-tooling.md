# Python Environment and Tooling

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** virtual environment, venv, uv, poetry, pip, pipenv, uvx, tool isolation, ModuleNotFoundError, environment setup, dependency management
**TokenBudget:** ~2100
**ContextTier:** High
**Depends:** 200-python-core.md
**LoadTrigger:** kw:venv, kw:virtual-environment, kw:uv, kw:poetry

## Scope

**What This Rule Covers:**
Virtual environment management, tool isolation patterns (uvx vs uv run), detailed command patterns for each toolchain (uv, poetry, pip), environment setup best practices, troubleshooting common environment issues, and project integration with Taskfile.

**When to Load This Rule:**
- Setting up Python development environments
- Managing virtual environments
- Troubleshooting ModuleNotFoundError or import issues
- Configuring tool isolation (uvx, pipx)
- Integrating Python tooling with Taskfile or Makefile

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Core Python patterns and toolchain detection

**Related:**
- **200a-python-validation-gate.md** - Validation gate commands per toolchain
- **203-python-project-setup.md** - Project structure and initialization

## Contract

### Inputs and Prerequisites

- Python 3.11+ available (or project's specified version)
- Project's dependency manager installed (uv, poetry, pip)
- pyproject.toml present (or creating new project)

### Mandatory

- Always use project's dependency manager to execute code
- Use isolated execution (uvx/pipx) for tools that don't import project code
- Use project environment (uv run/poetry run) for code that imports project modules

### Forbidden

- Mixing dependency managers (e.g., pip install in a poetry project)
- Running project code outside the project's virtual environment
- Installing development tools into the project's main dependencies

### Execution Steps

1. Identify project's toolchain (see 200-python-core.md Toolchain Detection)
2. Set up virtual environment using project's dependency manager
3. Install dependencies (including dev dependencies)
4. Verify environment is working (test module imports)
5. Configure tool isolation for development tools

### Output Format

```bash
# Environment ready state
# Python: 3.11.x
# Dependencies: installed via uv/poetry/pip
# Tools: ruff, ty available via uvx
```

### Validation

**Success Criteria:**
- Virtual environment created and activated
- All dependencies installed without conflicts
- Project modules importable
- Development tools accessible

### Design Principles

- **Toolchain Consistency:** Use one dependency manager per project
- **Tool Isolation:** Separate development tools from project dependencies
- **Reproducibility:** Lock files ensure consistent environments

### Post-Execution Checklist

- [ ] Project's toolchain identified (uv, poetry, pip)
- [ ] Virtual environment created and working
- [ ] Dependencies installed (including dev)
- [ ] Project modules importable
- [ ] Development tools accessible (ruff, ty/mypy, pytest)

## Virtual Environment Management

**Critical Principle:** Always use project's dependency manager to execute code

**If project uses uv:**
- `uv run python script.py` - Execute scripts
- `uv run pytest` - Run tests
- `uvx ruff check .` - Isolated linting

**If project uses poetry:**
- `poetry run python script.py` - Execute scripts
- `poetry run pytest` - Run tests
- `poetry run ruff check .` - Run linting (if ruff is a dev dependency)

**If project uses pip:**
- Activate venv first OR prefix with path to venv python
- `python script.py` - Execute scripts (venv active)
- `pytest` - Run tests (venv active)

## Tool Isolation Patterns

**Isolated Tool Execution (No Project Dependencies):**

Tools that don't import project code can run in isolation:

**uv projects:** Use `uvx` for isolated execution
```bash
uvx ruff check .      # Linter (no project imports)
uvx ruff format .     # Formatter (no project imports)
uvx ty check .        # Type checker (no project imports)
```

**poetry/pip projects:** Install tools as dev dependencies or use pipx
```bash
poetry run ruff check .    # If ruff in dev dependencies
pipx run ruff check .      # Isolated execution via pipx
```

**Project Environment Execution (Needs Project Dependencies):**

Commands that import project code MUST use project environment:

**uv projects:**
```bash
uv run pytest tests/               # Imports project code and plugins
uv run uvicorn app.main:app        # Imports app package
uv run python -m mypackage         # Runs module from project
```

**poetry projects:**
```bash
poetry run pytest tests/           # Imports project code and plugins
poetry run uvicorn app.main:app    # Imports app package
poetry run python -m mypackage     # Runs module from project
```

**pip projects:**
```bash
pytest tests/                      # Venv must be active
uvicorn app.main:app               # Venv must be active
python -m mypackage                # Venv must be active
```

**Decision rule:** Pure external tool, no project imports/plugins? Use `uvx`. Otherwise use `uv run` / `poetry run`.

## Command Patterns by Toolchain

**uv projects (uv.lock present):**
```bash
# Project execution
uv run python script.py
uv run uvicorn app.main:app --reload
uv run pytest tests/

# Isolated tools
uvx ruff check .
uvx ruff format .
uvx ty check .

# Environment management
uv python pin 3.11
uv sync --all-groups
uv lock --upgrade
```

**poetry projects (poetry.lock present):**
```bash
# Project execution
poetry run python script.py
poetry run uvicorn app.main:app --reload
poetry run pytest tests/

# Tools (if in dev dependencies)
poetry run ruff check .
poetry run mypy .

# Environment management
poetry install --with dev
poetry update
poetry lock
```

**pip projects (requirements.txt only):**
```bash
# Project execution (venv must be active)
python script.py
uvicorn app.main:app --reload
pytest tests/

# Tools (if installed in venv)
ruff check .
mypy .

# Environment management
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Environment Setup Best Practices

**uv projects:**
- Start with `uv python pin 3.11` to set Python version
- Use `uv sync --all-groups` to install dependencies
- Use `uv lock` before `uv sync` for consistency

**poetry projects:**
- Use `poetry install --with dev` to install dependencies
- Use `poetry lock` to update lock file

**pip projects:**
- Create venv: `python -m venv .venv`
- Activate: `source .venv/bin/activate` (Unix) or `.venv\Scripts\activate` (Windows)
- Install: `pip install -r requirements.txt`

## Troubleshooting Environment Issues

**ModuleNotFoundError diagnosis:**

1. **Check toolchain being used:**
   - uv project: Are you using `uv run`?
   - poetry project: Are you using `poetry run`?
   - pip project: Is venv activated?

2. **Verify dependencies installed:**
   - uv: `uv sync`
   - poetry: `poetry install`
   - pip: `pip install -r requirements.txt`

3. **Test module availability:**
   - uv: `uv run python -c "import module_name"`
   - poetry: `poetry run python -c "import module_name"`
   - pip: `python -c "import module_name"` (venv active)

## Project Integration

- **Rule:** Use project's toolchain consistently in Taskfile tasks and documentation
- **Pattern for Taskfile tasks:**
  - Detect toolchain: Check for uv.lock, poetry.lock, or Pipfile.lock
  - Use appropriate prefix: `uv run`, `poetry run`, or bare commands (pip)
- **Development tools:** Use isolated execution when possible (uvx, pipx) or install as dev dependencies
- **Always:** Include environment setup tasks with status checks to avoid redundant operations
- **Always:** Prefer `task validate` (or `task check` / `task ci`) when Taskfile.yml exists, falling back to direct tool commands otherwise
- **Documentation:** Provide setup instructions appropriate for project's chosen toolchain

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Mixing Dependency Managers

```bash
# Bad: Using pip install in a poetry project
# poetry.lock exists, but running:
pip install requests
```

**Problem:** Installs outside poetry's managed environment; dependency not tracked in pyproject.toml or poetry.lock; breaks reproducibility for other developers

**Correct Pattern:**
```bash
# Good: Use the project's dependency manager
poetry add requests
```

### Anti-Pattern 2: Running Project Code Without Environment

```bash
# Bad: Running project code without activating environment
python app/main.py
# ModuleNotFoundError: No module named 'fastapi'
```

**Problem:** Project dependencies are not available outside the virtual environment

**Correct Pattern:**
```bash
# Good: Use project's toolchain to run code
uv run python app/main.py      # uv project
poetry run python app/main.py  # poetry project
```
