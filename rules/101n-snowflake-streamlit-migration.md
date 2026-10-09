---
schema_version: v4.0
rule_version: v3.0.0
description: "Streamlit runtime migrations and in-place upgrades: prerequisites, dependency and API conversion, in-place ALTER of runtime properties, preserved grants and verified rollback."
last_updated: 2026-10-07
keywords:
  - kw:Streamlit runtime migration
  - kw:environment.yml to pyproject.toml
  - kw:get_active_session replacement
  - kw:Container Runtime infrastructure
  - kw:bidirectional runtime swap
  - kw:in-place Streamlit upgrade
token_budget: ~1000
context_tier: Low
depends:
  optional:
    - 101l-snowflake-streamlit-deployment.md  # Runtime selection, EAI setup, compute pool creation
---
# Streamlit Runtime Migration and Upgrades

## Scope

**What This Rule Covers:**
Moving Streamlit in Snowflake apps between warehouse and container runtimes, upgrading ROOT_LOCATION apps to FROM, and in-place Streamlit or dependency upgrades: prerequisites, dependency conversion, code changes, object updates, verification and rollback.

**When to Load This Rule:**
When changing an existing app's runtime, object type or dependency versions; load `101l-snowflake-streamlit-deployment.md` for integrations, pools and deployment mechanics.

## Contract

### Inputs and Prerequisites

- Existing Streamlit object (`DESCRIBE STREAMLIT`), source in version control, current dependency file, grants, secrets and viewer roles.
- Target runtime availability in the region, owner privileges (USAGE on compute pool and EAI for container runtime), Snowflake CLI version if used and approval for each change.

### Mandatory

- Back up or confirm version control of source before changes and record current object properties and grants.
- ROOT_LOCATION apps are warehouse-only; upgrade them to FROM-based objects per the documented procedure before any runtime migration.
- Warehouse to container: make the app compatible first (Python 3.11, Streamlit 1.50+), convert `environment.yml` to `pyproject.toml` or `requirements.txt` at the source root using verified PyPI names and versions, replace `get_active_session()` and `_snowflake` calls with `st.connection("snowflake")` and `st.secrets`, and review shared-server effects (module globals, caches, memory).
- Container to warehouse: confirm packages exist in the Snowflake Conda channel, convert to `environment.yml`, remove container-only features (PyPI-only packages, cross-session caches, container secrets) and use warehouse-runtime secret access.
- Migrate in place with `ALTER STREAMLIT ... SET RUNTIME_NAME` and `COMPUTE_POOL` (plus integrations and secrets) rather than DROP and CREATE, preserving the object, URL and grants; then publish a new live version.
- In-place upgrades change the dependency file in source and redeploy a new live version; test the upgrade in a development copy first and read Streamlit release notes for breaking changes.
- If a parallel copy is used for testing, deploy it under a separate name with restricted access and remove it after cutover; never drop the original before the replacement is verified.
- All ALTER/CREATE/DROP/GRANT and integration or pool changes are approved mutations; viewers may keep old warehouse sessions until they reload.
- Verify after migration as owner and viewer: app loads, imports resolve, queries run, secrets resolve, caching and memory behave and logs are clean; keep the previous runtime settings and source revision as the rollback.

### Execution Steps

1. Inspect object, source, dependencies, grants and region support; record rollback state.
2. Prepare code and dependency changes and required infrastructure with approval.
3. Apply in-place ALTER or redeploy, publish the live version and verify as owner and viewer.
4. Report changes, evidence, rollback path and follow-ups.

### Validation

- Prerequisites met; ROOT_LOCATION objects upgraded first.
- Dependencies and APIs converted for the target runtime.
- Migration done in place with grants preserved; no premature drops.
- Owner and viewer verification passed with a documented rollback.

## References

- [Migrating between runtime environments](https://docs.snowflake.com/en/developer-guide/streamlit/migrations-and-upgrades/runtime-migration)
- [Migrate from ROOT_LOCATION to FROM](https://docs.snowflake.com/en/developer-guide/streamlit/migrations-and-upgrades/root-location)
- [Types of Streamlit objects](https://docs.snowflake.com/en/developer-guide/streamlit/migrations-and-upgrades/overview)
- [ALTER STREAMLIT](https://docs.snowflake.com/en/sql-reference/sql/alter-streamlit)
- [Default container runtime behavior change](https://docs.snowflake.com/en/release-notes/bcr-bundles/2026_06/bcr-2342)
