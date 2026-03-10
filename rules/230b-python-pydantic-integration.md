# Python Pydantic Integration and Performance

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:serialization, kw:model-dump, kw:type-adapter
**Keywords:** Pydantic, serialization, JSON schema, FastAPI integration, database ORM, TypeAdapter, performance, testing, model_dump, SecretStr
**TokenBudget:** ~3450
**ContextTier:** Medium
**Depends:** 230-python-pydantic.md

## Scope

**What This Rule Covers:**
Pydantic v2 serialization, JSON schema generation, FastAPI integration, database ORM patterns, performance optimization, and model testing.

**When to Load This Rule:**
- Implementing serialization with model_dump or model_validate
- Generating JSON schemas for API documentation
- Integrating Pydantic with FastAPI or database ORMs
- Optimizing validation performance for batch processing
- Writing tests for Pydantic models

## References

### Dependencies

**Must Load First:**
- **230-python-pydantic.md** - Core Pydantic model patterns

**Related:**
- **210-python-fastapi-core.md** - FastAPI endpoint patterns
- **206-python-pytest.md** - Pytest patterns
- **230a-python-pydantic-settings.md** - Settings management

## Contract

### Inputs and Prerequisites

- Pydantic v2 models (from 230-python-pydantic.md)
- FastAPI for API integration (optional)
- SQLAlchemy for database integration (optional)

### Mandatory

- **Always:** Use `model_dump()` for dictionary conversion (not `.dict()`)
- **Always:** Use `model_validate()` for object creation (not `.from_orm()`)
- **Rule:** Handle sensitive data appropriately during serialization (SecretStr, exclude)
- **Rule:** Use `ConfigDict(from_attributes=True)` for ORM conversion
- **Rule:** Log and count errors in batch processing (never silently skip)

### Forbidden

- Using Pydantic v1 methods (`.dict()`, `.from_orm()`, `.schema()`)
- Silent error swallowing in batch validation (`except ValidationError: continue`)
- Using plain dicts for `model_config` (use `ConfigDict(...)`)

### Execution Steps

1. Define serialization methods on models (to_public_dict, to_internal_dict)
2. Configure SecretStr for sensitive fields
3. Set up FastAPI response models with dependency injection
4. Configure ORM integration with from_attributes
5. Use TypeAdapter for batch validation with error tracking
6. Write tests covering valid and invalid data

### Output Format

Pydantic models with serialization, API integration, ORM support, and test coverage.

### Validation

**Pre-Task-Completion Checks:**
- [ ] model_dump() produces correct output for all use cases
- [ ] SecretStr fields excluded from serialization
- [ ] ORM models convert correctly with from_attributes
- [ ] Batch processing logs and counts errors

### Investigation Required

Before modifying serialization, integration, or performance patterns, agents MUST check:

- [ ] **Existing serialization helpers**: Search for `model_dump`, `to_dict`, `to_json` in the project — avoid creating duplicate serialization methods
- [ ] **ORM conversion patterns**: Search for `from_attributes` and `model_validate` to understand existing ORM-to-Pydantic conversion flow
- [ ] **Pydantic version**: Check `pyproject.toml` — if Pydantic v1, methods like `.dict()` and `.from_orm()` need migration to v2 equivalents
- [ ] **Batch processing code**: Search for `ValidationError` catch blocks to identify existing error handling patterns (especially silent `continue` anti-patterns)
- [ ] **API response models**: Check FastAPI routes for existing `response_model` usage and request/response model separation

### Design Principles

- **Never swallow errors:** Always log, count, or collect validation failures
- **Separate concerns:** Domain models vs. API schemas vs. ORM models
- **Use v2 API:** model_dump, model_validate, ConfigDict consistently

### Post-Execution Checklist

- [ ] Serialization methods handle sensitive data
- [ ] FastAPI integration uses response_model
- [ ] ORM conversion uses from_attributes
- [ ] Batch processing tracks errors
- [ ] Tests cover valid and invalid scenarios
- [ ] No Pydantic v1 patterns remain

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Silent Error Swallowing in Batch Processing

**Problem:** Using bare `except ValidationError: continue` silently drops invalid records with no visibility into data quality issues.

**Correct Pattern:** Track and report errors with logging and counts so data quality issues are visible.

