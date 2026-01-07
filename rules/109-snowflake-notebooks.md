# Snowflake Notebook Directives

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** ML, reproducible notebooks, nbqa, notebook linting, code quality, Python, create notebook, debug notebook, notebook execution, notebook testing, notebook deployment, kernel management, cell execution
**TokenBudget:** ~4150
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

`edit_notebook`, `read_file`, `run_terminal_cmd` (for notebook execution), `codebase_search`, `write` (for .py/.sql refactoring)

### Forbidden

Direct database credential exposure; notebook execution without environment validation

### Execution Steps

1. Validate environment and dependencies
2. Implement descriptive cell naming conventions
3. Structure notebook with proper Markdown documentation
4. Push computation to Snowflake via Snowpark
5. Refactor production code to separate files

### Output Format

Jupyter notebook (.ipynb) with named cells, Markdown documentation, and optional refactored .py/.sql files

### Validation

Verify cell names follow naming conventions; validate deterministic execution; confirm no hardcoded secrets; test Snowpark connectivity

### Design Principles

- Deterministic notebooks; one environment with pinned versions; imports centralized at top.
- Parameterize runs; narrative in Markdown cells; keep code cells focused and avoid hidden state.
- Never hard-code secrets; push heavy compute to Snowflake (Snowpark); refactor final code into .py/.sql.

### Post-Execution Checklist

- [ ] All imports in single top cell
- [ ] Cell names are descriptive (`action_subject` format)
- [ ] Markdown cells for narrative/documentation
- [ ] Secrets from environment variables (not hardcoded)
- [ ] Snowpark DataFrames for large computations
- [ ] Run `uvx nbqa ruff notebooks/` for linting
- [ ] Test: "Restart Kernel & Run All" works without errors

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

## Post-Execution Checklist
- [ ] All cells have descriptive, user-friendly names (not cell1, cell2, etc.)
      Verify: Open notebook in Snowsight > Projects > Notebooks > [notebook name] > Check left sidebar cell names should follow action_subject format
- [ ] Cell naming follows action_subject pattern with underscores (lowercase)
      Verify: Review cell names in notebook left panel. Should be "load_customer_data", not "LoadCustomerData" or "Load Customer Data"
- [ ] Environment and dependencies properly configured and pinned with exact versions
      Verify: Check packages section in notebook settings. Versions should be pinned with == (e.g., pandas==2.0.0, not pandas>=2.0)
- [ ] **CRITICAL:** `uvx nbqa ruff notebooks/` passes with zero errors
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
    col("REGISTRATION_DATE")
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

## Data & Performance
- **Requirement:** Never hard-code credentials or sensitive information. Use environment variables or a secrets manager.
- **Always:** Follow the rules in `100-snowflake-core.md` for performant, cost-effective queries.
- **Requirement:** For large datasets, push computation to Snowflake via Snowpark DataFrames; avoid large local pulls.
- **Requirement:** Refactor production-ready code out of the notebook into `.py` or `.sql` files; notebooks serve as reports or exploratory tools.

## Code Quality & Linting

### Purpose
Jupyter notebooks should maintain the same code quality standards as Python modules. Use **nbqa** (Notebook Quality Assurance) to run standard Python linters on notebook code cells.

### Tool: nbqa + Ruff (Industry Standard)

**Rationale:** nbqa is the industry-standard tool (>1.5M downloads/month) for applying Python linters to notebooks. It extracts code cells, runs linters, and maps results back to the original notebook with correct line numbers.

#### Installation and Usage

```bash
# Check notebooks with Ruff linter (no installation required)
uvx nbqa ruff notebooks/

# Format notebooks with Ruff
uvx nbqa ruff format notebooks/

# Auto-fix linting issues
uvx nbqa ruff check --fix notebooks/

# Check specific notebook
uvx nbqa ruff notebooks/grid_asset_prediction.ipynb
```

#### Integration with Taskfile

Add notebook linting tasks to project `Taskfile.yml`:

```yaml
lint-notebooks:
  desc: "Lint Jupyter notebooks with Ruff via nbqa"
  cmds:
    - uvx nbqa ruff notebooks/

format-notebooks:
  desc: "Format Jupyter notebooks with Ruff via nbqa"
  cmds:
    - uvx nbqa ruff format notebooks/

format-notebooks-fix:
  desc: "Format Jupyter notebooks with Ruff and apply fixes"
  cmds:
    - uvx nbqa ruff format notebooks/
    - uvx nbqa ruff check --fix notebooks/

lint:
  desc: "Run all linting checks"
  cmds:
    - task: lint-ruff
    - task: lint-markdown
    - task: lint-notebooks
```

