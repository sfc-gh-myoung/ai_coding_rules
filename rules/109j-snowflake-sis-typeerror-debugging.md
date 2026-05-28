# Snowflake SiS TypeError & AttributeError Debugging

## Metadata

**SchemaVersion:** v3.3
**RuleVersion:** v3.1.1
**LastUpdated:** 2026-05-13
**Keywords:** kw:sis-typeerror, kw:typeerror bad argument, kw:attributeerror streamlit, kw:sis debugging, kw:auto_compress, kw:from source path, kw:live_version_location_uri, kw:root_location mismatch (legacy), kw:environment.yml, kw:streamlit version, kw:compression debugging, kw:stage path mismatch
**TokenBudget:** ~4200
**ContextTier:** Medium
**Depends:** required:100-snowflake-core.md, required:109c-snowflake-app-deployment-troubleshooting.md

## Scope

**What This Rule Covers:**
Detailed diagnostic workflows for the two most common Streamlit in Snowflake (SiS) deployment errors: TypeError from file compression or path mismatches, and AttributeError from missing or outdated environment.yml. Includes step-by-step diagnostic commands, root cause identification, and verified solutions.

**When to Load This Rule:**
- Debugging "TypeError: bad argument type for built-in operation" in SiS
- Debugging "AttributeError: module 'streamlit' has no attribute 'X'" in SiS
- Diagnosing AUTO_COMPRESS, FROM source path, or stage path issues
- Troubleshooting environment.yml version pinning

## References

### Dependencies

**Must Load First:**
- **109c-snowflake-app-deployment-troubleshooting.md** - Parent troubleshooting rule

**Related:**
- **101-snowflake-streamlit-core.md** - Streamlit development patterns
- **109b-snowflake-app-deployment-core.md** - Base deployment patterns

### External Documentation

