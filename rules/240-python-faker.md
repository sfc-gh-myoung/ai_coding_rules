---
schema_version: v4.0
rule_version: v5.0.0
description: "Reproducible synthetic Faker providers/fixtures with frozen time/version/order, real domain constraints and scoped uniqueness."
last_updated: 2026-10-07
keywords:
  - kw:Faker library
  - kw:seed_instance
  - kw:custom providers
  - kw:deterministic test data
  - kw:unique attribute
  - kw:locale fallback
token_budget: ~1000
context_tier: Low
depends:
  required:
    - 200-python-core.md  # Core Python patterns and uv usage
  optional:
    - 201-python-lint-format.md  # Ruff linting and formatting standards
    - 230-python-pydantic.md  # Pydantic integration for data validation
    - 240a-python-faker-testing.md  # Pytest fixtures, Factory Boy, seeding strategies
---
# Python Faker Data Generation Best Practices

## Scope

**What This Rule Covers:**
Synthetic test/demo provider selection, seeding, frozen time, locale/unique semantics and domain validation.

**When to Load This Rule:**
When generating test/development synthetic data; read `240a-python-faker-testing.md` for fixtures/factories and `240b-python-faker-advanced.md` for domain/volume generation.

## Contract

### Inputs and Prerequisites

- Existing factories/fixtures/provider/version, actual domain fields/constraints, locale distribution and approved synthetic output destination.
- Reproduction seed, fixed clock/window/timezone and deterministic call order/worker strategy where required.

### Mandatory

- Reuse current generators/fixtures and toolchain; no compulsory custom provider/class/plugin install. Keep Faker dev/test-only under this repository policy, not production user identities/credentials or real customer records.
- Use per-instance seed_instance for isolated fixtures; global Faker.seed affects shared RNG and must be deliberate. Same seed requires matching Faker/provider version, locale, call order and clock-dependent inputs for reproducibility; a >= version range isn't an exact pin.
- Freeze explicit time bounds/reference clock for date generation; relative now/-2y changes across runs even with seed. Preserve intended timezone/date types and no guessed timestamp windows.
- Use explicit literal boundary/assertion cases alongside varied generated data; don't replace simple known expected values with randomness. Log reproducible seed/version/config for fuzz cases rather than changing seed until tests pass.
- Choose providers/parameters that meet actual domain length/range/format/enums/precision, then validate generated output. Faker realism isn't type/security/validity proof. Use Decimal/scaled integers for exact money where required; independent address fields need not correspond geographically.
- Keep synthetic emails/URLs/phone/identifiers clearly non-actionable where possible; never send generated contacts notifications or claim fake banking/SSN data represents real people. No real PII seed samples or confidential external upload.
- unique tracks generated hashable results within its instance/pool and can exhaust; clear at actual scope boundary, handle UniquenessException deliberately and don't erase uniqueness midway through a batch. It doesn't guarantee database-wide/global worker uniqueness.
- Use deterministic sequential/namespace IDs or coordinated source keys for required relational/global uniqueness; random_int collisions are normal. Enforce database/domain constraints and associate foreign keys with generated parents, not independent random IDs.
- Reset both RNG and unique pools where test isolation needs it. Session-scoped generation can depend on execution order; function/scenario isolation preferred when assertions require repeatability. Worker seeds alone don't guarantee disjoint output.
- Verify actual provider/locale fallback; multi-locale Faker samples locale-specific generators rather than declaring a primary/fallback priority list. A locale name doesn't ensure every method's output uses that culture's format.
- Keep outputs bounded/reviewed and write only approved paths with manifest/count/type checks. Generation doesn't authorize loading databases, installing deps, or overwriting files.

### Execution Steps

1. Inspect fixtures/providers/domain and establish exact seed/version/time/locale contract.
2. Generate minimal useful synthetic data with constrained providers and stable relational identity.
3. Validate constraints/uniqueness/counts and reproducibility under repeated isolated runs.
4. Run project checks and report output scope/seed/config plus unsupported validity/privacy assumptions.

### Validation

- Version/seed/order/time/locale controlled enough for claimed reproducibility.
- Actual domain/type/precision/relations and uniqueness hold; boundary cases explicit.
- No real PII/production credentials or external contact effects; output paths/counts authorized.
- Fixtures reset required RNG/unique state and report exhaustion/failure rather than silently regenerate.

## References

- [Faker seeding, locale and uniqueness](https://faker.readthedocs.io/en/master/)
- [Faker providers](https://faker.readthedocs.io/en/master/providers.html)
- [Faker pytest fixtures](https://faker.readthedocs.io/en/master/pytest.html)
