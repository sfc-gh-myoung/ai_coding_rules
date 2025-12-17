# FastAPI Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential FastAPI patterns. Load for FastAPI tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** FastAPI, async, REST API, Pydantic, dependency injection, routing, request validation, response models, APIRouter, uvicorn, async def, application factory
**TokenBudget:** ~2950
**ContextTier:** High
**Depends:** rules/200-python-core.md

## Purpose
Provide comprehensive FastAPI development best practices, organized into focused patterns that cover all aspects of modern web API development including application architecture, async programming, request/response handling, and error management for building maintainable, performant web APIs.

## Rule Scope

FastAPI web API development with modern Python patterns, async/await, and Pydantic integration

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use `uv run uvicorn app.main:app --reload`** - Never bare `uvicorn` command
- **Application factory pattern** - Create app through factory functions for testability
- **Separate request/response models** - Use Pydantic models, never reuse same model
- **APIRouter for modularity** - Organize routes in separate files, include in main app
- **Async def for I/O operations** - Use `async def` for database, HTTP, file operations
- **Dependency injection** - Use `Depends()` for services, database sessions, auth
- **Never mix sync and async** - All I/O should be async or properly wrapped
- **Cross-thread communication** - Use `asyncio.get_running_loop()` + `loop.call_soon_threadsafe()` for thread-to-async communication (SSE, progress callbacks)

**Quick Checklist:**
- [ ] App created via factory function
- [ ] Routes organized with APIRouter
- [ ] Separate request/response Pydantic models
- [ ] All I/O operations use async def
- [ ] Dependency injection for services
- [ ] Global exception handlers configured
- [ ] Run with `uv run uvicorn`
- [ ] Cross-thread callbacks use `loop.call_soon_threadsafe()` (not `asyncio.get_event_loop()`)

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
1. **Modular Architecture** - Organize code into logical, testable modules
2. **Async-First Development** - Leverage Python's async capabilities for performance
3. **Security by Design** - Implement authentication, authorization, and input validation
4. **Production Readiness** - Deploy with proper monitoring, logging, and scalability
5. **Test-Driven Development** - Comprehensive testing strategies for reliability
6. **Documentation Excellence** - Clear API documentation with OpenAPI customization
7. **Application Factory Pattern** - Use factory functions for app creation and configuration
8. **Pydantic Validation** - Validate all inputs/outputs with separate request/response models
9. **Dependency Injection** - Use FastAPI's dependency system for services and database sessions
10. **Structured Error Handling** - Implement global exception handlers with consistent responses
11. **Type Safety** - Use comprehensive type hints with Pydantic and FastAPI integration
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Blocking Calls in Async Route Handlers

**Problem:** Using synchronous blocking operations (requests, time.sleep, synchronous DB drivers) inside async FastAPI route handlers.

**Why It Fails:** Blocks the event loop, defeating the purpose of async. One slow request blocks all concurrent requests. Throughput drops to single-threaded performance. Server becomes unresponsive under load.

**Correct Pattern:**
```python
# BAD: Blocking call in async route
@app.get("/data")
async def get_data():
    response = requests.get("https://api.example.com/data")  # Blocks event loop!
    return response.json()

# GOOD: Use async HTTP client
import httpx

@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

### Anti-Pattern 2: Missing Dependency Injection for Database Sessions

**Problem:** Creating database sessions directly in route handlers instead of using FastAPI's dependency injection system.

**Why It Fails:** Sessions not properly closed on errors, causing connection leaks. Testing requires monkeypatching. No request-scoped lifecycle management. Duplicate boilerplate in every route.

**Correct Pattern:**
```python
# BAD: Manual session management
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    session = SessionLocal()  # Not closed on exception!
    user = session.query(User).get(user_id)
    session.close()
    return user

# GOOD: Dependency injection with proper lifecycle
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).get(user_id)
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
> 1. **Read existing FastAPI app structure BEFORE adding routes** - Check main.py, routers/, models/ organization
> 2. **Verify current dependency injection patterns** - Check how database sessions, services are injected
> 3. **Never speculate about async/sync usage** - Read actual endpoint definitions to verify async patterns
> 4. **Check existing Pydantic models** - Don't create duplicate request/response models
> 5. **Make grounded recommendations based on investigated app structure** - Match existing patterns
>
> **Anti-Pattern:**
> "Based on typical FastAPI apps, you probably use this structure..."
> "Let me add this endpoint - it should follow standard patterns..."
>
> **Correct Pattern:**
> "Let me check your FastAPI app structure first."
> [reads main.py, routers/, checks for APIRouter usage]
> "I see you're using APIRouter in routers/users.py with dependency injection for database sessions. Here's a new endpoint following the same pattern..."

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
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Related Rules
- **Python Core**: `rules/200-python-core.md`
- **Python Project Setup**: `rules/203-python-project-setup.md`
- **FastAPI Security**: `rules/210a-python-fastapi-security.md`
- **FastAPI Testing**: `rules/210b-python-fastapi-testing.md`
- **FastAPI Deployment**: `rules/210c-python-fastapi-deployment.md`
- **FastAPI Monitoring**: `rules/210d-python-fastapi-monitoring.md`

