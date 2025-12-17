# Snowflake Application Deployment - Troubleshooting & Anti-Patterns

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Snowflake deployment troubleshooting, Streamlit debugging, SiS TypeError, notebook deployment issues, deployment errors, stage file debugging, AUTO_COMPRESS debugging, ROOT_LOCATION errors, deployment anti-patterns, diagnostic commands, deployment validation, cache issues
**TokenBudget:** ~3850
**ContextTier:** Medium
**Depends:** rules/100-snowflake-core.md, rules/109-snowflake-notebooks.md, rules/101-snowflake-streamlit-core.md, rules/109b-snowflake-app-deployment-core.md

## Purpose
Provide comprehensive troubleshooting guidance and anti-pattern identification for Snowflake application deployments, focusing on common errors, diagnostic commands, and proven solutions for Streamlit in Snowflake (SiS) TypeError issues and notebook caching problems.

## Rule Scope

Debugging and troubleshooting deployment issues for notebooks, Streamlit apps, UDFs, and stored procedures in Snowflake

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical diagnostic patterns for efficient debugging.

**MANDATORY:**
**Common Issues & Quick Fixes:**
- **SiS TypeError** - Check AUTO_COMPRESS=FALSE and ROOT_LOCATION match
- **Stale notebook code** - Run full deploy: drop, then remove, then upload, then create
- **Stage file not found** - Verify with `LIST @stage` before CREATE
- **Import errors** - Ensure .py files uncompressed (no .gz extension)
- **Path mismatch** - ROOT_LOCATION must match PUT target paths
- **Cached content** - Always use explicit REMOVE before upload

**Quick Diagnostic Commands:**
```bash
uvx snow sql -q "LIST @STAGE;"                    # Check file locations
uvx snow sql -q "DESCRIBE STREAMLIT DB.SCHEMA.APP;"  # Verify ROOT_LOCATION
uvx snow sql -q "SHOW NOTEBOOKS IN SCHEMA DB.SCHEMA;"  # Confirm object exists
```

## Contract

<contract>
<inputs_prereqs>
- Active Snowflake connection
- Access to stage LIST/DESCRIBE permissions
- Knowledge of deployed application names and stage locations
- Taskfile deployment scripts for re-deployment
</inputs_prereqs>

<mandatory>
- Snowflake CLI diagnostic commands (LIST, DESCRIBE, SHOW)
- Task automation for re-deployment
- grep/filtering for log analysis
- Browser dev tools for client-side debugging
</mandatory>

<forbidden>
- Skipping diagnostic phase and guessing solutions
- Manual file manipulation in Snowsight during troubleshooting
- Partial re-deployment without full cleanup (REMOVE)
- Ignoring ROOT_LOCATION path mismatches
</forbidden>

<steps>
1. Execute diagnostic commands to identify root cause
2. Verify stage file locations and compression status
3. Check ROOT_LOCATION alignment with actual paths
4. Validate full deployment workflow with explicit REMOVE
5. Confirm resolution with post-deployment verification
</steps>

<output_format>
- Diagnostic command outputs with interpretation
- Root cause analysis with evidence
- Step-by-step remediation commands
- Verification commands to confirm fix
</output_format>

<validation>
- Run diagnostic commands and verify expected outputs
- Execute remediation steps and check for errors
- Re-deploy application using full workflow
- Verify application loads without import errors
- Confirm stage files match expected structure (LIST @stage)
</validation>

