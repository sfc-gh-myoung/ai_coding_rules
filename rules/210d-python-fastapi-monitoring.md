# FastAPI Monitoring and Performance

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** FastAPI monitoring, health checks, logging, metrics, caching, Redis, observability, structured logging, health endpoints, correlation IDs
**TokenBudget:** ~2500
**ContextTier:** Medium
**Depends:** rules/210-python-fastapi-core.md

## Purpose
Establish monitoring, logging, and performance optimization patterns for FastAPI applications including health checks, structured logging, caching, and observability.

## Rule Scope

FastAPI health checks, logging, monitoring, and performance optimization patterns

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Implement /health endpoint** - Required for load balancers and orchestration
- **Use structured JSON logging** - Include correlation IDs for distributed tracing
- **Add caching strategically** - Use Redis for frequently accessed data
- **Monitor database connections** - Check and log connection pool health
- **Track request metrics** - Response times, error rates, throughput
- **Never log sensitive data** - Sanitize credentials, tokens, PII from logs

**Quick Checklist:**
- [ ] /health endpoint returns 200 with status details
- [ ] Structured logging configured (JSON format)
- [ ] Correlation IDs in all log entries
- [ ] Caching implemented for read-heavy endpoints
- [ ] Database health checks in /health response
- [ ] Error tracking and alerting configured
- [ ] Performance metrics collected

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
1. **Health Monitoring** - Implement comprehensive health checks for load balancers and orchestration
2. **Structured Logging** - Use JSON logging with correlation IDs for distributed tracing
3. **Performance Optimization** - Implement caching, connection pooling, and efficient patterns
4. **Observability** - Metrics, distributed tracing, and monitoring integration
5. **Error Tracking** - Comprehensive error logging and alerting
6. **Resource Monitoring** - Track system resources and database performance
</design_principles>

</contract>

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
> 1. **Read existing health endpoints BEFORE adding monitoring** - Check if /health or similar already exists
> 2. **Check logging configuration** - Read existing logging setup, format, handlers
> 3. **Never assume monitoring stack** - Check if Redis, Prometheus, or other tools are available
> 4. **Verify middleware order** - Read app initialization to understand middleware stack
> 5. **Test health checks** - Ensure they don't cause cascading failures
>
> **Anti-Pattern:**
> "Adding /health endpoint... (without checking if it exists)"
> "Configuring Redis caching... (without verifying Redis is available)"
>
> **Correct Pattern:**
> "Let me check your existing monitoring setup first."
> [reads app files, checks for health endpoints, reviews logging config]
> "I see you have basic health checks. Enhancing with database status and caching metrics..."

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
- [FastAPI Middleware Guide](https://fastapi.tiangolo.com/tutorial/middleware/) - Custom middleware, CORS, and request processing
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html) - Structured logging, handlers, and formatters
- [Redis Python Async](https://redis-py.readthedocs.io/en/stable/) - Async Redis operations and connection pooling

### Related Rules
- **FastAPI Core**: `rules/210-python-fastapi-core.md`
- **FastAPI Deployment**: `rules/210c-python-fastapi-deployment.md`
- **Python Core**: `rules/200-python-core.md`

## 1. Health Checks and Monitoring

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

## 2. Structured Logging

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

## 3. Performance Optimization

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

## 4. Performance Monitoring

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

## 5. Integration with Core Rules

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
