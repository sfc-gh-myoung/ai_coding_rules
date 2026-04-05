# Python Testing with pytest: Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-25
**Keywords:** pytest, testing, fixtures, parametrization, test isolation, mocking, test organization, coverage, AAA pattern, test markers, uv run pytest, unit test, unit tests
**TokenBudget:** ~4950
**ContextTier:** High
**Depends:** 000-global-core.md, 200-python-core.md, 201-python-lint-format.md, 203-python-project-setup.md
**LoadTrigger:** kw:test, kw:pytest, kw:coverage

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
- Excessive mocking of internal implementation details (do not mock >3 private methods [_prefix] or module-level functions not in the public API per test; prefer testing through public interfaces)
- Skipping tests without explicit user override
  - Valid skip reasons:
    1. **Platform-specific:** `@pytest.mark.skipif(sys.platform == "win32", reason="Unix-only feature")`
    2. **Missing dependency:** `@pytest.mark.skipif(not HAS_REDIS, reason="Redis not installed")`
    3. **Known bug with ticket:** `@pytest.mark.skip(reason="BUG-1234: Flaky due to race condition, fix in progress")`
    4. **Environment-specific:** `@pytest.mark.skipif(not os.getenv("CI"), reason="Only runs in CI")`
  - Invalid skip reasons: "TODO: fix later", "Flaky" without a ticket, bare `@pytest.mark.skip()` without `reason=`

### Execution Steps

1. Organize tests under `tests/` using `test_<module>_<behavior>.py` naming; `Test*` classes optional
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

### Post-Execution Checklist

See comprehensive Post-Execution Checklist in the Flaky Test Protocol section below.

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
- **Fixtures Over Inheritance:** Prefer function-scoped fixtures (use module/session only for setup >1s); avoid deep dependency chains
- **Parametrize Broadly:** Use parametrization to cover input spaces succinctly
- **Isolate Externalities:** Patch environment, clock, filesystem, and network
- **Selective Execution:** Use markers to include/exclude categories in different pipelines
- **Visibility:** Capture logs/stdout when the function under test writes output as part of its contract; ensure `__repr__` is informative

## Flaky Test Protocol

When a test passes and fails intermittently:

1. **Identify:** Run the test 10 times to confirm flakiness:
   ```bash
   uv run pytest tests/test_suspect.py::test_name --count=10 -x
   # Requires: uv add --dev pytest-repeat
   ```

2. **Classify the cause:**
   - **Race condition (Fails under load or parallel):** Add locks or make test sequential (`@pytest.mark.serial`)
   - **Time dependency (Fails near midnight/DST):** Use `freezegun` or `time-machine` to freeze time
   - **Resource leak (Fails late in suite):** Add proper teardown in fixture
   - **External service (Fails on network issues):** Mock the external call or use `vcr.py`

3. **Fix or quarantine** — never leave flaky tests unmarked:
   ```python
   @pytest.mark.xfail(reason="BUG-1234: Race condition in cache invalidation", strict=False)
   def test_cache_update():
       ...
   ```

4. **Track:** Every `xfail` must have a ticket number. Review quarantined tests weekly.

## Flaky Test Protocol

When a test passes and fails intermittently:

1. **Identify:** Run the test 10 times to confirm flakiness:
   ```bash
   uv run pytest tests/test_suspect.py::test_name --count=10 -x
   # Requires: uv add --dev pytest-repeat
   ```

2. **Classify the cause:**
   - **Race condition (Fails under load or parallel):** Add locks or make test sequential (`@pytest.mark.serial`)
   - **Time dependency (Fails near midnight/DST):** Use `freezegun` or `time-machine` to freeze time
   - **Resource leak (Fails late in suite):** Add proper teardown in fixture
   - **External service (Fails on network issues):** Mock the external call or use `vcr.py`

3. **Fix or quarantine** — never leave flaky tests unmarked:
   ```python
   @pytest.mark.xfail(reason="BUG-1234: Race condition in cache invalidation", strict=False)
   def test_cache_update():
       ...
   ```

