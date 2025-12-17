# Python Faker Data Generation Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Faker, test data generation, fake data, providers, localization, synthetic data, pytest fixtures, seeding, deterministic testing, Python testing
**TokenBudget:** ~3100
**ContextTier:** Low
**Depends:** rules/200-python-core.md

## Purpose
Establish comprehensive patterns for generating realistic test data using Python's Faker library, covering setup, providers, localization, testing integration, and performance optimization to create maintainable and deterministic test suites.

## Rule Scope

Python testing, data generation, test fixtures, development utilities

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Install with uv** - `uv add --group dev faker` for deterministic versions
- **Always seed for tests** - `Faker.seed(0)` for reproducible test data
- **Use specific providers** - faker.name(), faker.email() for type-safe data
- **Localize when needed** - `Faker('es_ES')` for locale-specific data
- **Create pytest fixtures** - Centralize Faker instances for consistency
- **Never use in production** - Faker is for testing/development only

**Quick Checklist:**
- [ ] faker added to dev dependencies
- [ ] Faker.seed() called in tests
- [ ] Custom providers defined for domain models
- [ ] pytest fixtures created for reusable instances
- [ ] Localization configured if needed
- [ ] Performance optimized for large datasets
- [ ] No Faker usage in production code

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

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Non-Deterministic Test Data Without Seeding

**Problem:** Using Faker without setting a seed, causing tests to generate different data on each run and making failures non-reproducible.

**Why It Fails:** Flaky tests that pass sometimes and fail others. Cannot reproduce bugs reported by CI. Debugging requires guessing which random data caused failure. Test isolation compromised.

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
Faker.seed(12345)  # Same data every run

# Or per-test seeding for isolation
@pytest.fixture
def fake():
    Faker.seed(0)
    return Faker()

def test_user_creation(fake):
    user = create_user(fake.email(), fake.name())  # Reproducible!
    assert user.is_valid()
```

### Anti-Pattern 2: Generating Unrealistic Data That Bypasses Validation

**Problem:** Using generic Faker methods that produce data not matching real-world constraints (e.g., `fake.text()` for fields with length limits).

**Why It Fails:** Tests pass with unrealistic data but fail in production. Validation edge cases not tested. Data doesn't match domain constraints. Database constraints violated.

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
> 1. **Read test files BEFORE adding Faker** - Check existing test data generation patterns
> 2. **Check pytest fixtures** - See if Faker fixtures already exist in conftest.py
> 3. **Never assume seeding strategy** - Read tests to understand reproducibility requirements
> 4. **Verify custom providers** - Check if domain-specific providers already defined
> 5. **Match existing patterns** - Follow project's test data conventions
>
> **Anti-Pattern:**
> "Adding Faker to generate test data... (without checking existing approach)"
> "Creating fake users... (without checking if factory already exists)"
>
> **Correct Pattern:**
> "Let me check your existing test data setup first."
> [reads test files, checks conftest.py, reviews fixtures]
> "I see you have pytest fixtures with seeded Faker. Adding new provider following this pattern..."

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
- [Faker Documentation](https://faker.readthedocs.io/en/stable/) - Comprehensive guide to fake data generation
- [pytest-faker Plugin](https://pypi.org/project/pytest-faker/) - Pytest fixtures and integration patterns
- [Factory Boy](https://factoryboy.readthedocs.io/) - Object factory patterns for complex test data

### Related Rules
- **Python Core**: `rules/200-python-core.md`
- **FastAPI Testing**: `rules/210b-python-fastapi-testing.md`
- **Demo Creation**: `rules/900-demo-creation.md`

## 1. Installation and Setup

### Dependencies and Environment
- **Requirement:** Use `uv` for dependency management following `200-python-core.md` patterns
- **Requirement:** Install Faker with: `uv add faker` or `uv add --group dev faker` for development only
- **Rule:** Use specific providers when needed: `faker[automotive,credit-card]` for specialized data
- **Always:** Pin Faker version for reproducible test data generation

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
    "faker>=20.0.0",
    "pytest>=7.0.0",
    "pytest-faker>=2.0.0",  # Pytest integration
]

test = [
    "faker>=20.0.0",
    "factory-boy>=3.3.0",  # For model factories
]
```

### Project Structure for Faker Usage
- **Rule:** Organize fake data generation in dedicated modules
- **Rule:** Separate test fixtures from production data generation
- **Always:** Use consistent patterns for different data types

