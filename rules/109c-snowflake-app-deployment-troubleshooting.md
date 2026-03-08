# Snowflake Application Deployment - Troubleshooting & Anti-Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-02-19
**LoadTrigger:** kw:deployment-error
**Keywords:** Snowflake deployment troubleshooting, Streamlit debugging, SiS TypeError, notebook deployment issues, deployment errors, stage file debugging, AUTO_COMPRESS debugging, ROOT_LOCATION errors, deployment anti-patterns, diagnostic commands, deployment validation, cache issues
**TokenBudget:** ~5300
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md, 109-snowflake-notebooks.md, 101-snowflake-streamlit-core.md, 109b-snowflake-app-deployment-core.md

## Scope

**What This Rule Covers:**
Comprehensive troubleshooting guidance and anti-pattern identification for Snowflake application deployments, focusing on common errors, diagnostic commands, and proven solutions for Streamlit in Snowflake (SiS) TypeError issues and notebook caching problems.

**When to Load This Rule:**
- Debugging Streamlit deployment errors
- Troubleshooting notebook caching issues
- Resolving TypeError in Streamlit in Snowflake (SiS)
- Diagnosing stage file problems
- Fixing application deployment failures

## References

### External Documentation
- [Streamlit in Snowflake (SiS) Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit) - Official SiS guide
- [Snowflake Notebooks Troubleshooting](https://docs.snowflake.com/en/user-guide/ui-snowsight-notebooks-troubleshoot) - Notebook debugging
- [Stage Management](https://docs.snowflake.com/en/user-guide/data-load-stages-intro) - Stage operations reference
- [Python Imports in Snowflake](https://docs.snowflake.com/en/developer-guide/udf/python/udf-python-packages) - Package and import handling

### Related Rules
- **Core Deployment**: `109b-snowflake-app-deployment-core.md` - Base deployment patterns
- **Streamlit Core**: `101-snowflake-streamlit-core.md` - Streamlit development
- **Snowflake Notebooks**: `109-snowflake-notebooks.md` - Notebook best practices
- **Snowflake Core**: `100-snowflake-core.md` - Foundational practices

## Contract

### Inputs and Prerequisites
- Active Snowflake connection
- Access to stage LIST/DESCRIBE permissions
- Knowledge of deployed application names and stage locations
- Taskfile deployment scripts for re-deployment

### Mandatory
- Run diagnostic commands (LIST, DESCRIBE, SHOW) before suggesting fixes
- Evidence-based root cause identification from command outputs
- Full deployment workflow for remediation (DROP, REMOVE, PUT, CREATE)
- `AUTO_COMPRESS=FALSE` verified in all PUT commands for application files
- `ROOT_LOCATION` verified to match actual stage file paths
- Post-fix verification commands to confirm resolution

### Forbidden
- Skipping diagnostic phase and guessing solutions
- Manual file manipulation in Snowsight during troubleshooting
- Partial re-deployment without full cleanup (REMOVE)
- Ignoring ROOT_LOCATION path mismatches

### Execution Steps
1. Execute diagnostic commands to identify root cause
2. Verify stage file locations and compression status
3. Check ROOT_LOCATION alignment with actual paths
4. Validate full deployment workflow with explicit REMOVE
5. Confirm resolution with post-deployment verification

### Output Format
- Diagnostic command outputs with interpretation
- Root cause analysis with evidence
- Step-by-step remediation commands
- Verification commands to confirm fix

### Validation
- Run diagnostic commands and verify expected outputs
- Execute remediation steps and check for errors
- Re-deploy application using full workflow
- Verify application loads without import errors
- Confirm stage files match expected structure (LIST @stage)

### Design Principles
- **Diagnose Before Fixing:** Always run diagnostic commands before suggesting solutions
- **Evidence-Based Debugging:** Use command outputs to validate assumptions
- **Root Cause Focus:** Address underlying issues, not symptoms
- **Reproducible Solutions:** Provide automation-based fixes, not manual workarounds
- **Verification Required:** Confirm every fix with validation commands

### Post-Execution Checklist

See detailed Post-Execution Checklist below for comprehensive troubleshooting validation steps.

## Anti-Patterns and Common Mistakes

### Deployment Process Anti-Patterns

See `109b-snowflake-app-deployment-core.md` for these foundational anti-patterns:
- **Anti-Pattern 1: Skipping REMOVE Step** - OVERWRITE alone causes stale cache issues
- **Anti-Pattern 2: Manual Snowsight UI Uploads** - Not reproducible or version-controlled
- **Anti-Pattern 3: Monolithic Deploy Tasks** - Combining all operations in one task prevents isolated debugging
- **Anti-Pattern 4: Hardcoded Credentials** - Security risk; use Snowflake CLI config instead

### Troubleshooting-Specific Anti-Patterns

**Anti-Pattern 5: Omitting AUTO_COMPRESS=FALSE for Streamlit SiS**
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

**Correct Pattern:**
```sql
# Correct: Explicit AUTO_COMPRESS=FALSE
PUT file://streamlit_app.py @STAGE
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;

PUT file://pages/*.py @STAGE/pages/
    AUTO_COMPRESS=FALSE
    OVERWRITE=TRUE;
```

**Anti-Pattern 6: Uploading Streamlit files to subdirectory path**
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

**Correct Pattern:**
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

**Anti-Pattern 7: Inverted Compression Flag Logic in Python Wrappers**
```python
# WRONG: Only adds --auto-compress when True, never adds --no-auto-compress when False
def snow_stage_copy(source, dest, auto_compress=True, recursive=False):
    flags = ["--overwrite"]
    if auto_compress:
        flags.append("--auto-compress")  # Redundant — already the CLI default
    if recursive:
        flags.append("--recursive")
    # When auto_compress=False, NO flag is added → CLI defaults to compress ON
    # Files silently stored as .py.gz; deployment succeeds but app crashes at runtime
```
**Problem:** The `--auto-compress` flag is already the CLI default, so adding it when `True` is redundant. When `False`, no flag is passed, so compression is never actually disabled. Deployment reports `[PASS]` but the app fails with `TypeError: bad argument type for built-in operation` because `.py` files are stored as `.py.gz`.

**Correct Pattern:**
```python
# CORRECT: Default auto_compress=False for app deployment, pass --no-auto-compress
def snow_stage_copy(source, dest, auto_compress=False, recursive=False):
    flags = ["--overwrite"]
    if not auto_compress:
        flags.append("--no-auto-compress")  # Explicitly disables compression
    if recursive:
        flags.append("--recursive")
```
**Key rules:**
- Default `auto_compress` to `False` for application deployment functions
- Pass `--no-auto-compress` when compression is disabled (not absence of `--auto-compress`)
- Verify with `LIST @stage` that files show `.py` not `.py.gz` after upload

## Post-Execution Checklist

- [ ] Diagnostic commands executed before suggesting fixes
- [ ] Root cause identified with evidence (command outputs)
- [ ] Solutions address underlying issue, not symptoms
- [ ] Remediation uses automation (Taskfile), not manual steps
- [ ] Verification commands provided to confirm fix
- [ ] AUTO_COMPRESS=FALSE verified for all .py files in Streamlit
- [ ] ROOT_LOCATION matches actual stage file paths
- [ ] Explicit REMOVE step included in deployment workflow
- [ ] Modular task structure (can test individual operations)
- [ ] No credentials hardcoded in scripts or Taskfiles
- [ ] Python/CLI wrappers pass `--no-auto-compress` (not absence of `--auto-compress`)
- [ ] Verified with `LIST @stage` that files show `.py` not `.py.gz` after upload

## Validation

- **Success Checks:**
  - Diagnostic commands reveal clear root cause
  - Remediation steps resolve issue completely
  - Verification commands confirm application functional
  - No workarounds or manual UI fixes required
  - Solution documented and reproducible

- **Negative Tests:**
  - Attempted fixes without diagnostics fail to resolve issue
  - Manual workarounds create new issues or hide root cause
  - Missing REMOVE step causes recurring stale cache problems

> **Investigation Required**
> When troubleshooting deployment issues:
> 1. **Execute diagnostic commands BEFORE making assumptions** - LIST @stage, DESCRIBE object, SHOW objects
> 2. **Verify file compression status** - Look for .gz extensions (indicates compression problem)
> 3. **Check ROOT_LOCATION alignment** - DESCRIBE output must match LIST paths exactly
> 4. **Validate full workflow executed** - Confirm drop, then remove, then upload, then create all ran
> 5. **Test in isolation** - Run individual task operations to identify failing step
>
> **Anti-Pattern:**
> "Your Streamlit app probably has a code error. Try fixing the Python syntax."
> "Just re-upload the file manually via Snowsight UI."
>
> **Correct Pattern:**
> "Let me diagnose the TypeError by checking file compression and paths."
> [runs LIST @stage to check .py.gz vs .py]
> [runs DESCRIBE STREAMLIT to verify ROOT_LOCATION]
> "Found the issue: files are compressed (.py.gz). Need to redeploy with AUTO_COMPRESS=FALSE."

## Troubleshooting Deployment Issues

### Additional References
- [Snowflake REMOVE Command](https://docs.snowflake.com/en/sql-reference/sql/remove) - Idempotent file removal patterns
- [Snowflake LIST Command](https://docs.snowflake.com/en/sql-reference/sql/list) - Stage file inspection and diagnostics
- [Streamlit in Snowflake Troubleshooting](https://docs.snowflake.com/en/developer-guide/streamlit/troubleshooting) - Official SiS debugging guide
- [Snowflake Stages](https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage) - Stage architecture and file organization

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

**Cause 3: Inverted Compression Flag in Python/CLI Wrappers**
- Python wrapper function adds `--auto-compress` when `True` (redundant — already the default)
- But never adds `--no-auto-compress` when `False` — compression is never actually disabled
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

# Step 2: Verify ROOT_LOCATION matches actual file paths
uvx snow sql -q "DESCRIBE STREAMLIT UTILITY_DEMO_V2.GRID_DATA.APP_NAME;"

# Look for ROOT_LOCATION value in output
# Expected: ROOT_LOCATION = @UTILITY_DEMO_V2.GRID_DATA.STREAMLIT_STAGE
# Must match LIST output paths (no extra /streamlit/ subdirectory nesting)

# Verify paths align:
# LIST shows: streamlit_stage/streamlit_app.py
# ROOT_LOCATION: @STREAMLIT_STAGE  (correct - matches root)
# NOT: @STREAMLIT_STAGE/streamlit  (wrong - extra subdirectory)

# Step 3: Detailed file listing with grep filter
uvx snow sql -q "LIST @UTILITY_DEMO_V2.GRID_DATA.STREAMLIT_STAGE;" \
  | grep -E "\.py$|\.yml$"

# Should show .py extensions (not .py.gz):
# streamlit_app.py   ✓ Correct
# pages/1_Home.py    ✓ Correct
# environment.yml    ✓ Correct
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

# Should see (file extensions without .gz):
# streamlit_stage/streamlit_app.py          ✓ Uncompressed
# streamlit_stage/pages/1_Page.py           ✓ Uncompressed
# streamlit_stage/environment.yml           ✓ Uncompressed

# Should NOT see:
# streamlit_stage/streamlit_app.py.gz       ✗ Compressed (causes TypeError)
# streamlit_stage/streamlit/app.py          ✗ Wrong path (ROOT_LOCATION mismatch)

# Verify Streamlit app loads without errors
# Navigate to Snowsight > Apps > Streamlit > APP_NAME
# Expected: Application loads, pages render, no TypeError

# Verify import system works
uvx snow sql -q "
SELECT SYSTEM\$CHECK_FILE_EXISTS('@STAGE/streamlit_app.py');
"
# Should return: TRUE (file exists and is accessible)
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

### Issue: "AttributeError: module 'streamlit' has no attribute 'X'"

**Symptoms:**
- Streamlit app fails with `AttributeError: module 'streamlit' has no attribute 'navigation'`
  (or `'Page'`, `'dialog'`, `'fragment'`, or other modern API)
- App works locally but fails when deployed to SiS
- Error appears immediately on app load or when navigating to a page that uses the missing API

**Root Cause:**
Missing or incorrect `environment.yml` in the stage. Without `environment.yml`, SiS defaults
to its bundled Streamlit version (currently **1.22.0**), which predates many modern APIs:

- `st.navigation()` — requires 1.36+ (not available in SiS default 1.22.0)
- `st.Page()` — requires 1.36+ (not available in SiS default 1.22.0)
- `st.dialog()` — requires 1.37+ (not available in SiS default 1.22.0)
- `st.fragment()` — requires 1.37+ (not available in SiS default 1.22.0)
- `st.rerun()` — requires 1.27+ (not available in SiS default 1.22.0)

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

2. **Redeploy with environment.yml included:**
   ```bash
   # Using snow stage copy (recommended for multi-file apps)
   uvx --from=snowflake-cli==3.14 snow stage copy \
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
       ROOT_LOCATION = '@DB.SCHEMA.STREAMLIT_STAGE'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = MY_WH;"
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

### Issue: Permission/Role Errors During Deployment

**Symptoms:**
- "Insufficient privileges" or "Access denied" during PUT, CREATE, or DROP
- Deployment works for one developer but not another

**Diagnostic Steps:**
```sql
-- Check current role and privileges
SELECT CURRENT_ROLE(), CURRENT_USER();

-- Verify stage access
SHOW GRANTS ON STAGE DB.SCHEMA.NOTEBOOK_STAGE;

-- Verify schema privileges (needed for CREATE NOTEBOOK/STREAMLIT)
SHOW GRANTS ON SCHEMA DB.SCHEMA;

-- Verify warehouse access (needed for QUERY_WAREHOUSE in CREATE)
SHOW GRANTS ON WAREHOUSE COMPUTE_WH;
```

**Required Privileges:**
- **PUT/REMOVE**: WRITE privilege on stage
- **CREATE NOTEBOOK**: CREATE NOTEBOOK privilege on schema
- **CREATE STREAMLIT**: CREATE STREAMLIT privilege on schema
- **DROP**: OWNERSHIP on the object, or appropriate DROP privilege
- **QUERY_WAREHOUSE**: USAGE privilege on the warehouse

**Fix:**
```sql
-- Grant deployment privileges to a role
GRANT USAGE ON SCHEMA DB.SCHEMA TO ROLE DEPLOYER;
GRANT WRITE ON STAGE DB.SCHEMA.NOTEBOOK_STAGE TO ROLE DEPLOYER;
GRANT CREATE NOTEBOOK ON SCHEMA DB.SCHEMA TO ROLE DEPLOYER;
GRANT CREATE STREAMLIT ON SCHEMA DB.SCHEMA TO ROLE DEPLOYER;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE DEPLOYER;
```
