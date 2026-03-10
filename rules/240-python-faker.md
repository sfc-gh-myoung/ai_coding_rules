# Python Faker Data Generation Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:faker, kw:test-data, kw:mock
**Keywords:** Faker, test data generation, fake data, providers, synthetic data, seeding, deterministic testing, Python testing
**TokenBudget:** ~3300
**ContextTier:** Low
**Depends:** 200-python-core.md

## Scope

**What This Rule Covers:**
Core patterns for generating realistic test data using Python's Faker library, covering setup, providers, seeding, and data generation classes.

**When to Load This Rule:**
- Generating test data for Python applications
- Creating synthetic datasets for development
- Setting up Faker with proper seeding

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Core Python patterns and uv usage

**Related:**
- **201-python-lint-format.md** - Ruff linting and formatting standards
- **230-python-pydantic.md** - Pydantic integration for data validation
- **240a-python-faker-testing.md** - Pytest fixtures, Factory Boy, seeding strategies
- **240b-python-faker-advanced.md** - Localization, custom providers, performance

### External Documentation
- [Faker Documentation](https://faker.readthedocs.io/en/stable/) - Comprehensive guide to fake data generation
- [pytest-faker Plugin](https://pypi.org/project/pytest-faker/) - Pytest fixtures and integration patterns
- [Factory Boy](https://factoryboy.readthedocs.io/) - Object factory patterns for complex test data

## Contract

### Inputs and Prerequisites

Python 3.11+, faker library, understanding of test data generation patterns

### Mandatory

- **Always:** Seed Faker instances for reproducible test data
- **Rule:** Use specific providers for type-safe data generation
- **Rule:** Use `seed_instance()` for per-instance seeding (not `Faker.seed()` which is global)

### Forbidden

- Non-deterministic test data without seeding
- Using Faker in production code
- Generating unrealistic data that bypasses validation
- Hardcoding large datasets of test data when Faker would be more maintainable (boundary values and specific assertion values should use literals)

### Execution Steps

1. Install Faker with uv: `uv add --group dev faker`
2. Seed Faker instances for reproducible test data
3. Use specific providers for type-safe data generation
4. Create pytest fixtures for reusable fake data (see 240a)
5. Implement custom providers for domain-specific data (see 240b)
6. Validate with: `uvx ruff check .` and `uv run pytest tests/`

### Output Format

Deterministic, realistic test data with proper seeding, reusable pytest fixtures, custom providers for domain models.

### Validation

**Pre-Task-Completion Checks:**
- faker added to dev dependencies
- Faker seeded in tests (prefer `seed_instance()` over `Faker.seed()`)
- Custom providers defined for domain models
- pytest fixtures created for reusable instances

**Success Criteria:**
- Test data is reproducible (same seed produces same data)
- Fake data matches domain constraints
- No Faker usage in production code

**Negative Tests:**
- Non-seeded Faker (should produce different data each run)
- Unrealistic data (should fail validation)
- Production code using Faker (should be flagged in review)

### Design Principles

- **Deterministic Testing:** Always seed Faker for reproducible test data
- **Domain-Specific:** Create custom providers for business-specific data
- **Reusable Fixtures:** Centralize fake data generation in pytest fixtures
- **Realistic Constraints:** Generate data matching real-world validation rules

### Post-Execution Checklist

- [ ] faker added to dev dependencies
- [ ] Faker instances seeded (prefer seed_instance)
- [ ] Custom providers defined for domain models
- [ ] pytest fixtures created for reusable instances
- [ ] No Faker usage in production code

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Non-Deterministic Test Data Without Seeding

**Problem:** Using Faker without setting a seed, causing tests to generate different data on each run and making failures non-reproducible.

**Why It Fails:** Flaky tests that pass sometimes and fail others. Cannot reproduce bugs reported by CI. Debugging requires guessing which random data caused failure.

**Correct Pattern:**
```python
# BAD: Random data each run
from faker import Faker
fake = Faker()

def test_user_creation():
    user = create_user(fake.email(), fake.name())  # Different every run!
    assert user.is_valid()

# GOOD: Seeded for reproducibility
from faker import Faker
fake = Faker()
fake.seed_instance(12345)  # Same data every run, instance-level

# Or per-test seeding for isolation
@pytest.fixture
def fake():
    f = Faker()
    f.seed_instance(0)
    return f

def test_user_creation(fake):
    user = create_user(fake.email(), fake.name())  # Reproducible!
    assert user.is_valid()
```

### Seed Value Selection

```python
# Seed values are arbitrary — any integer produces a deterministic sequence.
# Common conventions:

# 1. Fixed test seed — same across all tests for team consistency:
FAKER_SEED = 12345  # Defined once in conftest.py or constants

# 2. Per-scenario seeds — different seeds for different test domains:
USER_SEED = 100
ORDER_SEED = 200
PRODUCT_SEED = 300

# 3. CI reproducibility — log the seed to reproduce failures:
import os
SEED = int(os.environ.get("FAKER_SEED", "12345"))
fake.seed_instance(SEED)
# In CI: FAKER_SEED=67890 pytest tests/  (reproduce a specific run)
```

**When to change seeds:**
- **Never** change seeds in existing tests without reason — it changes all generated data and may break assertions
- **New test suites:** Pick any seed, document it in conftest.py
- **Debugging:** Use CI's logged seed to reproduce exact data
- **Parallel workers:** Use worker-specific offsets (see 240a for xdist patterns)

### Anti-Pattern 2: Generating Unrealistic Data That Bypasses Validation

**Problem:** Using generic Faker methods that produce data not matching real-world constraints (e.g., `fake.text()` for fields with length limits).

**Why It Fails:** Tests pass with unrealistic data but fail in production. Validation edge cases not tested. Database constraints violated.

**Correct Pattern:**
```python
# BAD: Generic data ignores constraints
fake.text()  # Could be 1000+ chars for a 50-char field
fake.random_int()  # Could be negative for age field
fake.word()  # Might not be valid for enum field

# GOOD: Constrained data matching domain
fake.text(max_nb_chars=50)  # Respects field length
fake.random_int(min=18, max=120)  # Valid age range
fake.random_element(["pending", "active", "closed"])  # Valid enum values

# BEST: Custom providers for domain-specific data
class OrderProvider(BaseProvider):
    def order_status(self):
        return self.random_element(["pending", "shipped", "delivered"])

fake.add_provider(OrderProvider)
```

> **Investigation Required**
> When applying this rule:
> 1. **Read test files BEFORE adding Faker** - Check existing test data generation patterns
> 2. **Check pytest fixtures** - See if Faker fixtures already exist in conftest.py
> 3. **Never assume seeding strategy** - Read tests to understand reproducibility requirements
> 4. **Verify custom providers** - Check if domain-specific providers already defined
> 5. **Match existing patterns** - Follow project's test data conventions
> 6. **Verify Faker is dev-only** - Check `pyproject.toml` — Faker must be in `[dependency-groups] dev` or `[project.optional-dependencies] dev`, never in `[project.dependencies]`. Using Faker in production code is forbidden.
>
> **Anti-Pattern:**
> "Adding Faker to generate test data... (without checking existing approach)"
> "Creating fake users... (without checking if factory already exists)"
>
> **Correct Pattern:**
> "Let me check your existing test data setup first."
> [reads test files, checks conftest.py, reviews fixtures]
> "I see you have pytest fixtures with seeded Faker. Adding new provider following this pattern..."

## Unique Value Management

Faker's `unique` attribute tracks previously generated values to prevent duplicates. Values accumulate across calls within the same Faker instance. **Clear between tests to avoid `UniquenessException`:**

```python
@pytest.fixture(autouse=True)
def reset_unique_values(seeded_faker):
    """Reset unique value tracking before each test.

    Without this, unique values accumulate across tests and eventually
    exhaust the available pool, raising UniquenessException.
    """
    yield
    seeded_faker.unique.clear()
```

### UniquenessException

When all possible values have been generated, `unique` raises `UniquenessException`:

```python
from faker import Faker
from faker.exceptions import UniquenessException

fake = Faker()
fake.seed_instance(12345)

# Small pool — only 2 possible values:
try:
    for _ in range(10):
        value = fake.unique.random_element(["active", "inactive"])
except UniquenessException:
    # Raised on 3rd call — only 2 unique values exist
    # Solutions:
    # 1. Clear and regenerate: fake.unique.clear()
    # 2. Use non-unique method: fake.random_element(["active", "inactive"])
    # 3. Expand the pool: add more elements to the list
    pass
```

### When to Use `unique` vs Regular Methods

- **Usernames, emails (must be unique):** Use `fake.unique.user_name()` because database constraints require uniqueness
- **Status fields, categories:** Use `fake.random_element([...])` because duplicates are expected and valid
- **Batch IDs, order numbers:** Use `fake.unique.random_int(min=1000, max=9999)` because business logic requires uniqueness
- **Descriptions, notes:** Use `fake.text()` because content can repeat

## Output Format Examples

```python
# conftest.py - Faker-specific output example
import pytest
from faker import Faker

@pytest.fixture(scope="session")
def seeded_faker() -> Faker:
    """Session-scoped, seeded Faker for reproducible test data."""
    f = Faker("en_US")
    f.seed_instance(12345)
    return f

@pytest.fixture
def fake_user(seeded_faker):
    """Generate a single fake user dict."""
    return {
        "username": seeded_faker.unique.user_name(),
        "email": seeded_faker.unique.email(),
        "age": seeded_faker.random_int(min=18, max=80),
    }
```

## Installation and Setup

### Dependencies and Environment
- **Requirement:** Use `uv` for dependency management following `200-python-core.md` patterns
- **Requirement:** Install Faker with: `uv add --group dev faker`
- **Rule:** Use specific providers when needed for specialized data
- **Always:** Pin Faker version for reproducible test data generation

```toml
# pyproject.toml
[dependency-groups]
dev = [
    "faker>=20.0.0",
    "pytest>=7.0.0",
    "pytest-faker>=2.0.0",
]
```

### Project Structure for Faker Usage
- **Rule:** Organize fake data generation in dedicated modules
- **Rule:** Separate test fixtures from production code

Directory structure for `project/`:
- **tests/** - Test suite
  - **fixtures/** - `__init__.py`, `user_fixtures.py`, `product_fixtures.py`
  - **factories/** - `__init__.py`, `user_factory.py`, `base_factory.py`
  - `conftest.py` - Pytest configuration
- **scripts/** - Utility scripts
  - `generate_test_data.py` - Data generation scripts

## Core Provider Usage

### DataGenerator Pattern
- **Rule:** Use appropriate providers for different data types
- **Always:** Initialize Faker instances with proper seeding
- **Rule:** Use `fake.pyfloat()` for float generation instead of accessing internal `fake.random.uniform()`

```python
from faker import Faker
from typing import Dict, Any

class DataGenerator:
    """Centralized data generation using Faker."""

    def __init__(self, locale: str = "en_US", seed: int = None):
        self.fake = Faker(locale)
        if seed is not None:
            self.fake.seed_instance(seed)

    def generate_user(self) -> Dict[str, Any]:
        """Generate realistic user data."""
        return {
            "id": self.fake.random_int(min=1, max=100000),
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "phone": self.fake.phone_number(),
            "address": {
                "street": self.fake.street_address(),
                "city": self.fake.city(),
                "state": self.fake.state_abbr(),
                "zip_code": self.fake.zipcode(),
                "country": self.fake.country_code(),
            },
            "date_of_birth": self.fake.date_of_birth(minimum_age=18, maximum_age=80),
            "created_at": self.fake.date_time_between(start_date="-2y", end_date="now"),
            "is_active": self.fake.boolean(chance_of_getting_true=85),
        }

    def generate_product(self) -> Dict[str, Any]:
        """Generate realistic product data."""
        categories = ["Electronics", "Clothing", "Books", "Home & Garden", "Sports"]
        return {
            "id": self.fake.uuid4(),
            "name": self.fake.catch_phrase(),
            "description": self.fake.text(max_nb_chars=500),
            "sku": self.fake.bothify(text="??-####-??", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            "price": self.fake.pyfloat(min_value=9.99, max_value=999.99, right_digits=2),
            "category": self.fake.random_element(elements=categories),
            "in_stock": self.fake.random_int(min=0, max=1000),
            "created_at": self.fake.date_time_between(start_date="-1y", end_date="now"),
        }

# Usage
generator = DataGenerator(seed=12345)  # Reproducible data
user_data = generator.generate_user()
product_data = generator.generate_product()
```

### Locale Fallback Behavior

When a provider method doesn't exist for the specified locale, Faker falls back to `en_US`:

```python
from faker import Faker

# Japanese locale — some providers fall back to English
fake_ja = Faker("ja_JP")
fake_ja.seed_instance(12345)

fake_ja.name()      # → Japanese name (provider exists)
fake_ja.ssn()       # → Falls back to en_US format (no ja_JP SSN provider)

# To explicitly set fallback locale:
fake = Faker(["ja_JP", "en_US"])  # ja_JP primary, en_US fallback
```
