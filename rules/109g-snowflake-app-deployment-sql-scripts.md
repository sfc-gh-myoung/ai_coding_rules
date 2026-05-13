# Snowflake App Deployment SQL Script Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.2.1
**LastUpdated:** 2026-05-13
**LoadTrigger:** kw:deployment-sql, kw:put-script
**Keywords:** PUT command, REMOVE command, CREATE NOTEBOOK, CREATE STREAMLIT, deployment scripts, upload script, stage upload, SQL deployment templates, snow stage copy, recursive upload
**TokenBudget:** ~3700
**ContextTier:** Low
**Depends:** 109b-snowflake-app-deployment-core.md

## Scope

**What This Rule Covers:**
Standardized SQL script templates for Snowflake application deployment operations: upload (PUT), remove (REMOVE), create (CREATE NOTEBOOK/STREAMLIT), drop (DROP), and CLI-based recursive upload patterns.

**When to Load This Rule:**
- Writing SQL scripts for application deployment
- Setting up PUT commands for stage uploads
- Creating NOTEBOOK or STREAMLIT objects from staged files
- Using snow stage copy for multi-file uploads

## References

### Related Rules
**Closely Related** (consider loading together):
- **109b-snowflake-app-deployment-core.md** - Parent rule with core deployment patterns
- **109c-snowflake-app-deployment-troubleshooting.md** - Deployment debugging

## Contract

### Inputs and Prerequisites

- Application files ready for deployment
- Internal stages created in target schemas
- Snowflake CLI installed (>=3.16.0)

### Mandatory

- AUTO_COMPRESS=FALSE on all PUT commands for .py, .yml, .ipynb files
- Explicit REMOVE before every PUT
- FROM source path in CREATE must point to a valid stage location containing all app files
- After `CREATE STREAMLIT ... FROM ...`, run `ALTER STREAMLIT <name> ADD LIVE VERSION FROM LAST` before the app is viewable by non-owner roles

### Forbidden

- AUTO_COMPRESS=TRUE for Python/YAML files
- PUT without corresponding REMOVE script

### Execution Steps

1. Create upload SQL script with AUTO_COMPRESS=FALSE
2. Create remove SQL script for each staged file
3. Create CREATE script with correct FROM source path and live-version activation
4. Create DROP script with IF EXISTS
5. Test each script individually

### Output Format

SQL script files following `NN_<schema>_<operation>.sql` naming convention.

### Validation

Each script executes without errors. Stage contents match expectations after upload. Objects created successfully after CREATE.

### Design Principles

- One SQL file per operation for modularity and testability.
- AUTO_COMPRESS=FALSE is mandatory for application files.
- Explicit REMOVE ensures clean deployment state.

### Post-Execution Checklist

- [ ] Upload scripts use AUTO_COMPRESS=FALSE for all .py/.yml/.ipynb files
- [ ] Remove scripts list every file that upload scripts PUT
- [ ] CREATE scripts use `FROM '@<stage>'` syntax matching upload paths
- [ ] CREATE STREAMLIT scripts include `ALTER STREAMLIT <name> ADD LIVE VERSION FROM LAST`
- [ ] DROP scripts use IF EXISTS for idempotency

## Implementation Details

## SQL Script Patterns

### Stage Creation Script (CREATE STAGE)

```sql
-- ============================================================================
-- Filename: 01_<schema>_create_stage.sql
-- Description: Create internal stage for application files
-- ============================================================================

CREATE STAGE IF NOT EXISTS <%DATABASE%>.<%SCHEMA%>.<%STAGE%>
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
    COMMENT = 'Stage for application deployment files';
```

> Run this once per environment before any PUT/upload operations.

### Upload Script (PUT)

```sql
-- ============================================================================
-- Filename: 02_<schema>_upload_files.sql
-- Description: Upload application files to stage
--
-- Parameters:
--   STAGE        - Snowflake stage name (e.g., DB.SCHEMA.STAGE)
--   NOTEBOOK_DIR - Local directory (e.g., notebooks)
--
-- Usage:
--   snow sql -D STAGE=STG -D NOTEBOOK_DIR=notebooks -f 02_<schema>_upload_files.sql
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
- **Never** use an extra nesting subdirectory for the main app file: `@STAGE_NAME/streamlit/streamlit_app.py` — upload `streamlit_app.py` directly to `@STAGE_NAME`. Subdirectories for `pages/` and `utils/` are fine.
- FROM source path in CREATE STREAMLIT must match actual file locations
- Subdirectory mismatch causes same "TypeError" (Snowflake cannot find files)

### Remove Script (REMOVE)

```sql
-- ============================================================================
-- Filename: 03_<schema>_remove_files.sql
-- Description: Remove application files from stage
-- Ensures clean deployment by removing old files before uploading new ones.
--
-- Parameters:
--   STAGE - Snowflake stage name
--
-- Usage:
--   snow sql -D STAGE=DB.SCHEMA.STAGE -f 03_<schema>_remove_files.sql
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
-- Filename: 04_<schema>_create_notebook.sql
-- Description: Create notebook object from staged files
--
-- Parameters:
--   DATABASE  - Database name
--   STAGE     - Stage name with files
--   WAREHOUSE - Compute warehouse
--
-- Usage:
--   snow sql -D DATABASE=DB -D STAGE=STG -D WAREHOUSE=WH -f 04_<schema>_create_notebook.sql
-- ============================================================================

