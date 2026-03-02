# Streamlit Deployment Errors

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v2.0.0
**LastUpdated:** 2026-03-02
**Keywords:** deployment error, Container Runtime, Warehouse Runtime, EAI error, compute pool, stage upload, service startup, troubleshooting, runtime error
**TokenBudget:** ~2200
**ContextTier:** Low
**Depends:** 101-snowflake-streamlit-core.md, 101l-snowflake-streamlit-deployment.md

## Scope

**What This Rule Covers:**
Deployment error scenarios and resolution steps for Streamlit applications in both Container Runtime and Warehouse Runtime environments.

**When to Load This Rule:**
- Debugging Container Runtime deployment failures
- Troubleshooting Warehouse Runtime errors
- Resolving External Access Integration (EAI) issues
- Fixing compute pool or stage problems
- Diagnosing service startup timeouts

## References

### Dependencies

**Must Load First:**
- **101-snowflake-streamlit-core.md** - Core Streamlit patterns
- **101l-snowflake-streamlit-deployment.md** - Deployment guidance

**Related:**
- **101c-snowflake-streamlit-security.md** - Security patterns

### External Documentation

- [Runtime Environments](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments)
- [Streamlit Troubleshooting](https://docs.snowflake.com/en/developer-guide/streamlit/troubleshooting)

## Contract

### Inputs and Prerequisites

- Streamlit deployment attempted
- Error message from deployment or app logs
- Access to Snowflake account with appropriate permissions

### Mandatory

- Identify error type from error message
- Follow resolution steps in order
- Verify fix before redeploying

### Forbidden

- Deploying without testing locally first
- Ignoring service logs when debugging
- Hardcoding credentials

### Execution Steps

1. Match error message to error scenario below
2. Follow resolution steps for that scenario
3. Verify fix locally if possible
4. Redeploy and monitor

### Output Format

Resolved deployment with Streamlit app accessible.

### Validation

- App loads without errors
- All features functional
- Logs show no warnings

### Post-Execution Checklist

- [ ] Error identified and matched to scenario
- [ ] Resolution steps followed in order
- [ ] Fix verified before redeploying
- [ ] App accessible after deployment

## Container Runtime Errors

### Error 1: External Access Integration Missing

```
Error: External access integration required for Container Runtime
Could not resolve host: pypi.org
```

**Cause:** Container Runtime requires EAI to access PyPI for package installation.

**Resolution:**
1. Create network rule for PyPI:
```sql
CREATE OR REPLACE NETWORK RULE pypi_network_rule
  TYPE = HOST_PORT
  MODE = EGRESS
  VALUE_LIST = ('pypi.org:443', 'files.pythonhosted.org:443');
```
2. Create external access integration:
```sql
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION pypi_access_integration
  ALLOWED_NETWORK_RULES = (pypi_network_rule)
  ENABLED = TRUE;
```
3. Add EAI to CREATE STREAMLIT command:
```sql
CREATE STREAMLIT ... EXTERNAL_ACCESS_INTEGRATIONS = (pypi_access_integration);
```

### Error 2: Compute Pool Not Ready

```
Error: Compute pool 'STREAMLIT_COMPUTE_POOL' is not in ACTIVE state
```

**Cause:** Compute pool not created, suspended, or still provisioning.

**Resolution:**
1. Check compute pool status: `SHOW COMPUTE POOLS`
2. Resume if suspended: `ALTER COMPUTE POOL streamlit_compute_pool RESUME`
3. Wait for ACTIVE state (may take several minutes on first creation)
4. Verify pool has sufficient resources for app requirements

### Error 3: Package Installation Failure

```
Error: Failed to install package 'mypackage>=1.0'
No matching distribution found
```

**Cause:** Package not available on PyPI or version constraint unsatisfiable.

**Resolution:**
1. Verify package exists on PyPI: `pip search mypackage` or check pypi.org
2. Check version constraints in `pyproject.toml` are valid
3. Test locally: `uv pip install -r pyproject.toml`
4. Use compatible version ranges, avoid overly strict pins

### Error 4: Python Version Mismatch

```
Error: Container Runtime requires Python 3.11
```

**Cause:** Container Runtime only supports Python 3.11.

**Resolution:**
1. Update `pyproject.toml`:
```toml
[project]
requires-python = ">=3.11"
```
2. Ensure all dependencies are compatible with Python 3.11
3. Test locally with Python 3.11

## Warehouse Runtime Errors

### Error 5: Stage Upload Compression Issue

```
TypeError: bad argument type for built-in operation
ModuleNotFoundError: No module named 'my_module'
```

**Cause:** Files compressed during upload; Python can't import `.py.gz` files.

**Resolution:**
1. Always disable auto-compression:
```bash
snow stage copy streamlit/ @STAGE --recursive --no-auto-compress --overwrite
```
```sql
PUT file://streamlit_app.py @STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```
2. Verify files on stage are `.py` not `.py.gz`: `LIST @STAGE`
3. Re-upload all files with compression disabled

### Error 6: environment.yml Python Version

```
Error: Python version specification not allowed in environment.yml
```

**Cause:** Warehouse Runtime manages Python version; explicit `python=X.Y` forbidden.

**Resolution:**
1. Remove `python=X.Y` from environment.yml:
```yaml
# CORRECT
name: my_app
channels:
  - snowflake
dependencies:
  - streamlit=1.51.0
  - pandas
```
2. Use only `snowflake` channel
3. Avoid conda-forge or other channels

### Error 7: Missing Streamlit Version Pin

```
Error: st.navigation is not a function
AttributeError: module 'streamlit' has no attribute 'Page'
```

**Cause:** Default bundled Streamlit version (1.22.0) lacks modern APIs.

**Resolution:**
1. Pin Streamlit version in environment.yml:
```yaml
dependencies:
  - streamlit=1.51.0  # Pin to modern version
```
2. Ensure version >=1.50 for `st.navigation()`, `st.Page()`
3. Check available versions: [Snowflake Anaconda Channel](https://repo.anaconda.com/pkgs/snowflake/)

### Error 8: get_active_session() Failure

```
SnowparkSessionException: No active session
```

**Cause:** `get_active_session()` only works in Warehouse Runtime, not Container Runtime.

**Resolution:**
1. Use `st.connection("snowflake")` instead (works in both runtimes):
```python
# Works in both Container Runtime and Warehouse Runtime
conn = st.connection("snowflake")
df = conn.query("SELECT * FROM my_table")
```
2. Avoid `snowflake.snowpark.context.get_active_session()` for portability

## Common Errors (Both Runtimes)

### Error 9: Stage Path Not Found

```
Error: Stage '@MY_DB.MY_SCHEMA.MY_STAGE/streamlit_app' does not exist
```

**Cause:** Stage doesn't exist or path incorrect.

**Resolution:**
1. Verify stage exists: `SHOW STAGES IN SCHEMA`
2. Check full path matches CREATE STREAMLIT exactly
3. Ensure files uploaded to correct subdirectory
4. Verify grants: `SHOW GRANTS ON STAGE <name>`

### Error 10: Permission Denied

```
Error: Insufficient privileges to operate on schema 'MY_SCHEMA'
```

**Cause:** Missing privileges on database, schema, or warehouse.

**Resolution:**
1. Grant required privileges:
```sql
GRANT USAGE ON DATABASE my_db TO ROLE my_role;
GRANT USAGE ON SCHEMA my_db.my_schema TO ROLE my_role;
GRANT CREATE STREAMLIT ON SCHEMA my_db.my_schema TO ROLE my_role;
GRANT USAGE ON WAREHOUSE my_warehouse TO ROLE my_role;
```
2. For Container Runtime, also grant compute pool usage:
```sql
GRANT USAGE ON COMPUTE POOL streamlit_compute_pool TO ROLE my_role;
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Debugging Without Checking Runtime Type

```python
# Assuming Warehouse Runtime patterns work in Container Runtime
from snowflake.snowpark.context import get_active_session
session = get_active_session()  # Fails silently in Container Runtime
```

**Problem:** Different runtimes have different capabilities. `get_active_session()` only works in Warehouse Runtime.

**Correct Pattern:**
```python
# Use st.connection which works in both runtimes
conn = st.connection("snowflake")
df = conn.query("SELECT * FROM my_table")
```

### Anti-Pattern 2: Ignoring Compression on Stage Upload

```bash
# Missing --no-auto-compress flag
snow stage copy app/ @STAGE --recursive --overwrite
```

**Problem:** Files get compressed to `.py.gz`, causing silent import failures with cryptic `TypeError` messages.

**Correct Pattern:**
```bash
snow stage copy app/ @STAGE --recursive --no-auto-compress --overwrite
```

### Anti-Pattern 3: Creating EAI Without All Required Domains

```sql
-- Missing required PyPI domains
CREATE NETWORK RULE pypi_rule
  TYPE = HOST_PORT MODE = EGRESS
  VALUE_LIST = ('pypi.org:443');  -- Incomplete!
```

**Problem:** Package downloads fail because `files.pythonhosted.org` is not included.

**Correct Pattern:**
```sql
CREATE NETWORK RULE pypi_rule
  TYPE = HOST_PORT MODE = EGRESS
  VALUE_LIST = ('pypi.org:443', 'files.pythonhosted.org:443');
```

## Validation Checklist

**Before Deployment:**
- [ ] Dependencies tested locally
- [ ] Stage exists and files uploaded (compression disabled for Warehouse Runtime)
- [ ] EAI configured (Container Runtime)
- [ ] Compute pool active (Container Runtime)
- [ ] Grants verified

**After Deployment:**
- [ ] App loads successfully
- [ ] All imports resolve
- [ ] Database queries execute
- [ ] No errors in logs
