# Python Documentation, Comments, and Docstrings

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Python docstrings, documentation, comments, pydocstyle, Ruff DOC rules, API documentation, Google style, NumPy style, PEP 257, code quality, semantic depth, side effects, preconditions, performance, thread safety
**TokenBudget:** ~5700
**ContextTier:** High
**Depends:** rules/200-python-core.md, rules/201-python-lint-format.md

## Purpose
Provide clear, enforceable standards for Python documentation (project docs), source code comments, and docstrings, aligned with widely accepted industry practices (PEP 257, PEP 8) and modern tooling (Ruff pydocstyle, Sphinx Napoleon).

## Rule Scope

Python comments, docstrings, and developer-facing documentation across libraries, apps, CLIs, and services

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Choose ONE docstring style** - Google (recommended) or NumPy, configure in pyproject.toml
- **All public APIs need docstrings** - Modules, classes, functions, methods
- **Enable Ruff D rules** - `select = ["D"]` in [tool.ruff.lint]
- **Docstrings must be semantically valuable** - Not just syntactically correct; explain context, side effects, preconditions
- **Document all side effects** - I/O operations, state mutations, subprocess calls, network requests
- **Use comments for "why"** - Not "what" (code shows what)
- **Follow PEP 257** - One-line summary, then blank line, then details
- **Never mix docstring styles** - Consistency across entire project

**Quick Checklist:**
- [ ] pyproject.toml has `[tool.ruff.lint.pydocstyle]` with convention
- [ ] All public functions have docstrings
- [ ] All classes have docstrings
- [ ] Docstrings start with one-line summary
- [ ] Args, Returns, Raises documented with semantic meaning (not just types)
- [ ] Side effects explicitly documented (I/O, state, subprocess, network)
- [ ] Preconditions and performance expectations documented
- [ ] Thread safety / concurrency behavior documented
- [ ] `uvx ruff check .` passes D rules
- [ ] Comments explain "why", not "what"

## Contract

<contract>
<inputs_prereqs>
Python 3.11+; `pyproject.toml`; Ruff; optional Sphinx with Napoleon
</inputs_prereqs>

<mandatory>
`uvx ruff` for lint/format; `uv run` for project execution; Sphinx for docs
</mandatory>

<forbidden>
Inconsistent, project-specific ad-hoc styles without configuration
</forbidden>

<steps>
1. Choose one docstring style for the repo: Google (recommended) or NumPy
2. Configure Ruff pydocstyle rules and convention
3. Add and maintain docstrings for all public modules/classes/functions/methods
4. Use comments to explain "why" and intent; avoid restating code
5. Prevent and fix common mistakes via lint and review
</steps>

<output_format>
Docstrings and comments following requirements below; updated `pyproject.toml` config
</output_format>

<validation>
`uvx ruff check .` passes with D-rules; docs build (if applicable) succeeds
</validation>

<design_principles>
- Prefer Google-style docstrings with Sphinx Napoleon (or NumPy if already established)
- Follow PEP 257 for structure and placement; PEP 8 for comment style
- Document behavior, constraints, side-effects, exceptions, and units over implementation
- Use type hints; do not duplicate types in docstrings
- Keep comments high-signal: explain intent and trade-offs
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Stale Docstrings That Don't Match Code

**Problem:** Docstrings that describe outdated behavior, wrong parameter names, or removed functionality because they weren't updated when code changed.

**Why It Fails:** Misleading documentation is worse than no documentation. Developers trust docstrings and write incorrect code based on them. IDE tooltips show wrong information. Auto-generated API docs become unreliable.

**Correct Pattern:**
```python
# BAD: Stale docstring (function signature changed)
def calculate_total(items, tax_rate, discount=0):
    """Calculate total price for items.

    Args:
        items: List of item prices
        tax: Tax percentage  # Wrong name!
        # discount parameter not documented
    """

# GOOD: Docstring matches current signature
def calculate_total(items: list[float], tax_rate: float, discount: float = 0) -> float:
    """Calculate total price for items with tax and discount.

    Args:
        items: List of item prices in dollars.
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%).
        discount: Discount amount to subtract. Defaults to 0.

    Returns:
        Total price after tax and discount.
    """
```

