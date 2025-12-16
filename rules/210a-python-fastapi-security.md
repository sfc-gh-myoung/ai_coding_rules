# FastAPI Security Patterns

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** FastAPI security, authentication, OAuth2, JWT, CORS, middleware, API keys, security best practices, bcrypt, HTTPBearer, role-based access control, RBAC
**TokenBudget:** ~2650
**ContextTier:** High
**Depends:** rules/210-python-fastapi-core.md

## Purpose
Establish comprehensive security practices for FastAPI applications including authentication, authorization, CORS configuration, and security middleware to protect APIs and user data.

## Rule Scope

FastAPI security patterns for authentication, authorization, CORS, and security middleware

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use bcrypt for password hashing** - `passlib.context.CryptContext(schemes=["bcrypt"])`
- **JWT tokens with HTTPBearer** - Use `fastapi.security.HTTPBearer()` for token auth
- **Environment variables for secrets** - Never hardcode `SECRET_KEY`, `DATABASE_URL`
- **Dependency injection for RBAC** - Create `get_current_user`, `require_role` dependencies
- **Configure CORS properly** - Specify allowed origins, methods, headers explicitly
- **Disable docs in production** - Set `docs_url=None`, `redoc_url=None` when `ENV=production`
- **Never store plaintext passwords** - Always hash with bcrypt before database storage

**Quick Checklist:**
- [ ] Passwords hashed with bcrypt (passlib)
- [ ] JWT authentication with HTTPBearer
- [ ] All secrets in environment variables
- [ ] RBAC implemented via dependency injection
- [ ] CORS configured with explicit origins
- [ ] Rate limiting middleware configured
- [ ] Docs disabled in production

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
1. **Authentication First** - Implement proper JWT-based authentication with secure token handling
2. **Authorization Controls** - Use dependency injection for role-based access control
3. **Password Security** - Hash passwords with bcrypt; never store plaintext credentials
4. **CORS Configuration** - Configure cross-origin requests appropriately for your environment
5. **Security Middleware** - Layer security controls with trusted hosts and rate limiting
6. **Environment Secrets** - Store all secrets in environment variables, never in code
7. **Production Hardening** - Disable debug features and docs in production environments
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Hardcoded Secrets in Application Code

**Problem:** Embedding API keys, database passwords, or JWT secrets directly in source code or configuration files committed to version control.

**Why It Fails:** Secrets exposed in git history forever, even after deletion. Rotating credentials requires code changes and redeployment. Secrets leaked to anyone with repo access. Violates security compliance requirements.

**Correct Pattern:**
```python
# BAD: Hardcoded secrets
SECRET_KEY = "super-secret-jwt-key-12345"
DATABASE_URL = "postgresql://admin:password123@prod-db:5432/app"

# GOOD: Environment variables with validation
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()  # Fails fast if secrets missing
```

