---
schema_version: v4.0
rule_version: v3.0.0
description: "Validated CLI/environment/file/default precedence, immutable per-invocation settings and secret-safe configuration reporting."
last_updated: 2026-10-07
keywords:
  - kw:Typer CLI configuration
  - kw:pydantic-settings integration
  - kw:configuration precedence chain
  - kw:environment variable prefix
  - kw:CLI option overrides
  - kw:TOML config file loading
token_budget: ~900
context_tier: Medium
depends:
  required:
    - 220-python-typer-cli.md  # Core Typer CLI patterns
  optional:
    - 230-python-pydantic.md  # Pydantic model patterns
    - 230a-python-pydantic-settings.md  # Pydantic Settings details
---
# Python Typer CLI Configuration Management

## Scope

**What This Rule Covers:**
Explicit source precedence, typed settings/file loading, CLI overrides, invocation isolation, provenance and secret-safe output.

**When to Load This Rule:**
When configuring Typer options/env/TOML sources. Read `230a-python-pydantic-settings.md` for actual settings-source APIs.

## Contract

### Inputs and Prerequisites

- Existing settings/callback/env prefix, actual Pydantic Settings version, approved config paths/formats and source precedence.
- Required values/secrets, optional defaults and override semantics; inspect schema/templates without printing secret-bearing .env files.

### Mandatory

- Extend the existing configuration owner. Support only needed sources; CLI > environment > file > defaults is a recommended explicit contract, not permission to silently change existing order or add every source.
- Implement file sources using supported settings-customise-sources/loaders or equivalent deliberate composition. BaseSettings does not load arbitrary TOML merely because config_file exists; dotenv/secrets/init have their own order. Test actual source combinations.
- Resolve explicit config path before final construction. An explicitly selected missing/malformed file fails clearly; optional absent default file can follow documented fallback. Validate schema/unknown keys and paths without file execution or arbitrary remote fetch.
- Preserve unset versus false/zero/empty/null CLI values; don't use truthiness to discard an override. Optional annotations/defaults and boolean flag syntax must match installed Typer behavior.
- Construct one final validated per-invocation settings instance and pass through ctx.obj/dependencies. Don't first instantiate required settings without CLI values or dump defaults back into highest-priority init input, masking lower sources.
- Do not mutate global shared settings/cache between CliRunner invocations. Revalidate composed values; model_copy(update=...) alone doesn't validate updates. Nested config/default factories and env_nested_delimiter must have explicit tested merge semantics.
- Fail fast on missing required credentials with no fallback/empty-secret default. SecretStr masks representations but is not encryption or an authorization boundary; retrieve actual values only at approved consumer calls and never in show-config/errors.
- Show configuration with redacted values and actual recorded provenance. model_dump doesn't identify source; never claim env/file origin from guesses. Document allowed environment names, defaults, config location and precedence.
- Keep help/version/completion independent from expensive config/service checks where possible; no startup directory writes, external calls or installs. Respect OS config conventions and authorized persistence scope.

### Execution Steps

1. Inspect current settings/sources and desired override contract; identify required values and secret-safe paths.
2. Implement explicit source composition, per-invocation validation and unset-aware CLI overrides.
3. Test CLI/env/file/default precedence, nested values, invalid/missing files, false/zero overrides and successive invocations.
4. Verify redacted config/provenance/help and project checks; report unresolved source/platform gaps.

### Validation

- All configured sources follow actual tested precedence; required CLI values can satisfy missing lower sources.
- False/zero/null/unset and nested merge semantics correct; errors nonzero and sanitized.
- No shared mutation, unvalidated copies, secret display or invented source provenance.
- Help/config discovery read-only; output documents sources/paths and actual checks.

## References

- [Pydantic Settings sources](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Typer context and callbacks](https://typer.tiangolo.com/tutorial/commands/context/)
- [Python TOML parser](https://docs.python.org/3/library/tomllib.html)