### Anti-Pattern 2: Over-Commenting Obvious Code

**Problem:** Adding comments that simply restate what the code does, rather than explaining why or providing context.

**Why It Fails:** Clutters code with noise. Comments become stale faster than code. Developers learn to ignore comments. Obscures genuinely important explanatory comments.

**Correct Pattern:**
```python
# BAD: Comments that restate the obvious
# Increment counter by 1
counter += 1
# Check if user is admin
if user.role == "admin":
    # Return true
    return True

# GOOD: Comments explain WHY, not WHAT
# Rate limit resets every hour; increment tracks requests in current window
counter += 1
# Admin bypass needed for emergency access during outages (see incident #1234)
if user.role == "admin":
    return True
```

## Post-Execution Checklist

### Syntax Compliance (Automated)
- [ ] One docstring style chosen and configured (Google/NumPy)
- [ ] Ruff D-rules enabled with correct convention
- [ ] Public APIs have docstrings with summaries and details
- [ ] No duplicated types in docstrings when type hints exist
- [ ] Comments explain intent; no commented-out code remains
- [ ] Optional docs build (Sphinx+Napoleon) succeeds
- [ ] `uvx ruff check .` passes including D-rules

### Quality Standards (Manual Review)
- [ ] Module docstrings explain architectural context (not just file contents)
- [ ] Function docstrings document all side effects (I/O, state, subprocess, network)
- [ ] Preconditions explicitly listed for functions with dependencies
- [ ] Performance expectations documented for operations >1 second
- [ ] Thread safety / concurrency behavior explicitly stated
- [ ] Argument descriptions explain semantics, constraints, units (not just types)
- [ ] Return value descriptions explain contents and structure
- [ ] Exception docstrings list triggers and handling strategies
- [ ] Dataclass fields document meaning and constraints
- [ ] Examples show realistic usage patterns (not toy code)

## Validation
- **Lint:** `uvx ruff check .` must pass, including D-rules
- **Format:** `uvx ruff format --check .` passes
- **Docs (optional):** `sphinx-build -b html docs/ docs/_build/html` completes without errors

> **Investigation Required**
> When applying this rule:
> 1. **Read pyproject.toml BEFORE adding docstrings** - Check if pydocstyle convention is already set
> 2. **Check existing docstring style** - Read a few functions/classes to see Google vs NumPy
> 3. **Never assume docstring format** - Match project's existing convention
> 4. **Verify Ruff D rules enabled** - Check [tool.ruff.lint] select field
> 5. **Read module docstrings** - Understand project's documentation standards
> 6. **Investigate architectural context** - Understand how the module/function fits in the system
> 7. **Identify side effects** - Look for file I/O, network calls, subprocess execution, state mutations
> 8. **Determine performance characteristics** - Check if operations are fast (<100ms) or slow (>1s)
> 9. **Check concurrency behavior** - Look for threading, async/await, shared state access
> 10. **Understand failure modes** - What can go wrong? What exceptions are raised? What are recovery strategies?
>
> **Anti-Pattern:**
> "Adding Google-style docstrings... (without checking existing style)"
> "Here's the documentation... (without matching project convention)"
> Writing "Execute SQL file" for a function that modifies database, spawns subprocess, logs to console
>
> **Correct Pattern:**
> "Let me check your existing docstring style first."
> [reads files, checks pyproject.toml pydocstyle config]
> "I see you use Google-style docstrings. Adding documentation following this convention..."
> [investigates code to understand side effects, performance, concurrency]
> "This function modifies Snowflake database, spawns snow CLI subprocess, and writes progress to console. Documenting all side effects..."

## Output Format Examples