## FastAPI Rule Categories

### Core Development Patterns (This File)
- Application structure and organization
- Async programming and performance
- Request/response handling with Pydantic
- Error handling and exception management
- Configuration management
- Integration with Python core rules

### [SECURE] Security and Authentication
**Rule:** `210a-python-fastapi-security.md`
- JWT token authentication
- Role-based access control
- Security middleware (CORS, rate limiting)
- Input sanitization and validation
- Production security hardening
- Environment secrets management

### [DEPLOY] Testing and Deployment
**Rule:** `26-python-fastapi-deployment.md`
- Comprehensive testing strategies
- API documentation with OpenAPI
- Production deployment with Docker
- Health checks and monitoring
- Performance optimization and caching
- Structured logging and observability

## Quick Reference

### Development Workflow
```bash
# Setup (following 200-python-core.md)
uv run uvicorn app.main:app --reload

# Testing
uv run pytest tests/ -v --cov=app

# Linting (see 201-python-lint-format.md for complete configuration)
uvx ruff check . && uvx ruff format .
```

### Essential Patterns
- **Application Factory**: Create apps through factory functions
- **Dependency Injection**: Use FastAPI's dependency system for services
- **Async Throughout**: Use async/await for all I/O operations
- **Pydantic Validation**: Separate request/response models
- **Security First**: Implement authentication and input validation
- **Production Ready**: Health checks, logging, and monitoring

## 1. Application Structure and Organization

### Project Layout
- **Always:** Use the application factory pattern for FastAPI apps.
- **Always:** Organize code into logical modules: `routers/`, `models/`, `services/`, `database/`.
- **Always:** Follow the project structure from `23-python-project-setup.md` with proper `__init__.py` files.

