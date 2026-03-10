# Python Pre-Task-Completion Validation Gate

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** validation, type checking, linting, formatting, pytest, ruff, ty, mypy, pre-task, gate, syntax
**TokenBudget:** ~3050
**ContextTier:** High
**Depends:** 200-python-core.md
**LoadTrigger:** kw:validate, kw:type-check, kw:lint

## Scope

**What This Rule Covers:**
The mandatory Pre-Task-Completion Validation Gate for all Python tasks: linting, formatting, type checking, syntax validation, test execution, and documentation updates. Includes the ty vs mypy decision tree and toolchain-specific validation commands.

**When to Load This Rule:**
- Before marking any Python task as complete
- When running validation checks (lint, format, type check, tests)
- When configuring type checking (ty vs mypy)
- When troubleshooting validation failures

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Core Python patterns and toolchain detection

**Related:**
- **201-python-lint-format.md** - Detailed Ruff linting and formatting
- **206-python-pytest.md** - Comprehensive testing patterns

## Contract

### Inputs and Prerequisites

- Python project with toolchain identified (see 200-python-core.md Toolchain Detection)
- Modified Python files ready for validation
- Test suite available (if project has tests)

### Mandatory

- All validation checks must pass before marking any Python task complete
- Type checking is mandatory on every file modification
- Do not use `# type: ignore` without documenting the specific error code and reason

### Forbidden

- Marking tasks complete without running the validation gate
- Using bare `# type: ignore` without a specific error code
- Skipping tests unless user explicitly requests override

### Pre-Commit Hook Integration

Automate validation with pre-commit hooks:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: local
    hooks:
      - id: type-check
        name: Type Check (ty)
        entry: uvx ty check src/
        language: system
        types: [python]
        pass_filenames: false
      - id: pytest-quick
        name: Quick Tests
        entry: uv run pytest -x -q --no-header
        language: system
        types: [python]
        pass_filenames: false
```

**Install hooks:**
```bash
uv add --group dev pre-commit
uv run pre-commit install
uv run pre-commit run --all-files  # Verify setup
```

### Execution Steps

1. Run linting check (must pass with zero errors)
2. Run formatting check (must pass)
3. Run type checking (must pass with zero errors)
4. Run syntax validation on all modified files
5. Run test suite (must pass)
6. Update CHANGELOG.md and README.md as required
7. Confirm all checks pass before marking task complete

### Output Format

```bash
# Validation output (target state)
# Linting: 0 errors
# Formatting: 0 files would be reformatted
# Type checking: 0 errors
# Tests: 12 passed
# Task complete.
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**CRITICAL:** Before marking any Python task as complete, ALL of the following checks MUST pass:

