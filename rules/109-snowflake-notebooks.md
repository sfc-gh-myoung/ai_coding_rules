# Snowflake Notebook Directives

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** ML, reproducible notebooks, nbqa, notebook linting, code quality, Python, create notebook, debug notebook, notebook execution, notebook testing, notebook deployment, kernel management, cell execution
**TokenBudget:** ~3200
**ContextTier:** Medium
**Depends:** rules/100-snowflake-core.md, rules/201-python-lint-format.md

## Purpose
Establish best practices for building reproducible, secure, and maintainable Jupyter Notebooks within the Snowflake environment, ensuring deterministic execution, proper state management, and seamless transition to production code.

## Rule Scope

Jupyter Notebooks in Snowflake with Snowpark for Python and reproducible data science workflows

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

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for 80% of common use cases reduces need to read full sections
- **Position advantage:** Early placement benefits from slight attention bias in LLM processing (first ~20% of content receives marginally more weight)
- **Progressive disclosure:** Enables agents to assess rule relevance before loading full content
- **Human-LLM collaboration:** Useful for both human developers (quick scanning) and AI assistants (decision point)

**Note:** While LLMs read sequentially (not auto-prioritizing this section), the concentrated pattern format and early position provide practical efficiency benefits. To maximize value for agents, include in system prompts: "Read Quick Start TL;DR sections first to identify essential patterns."

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Deterministic execution** - notebooks must run top-to-bottom without hidden state
- **All imports at top** - single dedicated cell for all imports
- **Descriptive cell names** - use `action_subject` format (e.g., `load_customer_data`)
- **Push compute to Snowflake** - use Snowpark DataFrames, avoid large local pulls
- **Use nbqa for linting** - `uvx nbqa ruff notebooks/` for code quality
- **Never hard-code secrets** - use environment variables or st.secrets
- **Don't rely on execution order** - cells must be independent and deterministic

**Quick Checklist:**
- [ ] All imports in single top cell
- [ ] Cell names are descriptive (`action_subject` format)
- [ ] Markdown cells for narrative/documentation
- [ ] Secrets from environment variables (not hardcoded)
- [ ] Snowpark DataFrames for large computations
- [ ] Run `uvx nbqa ruff notebooks/` for linting
- [ ] Test: "Restart Kernel & Run All" works without errors

> **Investigation Required**
> When applying this rule:
> 1. Run the notebook top-to-bottom BEFORE making recommendations
> 2. Verify cell execution order doesn't cause hidden state issues
> 3. Never speculate about notebook structure - read the actual .ipynb file
> 4. Check for hardcoded secrets or credentials in cells
> 5. Make grounded recommendations based on investigated notebook execution

## Contract

<contract>
<inputs_prereqs>
Snowflake account access; Snowpark for Python environment; Jupyter notebook environment; virtual environment with pinned dependencies
</inputs_prereqs>

<mandatory>
`edit_notebook`, `read_file`, `run_terminal_cmd` (for notebook execution), `codebase_search`, `write` (for .py/.sql refactoring)
</mandatory>

<forbidden>
Direct database credential exposure; notebook execution without environment validation
</forbidden>

<steps>
1. Validate environment and dependencies
2. Implement descriptive cell naming conventions
3. Structure notebook with proper Markdown documentation
4. Push computation to Snowflake via Snowpark
5. Refactor production code to separate files
</steps>

<output_format>
Jupyter notebook (.ipynb) with named cells, Markdown documentation, and optional refactored .py/.sql files
</output_format>

<validation>
Verify cell names follow naming conventions; validate deterministic execution; confirm no hardcoded secrets; test Snowpark connectivity
</validation>

<design_principles>
- Deterministic notebooks; one environment with pinned versions; imports centralized at top.
- Parameterize runs; narrative in Markdown cells; keep code cells focused and avoid hidden state.
- Never hard-code secrets; push heavy compute to Snowflake (Snowpark); refactor final code into .py/.sql.
</design_principles>

</contract>

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

## References

### External Documentation
- [Snowpark for Python](https://docs.snowflake.com/en/developer-guide/snowpark/python) - Official Snowflake documentation for DataFrames, distributed computing patterns, UDFs, and complete API reference (authoritative source, updated with each Snowflake release)
- [Python Connector](https://docs.snowflake.com/en/developer-guide/python-connector) - Official database connectivity guide covering authentication patterns, connection pooling, and session management (required reading for production deployments)
- [nbqa Documentation](https://nbqa.readthedocs.io/) - Comprehensive guide for running Python code quality tools on Jupyter notebooks (industry-standard linting approach with 1.5M+ monthly downloads)

### Related Rules
- **Snowflake Core**: `rules/100-snowflake-core.md`
- **App Deployment**: `rules/109b-snowflake-app-deployment-core.md`
- **Streamlit UI**: `rules/101-snowflake-streamlit-core.md`
- **Warehouse Management**: `rules/119-snowflake-warehouse-management.md`
- **Python Core**: `rules/200-python-core.md`
- **Python Linting**: `rules/201-python-lint-format.md`
- **Data Science Analytics**: `rules/920-data-science-analytics.md`

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

## 5. Code Quality & Linting

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

## Related Rules

**Closely Related** (consider loading together):
- `100-snowflake-core` - For Snowflake fundamentals, connection patterns, DDL syntax
- `111-snowflake-observability-core` - When adding telemetry and monitoring to notebook executions

**Sometimes Related** (load if specific scenario):
- `101-snowflake-streamlit-core` - When combining notebook development with Streamlit deployment
- `114-snowflake-cortex-aisql` - When using Cortex AI functions in notebook workflows
- `124-snowflake-data-quality-core` - When running data quality checks in notebooks

**Complementary** (different aspects of same domain):
- `103-snowflake-performance-tuning` - For optimizing queries in notebook cells
- `107-snowflake-security-governance` - For secrets management and RBAC in notebooks
