# FastAPI Deployment and Documentation

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** FastAPI deployment, Uvicorn, Gunicorn, ASGI, Docker, production deployment, health checks, multi-stage build, OpenAPI, API documentation
**TokenBudget:** ~2400
**ContextTier:** High
**Depends:** rules/210-python-fastapi-core.md

## Purpose
Establish production deployment patterns and API documentation practices for FastAPI applications using Docker, ASGI servers, and OpenAPI customization.

## Rule Scope

FastAPI production deployment with Docker, ASGI servers, and API documentation patterns

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use Gunicorn + Uvicorn workers** - `gunicorn -k uvicorn.workers.UvicornWorker app.main:app`
- **Multi-stage Docker builds** - Builder stage + production stage
- **Non-root container user** - Create and use dedicated app user in Dockerfile
- **Health check endpoint** - `/health` route for container health checks
- **OpenAPI customization** - Add examples, descriptions, response schemas
- **Environment-based config** - Different settings for dev/test/prod
- **Never run as root in containers** - Security risk, always use non-root user

**Quick Checklist:**
- [ ] Gunicorn + Uvicorn workers configured
- [ ] Multi-stage Dockerfile (builder + production)
- [ ] Non-root user in container
- [ ] Health check endpoint implemented
- [ ] OpenAPI examples and descriptions
- [ ] Environment-specific configuration
- [ ] Docker Compose for local development

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
1. **Production Ready** - Deploy with Uvicorn/Gunicorn and proper process management
2. **Container Deployment** - Use Docker with multi-stage builds and security best practices
3. **Documentation First** - Leverage OpenAPI with custom schemas and examples
4. **Security Hardening** - Run containers as non-root user with minimal attack surface
5. **Process Management** - Configure proper worker counts and timeout settings
6. **Environment Configuration** - Use environment-specific configuration files
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Single Worker Process in Production

**Problem:** Running FastAPI with a single uvicorn worker (`uvicorn main:app`) in production, unable to utilize multiple CPU cores.

**Why It Fails:** Single process handles all requests sequentially. CPU-bound tasks block the entire application. No fault tolerance—process crash means total downtime. Cannot scale to handle production traffic.

**Correct Pattern:**
```bash
# BAD: Single worker (development only)
uvicorn main:app --host 0.0.0.0 --port 8000

# GOOD: Multiple workers with process manager
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use uvicorn with workers (requires --workers flag)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Rule of thumb: workers = (2 * CPU_CORES) + 1
```

### Anti-Pattern 2: Missing Health Check Endpoints

**Problem:** Deploying FastAPI applications without health check endpoints for load balancers and orchestrators to verify application readiness.

**Why It Fails:** Load balancers can't detect unhealthy instances. Kubernetes can't perform liveness/readiness probes. Failed deployments aren't detected. Traffic routed to broken instances.

**Correct Pattern:**
```python
# BAD: No health checks
# Load balancer has no way to verify app is healthy

# GOOD: Comprehensive health endpoints
@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe - is the process running?"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness(db: Session = Depends(get_db)):
    """Kubernetes readiness probe - can we serve traffic?"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        raise HTTPException(503, "Database unavailable")
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
> 1. **Read existing deployment files BEFORE adding config** - Check Dockerfile, docker-compose.yml, gunicorn.conf.py
> 2. **Verify current ASGI server setup** - Check if Uvicorn or Gunicorn is already configured
> 3. **Never speculate about deployment target** - Ask user about deployment platform (AWS, GCP, Azure, etc.)
> 4. **Check existing health check endpoints** - Don't create duplicate /health routes
> 5. **Make grounded recommendations based on investigated deployment structure** - Match existing patterns
>
> **Anti-Pattern:**
> "Based on typical deployments, you probably use Docker..."
> "Let me add a Dockerfile - it should work with standard multi-stage builds..."
>
> **Correct Pattern:**
> "Let me check your existing deployment configuration first."
> [reads Dockerfile, docker-compose.yml, checks for ASGI server config]
> "I see you have a Dockerfile using Gunicorn with Uvicorn workers. Here's how to add health checks following the same pattern..."

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
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/) - Production deployment strategies and server configurations
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/) - ASGI server deployment and process management
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html) - Worker processes, timeouts, and production settings

### Related Rules
- **FastAPI Core**: `rules/210-python-fastapi-core.md`
- **FastAPI Security**: `rules/210a-python-fastapi-security.md`
- **FastAPI Monitoring**: `rules/210d-python-fastapi-monitoring.md`
- **Python Core**: `rules/200-python-core.md`

## 1. API Documentation

### OpenAPI Customization
- **Always:** Provide clear descriptions for all endpoints.
- **Always:** Use proper HTTP status codes and document them.
- **Rule:** Include examples in your API documentation.

```python
# app/docs/examples.py
from app.models.user import UserCreate, UserResponse