**Code Quality (use project's toolchain):**
- **CRITICAL:** Linting check - Must pass with zero errors
  - **uv:** `uvx ruff check .`
  - **poetry:** `poetry run ruff check .` (or `poetry run flake8 .`)
  - **pip:** `ruff check .` (or `flake8 .`)
- **CRITICAL:** Format check - Must pass, code properly formatted
  - **uv:** `uvx ruff format --check .`
  - **poetry:** `poetry run ruff format --check .` (or `poetry run black --check .`)
  - **pip:** `ruff format --check .` (or `black --check .`)
- **CRITICAL:** Type check - Must pass with zero type errors
  - **uv:** `uvx ty check .` (primary) or `uv run mypy .` (fallback)
  - **poetry:** `poetry run mypy .`
  - **pip:** `mypy .`
- **CRITICAL:** Syntax validation - All Python files compile without syntax errors
  - **All toolchains:** `find . -name "*.py" -exec python -m py_compile {} +` (using project's Python)

**Test Execution (use project's toolchain):**
- **CRITICAL:** All tests must pass (for projects with test suites)
  - **uv:** `uv run pytest`
  - **poetry:** `poetry run pytest`
  - **pip:** `pytest`
- **Rule:** Never skip tests unless user explicitly requests override

**Documentation:**
- **CRITICAL:** Update `CHANGELOG.md` with entry under `## [Unreleased]` for code changes
- **CRITICAL:** Review and update `README.md` when triggers apply (see `000-global-core.md` section 6)

**Gate Rules:**
- **Rule:** Run validation immediately after modifications, not in batches
- **Rule:** Do not mark tasks complete if ANY check fails
- **Rule:** Fix all failures before responding to user
- **Exception:** Only skip with explicit user override — acknowledge risks

**Success Criteria:**
- All code quality checks pass (ruff, ty/mypy, py_compile)
- All tests pass
- Documentation updated
- Pre-Task-Completion Validation Gate passed

**Negative Tests:**
- Task marked complete without running `ruff check` fails the gate
- Code using `datetime.utcnow()` is caught by linter
- Bare `except:` clause fails ruff check (B001/E722)
- Running `uv run` on a poetry project triggers investigation-first warning
- Missing CHANGELOG.md entry for code changes fails documentation check

### Design Principles

- **Zero Tolerance:** All checks must pass with 0 errors
- **Immediate Feedback:** Run validation after each modification, not in batches
- **No Silent Failures:** Every check failure must be addressed before task completion

### Validation Failure Recovery

When validation fails, follow this sequence:

1. **Lint failures:** Run `uv run ruff check . --fix` to auto-fix. Review changes before committing.
2. **Format failures:** Run `uv run ruff format .` to auto-format. Always safe to auto-apply.
3. **Type check failures:**
   - Read the error message carefully — ty/mypy errors are precise
   - Add type annotations to untyped parameters
   - Use `assert isinstance(x, Type)` to narrow types instead of `# type: ignore`
   - If genuinely unfixable: `# type: ignore[specific-error]` with comment explaining why
4. **Test failures:**
   - Run failing test in isolation: `uv run pytest path/to/test.py::test_name -vvs`
   - Check if failure is pre-existing: `git stash && uv run pytest path/to/test.py::test_name`
   - Fix the code, not the test (unless test itself is wrong)
5. **Multiple failures:** Fix in order: format, then lint, then type check, then tests (each may resolve downstream issues)

### CI/CD Pipeline Configuration

Replicate the validation gate in CI:

```yaml
# .github/workflows/validate.yml
name: Python Validation Gate
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - run: uv sync --frozen
      - name: Lint
        run: uv run ruff check .
      - name: Format Check
        run: uv run ruff format --check .
      - name: Type Check
        run: uvx ty check src/
      - name: Tests
        run: uv run pytest --tb=short -q
```

**Key principles:**
- Use `--frozen` to prevent lockfile changes in CI
- Run lint before tests (faster feedback)
- Use `--check` flags (don't auto-fix in CI)

### Post-Execution Checklist

- [ ] Linting passed with zero errors
- [ ] Formatting check passed
- [ ] Type checking passed with zero type errors
- [ ] Syntax validation passed (all Python files compile)
- [ ] All tests passed (if test suite exists)
- [ ] CHANGELOG.md updated for code changes
- [ ] README.md reviewed and updated if triggers apply

## Syntax Validation

- **Rule:** Before completing any task involving Python code changes, verify that all modified files are syntactically correct.
- **Rule:** Use `python -m py_compile` as a definitive check for syntax errors, in addition to linter feedback.
- **Command (use project's Python):**
  - **uv:** `uv run python -m py_compile -q <path>`
  - **poetry:** `poetry run python -m py_compile -q <path>`
  - **pip:** `python -m py_compile -q <path>` (venv active)

## Type Checking Decision Tree

**Recommended Type Checkers:**

**Primary (Modern, Fast):**
- **ty** - Extremely fast type checker from Astral (uv/ruff creators), written in Rust
- Best for new projects and Astral toolchain users
- Isolated execution via `uvx ty check .`

**Alternative (Mature, Plugins):**
- **mypy** - Mature type checker with extensive plugin ecosystem
- Required for Django, SQLAlchemy, and other frameworks needing plugins
- Execution via project environment: `poetry run mypy .` or `uv run mypy .`

**When to Use ty vs mypy:**

- **Speed:** ty is ~100x faster (Rust-based); mypy is slower (Python, incremental caching helps)
- **Config:** ty has zero-config by default; mypy requires `mypy.ini` or `pyproject.toml`
- **Plugin support:** ty has none (as of 2026); mypy has rich plugin ecosystem (django-stubs, sqlalchemy-stubs)
- **Strictness:** ty is strict by default; mypy is configurable (`--strict`, `--disallow-untyped-defs`)
- **Install:** ty uses `uvx ty check src/`; mypy uses `uv run mypy src/`
- **Best for:** ty suits new projects with fast feedback; mypy suits Django/SQLAlchemy projects needing stubs

**Decision:**
- **New projects:** Use ty (faster, simpler)
- **Existing projects:** Match existing type checker
- **Django/SQLAlchemy:** Use mypy with stubs until ty supports plugins

**Configuration in pyproject.toml:**
```toml
# ty configuration (for new ty projects)
[tool.ty]
python-version = "3.11"

# mypy configuration (for existing mypy projects)
[tool.mypy]
python_version = "3.11"
strict = true
```

**Integration with Validation Gate:**
- **CRITICAL:** Type checking (ty or mypy) is part of mandatory Pre-Task-Completion Validation Gate
- **Rule:** Type errors must be resolved before marking tasks complete
- **Rule:** Do not use `# type: ignore` without documenting the reason
  ```python
  # BAD - bare ignore hides real bugs
  result = some_untyped_lib()  # type: ignore

  # GOOD - specific error code + reason
  result = some_untyped_lib()  # type: ignore[no-untyped-call]  # third-party lib has no stubs
  ```

> **Investigation Required:**
> Before running validation:
> 1. Check which type checker the project uses (ty, mypy, pyright)
> 2. Check pyproject.toml for existing lint/format/type-check configuration
> 3. Check for `.pre-commit-config.yaml` — if present, use `pre-commit run` instead of manual commands
> 4. Check for CI configuration (`.github/workflows/`) — local validation should match CI
> 5. Check if project has custom Ruff rules or ignores that affect validation

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Skipping Validation Before Task Completion

```python
# AI makes code changes to fix a bug
# AI: "I've fixed the bug in user_service.py. Task complete!"
# [No ruff check, no ruff format, no pytest run]
```

**Problem:** May introduce linting violations; formatting inconsistencies; broken tests; syntax errors discovered later by user

**Correct Pattern:**
```bash
# After making changes, always validate using project's toolchain:
uvx ruff check .         # or: poetry run ruff check .
uvx ruff format --check . # or: poetry run ruff format --check .
uvx ty check .           # or: poetry run mypy .
uv run pytest            # or: poetry run pytest

# Only after ALL pass:
# "Changes validated: linting clean, formatting clean, types clean, tests passing (12/12). Task complete."
```

### Anti-Pattern 2: Skipping Type Checking

```python
# AI makes code changes
# AI: "I've updated the data processing function. Task complete!"
# [No type checking run - potential type errors undetected]
```

**Problem:** Type errors discovered later; runtime crashes from type mismatches

**Correct Pattern:**
```bash
# Always run type checking as part of validation:
uvx ty check .  # or: poetry run mypy .
```
