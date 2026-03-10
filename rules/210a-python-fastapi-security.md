# FastAPI Security Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:fastapi-security, kw:oauth, kw:jwt, kw:rbac
**Keywords:** FastAPI security, authentication, OAuth2, JWT, API keys, bcrypt, HTTPBearer, role-based access control, RBAC, token refresh, password hashing
**TokenBudget:** ~3800
**ContextTier:** High
**Depends:** 210-python-fastapi-core.md

## Scope

**What This Rule Covers:**
Authentication and authorization patterns for FastAPI applications. Covers JWT token authentication, OAuth2 password flow, password hashing (bcrypt), role-based access control (RBAC), token refresh, and secrets management. For CORS, security headers, rate limiting, and input validation, see **210e-python-fastapi-security-hardening.md**.

**When to Load This Rule:**
- Implementing authentication and authorization in FastAPI
- Securing FastAPI endpoints with JWT tokens
- Setting up role-based access control (RBAC)
- Managing JWT token lifecycle (creation, validation, refresh)
- Configuring password hashing and secrets

## References

### Dependencies

**Must Load First:**
- **210-python-fastapi-core.md** - FastAPI foundation patterns

**Related:**
- **200-python-core.md** - Python core patterns
- **210e-python-fastapi-security-hardening.md** - CORS, headers, rate limiting, input validation
- **210b-python-fastapi-testing.md** - Testing security implementations

### External Documentation

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

## Contract

### Inputs and Prerequisites

- FastAPI application structure
- User authentication requirements
- RBAC requirements and role definitions
- Environment configuration system
- Understanding of OAuth2/JWT patterns

### Mandatory

- `passlib` for password hashing (bcrypt) — or direct `bcrypt` library
- `python-jose` or `pyjwt` for JWT tokens
- `fastapi.security` modules (HTTPBearer, OAuth2PasswordBearer)
- Environment variables for secrets (no defaults for secret keys)

### Forbidden

- Hardcoding secrets in source code
- Storing plaintext passwords
- JWT secrets with default/fallback values
- Using access tokens as refresh tokens (check `type` claim)

### Execution Steps

1. Set up password hashing with bcrypt via passlib (or direct bcrypt)
2. Implement JWT token generation and validation
3. Implement token refresh with access/refresh token pair
4. Create authentication dependencies (get_current_user)
5. Implement role-based access control via dependency injection
6. Move all secrets to environment variables (no defaults)
7. Validate with security testing (auth flows, RBAC)
8. Apply hardening from **210e-python-fastapi-security-hardening.md**

### Output Format

Secured FastAPI application with:
- Bcrypt password hashing
- JWT authentication with HTTPBearer
- Token refresh with access/refresh pair
- RBAC via dependency injection
- Environment-based secrets management

### Validation

**Pre-Task-Completion Checks:**
- Password hashing configured with bcrypt (passlib or direct)
- JWT authentication implemented with HTTPBearer
- Token refresh endpoint with type validation
- Authentication dependencies implemented
- RBAC dependencies created via dependency injection
- All secrets stored in environment variables (no defaults)
- No hardcoded secrets in codebase

**Success Criteria:**
- Passwords never stored in plaintext
- JWT tokens validated on protected endpoints
- Token refresh works with type claim validation
- Unauthorized requests return 401
- Forbidden requests return 403 (RBAC)
- No secrets in source code or git history

**Negative Tests:**
- Invalid JWT token rejected with 401
- Missing role returns 403
- Access token rejected at refresh endpoint
- Hardcoded secrets trigger security scan alerts

### Design Principles

1. **Authentication First** - Implement proper JWT-based authentication with secure token handling
2. **Authorization Controls** - Use dependency injection for role-based access control
3. **Password Security** - Hash passwords with bcrypt; never store plaintext credentials
4. **Token Lifecycle** - Implement access/refresh token pairs with proper expiration
5. **Environment Secrets** - Store all secrets in environment variables, never in code
6. **Fail-Fast Secrets** - No default values for secret keys; app must fail at startup if missing

### Post-Execution Checklist

- [ ] Password hashing uses bcrypt (passlib or direct)
- [ ] JWT authentication with HTTPBearer on protected endpoints
- [ ] Token refresh endpoint with type claim validation
- [ ] RBAC dependencies enforce role checks
- [ ] All secrets loaded from environment variables (no defaults)
- [ ] No hardcoded secrets in codebase
- [ ] Hardening applied from 210e

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
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    secret_key: str
    database_url: str

settings = Settings()  # Fails fast if secrets missing
```

### Anti-Pattern 2: Missing Input Validation on User Data

**Problem:** Accepting user input without validation allows injection attacks and data corruption.

**Why It Fails:** Unvalidated input can contain malicious payloads, exceed expected lengths, or have unexpected types that break downstream processing.

**Correct Pattern:**
```python
# BAD: No validation on user input
@app.post("/users")
async def create_user(data: dict):
    return db.insert(data)  # Accepts anything!

