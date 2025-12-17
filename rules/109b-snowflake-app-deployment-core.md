# Snowflake Application Deployment Automation - Core Patterns

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential App Deployment patterns. Load for deployment tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** CREATE NOTEBOOK, stages, deployment automation, SiS, deploy app, deployment pipeline, app publishing, deployment patterns, deploy to snowflake, stage deployment, production deployment, app versioning, automated deployment
**TokenBudget:** ~4150
**ContextTier:** Medium
**Depends:** rules/100-snowflake-core.md, rules/109-snowflake-notebooks.md, rules/101-snowflake-streamlit-core.md, rules/820-taskfile-automation.md

## Purpose
Establish core deployment automation patterns for Snowflake applications (Notebooks, Streamlit apps, UDFs, and other staged applications), ensuring reliable, deterministic deployments through proper stage file management and object lifecycle control.

## Rule Scope

Deployment automation for Snowflake applications using internal stages, covering notebooks, Streamlit apps, UDFs, and stored procedures

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for 80% of common use cases reduces need to read full sections
- **Position advantage:** Early placement benefits from slight attention bias in LLM processing (first ~20% of content receives marginally more weight)
- **Progressive disclosure:** Enables agents to assess rule relevance before loading full content
- **Human-LLM collaboration:** Useful for both human developers (quick scanning) and AI assistants (decision point)

**Note:** While LLMs read sequentially (not auto-prioritizing this section), the concentrated pattern format and early position provide practical efficiency benefits. To maximize value for agents, include in system prompts: "Read Quick Start TL;DR sections first to identify essential patterns."

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **3-step deployment** - 1) DROP object, 2) REMOVE stage files, 3) PUT + CREATE
- **Use AUTO_COMPRESS=FALSE** - Prevents TypeError on imports
- **Use OVERWRITE=TRUE** - Ensures clean deployments
- **Automate with Taskfile** - Consistent deployment commands
- **Test in dev first** - Validate before production
- **Version control SQL** - Track deployment scripts in git
- **Never skip REMOVE** - Stale files cause import errors

**Quick Checklist:**
- [ ] DROP existing object SQL created
- [ ] REMOVE stage files SQL created
- [ ] PUT with AUTO_COMPRESS=FALSE
- [ ] CREATE with correct ROOT_LOCATION
- [ ] Taskfile targets defined
- [ ] Deployment tested in dev
- [ ] SQL scripts in version control

## Contract

<contract>
<inputs_prereqs>
- Snowflake connection and credentials
- Application files ready for deployment (.ipynb, .py, environment.yml)
- Taskfile.yml structure in place
- Internal stages created in target schemas
- SQL scripts for upload/remove/create operations
</inputs_prereqs>

<mandatory>
- Task automation (Taskfile.yml)
- Snowflake CLI (`uvx snow sql`)
- SQL template files with Snowflake variables (`<%VARIABLE%>`)
- PUT, REMOVE, CREATE NOTEBOOK, CREATE STREAMLIT, DROP commands
</mandatory>

