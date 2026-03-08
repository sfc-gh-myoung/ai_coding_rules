# Streamlit Deployment: Runtime Selection and Setup

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-02
**Keywords:** Container Runtime, Warehouse Runtime, deployment, pyproject.toml, environment.yml, compute pool, EAI, external access integration, CREATE STREAMLIT, migration
**TokenBudget:** ~4000
**ContextTier:** High
**Depends:** 101-snowflake-streamlit-core.md

## Scope

**What This Rule Covers:**
Comprehensive deployment guidance for Streamlit applications in Snowflake, covering runtime selection (Container vs Warehouse), dependency management, External Access Integration (EAI) setup, and migration between runtimes.

**When to Load This Rule:**
- Deploying a new Streamlit application to Snowflake
- Choosing between Container Runtime and Warehouse Runtime
- Setting up External Access Integration for PyPI access
- Migrating an existing app from Warehouse to Container Runtime
- Troubleshooting deployment configuration issues

## References

### Dependencies

**Must Load First:**
- **101-snowflake-streamlit-core.md** - Core Streamlit patterns and state management

**Related:**
- **101f-snowflake-streamlit-deployment-errors.md** - Deployment error troubleshooting
- **101c-snowflake-streamlit-security.md** - Secrets management by runtime

### External Documentation

- [Runtime Environments](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/runtime-environments) - Official runtime comparison
- [Dependency Management](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/dependency-management) - Package management by runtime
- [File Organization](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/file-organization) - Project structure
- [Secrets and Configuration](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/secrets-and-configuration) - Secrets by runtime

## Contract

### Inputs and Prerequisites

- Snowflake account with Streamlit privileges
- Application source code ready for deployment
- Understanding of compute requirements: Container Runtime needs a compute pool (`CPU_X64_XS` minimum, ~$0.06/credit); Warehouse Runtime uses a virtual warehouse (`X-SMALL` sufficient for most apps)

### Mandatory

- **Choose runtime based on requirements** - Use decision guide below
- **Container Runtime (DEFAULT):** Recommended for most applications
- **Set up EAI before Container Runtime deployment** - Required for PyPI access
- **Use correct dependency file format** - `pyproject.toml` for Container, `environment.yml` for Warehouse

### Forbidden

- Deploying Container Runtime without EAI (if packages needed beyond pre-installed)
- Using `environment.yml` with Container Runtime
- Using `pyproject.toml` with Warehouse Runtime
- Using `get_active_session()` in Container Runtime (not thread-safe)

### Execution Steps

1. Select runtime using decision guide
2. Create dependency file in correct format
3. For Container Runtime: Set up EAI and compute pool
4. Create Streamlit object with appropriate parameters
5. Verify deployment and test functionality

### Output Format

Deployed Streamlit application accessible via Snowsight URL.

### Validation

- Application loads without errors
- All dependencies resolve correctly
- Secrets accessible (if configured)
- Query warehouse responds to queries

### Post-Execution Checklist

- [ ] Runtime selected based on requirements
- [ ] Dependency file in correct format for runtime
- [ ] EAI configured (Container Runtime only)
- [ ] Compute pool created (Container Runtime only)
- [ ] CREATE STREAMLIT executed successfully
- [ ] Application accessible and functional

## Runtime Selection Decision Guide

### DEFAULT: Container Runtime

**Use Container Runtime for most applications.** It provides:

- **Cost-effective:** Compute pools cost less than warehouses per minute
- **Fast viewer experience:** Shared instance means no per-viewer startup delay
- **Full caching support:** `@st.cache_data` and `@st.cache_resource` work across sessions
- **Latest Streamlit:** Access to any Streamlit version including nightly builds
- **PyPI access:** Install any package from PyPI (with EAI)

**Container Runtime is recommended when:**
- Building dashboards for multiple concurrent users
- Application benefits from shared caching
- Need packages not in Snowflake Anaconda Channel
- Want latest Streamlit features (1.50+)
- Cost optimization is important

