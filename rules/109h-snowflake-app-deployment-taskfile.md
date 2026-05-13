# Snowflake App Deployment Taskfile Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:deployment-taskfile, kw:deploy-task
**Keywords:** Taskfile deployment, task automation, deployment tasks, task structure, deploy task, upload task, create task, drop task, remove task, deployment workflow
**TokenBudget:** ~3100
**ContextTier:** Low
**Depends:** 109b-snowflake-app-deployment-core.md, 820-taskfile-automation.md

## Scope

**What This Rule Covers:**
Taskfile implementation patterns for Snowflake application deployment automation, including task structure per application, variable configuration, includes, preconditions, and deployment validation tasks.

**When to Load This Rule:**
- Setting up Taskfile-based deployment automation
- Implementing the 5-step deployment workflow in Taskfile
- Configuring deployment variables and preconditions
- Adding deployment validation tasks

## References

### Related Rules
**Closely Related** (consider loading together):
- **109b-snowflake-app-deployment-core.md** - Parent rule with core deployment patterns
- **820-taskfile-automation.md** - General Taskfile patterns

## Contract

### Inputs and Prerequisites

- Taskfile.yml structure in place
- SQL scripts created per 109g
- Snowflake CLI installed

### Mandatory

- 5 core tasks: upload, create, drop, remove, deploy
- deploy task runs full workflow: drop, remove, upload, create
- Preconditions check for required files before upload

### Forbidden

- Manual deployment without Taskfile automation
- Missing preconditions on upload tasks

### Execution Steps

1. Create task/app/Taskfile.yml with variable definitions
2. Implement all 5 core tasks
3. Add preconditions for file existence
4. Add includes for shared utilities
5. Test each task individually and full deploy

### Output Format

Taskfile.yml files with deployment task definitions.

### Validation

`task --list` shows all 5 required operations. Individual tasks run successfully. Full deploy workflow completes without errors.

### Design Principles

- Modular tasks that can run independently or as a workflow.
- Preconditions prevent partial deployments.
- Variables enable environment-specific configuration.

### Post-Execution Checklist

- [ ] All 5 core tasks defined (upload, create, drop, remove, deploy)
- [ ] Deploy task runs drop, remove, upload, create in order
- [ ] Preconditions check for required files
- [ ] Variables configured for database, warehouse, stage

## Implementation Details

## Taskfile Implementation

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

# The shared utility task referenced above (../utils/Taskfile.yml):
# tasks:
#   sql:template:
#     cmds:
#       - "{{.SNOW_CLI_BASE}} sql -D STAGE={{.STAGE}} -D DATABASE={{.DATABASE}} -f {{.SQL_FILE}}"

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
          SQL_FILE: sql/operations/notebook/03_notebook_remove_files.sql
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
          SQL_FILE: sql/operations/notebook/02_notebook_upload_files.sql
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

### Streamlit Taskfile Variant

For Streamlit apps, adjust the upload task for `pages/`, `utils/`, and `environment.yml`:

```yaml
# task/streamlit/Taskfile.yml — key differences from notebook variant
vars:
  STREAMLIT_DIR: streamlit
  SNOWFLAKE_STAGE: "{{.SNOWFLAKE_DB}}.SCHEMA.STREAMLIT_STAGE"

tasks:
  upload:app:
    desc: Upload Streamlit files to stage
    silent: true
    cmds:
      - task: utils:sql:template
        vars:
          SQL_FILE: sql/operations/streamlit/02_streamlit_upload_files.sql
          STAGE: "{{.SNOWFLAKE_STAGE}}"
          APP_DIR: "{{.STREAMLIT_DIR}}"
    preconditions:
      - test -f {{.STREAMLIT_DIR}}/streamlit_app.py
      - test -f {{.STREAMLIT_DIR}}/environment.yml

  create:app:
    desc: Create Streamlit object from staged files
    cmds:
      - task: utils:sql:template
        vars:
          SQL_FILE: sql/operations/streamlit/create/create_app.sql
          DATABASE: "{{.SNOWFLAKE_DB}}"
          STAGE: "{{.SNOWFLAKE_STAGE}}"
          WAREHOUSE: "{{.SNOWFLAKE_WH}}"
```

> Upload SQL must include `pages/*.py`, `utils/*.py`, and `environment.yml` with `AUTO_COMPRESS=FALSE`. See **109g** for the full PUT script template.

### Verification Task

Add a `verify:app` task to confirm deployment succeeded:

