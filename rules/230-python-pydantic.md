---
schema_version: v4.0
rule_version: v5.0.0
description: "Pydantic v2 validated model contracts, safe pure validators, coercion/NULL/default semantics and controlled serialization."
last_updated: 2026-10-07
keywords:
  - kw:BaseModel inheritance
  - kw:Field constraints
  - kw:@field_validator decorator
  - kw:@model_validator decorator
  - kw:ConfigDict settings
  - kw:discriminated unions
token_budget: ~1150
context_tier: High
depends:
  required:
    - 200-python-core.md
---
# Python Pydantic Data Validation Best Practices

## Scope

**What This Rule Covers:**
Typed model/Field/config, pure reusable/nested/discriminated validation, assignment/copy safety and explicit serialization contracts.

**When to Load This Rule:**
When defining or validating Pydantic models; read `230a-python-pydantic-settings.md` for configuration and `230b-python-pydantic-integration.md` for serialization/API/ORM integration.

## Contract

### Inputs and Prerequisites

- Existing model/validator/config/API organization, actual Pydantic/runtime/toolchain and required extras.
- Domain field/type/precision/NULL/coercion/security semantics, permitted transformations and expected input/output/error schemas.

### Mandatory

- Read current model/versions and reuse owners before changes. v2 APIs aren't interchangeable with v1; migration requires scope review. Match manager/lock and extras, no redundant pydantic plus pydantic[email] install or forced version churn.
- Type model fields and define actual constraints with Field/Annotated/custom validators. ConfigDict is a typed convenience; supported dict model_config isn't invalid. Don't require all business authorization/database validation to live inside Pydantic.
- Decide coercion versus strictness, extra fields, aliases/name population, enum and assignment/revalidation behavior from contract. Shape validation is not trusted identity or permission, and schema metadata isn't enforcement of every downstream rule.
- Optional type and default are distinct: T|None without default can still be required. Use default_factory for per-instance mutable/time defaults when clarity/lifecycle needs it; Pydantic handles many mutable defaults by copy, so don't claim shared-state behavior blindly.
- Validators are pure deterministic validation/approved normalization: no files/directories/network/database actions. Before validators accept arbitrary input and must check type before string/dict methods; after validators receive parsed values, and cross-field order/mode matters.
- Use field_validator/model_validator and proper return contracts; raise supported meaningful validation exceptions rather than assert for business checks. Defaults aren't always validated without validate_default; assignment validation and nested mutations have limits.
- Normalize only legitimate domain values; don't lowercase arbitrary email local parts, invent banned product names/price bounds or strip punctuation as security. Decimal/timezone/precision and regex coverage follow actual data requirements.
- Handle nested models and discriminated unions with explicit tagged variants; test invalid/missing tags, subtype and extra-field behavior. Native type coercion or matching a regex doesn't establish existence/format authorization.
- Pydantic model validation and dump are runtime mechanisms, not compile-time proof. A raw dict returned through an actual API response_model can be validated/projected; prefer explicit public response fields rather than universal dict ban.
- model_construct bypasses validation; model_copy(update=...) doesn't validate supplied updates. Restrict to verified trusted data or explicitly revalidate. No silent mass assignment or widening allowed fields on update.
- computed_field is included in serialization; inspect input versus serialization JSON schema modes and recursion/sensitive fields. model_dump Python versus JSON mode and exclude_unset/none/defaults differ; test actual round-trip and field omission.
- from_attributes can trigger property/lazy-ORM access; don't expose sensitive subclasses/extra fields or perform blocking ORM work implicitly inside an async serializer. Use explicit materialized response data and preserve role boundaries.
- ValidationError can contain raw sensitive input/ctx and non-JSON exception objects; sanitize safe field/messages for external output. SecretStr masks representations but is not encrypted storage or protection from custom dump/value access.
- Test valid/invalid/boundary/empty/NULL/coercion/default/nested/copy/alias/serialization cases independently. Document schema/validator rationale and run project lint/format/type/tests, with no unapproved package or external calls.

### Execution Steps

1. Inspect existing versions/model contracts and precise fields/security semantics.
2. Implement minimal typed constraints/config and pure validators/nested union logic.
3. Test accepted/rejected and serialization/default/update boundaries with independent expected values.
4. Run project checks and report compatibility/output/error behavior plus remaining integration gaps.

### Validation

- Types/constraints/default/NULL/strict/alias/extra behavior match actual contract.
- Pure validators handle arbitrary before inputs and parsed after/cross-field values; no side effects.
- Public serialization/copies/construct/ORM/error handling preserve sensitive data and validation boundaries.
- Tests/checks pass and v1/v2/runtime assumptions explicit; no fabricated compile-time or integration guarantee.

## References

- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)
- [Validators](https://docs.pydantic.dev/latest/concepts/validators/)
- [Fields/defaults](https://docs.pydantic.dev/latest/concepts/fields/)
- [Configuration](https://docs.pydantic.dev/latest/concepts/config/)
- [Serialization](https://docs.pydantic.dev/latest/concepts/serialization/)
- [Discriminated unions](https://docs.pydantic.dev/latest/concepts/unions/)
