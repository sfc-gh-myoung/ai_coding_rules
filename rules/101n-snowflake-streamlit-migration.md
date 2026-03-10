# Streamlit Migration: Warehouse to Container Runtime

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-09
**Keywords:** migration, Warehouse Runtime, Container Runtime, environment.yml, pyproject.toml, get_active_session, st.connection, runtime migration
**TokenBudget:** ~2100
**ContextTier:** Low
**Depends:** 101l-snowflake-streamlit-deployment.md

## Scope

**What This Rule Covers:**
Step-by-step migration from Warehouse Runtime to Container Runtime for existing Streamlit applications.

**When to Load This Rule:**
- Migrating an existing Warehouse Runtime app to Container Runtime
- Converting environment.yml to pyproject.toml
- Replacing get_active_session() with st.connection()

## References

### Dependencies

**Must Load First:**
- **101l-snowflake-streamlit-deployment.md** - Runtime selection, EAI setup, compute pool creation

**Related:**
- **101c-snowflake-streamlit-security.md** - Secrets migration patterns

## Contract

### Inputs and Prerequisites

- Existing Streamlit app deployed on Warehouse Runtime
- Access to create EAI and compute pools
- Required privileges:
  - CREATE EXTERNAL ACCESS INTEGRATION privilege
  - CREATE COMPUTE POOL privilege (or ACCOUNTADMIN)
  - USAGE on warehouse

### Mandatory

- Convert dependency file format
- Update connection handling for thread safety
- Set up Container Runtime infrastructure before migration

### Forbidden

- Migrating without testing locally first
- Using get_active_session() in Container Runtime

### Execution Steps

1. Convert dependencies (environment.yml to pyproject.toml)
2. Update connection handling
3. Update secrets access
4. Set up infrastructure (EAI + compute pool)
5. Recreate Streamlit object

### Output Format

Migrated Streamlit app running on Container Runtime.

### Validation

- App loads without errors on Container Runtime
- All queries execute correctly
- Secrets accessible

**Troubleshooting:** If app fails to start on Container Runtime, check compute pool status: `DESCRIBE COMPUTE POOL <name>` -- state must be ACTIVE or IDLE. If SUSPENDED, resume it with `ALTER COMPUTE POOL <name> RESUME`.

### Post-Execution Checklist

- [ ] Dependencies converted
- [ ] Connection handling updated
- [ ] Infrastructure provisioned
- [ ] App tested on new runtime

## Step 1: Convert Dependencies

**From environment.yml:**
```yaml
name: my_app
channels:
  - snowflake
dependencies:
  - streamlit=1.51.0
  - pandas
  - plotly
  - pillow
```

**To pyproject.toml:**
```toml
[project]
requires-python = ">=3.11"
dependencies = [
    "streamlit>=1.51",
    "pandas",
    "plotly",
    "Pillow",  # Note: PyPI name differs from conda
]
```

**Common Name Differences:**
- `pillow` (conda) becomes `Pillow` (PyPI)
- `opencv` (conda) becomes `opencv-python` (PyPI)
- `pyyaml` (conda) becomes `PyYAML` (PyPI)

## Step 2: Update Connection Handling

**Before (Warehouse Runtime):**
```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()  # NOT thread-safe, won't work in Container
```

**After (Both Runtimes):**
```python
import streamlit as st
conn = st.connection("snowflake")
session = conn.session()
```

## Step 3: Update Secrets Access

See `101c-snowflake-streamlit-security.md` for detailed secrets migration patterns.

**Summary:**
- Container Runtime: Use `SYSTEM$GET_SECRET('secret_name')` in SQL or `SELECT SYSTEM$GET_SECRET('my_secret')` from Python via session.sql()
- Warehouse Runtime: Can use `_snowflake` module directly

## Step 4: Set Up Infrastructure

1. Create External Access Integration (see 101l)
2. Create Compute Pool (see 101l)
3. Grant necessary permissions

**Verify infrastructure before proceeding:**

```sql
SHOW COMPUTE POOLS LIKE 'streamlit%';
DESCRIBE EXTERNAL ACCESS INTEGRATION pypi_access_integration;
```

## Step 5: Recreate Streamlit Object

```sql
-- Drop old Streamlit (Warehouse Runtime)
DROP STREAMLIT my_db.my_schema.my_app;

-- Create new Streamlit (Container Runtime)
CREATE STREAMLIT my_db.my_schema.my_app
  FROM '@my_db.my_schema.my_stage/streamlit_app'
  MAIN_FILE = 'streamlit_app.py'
  RUNTIME_NAME = 'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'
  COMPUTE_POOL = streamlit_compute_pool
  QUERY_WAREHOUSE = my_warehouse
  EXTERNAL_ACCESS_INTEGRATIONS = (pypi_access_integration);
```

