# Snowflake Notebook Directives

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:notebook, kw:jupyter
**Keywords:** ML, reproducible notebooks, nbqa, notebook linting, code quality, Python, create notebook, debug notebook, notebook execution, notebook testing, notebook deployment, kernel management, cell execution
**TokenBudget:** ~4450
**ContextTier:** Medium
**Depends:** 100-snowflake-core.md, 201-python-lint-format.md

## Scope

**What This Rule Covers:**
Best practices for building reproducible, secure, and maintainable Jupyter Notebooks within the Snowflake environment, ensuring deterministic execution, proper state management, and seamless transition to production code.

**When to Load This Rule:**
- Creating Jupyter Notebooks in Snowflake
- Building reproducible data science workflows
- Using Snowpark for Python in notebooks
- Managing notebook state and dependencies
- Transitioning notebooks to production code

**Progressive Disclosure - Token Budget:**
- Quick Start + Contract: ~400 tokens (always load for notebook tasks)
- + Core Patterns (sections 1-2): ~1000 tokens (load for development)
- + Advanced Features (sections 3-4): ~1700 tokens (load for production)
- + Complete Reference: ~2200 tokens (full notebook guide)

**Recommended Loading Strategy:**
- **Understanding notebooks**: Quick Start only
- **Creating notebooks**: + Core Patterns
- **Production workflows**: + Advanced Features
- **Deployment**: + 109c (app deployment)

## References

