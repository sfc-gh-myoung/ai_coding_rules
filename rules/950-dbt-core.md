---
schema_version: v4.0
rule_version: v3.0.0
description: "dbt Projects on Snowflake: account-aware object model (live or versioned), credential-free profiles, governed dependencies, approved deploy/execute/schedule and verified runs."
last_updated: 2026-10-07
keywords:
  - kw:dbt project object
  - kw:EXECUTE DBT PROJECT
  - kw:profiles.yml snowflake
  - kw:snow dbt deploy
  - kw:dbt workspaces
  - kw:dbt external access integration
token_budget: ~1400
context_tier: High
depends:
  required:
    - 100-snowflake-core.md  # Snowflake SQL patterns, object naming, security
    - 200-python-core.md  # Python development standards (dbt uses Python)
  optional:
    - 951-create-dbt-semantic-view.md  # Building Snowflake semantic views as dbt materializations
    - 104-snowflake-streams-tasks.md  # Task scheduling patterns for orchestrating dbt runs
    - 111-snowflake-observability-core.md  # Telemetry setup for dbt monitoring
---
# dbt Projects on Snowflake

## Scope

**What This Rule Covers:**
DBT PROJECT objects, Workspaces development, `profiles.yml`/`env.yml`, dependencies and external access, `snow dbt deploy/execute`, `EXECUTE DBT PROJECT`, task scheduling, access control, monitoring and troubleshooting.

**When to Load This Rule:**
When creating, deploying, executing, scheduling or debugging dbt projects inside Snowflake; load `951-create-dbt-semantic-view.md` for semantic view materializations.

## Contract

### Inputs and Prerequisites

- Existing dbt project (`dbt_project.yml`, `profiles.yml`, packages, env files), target dbt version and the source (Git repository stage, named stage, workspace).
- Account's dbt project object model (single mutable `live` version under the 2026_06 behavior bundle, or legacy immutable `VERSION$N`), roles, warehouses, integrations, Snowflake CLI version and authority for each mutation.

### Mandatory

- Read the project and inspect existing objects with `SHOW DBT PROJECTS`/`DESCRIBE DBT PROJECT` before changing anything; `default_version` of `LIVE` indicates the live-version model.
- Creating or altering DBT PROJECT objects, schemas, network rules, external access integrations, tasks, grants or schema telemetry levels, and running `EXECUTE DBT PROJECT`, are Snowflake mutations or compute use requiring explicit approval and the intended role and warehouse.
- `profiles.yml` uses `type: snowflake` with target database, schema, role and warehouse; execution uses the Snowflake session, so never put passwords, keys or tokens in profiles. Follow current docs for required `account`/`user` fields rather than real credentials.
- Verify the target database and schemas exist or that the profile role may create them; the effective privileges combine the executing user and the profile role.
- Manage secrets for private packages through `env.yml` referencing Snowflake secrets, not inline in `packages.yml` or `ENV_VARS`; `ENV_VARS` keys are uppercase with a `DBT_` prefix.
- Resolve dependencies deliberately: include `dbt_packages/` from a local or workspace `dbt deps`, or provide `EXTERNAL_ACCESS_INTEGRATIONS` scoped to the required hosts only. Use `local_packages/` for cross-project dependencies rather than `../` paths.
- Live-version model: files are mutable through deploy, PUT/COPY FILES and write-back, and earlier versions are not retained, so rely on Git or source history for rollback and use run artifacts for `--state`, `dbt retry` and Slim CI. Legacy versioned model: add versions with `ALTER DBT PROJECT ... ADD VERSION` and avoid `CREATE OR REPLACE`, which resets version history.
- Pin `DBT_VERSION` or the object default to a supported version and test upgrades in development first.
- Run tests with or after models (`dbt build`, or a run task followed by a test task); create tasks suspended, resume children before the root, and set failure notifications.
- Grant least privilege: CREATE DBT PROJECT on the schema to deployers, USAGE to executors, MONITOR to observers; keep OWNERSHIP with the deployment role.
- Enable only the logging, tracing and metric levels the team will use, with awareness of event table cost, and inspect results through execution history, `SYSTEM$GET_DBT_LOG` and artifacts.
- CI/CD uses approved non-interactive auth (key pair, OIDC or workload identity) via secret stores, and `--force` deployment only where replacing files is intended.
- Verify execution results (success flag, test failures, materialized objects) from actual runs; do not claim deployment or data correctness from compiled SQL alone.

### Execution Steps

1. Read project files and inspect existing objects, version model, integrations, roles and schedules.
2. Prepare profiles, env files, dependencies and integration changes within approved scope.
3. With approval, deploy, execute in development, then schedule or promote, observing ownership and cleanup.
4. Report objects, versions or live state, commands, run evidence and remaining risks.

### Validation

- Object model identified and deployment method consistent with it; history or rollback path known.
- No credentials in profiles, packages or env vars; secrets via env.yml and Snowflake secrets.
- Dependencies resolved with minimal egress; dbt version pinned.
- Runs and tests succeeded in the target, tasks resumed intentionally and grants least privilege.

## References

- [dbt Projects on Snowflake](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake)
- [EXECUTE DBT PROJECT](https://docs.snowflake.com/en/sql-reference/sql/execute-dbt-project)
- [Live version behavior change](https://docs.snowflake.com/en/release-notes/bcr-bundles/2026_06/bcr-2362)
- [Dependencies](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-dependencies)
- [Access control](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-access-control)
- [Monitoring](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-monitoring-observability)
- [snow dbt deploy](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/dbt-commands/deploy)
