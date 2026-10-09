---
schema_version: v4.0
rule_version: v3.0.0
description: "CI/CD pipeline patterns for automated Snowflake SQL deployments: Makefile integration, GitHub Actions workflows, and environment-specific variable management across dev/test/prod."
last_updated: 2026-10-06
keywords:
  - kw:Makefile targets
  - kw:GitHub Actions workflows
  - kw:multi-environment deployment
  - kw:Snowflake CLI
  - kw:secrets store integration
  - kw:SQL template parameterization
  - kw:ci/cd
token_budget: ~900
context_tier: Low
depends:
  optional:
    - 102a-snowflake-sql-automation.md  # SQL automation patterns and templates
---
# Snowflake SQL: CI/CD Pipeline Integration

## Scope

**What This Rule Covers:**
Approved multi-environment SQL pipeline configuration, secret isolation, renderer/version binding, promotion and evidence.

**When to Load This Rule:**
When authoring or reviewing Snowflake deployment workflows and environment-specific template execution.

## Contract

### Inputs and Prerequisites

- Current CI/automation/CLI/auth mechanism and SQL artifact/dependency inventory.
- Authorized dev/test/prod targets, protected environments and secret-store access.

### Mandatory

- Use actual existing automation (Make/Task/scripts), not a mandatory new Makefile. Inspect CLI package/version/flags and use supported templating mode, not old package-name or renderer assumptions.
- Environment config binds account/connection/role/database/schema/warehouse explicitly; validate resolved identifiers against approved scope before DDL/DML.
- Credentials remain in approved CI secret/federated identity mechanisms, never source, password flags, command traces or persisted plaintext connection artifacts. Do not print resolved secrets.
- PR/untrusted-fork workflows must not receive production secrets or automatically deploy. Read-only validation and mutating promotion are distinct jobs with explicit environment approvals.
- Validate the same reviewed artifact in dev/test before authorized production promotion; pin relevant tools/actions by project policy and preserve reproducible lock/render configuration.
- Path triggers describe actual changed consumers; pipeline success only after all checks/loads/postconditions, no generic main-push production recipe.
- Template placeholders use the configured renderer (Snowflake CLI STANDARD for <%...%>, otherwise actual syntax). Escape/bind values and quote shell paths at their separate layers.
- Use data-preserving creation/ALTER/deterministic MERGE and scoped dependency/grant review. IF NOT EXISTS or MERGE names do not prove rerun/content safety.
- Capture exact environment/artifact/query/exit evidence, partial/failed outcomes and recovery prerequisites without confidential data upload.

### Execution Steps

1. Read current workflows/helpers/SQL and verify intended environment/auth/renderer contracts.
2. Implement minimal safe validation/deployment jobs with scoped credentials and explicit ordering.
3. Render/check locally without account mutation and inspect resolved target parameters.
4. Only under deployment approval, exercise dev/test and post-load checks, then promote reviewed artifact through protected gates.
5. Inspect failures/actual mutation state before scoped recovery; no automatic privilege escalation or broad rollback.

### Validation

- Correct target/renderer/tool bindings, secrets not exposed and untrusted workflows isolated.
- Actual dev/test outcomes precede authorized production, artifact identity preserved.
- Dependency/load/postchecks accurately sequence and report partial failures.
- Safe reruns/content verified, no blanket table/view replacement safety claim.
- Hosted results actual, unavailable pipeline/runtime tests disclosed and no deployment merely to satisfy checklist.

## References

- [Snowflake CLI SQL](https://docs.snowflake.com/en/developer-guide/snowflake-cli/sql/execute-sql)
- [Snowflake CLI GitHub Actions](https://docs.snowflake.com/en/developer-guide/snowflake-cli/cicd/integrate-ci-cd)
- [GitHub protected environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [GitHub secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)
- `102a-snowflake-sql-automation.md` for data-preserving deployment patterns.