```yaml
  verify:app:
    desc: Verify deployment succeeded
    silent: true
    cmds:
      - "{{.SNOW_CLI_BASE}} sql -q 'LIST @{{.SNOWFLAKE_STAGE}};'"
      - "{{.SNOW_CLI_BASE}} sql -q 'SHOW NOTEBOOKS IN SCHEMA {{.SNOWFLAKE_DB}}.SCHEMA;'"
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Deploy Task Without Ordered Dependencies (Using `deps` Instead of `cmds`)**

**Problem:** Developers use Taskfile's `deps` field to run drop, remove, upload, and create as parallel dependencies of the deploy task. Since `deps` run concurrently, the upload may start before remove finishes, or create may run before upload completes. This causes intermittent failures: sometimes the deployment works (tasks happen to finish in order), sometimes it fails (upload races with remove), making the issue difficult to reproduce and diagnose.

**Correct Pattern:** The deploy task must use sequential `cmds` with `task:` calls, not `deps`. The order is strict: drop -> remove -> upload -> create. Each step must complete before the next begins. Use `cmds` with `- task: drop:app` / `- task: remove:app` / `- task: upload:app` / `- task: create:app` in sequence.

```yaml
# Wrong: Using deps causes parallel execution — race conditions
deploy:app:
  deps:
    - drop:app
    - remove:app
    - upload:app     # May run before remove finishes!
    - create:app     # May run before upload finishes!

# Correct: Using cmds ensures strict sequential execution
deploy:app:
  desc: Deploy notebook (drop + remove + upload + create)
  cmds:
    - task: drop:app
    - task: remove:app
    - task: upload:app
    - task: create:app
```

**Anti-Pattern 2: Missing Preconditions on Upload Tasks**

**Problem:** The upload task has no `preconditions` block checking that required files exist locally. When a developer runs `task deploy:app` from a clean checkout or wrong directory, the PUT command fails with a cryptic Snowflake error about file not found. Worse, the drop and remove steps already ran successfully, so the previous working deployment is now gone with nothing to replace it.

**Correct Pattern:** Add `preconditions` to every upload task that verify required local files exist before any deployment step runs. Also add preconditions to the deploy task itself so the check happens before drop/remove execute: `preconditions: [{ test: -f {{.NOTEBOOK_DIR}}/app.ipynb, msg: "app.ipynb not found" }]`.

```yaml
# Wrong: No preconditions — drop/remove succeed, then upload fails on missing file
upload:app:
  cmds:
    - task: utils:sql:template
      vars:
        SQL_FILE: sql/upload_app.sql
# Result: Previous deployment already dropped, upload fails, app is gone

# Correct: Preconditions on both deploy and upload tasks
deploy:app:
  preconditions:
    - test -f {{.NOTEBOOK_DIR}}/app.ipynb
    - msg: "app.ipynb not found — run from project root"
  cmds:
    - task: drop:app
    - task: remove:app
    - task: upload:app
    - task: create:app

upload:app:
  preconditions:
    - test -f {{.NOTEBOOK_DIR}}/app.ipynb
    - msg: "app.ipynb not found"
  cmds:
    - task: utils:sql:template
      vars:
        SQL_FILE: sql/upload_app.sql
```

**Anti-Pattern 3: Hardcoding Database and Stage Names Instead of Using Variables**

**Problem:** Developers hardcode database names, stage paths, and warehouse names directly in task commands (e.g., `@UTILITY_DEMO_V2.GRID_DATA.NOTEBOOK_STAGE`) instead of using Taskfile `vars`. This makes it impossible to deploy to different environments without editing the Taskfile, and copy-paste errors across tasks lead to mismatched database/stage references where one task targets dev and another targets prod.

**Correct Pattern:** Define all environment-specific values as `vars` at the top of the Taskfile (`SNOWFLAKE_DB`, `SNOWFLAKE_WH`, `SNOWFLAKE_STAGE`). Reference them in commands with `{{.SNOWFLAKE_DB}}` syntax. For multi-environment support, use `ENV` variable with a shell case statement to resolve the correct database name per environment.

```yaml
# Wrong: Hardcoded names — impossible to deploy to different environments
drop:app:
  cmds:
    - snow sql -q "DROP NOTEBOOK IF EXISTS UTILITY_DEMO_V2.GRID_DATA.MY_NOTEBOOK;"
upload:app:
  cmds:
    - snow sql -q "PUT file://app.ipynb @PROD_DB.SCHEMA.STAGE AUTO_COMPRESS=FALSE;"
    #                                     ^^^^^^^ Oops, different DB than drop task!

# Correct: Variables at top, referenced everywhere
vars:
  SNOWFLAKE_DB: "{{.ENV_DB | default \"DEV_DB\"}}"
  SNOWFLAKE_WH: UTILITY_DEMO_WH
  SNOWFLAKE_STAGE: "{{.SNOWFLAKE_DB}}.GRID_DATA.NOTEBOOK_STAGE"

drop:app:
  cmds:
    - snow sql -q "DROP NOTEBOOK IF EXISTS {{.SNOWFLAKE_DB}}.GRID_DATA.MY_NOTEBOOK;"
upload:app:
  cmds:
    - snow sql -q "PUT file://app.ipynb @{{.SNOWFLAKE_STAGE}} AUTO_COMPRESS=FALSE;"
```

**Multi-Environment Deployment:**

```bash
# Deploy to dev (default)
task deploy:app

# Deploy to QA
ENV_DB=QA_DB task deploy:app

# Deploy to prod
ENV_DB=PROD_DB task deploy:app
```
