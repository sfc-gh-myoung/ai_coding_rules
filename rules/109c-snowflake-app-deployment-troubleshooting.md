# Snowflake Application Deployment - Troubleshooting & Anti-Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:deployment-error
**Keywords:** Snowflake deployment troubleshooting, Streamlit debugging, SiS TypeError, notebook deployment issues, deployment errors, stage file debugging, AUTO_COMPRESS debugging, ROOT_LOCATION errors, deployment anti-patterns, diagnostic commands, deployment validation, cache issues
**TokenBudget:** ~3500
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
- **SiS TypeError/AttributeError Debugging**: `109j-snowflake-sis-typeerror-debugging.md` - Detailed diagnostic workflows for TypeError and AttributeError
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

**Problem:** Uploading Streamlit files without `AUTO_COMPRESS=FALSE` causes them to be gzipped, which Snowflake cannot interpret.

```sql
-- WRONG: Missing AUTO_COMPRESS=FALSE
PUT file://streamlit_app.py @MY_STAGE OVERWRITE=TRUE;
-- File is compressed, causing "TypeError: bad argument type for built-in operation"
```

**Correct Pattern:**

```sql
-- CORRECT: Always specify AUTO_COMPRESS=FALSE for Streamlit files
PUT file://streamlit_app.py @MY_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
-- File remains uncompressed and readable by Snowflake
```

See `109b-snowflake-app-deployment-core.md` Anti-Pattern 2 for additional context on the `AUTO_COMPRESS=FALSE` requirement.

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

See `109b-snowflake-app-deployment-core.md` Anti-Pattern 3 for the inverted compression flag pattern and correct `--no-auto-compress` usage.

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

### Quick Troubleshooting Decision Tree

- **TypeError?** Check `AUTO_COMPRESS=FALSE`, then check `ROOT_LOCATION` path, then check wrapper flags (`--no-auto-compress`)
- **AttributeError?** Check `environment.yml`, then check Streamlit version, then see 109j
- **Stale code?** Run full deploy (`task deploy:app`), then clear browser cache (`Cmd+Shift+R`)
- **Permission denied?** Check `CURRENT_ROLE()`, then run `SHOW GRANTS TO ROLE`, then grant missing privileges
- **CREATE fails?** Run `DROP` first, then check object exists, then verify stage files with `LIST`

## Troubleshooting Deployment Issues

### Additional References
- [Snowflake REMOVE Command](https://docs.snowflake.com/en/sql-reference/sql/remove) - Idempotent file removal patterns
- [Snowflake LIST Command](https://docs.snowflake.com/en/sql-reference/sql/list) - Stage file inspection and diagnostics
- [Streamlit in Snowflake Troubleshooting](https://docs.snowflake.com/en/developer-guide/streamlit/troubleshooting) - Official SiS debugging guide
- [Snowflake Stages](https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage) - Stage architecture and file organization

### Issue: Streamlit SiS fails with "TypeError: bad argument type for built-in operation"

See **109j-snowflake-sis-typeerror-debugging.md** for the full diagnostic workflow covering three root causes (missing AUTO_COMPRESS=FALSE, stage path mismatch, inverted compression flag in wrappers), step-by-step diagnostic commands, solutions, and verification steps.

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

See **109j-snowflake-sis-typeerror-debugging.md** for the full diagnostic workflow covering missing or outdated `environment.yml`, Streamlit API version compatibility table, diagnostic commands, fix steps, and prevention guidance.

### Issue: environment.yml Problems

**Common causes:**
- Wrong Streamlit version pinned (e.g., `streamlit==1.22.0` lacks newer APIs)
- Missing required packages not listed in dependencies
- Version conflicts between packages

**Quick fix:** Verify `environment.yml` includes `streamlit>=1.50` and all imported packages. For detailed environment debugging, see **109j-snowflake-sis-typeerror-debugging.md**.

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

-- Check effective privileges for a user
SHOW GRANTS TO ROLE DEPLOYER;

-- Revoke excessive privileges if needed
REVOKE ALL ON SCHEMA DB.SCHEMA FROM ROLE DEPLOYER;

-- Debug role hierarchy
SHOW GRANTS OF ROLE DEPLOYER;  -- Who has DEPLOYER role?
SHOW GRANTS TO ROLE DEPLOYER;  -- What can DEPLOYER do?
```
