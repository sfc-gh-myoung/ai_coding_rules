<!-- Generated for Cline rules. See https://docs.cline.bot/features/cline-rules -->

**Keywords:** Snowflake deployment, stage management, notebook deployment, Streamlit deployment, PUT, REMOVE, CREATE NOTEBOOK, CREATE STREAMLIT, deployment automation, task automation, staged applications, drop, upload, create, deploy workflow, AUTO_COMPRESS, stage path, ROOT_LOCATION, SiS deployment, TypeError, file compression, import failure
**Depends:** 100-snowflake-core, 109-snowflake-notebooks, 101-snowflake-streamlit-core, 820-taskfile-automation

**TokenBudget:** ~600
**ContextTier:** Medium

# Snowflake Application Deployment Automation

## Purpose
Establish comprehensive deployment automation patterns for Snowflake applications (Notebooks, Streamlit apps, UDFs, and other staged applications), ensuring reliable, deterministic deployments through proper stage file management and object lifecycle control.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Deployment automation for Snowflake applications using internal stages, covering notebooks, Streamlit apps, UDFs, and stored procedures

## Contract

**🔥 MANDATORY:**
- **Inputs/Prereqs:** 
  - Snowflake connection and credentials
  - Application files ready for deployment (.ipynb, .py, environment.yml)
  - Taskfile.yml structure in place
  - Internal stages created in target schemas
  - SQL scripts for upload/remove/create operations
  
- **Allowed Tools:** 
  - Task automation (Taskfile.yml)
  - Snowflake CLI (`uvx snow sql`)
  - SQL template files with Snowflake variables (`<%VARIABLE%>`)
  - PUT, REMOVE, CREATE NOTEBOOK, CREATE STREAMLIT, DROP commands

