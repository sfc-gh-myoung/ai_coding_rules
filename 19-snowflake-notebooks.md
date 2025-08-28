**Description:** Rules for building reproducible, secure, and maintainable Jupyter Notebooks in the Snowflake environment.
**Applies to:** `**/*.ipynb`, `notebooks/**/*.py`
**Auto-attach:** false

# Snowflake Notebook Directives

## TL;DR
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

## 3. Data & Performance
- **Requirement:** Never hard-code credentials or sensitive information. Use environment variables or a secrets manager.
- **Always:** Follow the rules in `10-snowflake-core.md` for performant, cost-effective queries.
- **Requirement:** For large datasets, push computation to Snowflake via Snowpark DataFrames; avoid large local pulls.
- **Requirement:** Refactor production-ready code out of the notebook into `.py` or `.sql` files; notebooks serve as reports or exploratory tools.

## 4. Documentation
- **Always:** Reference the official documentation:
  - **Snowpark for Python**: https://docs.snowflake.com/en/developer-guide/snowpark/python
  - **Snowflake Python Connector**: https://docs.snowflake.com/en/developer-guide/python-connector