Directory structure for `project/`:
- **src/myapp/models/** - Application models
- **tests/** - Test suite
  - **fixtures/** - `__init__.py`, `user_fixtures.py`, `product_fixtures.py`
  - **factories/** - `__init__.py`, `user_factory.py`, `base_factory.py`
  - `conftest.py` - Pytest configuration
- **scripts/** - Utility scripts
  - `generate_test_data.py` - Data generation scripts
  - `seed_database.py` - Database seeding

## 2. Basic Faker Usage Patterns

### Core Provider Usage
- **Rule:** Use appropriate providers for different data types
- **Always:** Initialize Faker instances with proper configuration
- **Rule:** Use class-based approach for complex data generation

```python
from faker import Faker
from faker.providers import internet, automotive, credit_card
from typing import Dict, List, Any
import random

# Initialize with locale
fake = Faker('en_US')

# Add custom providers
fake.add_provider(internet)
fake.add_provider(automotive)
fake.add_provider(credit_card)

class DataGenerator:
    """Centralized data generation using Faker."""

    def __init__(self, locale: str = 'en_US', seed: int = None):
        self.fake = Faker(locale)
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

    def generate_user(self) -> Dict[str, Any]:
        """Generate realistic user data."""
        return {
            'id': self.fake.random_int(min=1, max=100000),
            'username': self.fake.user_name(),
            'email': self.fake.email(),
            'first_name': self.fake.first_name(),
            'last_name': self.fake.last_name(),
            'phone': self.fake.phone_number(),
            'address': {
                'street': self.fake.street_address(),
                'city': self.fake.city(),
                'state': self.fake.state_abbr(),
                'zip_code': self.fake.zipcode(),
                'country': self.fake.country_code()
            },
            'date_of_birth': self.fake.date_of_birth(minimum_age=18, maximum_age=80),
            'created_at': self.fake.date_time_between(start_date='-2y', end_date='now'),
            'is_active': self.fake.boolean(chance_of_getting_true=85)
        }

    def generate_product(self) -> Dict[str, Any]:
        """Generate realistic product data."""
        categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports']

        return {
            'id': self.fake.uuid4(),
            'name': self.fake.catch_phrase(),
            'description': self.fake.text(max_nb_chars=500),
            'sku': self.fake.bothify(text='??-####-??', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
            'price': round(self.fake.random.uniform(9.99, 999.99), 2),
            'category': self.fake.random_element(elements=categories),
            'in_stock': self.fake.random_int(min=0, max=1000),
            'weight': round(self.fake.random.uniform(0.1, 50.0), 2),
            'dimensions': {
                'length': round(self.fake.random.uniform(1, 100), 1),
                'width': round(self.fake.random.uniform(1, 100), 1),
                'height': round(self.fake.random.uniform(1, 100), 1)
            },
            'created_at': self.fake.date_time_between(start_date='-1y', end_date='now')
        }

# Usage
generator = DataGenerator(seed=12345)  # Reproducible data
user_data = generator.generate_user()
product_data = generator.generate_product()
```

### Localization and Multi-Language Support
- **Rule:** Use appropriate locales for region-specific data
- **Always:** Test with multiple locales when building international applications
- **Rule:** Handle locale-specific formatting and validation

```python
from faker import Faker
from typing import Dict, List

class LocalizedDataGenerator:
    """Generate localized data for different regions."""

    def __init__(self):
        self.locales = {
            'us': Faker('en_US'),
            'uk': Faker('en_GB'),
            'germany': Faker('de_DE'),
            'france': Faker('fr_FR'),
            'japan': Faker('ja_JP'),
            'brazil': Faker('pt_BR')
        }

    def generate_localized_user(self, locale: str = 'us') -> Dict[str, Any]:
        """Generate user data for specific locale."""
        if locale not in self.locales:
            raise ValueError(f"Unsupported locale: {locale}")

        fake = self.locales[locale]

        return {
            'name': fake.name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.address(),
            'company': fake.company(),
            'job_title': fake.job(),
            'currency': fake.currency_code(),
            'locale': locale,
            'timezone': str(fake.timezone())
        }

    def generate_multi_locale_dataset(self, count_per_locale: int = 10) -> List[Dict]:
        """Generate dataset with users from multiple locales."""
        dataset = []

        for locale in self.locales.keys():
            for _ in range(count_per_locale):
                user = self.generate_localized_user(locale)
                dataset.append(user)

        return dataset

# Usage
localized_gen = LocalizedDataGenerator()

# Generate German user
german_user = localized_gen.generate_localized_user('germany')

# Generate international dataset
international_users = localized_gen.generate_multi_locale_dataset(5)
```

## 3. Custom Providers and Extensions

### Creating Custom Providers
- **Rule:** Create custom providers for domain-specific data
- **Always:** Follow Faker's provider conventions and patterns
- **Rule:** Make custom providers reusable across projects

```python
from faker.providers import BaseProvider
from faker import Faker
import random
from typing import List, Dict

class TechCompanyProvider(BaseProvider):
    """Custom provider for tech company data."""

    tech_companies = [
        'TechCorp', 'DataSystems', 'CloudWorks', 'DevSolutions',
        'CodeCraft', 'ByteForge', 'PixelPush', 'LogicLabs'
    ]

    tech_domains = [
        'AI/ML', 'Web Development', 'Mobile Apps', 'DevOps',
        'Data Science', 'Cybersecurity', 'Cloud Computing', 'IoT'
    ]

    tech_roles = [
        'Software Engineer', 'Data Scientist', 'DevOps Engineer',
        'Product Manager', 'UX Designer', 'Security Analyst',
        'Cloud Architect', 'Full Stack Developer'
    ]

    programming_languages = [
        'Python', 'JavaScript', 'Java', 'Go', 'Rust',
        'TypeScript', 'C++', 'Ruby', 'PHP', 'Swift'
    ]

    def tech_company_name(self) -> str:
        """Generate a tech company name."""
        return self.random_element(self.tech_companies)

    def tech_domain(self) -> str:
        """Generate a technology domain."""
        return self.random_element(self.tech_domains)

    def tech_role(self) -> str:
        """Generate a technology job role."""
        return self.random_element(self.tech_roles)

    def programming_language(self) -> str:
        """Generate a programming language."""
        return self.random_element(self.programming_languages)

    def tech_stack(self, count: int = 3) -> List[str]:
        """Generate a technology stack."""
        return self.random_elements(
            elements=self.programming_languages,
            length=count,
            unique=True
        )

    def github_username(self) -> str:
        """Generate a GitHub-style username."""
        adjectives = ['cool', 'awesome', 'super', 'mega', 'ultra']
        nouns = ['coder', 'dev', 'ninja', 'guru', 'master']

        return f"{self.random_element(adjectives)}{self.random_element(nouns)}{self.random_int(10, 999)}"

class ProjectProvider(BaseProvider):
    """Custom provider for software project data."""

    project_types = ['Web App', 'Mobile App', 'API', 'Library', 'CLI Tool', 'Desktop App']

    def project_name(self) -> str:
        """Generate a project name."""
        adjective = self.generator.word()
        noun = self.generator.word()
        return f"{adjective.title()}{noun.title()}"

    def project_description(self) -> str:
        """Generate a project description."""
        templates = [
            "A {adjective} {project_type} for {purpose}",
            "Modern {project_type} built with {tech}",
            "{adjective} solution for {purpose} using {tech}"
        ]

        return self.generator.parse(self.random_element(templates)).format(
            adjective=self.generator.word(),
            project_type=self.random_element(self.project_types).lower(),
            purpose=self.generator.bs(),
            tech=self.generator.random_element(['Python', 'JavaScript', 'Go', 'Rust'])
        )

# Register and use custom providers
fake = Faker()
fake.add_provider(TechCompanyProvider)
fake.add_provider(ProjectProvider)

# Generate tech-specific data
tech_profile = {
    'company': fake.tech_company_name(),
    'role': fake.tech_role(),
    'domain': fake.tech_domain(),
    'languages': fake.tech_stack(4),
    'github': fake.github_username(),
    'project': {
        'name': fake.project_name(),
        'description': fake.project_description()
    }
}
```

## 4. Testing Integration

### Pytest Integration
- **Rule:** Use pytest-faker for seamless integration with pytest
- **Always:** Use fixtures for reusable fake data in tests
- **Rule:** Seed faker instances for reproducible tests

```python
import pytest
from faker import Faker
from typing import Dict, List
from myapp.models import User, Product

@pytest.fixture
def faker_seed():
    """Provide consistent seed for reproducible tests."""
    return 12345

@pytest.fixture
def fake_user_data(faker):
    """Generate fake user data for testing."""
    def _generate_user(**overrides) -> Dict:
        data = {
            'username': faker.user_name(),
            'email': faker.email(),
            'first_name': faker.first_name(),
            'last_name': faker.last_name(),
            'age': faker.random_int(min=18, max=80),
            'is_active': True
        }
        data.update(overrides)
        return data
    return _generate_user

@pytest.fixture
def fake_users_batch(fake_user_data):
    """Generate batch of fake users."""
    def _generate_batch(count: int = 10) -> List[Dict]:
        return [fake_user_data() for _ in range(count)]
    return _generate_batch

class TestUserModel:
    """Test user model with fake data."""

    def test_user_creation_with_fake_data(self, fake_user_data):
        """Test user creation with generated data."""
        user_data = fake_user_data()
        user = User(**user_data)

        assert user.username == user_data['username']
        assert user.email == user_data['email']
        assert user.is_active is True

    def test_user_validation_with_invalid_fake_data(self, fake_user_data):
        """Test validation with intentionally invalid data."""
        invalid_data = fake_user_data(
            age=-5,  # Invalid age
            email="invalid-email"  # Invalid email format
        )

        with pytest.raises(ValidationError):
            User(**invalid_data)

    def test_batch_user_processing(self, fake_users_batch):
        """Test processing multiple users."""
        users_data = fake_users_batch(50)
        users = [User(**data) for data in users_data]

        assert len(users) == 50
        assert all(user.is_active for user in users)

        # Test uniqueness of generated data
        usernames = [user.username for user in users]
        assert len(set(usernames)) == len(usernames)  # All unique
```

### Factory Pattern with Factory Boy
- **Rule:** Use Factory Boy with Faker for complex model creation
- **Rule:** Use SubFactory for related model creation

```python
import factory
from factory.faker import Faker as FactoryFaker

class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n + 1)
    username = factory.LazyAttribute(lambda obj: f"user_{obj.id}")
    email = FactoryFaker('email')
    first_name = FactoryFaker('first_name')
    is_active = True

class OrderFactory(factory.Factory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    quantity = FactoryFaker('random_int', min=1, max=10)
    status = FactoryFaker('random_element', elements=['pending', 'shipped'])

# Usage
def test_create_order():
    order = OrderFactory()
    assert order.user is not None
    assert order.quantity > 0
```

## 5. Performance and Optimization

### Efficient Data Generation
- **Rule:** Use generators for large datasets to manage memory
- **Rule:** Cache expensive operations and reuse Faker instances

```python
class PerformantDataGenerator:
    def __init__(self, locale: str = 'en_US', seed: int = None):
        self.fake = Faker(locale)
        if seed is not None:
            Faker.seed(seed)

        # Pre-generate common data for reuse
        self._cached_companies = [self.fake.company() for _ in range(100)]
        self._cached_domains = ['gmail.com', 'yahoo.com', 'company.com']

    def generate_users_batch(self, count: int) -> Iterator[Dict[str, Any]]:
        for i in range(count):
            yield {
                'id': i + 1,
                'username': f"user_{i + 1}",
                'email': f"user_{i + 1}@{self.fake.random_element(self._cached_domains)}",
                'first_name': self.fake.first_name(),
                'company': self.fake.random_element(self._cached_companies)
            }

    def generate_large_dataset(self, total: int, batch_size: int = 1000):
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            yield list(self.generate_users_batch(end - start))
```

### Seeding and Reproducibility
- **Rule:** Always use seeds for reproducible test data
- **Rule:** Use different seeds for different test scenarios

```python
class SeededDataGenerator:
    def __init__(self, base_seed: int = 12345):
        self.base_seed = base_seed
        self.scenario_seeds = {
            'user_registration': base_seed + 1,
            'error_scenarios': base_seed + 2
        }

    def get_seeded_faker(self, scenario: str) -> Faker:
        fake = Faker()
        Faker.seed(self.scenario_seeds[scenario])
        return fake

    def generate_test_data(self, scenario: str, count: int = 10) -> List[Dict]:
        fake = self.get_seeded_faker(scenario)

        if scenario == 'user_registration':
            return [{
                'username': fake.user_name(),
                'email': fake.email(),
                'age': fake.random_int(min=18, max=65)
            } for _ in range(count)]

        return []

# Usage
def test_with_seeded_data():
    generator = SeededDataGenerator(42)
    users = generator.generate_test_data('user_registration', 5)
    assert len(users) == 5
```

## Related Rules

- **`200-python-core.md`** - Core Python patterns and uv usage
- **`201-python-lint-format.md`** - Ruff linting and formatting standards
- **`203-python-project-setup.md`** - Python project structure and packaging
- **`230-python-pydantic.md`** - Pydantic integration for data validation
- **`800-project-changelog-rules.md`** - Changelog discipline for testing changes