# GOOD: Pydantic model with constraints
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    age: int = Field(ge=0, le=150)

@app.post("/users")
async def create_user(data: UserCreate):
    return db.insert(data.model_dump())  # Validated and typed
```

> **Investigation Required**
> When applying this rule:
> 1. **Read existing auth implementation BEFORE adding security** - Check for auth_service.py, security.py, existing JWT patterns
> 2. **Verify environment variable usage** - Check .env files, config.py for how secrets are currently loaded
> 3. **Never speculate about auth requirements** - Ask user about authentication needs, or check existing patterns
> 4. **Check existing auth setup** - Read main.py to see what authentication is already configured
> 5. **Make grounded recommendations based on investigated security setup** - Match existing patterns
>
> **Anti-Pattern:**
> "Based on typical FastAPI apps, you probably need JWT authentication..."
>
> **Correct Pattern:**
> "Let me check your existing authentication setup first."
> [reads auth_service.py, main.py, checks for HTTPBearer usage]
> "I see you're using passlib with bcrypt and HTTPBearer for JWT auth. Here's how to add role-based access control following the same pattern..."

## Authentication Setup

### JWT Token Authentication
- **Always:** Implement JWT-based authentication using HTTPBearer for protected endpoints.
- **Always:** Use JWT tokens with appropriate expiration times.
- **Rule:** Never store passwords in plain text; use proper hashing.

```python
# app/services/auth_service.py
# passlib — widely used but maintenance status uncertain as of 2024+
# Alternative: use bcrypt directly if passlib becomes unmaintained
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, UTC
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Optional
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = settings.jwt_secret_key
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

**Direct bcrypt alternative** (no passlib dependency):

```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

> **Note:** Monitor passlib's PyPI page for maintenance updates. If passlib is abandoned, migrate to direct `bcrypt` library.

### Token Refresh Pattern

```python
from datetime import UTC, datetime, timedelta

def create_token_pair(user_id: str) -> dict[str, str]:
    """Create access + refresh token pair."""
    access = create_access_token(
        data={"sub": user_id, "type": "access"},
        expires_delta=timedelta(minutes=30),
    )
    refresh = create_access_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=7),
    )
    return {"access_token": access, "refresh_token": refresh}


@app.post("/auth/refresh")
async def refresh_token(refresh_token: str = Body(...)):
    """Exchange refresh token for new access token."""
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
    if payload.get("type") != "refresh":
        raise HTTPException(401, "Invalid token type")
    user_id = payload.get("sub")
    return create_token_pair(user_id)
```

**Rules:**
- Access tokens: short-lived (15-30 minutes)
- Refresh tokens: longer-lived (7-30 days)
- Always check `type` claim to prevent access tokens being used as refresh
- Rotate refresh tokens on each use (return new pair)

### Login and Registration Endpoints
- **Always:** Validate credentials thoroughly before issuing tokens.
- **Always:** Return consistent error messages to prevent user enumeration.
- **Rule:** Rate limit authentication endpoints to prevent brute force attacks (e.g., 5 requests/minute/IP for login).

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

## Authorization and Access Control

### Role-Based Access Control
- **Always:** Implement role-based permissions using dependency injection.
- **Always:** Check permissions at the endpoint level, not in business logic.
- **Rule:** Use `{resource}:{action}` format for permission names (e.g., `users:delete`, `posts:create`).

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

## Environment and Configuration Security

### Secure Configuration Management
- **Always:** Store secrets in environment variables or secure vaults.
- **Rule:** Use different configurations for development, staging, and production.
- **Never:** Commit secrets to version control.

```python
# app/config/security.py
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict

class SecuritySettings(BaseSettings):
    """Security-focused configuration settings."""
    model_config = ConfigDict(env_prefix="SECURITY_", env_file=".env")

    # JWT Configuration — NO defaults for secrets
    jwt_secret_key: str  # Required — MUST be set, fails at startup if missing
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 7

    # Password Configuration
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_numbers: bool = True

    @field_validator('jwt_secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError('JWT secret key must be at least 32 characters long')
        return v
```

**Rule:** JWT secrets MUST NOT have default values. Use `BaseSettings` with no default (raises `ValidationError`) or `os.environ["KEY"]` (raises `KeyError`) to fail-fast at startup.

```python
# WRONG — has a default value (security vulnerability)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
SECRET_KEY = secrets.token_urlsafe(32)  # Generates new key on every restart!

# CORRECT — no default, fails fast
SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # Raises KeyError if not set
```

For CORS, security headers, rate limiting, input validation, and production hardening, see **210e-python-fastapi-security-hardening.md**.
