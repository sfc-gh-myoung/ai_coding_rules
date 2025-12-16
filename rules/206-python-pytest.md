# Python Testing with pytest: Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** pytest, testing, fixtures, parametrization, test isolation, mocking, test organization, coverage, AAA pattern, test markers, uv run pytest
**TokenBudget:** ~2050
**ContextTier:** High
**Depends:** rules/200-python-core.md, rules/201-python-lint-format.md, rules/203-python-project-setup.md

## Purpose
Define pragmatic, industry-standard testing practices with pytest to produce fast, reliable, maintainable tests that are easy to run locally and in CI, aligned with this repository's Python tooling conventions.

## Rule Scope

pytest usage for Python 3.11+ projects (test layout, fixtures, parametrization, isolation, markers, CI integration)

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Always use `uv run pytest`** - Never bare `pytest` command
- **AAA pattern** - Arrange (setup), Act (execute), Assert (verify) - one behavior per test
- **Fixtures for setup** - Prefer fixtures over setUp/tearDown, keep them small and focused
- **Parametrize inputs** - Use `@pytest.mark.parametrize` instead of loops
- **Isolate externalities** - Use `tmp_path`, `monkeypatch`, `capsys` for I/O, env, time
- **Tests must pass before completion** - MANDATORY gate, never skip without explicit user override
- **Never use bare `assert` without context** - Include descriptive failure messages

**Quick Checklist:**
- [ ] Tests in `tests/` directory, files named `test_*.py`
- [ ] Run `uv run pytest` (not bare `pytest`)
- [ ] AAA pattern: Arrange-Act-Assert
- [ ] Fixtures for setup (not setUp/tearDown)
- [ ] Parametrize with `@pytest.mark.parametrize`
- [ ] Isolate I/O with `tmp_path`, `monkeypatch`
- [ ] All tests pass before task completion

## Contract

<contract>
<inputs_prereqs>
Python 3.11+; `uv` and `uvx` installed; project configured per `200-python-core.md` and `201-python-lint-format.md`
</inputs_prereqs>

<mandatory>
`uv run pytest`; `uvx ruff` for lint/format; optional `pytest-cov` for coverage; `task` wrappers
</mandatory>

<forbidden>
Bare `pytest` (use `uv run pytest`), ad-hoc sleeps/timeouts without justification
</forbidden>

<steps>
1. Organize tests under `tests/` with clear naming: `test_*.py` and `Test*` classes (optional).
2. Use AAA (Arrange-Act-Assert); one behavior per test; prefer plain `assert`.
3. Model setup with fixtures; avoid `setUp`/`tearDown` from unittest; keep fixtures small and focused.
4. Parametrize inputs with `@pytest.mark.parametrize` instead of loops.
5. Isolate external effects (I/O, time, randomness, env vars, network) with `tmp_path`, `monkeypatch`, `capsys`, `freezegun`/`time` control, and mocks.
6. Categorize tests with markers (e.g., `unit`, `integration`, `slow`) and filter in CI.
7. Run via `uv run pytest`; ensure lints/format pass before completion.
</steps>

<output_format>
Focused diffs to test code; runnable examples for fixtures/parametrization; minimal CI commands.
</output_format>

<validation>
`uvx ruff check .` and `uvx ruff format --check .` pass; `uv run pytest` passes; optional coverage thresholds met.
</validation>

<design_principles>
- **Fast and deterministic:** Tests must be hermetic, avoiding hidden time or network dependencies.
- **Clear intent:** Descriptive test names; one assertion group per behavior; meaningful failure messages.
- **Fixtures over inheritance:** Prefer fixtures with appropriate scope; avoid deep fixture dependency chains.
- **Parametrize broadly:** Use parametrization to cover input spaces succinctly.
- **Isolate externalities:** Patch environment, clock, filesystem, and network.
- **Selective execution:** Use markers to include/exclude categories in different pipelines.
- **Visibility and diagnostics:** Capture logs and stdout/stderr when helpful; ensure `__repr__` of domain objects is informative (`205-python-classes.md`).
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Excessive Mocking That Tests Implementation Details

**Problem:** Mocking every dependency and internal function call, making tests tightly coupled to implementation rather than behavior.

**Why It Fails:** Tests break on any refactoring even when behavior is unchanged. Mocks don't catch integration bugs. Tests verify "code was called" not "feature works." False confidence from passing tests.

**Correct Pattern:**
```python
# BAD: Over-mocked test
def test_create_user(mocker):
    mocker.patch('app.services.user.validate_email')
    mocker.patch('app.services.user.hash_password')
    mocker.patch('app.services.user.db.insert')
    mocker.patch('app.services.user.send_email')
    result = create_user({"email": "test@example.com"})
    # Tests nothing about actual behavior

# GOOD: Test behavior with minimal mocking
def test_create_user(test_db, mock_email_service):
    # Only mock external services (email), use real DB
    result = create_user({"email": "test@example.com", "password": "secure123"})
    assert result.id is not None
    assert test_db.query(User).filter_by(email="test@example.com").first()
```

### Anti-Pattern 2: Flaky Tests With Time or Order Dependencies

**Problem:** Tests that pass or fail inconsistently due to reliance on system time, test execution order, or shared mutable state.

**Why It Fails:** Erodes trust in test suite. Developers ignore failures assuming "it's just flaky." Real bugs slip through. CI/CD becomes unreliable. Time wasted re-running tests.

