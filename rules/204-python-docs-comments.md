# Python Documentation, Comments, and Docstrings

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-01-27
**Keywords:** Python docstrings, documentation, comments, pydocstyle, Ruff DOC rules, Google style, NumPy style, PEP 257, semantic depth, side effects
**TokenBudget:** ~6000
**ContextTier:** High
**Depends:** 200-python-core.md, 201-python-lint-format.md
**LoadTrigger:** kw:docstring, kw:documentation, kw:comments

## Scope

**What This Rule Covers:**
Clear, enforceable standards for Python documentation, source code comments, and docstrings aligned with PEP 257 and modern tooling (Ruff pydocstyle, Sphinx Napoleon). Covers Google and NumPy styles, semantic depth requirements, side effects documentation.

**When to Load This Rule:**
- Writing or reviewing Python docstrings
- Setting up docstring standards for a new project
- Configuring Ruff pydocstyle rules
- Documenting public APIs

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Python foundation patterns
- **201-python-lint-format.md** - Ruff configuration and linting

### External Documentation

- [PEP 257](https://peps.python.org/pep-0257/) - Docstring conventions
- [Google Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [NumPy Style Guide](https://numpydoc.readthedocs.io/en/latest/format.html)
- [Sphinx Napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)

## Contract

### Inputs and Prerequisites

- Python 3.11+ codebase
- pyproject.toml for configuration
- Ruff for linting (pydocstyle rules)

### Mandatory

- **Choose ONE docstring style** - Google (recommended) or NumPy
- **All public APIs need docstrings** - Modules, classes, functions, methods
- **Enable Ruff D rules** - `select = ["D"]` in pyproject.toml
- **Docstrings must be semantically valuable** - Explain context, side effects, preconditions
- **Document all side effects** - I/O, state mutations, subprocess calls, network requests
- **Follow PEP 257** - One-line summary, blank line, then details

### Forbidden

- Mixing Google and NumPy styles in the same project
- Missing docstrings for public APIs
- Duplicating type information already in type hints
- Comments that merely restate the code ("what" instead of "why")

### Execution Steps

1. Choose one docstring style (Google recommended)
2. Configure Ruff pydocstyle rules in pyproject.toml
3. Add docstrings to all public modules, classes, functions
4. Use comments to explain "why" and intent
5. Document side effects, preconditions, performance
6. Run `uvx ruff check .` to validate

### Output Format

- Docstrings following Google or NumPy style
- Comments explaining intent and trade-offs
- Updated pyproject.toml with pydocstyle configuration

### Validation

**Success Criteria:**
- `uvx ruff check .` passes all D rules
- Docstrings provide semantic value beyond type hints
- Comments explain "why", not "what"

### Design Principles

- **Consistency:** One docstring style per project
- **Semantic depth:** Document behavior, constraints, side-effects
- **PEP compliance:** Follow PEP 257 for docstrings, PEP 8 for comments
- **Type hints first:** Use type annotations; don't duplicate in docstrings

### Post-Execution Checklist

- [ ] pyproject.toml has `[tool.ruff.lint.pydocstyle]` with convention
- [ ] All public functions have docstrings
- [ ] All classes have docstrings
- [ ] Side effects explicitly documented
- [ ] Preconditions and performance documented
- [ ] `uvx ruff check .` passes D rules

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Stale Docstrings

```python
# BAD: Docstring doesn't match signature
def calculate_total(items, tax_rate, discount=0):
    """Calculate total price.
    Args:
        items: List of item prices
        tax: Tax percentage  # Wrong name!
    """
```

**Problem:** Misleading documentation is worse than none. IDE tooltips show wrong info.

**Correct Pattern:**
```python
def calculate_total(items: list[float], tax_rate: float, discount: float = 0) -> float:
    """Calculate total price for items with tax and discount.
    Args:
        items: List of item prices in dollars.
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%).
        discount: Discount amount to subtract.
    """
```

### Anti-Pattern 2: Over-Commenting Obvious Code

```python
# BAD: Restates the obvious
counter += 1  # Increment counter by 1
if user.role == "admin":  # Check if user is admin
    return True  # Return true
```

**Problem:** Clutters code, comments become stale, obscures important explanations.

**Correct Pattern:**
```python
# Rate limit resets every hour; increment tracks requests in current window
counter += 1
# Admin bypass for emergency access during outages (see incident #1234)
if user.role == "admin":
    return True
```

## Ruff Configuration

```toml
[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "D"]

[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy"
```

## Google-style Example

```python
def fetch_user(user_id: str, include_roles: bool = False) -> User:
    """Fetch user by identifier.

    Args:
        user_id: Stable user identifier (UUID string).
        include_roles: When true, also loads role memberships.

    Returns:
        User: Hydrated user object. If `include_roles` is true, roles are populated.

    Raises:
        UserNotFoundError: If the user_id does not exist.
        PermissionError: If the caller lacks access.
    """
```

## Docstring Quality Standards

### The Five Questions Every Docstring Must Answer

1. **What** - One-line imperative summary
2. **Why** - Purpose and context
3. **When** - Preconditions, constraints, valid states
4. **How** - Key behavioral details
5. **Effects** - Side effects, state changes, I/O

### Module Docstrings - Architectural Context Required

```python
# BAD
"""Core operations for demo management."""

# GOOD
"""Core business logic for Snowflake demo lifecycle management.

This module provides manager classes that orchestrate demo operations.
Each manager handles a specific domain (data, database, apps, deployment).

Public API:
    - DataManager: Generate and upload synthetic data
    - DatabaseManager: Create/teardown Snowflake infrastructure

Side Effects:
    - Modifies Snowflake database objects
    - Writes/reads local CSV files
    - Executes external processes (snow CLI)

Thread Safety: Not thread-safe. Create separate instances for concurrent operations.
"""
```

### Function Docstrings - Document Behavior

```python
# BAD
def generate(self) -> OperationResult:
    """Generate synthetic data."""

# GOOD
def generate(self) -> OperationResult:
    """Generate synthetic mortgage data files for the demo.

    Executes data generation script creating CSVs (borrowers, properties, loans).
    Files written to config.data_path. Existing files overwritten without warning.

    Preconditions:
        - Python script must exist at config.scripts_path/generate_all_data.py
        - Python environment must have faker, pandas dependencies

    Performance: 30-60 seconds depending on CPU and disk I/O.

    Side Effects:
        - Creates config.data_path directory if missing
        - Overwrites existing CSV files
        - Spawns subprocess running Python script
        - Prints progress spinner to console
    """
```

### Side Effects Documentation - Always Explicit

```python
def execute_operation(operation_id: str, operation_type: OperationType):
    """Execute long-running operation asynchronously in background thread.

    Side Effects:
        - Mutates OPERATIONS dict (global state)
        - Modifies Snowflake database objects
        - Writes/reads local file system
        - Spawns subprocesses (snow CLI)
        - May run for minutes

    Concurrency:
        Not thread-safe. OPERATIONS dict writes are not synchronized.
    """
```

## Comment Standards (PEP 8)

- Comments explain intent, rationale, and trade-offs ("why" not "what")
- Block comments above code they describe
- Remove commented-out code; use version control
- Keep comments up to date when behavior changes

## Docstring Quality Checklist

**For Function/Method Docstrings:**
- [ ] Purpose: What does this accomplish? (Not just "what" but "why")
- [ ] Args Semantics: Meaning, constraints, units, valid ranges
- [ ] Returns Semantics: What's in return value, when it's None/empty
- [ ] Preconditions: What must be true before calling?
- [ ] Side Effects: File I/O, DB operations, network, subprocess, state mutations
- [ ] Performance: For operations >1 second
- [ ] Concurrency: Thread-safe? Async-safe? Locks required?
- [ ] Error Handling: What triggers exceptions? Should callers retry?

**For Class Docstrings:**
- [ ] Purpose: What abstraction does this represent?
- [ ] Lifecycle: Construction, cleanup, resource management
- [ ] Thread Safety: Safe for concurrent use?
- [ ] Key Methods: List 3-5 most important methods

**For Exception Docstrings:**
- [ ] Triggers: Concrete scenarios that raise this exception
- [ ] Handling Strategy: Retry? Log? Re-raise?
- [ ] Recovery: What actions can resolve this error?

## Common Quality Mistakes (Not Caught by Ruff)

**Mistake 1: Restating Function Name**
```python
# BAD: def get_user(...): """Get user."""
# GOOD: def get_user(...): """Fetch user account from database by unique identifier."""
```

**Mistake 2: Missing Side Effects**
```python
# BAD: """Save report data."""
# GOOD: """Persist report to JSON file and upload to S3 bucket.
#        Side Effects: Writes to ./reports/, uploads to AWS_BUCKET, prints progress."""
```

**Mistake 3: Vague Arguments**
```python
# BAD: Args: data: Data object. options: Options.
# GOOD: Args: data: Raw sensor readings with 'sensor_id' (str), 'readings' (list[float]).
#             options: Processing config with 'sampling_rate' (int), 'aggregation' (str).
```

**Mistake 4: No Preconditions/Performance**
```python
# BAD: """Run database migrations."""
# GOOD: """Apply pending schema migrations.
#        Preconditions: Connection established, ALTER TABLE privileges.
#        Performance: 30-60s typical, 5-15min for tables >1M rows."""
```