**❌ FORBIDDEN:**
- **Forbidden Tools:** 
  - Manual file uploads via Snowsight UI (not reproducible)
  - Hardcoded credentials in automation scripts
  - Deployment without version control
  - Mixing deployment modes (don't deploy same app to multiple stages)

**🔥 MANDATORY:**
- **Required Steps:**
  1. Create SQL scripts for each operation (upload, remove, create, drop)
  2. Implement task structure with 5 core operations
  3. Test deployment workflow end-to-end
  4. Document deployment process and troubleshooting
  5. Validate with actual deployment to Snowflake
  
- **Output Format:** 
  - Taskfile.yml with modular deployment tasks
  - SQL script files in organized directory structure
  - Documentation of deployment workflow
  
- **Validation Steps:** 
  - Run `task --list` to verify all tasks exist
  - Test individual operations (drop, remove, upload, create)
  - Test full deployment workflow
  - Verify stage contents after upload
  - Confirm application accessible in Snowflake

## Key Principles

- **Explicit Over Implicit:** Always use explicit REMOVE before PUT to ensure clean state
- **Modular Operations:** Break deployment into discrete, testable steps
- **Idempotent by Design:** All operations should be safely repeatable
- **Stage as Source of Truth:** Application files in stage are the canonical source
- **Separation of Concerns:** Object lifecycle (drop/create) separate from file management (remove/upload)

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
  deploy:    # Full workflow - drop → remove → upload → create
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

```
project/
├── task/
│   ├── notebook/
│   │   └── Taskfile.yml         # Notebook deployment tasks
│   └── streamlit/
│       └── Taskfile.yml         # Streamlit deployment tasks
├── sql/
│   └── operations/
│       ├── notebook/
│       │   ├── upload/
│       │   │   └── upload_*.sql
│       │   ├── remove/
│       │   │   └── remove_*.sql
│       │   ├── create/
│       │   │   └── create_*.sql
│       │   └── drop/
│       │       └── drop_*.sql
│       └── streamlit/
│           └── [same structure]
└── Taskfile.yml                 # Root taskfile with includes
```

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

**🔥 MANDATORY:**
**CRITICAL for Streamlit in Snowflake (SiS):**
- `AUTO_COMPRESS=FALSE` is **mandatory**, not optional
- Python's import system cannot read gzipped .py files
- Compressed files cause: "TypeError: bad argument type for built-in operation"
- Applies to: .py files, environment.yml, all Python modules

**Stage Path Requirement:**
- Upload files directly to stage root: `@STAGE_NAME`
- **Never** use subdirectory paths like: `@STAGE_NAME/streamlit/` ❌
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
- **Never** nest in extra subdirectory: `@STAGE/streamlit/` ❌

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

  # 5. DEPLOY - Full workflow (drop → remove → upload → create)
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
- ✅ Guarantees clean state (no possibility of stale content)
- ✅ Predictable deployments (same result every time)
- ✅ Prevents subtle caching issues
- ✅ Minimal overhead (REMOVE is fast)
- ✅ Production-ready reliability

### Real-World Evidence

**Before (OVERWRITE only):**
```bash
task notebook:deploy:all  # Uses PUT OVERWRITE=TRUE
# Result: Stage shows correct timestamp, but Snowsight shows old code
```

**After (drop → remove → upload → create):**
```bash
task notebook:deploy:all  # Uses explicit REMOVE
# Result: Reliable updates every time
```

## 5. Troubleshooting Deployment Issues

### Issue: Streamlit SiS fails with "TypeError: bad argument type for built-in operation"

**Symptoms:**
- Streamlit application fails to load in Snowflake
- Error message: "TypeError: bad argument type for built-in operation"
- Application worked previously or in development
- No pages render, blank screen or error displayed

**Common Causes:**

**Cause 1: Missing AUTO_COMPRESS=FALSE**
- Python files uploaded with compression (default behavior)
- Python's import system cannot read gzipped `.py` files
- Applies to all `.py` files: `streamlit_app.py`, `pages/*.py`, `utils/*.py`

**Cause 2: Stage Path Mismatch**
- Files uploaded to subdirectory (e.g., `@STAGE/streamlit/`)
- ROOT_LOCATION points to different path (e.g., `@STAGE`)
- Snowflake cannot find application files

**Diagnostic Steps:**

```bash
# Step 1: Check actual file locations and compression
uvx snow sql -q "LIST @UTILITY_DEMO_V2.GRID_DATA.STREAMLIT_STAGE;"

# Look for:
# - File extensions: Should be .py (not .py.gz)
# - File paths: Should match ROOT_LOCATION structure
# - Example correct: streamlit_stage/streamlit_app.py
# - Example wrong: streamlit_stage/streamlit/streamlit_app.py

# Step 2: Verify Streamlit configuration
uvx snow sql -q "SHOW STREAMLITS IN SCHEMA UTILITY_DEMO_V2.GRID_DATA;"
uvx snow sql -q "DESCRIBE STREAMLIT UTILITY_DEMO_V2.GRID_DATA.APP_NAME;"

# Check ROOT_LOCATION value matches stage file paths
```

**Solutions:**

**For Compression Issue:**
```bash
# 1. Redeploy with AUTO_COMPRESS=FALSE
task streamlit:remove:app   # Remove old compressed files
task streamlit:upload:app   # Upload with AUTO_COMPRESS=FALSE
task streamlit:create:app   # Recreate Streamlit object
```

**For Path Mismatch:**
```sql
-- Option 1: Fix upload paths (recommended)
-- Update upload script to use stage root:
PUT file://streamlit_app.py @STAGE  -- Not @STAGE/streamlit/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

-- Option 2: Fix ROOT_LOCATION to match current files
DROP STREAMLIT IF EXISTS DB.SCHEMA.APP_NAME;
CREATE STREAMLIT DB.SCHEMA.APP_NAME
    ROOT_LOCATION = '@STAGE/streamlit'  -- Match actual file location
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = WH;
```

**Verification:**
```bash
# Verify files are uncompressed and correctly located
uvx snow sql -q "LIST @STAGE;" | grep -E "\.py$|\.yml$"

# Should see:
# streamlit_stage/streamlit_app.py (NOT .py.gz)
# streamlit_stage/pages/1_Page.py
# streamlit_stage/environment.yml

# Test Streamlit app loads
# Navigate to Snowsight → Apps → Streamlit → APP_NAME
# Should load without TypeError
```

### Issue: "Notebook shows old code after deploy"

**Symptoms:**
- Deployment completes without errors
- Stage shows recent file timestamp
- Notebook in Snowsight still shows old code

**Solutions:**

1. **Run full deployment (includes REMOVE):**
   ```bash
   task notebook:deploy:app
   ```

2. **Force browser cache clear:**
   - Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
   - Close notebook completely
   - Navigate away from Notebooks section
   - Re-open notebook

3. **Verify stage contents:**
   ```bash
   uvx snow sql -q "LIST @DB.SCHEMA.NOTEBOOK_STAGE;"
   uvx snow sql -q "GET @DB.SCHEMA.NOTEBOOK_STAGE/app.ipynb file:///tmp/;"
   grep "your_fix" /tmp/app.ipynb  # Verify fix is in file
   ```

### Issue: "REMOVE fails - file not found"

**Expected Behavior:** This is OK - REMOVE is idempotent

**Explanation:** If the stage file doesn't exist, REMOVE succeeds with a warning (not an error)

**Verification:**
```bash
# Check stage contents before REMOVE
uvx snow sql -q "LIST @DB.SCHEMA.NOTEBOOK_STAGE;"
```

### Issue: "CREATE fails - object already exists"

**Solution:** Ensure `drop` task ran successfully

**Verification:**
```sql
-- Check if object exists
SELECT * FROM INFORMATION_SCHEMA.NOTEBOOKS 
WHERE NOTEBOOK_NAME = 'APP_NOTEBOOK';
```

**Manual fix:**
```bash
task notebook:drop:app  # Run drop manually
task notebook:create:app  # Then create
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
# Navigate to Projects → Notebooks
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

## Anti-Patterns and Common Mistakes

**❌ Anti-Pattern 1: Using OVERWRITE without explicit REMOVE**
```yaml
deploy:
  - upload  # PUT OVERWRITE=TRUE only
  - create
```
**Problem:** May encounter stale caching issues in Snowflake applications

**✅ Correct Pattern:**
```yaml
deploy:
  - drop     # Remove old object
  - remove   # Delete stage files explicitly
  - upload   # Upload fresh files
  - create   # Create from fresh files
```

**❌ Anti-Pattern 2: Manual uploads via Snowsight UI**
```
# Manually uploading files through Snowsight web interface
```
**Problem:** Not reproducible, no version control, no automation

**✅ Correct Pattern:**
```bash
task notebook:deploy:app  # Automated, reproducible, version-controlled
```

**❌ Anti-Pattern 3: Combining upload and create in one task**
```yaml
deploy:
  cmds:
    - uvx snow sql -q "PUT file://app.ipynb @stage"
    - uvx snow sql -q "CREATE NOTEBOOK FROM '@stage'"
```
**Problem:** No modularity, can't test individual steps, harder to debug

**✅ Correct Pattern:**
```yaml
upload:
  cmds: [task: utils:sql:template ...]

create:
  cmds: [task: utils:sql:template ...]

deploy:
  cmds:
    - task: upload
    - task: create
```

**❌ Anti-Pattern 4: Hardcoding credentials in scripts**
```sql
PUT 'file://app.ipynb' @stage 
  USER='admin' PASSWORD='secret123';
```
**Problem:** Security risk, not portable, violates best practices

**✅ Correct Pattern:**
```bash
# Use Snowflake CLI with configured connection
uvx snow sql -f upload.sql  # Uses ~/.snowflake/config.toml
```

**❌ Anti-Pattern 5: Omitting AUTO_COMPRESS=FALSE for Streamlit SiS**
```sql
# WRONG: Missing AUTO_COMPRESS=FALSE
PUT file://streamlit_app.py @STAGE
    OVERWRITE=TRUE;  # Defaults to AUTO_COMPRESS=TRUE!

PUT file://pages/*.py @STAGE/pages/
    OVERWRITE=TRUE;  # Files will be gzipped
```
**Problem:** Python import system cannot read compressed .py files  
**Symptom:** "TypeError: bad argument type for built-in operation"  
**Impact:** Application fails to load, no pages render, complete deployment failure

**✅ Correct Pattern:**
```sql
# Correct: Explicit AUTO_COMPRESS=FALSE
PUT file://streamlit_app.py @STAGE
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

PUT file://pages/*.py @STAGE/pages/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;
```

**❌ Anti-Pattern 6: Uploading Streamlit files to subdirectory path**
```sql
# WRONG: Files nested in subdirectory
PUT file://streamlit_app.py @STAGE/streamlit/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

PUT file://pages/*.py @STAGE/streamlit/pages/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

# CREATE STREAMLIT with mismatched ROOT_LOCATION
CREATE STREAMLIT APP
    ROOT_LOCATION = '@STAGE/streamlit'  # Expects files at /streamlit/
    MAIN_FILE = 'streamlit_app.py';     # But they're at /streamlit/streamlit_app.py
```
**Problem:** ROOT_LOCATION path mismatch - Snowflake cannot locate files  
**Symptom:** Same "TypeError: bad argument type for built-in operation"  
**Debugging:** `LIST @STAGE` shows `streamlit/streamlit_app.py` but ROOT_LOCATION expects different structure

**✅ Correct Pattern:**
```sql
# Correct: Upload to stage root
PUT file://streamlit_app.py @STAGE
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

PUT file://pages/*.py @STAGE/pages/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

# ROOT_LOCATION matches actual file location
CREATE STREAMLIT APP
    ROOT_LOCATION = '@STAGE'            # Matches actual location
    MAIN_FILE = 'streamlit_app.py'      # Found at @STAGE/streamlit_app.py
    QUERY_WAREHOUSE = WH;
```

## Quick Compliance Checklist

- [ ] Task structure includes all 5 operations (upload, create, drop, remove, deploy)
- [ ] SQL scripts organized in directory structure (upload/, remove/, create/, drop/)
- [ ] Explicit REMOVE task implemented before upload
- [ ] deploy task runs full workflow: drop → remove → upload → create
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

## Response Template

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
- [Snowflake PUT Command](https://docs.snowflake.com/en/sql-reference/sql/put) - Upload files to stages
- [Snowflake REMOVE Command](https://docs.snowflake.com/en/sql-reference/sql/remove) - Remove files from stages
- [Snowflake Stages](https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage) - Internal and external stages
- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/overview) - Command-line interface for Snowflake
- [Taskfile Documentation](https://taskfile.dev/) - Task automation framework

### Related Rules
- **Snowflake Notebooks**: `109-snowflake-notebooks.md`
- **Streamlit Core**: `101-snowflake-streamlit-core.md`
- **Taskfile Automation**: `820-taskfile-automation.md`
- **Snowflake Core**: `100-snowflake-core.md`
- **Data Loading**: `108-snowflake-data-loading.md`

