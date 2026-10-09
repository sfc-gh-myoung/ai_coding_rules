---
schema_version: v4.0
rule_version: v3.0.0
description: "Deploying Streamlit in Snowflake: requirement-based runtime choice, runtime-correct dependency files, scoped EAIs and compute pools, live versions and approved, verifiable rollouts."
last_updated: 2026-10-07
keywords:
  - kw:container runtime
  - kw:warehouse runtime
  - kw:pyproject.toml
  - kw:external access integration
  - kw:compute pool
  - kw:runtime migration
token_budget: ~1150
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation patterns and conventions
    - 101-snowflake-streamlit-core.md  # Core Streamlit patterns and state management
  optional:
    - 101f-snowflake-streamlit-deployment-errors.md  # Deployment error troubleshooting
    - 101c-snowflake-streamlit-security.md  # Secrets management by runtime
---
# Streamlit in Snowflake Deployment

## Scope

**What This Rule Covers:**
Deploying Streamlit apps to Snowflake: container vs warehouse runtime selection, source layout, dependency files, external access integrations, compute pools, CREATE/ALTER STREAMLIT with live versions, Snowflake CLI and Workspaces deployment, verification and rollback.

**When to Load This Rule:**
When creating, updating or migrating a deployed Streamlit app; load `101f-snowflake-streamlit-deployment-errors.md` for failures and `101n-snowflake-streamlit-migration.md` for runtime migration.

## Contract

### Inputs and Prerequisites

- App source, entrypoint, dependency file, existing Streamlit object (FROM vs ROOT_LOCATION) and deployment tooling (Snowflake CLI project, Workspaces, Git, SQL).
- Account region and cloud, owner role, query warehouse, compute pools and instance families, integrations, secrets and authority for each object change.

### Mandatory

- Choose the runtime from requirements: container runtime for shared caching, PyPI packages, newer Streamlit and lower per-minute cost under frequent use (compute pool, Python 3.11); warehouse runtime for Snowflake Conda packages, per-viewer isolation or Python 3.9–3.10, or where container runtime is unavailable in the region.
- Use the runtime's dependency format at the source root: container `pyproject.toml` (recommended) or `requirements.txt`; warehouse `environment.yml` with the Snowflake channel. Pin critical versions per the runtime's version syntax and verify availability.
- Set RUNTIME_NAME explicitly: under the 2026_06 behavior bundle, omitting it creates a container-runtime app (outside government/China regions and Native Apps), whereas it previously defaulted to warehouse runtime.
- Container runtimes ship minimal preinstalled packages; additional packages or versions from PyPI or another index need an external access integration whose network rule lists only the required hosts, with USAGE granted to the app owner.
- Size compute pools from verified instance families (`SHOW COMPUTE POOL INSTANCE FAMILIES`) and actual app memory, with node counts matching concurrent apps and cost limits; pool creation, resizing and resume are approved, billed changes.
- Create apps with `CREATE STREAMLIT ... FROM` with MAIN_FILE, QUERY_WAREHOUSE and, for container runtime, RUNTIME_NAME, COMPUTE_POOL, EXTERNAL_ACCESS_INTEGRATIONS and SECRETS as needed; publish with `ALTER STREAMLIT ... ADD LIVE VERSION FROM LAST` and grant USAGE to viewer roles.
- Prefer the project's Snowflake CLI definition (`snow streamlit deploy`) or Workspaces/Git flow over manual stage uploads; when using stages, upload uncompressed and preserve directory layout.
- All CREATE/ALTER/GRANT statements and deployments are mutations requiring approval in the intended environment; avoid `CREATE OR REPLACE` on existing apps because it drops existing grants; update the source and add a new live version instead.
- Keep secrets in Snowflake SECRET objects attached per runtime rules, never in source or dependency files.
- Plan rollback before deploying: keep the previous source revision available and redeploy it as a new live version.
- Verify after deployment: app loads for owner and a viewer role, dependencies import, queries run on the intended warehouse, secrets resolve and logs are clean.

### Execution Steps

1. Read source, existing object, tooling, region and privileges; select runtime and confirm approvals.
2. Prepare dependency files, integrations, compute pool and Streamlit object definitions with least privilege.
3. Deploy through the approved tool, publish the live version and grant access.
4. Verify as owner and viewer, record evidence and the rollback path.

### Validation

- Runtime choice justified; dependency file correct and at source root.
- EAI hosts and grants minimal; compute pool sized from evidence.
- No CREATE OR REPLACE on existing apps; live version published.
- Owner and viewer verification passed; rollback path documented.

## References

- [Runtime environments](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments)
- [Dependency management](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/dependency-management)
- [File organization](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/file-organization)
- [CREATE STREAMLIT](https://docs.snowflake.com/en/sql-reference/sql/create-streamlit)
- [snow streamlit deploy](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/streamlit-commands/deploy)
