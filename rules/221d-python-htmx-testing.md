# HTMX Testing Patterns

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** testing, pytest, unit tests, integration tests, fixtures, mocking, header validation, html assertions, test client, htmx testing
**TokenBudget:** ~2400
**ContextTier:** High
**Depends:** rules/221-python-htmx-core.md, rules/206-python-pytest.md

## Purpose

Defines testing strategies for HTMX endpoints in Python applications, covering unit tests for header validation, integration tests for partial responses, pytest fixtures for HTMX requests, HTML assertion patterns, and mocking strategies.

## Rule Scope

Python web applications (Flask, FastAPI, Django) with HTMX integration requiring comprehensive test coverage

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Test with HX-Request header** - Always include `HX-Request: true` for HTMX tests
- **Assert response headers** - Validate `HX-Trigger`, `HX-Redirect`, `HX-Retarget`, etc.
- **Validate HTML structure** - Use BeautifulSoup or lxml to assert partial HTML content
- **Create HTMX fixtures** - Reusable pytest fixtures for HTMX request headers
- **Test both request types** - Verify endpoint behavior with and without HTMX headers
- **Mock external dependencies** - Isolate HTMX logic from database/API calls

**Pre-Execution Checklist:**
- [ ] Pytest installed with test client (Flask test_client, FastAPI TestClient)
- [ ] HTMX request fixtures created
- [ ] HTML parsing library installed (BeautifulSoup4 or lxml)
- [ ] Unit tests for header detection logic
- [ ] Integration tests for partial vs. full-page responses
- [ ] Tests cover success and error cases
- [ ] Mocking strategy defined for external dependencies

## Contract

<inputs_prereqs>
Pytest framework; Flask test_client or FastAPI TestClient; HTML parsing library (BeautifulSoup4/lxml); HTMX core patterns (221-python-htmx-core.md); pytest best practices (206-python-pytest.md)
</inputs_prereqs>

<mandatory>
Pytest; test client; HTMX request fixtures; HTML assertion utilities; mocking library (pytest-mock or unittest.mock); test database/fixtures
</mandatory>

<forbidden>
Testing without HX-Request header; skipping HTML structure validation; not testing error cases; missing header assertions; testing only happy path; relying on visual inspection instead of assertions
</forbidden>

<steps>
1. Install pytest and test dependencies (BeautifulSoup4, pytest-mock)
2. Create pytest fixtures for test client and HTMX headers
3. Write unit tests for HTMX detection logic
4. Write integration tests for endpoints (with/without HX-Request)
5. Add HTML assertion helpers for partial validation
6. Test response headers (HX-Trigger, HX-Redirect, etc.)
7. Mock external dependencies (database, APIs)
8. Run tests with coverage reporting
</steps>

<output_format>
Pytest test suite with fixtures, unit tests, integration tests, HTML assertions, header validations, and mocking
</output_format>

<validation>
- All HTMX endpoints have test coverage (with and without HX-Request)
- Response headers validated (HX-Trigger, HX-Redirect, etc.)
- HTML structure assertions pass for partials
- Error cases tested (400, 401, 404, 500)
- Mocking isolates HTMX logic from dependencies
- Test coverage >80% for HTMX routes
</validation>

## Key Principles

### 1. Pytest Fixtures for HTMX

**Flask Test Client Fixtures:**
```python
import pytest
from app import create_app

@pytest.fixture
def app():
    app = create_app({'TESTING': True})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def htmx_headers():
    """Standard HTMX request headers"""
    return {
        'HX-Request': 'true',
        'HX-Current-URL': 'http://localhost/test'
    }

@pytest.fixture
def htmx_client(client, htmx_headers):
    """Test client with HTMX headers pre-configured"""
    class HTMXClient:
        def get(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(htmx_headers)
            return client.get(*args, **kwargs)

        def post(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(htmx_headers)
            return client.post(*args, **kwargs)

        def put(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(htmx_headers)
            return client.put(*args, **kwargs)

        def delete(self, *args, **kwargs):
            kwargs.setdefault('headers', {}).update(htmx_headers)
            return client.delete(*args, **kwargs)

    return HTMXClient()
```

