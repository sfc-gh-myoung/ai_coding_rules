# 001-complete-test-rule

## Metadata

**Keywords:** test, validation, complete, example, fixture, schema-v3, comprehensive, testing, verification, sample
**TokenBudget:** ~1200
**ContextTier:** High
**Depends:** rules/000-global-core.md

## Purpose

A complete rule file with all required sections and metadata for testing schema v3.0 validation.

## Rule Scope

Testing and validation scenarios for schema validator.

## Quick Start TL;DR

**MANDATORY:**

**Essential Patterns:**
- **Validate inputs:** Always check test prerequisites before execution
- **Use proper isolation:** Ensure tests don't interfere with each other
- **Document intent:** Clear test descriptions for maintainability
- **Verify outputs:** Check all assertions pass with meaningful messages

**Pre-Execution Checklist:**
- [ ] Test environment is properly configured
- [ ] All dependencies are installed
- [ ] Test data fixtures are available
- [ ] Previous tests have been cleaned up
- [ ] Test isolation is verified

## Contract

<inputs_prereqs>
- Test environment with pytest installed
- Access to test fixtures directory
- Clean test database or mock objects
</inputs_prereqs>

<mandatory>
- pytest for test execution
- coverage.py for code coverage
- Test fixtures and mocks
</mandatory>

<forbidden>
- Production databases
- Real API credentials
- Unverified external dependencies
</forbidden>

<steps>
1. Set up test environment and fixtures
2. Execute test suite with isolation
3. Verify all assertions pass
4. Check code coverage meets threshold
5. Clean up test resources
6. Document test results
</steps>

<output_format>
Test results in pytest format with coverage report
</output_format>

<validation>
- All tests pass without errors
- Code coverage exceeds 80%
- No test interference detected
- Cleanup verified successful
</validation>

## Key Principles

- **Test isolation:** Each test should run independently
- **Clear assertions:** Use descriptive assertion messages
- **Comprehensive coverage:** Test both success and failure paths
- **Documentation:** Explain what and why for each test

## Anti-Patterns and Common Mistakes

**Problem:** Tests that depend on execution order

```python
def test_first():
    global state
    state = "initialized"

def test_second():
    assert state == "initialized"  # Fails if test_first doesn't run first
```

**Why It Fails:** Test order is not guaranteed; creates fragile test suite.

**Correct Pattern:** Use fixtures for shared state

```python
@pytest.fixture
def initialized_state():
    return "initialized"

def test_with_fixture(initialized_state):
    assert initialized_state == "initialized"  # Works independently
```

## Post-Execution Checklist

- [ ] All test cases executed successfully
- [ ] Code coverage report generated and reviewed
- [ ] No test isolation issues detected
- [ ] Test cleanup completed properly
- [ ] Test results documented
- [ ] Edge cases and error handling verified

## Validation

**Success Checks:**
- All tests pass: `pytest tests/ --tb=short`
- Coverage threshold met: `pytest --cov=src --cov-report=term-missing`
- No warnings or deprecations in test output

**Negative Tests:**
- Error handling: Tests with invalid inputs fail gracefully
- Edge cases: Boundary conditions properly handled
- Cleanup verification: Resources properly released after test failures

## Output Format Examples

```bash
# Run full test suite
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Expected output format
============================= test session starts ==============================
collected 25 items

tests/test_module.py::test_example PASSED                                [ 4%]
tests/test_module.py::test_edge_case PASSED                              [ 8%]
...
========================= 25 passed in 2.45s ================================

Coverage report:
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
src/module.py           45      2    96%   23-24
--------------------------------------------------
TOTAL                   45      2    96%
```

## References

### External Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Guide](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://testing.googleblog.com/)

### Related Rules
- `000-global-core.md` - Core principles
- `206-python-pytest.md` - pytest-specific guidance
