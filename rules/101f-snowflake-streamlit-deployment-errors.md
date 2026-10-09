---
schema_version: v4.0
rule_version: v4.0.0
description: "Diagnose Streamlit in Snowflake deployment failures from logs and object state: runtime mismatches, dependencies, EAI/network rules, compute pools, stage files and privileges."
last_updated: 2026-10-07
keywords:
  - kw:Streamlit deployment
  - kw:Container Runtime
  - kw:Warehouse Runtime
  - kw:External Access Integration
  - kw:stage upload compression
  - kw:compute pool provisioning
token_budget: ~1050
context_tier: Low
depends:
  required:
    - 101-snowflake-streamlit-core.md  # Core Streamlit patterns
  optional:
    - 101l-snowflake-streamlit-deployment.md  # Deployment guidance
---
# Streamlit Deployment Errors

## Scope

**What This Rule Covers:**
Troubleshooting failed or unhealthy Streamlit in Snowflake deployments in container and warehouse runtimes: logs, dependency resolution, external access, compute pools, stage file layout and compression, runtime API mismatches, privileges and resource limits.

**When to Load This Rule:**
When a Streamlit app fails to deploy, start, import or query; load `101l-snowflake-streamlit-deployment.md` for the deployment workflow itself.

## Contract

### Inputs and Prerequisites

- Exact error text, Streamlit object definition (`DESCRIBE STREAMLIT`), runtime, source files and dependency file, and recent changes.
- Logs (container live console, event table telemetry, `snow streamlit logs`), roles and privileges and authority for any fix.

### Mandatory

- Diagnose before changing: capture the exact error and logs, inspect the Streamlit object, runtime, compute pool, integrations and files, and match the evidence to a cause rather than applying generic fixes.
- Fixes that create or alter network rules, integrations, compute pools, warehouses, grants or Streamlit objects are mutations requiring approval; prefer the narrowest change and avoid `CREATE OR REPLACE` on shared objects.
- Runtime mismatch: `get_active_session()` and `_snowflake` are warehouse-runtime only; container runtime needs `st.connection`, `st.secrets` and Python 3.11 per current docs.
- Dependency failures: container runtime resolves `pyproject.toml`/`requirements.txt` from a package index through an EAI allowing the index hosts (for PyPI, `pypi.org` and `files.pythonhosted.org`); warehouse runtime uses Snowflake Conda channel packages in `environment.yml`. Verify package and version availability for the runtime and pin critical versions.
- API errors such as missing `st.navigation`/`st.Page` mean the selected Streamlit version is older than the feature; choose a version the runtime offers that includes the API rather than downgrading code blindly.
- Compute pool issues: confirm state, instance family capacity and USAGE privileges; resuming or resizing pools incurs cost and needs approval.
- Stage-based deploys: files must keep directory layout and be uncompressed (`--no-auto-compress`/`AUTO_COMPRESS=FALSE`); verify with `LIST` and redeploy the live version as the docs require.
- Privilege errors: grant only the missing privilege (database/schema USAGE, CREATE STREAMLIT, warehouse or compute pool USAGE, object reads) to the owning role, never broad admin roles.
- Memory and timeout errors: reduce data pulled into the app, aggregate in Snowflake and cache appropriately before increasing compute.
- Verify the fix by redeploying in a non-production or approved target and confirming the app loads, imports resolve, queries run and logs are clean; report anything unverified.

### Execution Steps

1. Collect error text, logs and object, runtime, pool, integration, file and grant state.
2. Identify the root cause and propose the minimal fix with required approvals.
3. Apply the approved fix, redeploy and re-check logs and app behavior.
4. Report cause, change, evidence and any residual risk.

### Validation

- Cause established from logs and object state, not guessed.
- Fix minimal, approved and runtime-appropriate.
- Files uncompressed and dependencies available for the runtime.
- App loads and queries succeed after redeploy, with clean logs.

## References

- [Troubleshooting Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/troubleshooting)
- [Runtime environments](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments)
- [Dependency management](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/dependency-management)
- [Logging and tracing](https://docs.snowflake.com/en/developer-guide/streamlit/features/logging-tracing)
- [snow streamlit logs](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/streamlit-commands/logs)