4. **Track:** Every `xfail` must have a ticket number. Review quarantined tests weekly.

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
- Rule: Prefer function-scoped fixtures; use module/session scope only for setup taking >1 second (e.g., database connections, large file generation, external service initialization).
- Rule: Only use `autouse=True` fixtures for these specific cases:
  1. **Database cleanup:** Rollback/truncate after each test to prevent test pollution
  2. **Temporary directory:** Create and clean up temp files
  3. **Environment variable reset:** Restore `os.environ` after tests that modify it
  4. **Freeze time:** Reset mocked time (when using `freezegun` or `time-machine`)
  
  **Never use `autouse=True` for:** Test data setup (use explicit fixtures), logging configuration, mock setup (be explicit about what's mocked).
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
- Rule: Use `@pytest.mark.parametrize` for input matrices.
- Rule: When a function accepts >3 parameters, combine multiple parameters into tuples or dataclasses and use ids for readability.

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

### Parametrize Best Practices
- Rule: Always provide `ids=` for parametrized tests to make failure output readable.
- Rule: Limit parameter sets to ≤10 per test. If you need more, split into separate test functions or use `pytest.param` with marks:
  ```python
  @pytest.mark.parametrize("input_val,expected", [
      pytest.param("valid", True, id="happy-path"),
      pytest.param("", False, id="empty-string"),
      pytest.param(None, False, id="none-value", marks=pytest.mark.xfail),
  ])
  def test_validation(input_val, expected):
      assert validate(input_val) is expected
  ```
- Rule: Group related parameters into tuples or dataclasses rather than having >3 separate parametrize arguments.
- Rule: For parametrize sets >50 entries, use `pytest_generate_tests` or load test data from a fixture/file to keep test files readable and avoid slow collection.
- Rule: Avoid duplicate entries in parametrize sets — pytest runs them separately but duplicate ids cause confusing output. Use `set()` or unique ids to detect.

## Test Isolation and Mocking
- Rule: Control randomness with a fixed seed in setup; inject RNG where possible.
- Rule: Freeze or stub clocks for time-dependent code; avoid `time.sleep` in tests.
- Rule: Use `tmp_path` for filesystem; `monkeypatch` for env vars and module attributes; `capsys` for CLI output.
- Rule: When tests make HTTP calls, use `pytest-httpserver`/`responses` to stub HTTP; avoid live network.

```python
import random
import pytest

@pytest.fixture(autouse=True)
def _seed_rng():
    random.seed(1337)
```

## Resource-Aware Testing
- Rule: Use `tmp_path` (auto-cleanup) for disk-intensive tests to prevent leftover artifacts.
- Rule: Use `pytest-timeout` for long-running tests to prevent CI hangs: `@pytest.mark.timeout(30)`.
- Rule: Mark slow tests with `@pytest.mark.slow` based on these thresholds:
  - **Unit tests:** >500ms is slow (expected: <100ms each)
  - **Integration tests:** >5s is slow (expected: <2s each)
  - **E2E tests:** >30s is slow (expected: <10s each)
  
  Run without slow tests for fast feedback: `uv run pytest -m "not slow"`

## Test Markers and Selection
- Rule: Define markers in `pyproject.toml` (or `pytest.ini`) with descriptions.
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
- Rule: Use plain `assert` with helpful context; pytest rewrites provide clarity.
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
- Rule: When tests produce noisy log output, set `log_cli_level = "WARNING"` in pyproject.toml; use `@pytest.mark.filterwarnings` or `caplog.set_level(logging.ERROR)` for noisy tests.

```python
def main():
    print("ok")

def test_main_prints_ok(capsys):
    main()
    out, err = capsys.readouterr()
    assert out.strip() == "ok"
```

## Coverage and CI Integration
- Rule: Target 80% line coverage; 90% for modules in `src/*/services/`, `src/*/domain/`, or `src/*/core/` directories — excluding tests, configs, and migration scripts. Use `pytest-cov` for coverage reporting.
- Rule: Avoid coverage gaming; focus on assertion quality and meaningful branches.

```bash
uv run pytest --maxfail=1 --disable-warnings -q
uv run pytest --cov=yourpkg --cov-report=term-missing
```