### ALTERNATIVE: Warehouse Runtime

**Use Warehouse Runtime when:**
- Need per-viewer isolation (each user gets separate instance)
- Require packages only available in Snowflake Anaconda Channel
- Cannot configure External Access Integration (security restrictions)
- Existing application already uses `environment.yml`
- Need Python 3.9 or 3.10 (Container Runtime only supports 3.11)

### Feature Comparison

**Container Runtime:**
- **Compute:** Compute pool node
- **Instance Model:** Shared among viewers
- **Startup Time:** Fast (already running)
- **Python Versions:** 3.11 only
- **Streamlit Versions:** 1.50+ (any, including nightly)
- **Dependency File:** `pyproject.toml` or `requirements.txt`
- **Package Source:** PyPI (with EAI)
- **Caching:** Full cross-session support
- **Entrypoint Location:** Root or subdirectory
- **`get_active_session()`:** Not supported
- **`st.connection("snowflake")`:** Supported

**Warehouse Runtime:**
- **Compute:** Virtual warehouse
- **Instance Model:** Personal per viewer
- **Startup Time:** Slower (on-demand)
- **Python Versions:** 3.9, 3.10, 3.11
- **Streamlit Versions:** 1.22+ (limited list)
- **Dependency File:** `environment.yml`
- **Package Source:** Snowflake Anaconda Channel
- **Caching:** Per-session only
- **Entrypoint Location:** Root only
- **`get_active_session()`:** Supported
- **`st.connection("snowflake")`:** Supported

## Container Runtime Setup (Default)

### Step 1: Create External Access Integration for PyPI

**Required for installing packages from PyPI.** Even to specify Streamlit version, you need EAI.

```sql
-- 1. Create network rule for PyPI domains
CREATE OR REPLACE NETWORK RULE pypi_network_rule
  MODE = EGRESS
  TYPE = HOST_PORT
  VALUE_LIST = (
    'pypi.org',
    'pypi.python.org',
    'pythonhosted.org',
    'files.pythonhosted.org'
  );

-- 2. Create external access integration
CREATE OR REPLACE EXTERNAL ACCESS INTEGRATION pypi_access_integration
  ALLOWED_NETWORK_RULES = (pypi_network_rule)
  ENABLED = TRUE;

-- 3. Grant usage to app developer role
GRANT USAGE ON EXTERNAL ACCESS INTEGRATION pypi_access_integration
  TO ROLE app_developer_role;
```

### Step 2: Create Compute Pool

```sql
-- Create compute pool for Streamlit apps
-- MIN_NODES = number of apps you want running simultaneously
-- MAX_NODES = maximum apps during peak usage
CREATE COMPUTE POOL streamlit_compute_pool
  MIN_NODES = 1
  MAX_NODES = 5
  INSTANCE_FAMILY = CPU_X64_XS;

-- Grant usage to app developer role
GRANT USAGE ON COMPUTE POOL streamlit_compute_pool
  TO ROLE app_developer_role;
```

**Instance Family Guidelines:**
- `CPU_X64_XS`: Basic apps, low memory requirements (default)
- `CPU_X64_S`: Moderate memory needs
- `CPU_X64_M`: Large DataFrames, complex visualizations
- Note: Streamlit runs single-threaded; multiple CPUs won't help

### Step 3: Create Dependency File (pyproject.toml)

**Recommended format for Container Runtime:**

```toml
# pyproject.toml
[project]
requires-python = ">=3.11"
dependencies = [
    "streamlit>=1.50",
    "pandas>=2.0",
    "plotly>=5.18",
    "snowflake-snowpark-python>=1.11",
]
```

**Alternative: requirements.txt**

```text
# requirements.txt
streamlit>=1.50
pandas>=2.0
plotly>=5.18
snowflake-snowpark-python>=1.11
```

### Step 4: Project Structure

