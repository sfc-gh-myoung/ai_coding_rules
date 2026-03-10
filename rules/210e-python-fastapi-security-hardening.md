# 210e: FastAPI Security Hardening

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:fastapi-security, kw:cors, kw:rate-limit, kw:security-headers
**Keywords:** FastAPI hardening, CORS, CSRF, rate limiting, security headers, input validation, SQL injection, XSS prevention, trusted hosts, production security
**TokenBudget:** ~2800
**ContextTier:** Medium
**Depends:** 210a-python-fastapi-security.md

## Scope

**What This Rule Covers:**
Infrastructure security hardening for FastAPI applications. Covers CORS configuration, security headers, rate limiting, input validation, SQL injection prevention, XSS prevention, and production deployment security. For authentication and authorization patterns, see **210a-python-fastapi-security.md**.

**When to Load This Rule:**
- Configuring CORS middleware for FastAPI
- Adding security headers to API responses
- Implementing rate limiting per endpoint
- Hardening input validation against injection attacks
- Preparing FastAPI applications for production deployment

## References

### Dependencies

**Must Load First:**
- **210a-python-fastapi-security.md** - Authentication and authorization patterns

**Related:**
- **210-python-fastapi-core.md** - FastAPI foundation patterns
- **210c-python-fastapi-deployment.md** - Deployment configuration

### External Documentation

- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)

## Contract

### Inputs and Prerequisites

- FastAPI application with authentication configured (210a)
- Understanding of CORS and security header requirements
- Knowledge of expected API consumers (origins)

### Mandatory

- CORS middleware with explicit origin allowlist
- Security headers on all responses
- Rate limiting on authentication and write endpoints
- Parameterized queries for all database operations
- Input validation via Pydantic models

### Forbidden

- Using `allow_origins=["*"]` in production CORS
- String concatenation in SQL queries
- Trusting user input without validation
- Disabling security headers for convenience

### Execution Steps

1. Configure CORS middleware with explicit allowed origins
2. Add security headers middleware
3. Implement per-endpoint rate limiting with slowapi
4. Validate all inputs with Pydantic models and field validators
5. Ensure parameterized queries for database operations
6. Disable API docs and debug mode in production
7. Test security headers and CORS behavior

### Output Format

```python
# Example: Secure FastAPI configuration
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from secure import SecureHeaders

app = FastAPI(docs_url=None, redoc_url=None)  # Disable in production

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],  # Explicit allowlist
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Post-Execution Checklist

- [ ] CORS middleware uses explicit origin allowlist (no wildcards in production)
- [ ] Security headers middleware configured
- [ ] Rate limiting applied to auth and write endpoints
- [ ] All SQL queries use parameterization
- [ ] Pydantic models validate all user inputs
- [ ] API docs disabled in production deployments

### Validation

**Pre-Task-Completion Checks:**
- CORS configured with explicit allowed origins
- Security headers present on all responses
- Rate limiting active on auth and write endpoints
- No string concatenation in SQL queries
- Pydantic validation on all user inputs
- API docs disabled in production

**Success Criteria:**
- CORS blocks unauthorized origins
- Security headers pass securityheaders.com scan
- Rate-limited endpoints return 429 when exceeded
- SQL injection attempts are rejected
- Invalid inputs return 422 with clear error messages

## Anti-Patterns and Common Mistakes

### Anti-Pattern: Overly Permissive CORS Configuration

**Problem:** Setting `allow_origins=["*"]` in production CORS middleware, allowing any website to make authenticated requests to your API.

**Why It Fails:** Enables cross-site request forgery (CSRF) attacks. Malicious sites can make authenticated API calls using victim's cookies. Credential theft and data exfiltration become trivial.

**Correct Pattern:**
```python
# BAD: Allow all origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Any site can call your API!
    allow_credentials=True,
)

# GOOD: Explicit origin allowlist
ALLOWED_ORIGINS = [
    "https://myapp.com",
    "https://admin.myapp.com",
]
if settings.environment == "development":
    ALLOWED_ORIGINS.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
)
```

### Anti-Pattern 2: Missing Rate Limiting on Authentication Endpoints

**Problem:** Not rate limiting login/auth endpoints allows brute force password attacks.

**Why It Fails:** Attackers can attempt thousands of password combinations per minute. Without rate limiting, credential stuffing attacks succeed quickly.

**Correct Pattern:**
```python
# BAD: No rate limiting
@app.post("/auth/login")
async def login(credentials: LoginRequest):
    return authenticate(credentials)  # Unlimited attempts!

