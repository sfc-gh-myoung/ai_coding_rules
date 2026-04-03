# Snowflake Notebook Code Quality and Linting

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.3
**LastUpdated:** 2026-03-26
**LoadTrigger:** kw:nbqa, kw:notebook-linting
**Keywords:** nbqa, ruff, notebook linting, code quality, Jupyter, notebook formatting, lint notebooks, notebook validation
**TokenBudget:** ~3500
**ContextTier:** Low
**Depends:** 109-snowflake-notebooks.md, 201-python-lint-format.md

## Scope

**What This Rule Covers:**
Code quality tooling and linting configuration for Jupyter Notebooks using nbqa and Ruff, including automation integration, common linting issues, Ruff configuration, and when to skip linting.

**When to Load This Rule:**
- Setting up notebook linting in a project
- Configuring nbqa with Ruff for notebooks
- Integrating notebook linting into CI/CD or project automation (Makefile, Taskfile, or equivalent)
- Troubleshooting notebook linting issues
- Deciding when to skip linting for specific notebooks

## References

### External Documentation
- [nbqa](https://nbqa.readthedocs.io/) - Code quality tools for Jupyter notebooks
- [Ruff](https://docs.astral.sh/ruff/) - Fast Python linter and formatter

### Related Rules
**Closely Related** (consider loading together):
- **109-snowflake-notebooks.md** - Parent rule for notebook best practices
- **201-python-lint-format.md** - Python linting and formatting standards

## Contract

### Inputs and Prerequisites

- Jupyter notebooks in the project
- uv package manager installed (for uvx)
- pyproject.toml with Ruff configuration

### Mandatory

- Run `uvx nbqa ruff notebooks/` after modifying notebook files
- Run `uvx nbqa ruff format --check notebooks/` to verify formatting
- Fix all notebook linting errors before marking task complete

### Forbidden

- Skipping linting on production-bound notebooks without explicit user override
- Using pip install in notebook cells instead of Packages panel

### Execution Steps

1. Install/verify uv is available
2. Run `uvx nbqa ruff notebooks/` to check linting
3. Run `uvx nbqa ruff format notebooks/` to format
4. Fix any reported issues
5. Run `uvx nbqa ruff check --fix notebooks/` for auto-fixable issues

### Output Format

Linting report with cell-level error locations, or "All checks passed" confirmation.

### Validation

Run `uvx nbqa ruff notebooks/` and confirm zero errors. Run `uvx nbqa ruff format --check notebooks/` and confirm no formatting changes needed.

### Design Principles

- Same code quality standards for notebooks as Python modules.
- Automate linting via project automation for consistent CI/CD integration.
- Default to linting; exceptions should be rare and documented.

### Post-Execution Checklist

- [ ] `uvx nbqa ruff notebooks/` passes with zero errors
- [ ] `uvx nbqa ruff format --check notebooks/` passes
- [ ] Project automation includes lint/format targets for notebooks (or direct uvx commands)
- [ ] pyproject.toml has notebook-specific Ruff configuration

## Implementation Details

### Purpose

Jupyter notebooks should maintain the same code quality standards as Python modules. Use **nbqa** (Notebook Quality Assurance) to run standard Python linters on notebook code cells.

### Tool: nbqa + Ruff (Industry Standard)

**Rationale:** nbqa is the industry-standard tool (>1.5M downloads/month) for applying Python linters to notebooks. It extracts code cells, runs linters, and maps results back to the original notebook with correct line numbers.

#### Installation and Usage

See Contract Mandatory and Execution Steps above for the core commands. No installation required — `uvx` runs nbqa and Ruff directly.

```bash
# Check specific notebook
uvx nbqa ruff notebooks/grid_asset_prediction.ipynb
```

#### Integration with Project Automation

Add notebook linting targets to the project's automation entrypoint. Example `Makefile` implementation:

```makefile
.PHONY: lint-notebooks format-notebooks format-notebooks-fix validate-notebook-metadata lint

lint-notebooks: ## Lint Jupyter notebooks with Ruff via nbqa
	uvx nbqa ruff notebooks/

format-notebooks: ## Format Jupyter notebooks with Ruff via nbqa
	uvx nbqa ruff format notebooks/

format-notebooks-fix: ## Format and fix Jupyter notebooks
	uvx nbqa ruff format notebooks/
	uvx nbqa ruff check --fix notebooks/

validate-notebook-metadata: ## Verify all notebook cells have proper metadata names
	python3 -c " \
		import json, re, sys, glob; \
		issues = []; \
		[issues.extend([ \
			f'{nb_path} cell {i}: Missing name' \
			if not cell.get('metadata', {}).get('name') \
			else f'{nb_path} cell {i}: Generic name \"{cell.get("metadata", {}).get("name")}\"' \
			for i, cell in enumerate(json.load(open(nb_path))['cells']) \
			if not cell.get('metadata', {}).get('name') or re.match(r'^(cell|Cell|untitled)\d*$$', cell.get('metadata', {}).get('name', '')) \
		]) for nb_path in glob.glob('notebooks/**/*.ipynb', recursive=True) if '.ipynb_checkpoints' not in nb_path]; \
		print('\n'.join(issues)) if issues else print('All notebooks have valid cell names'); \
		sys.exit(1) if issues else None \
	"

lint: lint-ruff lint-markdown lint-notebooks validate-notebook-metadata ## Run all linting checks
```

> **Note:** This Makefile block is an example implementation. For Taskfile patterns, see `820-taskfile-automation.md`. For Makefile patterns, see `821-makefile-automation.md`.

#### Pre-Task-Completion Validation

**CRITICAL:** Notebook linting is part of the Pre-Task-Completion Validation Gate. See Contract Mandatory items above for required commands. Only skip validation if user explicitly requests override.

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
ignore = ["E501"]  # E501 ignored for linting (long lines allowed); line-length=100 still enforced by formatter

# Notebook-specific: Allow unused variables in exploratory cells
[tool.ruff.lint.per-file-ignores]
"notebooks/*.ipynb" = ["F841"]  # Unused variable assignment
```

**Notebook-valuable Ruff rules:** Beyond the defaults, these rules are particularly useful for notebooks:
- `B006` — mutable default arguments (common in notebook function definitions)
- `C4` — unnecessary comprehensions (simplify list/dict/set comprehensions)
- `UP` — pyupgrade for modern Python syntax (f-strings, type hints)

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

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Running nbqa on Saved Notebook Outputs Instead of Code Cells**

**Problem:** Developers run `uvx nbqa ruff notebooks/` but the notebook contains stale outputs with embedded Python tracebacks or code-like text in markdown cells. nbqa reports false positives from output cells, leading developers to add blanket `# noqa` suppression across the notebook, which then hides real linting issues in actual code cells.

**Correct Pattern:** Clear notebook outputs before linting (`jupyter nbconvert --clear-output --inplace notebooks/*.ipynb`), or configure nbqa to only lint code cells (the default behavior). Never add blanket `# noqa` to suppress output-related false positives -- investigate the actual source of the warning first.

```python
# Wrong: Suppress all warnings with blanket noqa to silence output-related false positives
# ruff: noqa
import pandas as pd
df = pd.read_csv("data.csv")
result = df.groupby("category").sum()  # Real lint issue (F841 unused var) now hidden

# Correct: Clear outputs first, then lint only code cells
# Step 1: jupyter nbconvert --clear-output --inplace notebooks/*.ipynb
# Step 2: uvx nbqa ruff notebooks/
# Step 3: Fix real issues reported, use targeted suppression only where justified
import pandas as pd
df = pd.read_csv("data.csv")
result = df.groupby("category").sum()
result.to_csv("output.csv")  # Actually use the variable
```

**Anti-Pattern 2: Linting Notebooks with a Separate Ruff Config from the Main Project**

**Problem:** A project has Ruff configured in `pyproject.toml` for Python modules, but developers create a separate `.ruff.toml` in the `notebooks/` directory with different rules (e.g., different line length, different select rules). This causes inconsistent code quality standards between notebooks and modules, and developers get confused when code passes linting in one context but fails in another.

**Correct Pattern:** Use a single `pyproject.toml` Ruff configuration for the entire project. Use `[tool.ruff.lint.per-file-ignores]` to add notebook-specific exceptions (e.g., `"notebooks/*.ipynb" = ["F841"]` for unused variables in exploratory cells) rather than maintaining separate configurations.

```toml
# Wrong: Separate .ruff.toml in notebooks/ directory with different rules
# notebooks/.ruff.toml
# line-length = 120
# [lint]
# select = ["E"]  # Only errors, missing F/W/I rules from main config

# Correct: Single pyproject.toml with per-file-ignores for notebooks
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]

[tool.ruff.lint.per-file-ignores]
"notebooks/*.ipynb" = ["F841"]  # Allow unused vars in exploratory cells
```

**Anti-Pattern 3: Running Linting Only in CI, Never Locally**

**Problem:** Notebook linting is configured only in CI/CD pipelines. Developers push notebooks without running `uvx nbqa ruff notebooks/` locally, discover failures after commit, and make quick `# noqa` fixes to pass CI rather than properly fixing the code. This leads to accumulation of suppressed warnings and degraded code quality over time.

**Correct Pattern:** Add notebook linting to the project's automation entrypoint and run it as part of the local development workflow before every commit. Include it in pre-commit hooks and run alongside other lint targets. Fix issues properly rather than suppressing them to pass CI.

```makefile
# Makefile
.PHONY: lint-notebooks lint

lint-notebooks: ## Lint Jupyter notebooks with Ruff via nbqa
	uvx nbqa ruff notebooks/
	uvx nbqa ruff format --check notebooks/

lint: lint-ruff lint-notebooks ## Run all linting checks (run before every commit)
```

**Correct CI/CD pattern** — run the same automation targets in CI:
```yaml
# .github/workflows/ci.yml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: make lint-notebooks  # Same target locally and in CI
```