## Migration Checklist

- [ ] Convert `environment.yml` to `pyproject.toml`
- [ ] Update package names (conda to PyPI)
- [ ] Replace `get_active_session()` with `st.connection("snowflake")`
- [ ] Update secrets access pattern (if using `_snowflake` module)
- [ ] Create External Access Integration
- [ ] Create Compute Pool
- [ ] Recreate Streamlit object with new parameters
- [ ] Test all functionality in new runtime

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using `get_active_session()` in Container Runtime**

**Problem:** Copying `get_active_session()` calls into a Container Runtime app, or wrapping it in a try/except as a "fallback." This function relies on the Warehouse Runtime's injected Snowpark session and is fundamentally incompatible with Container Runtime's architecture. It will raise an error at runtime, and try/except wrappers hide the real issue and make debugging harder.

```python
# WRONG - Fallback pattern masks the real problem
try:
    from snowflake.snowpark.context import get_active_session
    session = get_active_session()
except Exception:
    import streamlit as st
    session = st.connection("snowflake").session()
```

**Correct Pattern:** Use `st.connection("snowflake")` unconditionally. It works on both Warehouse and Container Runtimes, is thread-safe, and is the supported API going forward.

```python
import streamlit as st
conn = st.connection("snowflake")
session = conn.session()
```

**Anti-Pattern 2: Copying `environment.yml` Package Names Directly into `pyproject.toml`**

**Problem:** Taking conda package names verbatim and placing them in `pyproject.toml` `dependencies`. Conda and PyPI use different package naming conventions. Some names happen to overlap, but others (like `pillow`, `opencv`, `pyyaml`) differ and will cause install failures or pull the wrong package in Container Runtime.

```toml
# WRONG - conda names used verbatim
[project]
dependencies = [
    "pillow",          # PyPI name is "Pillow" (case-sensitive on some resolvers)
    "opencv",          # Does not exist on PyPI; need "opencv-python"
    "pyyaml",          # PyPI name is "PyYAML"
    "scikit-learn",    # This one happens to be correct
]
```

**Correct Pattern:** Look up each package's actual PyPI name before adding it to `pyproject.toml`. Check common differences: `pillow` -> `Pillow`, `opencv` -> `opencv-python`, `pyyaml` -> `PyYAML`.

```toml
[project]
dependencies = [
    "Pillow",
    "opencv-python",
    "PyYAML",
    "scikit-learn",
]
```

**Anti-Pattern 3: Dropping the Old Streamlit Object Before Verifying the New Infrastructure**

**Problem:** Running `DROP STREAMLIT` on the existing Warehouse Runtime app before confirming the compute pool, External Access Integration, and permissions are all in place. If any infrastructure step fails, the app is down with no quick rollback path.

```sql
-- WRONG - Dropping first with no safety net
DROP STREAMLIT my_db.my_schema.my_app;

-- Then discovering the compute pool doesn't exist yet...
CREATE STREAMLIT my_db.my_schema.my_app
  FROM '@my_db.my_schema.my_stage/streamlit_app'
  MAIN_FILE = 'streamlit_app.py'
  RUNTIME_NAME = 'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'
  COMPUTE_POOL = streamlit_compute_pool  -- ERROR: pool not found
  ...;
```

**Correct Pattern:** Provision and verify all Container Runtime infrastructure first. Optionally deploy under a temporary name to validate, then swap.

```sql
-- 1. Verify infrastructure exists
SHOW COMPUTE POOLS LIKE 'streamlit_compute_pool';
SHOW EXTERNAL ACCESS INTEGRATIONS LIKE 'pypi_access_integration';

-- 2. Deploy with a temporary name to test
CREATE STREAMLIT my_db.my_schema.my_app_v2
  FROM '@my_db.my_schema.my_stage/streamlit_app'
  MAIN_FILE = 'streamlit_app.py'
  RUNTIME_NAME = 'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'
  COMPUTE_POOL = streamlit_compute_pool
  QUERY_WAREHOUSE = my_warehouse
  EXTERNAL_ACCESS_INTEGRATIONS = (pypi_access_integration);

-- 3. Verify my_app_v2 works, then swap
DROP STREAMLIT my_db.my_schema.my_app;
ALTER STREAMLIT my_db.my_schema.my_app_v2 RENAME TO my_db.my_schema.my_app;
```
