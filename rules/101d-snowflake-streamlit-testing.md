# Streamlit Testing: AppTest and Debugging

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-12
**Keywords:** test Streamlit app, pytest, test framework, test patterns, app testing, UI testing, test automation, streamlit test suite, integration testing, test coverage, debug tests, test fixtures, testing strategies
**TokenBudget:** ~3750
**ContextTier:** High
**Depends:** 101-snowflake-streamlit-core.md, 206-python-pytest.md

## Scope

**What This Rule Covers:**
Comprehensive testing and debugging guidance for Streamlit applications using AppTest patterns (Streamlit 1.28+), unit testing strategies with pytest for data functions, mocking external services with unittest.mock, cache behavior testing, edge case coverage (empty, NULL, invalid), and debugging workflows targeting >80% test coverage without hitting production data.

**When to Load This Rule:**
- Writing automated tests for Streamlit apps
- Setting up unit tests for data processing functions
- Implementing UI/integration tests with AppTest
- Mocking database or API calls in tests
- Testing cache behavior (@st.cache_data validation)
- Debugging Streamlit applications
- Establishing test coverage standards (>80%)
- Setting up CI/CD test automation

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates
- **101-snowflake-streamlit-core.md** - Core Streamlit patterns
- **206-python-pytest.md** - Python testing with pytest

**Related:**
- **101b-snowflake-streamlit-performance.md** - Cache behavior testing
- **200-python-core.md** - Python testing fundamentals

### External Documentation

