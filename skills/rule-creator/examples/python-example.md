# Example: Python Library Rule Creation (pytest-mock)

## User Request

```
Create a new Cursor rule documenting pytest-mock best practices following schema
```

## Abbreviated Workflow (Key Steps Only)

### Phase 1: Discovery (5 min)

**Search RULES_INDEX.md:**
```bash
$ grep -i "pytest\|mock\|python.*test" RULES_INDEX.md
|| `200-python-core.md` | Python foundations | ...
|| `206-python-pytest.md` | pytest usage | ...

# Analysis:
Domain: 200-299 (Python)
Similar: 206 (pytest)
Next available: 209
```

**Research findings:**
- pytest-mock simplifies unittest.mock for pytest
- mocker fixture preferred over unittest.mock.patch
- spy() for verifying calls without replacing
- Integration with pytest fixtures

**Keywords (13):**
```
pytest-mock, mocking, testing, fixtures, mocker, spy, patch, unittest.mock,
test doubles, test isolation, Python testing, pytest plugins, mock verification
```

---

### Phase 2: Template Generation (1 min)

```bash
$ python scripts/template_generator.py 209-python-pytest-mock \
    --context-tier Medium \
    --output-dir rules/

 Created rule template: rules/209-python-pytest-mock.md
```

---

### Phase 3: Content Population (8 min)

**Metadata:**
```markdown
**Keywords:** pytest-mock, mocking, testing, fixtures, mocker, spy, patch, unittest.mock, test doubles, test isolation, Python testing, pytest plugins, mock verification
**TokenBudget:** ~1000
**ContextTier:** Medium
**Depends:** rules/000-global-core.md, rules/200-python-core.md, rules/206-python-pytest.md
```

**Essential Patterns:**
```markdown
- **mocker fixture preferred:** Use mocker.patch() instead of unittest.mock.patch as decorator
- **spy for verification:** Use mocker.spy() to verify calls without replacing implementation
- **Integration with fixtures:** Combine mocker with pytest fixtures for clean test setup
- **mock_return_value pattern:** Use return_value for simple mocks, side_effect for complex behavior
```

**Sample Anti-Pattern:**
```markdown
### Anti-Pattern 1: Using unittest.mock Directly

**Problem:** Importing and using unittest.mock.patch() in pytest tests instead of mocker fixture

```python
# Wrong: unittest.mock in pytest
from unittest.mock import patch

@patch('module.function')
def test_something(mock_func):
    mock_func.return_value = 42
    assert module.function() == 42
```

**Why It Fails:**
- Doesn't integrate with pytest fixtures
- Cleanup not automatic (may leak state)
- Less Pythonic in pytest context

**Correct Pattern:**
```python
# Right: Use mocker fixture
def test_something(mocker):
    mock_func = mocker.patch('module.function', return_value=42)
    assert module.function() == 42
    mock_func.assert_called_once()
```

**Benefits:**
- Automatic cleanup via pytest fixture
- Better integration with pytest ecosystem
- More readable and consistent
```

---

### Phase 4: Validation (2 min, 1 iteration)

```bash
$ python scripts/schema_validator.py rules/209-python-pytest-mock.md

SUMMARY:
   CRITICAL: 0
    HIGH: 0
  ℹ️  MEDIUM: 0
   Passed: 458 checks

RESULT:  PASSED (exit code 0)
```

 Passed on first try!

---

### Phase 5: Indexing (1 min)

**Entry:**
```markdown
| 209-python-pytest-mock | pytest-mock library patterns for test doubles and mocking | pytest-mock, mocking, testing, fixtures, mocker, spy, patch | rules/200-python-core.md, rules/206-python-pytest.md |
```

**Inserted after:**
```bash
|| `206-python-pytest.md` | ...
|| `209-python-pytest-mock.md` | ... [NEW]
|| `210-python-fastapi-core.md` | ...
```

 Indexed successfully

---

## Final Output

```
 Production-ready rule created: rules/209-python-pytest-mock.md

Statistics:
- Total time: ~17 minutes
- Validation iterations: 1 (passed first time)
- Size: ~15KB, ~380 lines
- TokenBudget: ~1000 tokens

Ready for use: rules/209-python-pytest-mock.md
```

## Key Differences from Frontend Example

**Domain:** Python (200-299) vs JavaScript (420-449)
**Dependencies:** More complex - depends on both 200-python-core AND 206-python-pytest
**Keywords:** More technical (mocking, fixtures) vs design-focused (themes, components)
**Validation:** Passed on first iteration (Frontend took 2)

**Success factors:**
- Clear domain (Python testing)
- Well-established library (pytest-mock)
- Followed existing patterns from 206-python-pytest.md
- Accurate keyword count from start