```python
# Investigation: Check current implementation
# Read existing files, understand patterns

# Implementation: Following uv + ruff + pytest standards
from typing import Protocol
from datetime import datetime, UTC

class ServiceProtocol(Protocol):
    """Clear contract for service implementations."""

    def process(self, data: dict) -> dict:
        """Process data following validation rules."""
        ...

def implementation_function(input_data: dict) -> dict:
    """
    Implement feature following project conventions.

    Args:
        input_data: Validated input following schema

    Returns:
        Processed result with metadata

    Raises:
        ValueError: If input validation fails
    """
    # Use datetime.now(UTC) not datetime.utcnow()
    timestamp = datetime.now(UTC)

    # Implement business logic
    result = {"status": "success", "timestamp": timestamp}
    return result

# Validation: Test the implementation
def test_implementation_function():
    """Test following AAA pattern."""
    # Arrange
    test_input = {"key": "value"}

    # Act
    result = implementation_function(test_input)

    # Assert
    assert result["status"] == "success"
    assert "timestamp" in result
```

```bash
# Validation commands
uvx ruff check .
uvx ruff format --check .
uv run pytest tests/
```

## References
- PEP 257 Docstring Conventions: https://peps.python.org/pep-0257/
- PEP 8 (Comments): https://peps.python.org/pep-0008/#comments
- Ruff pydocstyle rules (D): https://docs.astral.sh/ruff/rules/#pydocstyle-d
- Sphinx Napoleon: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

## 1. Docstring Standards (PEP 257 + Google/NumPy)
- **Requirement:** Use triple double-quotes for all docstrings. First line is a concise imperative summary ending with a period.
- **Requirement:** For multi-line docstrings, include a blank line after the summary, then details.
- **Requirement:** Maintain a single consistent style across the repo: Google (recommended) or NumPy.
- **Requirement:** Provide docstrings for all public modules, packages, classes, functions, and methods.
- **Rule:** Private helpers may omit docstrings if trivially obvious; otherwise document rationale and behavior.
- **Requirement:** Do not duplicate type annotations in docstrings; focus on semantics, constraints, and units.
- **Requirement:** Document non-trivial exceptions in a `Raises` section; document side-effects (I/O, logging, network, global state).
- **Requirement:** Place module docstrings as the first statement in the file. Describe purpose, public APIs, environment variables, and notable side-effects.
- **Rule:** Property docstrings should describe the attribute (not "Get X").

### 1.1 Google-style Examples
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
      PermissionError: If the caller lacks access to this user.

    """

class RateLimiter:
    """Token-bucket rate limiter.

    Controls request throughput using a token bucket with burst capacity.
    Thread-safe for concurrent callers.
    """

"""Payment processing integration.

Exposes public entry points for charge and refund workflows.
Reads API keys from environment variables. Emits audit logs to `payments_audit`.
"""
```

### 1.2 Docstring Quality Standards Beyond Syntax

**Critical:** Docstrings must be **semantically valuable**, not just syntactically correct. A docstring that passes Ruff D-rules but provides no useful information is a failed docstring.

#### The Five Questions Every Docstring Must Answer

1. **What** - One-line imperative summary (keep concise)
2. **Why** - Purpose and context (why does this exist?)
3. **When** - Preconditions, constraints, valid states
4. **How** - Key behavioral details (not implementation)
5. **Effects** - Side effects, state changes, I/O operations

#### Module Docstrings - Architectural Context Required

**Anti-Pattern (Minimal):**
```python
"""Core operations for demo management (data, database, apps, deployment)."""
```
[FAIL] Just lists file contents (obvious from code)
[FAIL] No explanation of architectural role
[FAIL] No usage patterns or entry points
[FAIL] Missing side effects

**Correct Pattern (Valuable):**
```python
"""Core business logic for Snowflake demo lifecycle management.

This module provides manager classes that orchestrate demo operations by coordinating
between the Snowflake CLI wrapper, local file system operations, and user feedback.
Each manager handles a specific domain (data, database, apps, deployment) and follows
a consistent pattern:

1. Initialize with Config and Console instances
2. Validate preconditions (files exist, Snowflake accessible)
3. Execute operations with progress tracking and error handling
4. Return OperationResult with success status, timing, and details

