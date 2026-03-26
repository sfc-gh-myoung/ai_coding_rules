# dbt Projects on Snowflake

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-26
**Keywords:** dbt, dbt Core, Snowflake, dbt project object, EXECUTE DBT PROJECT, CREATE DBT PROJECT, profiles.yml, Workspaces, snow dbt, dbt deploy, task scheduling, dbt monitoring, dbt access control, data transformation, schema customization, generate_schema_name, dbt versioning, snow://dbt
**TokenBudget:** ~5200
**ContextTier:** High
**Depends:** 100-snowflake-core.md, 200-python-core.md

## Scope

**What This Rule Covers:**
Best practices for using dbt Projects on Snowflake, Snowflake's native integration for running dbt Core projects. Covers the full lifecycle: project setup with profiles.yml and Workspaces, deployment as DBT PROJECT objects (via SQL, Snowsight, or Snowflake CLI), execution with EXECUTE DBT PROJECT, dependency management, Task-based scheduling, monitoring and observability, access control, and CI/CD integration.

**When to Load This Rule:**
- Creating, deploying, or managing dbt projects within Snowflake
- Working with EXECUTE DBT PROJECT, CREATE DBT PROJECT, or ALTER DBT PROJECT SQL commands
- Using Snowflake Workspaces for dbt development
- Using `snow dbt deploy` or `snow dbt execute` CLI commands
- Scheduling dbt project execution with Snowflake Tasks
- Troubleshooting dbt project deployment, execution, or dependency issues

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake SQL patterns, object naming, security
- **200-python-core.md** - Python development standards (dbt uses Python)

**Recommended:**
- **104-snowflake-streams-tasks.md** - Task scheduling patterns for orchestrating dbt runs
- **111-snowflake-observability-core.md** - Telemetry setup for dbt monitoring
- **112-snowflake-snowcli.md** - Snowflake CLI patterns for `snow dbt` commands

**Related:**
- **951-create-dbt-semantic-view.md** - Building Snowflake semantic views as dbt materializations

### External Documentation

