**Description:** FastAPI testing strategies with TestClient, pytest-asyncio, and comprehensive API testing patterns.
**AppliesTo:** `**/tests/**`, `**/test_*.py`, `**/conftest.py`
**AutoAttach:** false
**Type:** Agent Requested
**Keywords:** FastAPI testing, TestClient, pytest-asyncio, API tests, integration testing, mocking
**Version:** 1.2
**LastUpdated:** 2025-10-13

**TokenBudget:** ~600
**ContextTier:** Medium

# FastAPI Testing Strategies

## Purpose
Establish comprehensive testing strategies for FastAPI applications using TestClient, pytest-asyncio, and modern testing patterns to ensure reliability and maintainability.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** FastAPI testing strategies with TestClient, pytest-asyncio, and comprehensive API testing patterns


## Key Principles
1. **Test-Driven Development** - Use TestClient and pytest-asyncio for comprehensive API testing
2. **Async Testing** - Properly handle async operations in tests
3. **Fixture Management** - Create reusable test fixtures and utilities
4. **Mock External Dependencies** - Isolate units under test
5. **Test Both Success and Error Scenarios** - Comprehensive coverage
6. **Factory Patterns** - Use factory patterns for test data creation

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

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/) - Official testing patterns with TestClient and async support                                                                                 
- [Pytest Documentation](https://docs.pytest.org/) - Comprehensive testing framework guide and API reference
- [Pytest-asyncio Plugin](https://pytest-asyncio.readthedocs.io/) - Async test support and fixture management

### Related Rules
- **FastAPI Core**: `210-python-fastapi-core.md`
- **FastAPI Security**: `211-python-fastapi-security.md`
- **Python Core**: `200-python-core.md`
- **Faker**: `240-python-faker.md`