Public API:
    - DataManager: Generate and upload synthetic data
    - DatabaseManager: Create/load/teardown Snowflake infrastructure
    - AppManager: Deploy Streamlit apps and Jupyter notebooks
    - DeploymentManager: Orchestrate full deployment workflow

Side Effects:
    - Modifies Snowflake database objects (tables, views, stages, agents)
    - Writes/reads local CSV files in config.data_path
    - Executes external processes (uv/python, snow CLI)
    - Prints progress/status to console via Rich

Thread Safety:
    Not thread-safe. Create separate instances for concurrent operations.

Example:
    >>> config = Config.load(demo_path="./my_demo")
    >>> manager = DatabaseManager(config)
    >>> result = manager.setup()
    >>> if result.success:
    ...     print(f"Setup completed in {result.duration:.2f}s")
"""
```
[PASS] Explains WHY and HOW the module fits in architecture
[PASS] Documents patterns and entry points
[PASS] Lists all side effects explicitly
[PASS] Warns about thread safety
[PASS] Provides realistic usage example

#### Function Docstrings - Document Behavior, Not Implementation

**Anti-Pattern (Minimal):**
```python
def generate(self) -> OperationResult:
    """Generate synthetic mortgage data using existing script."""
```
[FAIL] Doesn't explain WHAT data or HOW MUCH
[FAIL] No mention of where output goes
[FAIL] Missing preconditions
[FAIL] No performance expectations
[FAIL] Doesn't warn about overwriting files

**Correct Pattern (Valuable):**
```python
def generate(self) -> OperationResult:
    """Generate synthetic mortgage data files required for the demo.

    Executes the data generation script (scripts/generate_all_data.py) which creates
    CSV files for the mortgage demo domain model:
        - borrowers.csv (~10K records)
        - properties.csv (~10K records)
        - loans.csv (~10K records)
        - payments.csv (~100K records)
        - property_inspections.csv (~5K records)

    Files are written to config.data_path (default: data/generated/) with deterministic
    seeding for reproducible data. Existing files are overwritten without confirmation.

    Preconditions:
        - Python data generation script must exist at config.scripts_path/generate_all_data.py
        - Python environment must have faker, pandas dependencies installed
        - Sufficient disk space (~50MB for generated CSV files)

    Performance:
        Typical execution time is 30-60 seconds depending on CPU and disk I/O.
        Progress indicator shows activity but not granular percentage.

    Returns:
        OperationResult with:
            - success=True if all CSV files generated successfully
            - duration: actual generation time in seconds
            - details['csv_files']: count of CSV files created
            - details['output_dir']: absolute path where files were written

    Side Effects:
        - Creates config.data_path directory if it doesn't exist
        - Overwrites existing CSV files without warning
        - Spawns subprocess running Python script
        - Prints progress spinner to console

    Example:
        >>> manager = DataManager(config)
        >>> result = manager.generate()
        >>> print(f"{result.details['csv_files']} files in {result.duration:.1f}s")
        5 files in 45.3s
    """
```
[PASS] Explains WHAT, WHY, WHERE, and HOW
[PASS] Documents preconditions and performance
[PASS] Warns about destructive behavior (overwrites)
[PASS] Specifies all side effects
[PASS] Example shows realistic usage

#### Dataclass Docstrings - Document Field Semantics

**Anti-Pattern (Minimal):**
```python
@dataclass
class OperationResult:
    """Result of an operation execution."""

    success: bool
    message: str
    duration: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
```
[FAIL] Just repeats the class name
[FAIL] No explanation of field semantics
[FAIL] No usage guidance

**Correct Pattern (Valuable):**
```python
@dataclass
class OperationResult:
    """Standardized outcome from a manager operation with timing and diagnostic data.

    Used as the return type for all manager operations (setup, teardown, generate, etc.)
    to provide consistent success/failure reporting across the CLI and web interfaces.

    Attributes:
        success: True if operation completed without errors. False means the operation
            failed and may require user intervention (check message/details for cause).
        message: Human-readable summary of what happened. On success, describes what was
            accomplished (e.g., "5 tables created"). On failure, describes the error.
        duration: Wall-clock time in seconds from operation start to completion. Useful
            for performance analysis and user feedback. Defaults to 0.0 if timing unavailable.
        details: Optional diagnostic data specific to the operation. May contain:
            - stdout/stderr from subprocess execution
            - counts of objects created/modified
            - file paths for artifacts generated
            - error details for troubleshooting

    Example:
        >>> result = manager.setup()
        >>> if not result.success:
        ...     logger.error(f"Setup failed: {result.message}")
        ...     logger.debug(f"Details: {result.details}")
    """

    success: bool
    message: str
    duration: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
```
[PASS] Explains the PURPOSE and CONTEXT
[PASS] Documents field semantics and constraints
[PASS] Shows example usage
[PASS] Explains what goes in `details` dict

#### Exception Docstrings - Document Triggers and Handling

**Anti-Pattern (Minimal):**
```python
class ConfigError(DemoManagerError):
    """Configuration-related errors (invalid config, missing files, etc.)."""
```
[FAIL] Lists categories but not WHEN to use
[FAIL] No examples of what triggers this
[FAIL] No handling guidance

**Correct Pattern (Valuable):**
```python
class ConfigError(DemoManagerError):
    """Raised when configuration is missing, malformed, or contains invalid values.

    This exception indicates a problem with the configuration file (demo_manager.yaml)
    or environment variables that must be fixed before the application can proceed.
    Unlike operational errors, ConfigErrors typically require user intervention to fix
    the configuration source, not retry logic.

    Common Triggers:
        - YAML syntax errors in config file
        - Missing required fields (snowflake.database, snowflake.schemas)
        - Invalid data types (port as string instead of int)
        - File paths that don't exist (sql_dir, data_dir)
        - Mutually exclusive options set simultaneously

    Handling:
        ConfigErrors should be caught at application startup and presented to the user
        with actionable fix instructions. Do not retry operations that fail with ConfigError.

    Example:
        >>> try:
        ...     config = Config.load("bad_config.yaml")
        ... except ConfigError as e:
        ...     print(f"Configuration error: {e}")
        ...     print("Fix your config file and try again")
        ...     sys.exit(1)
    """
```
[PASS] Explains WHEN and WHY this exception is raised
[PASS] Lists concrete trigger scenarios
[PASS] Provides handling guidance
[PASS] Shows realistic usage pattern

#### Side Effects Documentation - Always Explicit

**Required:** Document ALL side effects in a dedicated section or inline notes:

```python
def execute_operation(operation_id: str, operation_type: OperationType, config: Config):
    """Execute a long-running manager operation asynchronously in a background thread.

    Called by FastAPI BackgroundTasks to run operations without blocking HTTP responses.
    Updates the OPERATIONS dict (in-memory state store) with progress and results that
    can be polled via GET /api/operations/{operation_id}.

    Side Effects:
        - Mutates OPERATIONS dict (global state)
        - Modifies Snowflake database objects (depending on operation_type)
        - Writes/reads local file system
        - Spawns subprocesses (snow CLI, python scripts)
        - May run for minutes (database setup, data generation)
        - Prints to stdout/stderr (subprocess output)

    Concurrency:
        Not thread-safe. FastAPI BackgroundTasks runs in thread pool, so multiple
        operations can execute concurrently. OPERATIONS dict writes are not synchronized,
        which can cause race conditions if the same operation_id is reused.

    Args:
        operation_id: UUID string tracking this operation instance. Must be unique.
        operation_type: Enum specifying which manager method to invoke.
        config: Configuration with Snowflake credentials and file paths.
    """
```
[PASS] Lists ALL side effects (I/O, state, process, network)
[PASS] Documents concurrency behavior
[PASS] Warns about race conditions
[PASS] Estimates runtime ("may run for minutes")

## 2. Comment Standards (PEP 8)
- **Requirement:** Comments must explain intent, rationale, and trade-offs—the "why"—not restate the code.
- **Requirement:** Place block comments above the code they describe; keep inline comments short and sparing.
- **Requirement:** Remove commented-out code. Use version control or link to issues instead.
- **Rule:** Prefer references to requirements or tickets over long narrative comments.
- **Rule:** Keep comments up to date; when behavior changes, update adjacent comments/docstrings.

## 3. Project Documentation (Optional)
- **Rule:** If publishing developer docs, use Sphinx with Napoleon to parse Google/NumPy docstrings.
- **Rule:** Consider AutoAPI/Autodoc to generate API docs from code; use Intersphinx for cross-project links.
- **Consider:** Add a `docs/` folder with a minimal Sphinx configuration and CI job to build docs on PRs.

## 4. Enforcement with Ruff (pydocstyle)
- **Requirement:** Enable pydocstyle (D) rules in Ruff and set a single convention.

Example `pyproject.toml` snippet:
```toml
[tool.ruff]
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "D"]
ignore = []

[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy"
```

## 5. Common Mistakes & How to Prevent Them

### Syntax Mistakes (Caught by Ruff)
- **Missing docstrings on public APIs** - Enforce D-rules; PRs must add docstrings.
- **Parameter lists out of sync with signatures** - CI lint must fail; reviewers verify.
- **Duplicated types in docstrings when hints exist** - Remove types; describe semantics/units.
- **No blank line after summary** - Enforce PEP 257 via Ruff.
- **Module docstrings not first** - Enforce placement; move to top.
- **Inconsistent styles** - Pick one project-wide style; document in README.

### Quality Mistakes (NOT Caught by Ruff - Requires Human/AI Review)

#### Mistake 1: Restating the Function Name

**Anti-Pattern:**
```python
def get_user(user_id: str) -> User:
    """Get user."""  # [FAIL] Just repeats function name
```

**Correct:**
```python
def get_user(user_id: str) -> User:
    """Fetch user account from database by unique identifier.

    Args:
        user_id: UUID string of user account to retrieve.

    Returns:
        User object with profile, preferences, and role memberships.

    Raises:
        UserNotFoundError: If user_id does not exist in database.

    Side Effects:
        Queries users table via database connection pool.
    """
```

#### Mistake 2: Missing Side Effects Documentation

**Anti-Pattern:**
```python
def save_report(data: dict) -> None:
    """Save report data."""  # [FAIL] No mention of file I/O
```

**Correct:**
```python
def save_report(data: dict) -> None:
    """Persist report data to JSON file and upload to S3 bucket.

    Args:
        data: Report data dictionary with 'title', 'content', 'timestamp' keys.

    Side Effects:
        - Writes JSON file to ./reports/{timestamp}.json (overwrites if exists)
        - Uploads file to S3 bucket configured in AWS_BUCKET env var
        - Requires AWS credentials in environment or ~/.aws/credentials
        - Prints upload progress to stdout
        - May take 5-10 seconds for large reports (>10MB)

    Raises:
        ValueError: If required keys missing from data dict.
        S3Error: If AWS credentials invalid or bucket inaccessible.
    """
```

#### Mistake 3: Vague Argument Descriptions

**Anti-Pattern:**
```python
def process_data(data: dict, options: dict) -> dict:
    """Process data.

    Args:
        data: Data object.  # [FAIL] What's in it? What format?
        options: Options.  # [FAIL] What options? What do they do?

    Returns:
        dict: Results.  # [FAIL] What results? What keys?
    """
```

**Correct:**
```python
def process_data(data: dict, options: dict) -> dict:
    """Transform raw sensor data into aggregated metrics with configurable sampling.

    Args:
        data: Raw sensor readings with keys:
            - 'sensor_id' (str): Unique sensor identifier
            - 'readings' (list[float]): Numeric measurements
            - 'timestamp' (datetime): Collection time in UTC
        options: Processing configuration with keys:
            - 'sampling_rate' (int): Sample every Nth reading (default: 1 = all)
            - 'aggregation' (str): 'mean' | 'median' | 'sum' (default: 'mean')
            - 'outlier_threshold' (float): Std devs for outlier removal (default: 3.0)

    Returns:
        dict with keys:
            - 'sensor_id' (str): Same as input
            - 'metric' (float): Aggregated value per options.aggregation
            - 'sample_count' (int): Number of readings used
            - 'outliers_removed' (int): Count of outliers filtered
    """
```

#### Mistake 4: No Preconditions or Performance Expectations

**Anti-Pattern:**
```python
def migrate_database() -> None:
    """Run database migrations."""  # [FAIL] No preconditions, no timing
```

**Correct:**
```python
def migrate_database() -> None:
    """Apply pending schema migrations to production database.

    Preconditions:
        - Database connection must be established (call connect() first)
        - User must have ALTER TABLE privileges
        - Database must be at least version 5.7 (MySQL) or 12 (PostgreSQL)
        - All application servers should be in maintenance mode
        - Backup completed within last hour (verify externally)

    Performance:
        - Typical migration: 30-60 seconds
        - Large table migrations (>1M rows): 5-15 minutes
        - Blocks writes to affected tables during execution
        - Does NOT automatically rollback on failure

    Side Effects:
        - Modifies database schema (tables, columns, indexes)
        - Writes migration history to schema_migrations table
        - Logs SQL statements to migration.log
        - May lock tables temporarily (blocks concurrent writes)

    Raises:
        MigrationError: If migration SQL fails or version conflict detected.
        ConnectionError: If database connection lost during migration.
    """
```

#### Mistake 5: Missing Thread Safety / Concurrency Notes

**Anti-Pattern:**
```python
class Cache:
    """Simple in-memory cache."""  # [FAIL] Thread safe? Async safe?

    def __init__(self):
        self._data = {}
```

**Correct:**
```python
class Cache:
    """Simple in-memory cache with TTL support.

    Thread Safety:
        NOT thread-safe. Dictionary mutations are not synchronized. For multi-threaded
        usage, wrap get/set calls with threading.Lock or use thread-local storage.

    Concurrency:
        NOT async-safe. Use asyncio.Lock for async/await contexts.

    Memory Management:
        No automatic eviction. Items remain until explicitly cleared or process restarts.
        Monitor memory usage; consider TTL or LRU eviction for long-running processes.

    Example:
        >>> cache = Cache()
        >>> cache.set("key", "value", ttl=60)  # Expires after 60 seconds
        >>> value = cache.get("key")  # Returns "value" or None if expired
    """

    def __init__(self):
        self._data: dict[str, tuple[Any, float]] = {}  # (value, expiry_timestamp)
```

#### Mistake 6: Exception Docstrings Without Handling Guidance

**Anti-Pattern:**
```python
class DatabaseError(Exception):
    """Database error."""  # [FAIL] What causes it? How to handle?
```

**Correct:**
```python
class DatabaseError(Exception):
    """Raised when database operations fail due to connectivity or query errors.

    Common Triggers:
        - Connection timeout (database unreachable)
        - Invalid SQL syntax in query
        - Constraint violations (unique key, foreign key)
        - Insufficient privileges for operation
        - Database server out of disk space

    Handling:
        For transient errors (connection timeout, deadlock), retry with exponential backoff.
        For permanent errors (syntax, privileges), log error and notify operations team.
        Do NOT retry for constraint violations; these indicate data/logic bugs.

    Example:
        >>> try:
        ...     db.execute("INSERT INTO users ...")
        ... except DatabaseError as e:
        ...     if "timeout" in str(e).lower():
        ...         retry_with_backoff()
        ...     else:
        ...         logger.error(f"Permanent DB error: {e}")
        ...         raise
    """
```

### Prevention Strategies

1. **Code Review Checklist** - Add docstring quality items:
   - [ ] Side effects documented?
   - [ ] Performance characteristics noted for slow operations (>1s)?
   - [ ] Thread safety explicit?
   - [ ] Preconditions listed?
   - [ ] Arguments describe semantics, not just types?

2. **Pre-Commit Hook** - Add custom validation:
   ```python
   # Check for common anti-patterns
   MINIMAL_PATTERNS = [
       r'""".*\."""$',  # One-liner with no details
       r'"""Get |"""Set ',  # Getter/setter without context
   ]
   ```

3. **Documentation Review** - Periodic audit:
   - Sample 10 random functions
   - Check against quality standards
   - Update docstrings to match current code behavior

## 6. Docstring Semantic Depth Checklist

Use this checklist when writing or reviewing docstrings to ensure semantic value beyond syntax compliance.

### For Module Docstrings

- [ ] **Purpose**: Why does this module exist? What problem does it solve?
- [ ] **Architecture**: How does it fit in the overall system?
- [ ] **Public API**: What are the main entry points developers will use?
- [ ] **Side Effects**: Does it modify global state, spawn processes, make network calls?
- [ ] **Environment**: Does it read environment variables or require external services?
- [ ] **Thread Safety**: Can this module be used safely across multiple threads?
- [ ] **Example**: Show realistic usage of the module's main functionality

### For Function/Method Docstrings

- [ ] **Purpose**: What does this function accomplish? (Not just "what" but "why")
- [ ] **Args Semantics**: Describe meaning, constraints, units, valid ranges (not just types)
- [ ] **Returns Semantics**: Describe what's in the return value, when it's None/empty
- [ ] **Preconditions**: What must be true before calling? (auth, connection, file exists, etc.)
- [ ] **Side Effects**: List ALL:
  - [ ] File I/O (reads/writes, where, overwrite behavior)
  - [ ] Database operations (queries, mutations, transactions)
  - [ ] Network calls (APIs, services, timeouts)
  - [ ] Subprocess execution (commands, signals, environment)
  - [ ] State mutations (global vars, class attributes, caches)
  - [ ] Console output (logging, printing, progress)
- [ ] **Performance**: For operations >1 second:
  - [ ] Typical execution time
  - [ ] What factors affect performance (data size, network, disk I/O)
  - [ ] Blocking behavior (synchronous, async, background)
- [ ] **Concurrency**: For functions accessing shared state:
  - [ ] Thread-safe? Reentrant? Async-safe?
  - [ ] Locks required? Race conditions possible?
- [ ] **Error Handling**: For each exception:
  - [ ] What triggers this exception? (Concrete scenarios)
  - [ ] Should callers retry? How?
  - [ ] What recovery actions are possible?
- [ ] **Example**: Show realistic usage with expected output

### For Class Docstrings

- [ ] **Purpose**: What abstraction does this class represent?
- [ ] **Lifecycle**: How to construct? When to destroy? Resource cleanup?
- [ ] **State Management**: What state does it maintain? When is it valid?
- [ ] **Thread Safety**: Safe for concurrent use? Requires synchronization?
- [ ] **Key Methods**: List 3-5 most important methods with one-line descriptions
- [ ] **Side Effects**: What system resources does it use? (files, network, memory)
- [ ] **Example**: Show construction, typical operations, cleanup

### For Dataclass/Model Docstrings

- [ ] **Purpose**: What data does this represent? (Business concept, not technical structure)
- [ ] **Field Semantics**: For each field:
  - [ ] What does it mean? (Not just type)
  - [ ] Constraints? (range, format, uniqueness)
  - [ ] Optional or required? Default behavior?
  - [ ] Units? (seconds vs milliseconds, bytes vs KB)
- [ ] **Validation**: What validation rules apply?
- [ ] **Relationships**: Does it reference other models? How?
- [ ] **Example**: Show construction and common field values

### For Exception Docstrings

- [ ] **Triggers**: List 3-5 concrete scenarios that raise this exception
- [ ] **Error Categories**: Transient (retry) vs permanent (fix code) vs user error (validate input)
- [ ] **Handling Strategy**: Should callers retry? Log? Re-raise? Ignore?
- [ ] **Recovery**: What actions can resolve this error?
- [ ] **Example**: Show try/except with appropriate handling

## Python Docs & Comments Plan
- Style: Google | NumPy
- Ruff: select includes D; convention set to style
- Scope: Public APIs fully documented; comments updated for intent

## Changes
- Update pyproject ruff config
- Add/repair docstrings
- Remove commented-out code
```
