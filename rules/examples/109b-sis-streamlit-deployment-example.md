# 109b Example: Streamlit in Snowflake (SiS) Deployment

> **EXAMPLE FILE** - Reference implementation for `109b-snowflake-app-deployment-core.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 109b-snowflake-app-deployment-core.md
**Demonstrates:** Complete Streamlit in Snowflake (SiS) deployment workflow including environment.yml creation, recursive stage upload via Snowflake CLI, CREATE STREAMLIT, and validation
**Use When:** Deploying a multi-page Streamlit application to Snowflake SiS with proper environment pinning
**Version:** 1.0
**Last Validated:** 2026-02-19

## Prerequisites

- [ ] Snowflake account with Streamlit enabled
- [ ] Role with CREATE STAGE, CREATE STREAMLIT privileges
- [ ] Snowflake CLI installed (`uvx --from=snowflake-cli==3.14 snow --version`)
- [ ] Snowflake connection configured in `~/.snowflake/connections.toml`
- [ ] Streamlit app files in a local directory

## Local App Structure

```
streamlit/
  streamlit_app.py        # Main entrypoint
  environment.yml         # Package dependencies (CRITICAL)
  pages/
    1_Dashboard.py        # Page: Dashboard
    2_Settings.py         # Page: Settings
  utils/
    data_loader.py        # Shared utility module
```

## Implementation

### Step 1: Create environment.yml

**This step is critical.** Without `environment.yml`, SiS defaults to Streamlit 1.22.0,
which lacks `st.navigation()`, `st.Page()`, `st.fragment()`, and other modern APIs.

```yaml
# streamlit/environment.yml
name: my_streamlit_app
channels:
  - snowflake
dependencies:
  - streamlit=1.51.0
  - pandas
  - plotly
  - snowflake-snowpark-python
```

**Rules:**
- Always use the `snowflake` channel (not conda-forge or defaults)
- Pin Streamlit to a specific version (`=1.51.0`), not unpinned (`- streamlit`)
- Do NOT include `python=X.Y` declarations (SiS manages Python version)

### Step 2: Create Internal Stage

```sql
-- Create a dedicated stage for the Streamlit app
CREATE STAGE IF NOT EXISTS MY_DB.MY_SCHEMA.STREAMLIT_STAGE
  ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE')
  COMMENT = 'Stage for Streamlit application files';

-- Grant usage to developer role
GRANT USAGE ON STAGE MY_DB.MY_SCHEMA.STREAMLIT_STAGE
  TO ROLE app_developer_role;
```

### Step 3: Upload Files to Stage

**Option A: Snowflake CLI with --recursive (Recommended)**

```bash
# Remove old files first (clean slate)
uvx --from=snowflake-cli==3.14 snow sql \
  --connection default \
  -q "REMOVE @MY_DB.MY_SCHEMA.STREAMLIT_STAGE;"

# Upload entire directory recursively
uvx --from=snowflake-cli==3.14 snow stage copy \
  --connection default \
  streamlit/ @MY_DB.MY_SCHEMA.STREAMLIT_STAGE \
  --recursive \
  --no-auto-compress \
  --overwrite
```

**Option B: SQL PUT (Individual Files)**

```sql
-- Main application file (must be at stage root)
PUT file://streamlit/streamlit_app.py
    @MY_DB.MY_SCHEMA.STREAMLIT_STAGE
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

-- Environment specification (must be at stage root)
PUT file://streamlit/environment.yml
    @MY_DB.MY_SCHEMA.STREAMLIT_STAGE
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

-- Page files (subdirectory preserved)
PUT file://streamlit/pages/*.py
    @MY_DB.MY_SCHEMA.STREAMLIT_STAGE/pages/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

-- Utility files (subdirectory preserved)
PUT file://streamlit/utils/*.py
    @MY_DB.MY_SCHEMA.STREAMLIT_STAGE/utils/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;
