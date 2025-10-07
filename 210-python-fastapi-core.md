**Description:** Comprehensive FastAPI best practices for building modern, performant, and maintainable web APIs and applications.
**AppliesTo:** `**/*.py`, `**/main.py`, `**/routers/**`, `**/models/**`, `**/services/**`, `**/database/**`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

**TokenBudget:** ~900
**ContextTier:** Medium

# FastAPI Best Practices

## Purpose
Provide comprehensive FastAPI development best practices, organized into focused patterns that cover all aspects of modern web API development including application architecture, async programming, request/response handling, and error management for building maintainable, performant web APIs.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** FastAPI web API development with modern Python patterns, async/await, and Pydantic integration


## Key Principles
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

## FastAPI Rule Categories

### 🏗️ Core Development Patterns (This File)
- Application structure and organization
- Async programming and performance
- Request/response handling with Pydantic
- Error handling and exception management
- Configuration management
- Integration with Python core rules

### 🔐 Security and Authentication  
**Rule:** `211-python-fastapi-security.md`
- JWT token authentication
- Role-based access control
- Security middleware (CORS, rate limiting)
- Input sanitization and validation
- Production security hardening
- Environment secrets management

### 🚀 Testing and Deployment
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

```python
# Recommended structure
app/
├── __init__.py
├── main.py              # Application factory and startup
├── config.py            # Configuration management
├── dependencies.py      # Dependency injection
├── exceptions.py        # Custom exception handlers
├── routers/
│   ├── __init__.py
│   ├── auth.py         # Authentication endpoints
│   ├── users.py        # User management
│   └── api_v1.py       # API version routing
├── models/
│   ├── __init__.py
│   ├── user.py         # Pydantic models
│   └── responses.py    # Response schemas
├── services/
│   ├── __init__.py
│   ├── auth_service.py # Business logic
│   └── user_service.py
└── database/
    ├── __init__.py
    ├── connection.py   # Database setup
    └── models.py       # SQLAlchemy/ORM models
```

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
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Related Rules
- **Python Core**: `200-python-core.md`
- **Python Project Setup**: `203-python-project-setup.md`
- **FastAPI Security**: `211-python-fastapi-security.md`
- **FastAPI Testing**: `212-python-fastapi-testing.md`
- **FastAPI Deployment**: `213-python-fastapi-deployment.md`
- **FastAPI Monitoring**: `214-python-fastapi-monitoring.md`