**Correct Pattern:**
```python
# BAD: Time-dependent test
def test_token_expiry():
    token = create_token(expires_in=1)
    time.sleep(2)  # Flaky: sleep timing varies
    assert token.is_expired()

# GOOD: Use freezegun or explicit time control
from freezegun import freeze_time

def test_token_expiry():
    with freeze_time("2024-01-01 12:00:00"):
        token = create_token(expires_in=3600)
    with freeze_time("2024-01-01 13:00:01"):
        assert token.is_expired()
```

## Post-Execution Checklist
- [ ] **CRITICAL:** Pre-Task-Completion Test Execution Gate passed (all tests pass)
- [ ] **CRITICAL:** `uv run pytest` passed with all tests passing
- [ ] Tests run via `uv run pytest` (never bare pytest)
- [ ] Tests live under `tests/` and follow naming conventions
- [ ] Fixtures small, explicit, function-scoped by default; minimal autouse
- [ ] Parametrization used for input matrices; clear ids
- [ ] Isolation for time, randomness, env, FS, and network
- [ ] Markers defined and used for selection; CI filters slow/e2e
- [ ] Assertions clear; exceptions verified with `pytest.raises`
- [ ] Lints and formatting pass; optional coverage thresholds satisfied
- [ ] CHANGELOG.md and README.md updated as required

## Validation
- **Success Checks:** Pre-Task-Completion Test Execution Gate passed; `uv run pytest` passes with all tests passing; lint/format pass; deterministic behavior; meaningful failures; CHANGELOG.md and README.md updated as required.
- **Negative Tests:** Flaky tests; global state coupling; sleeps; live network; bare `pytest` usage; shared mutable fixtures; task completion attempted with failing tests is blocked.

> **Investigation Required**
> When applying this rule:
> 1. **Read existing test files BEFORE adding new tests** - Check current test patterns, fixture usage, and organization
> 2. **Run `uv run pytest` to verify tests pass** - Never assume tests work without running them
> 3. **Never speculate about test coverage** - Run `uv run pytest --cov` to check actual coverage
> 4. **Check conftest.py for existing fixtures** - Don't create duplicate fixtures
> 5. **Make grounded recommendations based on investigated test structure** - Don't suggest patterns that conflict with existing tests
>
> **Anti-Pattern:**
> "Based on typical pytest projects, you probably have these fixtures..."
> "Let me add this test - it should work with the existing setup..."
>
> **Correct Pattern:**
> "Let me check the existing test structure first."
> [reads tests/ directory and conftest.py]
> "I see you're using pytest fixtures for database setup in conftest.py. Here's a new test following the same pattern..."

## Output Format Examples
```bash
# Local run
uv run pytest -q

# With markers
uv run pytest -m "unit and not slow" -q

# With coverage
uv run pytest --cov=yourpkg --cov-report=term-missing
```

## References

### External Documentation
- [pytest Documentation](https://docs.pytest.org/) — Official docs
- [pytest Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [pytest Parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [pytest Marks](https://docs.pytest.org/en/stable/reference/reference.html#marks)
- [pytest Monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)
- [pytest tmp_path](https://docs.pytest.org/en/stable/how-to/tmp_path.html)
- [pytest capsys/caplog](https://docs.pytest.org/en/stable/how-to/capture-stdout-stderr.html)

### Related Rules
- **Python Core**: `rules/200-python-core.md`
- **Python Lint/Format**: `rules/201-python-lint-format.md`
- **Python Project Setup**: `rules/203-python-project-setup.md`
- **Python Docs & Comments**: `rules/204-python-docs-comments.md`
- **Python Classes**: `rules/205-python-classes.md`

## Pre-Task-Completion Test Execution Gate (CRITICAL)

**Reference:** Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**CRITICAL:** Test execution is MANDATORY before task completion. Tests are not optional.

### Mandatory Test Requirements
- **CRITICAL:** `uv run pytest` - All tests must pass before marking task complete
- **CRITICAL:** Never skip tests unless user explicitly requests override with acknowledged risks
- **CRITICAL:** Run tests immediately after code modifications, not in batches
- **Rule:** Do not mark tasks complete if ANY test fails
- **Rule:** Fix all test failures before responding to user
- **Exception:** Only skip with explicit user override (e.g., "skip tests") - acknowledge risks

### Test Execution Protocol
1. After any code modification, run `uv run pytest`
2. If tests fail, stop and report failures
3. Fix all failures
4. Re-run tests to confirm pass
5. Only then proceed to task completion

## 1. Test Layout & Naming
- Requirement: Place tests in a top-level `tests/` directory mirroring the source structure.
- Rule: Name files `test_<module>.py`; name tests `test_<behavior>` with descriptive intent.
- Consider: Group related tests in classes for shared fixtures, not for inheritance.

```python
# tests/test_math_ops.py
import pytest

def test_addition_basic():
    assert 1 + 2 == 3

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (-1, 1, 0),
    (0, 0, 0),
])
def test_addition_parametrized(a: int, b: int, expected: int) -> None:
    assert a + b == expected
```

## 2. Fixtures: Small, Focused, and Explicit
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

## 3. Parametrization over Loops
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

## 4. Isolation: Time, Randomness, I/O, and Network
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

## 5. Markers and Test Selection
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

## 6. Assertions & Error Handling
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

## 7. CLI, Logs, and Output Capture
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

## 8. Coverage and CI
- Consider: Use `pytest-cov` for coverage reporting with realistic thresholds.
- Rule: Avoid coverage gaming; focus on assertion quality and meaningful branches.

```bash
uv run pytest --maxfail=1 --disable-warnings -q
uv run pytest --cov=yourpkg --cov-report=term-missing
```