```
- `source_directory/`
  - `.streamlit/`
    - `config.toml` — Theme and configuration
  - `pyproject.toml` — Dependencies (recommended)
  - `streamlit_app.py` — Entrypoint
  - `pages/`
    - `dashboard.py`
    - `settings.py`
  - `utils/`
    - `helpers.py`
```

### Step 5: Upload to Stage and Create Streamlit

```sql
-- Upload files to stage (use Snowflake CLI or PUT)
-- snow stage copy ./app @my_db.my_schema.my_stage/streamlit_app --recursive

-- Create Streamlit with Container Runtime
CREATE STREAMLIT my_db.my_schema.my_app
  FROM '@my_db.my_schema.my_stage/streamlit_app'
  MAIN_FILE = 'streamlit_app.py'
  RUNTIME_NAME = 'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'
  COMPUTE_POOL = streamlit_compute_pool
  QUERY_WAREHOUSE = my_warehouse
  EXTERNAL_ACCESS_INTEGRATIONS = (pypi_access_integration);
```

**Key Parameters:**
- `RUNTIME_NAME`: Must be `'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'` for Container Runtime
- `COMPUTE_POOL`: Required for Container Runtime
- `QUERY_WAREHOUSE`: Warehouse for executing SQL queries within the app
- `EXTERNAL_ACCESS_INTEGRATIONS`: Required for PyPI package installation

### Pre-Deployment Validation

Run these checks before deploying:

```bash
# Verify Snowflake CLI connection
snow connection test

# Validate Streamlit project structure
snow streamlit validate

# Verify stage files uploaded correctly
snow stage list-files @my_db.my_schema.my_stage/streamlit_app
```

## Warehouse Runtime Setup (Alternative)

### Step 1: Create Dependency File (environment.yml)

```yaml
# environment.yml
name: my_streamlit_app
channels:
  - snowflake
dependencies:
  - streamlit=1.51.0
  - pandas
  - plotly
```

**Important:**
- Only `snowflake` channel allowed
- Do NOT include `python=X.Y` (managed by Snowflake)
- Pin Streamlit version to avoid defaulting to older bundled version

### Step 2: Project Structure

```
- `source_directory/`
  - `.streamlit/`
    - `config.toml` — Limited config options
  - `environment.yml` — Conda dependencies
  - `streamlit_app.py` — Entrypoint (MUST be in root)
  - `pages/`
    - `dashboard.py`
    - `settings.py`
```

**Constraint:** Entrypoint file MUST be in the root of source directory.

### Step 3: Upload to Stage

**CRITICAL: Disable auto-compression for .py and .yml files.**

```bash
# Using Snowflake CLI - MUST use --no-auto-compress
snow stage copy ./app @my_db.my_schema.my_stage/streamlit_app \
  --recursive --no-auto-compress --overwrite
```

```sql
-- Using SQL PUT - MUST use AUTO_COMPRESS=FALSE
PUT file://streamlit_app.py @my_stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://environment.yml @my_stage AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
```

**Why:** Without disabling compression, Snowflake compresses files to `.py.gz`, causing `TypeError: bad argument type for built-in operation`.

### Step 4: Create Streamlit

```sql
-- Create Streamlit with Warehouse Runtime (no RUNTIME_NAME)
CREATE STREAMLIT my_db.my_schema.my_app
  FROM '@my_db.my_schema.my_stage/streamlit_app'
  MAIN_FILE = 'streamlit_app.py'
  QUERY_WAREHOUSE = my_warehouse;
```

**Key Difference:** No `RUNTIME_NAME`, `COMPUTE_POOL`, or `EXTERNAL_ACCESS_INTEGRATIONS`.

## Migration: Warehouse to Container Runtime

### Step 1: Convert Dependencies

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

### Step 2: Update Connection Handling

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

### Step 3: Update Secrets Access

See `101c-snowflake-streamlit-security.md` for detailed secrets migration patterns.

**Summary:**
- Container Runtime: Use SQL functions to retrieve secrets
- Warehouse Runtime: Can use `_snowflake` module directly

### Step 4: Set Up Infrastructure

