**Description:** Rules for building reproducible, secure, and maintainable Jupyter Notebooks in the Snowflake environment.
**AppliesTo:** `**/*.ipynb`, `notebooks/**/*.py`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

**TokenBudget:** ~300
**ContextTier:** Medium

# Snowflake Notebook Directives

## Purpose
Establish best practices for building reproducible, secure, and maintainable Jupyter Notebooks within the Snowflake environment, ensuring deterministic execution, proper state management, and seamless transition to production code.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Jupyter Notebooks in Snowflake with Snowpark for Python and reproducible data science workflows


## Key Principles
- Deterministic notebooks; one environment with pinned versions; imports centralized at top.
- Parameterize runs; narrative in Markdown cells; keep code cells focused and avoid hidden state.
- Never hard-code secrets; push heavy compute to Snowflake (Snowpark); refactor final code into .py/.sql.

## 1. Reproducibility & State
- **Requirement:** Ensure notebooks are deterministic; outputs must not depend on execution order or hidden state.
- **Requirement:** Use a single virtual environment and pin versions for consistent dependencies.
- **Always:** Use a dedicated top cell for all imports.
- **Always:** Parameterize for environments (dev/prod) or inputs (e.g., with `papermill`).

## 2. Structure & Documentation
- **Always:** Use Markdown cells for narrative: purpose, business logic, assumptions.
- **Requirement:** Do not use code cells for documentation or static text.
- **Always:** Keep code cells focused on a single task; avoid mixing ingestion, transformation, and visualization.

## 3. Cell Naming & Organization
- **Requirement:** Use descriptive, user-friendly cell names that reflect the cell's purpose, not generic names like `cell1`, `cell2`.
- **Always:** Name cells with clear, action-oriented descriptions (e.g., `setup_snowpark_session`, `load_customer_data`, `calculate_monthly_metrics`).
- **Requirement:** Use consistent naming patterns: `action_subject` format with lowercase and underscores.
- **Always:** Group related cells with consistent prefixes (e.g., `data_ingestion_customers`, `data_ingestion_orders`).
- **Requirement:** For parameterized notebooks, use descriptive parameter cell names (e.g., `config_environment_settings`, `params_date_range`).

## 4. Data & Performance
- **Requirement:** Never hard-code credentials or sensitive information. Use environment variables or a secrets manager.
- **Always:** Follow the rules in `100-snowflake-core.md` for performant, cost-effective queries.
- **Requirement:** For large datasets, push computation to Snowflake via Snowpark DataFrames; avoid large local pulls.
- **Requirement:** Refactor production-ready code out of the notebook into `.py` or `.sql` files; notebooks serve as reports or exploratory tools.

## Contract
- **Inputs/Prereqs:** Snowflake account access; Snowpark for Python environment; Jupyter notebook environment; virtual environment with pinned dependencies
- **Allowed Tools:** `edit_notebook`, `read_file`, `run_terminal_cmd` (for notebook execution), `codebase_search`, `write` (for .py/.sql refactoring)
- **Forbidden Tools:** Direct database credential exposure; notebook execution without environment validation
- **Required Steps:** 
  1. Validate environment and dependencies
  2. Implement descriptive cell naming conventions
  3. Structure notebook with proper Markdown documentation
  4. Push computation to Snowflake via Snowpark
  5. Refactor production code to separate files
- **Output Format:** Jupyter notebook (.ipynb) with named cells, Markdown documentation, and optional refactored .py/.sql files
- **Validation Steps:** Verify cell names follow naming conventions; validate deterministic execution; confirm no hardcoded secrets; test Snowpark connectivity

## Quick Compliance Checklist
- [ ] All cells have descriptive, user-friendly names (not cell1, cell2, etc.)
- [ ] Cell naming follows action_subject pattern with underscores
- [ ] Environment and dependencies properly configured and pinned
- [ ] No hardcoded credentials or sensitive information present
- [ ] Computation pushed to Snowflake via Snowpark DataFrames
- [ ] Markdown cells provide clear narrative and documentation
- [ ] Notebook executes deterministically without hidden state
- [ ] Production code refactored to separate .py/.sql files when appropriate

## Validation
- **Success checks:** Cell names are descriptive and follow naming conventions; notebook runs deterministically from top to bottom; all Snowpark connections work; no secrets exposed; production logic extracted to .py/.sql files
- **Negative tests:** Generic cell names (cell1, cell2) should be flagged; notebooks with execution order dependencies should fail; hardcoded credentials should be detected; large local data pulls should be avoided

## Response Template
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

## References

### External Documentation
- [Snowpark for Python](https://docs.snowflake.com/en/developer-guide/snowpark/python) - DataFrames, functions, and distributed computing                                                                               
- [Python Connector](https://docs.snowflake.com/en/developer-guide/python-connector) - Database connectivity and authentication patterns

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Streamlit UI**: `101-snowflake-streamlit-ui.md`
- **Warehouse Management**: `119-snowflake-warehouse-management.md`
- **Python Core**: `200-python-core.md`
- **Data Science Analytics**: `500-data-science-analytics.md`