- [Streamlit in Snowflake Troubleshooting](https://docs.snowflake.com/en/developer-guide/streamlit/troubleshooting) - Official SiS debugging guide
- [Stage Management](https://docs.snowflake.com/en/user-guide/data-load-stages-intro) - Stage operations reference

## Contract

### Inputs and Prerequisites

- Active Snowflake connection with stage LIST/DESCRIBE permissions
- Knowledge of deployed Streamlit app name and stage location
- Access to deployment scripts (Taskfile or equivalent)

### Mandatory

- Run diagnostic commands (LIST, DESCRIBE) before suggesting fixes
- Verify file compression status (.py vs .py.gz) before remediation
- Verify FROM source path and MAIN_FILE correctness; for legacy apps, verify ROOT_LOCATION alignment with actual stage paths
- Include post-fix verification commands

### Forbidden

- Guessing the root cause without running diagnostic commands
- Suggesting manual Snowsight UI uploads as a fix

### Execution Steps

1. Identify error type (TypeError vs AttributeError)
2. Execute diagnostic commands for that error type
3. Identify root cause from command outputs
4. Apply targeted remediation
5. Verify fix with post-deployment checks

### Output Format

- Diagnostic command outputs with interpretation
- Root cause identification with evidence
- Step-by-step remediation commands
- Verification commands confirming resolution

### Validation

**Pre-Task-Completion Checks:**
- Diagnostic commands executed and outputs reviewed
- Root cause identified with evidence from command outputs
- Remediation addresses root cause (not symptoms)

**Success Criteria:**
- Application loads without TypeError or AttributeError
- Stage files show correct extensions (.py not .py.gz)
- For FROM-based apps: DESCRIBE STREAMLIT shows `live_version_location_uri` populated; for legacy apps: ROOT_LOCATION matches actual file paths

**Negative Tests:**
- Deployment without AUTO_COMPRESS=FALSE produces .py.gz files
- Missing environment.yml causes SiS to use default Streamlit 1.22.0

### Design Principles

- **Diagnose Before Fixing:** Always run LIST/DESCRIBE before remediation
- **Evidence-Based:** Use command outputs to confirm root cause
- **Verification Required:** Confirm every fix with validation commands

### Post-Execution Checklist

- [ ] Diagnostic commands executed before suggesting fixes
- [ ] Root cause identified with evidence from command outputs
- [ ] AUTO_COMPRESS=FALSE verified for all .py files
- [ ] For FROM-based apps: `live_version_location_uri` is populated in DESCRIBE STREAMLIT output; for legacy apps: ROOT_LOCATION matches stage file paths
- [ ] environment.yml present with pinned Streamlit version (if AttributeError)
- [ ] Post-fix verification confirms application loads correctly

## Issue: Streamlit SiS fails with "TypeError: bad argument type for built-in operation"

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

**Cause 2: Stage Path Mismatch (legacy ROOT_LOCATION apps)**
- Files uploaded to subdirectory (e.g., `@STAGE/streamlit/`)
- ROOT_LOCATION points to different path (e.g., `@STAGE`)
- Snowflake cannot find application files
- For FROM-based apps, see the "TypeError on FROM-based apps" section below for the equivalent failure modes

**Cause 3: Inverted Compression Flag in Python/CLI Wrappers**
- Python wrapper function adds `--auto-compress` when `True` (redundant -- already the default)
- But never adds `--no-auto-compress` when `False` -- compression is never actually disabled
- Deployment reports success (`[PASS]`) but app fails at runtime
- Especially insidious because `auto_compress=False` in the calling code *looks* correct

**Diagnostic Steps:**

Execute these commands to identify root cause:

```bash
# Step 1: Check actual file locations and compression status
uvx snow sql -q "LIST @UTILITY_DEMO_V2.GRID_DATA.STREAMLIT_STAGE;"

# Expected output (CORRECT - uncompressed):
# streamlit_stage/streamlit_app.py          | 4096  | <hash> | ...
# streamlit_stage/pages/1_Home.py           | 2048  | <hash> | ...
# streamlit_stage/environment.yml           | 512   | <hash> | ...

# Bad output (WRONG - compressed files):
# streamlit_stage/streamlit_app.py.gz       | 1024  | <hash> | ...
# streamlit_stage/pages/1_Home.py.gz        | 512   | <hash> | ...

# Step 2: Verify source path — behavior differs for FROM vs legacy apps
uvx snow sql -q "DESCRIBE STREAMLIT UTILITY_DEMO_V2.GRID_DATA.APP_NAME;"

# For FROM-based apps (created with FROM '@stage'):
# Look for live_version_location_uri in output
# Expected: live_version_location_uri = snow://streamlit/<id>/versions/<ver>/
# If missing or empty: app may not have an activated live version
# Run: ALTER STREAMLIT APP_NAME ADD LIVE VERSION FROM LAST;

# For legacy apps (created with ROOT_LOCATION = '@stage'):
# Look for root_location value in output
# Expected: root_location = @UTILITY_DEMO_V2.GRID_DATA.STREAMLIT_STAGE
# Must match LIST output paths (no extra /streamlit/ subdirectory nesting)
# Note: Legacy apps in older Snowsight may show root_location as a snow:// URL — this is expected

# Verify paths align (legacy apps):
# LIST shows: streamlit_stage/streamlit_app.py
# root_location: @STREAMLIT_STAGE  (correct - matches root)
# NOT: @STREAMLIT_STAGE/streamlit  (wrong - extra subdirectory)

# Step 3: Detailed file listing with grep filter
uvx snow sql -q "LIST @UTILITY_DEMO_V2.GRID_DATA.STREAMLIT_STAGE;" \
  | grep -E "\.py$|\.yml$"

# Should show .py extensions (not .py.gz):
# streamlit_app.py   [OK] Correct
# pages/1_Home.py    [OK] Correct
# environment.yml    [OK] Correct

# Step 4: If using a Python wrapper, verify the actual CLI command
# Add --verbose to your deployment command or check logs for --no-auto-compress
# If wrapper uses auto_compress=False but doesn't pass --no-auto-compress, files are still compressed
```

> **Multi-page apps:** Verify each page file individually: `LIST @STAGE/pages/;` — all `.py` files in subdirectories must also be uncompressed. A single compressed page file can cause TypeError for that page only.

**Solutions:**

**For Compression Issue:**
```bash
# 1. Redeploy with AUTO_COMPRESS=FALSE
task streamlit:remove:app   # Remove old compressed files
task streamlit:upload:app   # Upload with AUTO_COMPRESS=FALSE
task streamlit:create:app   # Recreate Streamlit object
```

**For Path Mismatch (FROM-based apps — recommended):**
```sql
-- Recreate app with correct FROM source path (files must be at stage root)
LIST @DB.SCHEMA.STREAMLIT_STAGE;  -- Verify files are at root before recreating
DROP STREAMLIT IF EXISTS DB.SCHEMA.APP_NAME;
CREATE STREAMLIT DB.SCHEMA.APP_NAME
    FROM '@DB.SCHEMA.STREAMLIT_STAGE'  -- Source stage root
    MAIN_FILE = 'streamlit_app.py'     -- Filename only, no leading slash
    QUERY_WAREHOUSE = WH;
ALTER STREAMLIT DB.SCHEMA.APP_NAME ADD LIVE VERSION FROM LAST;
```

**LEGACY (ROOT_LOCATION)** For Path Mismatch:
```sql
-- Option 1: Fix upload paths so files land at stage root
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

# Should see (file extensions without .gz):
# streamlit_stage/streamlit_app.py          [OK] Uncompressed
# streamlit_stage/pages/1_Page.py           [OK] Uncompressed
# streamlit_stage/environment.yml           [OK] Uncompressed

# Should NOT see:
# streamlit_stage/streamlit_app.py.gz       [FAIL] Compressed (causes TypeError)
# streamlit_stage/streamlit/app.py          [FAIL] Wrong path (source path mismatch)

# Verify Streamlit app loads without errors
# Navigate to Snowsight > Apps > Streamlit > APP_NAME
# Expected: Application loads, pages render, no TypeError

# Verify import system works
# Note: Use SYSTEM$CHECK_FILE_EXISTS (no backslash) in SQL worksheets.
# The backslash below is only needed for bash shell escaping.
uvx snow sql -q "
SELECT SYSTEM\$CHECK_FILE_EXISTS('@STAGE/streamlit_app.py');
"
# Should return: TRUE (file exists and is accessible)
```

## Issue: "AttributeError: module 'streamlit' has no attribute 'X'"

**Symptoms:**
- Streamlit app fails with `AttributeError: module 'streamlit' has no attribute 'navigation'`
  (or `'Page'`, `'dialog'`, `'fragment'`, or other modern API)
- App works locally but fails when deployed to SiS
- Error appears immediately on app load or when navigating to a page that uses the missing API

**Root Cause:**
Missing or incorrect `environment.yml` in the stage. Without `environment.yml`, SiS defaults
to its bundled Streamlit version (currently **1.22.0**), which predates many modern APIs:

> **Staleness guard:** Add `st.write(st.__version__)` temporarily to verify the actual bundled version. The default may change as Snowflake updates SiS.

- `st.navigation()` -- requires 1.36+ (not available in SiS default 1.22.0)
- `st.Page()` -- requires 1.36+ (not available in SiS default 1.22.0)
- `st.dialog()` -- requires 1.37+ (not available in SiS default 1.22.0)
- `st.fragment()` -- requires 1.37+ (not available in SiS default 1.22.0)
- `st.rerun()` -- requires 1.27+ (not available in SiS default 1.22.0)

**Diagnostic Steps:**

```bash
# Step 1: Check if environment.yml exists in stage
uvx snow sql -q "LIST @DB.SCHEMA.STREAMLIT_STAGE;" | grep environment.yml

# If no output -> environment.yml is MISSING (root cause confirmed)

# Step 2: If environment.yml exists, download and check contents
uvx snow sql -q "GET @DB.SCHEMA.STREAMLIT_STAGE/environment.yml file:///tmp/;"
cat /tmp/environment.yml

# Check: Does it pin streamlit to a recent version?
# BAD:  just "- streamlit" (no version, uses bundled default)
# GOOD: "- streamlit=1.51.0" (explicit pin)

# Step 3: Verify what Streamlit version the app is using
# Add this temporarily to streamlit_app.py:
#   import streamlit as st
#   st.write(f"Streamlit version: {st.__version__}")
```

**Fix:**

1. **Create `environment.yml`** in your Streamlit app directory:
   ```yaml
   name: my_app
   channels:
     - snowflake
   dependencies:
     - streamlit=1.51.0
     - pandas
     - plotly
   ```

   > **Package compatibility:** Some packages in the `snowflake` channel have version constraints. Run `conda search -c snowflake streamlit` locally to see available versions before pinning.

2. **Redeploy with environment.yml included:**
   ```bash
   # Using snow stage copy (recommended for multi-file apps)
   uvx --from=snowflake-cli==3.16.0 snow stage copy \
     streamlit/ @DB.SCHEMA.STREAMLIT_STAGE \
     --recursive --no-auto-compress --overwrite

   # Or using SQL PUT (single file)
   uvx snow sql -q "PUT file://streamlit/environment.yml
       @DB.SCHEMA.STREAMLIT_STAGE
       AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
   ```

3. **Recreate the Streamlit object** (environment.yml is read at creation time):
   ```bash
   uvx snow sql -q "DROP STREAMLIT IF EXISTS DB.SCHEMA.MY_APP;"
   uvx snow sql -q "CREATE STREAMLIT DB.SCHEMA.MY_APP
       FROM '@DB.SCHEMA.STREAMLIT_STAGE'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = MY_WH;"
   uvx snow sql -q "ALTER STREAMLIT DB.SCHEMA.MY_APP ADD LIVE VERSION FROM LAST;"
   ```

**Verification:**
```bash
# Confirm environment.yml is in stage
uvx snow sql -q "LIST @DB.SCHEMA.STREAMLIT_STAGE;" | grep environment.yml
# Expected: environment.yml listed (not .gz)

# Open app in Snowsight - should load without AttributeError
```

**Prevention:**
- Always include `environment.yml` with a pinned Streamlit version in your app directory
- Add `environment.yml` to your deployment precondition checks
- Pin to `streamlit=1.51.0` (or latest available in snowflake channel)

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Guessing the Root Cause Without Running Diagnostic Commands**

**Problem:** A developer sees "TypeError: bad argument type for built-in operation" and immediately assumes it's a code bug in their Streamlit app. They spend hours debugging their Python code, adding try/except blocks, and rewriting logic, when the actual cause is compressed `.py.gz` files on the stage, a FROM source path issue, or for legacy apps a ROOT_LOCATION mismatch.

**Correct Pattern:** Always run the diagnostic commands first: `LIST @STAGE;` to check for `.py.gz` extensions and `DESCRIBE STREAMLIT APP_NAME;` to verify `live_version_location_uri` (FROM-based apps) or `root_location` (legacy apps). These two commands identify the root cause in under 30 seconds. Never modify application code in response to a TypeError until you've confirmed the stage files are uncompressed and paths are aligned.

```bash
# Wrong: Debugging application code without checking stage files
# Developer sees TypeError and starts adding try/except blocks
# streamlit_app.py:
#   try:
#       import pages.dashboard  # TypeError here
#   except TypeError:
#       st.error("Import failed")  # Masks the real issue (compressed files)

# Correct: Run diagnostics first — check stage files and source path
uvx snow sql -q "LIST @DB.SCHEMA.STREAMLIT_STAGE;" | grep -E '\.py|\.yml'
# Look for .py.gz (compressed) vs .py (correct)
# If you see .py.gz → fix AUTO_COMPRESS, don't touch app code

uvx snow sql -q "DESCRIBE STREAMLIT DB.SCHEMA.MY_APP;"
# For FROM-based apps: verify live_version_location_uri is populated
# For legacy apps: verify root_location matches actual file paths from LIST output
```

**Anti-Pattern 2: Adding environment.yml Without Pinning the Streamlit Version**

**Problem:** A developer creates `environment.yml` to fix an AttributeError but lists `- streamlit` without a version pin. SiS resolves this to whatever version is bundled in the current Snowflake release (often 1.22.0), which is the same version that caused the AttributeError in the first place. The deployment appears to include the fix but the error persists, leading the developer to believe environment.yml doesn't work.

**Correct Pattern:** Always pin the Streamlit version explicitly: `- streamlit=1.51.0` (or the latest available in the `snowflake` conda channel). After deploying, verify the version by temporarily adding `st.write(st.__version__)` to the app. Remove the debug line once confirmed.

```yaml
# Wrong: No version pin — SiS uses bundled default (often 1.22.0)
name: my_app
channels:
  - snowflake
dependencies:
  - streamlit        # Resolves to 1.22.0 — st.navigation() still missing!
  - pandas

# Correct: Explicit version pin to get modern Streamlit APIs
name: my_app
channels:
  - snowflake
dependencies:
  - streamlit=1.51.0  # Explicit pin — st.navigation(), st.Page() available
  - pandas
```

**Anti-Pattern 3: Fixing Compression but Forgetting to Recreate the Streamlit Object**

**Problem:** A developer identifies that files were compressed, re-uploads with `AUTO_COMPRESS=FALSE`, and confirms via `LIST @STAGE;` that files now have correct `.py` extensions. But the app still shows the TypeError. The reason: the Streamlit object caches metadata from creation time. Simply re-uploading files doesn't update the object's internal references -- the object must be dropped and recreated to pick up the new files.

**Correct Pattern:** After fixing stage files, always drop and recreate the Streamlit object. For FROM-based apps: `DROP STREAMLIT IF EXISTS ...; CREATE STREAMLIT ... FROM '@stage' ...; ALTER STREAMLIT ... ADD LIVE VERSION FROM LAST;`. For legacy apps: `DROP STREAMLIT IF EXISTS ...; CREATE STREAMLIT ... ROOT_LOCATION='@stage' ...;`. The full redeployment workflow is: drop object -> remove stage files -> upload corrected files -> create object -> (FROM apps only) add live version. Skipping the drop/create steps is a common source of "I fixed it but it's still broken."

```sql
-- Wrong: Re-upload files but skip recreating the Streamlit object
REMOVE @DB.SCHEMA.STAGE/streamlit_app.py;
PUT file://streamlit_app.py @DB.SCHEMA.STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- LIST confirms .py (not .py.gz) — looks fixed!
-- But app still shows TypeError because object caches old metadata

-- Correct (FROM-based apps): Full redeployment with live-version activation
DROP STREAMLIT IF EXISTS DB.SCHEMA.MY_APP;
REMOVE @DB.SCHEMA.STAGE;
PUT file://streamlit_app.py @DB.SCHEMA.STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://environment.yml @DB.SCHEMA.STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
CREATE STREAMLIT DB.SCHEMA.MY_APP
    FROM '@DB.SCHEMA.STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = MY_WH;
ALTER STREAMLIT DB.SCHEMA.MY_APP ADD LIVE VERSION FROM LAST;
-- Object recreated with fresh metadata — TypeError resolved
```

## TypeError on FROM-based Apps

Apps created with `FROM '@stage'` have different failure modes from legacy `ROOT_LOCATION` apps. Use these diagnostics when `DESCRIBE STREAMLIT` shows `live_version_location_uri` (not `root_location`).

**FROM-specific Cause 1: MAIN_FILE has a leading slash (warehouse runtime)**

For warehouse-runtime apps, `MAIN_FILE` must be a filename only — no leading `/`.

```sql
-- Wrong: Leading slash causes file-not-found error in warehouse runtime
CREATE STREAMLIT DB.SCHEMA.MY_APP
    FROM '@DB.SCHEMA.STREAMLIT_STAGE'
    MAIN_FILE = '/streamlit_app.py'  -- Leading slash: not valid for warehouse runtime
    QUERY_WAREHOUSE = MY_WH;

-- Correct: Filename only
CREATE STREAMLIT DB.SCHEMA.MY_APP
    FROM '@DB.SCHEMA.STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'  -- No leading slash
    QUERY_WAREHOUSE = MY_WH;
ALTER STREAMLIT DB.SCHEMA.MY_APP ADD LIVE VERSION FROM LAST;
```

> **Container runtime:** A relative subpath like `subdir/my_app.py` is allowed for container runtime apps.

**FROM-specific Cause 2: Source stage was empty or missing files at CREATE time**

Because `FROM` copies files into an embedded stage at `CREATE` time, an empty or missing source stage produces a Streamlit object with no content.

```bash
# Diagnose: List source stage BEFORE creating the app
uvx snow sql -q "LIST @DB.SCHEMA.STREAMLIT_STAGE;"
# If empty or missing streamlit_app.py / environment.yml — upload files first

# Fix: Upload files, then recreate
uvx snow sql -q "DROP STREAMLIT IF EXISTS DB.SCHEMA.MY_APP;"
uvx snow sql -q "CREATE STREAMLIT DB.SCHEMA.MY_APP
    FROM '@DB.SCHEMA.STREAMLIT_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = MY_WH;"
uvx snow sql -q "ALTER STREAMLIT DB.SCHEMA.MY_APP ADD LIVE VERSION FROM LAST;"
```

**FROM-specific Cause 3: Missing live version activation**

Apps created with `FROM` are not live until `ALTER STREAMLIT ... ADD LIVE VERSION FROM LAST` runs or the owning role visits the app in Snowsight. Non-owner roles see a blank or inaccessible app.

```sql
-- Fix: Activate live version
ALTER STREAMLIT DB.SCHEMA.MY_APP ADD LIVE VERSION FROM LAST;

-- Verify: DESCRIBE should now show live_version_location_uri
DESCRIBE STREAMLIT DB.SCHEMA.MY_APP;
```