```python
# Wrong: Silent error swallowing
def process_large_dataset(data_stream):
    for item in data_stream:
        try:
            yield EfficientModel.model_validate(item)
        except ValidationError:
            continue  # No logging, no counting, data silently lost

# Correct: Track and report errors
import logging
logger = logging.getLogger(__name__)

def process_large_dataset(data_stream):
    errors = []
    for i, item in enumerate(data_stream):
        try:
            yield EfficientModel.model_validate(item)
        except ValidationError as e:
            logger.warning("Skipping invalid record %d: %s", i, e.error_count())
            errors.append((i, e))
            continue
    if errors:
        logger.warning("Skipped %d invalid records out of total", len(errors))
```

### Anti-Pattern 2: Using Pydantic v1 API

**Problem:** Using deprecated v1 methods that will be removed in future versions.

**Correct Pattern:** Use Pydantic v2 API consistently: `model_dump()`, `model_validate()`, `model_json_schema()`, and `ConfigDict`.

```python
# Wrong: Pydantic v1 API (deprecated)
user_dict = user.dict()
user = User.from_orm(orm_obj)
schema = User.schema()
model_config = {"strict": True}   # Plain dict

# Correct: Pydantic v2 API
user_dict = user.model_dump()
user = User.model_validate(orm_obj)
schema = User.model_json_schema()
model_config = ConfigDict(strict=True)
```

## Serialization Patterns

### Model Serialization with Sensitive Data

```python
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from typing import Optional
from datetime import datetime, UTC

class UserProfile(BaseModel):
    """User profile with serialization control."""

    id: int
    username: str
    email: str = Field(..., alias="email_address")
    password_hash: SecretStr = Field(..., exclude=True)
    full_name: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True)

    def to_public_dict(self) -> dict:
        """Serialize for public API responses."""
        return self.model_dump(exclude={"password_hash", "email"}, by_alias=True)

    def to_internal_dict(self) -> dict:
        """Serialize for internal use."""
        return self.model_dump(exclude={"password_hash"})
```

### Custom Field Serialization

Use `@field_serializer` for per-field control over serialization output:

```python
from datetime import datetime, UTC
from pydantic import BaseModel, Field, field_serializer, ConfigDict

class AuditEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_type: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict = Field(default_factory=dict)

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime, _info) -> str:
        """ISO 8601 format with Z suffix for UTC."""
        return value.strftime("%Y-%m-%dT%H:%M:%SZ")

    @field_serializer("metadata")
    def serialize_metadata(self, value: dict, _info) -> dict:
        """Remove internal keys starting with underscore."""
        return {k: v for k, v in value.items() if not k.startswith("_")}

# event.model_dump() →
# {"event_type": "login", "created_at": "2026-03-09T14:30:00Z",
#  "metadata": {"ip": "10.0.0.1"}}  # _internal_id stripped
```

### Direct JSON Serialization

For JSON output, prefer `model_dump_json()` over `json.dumps(model_dump())` — it skips the intermediate dict and is faster:

```python
response = ApiResponse(status="ok", data={"user_id": 42})

# GOOD: Direct JSON string — faster, handles datetime automatically
json_str = response.model_dump_json(indent=2)

# GOOD: Selective JSON serialization
json_str = response.model_dump_json(exclude={"timestamp"})

# BAD: Intermediate dict step — slower, may need custom encoder for datetime
import json
json_str = json.dumps(response.model_dump(), default=str)  # Avoid this
```

### Direct JSON Deserialization

Use `model_validate_json()` to parse JSON strings directly:

```python
# GOOD: Direct from JSON string — faster, single-pass parsing
user = User.model_validate_json('{"username": "jane", "email": "jane@example.com"}')

# GOOD: From bytes (e.g., HTTP request body)
user = User.model_validate_json(request.body)

# BAD: Intermediate dict step — slower
import json
user = User.model_validate(json.loads(json_string))  # Avoid this
```

