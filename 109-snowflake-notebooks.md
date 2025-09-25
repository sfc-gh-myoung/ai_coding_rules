**Description:** Rules for building reproducible, secure, and maintainable Jupyter Notebooks in the Snowflake environment.
**AppliesTo:** `**/*.ipynb`, `notebooks/**/*.py`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.1
**LastUpdated:** 2025-09-16

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

## 3. Data & Performance
- **Requirement:** Never hard-code credentials or sensitive information. Use environment variables or a secrets manager.
- **Always:** Follow the rules in `100-snowflake-core.md` for performant, cost-effective queries.
- **Requirement:** For large datasets, push computation to Snowflake via Snowpark DataFrames; avoid large local pulls.
- **Requirement:** Refactor production-ready code out of the notebook into `.py` or `.sql` files; notebooks serve as reports or exploratory tools.

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Snowpark for Python](https://docs.snowflake.com/en/developer-guide/snowpark/python) - DataFrames, functions, and distributed computing                                                                               
- [Python Connector](https://docs.snowflake.com/en/developer-guide/python-connector) - Database connectivity and authentication patterns

### Related Rules
- **Snowflake Core**: `100-snowflake-core.md`
- **Streamlit UI**: `101-snowflake-streamlit-ui.md`
- **Python Core**: `200-python-core.md`
- **Data Science Analytics**: `500-data-science-analytics.md`