CREATE NOTEBOOK IF NOT EXISTS <%DATABASE%>.SCHEMA.NOTEBOOK_NAME
FROM '@<%STAGE%>'
QUERY_WAREHOUSE = <%WAREHOUSE%>
MAIN_FILE = 'app.ipynb';
```

### Drop Script (DROP NOTEBOOK/STREAMLIT)

```sql
-- ============================================================================
-- Filename: 99_<schema>_drop_notebook.sql
-- Description: Drop notebook object
--
-- Parameters:
--   DATABASE - Database name
--
-- Usage:
--   snow sql -D DATABASE=DB -f 99_<schema>_drop_notebook.sql
-- ============================================================================

DROP NOTEBOOK IF EXISTS <%DATABASE%>.SCHEMA.NOTEBOOK_NAME;
```

### Streamlit Upload Script (SiS-Specific)

**Critical Requirements for Streamlit in Snowflake:**

```sql
-- ============================================================================
-- Filename: 02_<schema>_upload_streamlit.sql
-- Description: Upload Streamlit application files to stage (SiS deployment)
--
-- CRITICAL REQUIREMENTS:
--   1. AUTO_COMPRESS=FALSE - Python import system cannot read gzipped files
--   2. Stage root path - Files at @STAGE, not @STAGE/streamlit/
--   3. FROM source path must match actual file locations
--
-- Parameters:
--   STAGE - Snowflake stage name (e.g., UTILITY_DEMO_V2.GRID_DATA.STREAMLIT_STAGE)
--   APP_DIR - Local Streamlit app directory (e.g., streamlit/streamlit_sis)
--
-- Usage:
--   snow sql -D STAGE=DB.SCHEMA.STAGE -D APP_DIR=streamlit/sis -f 02_<schema>_upload_streamlit.sql
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

SELECT '[PASS] Streamlit application files uploaded' AS progress;
```

**Key Requirements:**
- Files at stage root: `streamlit_app.py`, `environment.yml`
- Subdirectories allowed for organization: `@STAGE/pages/`, `@STAGE/utils/`
- FROM source path in CREATE STREAMLIT matches: `'@STAGE'` (not `'@STAGE/streamlit'`)
- **Never** nest in extra subdirectory: `@STAGE/streamlit/`
- **environment.yml must pin `streamlit>=1.50`** - Without it, SiS defaults to Streamlit 1.22.0 which lacks modern APIs (`st.navigation()`, `st.Page()`, etc.)

**environment.yml Template:**
```yaml
# environment.yml template for SiS
name: sf_env
channels:
  - snowflake
dependencies:
  - streamlit>=1.50
  - snowflake-snowpark-python
```

### Snowflake CLI Recursive Upload (Recommended for Multi-File Apps)

For Streamlit apps with multiple files (pages, utils, assets), `snow stage copy --recursive`
is the recommended approach over individual SQL PUT statements:

```bash
# Upload entire Streamlit app directory recursively
# Note: Pin CLI version in one place for easy updates
# SNOW_CLI_VERSION=3.16.0
uvx --from=snowflake-cli==3.16.0 snow stage copy \
  --connection default \
  streamlit/ @DB.SCHEMA.STREAMLIT_STAGE \
  --recursive \
  --no-auto-compress \
  --overwrite
```

**Advantages over SQL PUT:**
- Single command uploads all files and preserves directory structure
- No need to enumerate individual PUT statements per file/glob
- Handles nested directories (pages/, utils/, assets/) automatically
- Easier to maintain as app grows

**Complete CLI-Based Deployment Workflow:**
```bash
# 1. Drop existing Streamlit object
uvx --from=snowflake-cli==3.16.0 snow sql \
  -q "DROP STREAMLIT IF EXISTS DB.SCHEMA.MY_APP;"

# 2. Remove old stage files
uvx --from=snowflake-cli==3.16.0 snow sql \
  -q "REMOVE @DB.SCHEMA.STREAMLIT_STAGE;"