**FastAPI Test Client Fixtures:**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def htmx_headers():
    return {
        'HX-Request': 'true',
        'HX-Current-URL': 'http://localhost/test'
    }

@pytest.fixture
def htmx_client(client, htmx_headers):
    """TestClient wrapper with HTMX headers"""
    class HTMXTestClient:
        def __init__(self, client, headers):
            self.client = client
            self.headers = headers

        def get(self, url, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return self.client.get(url, **kwargs)

        def post(self, url, **kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return self.client.post(url, **kwargs)

        # ... put, delete, etc.

    return HTMXTestClient(client, htmx_headers)
```

### 2. Unit Tests for HTMX Detection

**Testing Detection Logic:**
```python
def test_htmx_detection_with_header(client, htmx_headers):
    """Test endpoint detects HTMX request"""
    response = client.get('/users', headers=htmx_headers)

    assert response.status_code == 200
    # Should return partial, not full page
    assert '<html>' not in response.data.decode()
    assert '<table' in response.data.decode()

def test_htmx_detection_without_header(client):
    """Test endpoint returns full page without HTMX header"""
    response = client.get('/users')

    assert response.status_code == 200
    # Should return full page
    assert '<html>' in response.data.decode()
    assert '<table' in response.data.decode()

def test_htmx_only_endpoint_rejects_non_htmx(client):
    """Test HTMX-only endpoint rejects regular requests"""
    response = client.get('/htmx/users/search')

    assert response.status_code == 400
```

### 3. HTML Assertion Helpers

**BeautifulSoup Helpers:**
```python
from bs4 import BeautifulSoup

def parse_html(response_data):
    """Parse response HTML with BeautifulSoup"""
    return BeautifulSoup(response_data, 'html.parser')

def test_user_row_structure(htmx_client):
    """Test partial HTML structure"""
    response = htmx_client.get('/users/1')
    soup = parse_html(response.data)

    # Assert structure
    tr = soup.find('tr', id='user-1')
    assert tr is not None
    assert tr.find('td', text='John Doe') is not None

    # Assert HTMX attributes present
    edit_button = tr.find('button', attrs={'hx-get': '/users/1/edit'})
    assert edit_button is not None
    assert edit_button['hx-target'] == '#user-1'

def test_table_has_rows(htmx_client):
    """Test table contains expected rows"""
    response = htmx_client.get('/users')
    soup = parse_html(response.data)

    rows = soup.find_all('tr', id=lambda x: x and x.startswith('user-'))
    assert len(rows) == 3  # Expected number of users
```

**Custom Assertion Functions:**
```python
def assert_htmx_attributes(element, expected_attrs):
    """Assert HTMX attributes on element"""
    for attr, value in expected_attrs.items():
        assert element.get(attr) == value, \
            f"Expected {attr}={value}, got {element.get(attr)}"

def assert_element_count(soup, selector, expected_count):
    """Assert number of elements matching selector"""
    elements = soup.select(selector)
    assert len(elements) == expected_count, \
        f"Expected {expected_count} elements, found {len(elements)}"

# Usage
def test_user_buttons(htmx_client):
    response = htmx_client.get('/users/1')
    soup = parse_html(response.data)

    edit_btn = soup.find('button', attrs={'hx-get': '/users/1/edit'})
    assert_htmx_attributes(edit_btn, {
        'hx-get': '/users/1/edit',
        'hx-target': '#user-1',
        'hx-swap': 'outerHTML'
    })
```

### 4. Response Header Assertions

**Testing HTMX Response Headers:**
```python
def test_delete_triggers_event(htmx_client):
    """Test DELETE returns HX-Trigger header"""
    response = htmx_client.delete('/users/1')

    assert response.status_code == 200
    assert response.headers.get('HX-Trigger') == 'userDeleted'

def test_unauthorized_redirects(htmx_client):
    """Test unauthorized request returns HX-Redirect"""
    response = htmx_client.get('/protected')

    assert response.status_code == 401
    assert response.headers.get('HX-Redirect') == '/login'

def test_error_retargets(htmx_client):
    """Test error response retargets to error container"""
    response = htmx_client.post('/users', data={'name': ''})

    assert response.status_code == 400
    assert response.headers.get('HX-Retarget') == '#error-container'

def test_multiple_triggers(htmx_client):
    """Test multiple events in HX-Trigger header"""
    response = htmx_client.post('/cart/add/1')

    assert response.status_code == 200
    trigger_header = response.headers.get('HX-Trigger')
    # HX-Trigger can contain multiple events: {"event1": {}, "event2": {}}
    assert 'cartUpdated' in trigger_header
    assert 'itemAdded' in trigger_header
```

### 5. Integration Tests

**Full Request/Response Cycle:**
```python
def test_user_crud_workflow(client, htmx_client, db):
    """Test complete CRUD workflow with HTMX"""
    # Create user
    response = htmx_client.post('/users', data={
        'name': 'Jane Doe',
        'email': 'jane@example.com'
    })
    assert response.status_code == 200
    soup = parse_html(response.data)
    user_id = soup.find('tr')['id'].replace('user-', '')

    # Read user
    response = htmx_client.get(f'/users/{user_id}')
    assert response.status_code == 200
    assert 'Jane Doe' in response.data.decode()

    # Update user
    response = htmx_client.put(f'/users/{user_id}', data={
        'name': 'Jane Smith'
    })
    assert response.status_code == 200
    assert 'Jane Smith' in response.data.decode()
    assert response.headers.get('HX-Trigger') == 'userUpdated'

    # Delete user
    response = htmx_client.delete(f'/users/{user_id}')
    assert response.status_code == 200
    assert response.headers.get('HX-Trigger') == 'userDeleted'
```

**Form Validation Testing:**
```python
def test_form_validation_errors(htmx_client):
    """Test form returns validation errors"""
    response = htmx_client.post('/users', data={
        'name': '',  # Invalid: empty
        'email': 'not-an-email'  # Invalid: bad format
    })

    assert response.status_code == 400
    soup = parse_html(response.data)

    # Check error messages present
    name_error = soup.find('span', class_='error', text=lambda t: 'name' in t.lower())
    assert name_error is not None

    email_error = soup.find('span', class_='error', text=lambda t: 'email' in t.lower())
    assert email_error is not None
```

### 6. Mocking External Dependencies

**Mocking Database Calls:**
```python
from unittest.mock import patch, MagicMock

def test_users_list_with_mock(htmx_client, mocker):
    """Test users endpoint with mocked database"""
    # Mock get_users function
    mock_users = [
        {'id': 1, 'name': 'User 1', 'email': 'user1@example.com'},
        {'id': 2, 'name': 'User 2', 'email': 'user2@example.com'}
    ]
    mocker.patch('app.routes.get_users', return_value=mock_users)

    response = htmx_client.get('/users')

    assert response.status_code == 200
    soup = parse_html(response.data)
    rows = soup.find_all('tr', id=lambda x: x and x.startswith('user-'))
    assert len(rows) == 2
```

**Mocking External APIs:**
```python
def test_weather_endpoint_with_mock(htmx_client, mocker):
    """Test weather endpoint with mocked API"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'temp': 72,
        'condition': 'Sunny'
    }

    mocker.patch('httpx.AsyncClient.get', return_value=mock_response)

    response = htmx_client.get('/weather/seattle')

    assert response.status_code == 200
    assert '72' in response.data.decode()
    assert 'Sunny' in response.data.decode()
```

### 7. Parameterized Tests

**Testing Multiple Scenarios:**
```python
import pytest

@pytest.mark.parametrize('endpoint,expected_status', [
    ('/users', 200),
    ('/users/1', 200),
    ('/users/999', 404),
    ('/users/-1', 404)
])
def test_endpoint_status_codes(htmx_client, endpoint, expected_status):
    """Test various endpoints return correct status codes"""
    response = htmx_client.get(endpoint)
    assert response.status_code == expected_status

@pytest.mark.parametrize('method,endpoint,data,expected_trigger', [
    ('POST', '/users', {'name': 'Test'}, 'userCreated'),
    ('PUT', '/users/1', {'name': 'Updated'}, 'userUpdated'),
    ('DELETE', '/users/1', None, 'userDeleted')
])
def test_crud_triggers(htmx_client, method, endpoint, data, expected_trigger):
    """Test CRUD operations return correct HX-Trigger"""
    if method == 'POST':
        response = htmx_client.post(endpoint, data=data)
    elif method == 'PUT':
        response = htmx_client.put(endpoint, data=data)
    elif method == 'DELETE':
        response = htmx_client.delete(endpoint)

    assert response.headers.get('HX-Trigger') == expected_trigger
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Testing Only HTMX Requests

**Problem:** Only testing HTMX requests, ignoring non-HTMX full-page responses.

**Why It Fails:** Misses bugs in full-page rendering; incomplete test coverage.

**Correct Pattern:**
```python
def test_users_htmx(htmx_client):
    response = htmx_client.get('/users')
    assert '<html>' not in response.data.decode()  # Partial

def test_users_full_page(client):
    response = client.get('/users')
    assert '<html>' in response.data.decode()  # Full page
```

### Anti-Pattern 2: No HTML Structure Validation

**Problem:** Only checking status codes without validating HTML content.

**Why It Fails:** Passes even when HTML structure is broken; misses UI bugs.

**Correct Pattern:**
```python
def test_user_row(htmx_client):
    response = htmx_client.get('/users/1')
    soup = parse_html(response.data)
    tr = soup.find('tr', id='user-1')
    assert tr is not None
    assert tr.find('td', text='John Doe') is not None
```

## Post-Execution Checklist

- [ ] Pytest fixtures created for HTMX requests
- [ ] Unit tests validate HTMX detection logic
- [ ] Integration tests cover full request/response cycle
- [ ] HTML assertions validate partial structure
- [ ] Response header assertions check HX-* headers
- [ ] Error cases tested (400, 401, 404, 500)
- [ ] External dependencies mocked appropriately
- [ ] Parameterized tests reduce duplication
- [ ] Test coverage >80% for HTMX routes
- [ ] All tests pass consistently

## Validation

**Success Checks:**
- All HTMX endpoints have tests with `HX-Request` header
- Response headers validated (HX-Trigger, HX-Redirect, etc.)
- HTML structure assertions pass
- Error responses tested and validated
- Mocking isolates HTMX logic
- Coverage report shows >80% for HTMX routes

**Negative Tests:**
- HTMX-only endpoint rejects non-HTMX requests (400)
- Invalid input returns 400 with error HTML
- Unauthorized request returns 401 with HX-Redirect
- Missing resource returns 404

## Output Format Examples

### Complete Test Suite Structure

Directory structure for `tests/`:
- `conftest.py` - Fixtures (client, htmx_headers, htmx_client)
- `test_htmx_detection.py` - Unit tests for detection logic
- `test_users_htmx.py` - Integration tests for /users routes
- `test_forms_htmx.py` - Form validation tests
- `test_headers_htmx.py` - Response header tests
- **utils/** - `html_helpers.py` (HTML assertion utilities)

### Example Test File

```python
# tests/test_users_htmx.py
import pytest
from bs4 import BeautifulSoup

def parse_html(response_data):
    return BeautifulSoup(response_data, 'html.parser')

def test_users_list_htmx(htmx_client):
    """Test users list returns partial HTML for HTMX request"""
    response = htmx_client.get('/users')
    
    assert response.status_code == 200
    assert '<html>' not in response.data.decode()
    
    soup = parse_html(response.data)
    rows = soup.find_all('tr', id=lambda x: x and x.startswith('user-'))
    assert len(rows) > 0

def test_users_list_full_page(client):
    """Test users list returns full page for regular request"""
    response = client.get('/users')
    
    assert response.status_code == 200
    assert '<html>' in response.data.decode()
```

## References

### External Documentation
- [Pytest Documentation](https://docs.pytest.org/) - Official pytest guide
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/) - Flask test client
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/) - TestClient usage
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML parsing

### Related Rules
- **HTMX Foundation**: `rules/221-python-htmx-core.md` - HTMX patterns to test
- **Python Testing**: `rules/206-python-pytest.md` - Pytest best practices
- **Flask Integration**: `rules/221b-python-htmx-flask.md` - Flask-specific testing
- **FastAPI Integration**: `rules/221c-python-htmx-fastapi.md` - FastAPI-specific testing
- **Python Core**: `rules/200-python-core.md` - Python standards
