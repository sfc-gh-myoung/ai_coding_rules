---
schema_version: v4.0
rule_version: v3.0.0
description: "Domain/locale Faker providers and bounded generation with preserved identities, versioned RNG and validated synthetic outputs."
last_updated: 2026-10-07
keywords:
  - kw:faker localization
  - kw:custom provider
  - kw:BaseProvider extension
  - kw:DynamicProvider runtime
  - kw:streaming generator memory
  - kw:faker caching optimization
token_budget: ~800
context_tier: Low
depends:
  required:
    - 240-python-faker.md  # Core Faker patterns
  optional:
    - 240a-python-faker-testing.md  # Pytest integration and seeding
---
# Python Faker Advanced Patterns

## Scope

**What This Rule Covers:**
Requested locales, custom/dynamic provider registration, bounded performance and consistent batch/global identities.

**When to Load This Rule:**
When Faker needs domain providers/localization or measured volume optimization; read test companion for fixture isolation.

## Contract

### Inputs and Prerequisites

- Existing providers/registration and installed Faker version, actual locale/domain rules, required dataset size and output destination.
- Seed/time/version/order, relational/uniqueness scope and measured CPU/memory baseline.

### Mandatory

- Check built-in/previous providers before custom ones; load only required locales and verify every needed provider's actual format/fallback. Multi-locale choice is sampling, not ordered fallback, and random currencies need not match a country.
- Extend supported BaseProvider/DynamicProvider API with deterministic instance RNG and validated input pools. Later registrations can override methods; name conflicts and order must be intentional and tested.
- Dynamic external/config source pools must be authorized, bounded and parsed safely; synthetic output doesn't anonymize real customer values. No unapproved database/API fetch or sensitive list in a provider.
- Use suitable provider methods for discoverability, but fake.random is a supported generator RNG and isn't inherently unseeded. Decimal/scaled money and distribution requirements matter more than claiming pyfloat universally superior.
- Keep seeds/version/order/frozen time stable and test two independent instances. Caches change the generated distribution and RNG consumption; document effect rather than assert equivalent output automatically.
- Choose streaming/chunks from actual memory/latency/downstream fit; no fixed 1000/100000/one-million-record threshold or guaranteed ten-thousand/sec. A generator isn't memory-flat if callers collect it or unique/error pools grow indefinitely.
- Maintain global sequence/namespace across batches. Restarting a user generator at id=1 each chunk duplicates identifiers; track source index, parent references and resume/checkpoint consistently.
- Bound count/batch parameters, output bytes and caches; permit final partial batch. Downstream loads/writes require separate approval and count/key/type reconciliation, not implicit database insertion.
- Synthetic contact domains use safe non-actionable values, not public Gmail identities for automated sends. Custom packaging/publication is only justified for actual cross-project reuse and explicitly authorized.

### Execution Steps

1. Inspect current providers/requirements and benchmark permitted representative generation.
2. Implement smallest constrained provider/locale/stream/cache with stable relational identities.
3. Test registration collisions, reproducibility, boundary/exhaustion and cross-batch count/key integrity.
4. Run project checks and report actual speed/memory and generated-output limitations.

### Validation

- Required locale/provider contract and seeded domain distributions verified, no leaked real data.
- IDs/relationships/counts remain consistent across chunks/resume; memory/caches actually bounded.
- Performance measured rather than guaranteed, destination/dependency/publication scope respected.

## References

- [Faker providers](https://faker.readthedocs.io/en/master/providers.html)
- [Faker generator/RNG](https://faker.readthedocs.io/en/master/)
- [DynamicProvider](https://faker.readthedocs.io/en/master/providers/dynamic.html)
