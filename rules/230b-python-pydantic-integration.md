---
schema_version: v4.0
rule_version: v3.0.0
description: "Pydantic public serialization, JSON schema/ORM integration and bounded batch validation with explicit reject evidence."
last_updated: 2026-10-07
keywords:
  - kw:model_dump serialization
  - kw:TypeAdapter batch validation
  - kw:FastAPI response_model
  - kw:ORM from_attributes
  - kw:SecretStr field exclusion
  - kw:model_json_schema generation
  - kw:fastapi
token_budget: ~1100
context_tier: Medium
depends:
  required:
    - 230-python-pydantic.md  # Core Pydantic model patterns
  optional:
    - 210-python-fastapi-core.md  # FastAPI endpoint patterns
    - 206-python-pytest.md  # Pytest patterns
    - 230a-python-pydantic-settings.md  # Settings management
---
# Python Pydantic Integration and Performance

## Scope

**What This Rule Covers:**
Public/private dump boundaries, JSON/schema modes, safe ORM conversion, reusable TypeAdapters and accountable batch rejects.

**When to Load This Rule:**
When integrating model serialization/validation into APIs/ORM/batches; read settings/FastAPI/test companions when applicable.

## Contract

### Inputs and Prerequisites

- Current models/helpers and Pydantic/API/ORM versions, actual input/public output schema and confidential fields.
- Batch memory/error policy, async resource/ORM loading and known performance baseline.

### Mandatory

- Use verified v2 model_dump/model_validate/model_json_schema/model_dump_json APIs while preserving scoped migration compatibility; no duplicate helper family by default or blanket invalidity of dict model_config.
- Prefer explicit public response model/allowlist; SecretStr masks representation but secret field names/values can leak through custom serializers/internal access. Inspect excluded nested/aliased/subclass/computed fields and don't rely on masked placeholder output as omission.
- model_dump returns Python values; JSON mode/dump_json encodes supported types differently. Avoid accidental double JSON encoding in APIs and lossy default=str for dates/Decimals/objects; test actual serialized/validated round-trip semantics.
- model_validate_json can validate bytes/text directly, but request.body is a method/awaitable under some frameworks. Bound payloads and verify actual API; performance claims require measured representative data, not universal faster statements.
- Custom serializers preserve declared type/units/timezone/precision. Never format arbitrary local datetime with Z without UTC conversion or silently drop fraction/timezone precision. Alias/exclude_unset/none/default behavior explicit.
- JSON schema metadata/examples aren't validation. Use Literal/Enum/constraints for runtime choices instead of json_schema_extra enum; inspect validation versus serialization schema modes including computed fields and required/nullable distinctions.
- API response_model can validate/project dictionaries or objects under actual framework behavior; transaction success/auth/resource scopes separate. Synthetic returned id=1 isn't a persisted created user; never label a sketch production integration.
- from_attributes requires loaded authorized ORM data and active appropriate resource ownership; handle missing record before validation and avoid async lazy-load/blocking queries. Projection/serialization must not trigger unnoticed sensitive relationships or session-after-close I/O.
- Reuse TypeAdapter for supported types/list validation, don't construct it each row. Bound chunks/retained error evidence; a whole-list validation error can reject the batch, not automatically return valid subset. Choose fail-fast/quarantine/partial policy and reconcile accepted/rejected input counts/identities.
- Do not silently skip invalid records or log raw private ValidationError inputs. Track sanitized field/message/index with bounded samples and durable reject storage when required; unlimited errors list defeats memory-efficient streaming.
- No fictitious ConfigDict(slots=True) memory guarantee or unverified zero-copy/validation-bypass optimization. Benchmark actual validated pipeline; model_construct/copy bypass needs trusted contract and must not mask errors.
- Test public/private/schema/alias/date/Decimal/nested/ORM and empty/bad-row batch behavior independently; run project checks and disclose mocked versus actual database/API outcomes.

### Execution Steps

1. Read current model/helpers/API/ORM/batch and define exact output/security/error semantics.
2. Implement minimal correct dumps/schema/projection and bounded validated batch/ORM handling.
3. Test independent accepted/rejected/round-trip/public-field values and lifecycle boundaries.
4. Benchmark only approved representative scope, run project checks and report gaps.

### Validation

- Serialization modes/aliases/types/timezones/public fields agree with schema and don't expose secrets.
- Schema restrictions actually enforced, missing ORM records/lazy loading handled safely.
- Batch identities/counts/reject policy and memory bounds correct; no silent drop or fake success.
- Measured performance separate from claims; tests/checks pass without unapproved API/database effects.

## References

- [Serialization](https://docs.pydantic.dev/latest/concepts/serialization/)
- [JSON schema](https://docs.pydantic.dev/latest/concepts/json_schema/)
- [TypeAdapter](https://docs.pydantic.dev/latest/concepts/type_adapter/)
- [Performance guidance](https://docs.pydantic.dev/latest/concepts/performance/)
- [FastAPI response models](https://fastapi.tiangolo.com/tutorial/response-model/)
