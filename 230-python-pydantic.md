**Description:** Comprehensive Pydantic data validation patterns covering models, settings, serialization, and integration best practices for Python applications.
**AppliesTo:** `**/*.py`, `**/models/**/*`, `**/schemas/**/*`, `pyproject.toml`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-14

# Python Pydantic Data Validation Best Practices

## 1. Installation and Setup

### Dependencies and Environment
- **Requirement:** Use `uv` for dependency management following `@200-python-core.md` patterns
- **Requirement:** Install Pydantic with: `uv add pydantic` or `uv add "pydantic[email]"` for additional validators
- **Rule:** Use specific feature sets: `pydantic[email,dotenv]` for email validation and settings
- **Always:** Pin Pydantic to v2.x for modern features and performance

```toml
# pyproject.toml
[project]
dependencies = [
    "pydantic>=2.5.0",
    "pydantic[email]>=2.5.0",  # For email validation
    "pydantic-settings>=2.0.0",  # For settings management
]
```

### Project Structure for Pydantic Models
- **Rule:** Organize models in dedicated modules for maintainability
- **Rule:** Separate domain models from API schemas when using with FastAPI
- **Always:** Use clear naming conventions for different model types

```
project/
├── src/
│   └── myapp/
│       ├── models/              # Domain models
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── product.py
│       ├── schemas/             # API request/response schemas
│       │   ├── __init__.py
│       │   ├── user_schemas.py
│       │   └── api_models.py
│       └── config/
│           ├── __init__.py
│           └── settings.py      # Pydantic Settings
```

## 2. Model Definition Best Practices

### Basic Model Patterns
- **Rule:** Use `BaseModel` for data validation and serialization
- **Always:** Provide comprehensive type annotations for automatic validation
- **Rule:** Use descriptive field names and include docstrings for complex models

```python
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class User(BaseModel):
    """User model with comprehensive validation."""
    
    id: int = Field(..., gt=0, description="Unique user identifier")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    full_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=13, le=120, description="User age in years")
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list, max_items=10)
    
    class Config:
        # Enable validation on assignment
        validate_assignment = True
        # Use enum values in JSON
        use_enum_values = True
        # Example values for documentation
        schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "age": 30,
                "role": "user"
            }
        }
```

### Field Configuration and Validation
- **Rule:** Use `Field()` for complex validation constraints and metadata
- **Always:** Provide meaningful error messages for custom validators
- **Rule:** Use built-in validators before creating custom ones

```python
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional
import re

class Product(BaseModel):
    """Product model with custom validation."""
    
    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., regex=r'^[A-Z]{2,3}-\d{4,6}$')
    price: float = Field(..., gt=0, le=10000, description="Price in USD")
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    category: str = Field(..., min_length=1)
    
    @validator('name')
    def validate_name(cls, v):
        """Ensure product name doesn't contain prohibited words."""
        prohibited = ['test', 'sample', 'demo']
        if any(word in v.lower() for word in prohibited):
            raise ValueError('Product name cannot contain prohibited words')
        return v.title()
    
    @validator('sku')
    def validate_sku_format(cls, v):
        """Validate SKU format and check uniqueness."""
        if not re.match(r'^[A-Z]{2,3}-\d{4,6}$', v):
            raise ValueError('SKU must follow format: XX-NNNN or XXX-NNNNNN')
        return v.upper()
    
    @root_validator
    def validate_discount_logic(cls, values):
        """Ensure discount logic is consistent."""
        price = values.get('price')
        discount = values.get('discount_percent')
        
        if discount and discount > 0:
            if price and price < 10:  # No discount on items under $10
                raise ValueError('Discount not allowed on items under $10')
        
        return values
    
    @property
    def discounted_price(self) -> float:
        """Calculate price after discount."""
        if self.discount_percent:
            return self.price * (1 - self.discount_percent / 100)
        return self.price
```

## 3. Settings Management with Pydantic

### Application Settings Pattern
- **Rule:** Use `pydantic-settings` for configuration management
- **Always:** Support multiple configuration sources with clear precedence
- **Rule:** Validate all configuration values at startup

```python
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from pathlib import Path

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535)
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    database: str = Field(..., description="Database name")
    
    @property
    def url(self) -> str:
        """Generate database URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class AppSettings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False
    )
    
    # Application settings
    app_name: str = Field(default="MyApp", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", regex=r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$')
    
    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)
    
    # Security settings
    secret_key: str = Field(..., min_length=32, description="Secret key for encryption")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])
    
    # Database settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    
    # File paths
    data_dir: Path = Field(default=Path("./data"))
    log_file: Optional[Path] = Field(default=None)
    
    @validator('data_dir')
    def validate_data_dir(cls, v):
        """Ensure data directory exists."""
        v.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Ensure secret key is sufficiently complex."""
        if len(set(v)) < 10:  # At least 10 unique characters
            raise ValueError('Secret key must have sufficient entropy')
        return v

# Global settings instance
settings = AppSettings()
```

### Environment Variable Integration
- **Rule:** Use consistent environment variable naming with prefixes
- **Always:** Document all environment variables and their purposes
- **Rule:** Provide sensible defaults for development environments