# 3. Upload all files recursively
uvx --from=snowflake-cli==3.16.0 snow stage copy \
  --connection default \
  streamlit/ @DB.SCHEMA.STREAMLIT_STAGE \
  --recursive \
  --no-auto-compress \
  --overwrite

# 4. Create Streamlit object and activate live version
uvx --from=snowflake-cli==3.16.0 snow sql \
  -q "CREATE STREAMLIT DB.SCHEMA.MY_APP
      FROM '@DB.SCHEMA.STREAMLIT_STAGE'
      MAIN_FILE = 'streamlit_app.py'
      QUERY_WAREHOUSE = MY_WH;"
uvx --from=snowflake-cli==3.16.0 snow sql \
  -q "ALTER STREAMLIT DB.SCHEMA.MY_APP ADD LIVE VERSION FROM LAST;"
```

**CREATE STREAMLIT Statement (matches upload paths):**
```sql
CREATE STREAMLIT IF NOT EXISTS <%DATABASE%>.<%SCHEMA%>.APP_NAME
    FROM '@<%STAGE%>'  -- No = sign; copies files into embedded versioned stage
    MAIN_FILE = 'streamlit_app.py'  -- Filename only (no leading slash) for warehouse runtime
    QUERY_WAREHOUSE = <%WAREHOUSE%>
    -- Optional parameters:
    -- TITLE = 'My Application'
    -- COMMENT = 'Description of the app'
    -- EXTERNAL_ACCESS_INTEGRATIONS = (my_integration)
    ;

-- Activate live version so non-owner roles can access the app
ALTER STREAMLIT <%DATABASE%>.<%SCHEMA%>.APP_NAME ADD LIVE VERSION FROM LAST;
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Relying on OVERWRITE=TRUE Without Explicit REMOVE**

**Problem:** Developers skip the REMOVE script and rely solely on `OVERWRITE=TRUE` in PUT commands, assuming it fully replaces old files. However, if a file was renamed or deleted from the local directory (e.g., `pages/old_page.py` removed), the old stage file persists because OVERWRITE only replaces files with matching names. The stale file causes the deployed app to load deleted pages or import removed modules, producing confusing runtime errors.

**Correct Pattern:** Always run explicit `REMOVE @STAGE/filename;` for every file before uploading. Better yet, use `REMOVE @STAGE;` to clear the entire stage, then re-upload everything. The remove script should be a mirror of the upload script -- every PUT has a corresponding REMOVE.

```sql
-- Wrong: Relying on OVERWRITE alone — stale files from renamed/deleted pages persist
PUT file://streamlit/streamlit_app.py @STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://streamlit/pages/dashboard.py @STAGE/pages/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- old_page.py was deleted locally but still exists on stage — app loads ghost page

-- Correct: Explicit REMOVE before PUT to ensure clean state
REMOVE @STAGE;  -- Clear entire stage first
PUT file://streamlit/streamlit_app.py @STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://streamlit/pages/dashboard.py @STAGE/pages/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

**Anti-Pattern 2: Uploading Python Files Without AUTO_COMPRESS=FALSE**

**Problem:** Developers omit `AUTO_COMPRESS=FALSE` from PUT commands or use a Python wrapper that silently defaults to compression. Snowflake's PUT defaults to `AUTO_COMPRESS=TRUE`, which gzips `.py` files to `.py.gz`. The upload succeeds, the stage listing looks normal (Snowflake may hide the `.gz` extension in some views), but the app fails at runtime with `"TypeError: bad argument type for built-in operation"` because Python's import system cannot read gzipped files.

**Correct Pattern:** Every PUT command for `.py`, `.yml`, and `.ipynb` files must include `AUTO_COMPRESS=FALSE`. Verify after upload with `LIST @STAGE;` and confirm file extensions are `.py` not `.py.gz`. Add this as a deployment precondition check.

```sql
-- Wrong: Missing AUTO_COMPRESS=FALSE — files silently compressed to .py.gz
PUT file://streamlit/streamlit_app.py @STAGE OVERWRITE=TRUE;
PUT file://streamlit/environment.yml @STAGE OVERWRITE=TRUE;
-- LIST shows streamlit_app.py.gz — Python import system cannot read gzipped files

-- Correct: AUTO_COMPRESS=FALSE on every PUT for .py/.yml/.ipynb files
PUT file://streamlit/streamlit_app.py @STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://streamlit/environment.yml @STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- Verify: LIST @STAGE; should show .py and .yml (not .py.gz or .yml.gz)
```

**LEGACY (ROOT_LOCATION)** Anti-Pattern 3: Path Mismatch Between Upload and ROOT_LOCATION

> **Legacy context:** This anti-pattern applies to apps created with the legacy `ROOT_LOCATION` syntax. For new apps, use `FROM` instead (see CREATE STREAMLIT templates above). Legacy apps created in older Snowsight versions may show `root_location` as a `snow://` URL instead of a named stage — this is expected for older legacy apps; modern legacy apps use `@stage` paths.