# GOOD: Rate limited authentication
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/auth/login")
@limiter.limit("5/minute")  # Max 5 attempts per minute per IP
async def login(request: Request, credentials: LoginRequest):
    return authenticate(credentials)
```

## Security Middleware

### CORS Configuration
- **Always:** Configure CORS with explicit allowlist of origins.
- **Rule:** Only allow origins hosting your frontend in production.
- **Rule:** Only allow necessary HTTP methods and headers.

```python
# app/middleware/security.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config import Settings

def add_security_middleware(app: FastAPI, settings: Settings):
    """Add security middleware to FastAPI application."""

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "Accept"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )

    # Trusted hosts middleware (production only)
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )
```

### Security Headers
- **Always:** Add security headers to protect against common attacks.
- **Rule:** Use HTTPS in production; redirect HTTP to HTTPS.

```python
# app/middleware/headers.py
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # HSTS (only over HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
```

### Per-Endpoint Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/auth/login")
@limiter.limit("5/minute")  # Strict for auth endpoints
async def login(request: Request, credentials: LoginForm):
    ...

@app.get("/api/data")
@limiter.limit("100/minute")  # Generous for data endpoints
async def get_data(request: Request):
    ...
```

**Rate limit tiers:**

- **Auth (login/register):** 5/minute — prevents brute force
- **Password reset:** 3/minute — prevents email spam
- **API reads:** 100/minute — normal usage
- **API writes:** 30/minute — prevents abuse
- **File upload:** 10/minute — resource-intensive

## Input Sanitization and Validation

### SQL Injection Prevention
- **Always:** Use parameterized queries with SQLAlchemy.
- **Never:** Concatenate user input directly into SQL strings.
- **Rule:** Validate and sanitize all user inputs (strip HTML tags using `bleach.clean()` or Pydantic validators).

```python
# CORRECT: Using SQLAlchemy ORM (automatically parameterized)
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email - safe from SQL injection."""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

# CORRECT: Using raw SQL with parameters
async def search_users(db: AsyncSession, search_term: str) -> List[User]:
    """Search users by name - parameterized query."""
    result = await db.execute(
        text("SELECT * FROM users WHERE full_name ILIKE :search"),
        {"search": f"%{search_term}%"}
    )
    return result.fetchall()

# INCORRECT: String concatenation (vulnerable to SQL injection)
async def bad_search_users(db: AsyncSession, search_term: str):
    """DO NOT USE - vulnerable to SQL injection."""
    query = f"SELECT * FROM users WHERE full_name LIKE '%{search_term}%'"
    result = await db.execute(text(query))  # DANGEROUS!
    return result.fetchall()
```

### Input Validation with Pydantic
- **Always:** Use Pydantic validators for complex validation logic.
- **Rule:** Sanitize inputs that will be displayed to users.

```python
# app/models/security.py
from pydantic import BaseModel, field_validator, Field, EmailStr
import re
from typing import Optional

class SecureUserInput(BaseModel):
    """Example of secure input validation."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    bio: Optional[str] = Field(None, max_length=500)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        # Only allow alphanumeric and underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()

    @field_validator('bio')
    @classmethod
    def sanitize_bio(cls, v: Optional[str]) -> Optional[str]:
        if v:
            # Remove potentially dangerous characters
            v = re.sub(r'[<>"\']', '', v)
            return v.strip()
        return v
```

## Production Security Hardening

### Deployment Security Checklist
- **Always:** Disable debug mode in production.
- **Always:** Hide API documentation in production.

```python
# app/main.py - Production security configuration
from app.config import get_settings
from app.middleware.security import add_security_middleware, SecurityHeadersMiddleware

def create_secure_app() -> FastAPI:
    """Create FastAPI app with production security settings."""
    settings = get_settings()

    # Production-specific FastAPI configuration
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.version,
        # Disable docs in production
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # Add security middleware
    add_security_middleware(app, settings)
    app.add_middleware(SecurityHeadersMiddleware)

    # Add rate limiting
    if not settings.debug:
        limiter = add_rate_limiting_middleware(app)

    return app
```

### Post-Execution Checklist

- [ ] CORS configured with explicit origin allowlist
- [ ] Security headers middleware active
- [ ] Rate limiting on auth and write endpoints
- [ ] All SQL queries use parameterized patterns
- [ ] Pydantic validation on all user inputs
- [ ] API docs disabled in production
- [ ] Debug mode disabled in production