```python
# Environment variables example:
# MYAPP_DEBUG=true
# MYAPP_LOG_LEVEL=DEBUG
# MYAPP_DATABASE__HOST=localhost
# MYAPP_DATABASE__PORT=5432
# MYAPP_SECRET_KEY=your-secret-key-here

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MYAPP_",
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    debug: bool = False
    database_url: str = Field(..., description="Database connection URL")
    redis_url: Optional[str] = Field(None, description="Redis connection URL")
```

## 4. Serialization and JSON Schema

### Model Serialization Patterns
- **Rule:** Use `model_dump()` for dictionary conversion with proper configuration
- **Always:** Handle sensitive data appropriately during serialization
- **Rule:** Use aliases for external API compatibility

```python
from pydantic import BaseModel, Field, SecretStr
from typing import Optional
from datetime import datetime

class UserProfile(BaseModel):
    """User profile with serialization control."""
    
    id: int
    username: str
    email: str = Field(..., alias="email_address")
    password_hash: SecretStr = Field(..., exclude=True)  # Never serialize
    full_name: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        populate_by_name = True  # Allow both field name and alias
    
    def to_public_dict(self) -> dict:
        """Serialize for public API responses."""
        return self.model_dump(
            exclude={'password_hash', 'email'},
            by_alias=True
        )
    
    def to_internal_dict(self) -> dict:
        """Serialize for internal use."""
        return self.model_dump(exclude={'password_hash'})

# Usage example
user = UserProfile(
    id=1,
    username="johndoe",
    email_address="john@example.com",
    password_hash="hashed_password",
    full_name="John Doe",
    created_at=datetime.now()
)

public_data = user.to_public_dict()
# {'id': 1, 'username': 'johndoe', 'full_name': 'John Doe', 'created_at': '...'}
```

### JSON Schema Generation
- **Rule:** Use Pydantic's JSON Schema generation for API documentation
- **Rule:** Provide examples and descriptions in schema

```python
class APIResponse(BaseModel):
    success: bool = Field(..., description="Whether request was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[dict] = Field(None, description="Response data")
    
    class Config:
        schema_extra = {
            "examples": [{
                "success": True,
                "message": "Operation completed",
                "data": {"id": 1}
            }]
        }

schema = APIResponse.model_json_schema()
```

## 5. Integration Patterns

### FastAPI Integration
- **Rule:** Use Pydantic models for request/response validation in FastAPI
- **Always:** Separate API schemas from domain models
- **Rule:** Use dependency injection for settings

```python
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List

# Request/Response schemas
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
    settings: AppSettings = Depends(get_settings)
):
    """Create a new user with validation."""
    # Business logic here
    return UserResponse(
        id=1,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        is_active=True
    )
```

### Database Integration
- **Rule:** Use separate Pydantic models for database operations
- **Rule:** Use `from_attributes = True` for ORM to Pydantic conversion

```python
class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True  # Enable ORM mode

def get_user_by_id(user_id: int) -> UserSchema:
    user_orm = session.query(UserORM).filter(UserORM.id == user_id).first()
    return UserSchema.model_validate(user_orm)
```

## 6. Performance and Optimization

### Validation Performance
- **Rule:** Use strict mode for better performance
- **Rule:** Use `TypeAdapter` for simple validation scenarios

```python
from pydantic import BaseModel, TypeAdapter
from typing import List

class StrictUser(BaseModel):
    model_config = {"strict": True}
    id: int
    username: str
    email: str

UserList = TypeAdapter(List[StrictUser])

def validate_users_batch(users_data: List[dict]) -> List[StrictUser]:
    return UserList.validate_python(users_data)
```

### Memory Optimization
- **Rule:** Use `slots = True` for memory-efficient models
- **Rule:** Use generators for large dataset processing

```python
class EfficientModel(BaseModel):
    class Config:
        slots = True
    
    id: int
    name: str
    value: float

def process_large_dataset(data_stream: Iterator[dict]) -> Iterator[EfficientModel]:
    for item in data_stream:
        try:
            yield EfficientModel.model_validate(item)
        except ValidationError:
            continue
```

## 7. Testing with Pydantic

### Model Testing Patterns
- **Rule:** Test both valid and invalid data scenarios
- **Rule:** Use pytest fixtures for reusable test data

```python
import pytest
from pydantic import ValidationError

class TestUserModel:
    @pytest.fixture
    def valid_user_data(self):
        return {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser"
        }
    
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
        assert user_dict['email'] == "test@example.com"
```

## Related Rules

- **`@200-python-core.md`** - Core Python patterns and uv usage
- **`@201-python-lint-format.md`** - Ruff linting and formatting standards
- **`@203-python-project-setup.md`** - Python project structure and packaging
- **`@210-python-fastapi-core.md`** - FastAPI integration patterns
- **`@800-project-changelog-rules.md`** - Changelog discipline for data model changes

## References and Resources

- [Pydantic Documentation](https://docs.pydantic.dev/latest/) - Official Pydantic documentation
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings management
- [FastAPI with Pydantic](https://fastapi.tiangolo.com/tutorial/body/) - FastAPI integration
- [Pydantic Performance](https://docs.pydantic.dev/latest/concepts/performance/) - Performance optimization

## Rule Type and Scope

- **Type:** Agent Requested (use `@230-python-pydantic.md` to apply)
- **Scope:** Python data validation, model definition, settings management
- **Applies to:** Data models, API schemas, configuration management, validation logic
- **Validation:** Model testing, schema validation, performance testing
