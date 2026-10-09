---
schema_version: v4.0
rule_version: v3.0.0
description: "Isolated Faker/factory fixtures with reproducible sequences, stable relationships and real parallel uniqueness boundaries."
last_updated: 2026-10-07
keywords:
  - kw:faker pytest fixtures
  - kw:seed_instance parallel
  - kw:Factory Boy SubFactory
  - kw:pytest-xdist worker seeding
  - kw:conftest fixture hierarchy
  - kw:unique value cleanup
token_budget: ~900
context_tier: Low
depends:
  required:
    - 240-python-faker.md  # Core Faker patterns
    - 206-python-pytest.md  # Pytest patterns
  optional:
    - 240b-python-faker-advanced.md  # Custom providers and performance
---
# Python Faker Testing Integration

## Scope

**What This Rule Covers:**
Fixture/factory reuse, isolated RNG/unique pools, relational synthetic data and deterministic parallel execution.

**When to Load This Rule:**
When using Faker/Factory Boy in pytest; read `240b-python-faker-advanced.md` for providers/large generation.

## Contract

### Inputs and Prerequisites

- Existing fixtures/factories/plugins, source models/relationships, seed/version/time convention and database isolation.
- Actual serial/xdist worker configuration and permitted synthetic resource scope.

### Mandatory

- Reuse fixture owners and existing factory style; Factory Boy/SubFactory is useful for relationships, not mandatory for every object. Don't add pytest-faker/xdist/factory-boy dependencies or -n auto configuration unasked.
- Prefer per-test/scenario seeded Faker with frozen clock/version/locale and stable call order. Session RNG makes output depend on test order; clearing unique alone doesn't reseed. Fresh function-scoped Faker doesn't inherit another test's unique pool.
- Faker.seed affects process-local shared RNG, not all separate xdist workers remotely. Instance isolation avoids coupling within a process; worker processes already isolate globals, but shared databases/files still require separate identities.
- Worker-specific seeds can diversify outputs but don't guarantee no collisions or identical output after scheduler reassignment. Derive deterministic scenario/nodeid seed when reproducibility must not depend on worker; use explicit namespaces/sequences and isolated DB/schema for cross-worker uniqueness.
- Seed Factory Boy's actual RNG separately through its supported API when used; fake.seed_instance does not automatically seed every factory.Faker source. Reset sequences only at intended isolated scope, not inside a batch needing unique IDs.
- Factories accept intentional overrides/traits and compose parent relationships without inconsistent foreign keys. build versus create and lazy attributes differ; fixtures must not persist to a production session or claim creating data when only a Python object exists.
- unique pools can exhaust; clear only at test/dataset boundary and keep required same-batch uniqueness. Validate generated field formats/ranges/relations, not assume all usernames/emails are collision-free in a shared persistent store.
- Use explicit literal edge/invalid values and meaningful behavior assertions; random data isn't proof of every boundary. Record seeds/config on failure and retain it, not change seed to make tests green.
- Teardown restores RNG/unique/sequence/env/database state and closes resources; scoped conftest fixtures match actual sharing need without excessive autouse. Serial/parallel checks use installed plugins only and disclose unrun configurations.

### Execution Steps

1. Inspect current fixtures/factories/plugins and define data/seed/time/isolation contract.
2. Add minimal constrained factories/overrides/relations with scoped RNG and unique lifecycle.
3. Test valid/invalid/relationship/exhaustion/repeated-order cases and permitted parallel database namespaces.
4. Run project checks and report actual serial/parallel reproducibility scope.

### Validation

- Required seed/version/time/order and Factory Boy sources controlled; no shared fixture-state leak.
- Relationships/overrides/traits and uniqueness hold in actual isolated serial/parallel resources.
- Failures reproducible and boundary assertions meaningful; no unapproved plugin/database writes.

## References

- [Faker pytest integration](https://faker.readthedocs.io/en/master/pytest.html)
- [Factory Boy reproducibility](https://factoryboy.readthedocs.io/en/stable/recipes.html#using-reproducible-randomness)
- [Factory Boy reference](https://factoryboy.readthedocs.io/en/stable/reference.html)
- [xdist workers](https://pytest-xdist.readthedocs.io/en/stable/how-to.html)