**Official Documentation:**
- [dbt Projects on Snowflake](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake) - Feature overview and key concepts
- [Deploy dbt project objects](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-deploy) - Deployment methods (Snowsight, SQL, CLI)
- [EXECUTE DBT PROJECT](https://docs.snowflake.com/en/sql-reference/sql/execute-dbt-project) - SQL command reference
- [CREATE DBT PROJECT](https://docs.snowflake.com/en/sql-reference/sql/create-dbt-project) - SQL command reference
- [Access control for dbt projects](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-access-control) - RBAC and privileges
- [Dependencies for dbt Projects](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-dependencies) - Package management
- [Monitor dbt Projects](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-monitoring-observability) - Observability and logging
- [Versioning for dbt Projects](https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-versioning) - Version management and snow://dbt/ URIs

**Tutorials:**
- [Exploring dbt Projects on Snowflake](https://www.snowflake.com/en/developers/guides/dbt-projects-on-snowflake/) - Hands-on Snowflake developer guide
- [Getting Started Tutorial](https://docs.snowflake.com/en/user-guide/tutorials/dbt-projects-on-snowflake-getting-started-tutorial) - Step-by-step tutorial with Tasty Bytes data
- [Data Teams with dbt Cloud](https://www.snowflake.com/en/developers/guides/data-teams-with-dbt-cloud/) - dbt Cloud integration guide

**CLI Reference:**
- [snow dbt deploy](https://docs.snowflake.com/en/developer-guide/snowflake-cli/dbt/deploy) - CLI deployment reference
- [snow dbt execute](https://docs.snowflake.com/en/developer-guide/snowflake-cli/dbt/execute) - CLI execution reference

## Contract

### Inputs and Prerequisites

- Snowflake account with dbt Projects on Snowflake enabled
- A valid dbt project directory containing `dbt_project.yml` and `profiles.yml`
- Understanding of dbt Core concepts (models, sources, refs, tests)
- Snowflake role with CREATE DBT PROJECT privilege on target schema
- Warehouse available for dbt execution
- If using packages: External Access Integration configured for `hub.getdbt.com` and `codeload.github.com`
- If using Workspaces: Git repository connected via API Integration

### Mandatory

- MUST use `profiles.yml` with `type: snowflake` for all dbt projects deployed to Snowflake
- MUST leave `account` and `user` fields empty in `profiles.yml` (Snowflake uses current context)
- MUST ensure target schema exists before deployment (unlike dbt Core, Snowflake does not create schemas automatically)
- MUST use `snow dbt deploy` or `CREATE DBT PROJECT` to create the DBT PROJECT object before executing
- MUST deploy dependencies via one of: (a) `dbt deps` in Workspace with External Access Integration, (b) `dbt deps` locally then deploy with `snow dbt deploy`, or (c) set EXTERNAL_ACCESS_INTEGRATIONS on the DBT PROJECT object for automatic `dbt deps` during compilation
- MUST use EXECUTE DBT PROJECT (SQL) or `snow dbt execute` (CLI) to run dbt commands against deployed objects
- MUST grant USAGE privilege on the DBT PROJECT object to roles that need to execute it
- MUST set LOG_LEVEL, TRACE_LEVEL, and METRIC_LEVEL on the schema for monitoring

### Forbidden

- Running `dbt run` or `dbt build` directly against a deployed DBT PROJECT object from outside Snowflake (use EXECUTE DBT PROJECT instead)
- Modifying files in a deployed DBT PROJECT version (versions are immutable; create a new version with ALTER DBT PROJECT ADD VERSION)
- Embedding Git tokens in `packages.yml` without encryption
- Using internal user stages or table stages as source for CREATE DBT PROJECT (use named stages, Git stages, or Workspaces)
- Using `../` relative paths for cross-project dependencies (use `local_packages/` pattern instead)
- Setting `account` or `user` to actual values in `profiles.yml` for Snowflake-native execution (leave empty)

### Execution Steps

1. **[~5 min] Create profiles.yml** with target warehouse, database, schema, and role. Set `type: snowflake`. Leave `account` and `user` empty:
   ```yaml
   my_profile:
     target: dev
     outputs:
       dev:
         database: MY_DB
         role: MY_ROLE
         schema: MY_SCHEMA
         type: snowflake
         warehouse: MY_WH
         account: ''
         user: ''
   ```
2. **[~5 min] Set up External Access Integration** (if using dbt packages):
   ```sql
   CREATE OR REPLACE NETWORK RULE dbt_network_rule
     MODE = EGRESS TYPE = HOST_PORT
     VALUE_LIST = ('hub.getdbt.com', 'codeload.github.com');
   CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION dbt_ext_access
     ALLOWED_NETWORK_RULES = (dbt_network_rule) ENABLED = TRUE;
   ```
3. **[~5 min] Develop and test in Workspace** - Create Workspace from Git repository, run `dbt compile`, `dbt run`, `dbt test` interactively. Use DAG view and compiled SQL preview.
4. **[~2 min] Run dbt deps** (if packages exist) - In Workspace toolbar: select `deps`, enter External Access Integration name, click Deps. Or locally: `dbt deps` then include `dbt_packages/` in deployment.
5. **[~2 min] Deploy as DBT PROJECT object** using one of:
   - Snowsight: Workspace > Connect > Deploy dbt project
   - SQL: `CREATE DBT PROJECT db.schema.project FROM '@git_stage/branches/main' EXTERNAL_ACCESS_INTEGRATIONS = (dbt_ext_access);`
   - CLI: `snow dbt deploy project_name --source /path/to/project`
6. **[~2 min] Execute the dbt project**:
   ```sql
   EXECUTE DBT PROJECT db.schema.my_project ARGS='run --target dev';
   EXECUTE DBT PROJECT db.schema.my_project ARGS='test --target dev';
   ```
7. **[~5 min] Schedule with Snowflake Tasks** for production:
   ```sql
   CREATE TASK db.schema.dbt_run_task
     WAREHOUSE = MY_WH SCHEDULE = '60 MINUTES'
     AS EXECUTE DBT PROJECT db.schema.my_project ARGS='run --target prod';
   CREATE TASK db.schema.dbt_test_task
     WAREHOUSE = MY_WH AFTER db.schema.dbt_run_task
     AS EXECUTE DBT PROJECT db.schema.my_project ARGS='test --target prod';
   ALTER TASK db.schema.dbt_test_task RESUME;
   ALTER TASK db.schema.dbt_run_task RESUME;
   ```
8. **[~2 min] Enable monitoring** on the schema:
   ```sql
   ALTER SCHEMA db.schema SET LOG_LEVEL = 'INFO';
   ALTER SCHEMA db.schema SET TRACE_LEVEL = 'ALWAYS';
   ALTER SCHEMA db.schema SET METRIC_LEVEL = 'ALL';
   ```
9. **[~2 min] Grant access** for execution and monitoring:
   ```sql
   GRANT USAGE ON DBT PROJECT db.schema.my_project TO ROLE executor_role;
   GRANT MONITOR ON DBT PROJECT db.schema.my_project TO ROLE monitor_role;
   ```

**Total estimated time:** ~30 minutes for initial setup and deployment

### Output Format

Deployed DBT PROJECT object in Snowflake; materialized dbt models (tables/views) in target database.schema; scheduled Tasks for automated execution; monitoring enabled via Snowsight Transformation > dbt Projects.

```sql
SHOW DBT PROJECTS IN SCHEMA db.schema;
DESCRIBE DBT PROJECT db.schema.my_project;
```

### Validation

**Pre-Task-Completion Checks:**
- `SHOW DBT PROJECTS IN SCHEMA db.schema;` returns the deployed project
- `DESCRIBE DBT PROJECT db.schema.my_project;` shows project details and versions
- `EXECUTE DBT PROJECT db.schema.my_project ARGS='run --target dev';` returns SUCCESS = TRUE
- Task history shows successful scheduled runs (Transformation > dbt Projects in Snowsight)

**Success Criteria:**
- DBT PROJECT object exists with at least one version
- dbt run completes without errors (SUCCESS = TRUE, EXCEPTION = None)
- dbt test completes without failures
- Materialized models appear in target schema
- Monitoring data visible in Snowsight (Transformation > dbt Projects)

**Negative Tests:**
- Executing without USAGE privilege returns access denied error
- Running `dbt deps` on deployed object does not modify files (versions are immutable)
- Missing `profiles.yml` causes deployment failure
- Non-existent target schema causes compilation failure

### Design Principles

- **Immutable versions:** Each deployment creates a new immutable version. Use ALTER DBT PROJECT ADD VERSION to update; use CREATE OR REPLACE DBT PROJECT only when resetting to version$1 is acceptable.
- **Profile-driven execution:** The `role`, `warehouse`, `database`, and `schema` in profiles.yml control where dbt materializes output. The calling user's privileges intersect with the profile role's privileges.
- **Dependencies as code:** Include all dependencies in the project before deployment, or configure EXTERNAL_ACCESS_INTEGRATIONS for automatic resolution during compilation.
- **Task DAGs for orchestration:** Chain dbt run and dbt test as sequential Tasks using AFTER clause for production reliability.

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (100-snowflake-core.md, 200-python-core.md)
- [ ] `profiles.yml` and `dbt_project.yml` present in project
- [ ] Target schema exists in Snowflake
- [ ] Role has CREATE DBT PROJECT privilege on target schema

**After Completion:**
- [ ] DBT PROJECT object created (verified with SHOW DBT PROJECTS)
- [ ] dbt run executes successfully (SUCCESS = TRUE)
- [ ] dbt test passes without failures
- [ ] Materialized models exist in target schema
- [ ] Tasks created and resumed for scheduled execution (if production)
- [ ] Monitoring enabled (LOG_LEVEL, TRACE_LEVEL, METRIC_LEVEL set on schema)
- [ ] USAGE and MONITOR grants issued to appropriate roles
- [ ] CI/CD pipeline updated with `snow dbt deploy` commands (if applicable)

## Key Concepts

### DBT PROJECT Object

A schema-level Snowflake object containing versioned dbt project source files. Created with CREATE DBT PROJECT, updated with ALTER DBT PROJECT ADD VERSION. Each version is immutable. Versions follow the pattern `version$1`, `version$2`, etc., and can be referenced via `snow://dbt/db.schema.project/version$N` URIs. CREATE OR REPLACE resets to `version$1`.

### Workspaces

Git-connected web IDE in Snowsight (Projects > Workspaces) for editing, testing, running, and deploying dbt projects. Supports creating Workspaces from Git repositories (public or private with OAuth/PAT). Provides dbt toolbar for compile/run/test/deps commands, DAG visualization, and compiled SQL preview.

### profiles.yml Configuration

Required configuration specifying target warehouse, database, schema, and role. The `type` field must be `snowflake`. The `account` and `user` fields must be present but can be empty (Snowflake uses current session context). Target schema must exist before deployment.

```yaml
my_profile:
  target: dev
  outputs:
    dev:
      database: ANALYTICS_DB
      role: DBT_ROLE
      schema: STAGING
      type: snowflake
      warehouse: DBT_WH
      account: ''
      user: ''
    prod:
      database: ANALYTICS_DB
      role: DBT_ROLE
      schema: PRODUCTION
      type: snowflake
      warehouse: DBT_WH
      account: ''
      user: ''
```

### Schema Customization

Use `generate_schema_name` macro to control materialization schemas. When `schema` config is set on a model, Snowflake concatenates it with the target schema (e.g., `target_schema_model_schema`). Override the macro in `macros/generate_schema_name.sql` for custom behavior. Target schema in `profiles.yml` must exist; custom schemas are created automatically by dbt.

### Deployment Methods

- **Snowsight:** Workspace > Connect > Deploy dbt project (creates object from workspace)
- **SQL:** `CREATE DBT PROJECT db.schema.name FROM '<source>' [EXTERNAL_ACCESS_INTEGRATIONS = (...)]`
- **CLI:** `snow dbt deploy project_name [--source /path] [--default-target prod] [--dbt-version 1.9.4]`

Source locations: Git repository stages, internal named stages, existing dbt project stages (`snow://dbt/...`), Workspaces (`snow://workspace/...`)

### Execution

```sql
EXECUTE DBT PROJECT db.schema.my_project
  ARGS = 'run --target prod --select my_model+';
```

Supported dbt commands: `run`, `test`, `build`, `compile`, `deps`, `seed`. Default command is `run` if only CLI options are specified. DBT_VERSION parameter overrides the project's pinned version.

### Access Control Privileges

- **CREATE DBT PROJECT** on schema: Create new dbt project objects
- **OWNERSHIP** on dbt project: ALTER or DROP the object
- **USAGE** on dbt project: Execute and list/get files
- **MONITOR** on dbt project: View in Snowsight monitoring

The executing user's privileges intersect with the `role` specified in `profiles.yml`.

### Dependency Management

Declare packages in `packages.yml`. Run `dbt deps` in one of:
- Workspace (requires External Access Integration)
- Local machine, then deploy entire project including `dbt_packages/`
- Automatically during deployment if EXTERNAL_ACCESS_INTEGRATIONS is set on the object

Required network rule hosts: `hub.getdbt.com`, `codeload.github.com`

Cross-project dependencies: Copy the referenced project into a `local_packages/` directory within the main project. Reference with `local: local_packages/metrics_project` in `packages.yml`.

### Monitoring and Observability

**Enable on schema:**
```sql
ALTER SCHEMA db.schema SET LOG_LEVEL = 'INFO';
ALTER SCHEMA db.schema SET TRACE_LEVEL = 'ALWAYS';
ALTER SCHEMA db.schema SET METRIC_LEVEL = 'ALL';
```

**Snowsight:** Transformation > dbt Projects shows run history, status, and parameters.

**Programmatic access:**
- `INFORMATION_SCHEMA.DBT_PROJECT_EXECUTION_HISTORY()` - Execution history table function
- `SYSTEM$GET_DBT_LOG(query_id)` - Text log output
- `SYSTEM$LOCATE_DBT_ARTIFACTS(query_id)` - Stage path to artifacts (manifest.json, compiled SQL, logs)
- `SYSTEM$LOCATE_DBT_ARCHIVE(query_id)` - ZIP file URL for download

**Tracing:** dbt executions integrate with Snowflake's OpenTelemetry tracing. View in Monitoring > Traces & Logs.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Setting account and user in profiles.yml

```yaml
# Bad: Specifying actual account and user values
my_profile:
  target: dev
  outputs:
    dev:
      account: xy12345.us-west-2
      user: jsmith
      database: MY_DB
      role: MY_ROLE
      schema: MY_SCHEMA
      type: snowflake
      warehouse: MY_WH
```

**Problem:** dbt projects execute within Snowflake under the current session context. Hardcoding account and user values can cause authentication conflicts or deployment failures across environments.

**Correct Pattern:**
```yaml
# Good: Leave account and user empty
my_profile:
  target: dev
  outputs:
    dev:
      account: ''
      user: ''
      database: MY_DB
      role: MY_ROLE
      schema: MY_SCHEMA
      type: snowflake
      warehouse: MY_WH
```

**Benefits:** Works across all Snowflake accounts and users without modification. Snowflake automatically uses the current session context.

### Anti-Pattern 2: Deploying without running dbt deps first

```sql
-- Bad: Deploying a project that references packages without installing them
CREATE DBT PROJECT db.schema.my_project
  FROM '@git_stage/branches/main';

-- Execution fails because dbt_packages/ is missing
EXECUTE DBT PROJECT db.schema.my_project ARGS='run --target dev';
```

**Problem:** If the project declares packages in `packages.yml` but `dbt_packages/` is not populated, compilation and execution fail with "package not found" errors. Deployed versions are immutable, so you cannot run `dbt deps` after deployment.

**Correct Pattern:**
```sql
-- Good: Option A - External Access Integration for automatic deps
CREATE DBT PROJECT db.schema.my_project
  FROM '@git_stage/branches/main'
  EXTERNAL_ACCESS_INTEGRATIONS = (dbt_ext_access);

-- Good: Option B - Run deps locally, deploy with all packages included
-- (local) dbt deps && snow dbt deploy my_project --source ./
```

**Benefits:** Dependencies are resolved before or during compilation. The deployed object contains all required packages.

### Anti-Pattern 3: Using CREATE OR REPLACE for routine updates

```sql
-- Bad: Resetting version history on every update
CREATE OR REPLACE DBT PROJECT db.schema.my_project
  FROM '@git_stage/branches/main';
```

**Problem:** CREATE OR REPLACE resets the version identifier to `version$1` and removes all version history and aliases. This breaks rollback capability and audit trails.

**Correct Pattern:**
```sql
-- Good: Add a new version to preserve history
ALTER GIT REPOSITORY db.schema.git_stage FETCH;
ALTER DBT PROJECT db.schema.my_project
  ADD VERSION
  FROM '@git_stage/branches/main';
```

**Benefits:** Maintains version history (version$1, version$2, etc.) for rollback and audit. Previous versions remain accessible.

### Anti-Pattern 4: Scheduling dbt run without dbt test

```sql
-- Bad: Only scheduling dbt run without test validation
CREATE TASK db.schema.dbt_run_task
  WAREHOUSE = MY_WH SCHEDULE = '60 MINUTES'
  AS EXECUTE DBT PROJECT db.schema.my_project ARGS='run --target prod';
```

**Problem:** Data quality issues go undetected. Failed tests are not caught before downstream consumers use the data.

**Correct Pattern:**
```sql
-- Good: Chain run and test as task DAG
CREATE TASK db.schema.dbt_run_task
  WAREHOUSE = MY_WH SCHEDULE = '60 MINUTES'
  AS EXECUTE DBT PROJECT db.schema.my_project ARGS='run --target prod';

CREATE TASK db.schema.dbt_test_task
  WAREHOUSE = MY_WH AFTER db.schema.dbt_run_task
  AS EXECUTE DBT PROJECT db.schema.my_project ARGS='test --target prod';

ALTER TASK db.schema.dbt_test_task RESUME;
ALTER TASK db.schema.dbt_run_task RESUME;
```

**Benefits:** Tests run automatically after each dbt run. Failures are captured in task history and can trigger alerts.

## CI/CD Integration

### Snowflake CLI Commands

```bash
snow dbt deploy my_project --source /path/to/project --default-target prod --force
snow dbt execute my_project --args 'run --target prod'
snow dbt execute my_project --args 'test --target prod'
```

### GitHub Actions Example

```yaml
- name: Deploy dbt project
  run: snow dbt deploy my_project --source ./dbt_project --force
  env:
    SNOWFLAKE_CONNECTIONS_DEFAULT_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}

- name: Execute dbt run
  run: snow dbt execute my_project --args 'run --target prod'

- name: Execute dbt test
  run: snow dbt execute my_project --args 'test --target prod'
```

## Troubleshooting

### "Package not found" during execution
**Cause:** Dependencies not installed before deployment.
**Fix:** Redeploy with EXTERNAL_ACCESS_INTEGRATIONS set, or run `dbt deps` locally and redeploy with `snow dbt deploy --force`.

### Compilation fails with "schema does not exist"
**Cause:** Target schema in `profiles.yml` does not exist.
**Fix:** Create the schema before deploying: `CREATE SCHEMA IF NOT EXISTS db.schema;`

### "Access denied" on EXECUTE DBT PROJECT
**Cause:** Missing USAGE privilege on the DBT PROJECT object, or the profile role lacks required object privileges.
**Fix:** `GRANT USAGE ON DBT PROJECT db.schema.my_project TO ROLE executor_role;` and verify the profile role has warehouse, database, and schema access.

### Task execution fails silently
**Cause:** Child tasks not resumed, or monitoring not enabled.
**Fix:** Resume all tasks in the DAG (child tasks first, then root). Enable LOG_LEVEL, TRACE_LEVEL, METRIC_LEVEL on schema. Check Transformation > dbt Projects in Snowsight.

### Deploy fails with file ordering errors
**Cause:** Bug in snowflake-cli versions before 3.16.0 caused file upload ordering issues during `snow dbt deploy`.
**Fix:** Upgrade Snowflake CLI to v3.16.0+. If unable to upgrade, retry deployment.
