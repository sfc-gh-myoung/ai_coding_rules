# HTMX Testing Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-03-09
**Keywords:** testing, pytest, unit tests, integration tests, fixtures, mocking, header validation, html assertions, test client, htmx testing
**TokenBudget:** ~4600
**ContextTier:** High
**Depends:** 221-python-htmx-core.md, 206-python-pytest.md

## Scope

**What This Rule Covers:**
Testing strategies for HTMX endpoints in Python applications, covering unit tests for header validation, integration tests for partial responses, pytest fixtures for HTMX requests, HTML assertion patterns, and mocking strategies.

**When to Load This Rule:**
- Writing tests for HTMX endpoints
- Creating pytest fixtures for HTMX requests
- Validating HTMX response headers
- Testing HTML structure in partials
- Mocking external dependencies in HTMX tests
- Setting up integration tests for HTMX applications

## References

### Dependencies

**Must Load First:**
- **221-python-htmx-core.md** - HTMX patterns to test
- **206-python-pytest.md** - Pytest best practices

**Related:**
- **221b-python-htmx-flask.md** - Flask-specific testing
- **221c-python-htmx-fastapi.md** - FastAPI-specific testing
- **200-python-core.md** - Python standards

### External Documentation

- [Pytest Documentation](https://docs.pytest.org/) - Official pytest guide
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/) - Flask test client
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/) - TestClient usage
- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML parsing

## Contract

### Inputs and Prerequisites

- Pytest framework
- Flask test_client or FastAPI TestClient
- HTML parsing library (BeautifulSoup4/lxml)
- HTMX core patterns (221-python-htmx-core.md)
- Pytest best practices (206-python-pytest.md)

### Mandatory

- Pytest
- Test client
- HTMX request fixtures
- HTML assertion utilities
- Mocking library (pytest-mock or unittest.mock)
- Test database/fixtures

### Forbidden

- Testing without HX-Request header
- Skipping HTML structure validation
- Not testing at minimum: 400 (validation failure), 401 (unauthorized), 404 (not found), and 500 (server error) responses for each HTMX endpoint group
- Missing header assertions
- Testing only happy path
- Relying on visual inspection instead of assertions

### Execution Steps

1. Install pytest and test dependencies (BeautifulSoup4, pytest-mock)
2. Create pytest fixtures for test client and HTMX headers
3. Write unit tests for HTMX detection logic
4. Write integration tests for endpoints (with/without HX-Request)
5. Add HTML assertion helpers for partial validation
6. Test response headers (HX-Trigger, HX-Redirect, etc.)
7. Mock external dependencies (database, APIs)
8. Run tests with coverage reporting

### Output Format

- Pytest test suite with fixtures
- Unit tests
- Integration tests
- HTML assertions
- Header validations
- Mocking

### Validation

**Pre-Task-Completion Checks:**
- Pytest installed with test client (Flask test_client, FastAPI TestClient)
- HTMX request fixtures created
- HTML parsing library installed (BeautifulSoup4 or lxml)
- Unit tests for header detection logic
- Integration tests for partial vs. full-page responses
- Tests cover success and error cases

**Success Criteria:**
- All HTMX endpoints have test coverage (with and without HX-Request)
- Response headers validated (HX-Trigger, HX-Redirect, etc.)
- HTML structure assertions pass for partials
- Error cases tested (400, 401, 404, 500)
- Mocking isolates HTMX logic from dependencies
- Test coverage >80% for HTMX routes

### Design Principles

- **Test with HX-Request header** - Always include `HX-Request: true` for HTMX tests
- **Assert response headers** - Validate `HX-Trigger`, `HX-Redirect`, `HX-Retarget`, etc.
- **Validate HTML structure** - Use BeautifulSoup or lxml to assert partial HTML content
- **Create HTMX fixtures** - Reusable pytest fixtures for HTMX request headers
- **Test both request types** - Verify endpoint behavior with and without HTMX headers
- **Mock external dependencies** - Isolate HTMX logic from database/API calls

### Post-Execution Checklist

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
- [ ] Mocking strategy defined for external dependencies

> **Investigation Required**
> Before creating or modifying HTMX tests, the agent MUST:
> 1. Read existing `conftest.py` files for HTMX test fixtures — never create duplicate `htmx_client` fixtures
> 2. Check installed HTML parsing library: `uv pip list | grep -i beautifulsoup` — use existing parser
> 3. Inspect current test directory structure and file naming conventions (e.g., `test_htmx_*.py` vs `tests/htmx/`)
> 4. Check if `pytest-cov` is configured in `pyproject.toml` for coverage settings
> 5. Verify existing mock patterns — use `@patch` or `mocker.patch()` consistently with the project