### JSON Schema Generation

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class APIResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"success": True, "message": "Operation completed", "data": {"id": 1}}]
        },
    )

    success: bool = Field(..., description="Whether request was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[dict] = Field(None, description="Response data")

schema = APIResponse.model_json_schema()
```

## FastAPI Integration

### Request/Response Models with Dependency Injection

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool

app = FastAPI()

def get_settings() -> AppSettings:
    """Dependency for accessing application settings."""
    return settings

@app.post("/users/", response_model=UserResponse)
async def create_user(
    user_data: UserCreateRequest,
    settings: AppSettings = Depends(get_settings),
):
    """Create a new user with validation."""
    return UserResponse(
        id=1, username=user_data.username,
        email=user_data.email, full_name=user_data.full_name, is_active=True,
    )
```

## Database Integration

### ORM Model Conversion

```python
from pydantic import BaseModel, ConfigDict

class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    is_active: bool

def get_user_by_id(user_id: int) -> UserSchema:
    user_orm = session.query(UserORM).filter(UserORM.id == user_id).first()
    return UserSchema.model_validate(user_orm)
```

## Performance Optimization

### TypeAdapter for Batch Validation

```python
from pydantic import BaseModel, ConfigDict, TypeAdapter
from typing import List

class StrictUser(BaseModel):
    model_config = ConfigDict(strict=True)
    id: int
    username: str
    email: str

UserList = TypeAdapter(List[StrictUser])

def validate_users_batch(users_data: list[dict]) -> list[StrictUser]:
    return UserList.validate_python(users_data)
```

### Memory-Efficient Models

```python
from pydantic import BaseModel, ConfigDict

class EfficientModel(BaseModel):
    model_config = ConfigDict(slots=True)

    id: int
    name: str
    value: float
```

## Testing Pydantic Models

### Model Testing Patterns

```python
import pytest
from pydantic import ValidationError

class TestUserModel:
    @pytest.fixture
    def valid_user_data(self):
        return {"id": 1, "email": "test@example.com", "username": "testuser"}

    def test_user_creation_success(self, valid_user_data):
        user = User(**valid_user_data)
        assert user.id == 1
        assert user.email == "test@example.com"

    def test_user_validation_errors(self):
        with pytest.raises(ValidationError):
            User(id=-1, email="invalid-email", username="ab")

    def test_user_serialization(self, valid_user_data):
        user = User(**valid_user_data)
        user_dict = user.model_dump()
        assert user_dict["email"] == "test@example.com"
```

## Computed Fields in Serialization

Use `@computed_field` to include derived values in `model_dump()` and JSON schema:

```python
from pydantic import BaseModel, Field, computed_field

class Invoice(BaseModel):
    items: list[dict] = Field(description="Line items with 'amount' key")
    tax_rate: float = Field(default=0.08, ge=0, le=1)

    @computed_field
    @property
    def subtotal(self) -> float:
        """Sum of all item amounts — included in serialization."""
        return sum(item.get("amount", 0) for item in self.items)

    @computed_field
    @property
    def tax(self) -> float:
        """Tax amount — included in serialization."""
        return round(self.subtotal * self.tax_rate, 2)

    @computed_field
    @property
    def total(self) -> float:
        """Grand total — included in serialization."""
        return round(self.subtotal + self.tax, 2)

invoice = Invoice(items=[{"desc": "Widget", "amount": 100}, {"desc": "Gadget", "amount": 50}])
invoice.model_dump()
# {"items": [...], "tax_rate": 0.08, "subtotal": 150.0, "tax": 12.0, "total": 162.0}
# ^^^ subtotal, tax, total are ALL included because of @computed_field
# Compare: plain @property would NOT appear in model_dump()
```

## JSON Schema Generation

Use `model_json_schema()` to generate OpenAPI-compatible schemas:

```python
from pydantic import BaseModel, Field

class CreateUserRequest(BaseModel):
    """Request body for creating a new user."""
    username: str = Field(
        min_length=3, max_length=50,
        json_schema_extra={"examples": ["jane_doe"]}
    )
    email: str = Field(
        pattern=r"^[\w.+-]+@[\w-]+\.[\w.]+$",
        json_schema_extra={"examples": ["jane@example.com"]}
    )
    role: str = Field(
        default="viewer",
        json_schema_extra={"enum": ["admin", "editor", "viewer"]}
    )

# Generate JSON Schema (for OpenAPI docs, Swagger UI, etc.)
schema = CreateUserRequest.model_json_schema()
# {
#   "title": "CreateUserRequest",
#   "description": "Request body for creating a new user.",
#   "properties": {
#     "username": {"type": "string", "minLength": 3, "maxLength": 50, ...},
#     ...
#   },
#   "required": ["username", "email"]
# }

# Customize schema generation mode:
schema_serial = CreateUserRequest.model_json_schema(mode="serialization")
schema_valid = CreateUserRequest.model_json_schema(mode="validation")
```

FastAPI automatically uses `model_json_schema()` for Swagger UI docs — `json_schema_extra` values appear as examples in the interactive documentation.