#### Pre-Task-Completion Validation

**CRITICAL:** Notebook linting is part of the Pre-Task-Completion Validation Gate.

- **Requirement:** Run `uvx nbqa ruff notebooks/` after modifying notebook files
- **Requirement:** Run `uvx nbqa ruff format --check notebooks/` to verify formatting
- **Rule:** Fix all notebook linting errors before marking task complete
- **Exception:** Only skip validation if user explicitly requests override

#### How nbqa Works

1. **Extract**: nbqa extracts Python code from notebook cells
2. **Lint**: Runs your chosen linter (Ruff) on the extracted code
3. **Map**: Maps linting results back to notebook cells with correct line numbers
4. **Non-Destructive**: Only modifies code cells; preserves outputs, metadata, and cell structure

#### Common Notebook Linting Issues

1. **Unused imports**: Import statements in setup cells not used in later cells
   - Fix: Remove unused imports or consolidate into single import cell

2. **Line length**: Code lines exceeding character limits
   - Fix: Break long lines, especially for Snowpark DataFrame operations

3. **Undefined variables**: Variables used before definition due to out-of-order execution
   - Fix: Ensure deterministic execution order (top to bottom)

4. **Import order**: Inconsistent import organization
   - Fix: Use Ruff to auto-sort imports with `uvx nbqa ruff check --fix`

5. **Missing docstrings**: Functions defined in notebooks without documentation
   - Fix: Add docstrings to function cells following `204-python-docs-comments.md`

### Ruff Configuration for Notebooks

Use the same `pyproject.toml` configuration as your Python modules. nbqa will automatically use project Ruff settings.

**Example** `pyproject.toml`:
```toml
[tool.ruff]
target-version = "py311"
line-length = 100  # Slightly longer for notebook readability

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["E501"]  # Allow long lines in notebooks for complex expressions

# Notebook-specific: Allow unused variables in exploratory cells
[tool.ruff.lint.per-file-ignores]
"notebooks/*.ipynb" = ["F841"]  # Unused variable assignment
```

### Alternative Tools

- **jupytext**: Convert notebooks to `.py` files, lint those, convert back (more complex workflow)
- **nbQA with other linters**: Use `uvx nbqa black`, `uvx nbqa isort`, etc. (less consistent with Ruff-first approach)

### Benefits of nbqa + Ruff

- Consistent code quality standards across `.py` modules and `.ipynb` notebooks
- Catches common errors before notebook execution
- Enforces import organization and formatting standards
- CI/CD ready for automated quality checks
- Integrates with existing `uv` + `ruff` tooling ecosystem

### When to Skip nbqa Linting

**Valid Exceptions:**

**1. Exploratory notebooks** (temporary analysis, not production-bound)
- **Rationale:** Linting adds overhead without value for throwaway code intended for one-time analysis
- **Example:** Ad-hoc data exploration, one-time customer requests, rapid prototyping sessions
- **Action:** Skip linting entirely, but add "EXPLORATORY" tag to notebook filename or header cell

**2. Tutorial notebooks with intentional anti-patterns**
- **Rationale:** May demonstrate "wrong" code for teaching purposes before showing corrections
- **Example:** Teaching notebooks showing common mistakes (using `SELECT *`, missing error handling) before demonstrating best practices
- **Action:** Use `# ruff: noqa` comments with explanatory notes documenting why violations are intentional

**3. Notebooks with external dependencies unavailable in linting environment**
- **Rationale:** Import errors block linting of otherwise valid code when proprietary or environment-specific libraries required
- **Example:** Notebooks requiring proprietary company libraries, hardware-specific modules, or specialized Snowflake functions not in local environment
- **Action:** Use `# type: ignore` for problematic imports or exclude file pattern in `pyproject.toml` per-file-ignores

**4. Notebooks using Snowflake-specific magic commands or SQL cells**
- **Rationale:** nbqa may not recognize Snowflake SQL cell syntax or custom magic commands
- **Example:** `%%sql` cell magic for inline SQL, `!snow` command cells, Snowflake worksheet-style cells
- **Action:** Configure Ruff to ignore specific cell patterns or use `# noqa` for magic command cells

**Override Pattern Example:**
```python
# Cell: exploratory_analysis_prototype
# ruff: noqa - Temporary code for exploration, not production-ready
# Will be deleted after analysis complete
large_df = session.table("MASSIVE_TABLE").to_pandas()  # F841: Unused, keeping for manual inspection
result = large_df.describe()  # Quick stats for investigation
```

**When in Doubt:** Default to linting. Exceptions should be rare (<10% of notebooks) and explicitly documented with rationale.
