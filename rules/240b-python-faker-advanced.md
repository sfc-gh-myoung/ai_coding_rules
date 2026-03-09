# Python Faker Advanced Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:locale, kw:custom-provider, kw:faker-performance
**Keywords:** Faker, localization, locale, custom providers, BaseProvider, performance optimization, batch generation, caching, multi-language
**TokenBudget:** ~2100
**ContextTier:** Low
**Depends:** 240-python-faker.md

## Scope

**What This Rule Covers:**
Advanced Faker patterns including localization for international testing, creating custom providers for domain-specific data, and performance optimization for large dataset generation.

**When to Load This Rule:**
- Localizing test data for international applications
- Creating custom Faker providers for domain models
- Generating large datasets efficiently
- Optimizing Faker performance with caching

## References

### Dependencies

**Must Load First:**
- **240-python-faker.md** - Core Faker patterns

**Related:**
- **240a-python-faker-testing.md** - Pytest integration and seeding

## Contract

### Inputs and Prerequisites

- Faker installed (from 240-python-faker.md)
- Understanding of domain data requirements for custom providers

### Mandatory

- **Always:** Use `seed_instance()` for per-instance seeding in all generators
- **Rule:** Follow Faker's provider conventions when creating custom providers
- **Rule:** Use generators for large dataset generation to manage memory

### Forbidden

- Accessing internal `fake.random.uniform()` when `fake.pyfloat()` works (less discoverable)
- Creating custom providers that duplicate built-in Faker functionality
- Loading all locales when only one or two are needed

### Execution Steps

1. Identify locale requirements for the project
2. Create custom providers for domain-specific data
3. Implement performance-optimized generators for large datasets
4. Cache expensive operations (pre-generate common data)
5. Test custom providers with seeded instances

### Output Format

Custom Faker providers, localized data generators, and batch-optimized generation classes.

### Validation

**Pre-Task-Completion Checks:**
- [ ] Custom providers extend BaseProvider correctly
- [ ] Localized generators handle all required locales
- [ ] Large dataset generators use memory-efficient patterns
- [ ] All generators use seed_instance()

### Design Principles

- **Provider convention:** Follow Faker's BaseProvider pattern for reusability
- **Memory efficiency:** Use generators for large datasets, cache common data
- **Locale isolation:** Initialize separate Faker instances per locale

### Post-Execution Checklist

- [ ] Custom providers created and registered
- [ ] Localization configured for required regions
- [ ] Performance optimized for dataset size
- [ ] All generators properly seeded

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Accessing Internal Random Module

**Problem:** Using `fake.random.uniform()` to generate floats instead of Faker's native `pyfloat()` method. The internal random module is less discoverable and bypasses Faker's seeding in some edge cases.

**Correct Pattern:** Use Faker's built-in methods like `pyfloat()` which respect seeding and are discoverable.

```python
# Wrong: Accessing internal random module
price = round(self.fake.random.uniform(9.99, 999.99), 2)

# Correct: Using Faker-native method
price = self.fake.pyfloat(min_value=9.99, max_value=999.99, right_digits=2)
```

### Anti-Pattern 2: Loading All Locales Unnecessarily

**Problem:** Creating Faker instances with many locales when only specific ones are needed, wasting memory and startup time.

**Correct Pattern:** Load only the locales you actually need, using separate instances per locale.

```python
# Wrong: Loading unnecessary locales
fake = Faker(["en_US", "en_GB", "de_DE", "fr_FR", "ja_JP", "pt_BR", "zh_CN", "ko_KR"])

# Correct: Load only what you need
fake_us = Faker("en_US")
fake_de = Faker("de_DE")  # Only if German data is actually needed
```

## Localization Patterns

### Multi-Locale Data Generation

```python
from faker import Faker
from typing import Dict, Any, List

class LocalizedDataGenerator:
    """Generate localized data for different regions."""

    def __init__(self):
        self.locales = {
            "us": Faker("en_US"),
            "uk": Faker("en_GB"),
            "germany": Faker("de_DE"),
            "france": Faker("fr_FR"),
            "japan": Faker("ja_JP"),
            "brazil": Faker("pt_BR"),
        }
        # Seed each instance for reproducibility
        for fake in self.locales.values():
            fake.seed_instance(12345)

    def generate_localized_user(self, locale: str = "us") -> Dict[str, Any]:
        """Generate user data for specific locale."""
        if locale not in self.locales:
            raise ValueError(f"Unsupported locale: {locale}")

        fake = self.locales[locale]
        return {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "company": fake.company(),
            "job_title": fake.job(),
            "currency": fake.currency_code(),
            "locale": locale,
        }

    def generate_multi_locale_dataset(self, count_per_locale: int = 10) -> List[Dict]:
        """Generate dataset with users from multiple locales."""
        dataset = []
        for locale in self.locales:
            for _ in range(count_per_locale):
                dataset.append(self.generate_localized_user(locale))
        return dataset
```