## Key Principles

### 1. Pytest Fixtures for HTMX

**Client and HTMX Header Fixtures:**

The `client` fixture differs by framework; the HTMX wrapper pattern is the same for both.

- **Flask:** `client = app.test_client()` (requires `app` fixture via `create_app({'TESTING': True})`)
- **FastAPI:** `client = TestClient(app)` (from `fastapi.testclient`)

```python
import pytest

@pytest.fixture
def htmx_headers():
    """Standard HTMX request headers"""
    return {
        'HX-Request': 'true',
        'HX-Current-URL': 'http://localhost/test'
    }

@pytest.fixture
def htmx_client(client, htmx_headers):
    """Test client wrapper that injects HTMX headers into every request"""
    class HTMXClient:
        def __init__(self, client, headers):
            self.client = client
            self.headers = headers

        def _merge(self, kwargs):
            kwargs.setdefault('headers', {}).update(self.headers)
            return kwargs

        def get(self, *a, **kw):    return self.client.get(*a, **self._merge(kw))
        def post(self, *a, **kw):   return self.client.post(*a, **self._merge(kw))
        def put(self, *a, **kw):    return self.client.put(*a, **self._merge(kw))
        def delete(self, *a, **kw): return self.client.delete(*a, **self._merge(kw))

    return HTMXClient(client, htmx_headers)
```

> **Async testing:** FastAPI's `TestClient` handles async routes synchronously via `anyio`. For direct async testing, use `httpx.AsyncClient` with `@pytest.mark.anyio`.

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
    assert tr.find('td', string='John Doe') is not None

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
    name_error = soup.find('span', class_='error', string=lambda t: t and 'name' in t.lower())
    assert name_error is not None

    email_error = soup.find('span', class_='error', string=lambda t: t and 'email' in t.lower())
    assert email_error is not None
```

### 6. Mocking External Dependencies

**Mocking Database Calls:**
```python
from unittest.mock import patch, MagicMock, AsyncMock

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

### Testing OOB Swaps

HTMX Out-of-Band swaps return multiple elements in a single response. Parse and assert each independently:

```python
def test_update_user_with_oob_notification(htmx_client):
    """Update should return updated row + OOB notification."""
    response = htmx_client.put('/users/1', data={'name': 'Updated Name'})
    assert response.status_code == 200

    soup = parse_html(response.data)

    # Primary content — updated user row
    user_row = soup.find('tr', id='user-1')
    assert user_row is not None
    assert 'Updated Name' in user_row.text

    # OOB element — notification toast
    oob_element = soup.find(attrs={'hx-swap-oob': 'true'})
    assert oob_element is not None
    assert oob_element.get('id') == 'notification-area'

    # HX-Trigger header for client-side events
    assert 'userUpdated' in response.headers.get('HX-Trigger', '')
```

**Key rules:**
- Parse the full response body — OOB elements are siblings of the primary content
- Use `soup.find(attrs={'hx-swap-oob': 'true'})` to locate OOB elements
- Assert both primary content and each OOB element independently

### Testing CSRF Protection

```python
def test_csrf_required_on_htmx_post(htmx_client, app):
    """POST without CSRF token should be rejected."""
    response = htmx_client.post('/users', data={'name': 'Test'})
    assert response.status_code == 400  # Flask-WTF rejects without token


def test_csrf_token_in_htmx_request(htmx_client, app):
    """POST with CSRF token should succeed."""
    with app.test_request_context():
        from flask_wtf.csrf import generate_csrf
        token = generate_csrf()

    response = htmx_client.post(
        '/users',
        data={'name': 'Test User', 'csrf_token': token},
        headers={'X-CSRFToken': token},  # HTMX sends via htmx:configRequest
    )
    assert response.status_code in (200, 201)
```

**Key rules:**
- Test that POST/PUT/DELETE endpoints reject requests without CSRF tokens
- Test that the `X-CSRFToken` header (set by `htmx:configRequest`) is accepted

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
    assert tr.find('td', string='John Doe') is not None
```

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

See sections 1-7 above for individual test patterns. Combine fixtures (section 1), assertions (sections 2-3), and integration patterns (section 4) into `tests/htmx/test_<feature>.py` files.
