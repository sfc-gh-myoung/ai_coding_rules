# Snowflake Notebook Code Quality and Linting

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:nbqa, kw:notebook-linting
**Keywords:** nbqa, ruff, notebook linting, code quality, Jupyter, notebook formatting, lint notebooks, notebook validation
**TokenBudget:** ~3350
**ContextTier:** Low
**Depends:** 109-snowflake-notebooks.md, 201-python-lint-format.md

## Scope

**What This Rule Covers:**
Code quality tooling and linting configuration for Jupyter Notebooks using nbqa and Ruff, including Taskfile integration, common linting issues, Ruff configuration, and when to skip linting.

**When to Load This Rule:**
- Setting up notebook linting in a project
- Configuring nbqa with Ruff for notebooks
- Integrating notebook linting into CI/CD or Taskfile
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
- Automate linting via Taskfile for consistent CI/CD integration.
- Default to linting; exceptions should be rare and documented.

### Post-Execution Checklist

- [ ] `uvx nbqa ruff notebooks/` passes with zero errors
- [ ] `uvx nbqa ruff format --check notebooks/` passes
- [ ] Taskfile includes lint-notebooks and format-notebooks tasks
- [ ] pyproject.toml has notebook-specific Ruff configuration

## Implementation Details

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

validate-notebook-metadata:
  desc: "Verify all notebook cells have proper metadata names"
  cmds:
    - |
      python3 -c "
      import json, re, sys, glob
      issues = []
      for nb_path in glob.glob('notebooks/**/*.ipynb', recursive=True):
          if '.ipynb_checkpoints' in nb_path: continue
          with open(nb_path) as f:
              nb = json.load(f)
          for i, cell in enumerate(nb['cells']):
              name = cell.get('metadata', {}).get('name')
              if not name:
                  issues.append(f'{nb_path} cell {i}: Missing name')
              elif re.match(r'^(cell|Cell|untitled)\d*$', name):
                  issues.append(f'{nb_path} cell {i}: Generic name \"{name}\"')
      if issues:
          print('\n'.join(issues))
          sys.exit(1)
      print('All notebooks have valid cell names')
      "

lint:
  desc: "Run all linting checks"
  cmds:
    - task: lint-ruff
    - task: lint-markdown
    - task: lint-notebooks
    - task: validate-notebook-metadata
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

**Correct Pattern:** Add notebook linting to the project's Taskfile (`task lint-notebooks`) and run it as part of the local development workflow before every commit. Include it in pre-commit hooks or make it a habit alongside `task lint`. Fix issues properly rather than suppressing them to pass CI.

```yaml
# Wrong: Linting only in CI, developers never run locally
# .github/workflows/ci.yml
# - run: uvx nbqa ruff notebooks/
# Result: Developers add "# noqa" to fix CI failures without understanding issues

# Correct: Add to Taskfile for local + CI use
# Taskfile.yml
lint-notebooks:
  desc: "Lint Jupyter notebooks with Ruff via nbqa"
  cmds:
    - uvx nbqa ruff notebooks/
    - uvx nbqa ruff format --check notebooks/

lint:
  desc: "Run all linting checks (run before every commit)"
  cmds:
    - task: lint-ruff
    - task: lint-notebooks
```
