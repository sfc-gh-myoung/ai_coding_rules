# FastAPI Testing Strategies

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** FastAPI testing, TestClient, pytest-asyncio, API tests, integration testing, mocking, test fixtures, AAA pattern, async testing, Python
**TokenBudget:** ~2050
**ContextTier:** High
**Depends:** rules/210-python-fastapi-core.md

## Purpose
Establish comprehensive testing strategies for FastAPI applications using TestClient, pytest-asyncio, and modern testing patterns to ensure reliability and maintainability.

## Rule Scope

FastAPI testing strategies with TestClient, pytest-asyncio, and comprehensive API testing patterns

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use TestClient for API testing** - `from fastapi.testclient import TestClient`
- **pytest-asyncio for async tests** - Mark tests with `@pytest.mark.asyncio`
- **Override dependencies in tests** - Use `app.dependency_overrides` for mocks
- **Test database fixture** - Create isolated test DB for each test
- **AAA pattern** - Arrange-Act-Assert in all tests
- **Test both success and errors** - Verify status codes, response bodies, error cases
- **Never share state between tests** - Each test must be isolated

**Quick Checklist:**
- [ ] TestClient configured in conftest.py
- [ ] Test database fixture with cleanup
- [ ] Dependencies overridden via app.dependency_overrides
- [ ] AAA pattern in all tests
- [ ] Both 200 and error status codes tested
- [ ] Async tests marked with @pytest.mark.asyncio
- [ ] Tests isolated (no shared state)

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

<design_principles>
1. **Test-Driven Development** - Use TestClient and pytest-asyncio for comprehensive API testing
2. **Async Testing** - Properly handle async operations in tests
3. **Fixture Management** - Create reusable test fixtures and utilities
4. **Mock External Dependencies** - Isolate units under test
5. **Test Both Success and Error Scenarios** - Comprehensive coverage
6. **Factory Patterns** - Use factory patterns for test data creation
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Using Synchronous TestClient for Async Endpoints

**Problem:** Using `TestClient` (synchronous) to test async endpoints that use async database operations or async dependencies.

**Why It Fails:** TestClient runs async code in a separate thread, masking concurrency bugs. Async context variables don't propagate correctly. Database sessions may not be properly scoped. Tests pass but production fails.

**Correct Pattern:**
```python
# BAD: Sync client for async app
from fastapi.testclient import TestClient

def test_async_endpoint():
    client = TestClient(app)
    response = client.get("/async-data")  # Runs in thread, misses async bugs

# GOOD: Use httpx.AsyncClient for async testing
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.mark.anyio
async def test_async_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.get("/async-data")
        assert response.status_code == 200
```

### Anti-Pattern 2: Testing Against Production Database

**Problem:** Running tests against real databases instead of isolated test databases or in-memory alternatives.

**Why It Fails:** Tests modify production data. Parallel test runs conflict with each other. Test failures can corrupt real data. Tests become slow and flaky due to network latency.

**Correct Pattern:**
```python
# BAD: Tests use production database
@pytest.fixture
def db():
    return SessionLocal()  # Connects to DATABASE_URL (production!)

# GOOD: Isolated test database with cleanup
@pytest.fixture
async def test_db():
    # Use separate test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()
```

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

> **Investigation Required**
> When applying this rule:
> 1. **Read existing test structure BEFORE adding tests** - Check tests/ directory, conftest.py, existing fixtures
> 2. **Verify current TestClient setup** - Check how app is created and dependencies are overridden
> 3. **Never speculate about test database** - Read conftest.py to see how test DB is configured
> 4. **Check existing test patterns** - Match AAA pattern, fixture usage, mocking approach
> 5. **Make grounded recommendations based on investigated test structure** - Don't add duplicate fixtures
>
> **Anti-Pattern:**
> "Based on typical FastAPI test setups, you probably use SQLite for testing..."
> "Let me add this test - it should work with standard TestClient..."
>
> **Correct Pattern:**
> "Let me check your existing test structure first."
> [reads tests/conftest.py, tests/test_*.py]
> "I see you have a test_app fixture that overrides get_db. Here's a new test following the same pattern with AAA structure..."

## Output Format Examples

