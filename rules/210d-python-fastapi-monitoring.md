# FastAPI Monitoring and Performance

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** FastAPI monitoring, health checks, logging, metrics, caching, Redis, observability, structured logging, health endpoints, correlation IDs
**TokenBudget:** ~3900
**ContextTier:** Medium
**Depends:** 210-python-fastapi-core.md

## Scope

**What This Rule Covers:**
Establish monitoring, logging, and performance optimization patterns for FastAPI applications including health checks, structured logging, caching, and observability.

**When to Load This Rule:**
- FastAPI health checks, logging, monitoring, and performance optimization patterns

## References

### External Documentation
- [FastAPI Middleware Guide](https://fastapi.tiangolo.com/tutorial/middleware/) - Custom middleware, CORS, and request processing
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html) - Structured logging, handlers, and formatters
- [Redis Python Async](https://redis-py.readthedocs.io/en/stable/) - Async Redis operations and connection pooling

### Related Rules
- **FastAPI Core**: `210-python-fastapi-core.md`
- **FastAPI Deployment**: `210c-python-fastapi-deployment.md`
- **Python Core**: `200-python-core.md`

## Contract

### Inputs and Prerequisites

- Existing FastAPI application with routes defined
- Understanding of monitoring and observability requirements
- Knowledge of health check patterns for load balancers
- Access to logging and metrics infrastructure

### Mandatory

- **FastAPI** application instance
- **Health check endpoints** (/health, /health/ready, /health/live)
- **Structured logging** with JSON formatter
- **Correlation IDs** for request tracing
- **Redis** for caching (if using caching patterns)

### Forbidden

- Logging sensitive data (passwords, tokens, PII) without sanitization
- Missing correlation IDs for distributed tracing
- Single health check endpoint without readiness/liveness separation
- Synchronous blocking operations in async endpoints
- Hardcoded connection pool sizes without configuration

### Execution Steps

1. Implement health check endpoints (/health, /health/ready, /health/live)
2. Configure structured logging with JSON formatter
3. Add correlation ID middleware for request tracing
4. Implement caching layer with Redis (if needed)
5. Configure connection pool optimization for database
6. Add metrics collection middleware
7. Set up error tracking and alerting
8. Validate with: `curl http://localhost:8000/health` and `uv run pytest tests/`

### Output Format

FastAPI application with:
- Health check router with multiple endpoints
- Structured logging configuration with JSON output
- Correlation ID middleware
- Caching manager with Redis integration
- Metrics middleware for performance tracking
- Error handlers with proper logging

### Validation

**Pre-Task-Completion Checks:**
- Health endpoints return 200 for healthy state
- Structured logs include correlation_id field
- Sensitive data is sanitized before logging
- Cache hit/miss metrics are tracked
- Database connection pool is configured

**Success Criteria:**
- `curl http://localhost:8000/health` returns {"status": "healthy"}
- `curl http://localhost:8000/health/ready` checks database connectivity
- Logs are in JSON format with correlation IDs
- `uvx ruff check .` passes with zero errors
- `uv run pytest tests/` passes all monitoring tests

### Design Principles

1. **Health Monitoring** - Implement comprehensive health checks for load balancers and orchestration
2. **Structured Logging** - Use JSON logging with correlation IDs for distributed tracing
3. **Performance Optimization** - Implement caching, connection pooling, and efficient patterns
4. **Observability** - Metrics, distributed tracing, and monitoring integration
5. **Error Tracking** - Comprehensive error logging and alerting
6. **Resource Monitoring** - Track system resources and database performance

### Post-Execution Checklist

- [ ] Health check endpoints implemented (/health, /health/ready, /health/live)
- [ ] Structured logging configured with JSON formatter
- [ ] Correlation ID middleware added
- [ ] Sensitive data sanitization in logs
- [ ] Caching layer configured (if needed)
- [ ] Connection pool optimized
- [ ] Metrics middleware collecting performance data
- [ ] Error tracking configured
- [ ] Tests cover health checks and logging
- [ ] Linting and tests pass

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Logging Sensitive Data in Request/Response Bodies

**Problem:** Enabling full request/response body logging without filtering sensitive fields like passwords, tokens, or PII.

**Why It Fails:** Credentials and personal data written to log files. Log aggregation services store sensitive data. Compliance violations (GDPR, HIPAA, PCI-DSS). Security audits fail. Data breaches from log access.

**Correct Pattern:**
```python
# BAD: Log everything including secrets
@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    logger.info(f"Request body: {body}")  # Logs passwords!
    return await call_next(request)

# GOOD: Filter sensitive fields before logging
SENSITIVE_FIELDS = {"password", "token", "api_key", "ssn", "credit_card"}

def sanitize_log_data(data: dict) -> dict:
    return {k: "***REDACTED***" if k in SENSITIVE_FIELDS else v
            for k, v in data.items()}

logger.info(f"Request: {sanitize_log_data(request_data)}")
```

### Anti-Pattern 2: Missing Correlation IDs for Request Tracing

**Problem:** Not generating or propagating unique request IDs across service calls, making it impossible to trace requests through distributed systems.

**Why It Fails:** Cannot correlate logs from different services for same request. Debugging production issues requires manual timestamp matching. No distributed tracing capability. Incident response takes hours instead of minutes.

**Correct Pattern:**
```python
# BAD: No request correlation
@app.get("/api/data")
async def get_data():
    logger.info("Fetching data")  # Which request is this?
    return await fetch_from_service()

# GOOD: Correlation ID middleware
from uuid import uuid4

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
    with structlog.contextvars.bound_contextvars(correlation_id=correlation_id):
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
```

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

## Health Checks and Monitoring

### Health Check Endpoints
- **Always:** Implement health check endpoints for load balancers.
- **Always:** Use structured logging with correlation IDs.
- **Rule:** Monitor application metrics and performance.

```python
# app/routers/health.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_db
from app.config import get_settings
from datetime import datetime, UTC
import psutil
import asyncio

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Basic health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": get_settings().version
    }

@router.get("/health/detailed")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with system metrics."""
    try:
        # Database connectivity check
        await db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # System metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    health_data = {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": get_settings().version,
        "checks": {
            "database": db_status,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        }
    }

    if health_data["status"] == "degraded":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_data
        )

    return health_data

@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe."""
    try:
        await db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "not ready", "reason": "database unavailable"}
        )

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}
```

## Structured Logging

### Logging Configuration
- **Always:** Use structured logging with JSON format.
- **Rule:** Include correlation IDs for request tracing.

```python
# app/logging/config.py
import logging
import json
import uuid
from datetime import datetime, UTC
from fastapi import Request
from typing import Dict, Any

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, 'correlation_id'):
            log_data['correlation_id'] = record.correlation_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)

def setup_logging():
    """Configure application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )

    # Set formatter for all handlers
    formatter = StructuredFormatter()
    for handler in logging.root.handlers:
        handler.setFormatter(formatter)

# Middleware for request logging
class RequestLoggingMiddleware:
    """Middleware to add correlation IDs and log requests."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Generate correlation ID
            correlation_id = str(uuid.uuid4())

            # Add to request state
            request = Request(scope, receive)
            request.state.correlation_id = correlation_id

            # Log request
            logger = logging.getLogger("fastapi.request")
            logger.info(
                "Request started",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "url": str(request.url),
                    "client_ip": request.client.host if request.client else None
                }
            )

        await self.app(scope, receive, send)
```

## Performance Optimization

### Caching Strategies
- **Always:** Implement caching for expensive operations.
- **Rule:** Use appropriate cache invalidation strategies.

```python
# app/cache/redis.py
import redis.asyncio as redis
import json
from typing import Optional, Any
from functools import wraps
import hashlib

class CacheManager:
    """Redis-based cache manager."""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL."""
        try:
            serialized = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized)
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            await self.redis.delete(key)
            return True
        except Exception:
            return False

def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = f"{key_prefix}:{hashlib.md5(key_data.encode()).hexdigest()}"

            # Try to get from cache
            cache_manager = get_cache_manager()
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            return result

        return wrapper
    return decorator

# Usage example
@cache_result(ttl=600, key_prefix="user")
async def get_user_profile(user_id: int):
    """Get user profile with caching."""
    # Expensive database operation
    return await fetch_user_profile_from_db(user_id)
```

### Connection Pool Optimization
```python
# app/database/connection.py - Enhanced connection pooling
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Optimized engine configuration
engine = create_async_engine(
    settings.database_url,
    # Connection pool settings
    pool_size=20,           # Number of connections to maintain
    max_overflow=30,        # Additional connections beyond pool_size
    pool_pre_ping=True,     # Verify connections before use
    pool_recycle=3600,      # Recycle connections after 1 hour
    # Performance settings
    echo=settings.debug,    # Log SQL queries in debug mode
    future=True,           # Use SQLAlchemy 2.0 style
)
```

## Performance Monitoring

### Metrics Collection
```python
# app/middleware/metrics.py
import time
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import logging

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect performance metrics."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process request
        response: Response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log metrics
        logger = logging.getLogger("fastapi.metrics")
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_seconds": duration,
                "correlation_id": getattr(request.state, 'correlation_id', None)
            }
        )

        # Add performance headers
        response.headers["X-Process-Time"] = str(duration)

        return response
```

## Integration with Core Rules

### Development Commands
- **Always:** Follow Python core rules from `200-python-core.md`.
- **Always:** Apply linting rules from `201-python-lint-format.md`.

```bash
# Health check testing
curl http://localhost:8000/health
curl http://localhost:8000/health/detailed

# Log monitoring (development)
uv run uvicorn app.main:app --log-level debug

# Performance testing
uv run python -m pytest tests/test_performance.py -v
```

### Configuration Integration
```python
# app/config.py - Monitoring settings
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Existing settings...

    # Monitoring settings
    enable_metrics: bool = True
    enable_health_checks: bool = True
    log_level: str = "INFO"

    # Cache settings
    redis_url: Optional[str] = None
    cache_ttl_default: int = 300

    # Performance settings
    max_request_size: int = 16 * 1024 * 1024  # 16MB
    request_timeout: int = 30

    class Config:
        env_file = ".env"
```
