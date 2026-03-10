# Python Pydantic Data Validation Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:pydantic, kw:validation, kw:basemodel
**Keywords:** Pydantic, data validation, models, BaseModel, field validation, Field, validator, model_validator, EmailStr
**TokenBudget:** ~3800
**ContextTier:** High
**Depends:** 200-python-core.md

## Scope

**What This Rule Covers:**
Model definition and field validation patterns using Pydantic v2, covering BaseModel design, Field() constraints, custom validators, and anti-patterns.

**When to Load This Rule:**
- Defining Pydantic models for data validation
- Adding field constraints and custom validators
- Setting up a Pydantic-based project structure

## References

### External Documentation
- [Pydantic Documentation](https://docs.pydantic.dev/latest/) - Complete guide to data validation and serialization
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Configuration management

### Related Rules
- **200-python-core.md** - Core Python patterns and uv usage
- **201-python-lint-format.md** - Ruff linting and formatting standards
- **230a-python-pydantic-settings.md** - Settings management with pydantic-settings
- **230b-python-pydantic-integration.md** - Serialization, FastAPI, database, performance, testing

## Contract

### Inputs and Prerequisites

- Python project with `pyproject.toml` configured
- Understanding of type annotations and Python typing

### Mandatory

- **Always:** Use `pydantic>=2.5.0` installed via `uv add pydantic`
- **Always:** Type annotations on all model fields
- **Rule:** Validation rules defined using Field() or validators
- **Rule:** Use `ConfigDict(...)` for model configuration (not plain dicts)

### Forbidden

- Using Pydantic v1 patterns (deprecated)
- Returning raw dictionaries instead of Pydantic models in APIs
- Validation logic outside Pydantic models
- Skipping field validation for user input
- Using mutable default values without default_factory
- Side-effects in validators (file I/O, network calls, directory creation)

### Execution Steps

1. Install Pydantic with required extras: `uv add "pydantic[email]"` or `uv add pydantic-settings`
2. Define BaseModel classes with comprehensive type annotations
3. Add Field() constraints for validation rules (min_length, max_length, ge, le, pattern)
4. Implement custom validators using @field_validator or @model_validator decorators
5. Configure model settings using ConfigDict (from_attributes, validate_assignment)
6. Test models with valid and invalid data using pytest
7. Validate with: `uvx ruff check .` and `uv run pytest tests/`

### Output Format

Python modules containing:
- BaseModel classes with type-annotated fields
- Field() definitions with validation constraints
- Custom validators with clear error messages
- Comprehensive docstrings explaining model purpose and fields

### Validation

**Pre-Task-Completion Checks:**
- All model fields have type annotations
- Field() constraints match business requirements
- Custom validators raise ValueError with descriptive messages
- Models serialize/deserialize correctly (model_dump, model_validate)

**Success Criteria:**
- `uvx ruff check .` passes with zero errors
- `uv run pytest tests/` passes all model validation tests
- Invalid data raises ValidationError with clear messages

### Design Principles

- **Validators should validate, not mutate:** Never create files, directories, or make network calls in validators
- **Fail fast:** Raise clear errors at model creation time
- **Reuse:** Prefer built-in Field constraints over custom validators

### Post-Execution Checklist

- [ ] Pydantic v2 installed with required extras
- [ ] All models inherit from BaseModel
- [ ] Field validation constraints defined
- [ ] Custom validators implemented where needed
- [ ] ConfigDict used consistently (no plain dicts)
- [ ] Tests cover valid and invalid data scenarios
- [ ] Linting and tests pass

### Investigation Required

Before creating or modifying Pydantic models, agents MUST check:

- [ ] **Existing models**: Search for `class.*BaseModel` in the project to find existing Pydantic models and avoid duplication
- [ ] **Pydantic version**: Check `pyproject.toml` for current Pydantic version — if v1, migration is needed before applying v2 patterns
- [ ] **Model organization**: Identify existing directory structure (models/, schemas/, types/) to place new models consistently
- [ ] **Installed extras**: Check if `pydantic[email]` is already installed — avoid duplicate dependency declarations
- [ ] **Existing validators**: Search for `@field_validator` and `@model_validator` to understand current validation patterns

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Using Dict Instead of Pydantic Models for API Responses

**Problem:** Returning raw dictionaries from API endpoints instead of Pydantic models, losing type safety and automatic serialization.

**Why It Fails:** No compile-time type checking. Typos in field names not caught until runtime. No automatic JSON serialization of complex types (datetime, UUID). Missing OpenAPI schema generation.

**Correct Pattern:**
```python
# BAD: Raw dict responses
@app.get("/users/{user_id}")
async def get_user(user_id: int) -> dict:
    user = db.get_user(user_id)
    return {"id": user.id, "name": user.name, "created": str(user.created_at)}

# GOOD: Pydantic response model
class UserResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int) -> UserResponse:
    return UserResponse.model_validate(db.get_user(user_id))
```

### Anti-Pattern 2: Validation Logic Outside Pydantic Models

**Problem:** Performing validation in route handlers or service layers instead of using Pydantic validators, scattering validation logic throughout the codebase.

**Correct Pattern:**
```python
# BAD: Validation in route handler
@app.post("/users")
async def create_user(data: dict):
    if not data.get("email") or "@" not in data["email"]:
        raise HTTPException(400, "Invalid email")

# GOOD: Validation in Pydantic model
class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

@app.post("/users")
async def create_user(data: UserCreate):  # Auto-validated
    return create_user_in_db(data)
```

### Anti-Pattern 3: Side-Effects in Validators

**Problem:** Validators that create directories, write files, or make network calls. Validators should only validate and transform data.

```python
# BAD: Creates directories during validation
@field_validator("data_dir")
@classmethod
def validate_data_dir(cls, v: Path) -> Path:
    v.mkdir(parents=True, exist_ok=True)  # Side-effect!
    return v

# GOOD: Validate only; create directories at application startup
@field_validator("data_dir")
@classmethod
def validate_data_dir(cls, v: Path) -> Path:
    if not v.parent.exists():
        raise ValueError(f"Parent directory does not exist: {v.parent}")
    return v
# Call settings.data_dir.mkdir(parents=True, exist_ok=True) at startup
```

## Output Format Examples

```python
from datetime import datetime, UTC
from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field

class OrderItem(BaseModel):
    """Example Pydantic v2 model with common patterns."""

    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        json_schema_extra={"example": {"sku": "AB-1234", "quantity": 2, "unit_price": 19.99}},
    )

    sku: str = Field(..., pattern=r'^[A-Z]{2,3}-\d{4,6}$')
    quantity: int = Field(..., gt=0, le=1000)
    unit_price: float = Field(..., gt=0)
    ordered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, v: str) -> str:
        return v.upper()

    # @computed_field includes the field in model_dump() and JSON schema
    # Unlike @property, computed fields appear in serialization output
    @computed_field
    @property
    def total(self) -> float:
        """Total price — included in serialization."""
        return self.quantity * self.unit_price
        # item.model_dump() → {"sku": "AB-1234", ..., "total": 39.98}
```

## Installation and Setup

### Dependencies and Environment
- **Requirement:** Use `uv` for dependency management following `200-python-core.md` patterns
- **Requirement:** Install Pydantic with: `uv add pydantic` or `uv add "pydantic[email]"` for additional validators
- **Rule:** Use specific feature sets: `pydantic[email]` for email validation
- **Always:** Pin Pydantic to v2.x for modern features and performance

```toml
# pyproject.toml
[project]
dependencies = [
    "pydantic>=2.5.0",
    "pydantic[email]>=2.5.0",
]
```

### Project Structure for Pydantic Models
- **Rule:** Organize models in dedicated modules for maintainability
- **Rule:** Separate domain models from API schemas when using with FastAPI

Directory structure for `project/`:
- **src/myapp/** - Source package
  - **models/** - Domain models: `__init__.py`, `user.py`, `product.py`
  - **schemas/** - API request/response schemas: `__init__.py`, `user_schemas.py`
  - **config/** - Configuration: `__init__.py`, `settings.py`

## Model Definition Best Practices

### Basic Model Patterns
- **Rule:** Use `BaseModel` for data validation and serialization
- **Always:** Provide comprehensive type annotations for automatic validation
- **Rule:** Use descriptive field names and include docstrings for complex models

```python
from datetime import datetime, UTC
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, EmailStr
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class User(BaseModel):
    """User model with comprehensive validation."""

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "age": 30,
                "role": "user",
            }
        },
    )

    id: int = Field(..., gt=0, description="Unique user identifier")
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_]+$')
    full_name: Optional[str] = Field(None, max_length=100)
    age: Optional[int] = Field(None, ge=13, le=120, description="User age in years")
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tags: List[str] = Field(default_factory=list, max_length=10)
```

### Field Configuration and Validation
- **Rule:** Use `Field()` for complex validation constraints and metadata
- **Always:** Provide meaningful error messages for custom validators
- **Rule:** Use built-in validators before creating custom ones

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional

class Product(BaseModel):
    """Product model with custom validation."""

    name: str = Field(..., min_length=1, max_length=200)
    sku: str = Field(..., pattern=r'^[A-Z]{2,3}-\d{4,6}$')
    price: float = Field(..., gt=0, le=10000, description="Price in USD")
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    category: str = Field(..., min_length=1)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure product name doesn't contain prohibited words."""
        prohibited = ['test', 'sample', 'demo']
        if any(word in v.lower() for word in prohibited):
            raise ValueError('Product name cannot contain prohibited words')
        return v.title()

    @model_validator(mode='before')
    @classmethod
    def validate_discount_logic(cls, values: dict) -> dict:
        """Ensure discount logic is consistent."""
        price = values.get('price')
        discount = values.get('discount_percent')
        if discount and discount > 0 and price and price < 10:
            raise ValueError('Discount not allowed on items under $10')
        return values
```

## Nested Models

Pydantic supports model composition — use nested models for structured data:

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class Address(BaseModel):
    """Mailing or billing address."""
    street: str = Field(min_length=1, max_length=200)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=2, pattern=r"^[A-Z]{2}$")
    zip_code: str = Field(pattern=r"^\d{5}(-\d{4})?$")
    country: str = Field(default="US", max_length=2)

class Customer(BaseModel):
    """Customer with multiple addresses."""
    model_config = ConfigDict(from_attributes=True)

    name: str = Field(min_length=1, max_length=100)
    billing_address: Address
    shipping_addresses: List[Address] = Field(default_factory=list)
    primary_phone: Optional[str] = Field(
        default=None, pattern=r"^\+?1?\d{10,15}$"
    )

# Nested models validate recursively:
customer = Customer(
    name="Jane Doe",
    billing_address={"street": "123 Main St", "city": "Portland",
                     "state": "OR", "zip_code": "97201"},
    shipping_addresses=[
        {"street": "456 Oak Ave", "city": "Seattle",
         "state": "WA", "zip_code": "98101"}
    ]
)
# customer.billing_address is an Address instance, not a dict
```

## Discriminated Unions

Use discriminated unions for polymorphic data with a type field:

```python
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Union

class CreditCardPayment(BaseModel):
    payment_type: Literal["credit_card"]
    card_number: str = Field(pattern=r"^\d{16}$")
    expiry: str = Field(pattern=r"^\d{2}/\d{2}$")
    cvv: str = Field(pattern=r"^\d{3,4}$")

class BankTransferPayment(BaseModel):
    payment_type: Literal["bank_transfer"]
    routing_number: str = Field(pattern=r"^\d{9}$")
    account_number: str = Field(min_length=8, max_length=17)

class CryptoPayment(BaseModel):
    payment_type: Literal["crypto"]
    wallet_address: str = Field(min_length=26, max_length=62)
    network: str = Field(pattern=r"^(ethereum|bitcoin|solana)$")

# Discriminator selects the right model based on payment_type:
Payment = Annotated[
    Union[CreditCardPayment, BankTransferPayment, CryptoPayment],
    Field(discriminator="payment_type")
]

class Order(BaseModel):
    order_id: str
    payment: Payment  # Validates against correct submodel automatically
```

## Custom Types with Annotated Validators

Use `Annotated` with `BeforeValidator` / `AfterValidator` for reusable type-level validation:

```python
from typing import Annotated
from pydantic import BaseModel, AfterValidator, BeforeValidator

def strip_whitespace(v: str) -> str:
    """Pre-process: strip leading/trailing whitespace."""
    return v.strip()

def validate_not_empty(v: str) -> str:
    """Post-process: ensure string is not empty after stripping."""
    if not v:
        raise ValueError("Value must not be empty or whitespace-only")
    return v

# Reusable custom type — use across multiple models:
CleanString = Annotated[str, BeforeValidator(strip_whitespace), AfterValidator(validate_not_empty)]

def normalize_email(v: str) -> str:
    """Normalize email to lowercase."""
    return v.lower().strip()

NormalizedEmail = Annotated[str, BeforeValidator(normalize_email)]

class ContactForm(BaseModel):
    name: CleanString  # Strips whitespace, rejects empty
    email: NormalizedEmail  # Lowercases and strips
    message: CleanString
```