<design_principles>
- **Diagnose Before Fixing:** Always run diagnostic commands before suggesting solutions
- **Evidence-Based Debugging:** Use command outputs to validate assumptions
- **Root Cause Focus:** Address underlying issues, not symptoms
- **Reproducible Solutions:** Provide automation-based fixes, not manual workarounds
- **Verification Required:** Confirm every fix with validation commands
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using OVERWRITE without explicit REMOVE**
```yaml
# File: task/notebook/Taskfile.yml - INCOMPLETE DEPLOYMENT
version: '3.45'

set: [pipefail]

vars:
  SNOWFLAKE_DB: PROD_DB
  NOTEBOOK_STAGE: "{{.SNOWFLAKE_DB}}.SCHEMA.NOTEBOOK_STAGE"

tasks:
  upload:notebook:
    desc: Upload notebook to stage
    cmds:
      - uvx snow sql -q "PUT file://notebooks/app.ipynb @{{.NOTEBOOK_STAGE}} OVERWRITE=TRUE;"

  create:notebook:
    desc: Create notebook from stage
    cmds:
      - uvx snow sql -q "CREATE NOTEBOOK DB.SCHEMA.APP FROM '@{{.NOTEBOOK_STAGE}}';"

  deploy:notebook:
    desc: Deploy notebook (INCOMPLETE - missing REMOVE)
    cmds:
      - task: upload:notebook  # Only uploads with OVERWRITE
      - task: create:notebook  # May use cached old version
```
**Problem:** No explicit REMOVE step before upload. Even though `OVERWRITE=TRUE` replaces the file in the stage, Snowflake applications (notebooks/Streamlit) cache content at creation time. Subsequent file updates don't automatically propagate to running applications. Result: Stage metadata shows new timestamp, but Snowsight displays old cached code. Developers waste time debugging "phantom" issues that only exist in stale cached versions.

**Correct Pattern:**
```yaml
# File: task/notebook/Taskfile.yml - COMPLETE DEPLOYMENT
version: '3.45'

set: [pipefail]

vars:
  SNOWFLAKE_DB: PROD_DB
  NOTEBOOK_STAGE: "{{.SNOWFLAKE_DB}}.SCHEMA.NOTEBOOK_STAGE"

tasks:
  drop:notebook:
    desc: Drop notebook object
    cmds:
      - uvx snow sql -q "DROP NOTEBOOK IF EXISTS DB.SCHEMA.APP;"

  remove:notebook:
    desc: Remove stage files explicitly
    cmds:
      - uvx snow sql -q "REMOVE @{{.NOTEBOOK_STAGE}}/app.ipynb;"
      - uvx snow sql -q "REMOVE @{{.NOTEBOOK_STAGE}}/environment.yml;"

  upload:notebook:
    desc: Upload notebook to stage
    cmds:
      - uvx snow sql -q "PUT file://notebooks/app.ipynb @{{.NOTEBOOK_STAGE}} AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"

  create:notebook:
    desc: Create notebook from stage
    cmds:
      - uvx snow sql -q "CREATE NOTEBOOK DB.SCHEMA.APP FROM '@{{.NOTEBOOK_STAGE}}';"

  deploy:notebook:
    desc: Deploy notebook with clean slate
    cmds:
      - task: drop:notebook     # 1. Remove old object (clears object cache)
      - task: remove:notebook   # 2. Delete stage files (clears file cache)
      - task: upload:notebook   # 3. Upload fresh files
      - task: create:notebook   # 4. Create from fresh files
```
**Benefits:** Guarantees clean state every deployment, prevents stale caching bugs, predictable results (same output every time), production-ready reliability with minimal overhead (<1s for REMOVE operations)