user_create_example = {
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
}

user_response_example = {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "created_at": "2024-01-15T10:30:00Z",
    "is_active": True
}

# Enhanced endpoint documentation
@router.post(
    "/users/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user account with email and password. Email must be unique.",
    response_description="The created user object",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": user_response_example
                }
            }
        },
        400: {
            "description": "Invalid input data",
            "content": {
                "application/json": {
                    "example": {"error": "Email already registered", "type": "validation_error"}
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation failed",
                        "details": [{"field": "email", "message": "Invalid email format"}],
                        "type": "validation_error"
                    }
                }
            }
        }
    },
    tags=["users"]
)
async def create_user(
    user_data: UserCreate = Body(..., example=user_create_example),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Create a new user account.

    **Required fields:**
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **full_name**: User's full name (1-100 characters)

    **Returns:**
    - User object with ID and timestamps
    - Password is never returned in response
    """
    # Implementation here
    pass
```

### Custom OpenAPI Schema
- **Always:** Customize OpenAPI metadata for better documentation.
- **Rule:** Organize endpoints with tags and descriptions.

```python
# app/docs/openapi.py
from fastapi.openapi.utils import get_openapi
from app.main import app

def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="FastAPI Application",
        version="1.0.0",
        description="""
        ## FastAPI Application API

        This API provides user management, authentication, and business logic endpoints.

        ### Authentication
        Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:
        ```
        Authorization: Bearer <your-jwt-token>
        ```

        ### Error Handling
        All errors follow a consistent format with appropriate HTTP status codes.

        ### Rate Limiting
        API endpoints are rate limited. Check response headers for current limits.
        """,
        routes=app.routes,
        tags=[
            {
                "name": "auth",
                "description": "Authentication and authorization operations"
            },
            {
                "name": "users",
                "description": "User management operations"
            },
            {
                "name": "health",
                "description": "Health check endpoints for monitoring"
            }
        ]
    )

    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## 2. Production Deployment

### ASGI Server Configuration
- **Always:** Use Uvicorn with Gunicorn for production deployment.
- **Always:** Configure proper worker counts and timeout settings.
- **Rule:** Use environment-specific configuration files.

```python
# gunicorn.conf.py
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
worker_class = "uvicorn.workers.UvicornWorker"
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeouts
timeout = 30
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "fastapi-app"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = os.getenv("USER", "nobody")
group = os.getenv("GROUP", "nogroup")
tmp_upload_dir = None

# SSL (if needed)
keyfile = os.getenv("SSL_KEYFILE")
certfile = os.getenv("SSL_CERTFILE")
```

### Docker Configuration
- **Always:** Use multi-stage Docker builds for smaller images.
- **Rule:** Run containers as non-root user for security.
- **Always:** Use specific base image versions, not 'latest'.

```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set work directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
```

### Docker Compose for Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@db:5432/fastapi_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: fastapi_db
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 3. Integration with Core Rules

### Development Commands
- **Always:** Follow Python core rules from `200-python-core.md` for all commands.
- **Always:** Apply linting rules from `201-python-lint-format.md`.

```bash
# See 200-python-core.md for development commands
# Production deployment
uv run gunicorn app.main:app -c gunicorn.conf.py

# Container builds
docker build -t fastapi-app .
docker-compose up --build
```