Recommended directory structure for `app/`:
- `__init__.py`
- `main.py` - Application factory and startup
- `config.py` - Configuration management
- `dependencies.py` - Dependency injection
- `exceptions.py` - Custom exception handlers
- **routers/** - API route definitions
  - `__init__.py`
  - `auth.py` - Authentication endpoints
  - `users.py` - User management
  - `api_v1.py` - API version routing
- **models/** - Data models
  - `__init__.py`
  - `user.py` - Pydantic models
  - `responses.py` - Response schemas
- **services/** - Business logic
  - `__init__.py`
  - `auth_service.py`
  - `user_service.py`
- **database/** - Database layer
  - `__init__.py`
  - `connection.py` - Database setup
  - `models.py` - SQLAlchemy/ORM models

### Application Factory Pattern
- **Requirement:** Create FastAPI app instance through a factory function.
- **Always:** Separate app creation from configuration and startup logic.

```python
# app/main.py
from fastapi import FastAPI
from app.routers import auth, users
from app.exceptions import add_exception_handlers
from app.config import get_settings

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.version,
        docs_url="/docs" if settings.debug else None,
    )

    # Add exception handlers
    add_exception_handlers(app)

    # Include routers
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(users.router, prefix="/users", tags=["users"])

    return app

app = create_app()
```

## 2. Async Programming and Performance

### Async Best Practices
- **Critical:** Use `async def` for all route handlers that perform I/O operations.
- **Always:** Use `await` for database queries, HTTP requests, and file operations.
- **Rule:** Never mix blocking and non-blocking code without proper handling.

```python
# CORRECT: Async route with proper await
@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# INCORRECT: Missing async/await
@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    # This blocks the event loop
    user = db.query(User).filter(User.id == user_id).first()
    return user
```

### Cross-Thread Async Communication (SSE, Background Tasks)
- **Critical:** When running synchronous code in a thread that needs to communicate with async code, capture the event loop BEFORE starting the thread.
- **Always:** Use `asyncio.get_running_loop()` (not `get_event_loop()`) to capture the loop in an async context.
- **Always:** Use `loop.call_soon_threadsafe()` to safely add items to an `asyncio.Queue` from a background thread.
- **Always:** Use `asyncio.to_thread()` for running blocking code - it properly integrates with the event loop.
- **Never:** Call `asyncio.get_event_loop()` from inside a thread - threads don't have event loops.

```python
# CORRECT: Cross-thread communication for SSE streaming with progress updates
@router.get("/process/stream")
async def process_with_progress():
    """Stream progress updates from a blocking operation."""
    # Capture event loop BEFORE starting thread work
    loop = asyncio.get_running_loop()
    progress_queue: asyncio.Queue[dict] = asyncio.Queue()

    def progress_callback(step: str, message: str) -> None:
        """Thread-safe callback using loop.call_soon_threadsafe()."""
        loop.call_soon_threadsafe(
            progress_queue.put_nowait,
            {"step": step, "message": message}
        )

    async def run_blocking_work():
        """Run blocking code in thread pool with asyncio.to_thread()."""
        return await asyncio.to_thread(
            blocking_function, progress_callback
        )

    async def event_generator():
        """Generate SSE events from progress queue."""
        task = asyncio.create_task(run_blocking_work())

        while True:
            if task.done():
                # Drain remaining messages
                while not progress_queue.empty():
                    msg = await progress_queue.get()
                    yield f"data: {json.dumps(msg)}\n\n"

                # Send final result
                try:
                    result = task.result()
                    yield f"data: {json.dumps({'status': 'done'})}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
                break

            try:
                msg = await asyncio.wait_for(progress_queue.get(), timeout=0.5)
                yield f"data: {json.dumps(msg)}\n\n"
            except TimeoutError:
                yield f"data: {json.dumps({'step': 'ping'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# INCORRECT: Trying to access event loop from thread
def bad_callback(step: str, message: str) -> None:
    # This will raise "no current event loop in thread" error!
    asyncio.get_event_loop().call_soon_threadsafe(...)
```

### Database Connections
- **Always:** Use connection pooling with async database drivers.
- **Always:** Implement proper dependency injection for database sessions.
- **Rule:** Never create database connections in route handlers directly.

```python
# app/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

## 3. Request/Response Handling and Validation

### Pydantic Models
- **Always:** Use Pydantic models for request and response validation.
- **Always:** Separate input models from output models for security.
- **Rule:** Never expose internal model fields in API responses.

```python
# app/models/user.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """User creation request model."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)

class UserResponse(BaseModel):
    """User response model - excludes sensitive fields."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    created_at: datetime
    is_active: bool

class UserUpdate(BaseModel):
    """User update model - all fields optional."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: Optional[bool] = None
```

### Input Validation
- **Always:** Validate all input parameters using Pydantic Field constraints.
- **Always:** Use appropriate HTTP status codes for validation errors.
- **Rule:** Provide clear, actionable error messages.

```python
from pydantic import field_validator, Field

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0, le=10000)
    category_id: int = Field(..., gt=0)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        return v.strip()
```

## 4. Error Handling and Exception Management

### Custom Exception Handlers
- **Always:** Implement global exception handlers for consistent error responses.
- **Always:** Log errors with appropriate severity levels.
- **Rule:** Never expose internal error details to clients in production.

```python
# app/exceptions.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

class AppException(Exception):
    """Base application exception."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class UserNotFoundError(AppException):
    def __init__(self, user_id: int):
        super().__init__(f"User {user_id} not found", 404)

async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"Application error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": "application_error"}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "details": exc.errors(),
            "type": "validation_error"
        }
    )

def add_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
```

## 5. Configuration Management

### Environment-Based Configuration
- **Always:** Use environment variables for configuration.
- **Always:** Use Pydantic Settings for type-safe configuration.
- **Rule:** Never commit secrets to version control.

```python
# app/config.py
from pydantic import BaseSettings, PostgresDsn, field_validator, ConfigDict
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "FastAPI App"
    debug: bool = False
    version: str = "1.0.0"

    # Database
    database_url: PostgresDsn

    # Security
    secret_key: str
    access_token_expire_minutes: int = 30

    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

## 6. Integration with Python Core Rules

### Compliance with Existing Rules
- **Always:** Follow all directives from `200-python-core.md` for Python best practices.
- **Always:** Use `uv run uvicorn` instead of bare `uvicorn` for development.
- **Always:** Apply linting and formatting rules from `201-python-lint-format.md`.
- **Always:** Follow project setup patterns from `203-python-project-setup.md`.

### Development Commands
- **Always:** Follow Python core rules from `200-python-core.md` for all uv commands.
- **Always:** Apply linting and formatting rules from `201-python-lint-format.md`.
- **FastAPI Specific:** Use `uv run uvicorn app.main:app --reload` for development server.