<forbidden>
- Manual file uploads via Snowsight UI (not reproducible)
- Hardcoded credentials in automation scripts
- Deployment without version control
- Mixing deployment modes (don't deploy same app to multiple stages)
</forbidden>

<steps>
1. Create SQL scripts for each operation (upload, remove, create, drop)
2. Implement task structure with 5 core operations
3. Test deployment workflow end-to-end
4. Document deployment process and troubleshooting
5. Validate with actual deployment to Snowflake
</steps>

<output_format>
- Taskfile.yml with modular deployment tasks
- SQL script files in organized directory structure
- Documentation of deployment workflow
</output_format>

<validation>
- Deploy to dev environment and verify object creation
- Run `task app:deploy-dev` successfully
- Check Snowsight for deployed notebook/streamlit
- Test application functionality in Snowflake
- Verify SQL scripts execute without errors
</validation>

<design_principles>
- **Explicit Over Implicit:** Always use explicit REMOVE before PUT to ensure clean state
- **Modular Operations:** Break deployment into discrete, testable steps
- **Idempotent by Design:** All operations should be safely repeatable
- **Stage as Source of Truth:** Application files in stage are the canonical source
- **Separation of Concerns:** Object lifecycle (drop/create) separate from file management (remove/upload)
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Skipping REMOVE Step**
```sql
-- Bad: Only PUT + CREATE without REMOVE
PUT file://@~/apps/my_app.py @apps_stage/my_app AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
CREATE STREAMLIT my_app ROOT_LOCATION = '@apps_stage/my_app';
```
**Problem:** Stale files from previous deployments remain on stage, causing import errors and version conflicts.

**Correct Pattern:**
```sql
-- Good: Always REMOVE before PUT
REMOVE @apps_stage/my_app;
PUT file://@~/apps/my_app.py @apps_stage/my_app AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
CREATE STREAMLIT my_app ROOT_LOCATION = '@apps_stage/my_app';
```
**Benefits:** Clean slate for each deployment; no version conflicts; predictable state.

**Anti-Pattern 2: Using AUTO_COMPRESS=TRUE**
```sql
-- Bad: Default AUTO_COMPRESS causes import errors
PUT file://@~/apps/*.py @apps_stage/my_app AUTO_COMPRESS=TRUE;
```
**Problem:** Snowflake compresses .py files to .py.gz, breaking Python imports with `TypeError: expected str, bytes or os.PathLike object, not NoneType`.

**Correct Pattern:**
```sql
-- Good: Explicitly disable compression for Python files
PUT file://@~/apps/*.py @apps_stage/my_app AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```
**Benefits:** Python imports work correctly; no compression-related errors.

**Anti-Pattern 3: Manual Deployment via Snowsight UI**
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

## References

### External Documentation
- [Snowflake PUT Command](https://docs.snowflake.com/en/sql-reference/sql/put) - Official SQL reference for file upload command covering AUTO_COMPRESS options, OVERWRITE behavior, parallel upload optimization, and stage path syntax (authoritative documentation for all PUT parameters)
- [Snowflake REMOVE Command](https://docs.snowflake.com/en/sql-reference/sql/remove) - Official SQL reference for stage file removal including pattern matching, recursive deletion, and idempotent behavior (critical for clean deployment workflows)
- [Snowflake Stages](https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage) - Comprehensive guide to internal and external stages, directory structures, access control, and file organization patterns (essential reading for stage architecture decisions)
- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/overview) - Official command-line interface documentation covering connection configuration, SQL execution, and automation patterns (required for deployment automation workflows)
- [Taskfile Documentation](https://taskfile.dev/) - Modern task automation framework with declarative YAML syntax, dependency management, and cross-platform support (industry-standard alternative to Makefiles with 10K+ GitHub stars)

### Related Rules
- **Snowflake Notebooks**: `rules/109-snowflake-notebooks.md`
- **Streamlit Core**: `rules/101-snowflake-streamlit-core.md`
- **Taskfile Automation**: `rules/820-taskfile-automation.md`
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **Deployment Troubleshooting**: `rules/109c-snowflake-app-deployment-troubleshooting.md` - See this rule for debugging deployment issues, SiS TypeError resolution, and anti-patterns with complete runnable code examples

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

## 1. Directory Structure

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

## 2. SQL Script Patterns

### Upload Script (PUT)

```sql
-- ============================================================================
-- Filename: upload_app_files.sql
-- Description: Upload application files to stage
--
-- Parameters:
--   STAGE        - Snowflake stage name (e.g., DB.SCHEMA.STAGE)
--   NOTEBOOK_DIR - Local directory (e.g., notebooks)
--
-- Usage:
--   snow sql -D STAGE=STG -D NOTEBOOK_DIR=notebooks -f upload_app_files.sql
-- ============================================================================

PUT 'file://<%NOTEBOOK_DIR%>/app.ipynb'
@<%STAGE%>
AUTO_COMPRESS=FALSE
OVERWRITE=TRUE;
```

**Key Parameters:**
- `AUTO_COMPRESS=FALSE` - Keep files uncompressed for Snowflake processing
- `OVERWRITE=TRUE` - Replace existing file (but explicit REMOVE is still recommended)

**MANDATORY:**
**CRITICAL for Streamlit in Snowflake (SiS):**
- `AUTO_COMPRESS=FALSE` is **mandatory**, not optional
- Python's import system cannot read gzipped .py files
- Compressed files cause: "TypeError: bad argument type for built-in operation"
- Applies to: .py files, environment.yml, all Python modules

**Stage Path Requirement:**
- Upload files directly to stage root: `@STAGE_NAME`
- **Never** use subdirectory paths like: `@STAGE_NAME/streamlit/`
- ROOT_LOCATION in CREATE STREAMLIT must match actual file location
- Subdirectory mismatch causes same "TypeError" (Snowflake cannot find files)

### Remove Script (REMOVE)

```sql
-- ============================================================================
-- Filename: remove_app_files.sql
-- Description: Remove application files from stage
-- Ensures clean deployment by removing old files before uploading new ones.
--
-- Parameters:
--   STAGE - Snowflake stage name
--
-- Usage:
--   snow sql -D STAGE=DB.SCHEMA.STAGE -f remove_app_files.sql
-- ============================================================================

REMOVE @<%STAGE%>/app.ipynb;
REMOVE @<%STAGE%>/environment.yml;
```

**Why Explicit REMOVE?**
- Prevents stale file caching issues
- Ensures clean state before upload
- More predictable than relying on OVERWRITE=TRUE alone
- Belt-and-suspenders approach for production reliability

### Create Script (CREATE NOTEBOOK/STREAMLIT)

```sql
-- ============================================================================
-- Filename: create_notebook.sql
-- Description: Create notebook object from staged files
--
-- Parameters:
--   DATABASE  - Database name
--   STAGE     - Stage name with files
--   WAREHOUSE - Compute warehouse
--
-- Usage:
--   snow sql -D DATABASE=DB -D STAGE=STG -D WAREHOUSE=WH -f create_notebook.sql
-- ============================================================================

CREATE NOTEBOOK IF NOT EXISTS <%DATABASE%>.SCHEMA.NOTEBOOK_NAME
FROM '@<%STAGE%>'
QUERY_WAREHOUSE = <%WAREHOUSE%>
MAIN_FILE = 'app.ipynb';
```

### Drop Script (DROP NOTEBOOK/STREAMLIT)

```sql
-- ============================================================================
-- Filename: drop_notebook.sql
-- Description: Drop notebook object
--
-- Parameters:
--   DATABASE - Database name
--
-- Usage:
--   snow sql -D DATABASE=DB -f drop_notebook.sql
-- ============================================================================

DROP NOTEBOOK IF EXISTS <%DATABASE%>.SCHEMA.NOTEBOOK_NAME;
```

### Streamlit Upload Script (SiS-Specific)

**Critical Requirements for Streamlit in Snowflake:**

```sql
-- ============================================================================
-- Filename: upload_streamlit_app.sql
-- Description: Upload Streamlit application files to stage (SiS deployment)
--
-- CRITICAL REQUIREMENTS:
--   1. AUTO_COMPRESS=FALSE - Python import system cannot read gzipped files
--   2. Stage root path - Files at @STAGE, not @STAGE/streamlit/
--   3. ROOT_LOCATION must match actual file locations
--
-- Parameters:
--   STAGE - Snowflake stage name (e.g., UTILITY_DEMO_V2.GRID_DATA.STREAMLIT_STAGE)
--   APP_DIR - Local Streamlit app directory (e.g., streamlit/streamlit_sis)
--
-- Usage:
--   snow sql -D STAGE=DB.SCHEMA.STAGE -D APP_DIR=streamlit/sis -f upload_streamlit_app.sql
-- ============================================================================

-- Main application file (must be at stage root)
PUT file://<%APP_DIR%>/streamlit_app.py
    @<%STAGE%>
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

-- Page files (subdirectory allowed)
PUT file://<%APP_DIR%>/pages/*.py
    @<%STAGE%>/pages/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

-- Utility files (subdirectory allowed)
PUT file://<%APP_DIR%>/utils/*.py
    @<%STAGE%>/utils/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

-- Environment specification (must be at stage root)
PUT file://<%APP_DIR%>/environment.yml
    @<%STAGE%>
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

SELECT '✓ Streamlit application files uploaded' AS progress;
```

**Key Requirements:**
- Files at stage root: `streamlit_app.py`, `environment.yml`
- Subdirectories allowed for organization: `@STAGE/pages/`, `@STAGE/utils/`
- ROOT_LOCATION in CREATE STREAMLIT matches: `'@STAGE'` (not `'@STAGE/streamlit'`)
- **Never** nest in extra subdirectory: `@STAGE/streamlit/`

**CREATE STREAMLIT Statement (matches upload paths):**
```sql
CREATE STREAMLIT IF NOT EXISTS <%DATABASE%>.<%SCHEMA%>.APP_NAME
    ROOT_LOCATION = '@<%STAGE%>'  -- Matches PUT locations
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = <%WAREHOUSE%>;
```

## 3. Taskfile Implementation

### Task Structure Per Application

```yaml
# task/notebook/Taskfile.yml
version: '3.45'

set: [pipefail]

vars:
  SNOWFLAKE_CLI_VERSION: "3.12"
  SNOWFLAKE_DB: UTILITY_DEMO_V2
  SNOWFLAKE_WH: UTILITY_DEMO_WH
  NOTEBOOK_DIR: notebooks
  SNOW_CLI_BASE: "uvx --from=snowflake-cli=={{.SNOWFLAKE_CLI_VERSION}} snow"

includes:
  utils:
    taskfile: ../utils/Taskfile.yml
    internal: true

tasks:
  # 1. DROP - Remove notebook object
  drop:app:
    desc: Drop notebook object from schema
    silent: true
    cmds:
      - echo "Dropping notebook object..."
      - task: utils:sql:template
        vars:
          SQL_FILE: sql/operations/notebook/drop/drop_app.sql
          DATABASE: "{{.SNOWFLAKE_DB}}"
      - echo "Notebook object dropped"

  # 2. REMOVE - Delete stage files
  remove:app:
    desc: Remove notebook files from stage
    silent: true
    vars:
      SNOWFLAKE_STAGE: "{{.SNOWFLAKE_DB}}.SCHEMA.NOTEBOOK_STAGE"
    cmds:
      - echo "Removing notebook files from stage..."
      - task: utils:sql:template
        vars:
          SQL_FILE: sql/operations/notebook/remove/remove_app_files.sql
          STAGE: "{{.SNOWFLAKE_STAGE}}"
      - echo "Notebook files removed from @SCHEMA.NOTEBOOK_STAGE"

  # 3. UPLOAD - Upload files to stage
  upload:app:
    desc: Upload notebook files to stage
    silent: true
    vars:
      SNOWFLAKE_STAGE: "{{.SNOWFLAKE_DB}}.SCHEMA.NOTEBOOK_STAGE"
    cmds:
      - echo "Uploading notebook files to stage..."
      - task: utils:sql:template
        vars:
          SQL_FILE: sql/operations/notebook/upload/upload_app_files.sql
          STAGE: "{{.SNOWFLAKE_STAGE}}"
          NOTEBOOK_DIR: "{{.NOTEBOOK_DIR}}"
      - echo "Notebook uploaded to @SCHEMA.NOTEBOOK_STAGE"
    preconditions:
      - test -f {{.NOTEBOOK_DIR}}/app.ipynb
      - msg: "app.ipynb not found"

  # 4. CREATE - Create notebook from stage
  create:app:
    desc: Create notebook object from staged files
    silent: true
    vars:
      SNOWFLAKE_STAGE: "{{.SNOWFLAKE_DB}}.SCHEMA.NOTEBOOK_STAGE"
    cmds:
      - echo "Creating notebook from staged files..."
      - task: utils:sql:template
        vars:
          SQL_FILE: sql/operations/notebook/create/create_app.sql
          DATABASE: "{{.SNOWFLAKE_DB}}"
          STAGE: "{{.SNOWFLAKE_STAGE}}"
          WAREHOUSE: "{{.SNOWFLAKE_WH}}"
      - echo "Notebook created successfully"

  # 5. DEPLOY - Full workflow (drop, then remove, then upload, then create)
  deploy:app:
    desc: Deploy notebook with clean slate (drop + remove + upload + create)
    silent: true
    vars:
      NOTEBOOK_NAME: APP_NOTEBOOK
    cmds:
      - echo "Deploying notebook to Snowflake..."
      - task: drop:app
      - task: remove:app
      - task: upload:app
      - task: create:app
      - echo "Notebook deployed successfully"
      - echo ""
      - echo "Access in Snowsight - Projects - Notebooks - {{.NOTEBOOK_NAME}}"
    preconditions:
      - test -f {{.NOTEBOOK_DIR}}/app.ipynb
      - msg: "app.ipynb not found"
```

## 4. Why Explicit REMOVE Before PUT?

### The Stale Cache Problem

**Observed Behavior:**
- `PUT file @stage OVERWRITE=TRUE` successfully replaces the file in the stage
- However, Snowflake applications (notebooks/Streamlit) may cache content at creation time
- Subsequent file updates don't automatically propagate to the running application
- Result: Your fix is in the stage, but the app still shows old code

### The Solution: Explicit REMOVE

```yaml
deploy:
  1. drop     # Remove old object (clears object-level cache)
  2. remove   # Delete stage files (clears file-level cache)
  3. upload   # Upload fresh files
  4. create   # Create new object from fresh files
```

**Benefits:**
- Guarantees clean state (no possibility of stale content)
- Predictable deployments (same result every time)
- Prevents subtle caching issues
- Minimal overhead (REMOVE is fast)
- Production-ready reliability

### Real-World Evidence

**Before (OVERWRITE only):**
```bash
task notebook:deploy:all  # Uses PUT OVERWRITE=TRUE
# Result: Stage shows correct timestamp, but Snowsight shows old code
```

**After (drop, then remove, then upload, then create):**
```bash
task notebook:deploy:all  # Uses explicit REMOVE
# Result: Reliable updates every time
```

## 6. Deployment Validation

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

## 7. Advanced Patterns

### Multi-Environment Deployment

```yaml
vars:
  ENV: "{{.ENV | default \"dev\"}}"
  DB_NAME:
    sh: |
      case "{{.ENV}}" in
        prod) echo "PROD_DB" ;;
        qa)   echo "QA_DB" ;;
        *)    echo "DEV_DB" ;;
      esac

tasks:
  deploy:app:
    cmds:
      - echo "Deploying to {{.ENV}} environment ({{.DB_NAME}})..."
      - task: drop:app
        vars: {SNOWFLAKE_DB: "{{.DB_NAME}}"}
      - task: remove:app
        vars: {SNOWFLAKE_DB: "{{.DB_NAME}}"}
      - task: upload:app
        vars: {SNOWFLAKE_DB: "{{.DB_NAME}}"}
      - task: create:app
        vars: {SNOWFLAKE_DB: "{{.DB_NAME}}"}
```

**Usage:**
```bash
task notebook:deploy:app ENV=dev
task notebook:deploy:app ENV=qa
task notebook:deploy:app ENV=prod
```

### Deployment with Validation

```yaml
tasks:
  deploy:app:
    cmds:
      - task: drop:app
      - task: remove:app
      - task: upload:app
      - task: validate:stage
      - task: create:app
      - task: validate:object

  validate:stage:
    desc: Verify files in stage
    silent: true
    cmds:
      - |
        echo "Validating stage contents..."
        uvx snow sql -q "LIST @{{.SNOWFLAKE_STAGE}};" | grep -q "app.ipynb"
        echo "✓ Stage validation passed"

  validate:object:
    desc: Verify object exists
    silent: true
    cmds:
      - |
        echo "Validating notebook object..."
        uvx snow sql -q "SHOW NOTEBOOKS IN SCHEMA {{.SNOWFLAKE_DB}}.SCHEMA;" \
          | grep -q "APP_NOTEBOOK"
        echo "✓ Object validation passed"
```
