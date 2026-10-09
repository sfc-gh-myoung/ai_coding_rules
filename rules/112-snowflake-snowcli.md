---
schema_version: v4.0
rule_version: v5.0.0
description: Version-bound Snowflake CLI automation with explicit targets, secure authentication, renderer discipline, and safe transfer/deployment controls.
last_updated: 2026-10-07
keywords:
  - kw:snowcli
  - kw:snowcli uvx pinned
  - kw:stage copy no-auto-compress
  - kw:streamlit deploy FROM
  - kw:connection profile env
  - kw:CI non-interactive json
  - kw:snowflake.yml
  - kw:snowflake.yml project
  - file:snowflake.yml
token_budget: ~1250
context_tier: Medium
depends:
  required:
    - 100-snowflake-core.md  # Snowflake foundation patterns
  optional:
    - 820-taskfile-automation.md
    - 803-project-git-workflow.md  # CI/CD integration patterns
---
# Snowflake CLI Usage Best Practices

## Scope

**What This Rule Covers:**
CLI version/environment identity, connections/authentication, SQL/project rendering, structured automation, stage transfers and scoped deployments.

**When to Load This Rule:**
When configuring or reviewing snow commands, snowflake.yml, connection profiles, CI or stage/app automation.

## Contract

### Inputs and Prerequisites

- Existing CLI installation/version, package/runtime requirements, project definition/schema, config/connection and automation helpers.
- Approved target account/role/database/schema/compute and operation scope, supported non-interactive auth and secret-store access.

### Mandatory

- Reuse project-managed installation and one reviewed version pin for automation. uvx/uv tool/pipx or supported installers can isolate tools; uvx can download packages and is not proof of full hermetic reproducibility. No global pip or unapproved dependency/environment changes.
- Verify installed version/help and exact command flags before use; do not assert a hardcoded version is installed or one old minimum applies to all features. Controlled upgrades include applicable local/dev checks and lock changes.
- Inspect existing connection config without exposing secrets or changing defaults. Bind explicit connection/account/role/context in automation and validate resolved target scope before SQL/transfers; config precedence/env keys must match actual client docs.
- Use approved SSO/key-pair/OAuth/PAT/workload identity according to environment. Browser auth is not universally CI-safe; credentials/private keys/tokens remain in approved stores and never password flags, source, logs or persisted plaintext CI artifacts.
- Connection tests contact the account and can invoke authentication. They require authorized network scope; --version/help and local config checks do not prove account connectivity or authorize SQL.
- Use structured JSON/CSV output with supported flags, exact schema parsing and stdout/stderr/exit evidence. Fail closed on unknown fields/nonzero errors; table grep and success banners are not robust verification.
- Verify actual non-interactive behavior; do not prescribe nonexistent --no-input. Supply required parameters/auth and bounded timeouts, and reject missing inputs instead of hanging or choosing production defaults.
- SQL template modes are explicit: STANDARD uses <%...%>, LEGACY uses ampersands, JINJA uses braces, NONE disables substitution. Client substitution is not SQL value binding/identifier authorization; inspect renderer and quote/escape each layer independently.
- Inspect current snowflake.yml definition_version/entity schema and included files before deploy; do not fabricate supported object/entity types or assume all versions accept one schema. Prepare local validation separately from account execution.
- Stage copy transfer direction/recursive/path/overwrite behavior is version-specific; quote local glob patterns and allowlist manifest assets. Current stage copy docs default auto-compress FALSE while SQL PUT defaults TRUE; explicitly choose plain app assets and test emitted wrapper flags.
- --overwrite/--prune/--replace/--refresh/teardown are mutations with different scopes. Inspect owned paths/objects, grants, consumers and recovery before authorization; no --force production teardown recipe.
- Streamlit modern FROM versus legacy ROOT_LOCATION and runtime dependency/live-version workflows must match actual CLI behavior. Do not claim every stage re-upload updates a copied app or universal version-specific bug without evidence.
- Debug/diagnostic logs may contain sensitive details; redact and retain within approved locations. Error classification uses message/context, not simplistic auth/object-not-found mapping or automatic privilege escalation.
- Preserve recorded failures and uncertain server outcomes; inspect current state before replaying DDL/DML/uploads/deployments. Source-control publication and external notifications remain separately authorized.

### Execution Steps

1. Inspect current tools/help, config/project/helpers and allowed operations without printing secrets.
2. Bind reviewed version/auth/target/renderer and implement minimal structured fail-closed automation.
3. Run appropriate local config/script/schema checks; test connectivity only with approval.
4. Execute scoped approved account/transfer/deployment commands and verify exact outcomes/artifact identity.
5. Report version/target/exit evidence and gaps; inspect uncertain state before approved recovery or retries.

### Validation

- Installed version/flags/project schema and renderer grounded, no guessed syntax/default or arbitrary upgrade.
- Explicit intended context/auth, secure secrets, bounded non-interactive behavior and structured error handling.
- Correct transfer manifest/path/compression and separately approved destructive/prune/refresh scope.
- Actual command and effective object/file outcomes verified, not inferred from query authorization success.
- Deliver automation/configuration and exact local/account limitations; unexecuted SQL/connectivity remains unverified.

## References

- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/index)
- [SQL execution and templating](https://docs.snowflake.com/en/developer-guide/snowflake-cli/sql/execute-sql)
- [Stage copy options and defaults](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/stage-commands/copy)
- [Project definitions](https://docs.snowflake.com/en/developer-guide/snowflake-cli/project-definitions/about)
- `100f-snowflake-connection-errors.md` for safe diagnostics.
- `109b-snowflake-app-deployment-core.md` for preserving deployment lifecycle.