```

**Critical notes for both options:**
- `AUTO_COMPRESS=FALSE` / `--no-auto-compress` is **mandatory** for all `.py` and `.yml` files
- Files must be at stage root (not nested in an extra subdirectory like `@STAGE/streamlit/`)
- `environment.yml` must be at the same level as `streamlit_app.py`

### Step 4: Create Streamlit Object

```sql
-- Drop existing object if re-deploying
DROP STREAMLIT IF EXISTS MY_DB.MY_SCHEMA.MY_APP;

-- Create Streamlit app from staged files
CREATE STREAMLIT MY_DB.MY_SCHEMA.MY_APP
    ROOT_LOCATION = '@MY_DB.MY_SCHEMA.STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = MY_WH
    COMMENT = 'Multi-page Streamlit dashboard';

-- Grant usage to end users
GRANT USAGE ON STREAMLIT MY_DB.MY_SCHEMA.MY_APP
    TO ROLE analyst_role;
```

**Key:** `ROOT_LOCATION` must point to the stage root where files were uploaded. Do not
append a subdirectory unless files were explicitly uploaded into one.

### Step 5: Full Deployment Script (One-Command)

```bash
#!/usr/bin/env bash
# deploy_streamlit.sh - Full SiS deployment workflow
set -euo pipefail

CLI="uvx --from=snowflake-cli==3.14 snow"
CONN="--connection default"
DB="MY_DB"
SCHEMA="MY_SCHEMA"
STAGE="${DB}.${SCHEMA}.STREAMLIT_STAGE"
APP_NAME="${DB}.${SCHEMA}.MY_APP"
WAREHOUSE="MY_WH"

echo "1/4 Dropping existing Streamlit object..."
$CLI sql $CONN -q "DROP STREAMLIT IF EXISTS ${APP_NAME};"

echo "2/4 Removing old stage files..."
$CLI sql $CONN -q "REMOVE @${STAGE};"

echo "3/4 Uploading files to stage..."
$CLI stage copy $CONN \
  streamlit/ @${STAGE} \
  --recursive \
  --no-auto-compress \
  --overwrite

echo "4/4 Creating Streamlit object..."
$CLI sql $CONN -q "CREATE STREAMLIT ${APP_NAME}
    ROOT_LOCATION = '@${STAGE}'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = ${WAREHOUSE};"

echo "Deployment complete. Open in Snowsight: Streamlit > ${APP_NAME}"
```

## Monitoring

```bash
# List stage contents to verify upload
uvx --from=snowflake-cli==3.14 snow sql \
  -q "LIST @MY_DB.MY_SCHEMA.STREAMLIT_STAGE;"

# Expected output (all files uncompressed, no .gz):
# streamlit_stage/streamlit_app.py      | 4096  | <hash> | ...
# streamlit_stage/environment.yml       | 512   | <hash> | ...
# streamlit_stage/pages/1_Dashboard.py  | 2048  | <hash> | ...
# streamlit_stage/pages/2_Settings.py   | 1024  | <hash> | ...
# streamlit_stage/utils/data_loader.py  | 3072  | <hash> | ...

# Verify Streamlit object exists
uvx --from=snowflake-cli==3.14 snow sql \
  -q "SHOW STREAMLITS LIKE 'MY_APP' IN SCHEMA MY_DB.MY_SCHEMA;"

# Describe Streamlit object (check ROOT_LOCATION)
uvx --from=snowflake-cli==3.14 snow sql \
  -q "DESCRIBE STREAMLIT MY_DB.MY_SCHEMA.MY_APP;"
```

## Validation

```bash
# 1. Verify all files are uncompressed (.py not .py.gz)
uvx --from=snowflake-cli==3.14 snow sql \
  -q "LIST @MY_DB.MY_SCHEMA.STREAMLIT_STAGE;" \
  | grep -E "\.py$|\.yml$"
# Expected: All files end in .py or .yml (no .gz suffix)

# 2. Verify environment.yml is present
uvx --from=snowflake-cli==3.14 snow sql \
  -q "LIST @MY_DB.MY_SCHEMA.STREAMLIT_STAGE;" \
  | grep environment.yml
