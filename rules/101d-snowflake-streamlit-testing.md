# Streamlit Testing: AppTest and Debugging

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** test Streamlit app, pytest, test framework, test patterns, app testing, UI testing, test automation, streamlit test suite, integration testing, test coverage, debug tests, test fixtures, testing strategies
**TokenBudget:** ~2600
**ContextTier:** High
**Depends:** rules/101-snowflake-streamlit-core.md, rules/206-python-pytest.md

## Purpose
Provide comprehensive testing and debugging guidance for Streamlit applications including AppTest patterns, unit testing strategies, debugging workflows, and common issue resolution.

## Rule Scope

Streamlit testing with AppTest, unit testing data functions, debugging patterns

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Unit test data functions:** Use `pytest` for all data processing logic
- **AppTest for UI testing:** Use `streamlit.testing.v1.AppTest` for UI/integration tests (Streamlit 1.28+)
- **Mock external services:** Use `unittest.mock` to avoid hitting real databases/APIs
- **Test edge cases:** Empty data, invalid inputs, NULL/NaN values, error conditions
- **Test cache behavior:** Verify `@st.cache_data` hits, misses, and invalidation
- **Target >80% coverage:** Use `pytest-cov` to measure test coverage
- **Never test against production data** - always use mocks or test databases

**Quick Checklist:**
- [ ] Unit tests for all data processing functions
- [ ] AppTest for UI/integration testing
- [ ] Mocks for database/API calls
- [ ] Edge cases covered (empty, NULL, invalid)
- [ ] Cache behavior tested
- [ ] All tests pass: `uv run pytest`
- [ ] Coverage >80%: `uv run pytest --cov`

## Contract

<contract>
<inputs_prereqs>
Streamlit app configured (see 101-snowflake-streamlit-core.md), pytest installed, Streamlit 1.28+ for AppTest
</inputs_prereqs>

<mandatory>
streamlit.testing.v1.AppTest, pytest, unittest, mock objects, debugger
</mandatory>

<forbidden>
Manual testing only (no automated tests), testing without mocks for external services, tests that modify production data
</forbidden>

<steps>
1. Write unit tests for data processing functions using pytest
2. Use AppTest for UI/integration testing (Streamlit 1.28+)
3. Test cached functions to ensure proper cache invalidation
4. Test with various input combinations and edge cases
5. Mock external services (databases, APIs) in tests
6. Test error handling and edge cases
</steps>

<output_format>
Test suite with unit tests for data functions, AppTest integration tests, >80% code coverage
</output_format>

<validation>
All tests pass, edge cases covered, mocks used for external services, cache behavior tested
</validation>

<design_principles>
- **Test Data Functions:** Unit test all data processing logic
- **AppTest for UI:** Use Streamlit AppTest for UI/integration testing
- **Mock External Services:** Don't hit real databases/APIs in tests
- **Test Edge Cases:** Empty data, invalid inputs, error conditions
- **Cache Testing:** Verify cache behavior (hits, misses, invalidation)
</design_principles>

</contract>

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

## Post-Execution Checklist
- [ ] Unit tests for all data processing functions
- [ ] AppTest integration tests for core UI workflows
- [ ] Mock objects used for external services (databases, APIs)
- [ ] Edge cases tested (empty data, invalid inputs, errors)
- [ ] Cache behavior tested (hits, misses, invalidation)
- [ ] Test coverage >80% for data processing logic
- [ ] All tests pass in CI/CD pipeline
- [ ] Manual testing checklist completed before deployment

## Validation
- **Success Checks:** All tests pass, edge cases covered, cache behavior verified, mocks used correctly, AppTest integration tests validate UI workflows
- **Negative Tests:** Introduce bugs (should fail tests), break cache (tests should catch it), test with invalid inputs (should handle gracefully)

> **Investigation Required**
> When applying this rule:
> 1. Read test files BEFORE making recommendations
> 2. Verify pytest and AppTest are installed and configured
> 3. Check if tests use mocks for external services
> 4. Never speculate about test coverage - inspect actual test files
> 5. Verify cache testing patterns if caching is used
> 6. Check if edge cases are covered in tests

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

## References

### External Documentation

**Streamlit Testing:**
- [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing) - Official AppTest documentation
- [Testing Apps Tutorial](https://docs.streamlit.io/develop/concepts/app-testing) - Complete guide to testing Streamlit apps
- [App Testing Release Notes](https://docs.streamlit.io/develop/quick-reference/release-notes#version-1280) - AppTest introduced in 1.28.0

**Python Testing:**
- [pytest Documentation](https://docs.pytest.org/) - pytest testing framework
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html) - Python mock objects for testing
- [pytest-cov](https://pytest-cov.readthedocs.io/) - Coverage reporting for pytest

**Debugging:**
- [Streamlit Debugging](https://docs.streamlit.io/develop/concepts/app-design/app-debugging) - Official debugging guide
- [Performance Profiling](https://docs.streamlit.io/develop/concepts/architecture/caching#debugging-cache-issues) - Cache debugging

### Related Rules
- **Streamlit Core**: `rules/101-snowflake-streamlit-core.md`
- **Streamlit Performance**: `rules/101b-snowflake-streamlit-performance.md` (cache testing)
- **Python pytest**: `rules/206-python-pytest.md`
- **Python Core**: `rules/200-python-core.md`

> **[AI] Claude 4 Specific Guidance**
> **Claude 4 Streamlit Testing Optimizations:**
> - Parallel test analysis: Can review multiple test files simultaneously for coverage gaps
> - Context awareness: Track test patterns and mock usage across test suite
> - Investigation-first: Excel at discovering missing tests and untested edge cases
> - Pattern recognition: Quickly identify test anti-patterns (no mocks, missing edge cases)

## 1. Unit Testing Data Functions

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

## 2. UI and Integration Testing with AppTest

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

## 3. Testing Cached Functions

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

## 4. Common Debugging Issues

### App Crashes or Freezes
- **Avoid:** Infinite loops in widget callbacks
- **Always:** Use @st.cache_data to prevent redundant data loading
- **Check:** Blocking operations without feedback (add st.spinner)

### Slow Performance
- **Profile:** Use `st.write(st.experimental_get_query_params())` to check rerun frequency
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

## 5. Manual Testing Checklist

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
