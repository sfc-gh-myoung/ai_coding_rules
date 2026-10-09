---
schema_version: v4.0
rule_version: v3.0.0
description: "Explicit validated Pydantic Settings sources, nested environment semantics, pure startup validation and protected credentials."
last_updated: 2026-10-07
keywords:
  - kw:pydantic-settings
  - kw:BaseSettings
  - kw:environment variable loading
  - kw:SettingsConfigDict
  - kw:nested settings delimiter
  - kw:startup validation
token_budget: ~900
context_tier: Medium
depends:
  required:
    - 230-python-pydantic.md  # Core Pydantic model patterns
  optional:
    - 220a-python-typer-config.md  # CLI configuration integration
    - 210-python-fastapi-core.md  # FastAPI settings injection
---
# Python Pydantic Settings Management

## Scope

**What This Rule Covers:**
Typed source precedence, environment/nested/secret inputs, pure validation and deliberate runtime resource creation.

**When to Load This Rule:**
When implementing configuration with pydantic-settings; read CLI/FastAPI companions for injection/lifecycle when relevant.

## Contract

### Inputs and Prerequisites

- Existing settings owner/version/source order, environment prefix/aliases/nested merge and deployment configuration.
- Required versus optional values, secret mechanism and authorized startup/resources/test scope.

### Mandatory

- Reuse existing BaseSettings/source owner and installed APIs; don't force replacing another working configuration library or installing packages. SettingsConfigDict improves typed configuration; supported plain dict isn't forbidden syntax.
- Document actual priority for init/CLI/env/dotenv/files/secrets/defaults and implement needed custom sources explicitly. env_file doesn't read arbitrary TOML; source precedence and aliases/prefix/case differ by configuration.
- Namespace environment names where appropriate and retain required platform names intentionally. Prefix in comments is not active unless configured; aliases can override prefix behavior. Test actual nested JSON/delimiter/partial update semantics.
- Prefer nested BaseModel for values parsed by a parent source unless independently sourced nested BaseSettings is deliberate. default_factory on a required nested Settings can read unrelated env or fail before intended merge; test real construction.
- Fields have actual type/range/domain constraints and no secret fallback/blank default. A count of distinct characters is not a valid entropy estimate. SecretStr masks default representations, not encrypted memory/storage or custom serializer/get_secret_value leakage.
- Validate before serving traffic, but avoid eager global construction that blocks --help/tests or needed CLI overrides. Inject one scoped/cached instance with explicit cache reset/reload policy; configuration provenance isn't recoverable from model_dump alone.
- Validators remain pure: no directories/files/network/grants. Path validation versus existence/runtime creation is separate and authorization-scoped; no automatic startup mkdir just because a setting parsed.
- Construct database URLs with supported escaping/builders; interpolated password/user strings can corrupt URLs and expose secrets in logs. Reveal values only to approved consumers, redact errors/trace/config reports.
- Fail invalid/missing settings clearly at entry boundary without raw ValidationError sensitive input. Library code doesn't sys.exit unexpectedly; CLI/server owner translates failure to correct startup/error behavior.
- Test source combinations, false/zero/empty/unset, case/alias/nested fields, missing secrets, invalid files and cached reload. No production secret reads or unauthorized persistent resources.

### Execution Steps

1. Read current sources/settings and define precise priority/validation/lifecycle contract.
2. Implement minimal typed fields/pure validators and approved sources with safe injection.
3. Test actual source/nested/cache/secret/error behavior and resource-free parsing.
4. Run project checks and report effective behavior/provenance and startup gaps.

### Validation

- Source/prefix/alias/nested precedence proven by tests, required settings not masked by defaults.
- Pure parsing and scoped runtime resource creation distinct; no secret/URL/error leakage.
- Invalid startup and caching/reload behavior intentional and test-isolated.

## References

- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Secret types](https://docs.pydantic.dev/latest/api/types/#pydantic.types.SecretStr)
- [FastAPI settings lifecycle](https://fastapi.tiangolo.com/advanced/settings/)
