# Python Testing with pytest: Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** pytest, testing, fixtures, parametrization, test isolation, mocking, test organization, coverage, AAA pattern, test markers, uv run pytest
**TokenBudget:** ~3600
**ContextTier:** High
**Depends:** 200-python-core.md, 201-python-lint-format.md, 203-python-project-setup.md

## Scope

**What This Rule Covers:**
Pragmatic, industry-standard testing practices with pytest to produce fast, reliable, maintainable tests aligned with modern Python tooling conventions.

**When to Load This Rule:**
- Writing or modifying Python tests
- Setting up pytest configuration and fixtures
- Implementing test parametrization
- Organizing test suites (layout, markers, CI integration)
- Debugging test failures or flaky tests
- Adding test coverage to Python projects
- Integrating tests into CI/CD pipelines

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates
- **200-python-core.md** - Python core patterns (uv, pytest execution)

**Recommended:**
- **201-python-lint-format.md** - Ruff linting and formatting for test code
- **203-python-project-setup.md** - Project structure and pytest configuration

**Related:**
- **204-python-docs-comments.md** - Documentation standards for test docstrings
- **205-python-classes.md** - Class patterns for test organization

### External Documentation

**Official Documentation:**
- [pytest Documentation](https://docs.pytest.org/) - Official pytest docs
- [pytest Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) - Fixture patterns and scopes
- [pytest Parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html) - Test parametrization
- [pytest Marks](https://docs.pytest.org/en/stable/reference/reference.html#marks) - Test markers and selection

**Best Practices Guides:**
- [pytest Monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) - Environment and attribute patching
- [pytest tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html) - Temporary filesystem fixtures
- [pytest capsys/caplog](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html) - Output capture

## Contract

### Inputs and Prerequisites

- Python 3.11+ installed
- `uv` and `uvx` available
- Project configured per `200-python-core.md` (uv, Ruff, pytest)
- Test files or existing test suite identified

### Mandatory

- **Always use `uv run pytest`** - Never bare `pytest` command
- **AAA pattern** - Arrange (setup), Act (execute), Assert (verify)
- **Fixtures for setup** - Prefer fixtures over setUp/tearDown
- **Parametrize inputs** - Use `@pytest.mark.parametrize` instead of loops
- **Isolate externalities** - Use `tmp_path`, `monkeypatch`, `capsys`
- **Tests must pass** - MANDATORY gate before task completion
- **Lint and format** - Run `uvx ruff` on test code

### Forbidden

- Bare `pytest` command (use `uv run pytest`)
- Ad-hoc sleeps/timeouts without justification
- Tests coupled to execution order or global state
- Shared mutable fixtures
- Excessive mocking of internal implementation details
- Skipping tests without explicit user override

### Execution Steps

1. Organize tests under `tests/` with clear naming: `test_*.py` and `Test*` classes (optional)
2. Use AAA pattern (Arrange-Act-Assert); one behavior per test
3. Model setup with fixtures; avoid `setUp`/`tearDown`; keep fixtures small and focused
4. Parametrize inputs with `@pytest.mark.parametrize` instead of loops
5. Isolate external effects (I/O, time, randomness, env vars) with `tmp_path`, `monkeypatch`, `capsys`
6. Categorize tests with markers (e.g., `unit`, `integration`, `slow`) and filter in CI
7. Run via `uv run pytest`; ensure lints/format pass before completion

### Output Format

```python
# tests/test_user_service.py
import pytest
from yourapp.services import UserService

# Arrange-Act-Assert pattern
def test_create_user_success():
    # Arrange
    service = UserService()
    user_data = {"email": "test@example.com", "name": "Test User"}
    
    # Act
    result = service.create_user(user_data)
    
    # Assert
    assert result.id is not None
    assert result.email == "test@example.com"

# Parametrization
@pytest.mark.parametrize(
    "email,valid",
    [
        ("user@example.com", True),
        ("invalid-email", False),
        ("", False),
    ],
    ids=["valid", "missing_at", "empty"],
)
def test_email_validation(email: str, valid: bool):
    assert UserService.validate_email(email) == valid
```

```bash
# Validation commands
uv run pytest -q
uv run pytest -m "unit and not slow"
uv run pytest --cov=yourpkg --cov-report=term-missing
```

### Validation

**Pre-Task-Completion Test Execution Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**CRITICAL:** Test execution is MANDATORY before task completion. Tests are not optional.

**Test Execution:**
- **CRITICAL:** `uv run pytest` - All tests must pass before marking task complete
- **CRITICAL:** Never skip tests unless user explicitly requests override with acknowledged risks
- **CRITICAL:** Run tests immediately after code modifications, not in batches
- **Rule:** Do not mark tasks complete if ANY test fails
- **Rule:** Fix all test failures before responding to user
- **Exception:** Only skip with explicit user override (e.g., "skip tests") - acknowledge risks

**Code Quality:**
- **CRITICAL:** `uvx ruff check .` passes on test code
- **CRITICAL:** `uvx ruff format --check .` passes on test code
- **Format Check:** Tests follow AAA pattern (Arrange-Act-Assert)
- **Organization:** Tests in `tests/` directory, files named `test_*.py`

**Test Quality:**
- **Fixtures:** Small, explicit, function-scoped by default; minimal autouse
- **Parametrization:** Used for input matrices with clear ids
- **Isolation:** Time, randomness, env, FS, and network isolated
- **Markers:** Defined and used for selection; CI filters slow/e2e tests
- **Assertions:** Clear with meaningful failure messages

**Success Criteria:**
- `uv run pytest` passes with all tests passing
- Lint and format pass
- Tests are deterministic (no flaky failures)
- Meaningful failure messages
- CHANGELOG.md and README.md updated as required

**Test Execution Protocol:**
1. After any code modification, run `uv run pytest`
2. If tests fail, stop and report failures
3. Fix all failures
4. Re-run tests to confirm pass
5. Only then proceed to task completion

**Investigation Required:**
1. **Read existing test files BEFORE adding new tests** - Check current patterns, fixtures, organization
2. **Run `uv run pytest` to verify tests pass** - Never assume tests work without running them
3. **Never speculate about test coverage** - Run `uv run pytest --cov` to check actual coverage
4. **Check conftest.py for existing fixtures** - Don't create duplicate fixtures
5. **Make grounded recommendations** - Don't suggest patterns that conflict with existing tests

**Anti-Pattern Examples:**
- "Based on typical pytest projects, you probably have these fixtures..."
- "Let me add this test - it should work with the existing setup..."
- Marking task complete without running tests
- Skipping tests without user override

**Correct Pattern:**
- "Let me check the existing test structure first."
- [reads tests/ directory and conftest.py]
- "I see you're using pytest fixtures for database setup. Here's a new test following the same pattern..."
- [runs uv run pytest]
- "Tests passing (15/15). Task complete."

### Design Principles

- **Fast and Deterministic:** Tests must be hermetic, avoiding hidden time or network dependencies
- **Clear Intent:** Descriptive test names; one assertion group per behavior; meaningful failure messages
- **Fixtures Over Inheritance:** Prefer fixtures with appropriate scope; avoid deep dependency chains
- **Parametrize Broadly:** Use parametrization to cover input spaces succinctly
- **Isolate Externalities:** Patch environment, clock, filesystem, and network
- **Selective Execution:** Use markers to include/exclude categories in different pipelines
- **Visibility:** Capture logs and stdout/stderr when helpful; ensure `__repr__` is informative

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (000-global-core.md, 200-python-core.md)
- [ ] Python 3.11+ available
- [ ] uv and pytest installed
- [ ] Existing test structure reviewed

**After Completion:**
- [ ] **CRITICAL:** `uv run pytest` passed with all tests passing
- [ ] **CRITICAL:** Tests run via `uv run pytest` (never bare pytest)
- [ ] Tests live under `tests/` and follow naming conventions
- [ ] Fixtures small, explicit, function-scoped by default
- [ ] Parametrization used for input matrices with clear ids
- [ ] Isolation for time, randomness, env, FS, and network
- [ ] Markers defined and used for selection
- [ ] Assertions clear with meaningful messages
- [ ] Lints and formatting pass (`uvx ruff`)
- [ ] Optional coverage thresholds satisfied
- [ ] CHANGELOG.md and README.md updated as required

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Running Tests Without uv run Prefix

**Problem:** Executing pytest directly (`pytest tests/`) instead of using `uv run pytest tests/`, causing tests to run outside the project's virtual environment with wrong dependencies.

**Why It Fails:** Tests may pass locally but fail in CI/CD due to dependency mismatches, import errors occur when packages aren't in system Python, and version conflicts go undetected until production deployment.

**Correct Pattern:**
```bash
# BAD: Running pytest without uv
pytest tests/
python -m pytest tests/

# GOOD: Always use uv run
uv run pytest tests/
uv run pytest tests/ -v --tb=short
uv run pytest tests/test_specific.py::test_function
```

### Anti-Pattern 2: Using Broad Exception Catching in Test Assertions

**Problem:** Writing tests that catch all exceptions or use overly broad `try/except` blocks, hiding actual test failures and making debugging difficult.

**Why It Fails:** Tests pass when they should fail, root cause of failures is obscured, and debugging requires re-running tests with modified code. Broad exception handling defeats the purpose of testing.

**Correct Pattern:**
```python
# BAD: Broad exception catching hides failures
def test_division():
    try:
        result = divide(10, 0)
        assert result == 0  # Never reached, but test passes
    except:
        pass  # Swallows ZeroDivisionError, test passes incorrectly

# GOOD: Explicit exception testing with pytest.raises
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        divide(10, 0)

def test_division_success():
    result = divide(10, 2)
    assert result == 5  # Clear assertion, fails loudly if wrong
```

### Anti-Pattern 3: Creating Complex Fixture Dependency Chains

**Problem:** Building deeply nested fixture dependencies where fixtures depend on other fixtures which depend on more fixtures, creating hard-to-understand test setup.

**Why It Fails:** Test failures are hard to debug because setup logic is scattered across multiple fixtures, changing one fixture breaks unrelated tests, and new developers can't understand test requirements.

**Correct Pattern:**
```python
# BAD: Deep fixture dependency chain
@pytest.fixture
def database():
    return create_db()

@pytest.fixture
def user_table(database):
    return database.create_table("users")

@pytest.fixture
def test_user(user_table):
    return user_table.insert({"name": "test"})

@pytest.fixture
def user_session(test_user):
    return create_session(test_user)

def test_something(user_session):  # What does this need? Unclear!
    assert user_session.is_active()

# GOOD: Flat, explicit fixtures with composition
@pytest.fixture
def database():
    return create_db()

@pytest.fixture
def test_user(database):
    # Single fixture handles user creation directly
    table = database.create_table("users")
    return table.insert({"name": "test"})

def test_user_session(database, test_user):
    # Test explicitly requests what it needs
    session = create_session(test_user)
    assert session.is_active()
```

## Fixture Patterns and Best Practices
- Requirement: Prefer function-scoped fixtures; use module/session scope only for expensive shared setup.
- Rule: Avoid `autouse=True` except for universally required safety (e.g., environment isolation).
- Rule: Keep fixtures single-responsibility; compose instead of nesting complex dependency trees.

```python
# tests/conftest.py
import os
import pytest

@pytest.fixture()
def db_url(monkeypatch: pytest.MonkeyPatch) -> str:
    monkeypatch.setenv("DB_URL", "sqlite:///:memory:")
    return os.environ["DB_URL"]

@pytest.fixture()
def tmp_file(tmp_path):
    p = tmp_path / "data.txt"
    p.write_text("hello")
    return p
```

## Test Parametrization
- Requirement: Use `@pytest.mark.parametrize` for input matrices.
- Consider: Combine multiple parameters and ids for readability.

```python
import pytest

@pytest.mark.parametrize(
    "email,valid",
    [("a@example.com", True), ("bad", False)],
    ids=["ok", "invalid"],
)
def test_email_validation(email: str, valid: bool) -> None:
    assert ("@" in email) is valid
```

## Test Isolation and Mocking
- Rule: Control randomness with a fixed seed in setup; inject RNG where possible.
- Rule: Freeze or stub clocks for time-dependent code; avoid `time.sleep` in tests.
- Rule: Use `tmp_path` for filesystem; `monkeypatch` for env vars and module attributes; `capsys` for CLI output.
- Consider: Use `pytest-httpserver`/`responses` to stub HTTP; avoid live network.

```python
import random
import pytest

@pytest.fixture(autouse=True)
def _seed_rng():
    random.seed(1337)
```

## Test Markers and Selection
- Requirement: Define markers in `pyproject.toml` (or `pytest.ini`) with descriptions.
- Rule: Use markers like `unit`, `integration`, `slow`, `e2e` and filter in CI (e.g., `-m "not slow and not e2e"`).

```toml
[tool.pytest.ini_options]
markers = [
  "unit: fast, hermetic unit tests",
  "integration: tests requiring multiple components",
  "slow: long-running tests",
]
```

## Assertions and Error Handling
- Requirement: Use plain `assert` with helpful context; pytest rewrites provide clarity.
- Rule: Use `pytest.raises` for exceptions and assert on the message where relevant.

```python
import pytest

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ZeroDivisionError("division by zero")
    return a / b

def test_divide_raises_on_zero():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        divide(1, 0)
```

## Output Capture and Logging
- Rule: Use `capsys`/`caplog` to assert on stdout/stderr/logs.
- Consider: Configure log level for tests to reduce noise while preserving diagnostics.

```python
def main():
    print("ok")

def test_main_prints_ok(capsys):
    main()
    out, err = capsys.readouterr()
    assert out.strip() == "ok"
```

## Coverage and CI Integration
- Consider: Use `pytest-cov` for coverage reporting with realistic thresholds.
- Rule: Avoid coverage gaming; focus on assertion quality and meaningful branches.

```bash
uv run pytest --maxfail=1 --disable-warnings -q
uv run pytest --cov=yourpkg --cov-report=term-missing
```
