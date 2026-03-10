# Snowflake Application Deployment Automation - Core Patterns

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential App Deployment patterns. Load for deployment tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:app-deployment, kw:deploy
**Keywords:** CREATE NOTEBOOK, stages, deployment automation, SiS, deploy app, deployment pipeline, app publishing, deployment patterns, deploy to snowflake, stage deployment, production deployment, app versioning, automated deployment
**TokenBudget:** ~3650
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md, 109-snowflake-notebooks.md, 101-snowflake-streamlit-core.md, 820-taskfile-automation.md

## Scope

**What This Rule Covers:**
Core deployment automation patterns for Snowflake applications (Notebooks, Streamlit apps, UDFs, and other staged applications), ensuring reliable, deterministic deployments through proper stage file management and object lifecycle control.

**When to Load This Rule:**
- Deploying Streamlit apps to Snowflake
- Automating notebook deployments
- Managing staged application files
- Implementing deployment pipelines
- Controlling application lifecycle in Snowflake

## References

### External Documentation
- [CREATE NOTEBOOK](https://docs.snowflake.com/en/sql-reference/sql/create-notebook) - Official Notebook deployment syntax
- [PUT Command](https://docs.snowflake.com/en/sql-reference/sql/put) - Stage file upload reference
- [Internal Stages](https://docs.snowflake.com/en/user-guide/data-load-stages-intro) - Stage management guide

### Related Rules
- **Snowflake Notebooks**: `109-snowflake-notebooks.md` - Core notebook patterns
- **Streamlit Core**: `101-snowflake-streamlit-core.md` - Streamlit app development
- **Taskfile Automation**: `820-taskfile-automation.md` - Task automation patterns
- **Troubleshooting**: `109c-snowflake-app-deployment-troubleshooting.md` - Deployment debugging

## Contract

### Inputs and Prerequisites
- Snowflake connection and credentials
- Application files ready for deployment (.ipynb, .py, environment.yml)
- Taskfile.yml structure in place
- Internal stages created in target schemas
- SQL scripts for upload/remove/create operations

### Mandatory
- 5-step deployment workflow: DROP, REMOVE, upload (PUT), CREATE, deploy (orchestrator)
- `AUTO_COMPRESS=FALSE` on all PUT commands for `.py`, `.yml`, `.ipynb` files
- Explicit `REMOVE @stage/file` before every `PUT` (not just `OVERWRITE=TRUE`)
- `ROOT_LOCATION` in CREATE must match actual stage file paths
- Taskfile.yml automation (no manual Snowsight UI deployments)
- SQL scripts stored in version control, not inline in YAML
- Snowflake CLI minimum version: 3.12+ (`uvx --from=snowflake-cli>=3.12 snow`) — verify against [Snowflake CLI releases](https://docs.snowflake.com/en/developer-guide/snowflake-cli/index) for latest requirements

### Forbidden
- Manual file uploads via Snowsight UI (not reproducible)
- Hardcoded credentials in automation scripts. Use environment variables or Snowflake CLI connection configuration (`~/.snowflake/connections.toml`). Never embed credentials in Taskfile.yml or SQL scripts.
- Deployment without version control
- Mixing deployment modes (don't deploy same app to multiple stages)

### Execution Steps
1. Create SQL scripts for each operation (upload, remove, create, drop)
2. Implement task structure with 5 core operations
3. Test deployment workflow end-to-end
4. Document deployment process and troubleshooting
5. Validate with actual deployment to Snowflake

### Output Format
- Taskfile.yml with modular deployment tasks
- SQL script files in organized directory structure
- Documentation of deployment workflow

### Validation
- Deploy to dev environment and verify object creation
- Run `task app:deploy-dev` successfully
- Check Snowsight for deployed notebook/streamlit
- Test application functionality in Snowflake
- Verify SQL scripts execute without errors

### Design Principles
- **Explicit Over Implicit:** Always use explicit REMOVE before PUT to ensure clean state
- **Modular Operations:** Break deployment into discrete, testable steps
- **Idempotent by Design:** All operations should be safely repeatable
- **Stage as Source of Truth:** Application files in stage are the canonical source
- **Separation of Concerns:** Object lifecycle (drop/create) separate from file management (remove/upload)

### Post-Execution Checklist

See detailed Post-Execution Checklist below for comprehensive deployment validation steps.

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Skipping REMOVE Step**
```sql
-- Bad: Only PUT + CREATE without REMOVE
PUT file://./apps/my_app.py @apps_stage/my_app AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
CREATE STREAMLIT my_app ROOT_LOCATION = '@apps_stage/my_app';
```
**Problem:** Stale files from previous deployments remain on stage, causing import errors and version conflicts.

**Correct Pattern:**
```sql
-- Good: Always REMOVE before PUT
REMOVE @apps_stage/my_app;
PUT file://./apps/my_app.py @apps_stage/my_app AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
CREATE STREAMLIT my_app ROOT_LOCATION = '@apps_stage/my_app';
```
**Benefits:** Clean slate for each deployment; no version conflicts; predictable state.

**Anti-Pattern 2: Using AUTO_COMPRESS=TRUE**
```sql
-- Bad: Default AUTO_COMPRESS causes import errors
PUT file://./apps/*.py @apps_stage/my_app AUTO_COMPRESS=TRUE;
```
**Problem:** Snowflake compresses .py files to .py.gz, breaking Python imports with `TypeError: expected str, bytes or os.PathLike object, not NoneType`.

**Correct Pattern:**
```sql
-- Good: Explicitly disable compression for Python files
PUT file://./apps/*.py @apps_stage/my_app AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```
**Benefits:** Python imports work correctly; no compression-related errors.

**Anti-Pattern 3: Inverted Compression Flag in Python/CLI Wrappers**
```python
# Bad: Flag logic is inverted — --no-auto-compress is NEVER passed
def stage_copy(path, stage, auto_compress=True, recursive=False):
    flags = ["--overwrite"]
    if auto_compress:                   # Only adds flag when True
        flags.append("--auto-compress") # Wrong flag name AND wrong condition
    # When auto_compress=False: no flag added → CLI uses default (compress ON)
    # Result: .py files silently uploaded as .py.gz → SiS TypeError
```
**Problem:** The `snow stage copy` CLI **auto-compresses by default**. To disable compression, you must explicitly pass `--no-auto-compress`. A wrapper that only adds a flag when `auto_compress=True` (or uses `--auto-compress` instead of `--no-auto-compress`) never actually disables compression. Files are silently compressed, deployment reports `[PASS]`, but the app fails at runtime with `TypeError`.

**Correct Pattern:**
```python
# Good: Default to no compression for application deployments
def stage_copy(path, stage, auto_compress=False, recursive=False):
    flags = ["--overwrite"]
    if not auto_compress:                  # Explicitly disable when False
        flags.append("--no-auto-compress") # Correct flag name
    if recursive:
        flags.append("--recursive")
    # Default auto_compress=False ensures safe SiS deployments
```
**Key Rules:**
- Default `auto_compress` parameter to `False` for application deployment functions
- Use `--no-auto-compress` (not `--auto-compress false` or absence of flag)
- Test by running `LIST @stage` after upload and verifying `.py` not `.py.gz`

**Anti-Pattern 4: Manual Deployment via Snowsight UI**
```
Bad: Manually upload files via UI, then Create app via UI
```
**Problem:** Not reproducible; no version control; error-prone; can't automate; team knowledge siloed.

**Correct Pattern:**
```yaml
# Good: Automated deployment via Taskfile
tasks:
  deploy:app:
    desc: Deploy application (reproducible, version-controlled)
    cmds:
      - task: drop:app
      - task: remove:app
      - task: upload:app
      - task: create:app
```
**Benefits:** Reproducible; version-controlled; automated; team-friendly; testable.

## Post-Execution Checklist

- [ ] Task structure includes all 5 operations (upload, create, drop, remove, deploy)
- [ ] SQL scripts organized in directory structure (upload/, remove/, create/, drop/)
- [ ] Explicit REMOVE task implemented before upload
- [ ] deploy task runs full workflow: drop, then remove, then upload, then create
- [ ] Preconditions check for required files before upload
- [ ] Stage names fully qualified (DB.SCHEMA.STAGE)
- [ ] Snowflake variables use `<%VARIABLE%>` syntax
- [ ] Task descriptions are clear and user-friendly
- [ ] silent: true added to tasks with multiple echo statements
- [ ] Deployment validated end-to-end in Snowflake
- [ ] AUTO_COMPRESS=FALSE specified for all Streamlit PUT commands (mandatory for SiS)
- [ ] Python/CLI wrappers pass `--no-auto-compress` (not absence of `--auto-compress`)
- [ ] Verified with `LIST @stage` that files show `.py` not `.py.gz` after upload
- [ ] environment.yml with pinned Streamlit version (>=1.50) included in stage
- [ ] Stage paths match ROOT_LOCATION (no extra subdirectory nesting)

## Validation

- **Success Checks:**
  - `task --list` shows all 5 required operations
  - Individual tasks run successfully in isolation
  - deploy task completes full workflow without errors
  - Stage shows files with correct timestamp after upload
  - Application accessible in Snowsight after create
  - Application shows updated content after full deploy

- **Negative Tests:**
  - REMOVE with non-existent file succeeds with warning (idempotent)
  - CREATE without stage files fails gracefully
  - DROP non-existent object succeeds (IF EXISTS)
  - Upload without precondition file fails before attempting upload

> **Investigation Required**
> When applying this rule:
> 1. **Read existing deployment scripts BEFORE creating new ones** - Check Taskfile, SQL patterns, stage paths
> 2. **Verify stage structure** - List stage contents to understand organization
> 3. **Never assume stage paths** - Check ROOT_LOCATION in existing CREATE statements
> 4. **Check Taskfile patterns** - Match existing task naming and structure
> 5. **Test deployment** - Run in dev environment before suggesting for production
>
> **Anti-Pattern:**
> "Creating deployment script... (without checking existing patterns)"
> "Using AUTO_COMPRESS=TRUE... (causes import errors)"
>
> **Correct Pattern:**
> "Let me check your existing deployment setup first."
> [reads Taskfile.yml, checks SQL scripts, lists stage]
> "I see you use 3-step deployment with AUTO_COMPRESS=FALSE. Following this pattern for the new app..."

## Output Format Examples

```yaml
# task/app/Taskfile.yml
version: '3.45'
set: [pipefail]

vars:
  SNOWFLAKE_DB: MY_DB
  SNOWFLAKE_WH: MY_WH
  APP_DIR: apps

tasks:
  drop:app:
    desc: Drop application object
    silent: true
    cmds:
      - echo "Dropping application object..."
      - task: utils:sql:template
        vars: {SQL_FILE: sql/operations/app/drop/drop_app.sql}

  remove:app:
    desc: Remove application files from stage
    silent: true
    cmds:
      - echo "Removing files from stage..."
      - task: utils:sql:template
        vars: {SQL_FILE: sql/operations/app/remove/remove_app_files.sql}

  upload:app:
    desc: Upload application files to stage
    silent: true
    cmds:
      - echo "Uploading files to stage..."
      - task: utils:sql:template
        vars: {SQL_FILE: sql/operations/app/upload/upload_app_files.sql}
    preconditions:
      - test -f {{.APP_DIR}}/app.py

  create:app:
    desc: Create application from staged files
    silent: true
    cmds:
      - echo "Creating application..."
      - task: utils:sql:template
        vars: {SQL_FILE: sql/operations/app/create/create_app.sql}

  deploy:app:
    desc: Deploy application (drop + remove + upload + create)
    silent: true
    cmds:
      - echo "Deploying application to Snowflake..."
      - task: drop:app
      - task: remove:app
      - task: upload:app
      - task: create:app
      - echo "Application deployed successfully"
```

## Core Deployment Pattern

### The 5-Step Workflow

Every Snowflake application deployment should support these 5 operations:

```yaml
# Required task structure for each application
tasks:
  upload:    # Upload files to stage (PUT)
  create:    # Create object from staged files (CREATE NOTEBOOK/STREAMLIT)
  drop:      # Drop object (DROP NOTEBOOK/STREAMLIT)
  remove:    # Remove files from stage (REMOVE @stage/file)
  deploy:    # Full workflow - drop, then remove, then upload, then create
```

### Why This Structure?

**Two Distinct Lifecycles:**
- **Object Lifecycle:** Snowflake metadata (notebook/Streamlit object)
  - Managed by: `drop` and `create` tasks
  - Commands: `DROP NOTEBOOK`, `CREATE NOTEBOOK`

- **File Lifecycle:** Physical files in stages
  - Managed by: `remove` and `upload` tasks
  - Commands: `REMOVE @stage/file`, `PUT file @stage`

**Analogy:**
- Object (notebook/Streamlit) = Shortcut/link
- Stage file (.ipynb/.py) = Actual file
- Both must be managed for reliable deployment

## Directory Structure

### Recommended Layout

Directory structure for `project/`:
- **task/** - Taskfile definitions
  - **notebook/** - `Taskfile.yml` (Notebook deployment tasks)
  - **streamlit/** - `Taskfile.yml` (Streamlit deployment tasks)
- **sql/operations/** - SQL scripts by app type
  - **notebook/** - Notebook-specific scripts
    - **upload/** - `upload_*.sql`
    - **remove/** - `remove_*.sql`
    - **create/** - `create_*.sql`
    - **drop/** - `drop_*.sql`
  - **streamlit/** - Same structure as notebook
- `Taskfile.yml` - Root taskfile with includes

## SQL Script Patterns

> For complete SQL script templates (upload/PUT, remove, create, drop) and CLI-based recursive upload patterns, see **109g-snowflake-app-deployment-sql-scripts.md**.

**Key rules:**
- `AUTO_COMPRESS=FALSE` is mandatory for all .py, .yml, .ipynb files
- Explicit `REMOVE @stage/file` before every `PUT`
- `ROOT_LOCATION` in CREATE must match actual stage file paths
- For multi-file apps, use `snow stage copy --recursive --no-auto-compress`

## Taskfile Implementation

> For complete Taskfile implementation with task definitions, variables, includes, preconditions, and deployment validation, see **109h-snowflake-app-deployment-taskfile.md**.

**Key structure:** Each application needs 5 tasks: `upload`, `create`, `drop`, `remove`, `deploy` (which runs drop, remove, upload, create in order).

> **CI/CD integration:** Taskfile tasks can be called directly from GitHub Actions or GitLab CI pipelines. See **109i-snowflake-app-deployment-advanced.md** for environment-specific deployment patterns.

## Deployment Validation

### Post-Deployment Checklist

```bash
# 1. Verify task structure
task --list | grep notebook
# Should show: drop, remove, upload, create, deploy

# 2. Verify stage contents
uvx snow sql -q "LIST @DB.SCHEMA.NOTEBOOK_STAGE;"
# Should show app.ipynb with recent timestamp

# 3. Verify object exists
uvx snow sql -q "SHOW NOTEBOOKS IN SCHEMA DB.SCHEMA;"
# Should show your notebook

# 4. Test in Snowsight
# Navigate to Projects > Notebooks
# Open notebook
# Run cells to verify functionality
```

### Deployment Metrics

**Target Performance:**
- `drop` task: < 2 seconds
- `remove` task: < 1 second
- `upload` task: < 5 seconds (depends on file size)
- `create` task: < 3 seconds
- **Total deployment:** < 15 seconds

## Advanced Patterns

### Rollback Strategy

If deployment fails: re-deploy the previous version using the same 5-step workflow with the previous file versions. For quick rollback, keep the last known-good files in a `_backup/` directory on your local machine and re-run `task deploy:app` pointing to those files.

> For multi-environment deployment (dev/qa/prod), deployment with validation gates, and rollback/recovery procedures, see **109i-snowflake-app-deployment-advanced.md**.