**Streamlit Testing:**
- [Streamlit App Testing](https://docs.streamlit.io/develop/api-reference/app-testing) - Official AppTest documentation
- [AppTest Tutorial](https://docs.streamlit.io/develop/concepts/app-testing) - Testing Streamlit apps guide

**Python Testing:**
- [pytest Documentation](https://docs.pytest.org/) - pytest testing framework
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) - Mock object library
- [pytest-cov](https://pytest-cov.readthedocs.io/) - Coverage plugin for pytest

## Contract

### Inputs and Prerequisites

Streamlit app configured (see 101-snowflake-streamlit-core.md), pytest installed, Streamlit 1.28+ for AppTest

### Mandatory

- **Coverage Target:** >80% code coverage with pytest-cov
- streamlit.testing.v1.AppTest, pytest, unittest, mock objects, debugger

### Forbidden

- Manual testing only (no automated tests)
- Testing without mocks for external services
- Tests that modify production data

### Execution Steps

1. Write unit tests for data processing functions using pytest
2. Use AppTest for UI/integration testing (Streamlit 1.28+)
3. Test cached functions to ensure proper cache invalidation
4. Test with various input combinations and edge cases
5. Mock external services (databases, APIs) in tests
6. Test error handling and edge cases

### Output Format

Test suite with unit tests for data functions, AppTest integration tests, >80% code coverage

### Validation

**Test Requirements:**
- All tests pass (uv run pytest)
- Edge cases covered (empty, NULL, invalid)
- Mocks used for external services
- Cache behavior tested

**Success Criteria:**
- Unit tests for all data processing functions
- AppTest integration tests for UI flows
- Test coverage >80%
- No tests hitting production data
- CI/CD integration working

**Coverage Target:** >80% code coverage with pytest-cov

### Design Principles

- **Test Data Functions:** Unit test all data processing logic
- **AppTest for UI:** Use Streamlit AppTest for UI/integration testing
- **Mock External Services:** Don't hit real databases/APIs in tests
- **Test Edge Cases:** Empty data, invalid inputs, error conditions
- **Cache Testing:** Verify cache behavior (hits, misses, invalidation)

### Post-Execution Checklist

- [ ] Unit tests for all data processing functions
- [ ] AppTest for UI/integration testing
- [ ] Mocks for database/API calls (no production data access)
- [ ] Edge cases covered (empty data, NULL, invalid inputs)
- [ ] Cache behavior tested (@st.cache_data validation)
- [ ] All tests pass: `uv run pytest`
- [ ] Test coverage >80%: `uv run pytest --cov`
- [ ] CI/CD pipeline configured to run tests

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: No automated tests**
```python
# Just manually clicking through the app
# No tests, no CI/CD validation
```
**Problem:** Regressions go undetected, manual testing is slow and error-prone

**Correct Pattern:**
```python
# test_app.py
def test_core_functionality():
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    assert not at.exception
    assert len(at.dataframe) > 0
```

**Anti-Pattern 2: Testing against production database**
```python
def test_load_data():
    # Hits real production database!
    df = load_data_from_prod()
    assert len(df) > 0
```
**Problem:** Slow tests, potential data corruption, cost

**Correct Pattern:**
```python
from unittest.mock import patch

def test_load_data():
    with patch('your_app.get_snowflake_session') as mock:
        mock_df = pd.DataFrame({'col1': [1, 2, 3]})
        mock.return_value.table.return_value.to_pandas.return_value = mock_df

        df = load_data()
        assert len(df) == 3
```

**Anti-Pattern 3: Not testing edge cases**
```python
def test_process_data():
    # Only tests happy path
    df = pd.DataFrame({'col1': [1, 2, 3]})
    result = process_data(df)
    assert result is not None
```
**Problem:** Fails on empty data, invalid inputs, error conditions

**Correct Pattern:**
```python
def test_process_data_empty():
    result = process_data(pd.DataFrame())
    assert result is not None

def test_process_data_invalid():
    df = pd.DataFrame({'wrong_col': [1, 2]})
    with pytest.raises(KeyError):
        process_data(df)
```

**Anti-Pattern 4: Not testing cache invalidation**
```python
def test_cache():
    result1 = load_cached_data()
    result2 = load_cached_data()
    # Assumes cache works but doesn't verify
```
**Problem:** Cache may not be working correctly, no validation

**Correct Pattern:**
```python
def test_cache_with_mock():
    with patch('db.query') as mock_query:
        mock_query.return_value = [1, 2, 3]

        # First call
        load_cached_data()
        assert mock_query.call_count == 1

        # Second call (should use cache)
        load_cached_data()
        assert mock_query.call_count == 1  # Still 1, cache hit
```

## Output Format Examples
```python
# test_app.py
import pytest
from streamlit.testing.v1 import AppTest
from unittest.mock import patch, MagicMock
import pandas as pd

# Unit tests for data functions
def test_normalize_columns():
    """Test Snowflake column normalization."""
    df = pd.DataFrame({'COL1': [1, 2], 'COL2': [3, 4]})
    result = normalize_columns(df)
    assert 'col1' in result.columns

def test_process_data_empty():
    """Test edge case: empty dataframe."""
    result = process_data(pd.DataFrame())
    assert result is not None

# AppTest integration tests
def test_app_loads():
    """Smoke test: app loads without errors."""
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    assert not at.exception

def test_user_workflow():
    """Test complete user interaction workflow."""
    at = AppTest.from_file("streamlit_app.py")
    at.run()

    # Simulate user actions
    at.text_input[0].set_value("test").run()
    at.button[0].click().run()

    # Verify results
    assert len(at.success) > 0

# Mock external services
@patch('your_app.get_snowflake_session')
def test_load_data(mock_session):
    """Test data loading with mocked database."""
    mock_df = pd.DataFrame({'col1': [1, 2, 3]})
    mock_session.return_value.table.return_value.to_pandas.return_value = mock_df

    result = load_data()
    assert len(result) == 3
```

## Unit Testing Data Functions

**MANDATORY:**
**Write unit tests for data processing functions using pytest:**

```python
# test_data.py
import pytest
import pandas as pd
from your_app import load_data, process_data, normalize_columns

def test_normalize_columns():
    """Test column name normalization from Snowflake."""
    df = pd.DataFrame({'COL1': [1, 2], 'COL2': [3, 4]})
    result = normalize_columns(df)

    assert 'col1' in result.columns
    assert 'col2' in result.columns
    assert 'COL1' not in result.columns

def test_process_data_empty_input():
    """Test graceful handling of empty dataframe."""
    empty_df = pd.DataFrame()
    result = process_data(empty_df)

    assert result is not None
    assert isinstance(result, pd.DataFrame)

def test_process_data_valid_input():
    """Test data processing with valid input."""
    df = pd.DataFrame({
        'date': ['2025-01-01', '2025-01-02'],
        'value': [100, 200]
    })
    result = process_data(df)

    assert len(result) == 2
    assert 'processed_value' in result.columns

@pytest.fixture
def sample_data():
    """Fixture providing sample test data."""
    return pd.DataFrame({
        'id': [1, 2, 3],
        'value': [10, 20, 30],
        'category': ['A', 'B', 'A']
    })

def test_aggregation(sample_data):
    """Test aggregation logic using fixture."""
    result = aggregate_by_category(sample_data)

    assert len(result) == 2  # Two categories
    assert result[result['category'] == 'A']['total'].iloc[0] == 40
```

## UI and Integration Testing with AppTest

**MANDATORY:**
**Use Streamlit AppTest (Streamlit 1.28+) for UI/integration testing:**

**Basic AppTest Examples:**
```python
# test_app.py
from streamlit.testing.v1 import AppTest

def test_app_loads():
    """Smoke test: verify app loads without errors."""
    at = AppTest.from_file("streamlit_app.py")
    at.run()
    assert not at.exception, f"App raised exception: {at.exception}"

def test_data_display():
    """Verify expected UI elements are present."""
    at = AppTest.from_file("streamlit_app.py")
    at.run()

    # Check for elements
    assert len(at.title) > 0, "No title rendered"
    assert len(at.dataframe) > 0, "No dataframes displayed"
    assert len(at.metric) >= 3, "Expected at least 3 metrics"

def test_user_interaction():
    """Test user interaction workflow."""
    at = AppTest.from_file("streamlit_app.py")
    at.run()

    # Simulate user input
    assert len(at.text_input) > 0, "No text inputs found"
    at.text_input[0].set_value("test query").run()

    # Click button
    assert len(at.button) > 0, "No buttons found"
    at.button[0].click().run()

    # Verify state change
    assert at.session_state.query_executed == True

def test_error_handling():
    """Verify graceful error handling."""
    at = AppTest.from_file("streamlit_app.py")
    at.run()

    # Trigger error condition
    at.text_input[0].set_value("").run()  # Empty input
    at.button[0].click().run()

    # Check error message displayed
    assert len(at.error) > 0, "No error message shown"
    assert "required" in str(at.error[0]).lower()

def test_navigation():
    """Test multipage navigation."""
    at = AppTest.from_file("streamlit_app.py")
    at.run()

    # Navigate to different page
    at.sidebar.selectbox[0].set_value("Dashboard").run()

    # Verify page content changed
    assert "Dashboard" in str(at.title[0])
```

**Advanced AppTest Patterns:**
```python
def test_form_submission():
    """Test form submission workflow."""
    at = AppTest.from_file("streamlit_app.py")
    at.run()

    # Fill form fields
    at.text_input("username").set_value("testuser").run()
    at.text_input("email").set_value("test@example.com").run()

    # Submit form
    at.button("Submit").click().run()

    # Verify success message
    assert len(at.success) > 0
    assert "submitted" in str(at.success[0]).lower()

def test_caching():
    """Test cache behavior."""
    at = AppTest.from_file("streamlit_app.py")

    # First run - cache miss
    at.run()
    initial_load_time = at.session_state.get('load_time', 0)

    # Second run - cache hit (should be faster)
    at.run()
    cached_load_time = at.session_state.get('load_time', 0)

    assert cached_load_time < initial_load_time or cached_load_time == 0
```

## Testing Cached Functions

**MANDATORY:**
**Test cached functions to ensure proper cache invalidation:**

```python
import streamlit as st
from unittest.mock import patch, MagicMock

def test_cache_data_behavior():
    """Test @st.cache_data behavior."""
    with patch('your_app.get_snowflake_session') as mock_session:
        mock_df = pd.DataFrame({'col1': [1, 2, 3]})
        mock_session.return_value.table.return_value.to_pandas.return_value = mock_df

        # First call - should hit database
        result1 = load_data()
        assert mock_session.called

        # Second call within ttl - should use cache
        mock_session.reset_mock()
        result2 = load_data()
        assert not mock_session.called  # Cache hit

        # Verify results identical
        pd.testing.assert_frame_equal(result1, result2)

def test_cache_resource_behavior():
    """Test @st.cache_resource for connections."""
    with patch('your_app.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.builder.configs.return_value.create.return_value = mock_session

        # First call - creates connection
        conn1 = get_snowflake_session()
        assert mock_session_class.called

        # Second call - reuses connection
        mock_session_class.reset_mock()
        conn2 = get_snowflake_session()
        assert not mock_session_class.called  # Cache hit

        # Verify same connection object
        assert conn1 is conn2
```

## Common Debugging Issues

### App Crashes or Freezes
- **Avoid:** Infinite loops in widget callbacks
- **Always:** Use @st.cache_data to prevent redundant data loading
- **Check:** Blocking operations without feedback (add st.spinner)

### Slow Performance
- **Profile:** Use `st.write(st.query_params)` to check rerun frequency (Streamlit 1.30+)
- **Optimize:** Expensive operations with proper caching
- **Consider:** Lazy loading for large datasets, sampling for development/testing

### Widget State Issues
- **Always:** Initialize all session state variables explicitly
- **Use:** Widget keys for stable identity across reruns
- **Avoid:** Overwriting session state in widget callbacks

```python
# [PASS] Correct state management
if 'counter' not in st.session_state:
    st.session_state.counter = 0

def increment():
    st.session_state.counter += 1

st.button("Increment", on_click=increment)
st.write(f"Count: {st.session_state.counter}")
```

### Memory Issues
- **Clear:** Large cached objects when no longer needed
- **Limit:** Conversation history and data in session state
- **Use:** Pagination for large result sets

### Column Name KeyErrors
- **Critical:** Remember Snowflake returns UPPERCASE column names
- **Always:** Normalize to lowercase in data loaders
- **Reference:** See 101b-snowflake-streamlit-performance.md

## Manual Testing Checklist

**RECOMMENDED:**
**Manual Testing Before Deployment:**
- [ ] App loads in <2s with production-like data volume
- [ ] All navigation paths functional (sidebar, buttons, links)
- [ ] Error states show user-friendly messages (not stack traces)
- [ ] Responsive layout works on mobile (DevTools device emulation)
- [ ] Charts are interactive (zoom, pan, hover tooltips)
- [ ] Session state persists across page changes
- [ ] Caching works correctly (@st.cache_data/@st.cache_resource)
- [ ] Form validation provides clear feedback
- [ ] Loading states show progress indicators
- [ ] Secrets load correctly from st.secrets