## Custom Providers

### Domain-Specific Provider Pattern

```python
from faker.providers import BaseProvider
from faker import Faker
from typing import List

class TechCompanyProvider(BaseProvider):
    """Custom provider for tech company data."""

    tech_companies = [
        "TechCorp", "DataSystems", "CloudWorks", "NetDynamics", "CodeForge",
    ]
    tech_domains = ["AI/ML", "Web Development", "DevOps", "Cloud Infrastructure"]
    tech_roles = ["Software Engineer", "Data Scientist", "DevOps Engineer", "SRE"]
    programming_languages = ["Python", "JavaScript", "Go", "Rust", "TypeScript"]

    def tech_company_name(self) -> str:
        return self.random_element(self.tech_companies)

    def tech_domain(self) -> str:
        return self.random_element(self.tech_domains)

    def tech_role(self) -> str:
        return self.random_element(self.tech_roles)

    def tech_stack(self, count: int = 3) -> List[str]:
        return self.random_elements(
            elements=self.programming_languages, length=count, unique=True
        )

    def github_username(self) -> str:
        adjectives = ["cool", "awesome", "super", "mega"]
        nouns = ["coder", "dev", "ninja", "guru"]
        return f"{self.random_element(adjectives)}{self.random_element(nouns)}{self.random_int(10, 999)}"

class ProjectProvider(BaseProvider):
    """Custom provider for software project data."""

    project_types = ["Web App", "Mobile App", "API", "Library", "CLI Tool"]

    def project_name(self) -> str:
        adjective = self.generator.word()
        noun = self.generator.word()
        return f"{adjective.title()}{noun.title()}"

    def project_description(self) -> str:
        """Generate project description. Uses generator.bs() for business-speak phrases."""
        templates = [
            "A {adjective} {project_type} for {purpose}",
            "Modern {project_type} built with {tech}",
        ]
        return self.random_element(templates).format(
            adjective=self.generator.word(),
            project_type=self.random_element(self.project_types).lower(),
            purpose=self.generator.bs(),  # bs() generates "business speak" phrases
            tech=self.random_element(["Python", "JavaScript", "Go", "Rust"]),
        )

# Register and use custom providers
fake = Faker()
fake.seed_instance(12345)
fake.add_provider(TechCompanyProvider)
fake.add_provider(ProjectProvider)

tech_profile = {
    "company": fake.tech_company_name(),
    "role": fake.tech_role(),
    "languages": fake.tech_stack(4),
    "github": fake.github_username(),
    "project": {"name": fake.project_name(), "description": fake.project_description()},
}
```

## Performance Optimization

### Efficient Large Dataset Generation

```python
from faker import Faker
from typing import Iterator, Dict, Any, List

class PerformantDataGenerator:
    """Memory-efficient data generation with caching."""

    def __init__(self, locale: str = "en_US", seed: int = None):
        self.fake = Faker(locale)
        if seed is not None:
            self.fake.seed_instance(seed)

        # Pre-generate common data for reuse
        self._cached_companies = [self.fake.company() for _ in range(100)]
        self._cached_domains = ["gmail.com", "yahoo.com", "company.com"]

    def generate_users_stream(self, count: int) -> Iterator[Dict[str, Any]]:
        """Generate users as a stream to manage memory."""
        for i in range(count):
            yield {
                "id": i + 1,
                "username": f"user_{i + 1}",
                "email": f"user_{i + 1}@{self.fake.random_element(self._cached_domains)}",
                "first_name": self.fake.first_name(),
                "company": self.fake.random_element(self._cached_companies),
            }

    def generate_in_batches(self, total: int, batch_size: int = 1000) -> Iterator[List[Dict]]:
        """Generate data in batches for processing pipelines."""
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            yield list(self.generate_users_stream(end - start))
```