**Anti-Pattern 2: Manual uploads via Snowsight UI**
```
User workflow:
1. Navigate to Snowsight > Data > Databases > PROD_DB > Stages > NOTEBOOK_STAGE
2. Click "Upload Files" button
3. Select app.ipynb from local filesystem
4. Click "Upload" and wait for confirmation
5. Navigate to Projects > Notebooks
6. Click "Create Notebook", then Select stage location
7. Repeat steps 1-6 for every update
```
**Problem:** Not reproducible (no script record of deployment), no version control (can't audit who deployed what when), no automation (manual clicking required for each deploy), error-prone (easy to forget files or upload to wrong stage), team friction (process differs per developer)

**Correct Pattern:**
```bash
# Automated, version-controlled deployment
task notebook:deploy:app

# Single command handles:
# - Drops old object
# - Removes stale files
# - Uploads all dependencies
# - Creates fresh notebook
# - Validates deployment

# All deployment logic stored in version control (Taskfile.yml + SQL scripts)
# Reproducible across environments (dev, qa, prod)
# Auditable (git log shows deployment changes)
```
**Benefits:** One-command deployment, version-controlled process, reproducible results, team consistency, CI/CD ready, auditable history

**Anti-Pattern 3: Combining upload and create in one task**
```yaml
# File: task/notebook/Taskfile.yml - MONOLITHIC TASK (HARD TO DEBUG)
version: '3.45'

tasks:
  deploy:notebook:
    desc: Deploy notebook (monolithic - all-in-one)
    cmds:
      # All SQL commands inline - no modularity
      - uvx snow sql -q "DROP NOTEBOOK IF EXISTS DB.SCHEMA.APP;"
      - uvx snow sql -q "REMOVE @DB.SCHEMA.STAGE/app.ipynb;"
      - uvx snow sql -q "PUT file://notebooks/app.ipynb @DB.SCHEMA.STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
      - uvx snow sql -q "CREATE NOTEBOOK DB.SCHEMA.APP FROM '@DB.SCHEMA.STAGE' MAIN_FILE='app.ipynb';"
```
**Problem:** No modularity (can't test individual steps in isolation), difficult debugging (which of 4 commands failed?), can't reuse operations (need to duplicate PUT command in other tasks), hard to maintain (SQL commands embedded in YAML, not in dedicated SQL files), no validation between steps (upload might succeed but create might fail silently)

**Correct Pattern:**
```yaml
# File: task/notebook/Taskfile.yml - MODULAR TASKS
version: '3.45'

includes:
  utils:
    taskfile: ../utils/Taskfile.yml
    internal: true

tasks:
  drop:notebook:
    desc: Drop notebook object
    cmds:
      - task: utils:sql:template
        vars: {SQL_FILE: sql/operations/notebook/drop/drop_app.sql}

  remove:notebook:
    desc: Remove stage files
    cmds:
      - task: utils:sql:template
        vars: {SQL_FILE: sql/operations/notebook/remove/remove_app_files.sql}

  upload:notebook:
    desc: Upload to stage
    cmds:
      - task: utils:sql:template
        vars: {SQL_FILE: sql/operations/notebook/upload/upload_app_files.sql}
    preconditions:
      - test -f notebooks/app.ipynb  # Validate file exists

  create:notebook:
    desc: Create from stage
    cmds:
      - task: utils:sql:template
        vars: {SQL_FILE: sql/operations/notebook/create/create_app.sql}

  deploy:notebook:
    desc: Full deployment workflow
    cmds:
      - task: drop:notebook     # Test individually: task drop:notebook
      - task: remove:notebook   # Test individually: task remove:notebook
      - task: upload:notebook   # Test individually: task upload:notebook
      - task: create:notebook   # Test individually: task create:notebook

# SQL files stored separately in sql/operations/notebook/{drop,remove,upload,create}/*.sql
```
**Benefits:** Testable in isolation (`task upload:notebook` to test just upload), reusable operations (other tasks can call `upload:notebook`), easier debugging (know exactly which step failed), maintainable SQL (edit SQL files without touching YAML), validation gates (preconditions prevent bad deploys), CI/CD friendly (run individual steps in pipeline stages)

**Anti-Pattern 4: Hardcoding credentials in scripts**
```sql
-- File: sql/operations/notebook/upload/upload_app.sql - INSECURE
-- ============================================================================
-- DANGER: Hardcoded credentials - security vulnerability!
-- ============================================================================

USE DATABASE PROD_DB;
USE SCHEMA ANALYTICS;
USE WAREHOUSE COMPUTE_WH;

-- Connect with embedded credentials (NEVER DO THIS)
ALTER SESSION SET ACCOUNT_IDENTIFIER = 'abc12345.us-east-1';
ALTER SESSION SET USER = 'admin@company.com';
ALTER SESSION SET PASSWORD = 'PLACEHOLDER_PASSWORD';  -- Plain text password!

PUT 'file://notebooks/app.ipynb'
@PROD_DB.ANALYTICS.NOTEBOOK_STAGE
AUTO_COMPRESS=FALSE
OVERWRITE=TRUE;
```
**Problem:** Security risk (credentials visible in version control, git history permanently stores secrets), not portable (hardcoded account/user breaks for other developers), credential rotation nightmare (must update every SQL file when password changes), audit trail issues (can't track who actually deployed using shared credentials), compliance violations (SOC2, GDPR, PCI-DSS prohibit plain text secrets)

**Correct Pattern:**
```sql
-- File: sql/operations/notebook/upload/upload_app.sql - SECURE
-- ============================================================================
-- Uses Snowflake CLI connection configuration (no credentials in file)
-- ============================================================================

-- No credentials needed - Snowflake CLI handles authentication
-- Connection defined in ~/.snowflake/config.toml or environment variables

PUT 'file://notebooks/app.ipynb'
@<%STAGE%>  -- Variable substitution via Taskfile
AUTO_COMPRESS=FALSE
OVERWRITE=TRUE;
```

```toml
# File: ~/.snowflake/config.toml - Secure credential storage
[connections.prod]
account = "abc12345.us-east-1"
user = "dev@company.com"
authenticator = "externalbrowser"  # SSO authentication (no password storage)
database = "PROD_DB"
schema = "ANALYTICS"
warehouse = "COMPUTE_WH"
```

```yaml
# File: task/notebook/Taskfile.yml - Uses configured connection
tasks:
  upload:notebook:
    desc: Upload using secure connection
    cmds:
      # Snowflake CLI automatically uses connection from config.toml
      - task: utils:sql:template
        vars:
          SQL_FILE: sql/operations/notebook/upload/upload_app.sql
          STAGE: "{{.SNOWFLAKE_DB}}.{{.SNOWFLAKE_SCHEMA}}.NOTEBOOK_STAGE"
    # No credentials in Taskfile - all auth handled by CLI config
```
**Benefits:** Secure credential management (secrets never in version control), portable across developers (each uses own credentials from config), SSO integration (externalbrowser authenticator for corporate auth), easy credential rotation (update config.toml once), audit trail (individual credentials tracked in Snowflake), compliance ready (meets security standards)

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

## Output Format Examples

```bash
# Diagnostic workflow for SiS TypeError

# 1. Check file compression status
uvx snow sql -q "LIST @DB.SCHEMA.STAGE;" | grep -E "\.py|\.yml"

# 2. Verify ROOT_LOCATION configuration
uvx snow sql -q "DESCRIBE STREAMLIT DB.SCHEMA.APP_NAME;"

# 3. If compression issue found:
task streamlit:remove:app
task streamlit:upload:app  # With AUTO_COMPRESS=FALSE
task streamlit:create:app

# 4. Verify fix
uvx snow sql -q "LIST @DB.SCHEMA.STAGE;" | grep "\.py$"  # Should show .py, not .py.gz

# 5. Test in Snowsight
# Navigate to Apps > Streamlit > APP_NAME
# Expected: Application loads without TypeError
```

## References

### External Documentation
- [Snowflake PUT Command](https://docs.snowflake.com/en/sql-reference/sql/put) - AUTO_COMPRESS behavior and troubleshooting
- [Snowflake REMOVE Command](https://docs.snowflake.com/en/sql-reference/sql/remove) - Idempotent file removal patterns
- [Snowflake LIST Command](https://docs.snowflake.com/en/sql-reference/sql/list) - Stage file inspection and diagnostics
- [Streamlit in Snowflake Troubleshooting](https://docs.snowflake.com/en/developer-guide/streamlit/troubleshooting) - Official SiS debugging guide
- [Snowflake Stages](https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage) - Stage architecture and file organization

### Related Rules
- **Core Deployment Patterns**: `rules/109b-snowflake-app-deployment-core.md` - See this rule for foundational deployment automation patterns and workflows
- **Snowflake Notebooks**: `rules/109-snowflake-notebooks.md`
- **Streamlit Core**: `rules/101-snowflake-streamlit-core.md`
- **Taskfile Automation**: `rules/820-taskfile-automation.md`
- **Snowflake Core**: `rules/100-snowflake-core.md`

## Troubleshooting Deployment Issues

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