### Anti-Pattern 2: Overly Permissive CORS Configuration

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
> 1. **Read existing auth implementation BEFORE adding security** - Check for auth_service.py, security.py, existing JWT patterns
> 2. **Verify environment variable usage** - Check .env files, config.py for how secrets are currently loaded
> 3. **Never speculate about CORS requirements** - Ask user about allowed origins, or check existing middleware
> 4. **Check existing middleware stack** - Read main.py to see what security middleware is already configured
> 5. **Make grounded recommendations based on investigated security setup** - Match existing patterns
>
> **Anti-Pattern:**
> "Based on typical FastAPI apps, you probably need JWT authentication..."
> "Let me add CORS middleware - it should work with standard settings..."
>
> **Correct Pattern:**
> "Let me check your existing authentication setup first."
> [reads auth_service.py, main.py, checks for HTTPBearer usage]
> "I see you're using passlib with bcrypt and HTTPBearer for JWT auth. Here's how to add role-based access control following the same pattern..."

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
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [Passlib Documentation](https://passlib.readthedocs.io/)
- [Python-JOSE](https://python-jose.readthedocs.io/)
- [Pydantic v2 Validators](https://docs.pydantic.dev/latest/concepts/validators/)

### Related Rules
- **FastAPI Core**: `rules/210-python-fastapi-core.md`
- **FastAPI Testing**: `rules/210b-python-fastapi-testing.md`
- **FastAPI Deployment**: `rules/210c-python-fastapi-deployment.md`

## 1. Authentication Setup

### JWT Token Authentication
- **Always:** Implement proper authentication for protected endpoints.
- **Always:** Use JWT tokens with appropriate expiration times.
- **Rule:** Never store passwords in plain text; use proper hashing.

```python
# app/services/auth_service.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = "your-secret-key"  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash using bcrypt."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token with expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(security)):
    """Extract and validate current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Fetch user from database
    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user
```

### Login and Registration Endpoints
- **Always:** Validate credentials thoroughly before issuing tokens.
- **Always:** Return consistent error messages to prevent user enumeration.
- **Rule:** Rate limit authentication endpoints to prevent brute force attacks.

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import authenticate_user, create_access_token
from app.models.auth import Token, UserCreate, UserResponse
from datetime import timedelta

router = APIRouter()

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return access token."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register new user account."""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    user = await create_user(db, user_data, hashed_password)
    return user
```

## 2. Authorization and Access Control

### Role-Based Access Control
- **Always:** Implement role-based permissions using dependency injection.
- **Always:** Check permissions at the endpoint level, not in business logic.
- **Rule:** Use clear, descriptive permission names.

```python
# app/dependencies/auth.py
from fastapi import Depends, HTTPException, status
from app.services.auth_service import get_current_user
from app.models.user import User
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

def require_role(required_role: UserRole):
    """Dependency factory for role-based access control."""
    def check_role(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return check_role

def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role for access."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_active_user(current_user: User = Depends(get_current_user)):
    """Require active user account."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    return current_user

# Usage in routes
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete user - admin only."""
    await delete_user_by_id(db, user_id)
    return {"message": "User deleted successfully"}
```

## 3. Security Middleware

### CORS Configuration
- **Always:** Configure CORS properly for your use case.
- **Rule:** Be restrictive with allowed origins in production.
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
        allow_headers=["*"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )

    # Trusted hosts middleware (production only)
    if not settings.debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_hosts
        )

def add_rate_limiting_middleware(app: FastAPI):
    """Add rate limiting middleware (example with slowapi)."""
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    return limiter
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

## 4. Input Sanitization and Validation

### SQL Injection Prevention
- **Always:** Use parameterized queries with SQLAlchemy.
- **Never:** Concatenate user input directly into SQL strings.
- **Rule:** Validate and sanitize all user inputs.

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

## 5. Environment and Configuration Security

### Secure Configuration Management
- **Always:** Store secrets in environment variables or secure vaults.
- **Rule:** Use different configurations for development, staging, and production.
- **Never:** Commit secrets to version control.

```python
# app/config/security.py
from pydantic import BaseSettings, field_validator, ConfigDict
from typing import List
import secrets

class SecuritySettings(BaseSettings):
    """Security-focused configuration settings."""
    model_config = ConfigDict(env_prefix="SECURITY_", env_file=".env")

    # JWT Configuration
    jwt_secret_key: str = secrets.token_urlsafe(32)
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    # Password Configuration
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = False

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600  # 1 hour

    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    cors_credentials: bool = True

    # Security Headers
    enable_security_headers: bool = True
    hsts_max_age: int = 31536000  # 1 year

    @field_validator('jwt_secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError('JWT secret key must be at least 32 characters long')
        return v

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
```

## 6. Production Security Hardening

### Deployment Security Checklist
- **Always:** Disable debug mode in production.
- **Always:** Hide API documentation in production.
- **Rule:** Use environment-specific security configurations.

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

        # Apply rate limiting to auth endpoints
        @app.middleware("http")
        async def rate_limit_auth(request: Request, call_next):
            if request.url.path.startswith("/auth/"):
                # More restrictive rate limiting for auth endpoints
                pass
            response = await call_next(request)
            return response

    return app
```