1. Create External Access Integration (see above)
2. Create Compute Pool (see above)
3. Grant necessary permissions

### Step 5: Recreate Streamlit Object

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

### Migration Checklist

- [ ] Convert `environment.yml` to `pyproject.toml`
- [ ] Update package names (conda to PyPI)
- [ ] Replace `get_active_session()` with `st.connection("snowflake")`
- [ ] Update secrets access pattern (if using `_snowflake` module)
- [ ] Create External Access Integration
- [ ] Create Compute Pool
- [ ] Recreate Streamlit object with new parameters
- [ ] Test all functionality in new runtime

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Missing EAI for Container Runtime

**Problem:**
```sql
CREATE STREAMLIT my_app
  FROM '@my_stage/app'
  MAIN_FILE = 'streamlit_app.py'
  RUNTIME_NAME = 'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'
  COMPUTE_POOL = my_pool
  QUERY_WAREHOUSE = my_wh;
  -- Missing EXTERNAL_ACCESS_INTEGRATIONS!
```

**Why It Fails:** Without EAI, the app cannot install packages from PyPI. Even pinning Streamlit version in `pyproject.toml` requires PyPI access.

**Correct Pattern:**
```sql
CREATE STREAMLIT my_app
  FROM '@my_stage/app'
  MAIN_FILE = 'streamlit_app.py'
  RUNTIME_NAME = 'SYSTEM$ST_CONTAINER_RUNTIME_PY3_11'
  COMPUTE_POOL = my_pool
  QUERY_WAREHOUSE = my_wh
  EXTERNAL_ACCESS_INTEGRATIONS = (pypi_access_integration);
```

### Anti-Pattern 2: Using get_active_session() in Container Runtime

**Problem:**
```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()  # Fails in Container Runtime!
```

**Why It Fails:** `get_active_session()` is not thread-safe and only works in Warehouse Runtime.

**Correct Pattern:**
```python
import streamlit as st
conn = st.connection("snowflake")
session = conn.session()  # Works in both runtimes
```

### Anti-Pattern 3: Wrong Dependency File for Runtime

**Problem:**
```yaml
# Using environment.yml with Container Runtime - WRONG!
name: my_app
channels:
  - snowflake
dependencies:
  - streamlit
```

**Why It Fails:** Container Runtime uses `uv` (pip-based), not conda. It ignores `environment.yml`.

**Correct Pattern for Container Runtime:**
```toml
# pyproject.toml
[project]
dependencies = ["streamlit>=1.50"]
```

### Anti-Pattern 4: Compressed File Upload for Warehouse Runtime

**Problem:**
```bash
snow stage copy ./app @my_stage --recursive
# Missing --no-auto-compress!
```

**Why It Fails:** Snowflake compresses `.py` files to `.py.gz`, causing import failures with `TypeError: bad argument type for built-in operation`.

**Correct Pattern:**
```bash
snow stage copy ./app @my_stage --recursive --no-auto-compress --overwrite
```

## Compute Pool Troubleshooting

**Pool stuck in `STARTING` or `IDLE`:**
```sql
-- Check compute pool status
DESCRIBE COMPUTE POOL streamlit_compute_pool;
-- If stuck, try suspending and resuming
ALTER COMPUTE POOL streamlit_compute_pool SUSPEND;
ALTER COMPUTE POOL streamlit_compute_pool RESUME;
```

**App fails with "no available nodes":** Increase `MAX_NODES` or wait for capacity:
```sql
ALTER COMPUTE POOL streamlit_compute_pool SET MAX_NODES = 10;
```

**Permission denied on compute pool:** Ensure the role has USAGE granted:
```sql
GRANT USAGE ON COMPUTE POOL streamlit_compute_pool TO ROLE app_developer_role;
```

**Instance family too small:** If the app crashes with OOM errors, upgrade the instance family:
```sql
ALTER COMPUTE POOL streamlit_compute_pool SET INSTANCE_FAMILY = CPU_X64_S;
```