# Expected: environment.yml listed

# 3. Verify ROOT_LOCATION matches stage
uvx --from=snowflake-cli==3.14 snow sql \
  -q "DESCRIBE STREAMLIT MY_DB.MY_SCHEMA.MY_APP;"
# Expected: ROOT_LOCATION = @MY_DB.MY_SCHEMA.STREAMLIT_STAGE

# 4. Open in Snowsight
# Navigate to: Projects > Streamlit > MY_APP
# Expected: App loads without errors, pages render, navigation works
```

**Expected Results:**
- Stage contains all app files without compression (.py, .yml, not .py.gz)
- `environment.yml` present at stage root alongside `streamlit_app.py`
- Streamlit object ROOT_LOCATION matches the stage path
- App loads in Snowsight without `TypeError` or `AttributeError`
- Navigation, pages, and modern Streamlit APIs function correctly

## Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Missing `environment.yml` | `AttributeError: module 'streamlit' has no attribute 'navigation'` | Add `environment.yml` with pinned `streamlit=1.51.0` |
| Missing `--no-auto-compress` | `TypeError: bad argument type for built-in operation` | Add `--no-auto-compress` to `snow stage copy` or `AUTO_COMPRESS=FALSE` to PUT |
| Files in subdirectory (`@STAGE/streamlit/`) | `TypeError` - ROOT_LOCATION mismatch | Upload to stage root: `@STAGE`, not `@STAGE/streamlit/` |
| Unpinned streamlit in environment.yml | Uses bundled 1.22.0, modern APIs missing | Pin: `streamlit=1.51.0` |
| Skipping DROP + REMOVE before re-deploy | Stale cached content shown | Always run full workflow: drop, remove, upload, create |

## Python Wrapper: Correct `--no-auto-compress` Flag Logic

When wrapping `snow stage copy` in a Python function for deployment automation,
the compression flag must be handled correctly. The CLI **defaults to compression ON**,
so the wrapper must explicitly pass `--no-auto-compress` when compression is disabled.

**Wrong — inverted flag logic (silent deployment failure):**
```python
# BAD: Adds --auto-compress when True (redundant), never adds --no-auto-compress when False
def snow_stage_copy(source, dest, auto_compress=True, recursive=False):
    flags = ["--overwrite"]
    if auto_compress:
        flags.append("--auto-compress")   # Redundant — already the CLI default
    if recursive:
        flags.append("--recursive")
    cmd = ["snow", "stage", "copy", source, dest] + flags
    subprocess.run(cmd, check=True)

# Caller thinks compression is disabled, but --no-auto-compress is never passed:
snow_stage_copy("streamlit/", "@STAGE", auto_compress=False, recursive=True)
# Actual CLI command: snow stage copy streamlit/ @STAGE --overwrite --recursive
# Result: .py files silently compressed to .py.gz → TypeError at runtime
```

**Correct — default `auto_compress=False` for app deployment:**
```python
# GOOD: Defaults to no compression, explicitly passes --no-auto-compress
def snow_stage_copy(source, dest, auto_compress=False, recursive=False):
    flags = ["--overwrite"]
    if not auto_compress:
        flags.append("--no-auto-compress")  # Explicitly disables compression
    if recursive:
        flags.append("--recursive")
    cmd = ["snow", "stage", "copy", source, dest] + flags
    subprocess.run(cmd, check=True)

# Now compression is correctly disabled:
snow_stage_copy("streamlit/", "@STAGE", auto_compress=False, recursive=True)
# Actual CLI command: snow stage copy streamlit/ @STAGE --overwrite --no-auto-compress --recursive
# Result: .py files uploaded uncompressed → app works correctly
```

**Key rules:**
- Default `auto_compress` parameter to `False` for application deployment wrappers
- Pass `--no-auto-compress` when `auto_compress` is `False` (not absence of `--auto-compress`)
- After upload, verify with `LIST @stage` that files show `.py` not `.py.gz`