### External Documentation
- [Snowflake Notebooks](https://docs.snowflake.com/en/user-guide/ui-snowsight-notebooks-gs) - Official Notebooks documentation
- [Snowpark for Python](https://docs.snowflake.com/en/developer-guide/snowpark/python/index) - Snowpark Python API reference
- [nbqa](https://nbqa.readthedocs.io/) - Code quality tools for Jupyter notebooks
- [Jupyter Best Practices](https://jupyter-notebook.readthedocs.io/en/stable/notebook.html) - Notebook usage guidelines

### Related Rules
**Closely Related** (consider loading together):
- **100-snowflake-core.md** - Snowflake fundamentals, connection patterns, DDL syntax
- **111-snowflake-observability-core.md** - adding telemetry and monitoring to notebook executions

**Sometimes Related** (load if specific scenario):
- **101-snowflake-streamlit-core.md** - combining notebook development with Streamlit deployment
- **114-snowflake-cortex-aisql.md** - using Cortex AI functions in notebook workflows
- **124-snowflake-data-quality-core.md** - running data quality checks in notebooks

**Complementary** (different aspects of same domain):
- **103-snowflake-performance-tuning.md** - optimizing queries in notebook cells
- **107-snowflake-security-governance.md** - secrets management and RBAC in notebooks

## Contract

### Inputs and Prerequisites

Snowflake account access; Snowpark for Python environment; Jupyter notebook environment; virtual environment with pinned dependencies

### Mandatory

- All imports in a single top cell
- Descriptive cell names following `action_subject` format (lowercase, underscores)
- Markdown cells for narrative documentation between code sections
- Secrets from environment variables or secrets manager (never hardcoded)
- Snowpark DataFrames for large computations (minimize local `.to_pandas()` calls)
- Deterministic execution: "Restart Kernel & Run All" must succeed

### Forbidden

- Hardcoded credentials or connection strings in notebook cells
- Notebook execution without environment validation (pinned dependencies)
- Generic cell names (cell1, cell2, untitled)
- Code cells used for documentation or static text

### Conditional

- `uvx nbqa ruff notebooks/` linting required for production-bound notebooks (optional for exploratory)
- Production code extraction to `.py`/`.sql` files when notebook exceeds >=500 lines

### Execution Steps

1. Set up environment: configure warehouse, install packages via Packages panel
2. Validate dependencies: pin versions, verify Snowpark connectivity
3. Implement descriptive cell naming conventions (`action_subject` format)
4. Structure notebook with proper Markdown documentation between code sections
5. Centralize all imports in a single top cell
6. Push computation to Snowflake via Snowpark DataFrames
7. Test deterministic execution: "Restart Kernel & Run All" must succeed
8. Lint with `uvx nbqa ruff notebooks/` for production-bound notebooks
9. Refactor production code to separate `.py`/`.sql` files when notebook exceeds 500 lines

### Output Format

Jupyter notebook (.ipynb) with named cells, Markdown documentation, and optional refactored .py/.sql files

### Validation

Verify cell names follow naming conventions; validate deterministic execution; confirm no hardcoded secrets; test Snowpark connectivity

### Design Principles

- Deterministic notebooks; one environment with pinned versions; imports centralized at top.
- Parameterize runs; narrative in Markdown cells; keep code cells focused and avoid hidden state.
- Never hard-code secrets; push heavy compute to Snowflake (Snowpark); refactor final code into .py/.sql.

### Post-Execution Checklist

See the Post-Execution Checklist section below for comprehensive validation steps with specific verification commands.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Hidden State Dependencies Between Cells

**Problem:** Notebook cells that depend on variables or state created by out-of-order execution, causing "Restart Kernel & Run All" to fail.

**Why It Fails:** Notebooks executed interactively accumulate hidden state. When shared or deployed, they fail because cells assume variables exist from previous ad-hoc runs. This breaks reproducibility and makes debugging impossible.

**Correct Pattern:**
```python
# BAD: Cell 5 depends on variable from deleted Cell 3
# df_filtered was created interactively, then Cell 3 was deleted
result = df_filtered.groupby('region').sum()  # NameError on fresh run

# GOOD: Each cell is self-contained or explicitly chains
# Cell 1: Load data
df_raw = session.table('SALES').to_pandas()

# Cell 2: Filter (explicit dependency on Cell 1)
df_filtered = df_raw[df_raw['status'] == 'active']

# Cell 3: Aggregate (explicit dependency on Cell 2)
result = df_filtered.groupby('region').sum()
```

### Anti-Pattern 2: Hardcoded Credentials in Notebook Cells

**Problem:** Embedding database passwords, API keys, or connection strings directly in notebook code cells.

**Why It Fails:** Notebooks are often shared, committed to git, or exported. Credentials become exposed, creating security vulnerabilities. Rotating credentials requires editing every notebook.

**Correct Pattern:**
```python
# BAD: Credentials in code
connection = snowflake.connector.connect(
    user='admin',
    password='SuperSecret123!',  # Exposed in .ipynb JSON
    account='xy12345.us-east-1'
)

# GOOD: Credentials from environment
import os
connection = snowflake.connector.connect(
    user=os.environ['SNOWFLAKE_USER'],
    password=os.environ['SNOWFLAKE_PASSWORD'],
    account=os.environ['SNOWFLAKE_ACCOUNT']
)
# Or use Streamlit secrets: st.secrets["snowflake"]["password"]
```

### Anti-Pattern 3: Using pip install in Notebook Cells

**Problem:** Installing packages with `pip install` or `!pip install` in notebook cells instead of using the Snowflake Notebook Packages panel.

**Why It Fails:** `pip install` in cells is not persistent across kernel restarts in Snowflake Notebooks, creates inconsistent environments, and may conflict with pre-installed packages. The Packages panel ensures reproducible dependency management.

**Correct Pattern:**
```python
# BAD: pip install in cells
!pip install pandas==2.0.0
!pip install scikit-learn

# GOOD: Use the Packages panel in Snowflake Notebook settings
# Navigate to notebook settings > Packages > Add package with version pin
# Packages are managed at the notebook level and persist across sessions
```

### Anti-Pattern 4: Pulling Entire Tables Locally with .to_pandas()

**Problem:** Converting large Snowpark DataFrames to pandas DataFrames for processing that could be done in Snowflake.

**Why It Fails:** Transfers large datasets to the notebook's local compute, causing memory errors, slow performance, and unnecessary egress costs. Snowpark pushes computation to Snowflake's distributed engine.

**Correct Pattern:**
```python
# BAD: Pull entire table locally for filtering
df = session.table("LARGE_TABLE").to_pandas()  # 10M rows to local memory
result = df[df['status'] == 'active'].groupby('region').sum()

# GOOD: Filter and aggregate in Snowpark, then collect small result
result = (session.table("LARGE_TABLE")
    .filter(col("STATUS") == "active")
    .group_by("REGION")
    .agg(sum("AMOUNT").alias("TOTAL"))
    .to_pandas())  # Only collect the small aggregated result
```

## Post-Execution Checklist
- [ ] All cells have descriptive, user-friendly names (not cell1, cell2, etc.)
      Verify: Open notebook in Snowsight > Projects > Notebooks > [notebook name] > Check left sidebar cell names should follow action_subject format
- [ ] Cell naming follows action_subject pattern with underscores (lowercase)
      Verify: Review cell names in notebook left panel. Should be "load_customer_data", not "LoadCustomerData" or "Load Customer Data"
- [ ] Environment and dependencies properly configured and pinned with exact versions
      Verify: Check packages section in notebook settings. Versions should be pinned with == (e.g., pandas==2.0.0, not pandas>=2.0)
- [ ] **REQUIRED:** `uvx nbqa ruff notebooks/` passes with zero errors
      Verify: Run command in terminal. Must show "All checks passed!" or 0 errors, no E/W/F violations
- [ ] **CRITICAL:** `uvx nbqa ruff format --check notebooks/` passes
      Verify: Run command in terminal. Must show "n files would be left unchanged" or no formatting changes needed
- [ ] No hardcoded credentials or sensitive information present
      Verify: Search notebook for keywords: "password", "token", "secret", "key", "api_key". Should find zero matches outside of variable names
- [ ] Computation pushed to Snowflake via Snowpark DataFrames (minimize local data)
      Verify: Check for .to_pandas() calls. Should be minimal (<3 instances), used only for final results/visualization, not intermediate processing
- [ ] Markdown cells provide clear narrative and documentation for each section
      Verify: Read through notebook. Markdown should explain purpose of each section, why approaches chosen, business context
- [ ] Notebook executes deterministically without hidden state (top-to-bottom)
      Verify: Restart kernel and run all cells sequentially. Should execute in order without NameError or undefined variables
- [ ] Production code refactored to separate .py/.sql files when appropriate
      Verify: Check if notebook has >500 lines of code OR reusable functions. Consider extracting to modules in src/ directory

## Validation
- **Success checks:** Cell names are descriptive and follow naming conventions; `uvx nbqa ruff notebooks/` passes with zero errors; `uvx nbqa ruff format --check notebooks/` passes; notebook runs deterministically from top to bottom; all Snowpark connections work; no secrets exposed; production logic extracted to .py/.sql files
- **Negative tests:** Generic cell names (cell1, cell2) should be flagged; notebooks with linting errors fail validation; notebooks with execution order dependencies should fail; hardcoded credentials should be detected; large local data pulls should be avoided

## Output Format Examples
```python
# Cell: setup_environment_and_imports
import snowflake.snowpark as snowpark
from snowflake.snowpark.functions import col, sum, avg
import os

# Cell: config_snowflake_connection
connection_params = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "warehouse": "COMPUTE_WH",
    "database": "ANALYTICS_DB",
    "schema": "PUBLIC"
}

# Cell: create_snowpark_session
session = snowpark.Session.builder.configs(connection_params).create()

# Cell: load_customer_data
customers_df = session.table("CUSTOMERS").select(
    col("CUSTOMER_ID"),
    col("CUSTOMER_NAME"),
    col("REGISTRATION_DATE"),
    month(col("REGISTRATION_DATE")).alias("REGISTRATION_MONTH")
)

# Cell: calculate_monthly_metrics
monthly_summary = customers_df.group_by("REGISTRATION_MONTH").agg(
    sum("TOTAL_ORDERS").alias("MONTHLY_ORDERS"),
    avg("ORDER_VALUE").alias("AVG_ORDER_VALUE")
)
```

## Reproducibility & State
- **Requirement:** Ensure notebooks are deterministic; outputs must not depend on execution order or hidden state.
- **Requirement:** Use a single virtual environment and pin versions for consistent dependencies.
- **Always:** Use a dedicated top cell for all imports.
- **Always:** Parameterize for environments (dev/prod) or inputs (e.g., with `papermill`).

## Structure & Documentation
- **Always:** Use Markdown cells for narrative: purpose, business logic, assumptions.
- **Requirement:** Do not use code cells for documentation or static text.
- **Always:** Keep code cells focused on a single task; avoid mixing ingestion, transformation, and visualization.

## Cell Naming & Organization
- **Requirement:** Use descriptive, user-friendly cell names that reflect the cell's purpose, not generic names like `cell1`, `cell2`.
- **Always:** Name cells with clear, action-oriented descriptions (e.g., `setup_snowpark_session`, `load_customer_data`, `calculate_monthly_metrics`).
- **Requirement:** Use consistent naming patterns: `action_subject` format with lowercase and underscores.
- **Always:** Group related cells with consistent prefixes (e.g., `data_ingestion_customers`, `data_ingestion_orders`).
- **Requirement:** For parameterized notebooks, use descriptive parameter cell names (e.g., `config_environment_settings`, `params_date_range`).

### Cell Metadata Validation

**Inline Validation (run directly):**
```bash
python3 -c "
import json, re, sys
nb_path = 'notebooks/your_notebook.ipynb'  # Update path
with open(nb_path) as f:
    nb = json.load(f)
issues = []
for i, cell in enumerate(nb['cells']):
    name = cell.get('metadata', {}).get('name')
    if not name:
        issues.append(f'Cell {i}: Missing name in metadata')
    elif re.match(r'^(cell|Cell|untitled|Untitled)\d*$', name):
        issues.append(f'Cell {i}: Generic name \"{name}\" - use descriptive action_subject format')
    elif not re.match(r'^[a-z][a-z0-9_]*$', name):
        issues.append(f'Cell {i}: Name \"{name}\" should be lowercase with underscores')
if issues:
    print('\n'.join(issues))
    sys.exit(1)
print(f'All {len(nb[\"cells\"])} cells have valid names')
"
```

**Fix cells with missing/generic names:**
```bash
python3 -c "
import json
nb_path = 'notebooks/your_notebook.ipynb'  # Update path
with open(nb_path) as f:
    nb = json.load(f)
# Define fixes: {cell_index: 'new_name'}
fixes = {
    0: 'intro_header',
    1: 'setup_imports',
    # Add more as needed
}
for idx, new_name in fixes.items():
    if 'metadata' not in nb['cells'][idx]:
        nb['cells'][idx]['metadata'] = {}
    nb['cells'][idx]['metadata']['name'] = new_name
    print(f'Cell {idx}: Set name to \"{new_name}\"')
with open(nb_path, 'w') as f:
    json.dump(nb, f, indent=1)
print('Done')
"
```

**What validation checks:**
1. All cells have a `name` field in metadata
2. Names are not generic (cell1, cell2, untitled, etc.)
3. Names follow `action_subject` format (lowercase with underscores)

**Creating New Cells with Proper Metadata:**
When adding cells programmatically or copying from other notebooks, ensure metadata includes the name field:
```json
{
  "cell_type": "code",
  "metadata": {
    "name": "load_customer_data"
  },
  "source": ["# Your code here"]
}
```

**Common Naming Prefixes:**
- `setup_` - Environment/config cells (e.g., `setup_imports`, `setup_session`)
- `config_` - Configuration parameters (e.g., `config_demo_scenario`, `config_warehouse`)
- `load_` - Data loading cells (e.g., `load_customer_data`, `load_features`)
- `validate_` - Validation/quality checks (e.g., `validate_data_quality`, `validate_schema`)
- `train_` - Model training cells (e.g., `train_random_forest`, `train_xgboost`)
- `step_header_` - Step description markdown (e.g., `step_header_data_prep`)
- `teaching_` - Educational content (e.g., `teaching_class_imbalance`)
- `checkpoint_` - Validation checkpoints (e.g., `checkpoint_data_prep_validation`)

## Data & Performance
- **Requirement:** Never hard-code credentials or sensitive information. Use environment variables or a secrets manager.
- **Always:** Follow the rules in `100-snowflake-core.md` for performant, cost-effective queries.
- **Requirement:** For large datasets, push computation to Snowflake via Snowpark DataFrames; avoid large local pulls.
- **Requirement:** Refactor production-ready code out of the notebook into `.py` or `.sql` files; notebooks serve as reports or exploratory tools.

## Notebook Scheduling

For automated notebook execution, convert notebooks to Snowflake Tasks. See `104-snowflake-streams-tasks.md` for task scheduling patterns.

```sql
-- Schedule notebook execution via Snowflake Task
CREATE OR REPLACE TASK run_daily_notebook
  WAREHOUSE = COMPUTE_WH
  SCHEDULE = 'USING CRON 0 6 * * * America/Los_Angeles'
  COMMENT = 'Daily execution of analytics notebook'
AS
  EXECUTE NOTEBOOK "DB"."SCHEMA"."MY_NOTEBOOK"();
```

## Snowflake Notebooks UI Patterns

### Snowsight Notebook Features
- **Cell types:** Python, SQL, and Markdown cells are all supported natively
- **SQL cell results:** SQL cells return results as DataFrames accessible in subsequent Python cells via `cell_name.to_pandas()`
- **Active warehouse:** Set via notebook settings or `USE WAREHOUSE` in a SQL cell
- **Packages:** Add Python packages via the Packages panel (not `pip install` in cells)
- **Session context:** Each notebook has its own Snowpark session accessible via `get_active_session()`

### Session and Kernel Management
- **`get_active_session()`**: Use this instead of creating manual connections in Snowflake Notebooks
- **Kernel restart:** Clears all variables; use "Restart & Run All" for reproducibility testing
- **Idle timeout:** Snowflake Notebooks have a configurable idle timeout; save work frequently
- **Warehouse selection:** Choose appropriate warehouse size in notebook settings before running compute-heavy cells
- **Cell execution order:** Cells execute in the kernel's order, not visual order; always use sequential top-to-bottom execution

```python
# Snowflake Notebook session pattern
from snowflake.snowpark.context import get_active_session
session = get_active_session()

# Use session for all Snowpark operations
df = session.table("DB.SCHEMA.TABLE")
```

## Code Quality & Linting

> For notebook linting with nbqa, Ruff, Taskfile integration, Ruff configuration, common linting issues, and when to skip linting, see **109d-snowflake-notebooks-linting.md**.

**Quick Reference:**
```bash
# Check notebooks with Ruff linter
uvx nbqa ruff notebooks/

# Format notebooks with Ruff
uvx nbqa ruff format notebooks/

# Auto-fix linting issues
uvx nbqa ruff check --fix notebooks/
```