```python
# Investigation: Check current implementation
# Read existing files, understand patterns

# Implementation: Following uv + ruff + pytest standards
from typing import Protocol
from datetime import datetime, UTC

class ServiceProtocol(Protocol):
    """Clear contract for service implementations."""

    def process(self, data: dict) -> dict:
        """Process data following validation rules."""
        ...

def implementation_function(input_data: dict) -> dict:
    """
    Implement feature following project conventions.

    Args:
        input_data: Validated input following schema

    Returns:
        Processed result with metadata

    Raises:
        ValueError: If input validation fails
    """
    # Use datetime.now(UTC) not datetime.utcnow()
    timestamp = datetime.now(UTC)

    # Implement business logic
    result = {"status": "success", "timestamp": timestamp}
    return result

# Validation: Test the implementation
def test_implementation_function():
    """Test following AAA pattern."""
    # Arrange
    test_input = {"key": "value"}

    # Act
    result = implementation_function(test_input)

    # Assert
    assert result["status"] == "success"
    assert "timestamp" in result
```

```bash
# Validation commands
uvx ruff check .
uvx ruff format --check .
uv run pytest tests/
```

## References

### External Documentation
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/) - Official testing patterns with TestClient and async support
- [Pytest Documentation](https://docs.pytest.org/) - Comprehensive testing framework guide and API reference
- [Pytest-asyncio Plugin](https://pytest-asyncio.readthedocs.io/) - Async test support and fixture management

### Related Rules
- **FastAPI Core**: `rules/210-python-fastapi-core.md`
- **FastAPI Security**: `rules/210a-python-fastapi-security.md`
- **Python Core**: `rules/200-python-core.md`
- **Faker**: `rules/240-python-faker.md`

## 1. Test Structure and Setup

### Basic Test Configuration
- **Always:** Use TestClient for API testing.
- **Always:** Use pytest-asyncio for async test functions.
- **Rule:** Test both success and error scenarios.

```python
# tests/conftest.py
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import create_app
from app.database.connection import get_db
from app.config import get_settings

# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create test database session."""
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def test_app(test_db):
    """Create test app with overridden dependencies."""
    app = create_app()

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    return app

@pytest.fixture
def client(test_app):
    """Create test client."""
    return TestClient(test_app)
```

## 2. API Testing Patterns

### Comprehensive Endpoint Testing
- **Always:** Test all CRUD operations and edge cases.
- **Rule:** Use factory patterns for test data creation.
- **Always:** Test authentication and authorization flows.

```python
# tests/test_users.py
import pytest
from fastapi import status
from app.models.user import UserCreate

class TestUserEndpoints:
    """Test suite for user management endpoints."""

    def test_create_user_success(self, client):
        """Test successful user creation."""
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = client.post("/users/", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert "password" not in data  # Ensure password not returned
        assert "id" in data
        assert "created_at" in data

    def test_create_user_invalid_email(self, client):
        """Test user creation with invalid email."""
        user_data = {
            "email": "invalid-email",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = client.post("/users/", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_data = response.json()
        assert "validation_error" in error_data["type"]
        assert "email" in str(error_data["details"])

    def test_get_user_authenticated(self, client, auth_headers):
        """Test getting user with valid authentication."""
        response = client.get("/users/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "email" in data
        assert "id" in data

    def test_get_user_unauthorized(self, client):
        """Test getting user without authentication."""
        response = client.get("/users/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_async_service_function(self, test_db):
        """Test async service functions directly."""
        from app.services.user_service import create_user

        user_data = UserCreate(
            email="async@test.com",
            password="password123",
            full_name="Async Test"
        )

        user = await create_user(test_db, user_data)
        assert user.email == user_data.email
        assert user.id is not None
```

## 3. Test Utilities and Fixtures

### Reusable Testing Components
- **Always:** Create reusable test fixtures and utilities.
- **Rule:** Mock external dependencies in tests.

```python
# tests/utils.py
from fastapi.testclient import TestClient
from app.services.auth_service import create_access_token
from datetime import timedelta

def create_test_user(client: TestClient, email: str = "test@example.com") -> dict:
    """Create a test user and return user data."""
    user_data = {
        "email": email,
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    return response.json()

def get_auth_headers(user_email: str = "test@example.com") -> dict:
    """Generate authentication headers for testing."""
    access_token = create_access_token(
        data={"sub": user_email},
        expires_delta=timedelta(hours=1)
    )
    return {"Authorization": f"Bearer {access_token}"}

@pytest.fixture
def auth_headers():
    """Fixture for authentication headers."""
    return get_auth_headers()
```

## 4. Integration with Core Rules

### Development Commands
- **Always:** Follow Python core rules from `200-python-core.md` for testing commands.
- **Always:** Apply linting rules from `201-python-lint-format.md` to test code.

# See 200-python-core.md for complete uv command patterns

### Test Configuration
```toml
# pyproject.toml - Test configuration
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = [
    "--strict-markers",
    "--cov=app",
    "--cov-report=term-missing",
    "--asyncio-mode=auto",
]
asyncio_mode = "auto"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```