**Problem:** Files are uploaded to the stage root (`@STAGE/streamlit_app.py`) but the CREATE STREAMLIT statement specifies `ROOT_LOCATION = '@STAGE/streamlit'`, or vice versa. This path mismatch causes the same `"TypeError"` as compression issues, making it hard to diagnose.

```sql
-- LEGACY: Files uploaded to stage root but ROOT_LOCATION points to subdirectory
PUT file://streamlit_app.py @STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- LIST @STAGE shows: streamlit_stage/streamlit_app.py
CREATE STREAMLIT DB.SCHEMA.MY_APP
    ROOT_LOCATION = '@STAGE/streamlit'  -- Mismatch! Files are at root, not /streamlit/
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = WH;

-- LEGACY Correct: ROOT_LOCATION matches actual file paths from LIST output
CREATE STREAMLIT DB.SCHEMA.MY_APP
    ROOT_LOCATION = '@STAGE'  -- Matches actual upload location
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = WH;
```

**Anti-Pattern 4: FROM Source Path Doesn't Exist or Is Empty**

**Problem:** The stage path passed to `FROM` does not exist, has no files, or points to a subdirectory that doesn't contain the main file. Because `FROM` copies files into an embedded versioned stage at CREATE time, an empty or missing source produces a Streamlit object with no content, causing `TypeError` or a blank app on open.

**Correct Pattern:** Run `LIST @STAGE;` before `CREATE STREAMLIT` to confirm files exist at the expected path. Verify `MAIN_FILE` is a filename only (no leading `/`) for warehouse runtime.

```sql
-- Verify files exist before creating the Streamlit object
LIST @DB.SCHEMA.STREAMLIT_STAGE;
-- Expected: streamlit_app.py, environment.yml, pages/*, utils/* listed (no .gz extensions)

-- Wrong: MAIN_FILE with leading slash (warehouse runtime rejects it)
CREATE STREAMLIT DB.SCHEMA.MY_APP
    FROM '@DB.SCHEMA.STREAMLIT_STAGE'
    MAIN_FILE = '/streamlit_app.py'  -- Leading slash causes file-not-found error
    QUERY_WAREHOUSE = MY_WH;

-- Correct: FROM with verified stage path; MAIN_FILE filename only
CREATE STREAMLIT DB.SCHEMA.MY_APP
    FROM '@DB.SCHEMA.STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'  -- Filename only, no leading slash
    QUERY_WAREHOUSE = MY_WH;
ALTER STREAMLIT DB.SCHEMA.MY_APP ADD LIVE VERSION FROM LAST;
```

## Updating an Existing App's Source Files

How to push source file updates depends on whether the app was created with `FROM` or legacy `ROOT_LOCATION`.

### FROM-Based Apps (Recommended)

`FROM` copies files into an **embedded versioned stage** at CREATE time. Edits to the original source stage do **not** automatically update the app. To update:

**Option A — Recreate (recommended for full redeployment):**
```sql
DROP STREAMLIT IF EXISTS DB.SCHEMA.MY_APP;
-- (re-upload files to source stage if needed)
CREATE STREAMLIT DB.SCHEMA.MY_APP
    FROM '@DB.SCHEMA.STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = MY_WH;
ALTER STREAMLIT DB.SCHEMA.MY_APP ADD LIVE VERSION FROM LAST;
```

**Option B — Copy files into live_version_location_uri (in-place update):**
```sql
-- Retrieve the embedded stage URI
DESCRIBE STREAMLIT DB.SCHEMA.MY_APP;
-- Note the live_version_location_uri value (e.g. snow://streamlit/...)

-- Copy updated files directly into the embedded stage
COPY FILES
  INTO @<live_version_location_uri>/
  FROM @DB.SCHEMA.STREAMLIT_STAGE/;
```

### **LEGACY (ROOT_LOCATION)** Apps

Legacy apps read from the named stage at runtime. To update: PUT or COPY FILES directly against the stage referenced by `root_location` — no recreate needed.

```sql
-- Update source files in the legacy stage
REMOVE @DB.SCHEMA.STREAMLIT_STAGE/streamlit_app.py;
PUT file://streamlit_app.py @DB.SCHEMA.STREAMLIT_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- App picks up changes on next load (no ALTER or recreate required)
```
