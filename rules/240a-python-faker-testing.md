# Python Faker Testing Integration

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:faker-fixtures, kw:factory-boy, kw:seeded-data
**Keywords:** Faker, pytest fixtures, Factory Boy, seeded testing, deterministic data, pytest-xdist, test isolation, SubFactory
**TokenBudget:** ~1900
**ContextTier:** Low
**Depends:** 240-python-faker.md, 206-python-pytest.md

## Scope

**What This Rule Covers:**
Pytest integration with Faker including fixture patterns, Factory Boy for complex models, and seeding strategies for reproducible and parallel-safe tests.

**When to Load This Rule:**
- Creating pytest fixtures with Faker data
- Using Factory Boy for model factories
- Setting up seeded test data for CI reproducibility
- Running Faker-based tests with pytest-xdist

## References

### Dependencies

**Must Load First:**
- **240-python-faker.md** - Core Faker patterns
- **206-python-pytest.md** - Pytest patterns

**Related:**
- **240b-python-faker-advanced.md** - Custom providers and performance

## Contract

### Inputs and Prerequisites

- Faker installed (from 240-python-faker.md)
- pytest installed for testing integration

### Mandatory

- **Critical:** Use `seed_instance()` for per-instance seeding, not `Faker.seed()` which is global and unsafe for parallel tests
- **Always:** Use fixtures for reusable fake data in tests
- **Rule:** Use Factory Boy with SubFactory for related model creation

### Forbidden

- Using `Faker.seed()` in parallel test environments (use `seed_instance()`)
- Creating Faker instances without seeding in tests
- Duplicating fixture logic across test files (centralize in conftest.py)

### Execution Steps

1. Create seeded Faker fixture in conftest.py
2. Build data generation fixtures using factory functions
3. Set up Factory Boy factories for complex models
4. Verify reproducibility by running tests twice with same seed
5. Verify parallel safety with `pytest -n auto` (if using xdist)

### Output Format

conftest.py with seeded Faker fixtures, Factory Boy factories, and reproducible test data.

### Validation

**Pre-Task-Completion Checks:**
- [ ] Faker fixtures use `seed_instance()` not `Faker.seed()`
- [ ] Factory functions accept override parameters
- [ ] Factory Boy factories use SubFactory for relationships
- [ ] Tests produce same results on repeated runs

### Design Principles

- **Instance seeding:** Always use `seed_instance()` for test isolation
- **Override pattern:** Fixtures accept keyword overrides for flexibility
- **Factory composition:** Use SubFactory for related models

### Post-Execution Checklist

- [ ] Seeded Faker fixture in conftest.py
- [ ] Data generation fixtures with override support
- [ ] Factory Boy factories for complex models
- [ ] Parallel test safety verified

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Global Seeding in Parallel Tests

**Problem:** `Faker.seed()` is a CLASS method that seeds ALL Faker instances globally. In parallel test execution (pytest-xdist), one worker's seed overwrites another's, causing non-deterministic failures.

**Correct Pattern:** Use `seed_instance()` for per-instance seeding that is safe for parallel execution.

```python
# Wrong: Global seed - race condition with pytest-xdist
fake = Faker()
Faker.seed(12345)  # Affects ALL Faker instances across all workers!

# Correct: Instance-level seed - safe for parallel execution
fake = Faker()
fake.seed_instance(12345)  # Only seeds THIS instance
```

### Anti-Pattern 2: Fixture Logic Scattered Across Test Files

**Problem:** Each test file creates its own Faker instance and data generation functions, leading to inconsistent seeding and duplicated logic.

**Correct Pattern:** Centralize Faker fixtures in `conftest.py` with consistent seeding and reusable data generators.

```python
# Wrong: Duplicated in every test file
# tests/test_users.py
fake = Faker()
fake.seed_instance(42)
def make_user(): ...

# tests/test_orders.py
fake = Faker()
fake.seed_instance(99)  # Different seed!
def make_user(): ...  # Duplicated!

# Correct: Centralized in conftest.py
# tests/conftest.py
@pytest.fixture
def fake():
    f = Faker()
    f.seed_instance(12345)
    return f

@pytest.fixture
def fake_user(fake):
    def _generate(**overrides):
        data = {"username": fake.user_name(), "email": fake.email()}
        data.update(overrides)
        return data
    return _generate
```

## Pytest Fixture Patterns

### Seeded Faker Fixture

```python
# conftest.py
import pytest
from faker import Faker

@pytest.fixture
def fake():
    """Per-test seeded Faker for reproducible, isolated test data."""
    f = Faker()
    f.seed_instance(12345)
    return f
```

### Data Generation Fixtures with Overrides

```python
from typing import Dict
from myapp.models import User

@pytest.fixture
def fake_user_data(fake):
    """Generate fake user data with optional overrides."""
    def _generate(**overrides) -> Dict:
        data = {
            "username": fake.unique.user_name(),
            "email": fake.unique.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "age": fake.random_int(min=18, max=80),
            "is_active": True,
        }
        data.update(overrides)
        return data
    return _generate

@pytest.fixture
def fake_users_batch(fake_user_data):
    """Generate batch of fake users."""
    def _generate_batch(count: int = 10):
        return [fake_user_data() for _ in range(count)]
    return _generate_batch
```

### Test Examples

```python
class TestUserModel:
    def test_user_creation(self, fake_user_data):
        user_data = fake_user_data()
        user = User(**user_data)
        assert user.username == user_data["username"]

    def test_user_validation_with_invalid_data(self, fake_user_data):
        invalid_data = fake_user_data(age=-5, email="invalid")
        with pytest.raises(ValidationError):
            User(**invalid_data)

    def test_batch_processing(self, fake_users_batch):
        users_data = fake_users_batch(50)
        users = [User(**data) for data in users_data]
        assert len(users) == 50
        usernames = [u.username for u in users]
        assert len(set(usernames)) == len(usernames)  # All unique
```

## Factory Boy Integration

### Model Factories with SubFactory

```python
import factory
from factory.faker import Faker as FactoryFaker
from myapp.models import User, Order

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    username = factory.LazyAttribute(lambda obj: f"user_{obj.id}")
    email = FactoryFaker("email")
    first_name = FactoryFaker("first_name")
    is_active = True

class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    quantity = FactoryFaker("random_int", min=1, max=10)
    status = FactoryFaker("random_element", elements=["pending", "shipped"])

# Usage
def test_create_order():
    order = OrderFactory()
    assert order.user is not None
    assert order.quantity > 0
```

## Seeding Strategies

### Per-Scenario Seeding

```python
from faker import Faker
from typing import Dict, List

class SeededDataGenerator:
    """Generate scenario-specific test data with isolated seeds."""

    def __init__(self, base_seed: int = 12345):
        self.base_seed = base_seed
        self.scenario_seeds = {
            "user_registration": base_seed + 1,
            "error_scenarios": base_seed + 2,
        }

    def get_seeded_faker(self, scenario: str) -> Faker:
        """Get a Faker instance seeded for a specific scenario."""
        fake = Faker()
        # seed_instance() seeds only THIS instance (safe for parallel tests)
        # Faker.seed() is global and affects ALL instances (unsafe for xdist)
        fake.seed_instance(self.scenario_seeds[scenario])
        return fake

    def generate_test_data(self, scenario: str, count: int = 10) -> List[Dict]:
        fake = self.get_seeded_faker(scenario)
        if scenario == "user_registration":
            return [
                {
                    "username": fake.user_name(),
                    "email": fake.email(),
                    "age": fake.random_int(min=18, max=65),
                }
                for _ in range(count)
            ]
        return []
```
