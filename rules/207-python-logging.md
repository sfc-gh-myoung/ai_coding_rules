# Python Logging Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** logging, Python logging, logger, handlers, formatters, log levels, WebLogHandler, Rich console, SSE streaming, structured logging, operation ID, thread safety, log hierarchy, log propagation
**TokenBudget:** ~2000
**ContextTier:** High
**Depends:** rules/200-python-core.md

## Purpose

Establish best practices for Python logging in applications that require both CLI output (Rich console) and web UI log streaming (SSE/WebSocket), ensuring consistent logging patterns, proper handler configuration, and avoiding common pitfalls like duplicate logs.

## Rule Scope

Python applications using the `logging` module, especially those with dual output requirements (CLI and web UI)

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use Python `logging` module** - never `print()` for operational messages
- **Bridge Rich console to logger** - emit to both console AND logger for web UI capture
- **Use hierarchical logger names** - `app.module.submodule` enables selective handler attachment
- **Attach handlers at runtime** - add/remove WebLogHandler during operations, not globally
- **Prefix SUCCESS messages** - use `"SUCCESS: {message}"` pattern since Python has no SUCCESS level
- **Include operation IDs** - tag logs with operation context for filtering in web UI

**Pre-Execution Checklist:**
- [ ] Logger uses hierarchical naming (`app.module`)
- [ ] No `print()` statements for operational messages
- [ ] Console functions bridge to Python logger
- [ ] WebLogHandler attached only during operation execution
- [ ] SUCCESS messages use consistent prefix pattern
- [ ] Thread safety considered for custom handlers

## Contract

<contract>
<inputs_prereqs>
Python 3.11+; logging module; Rich console (optional); web framework with SSE support (optional)
</inputs_prereqs>

<mandatory>
Use `logging.getLogger()` with hierarchical names; bridge console output to logger; attach handlers at appropriate scope
</mandatory>

<forbidden>
Using `print()` for operational messages; global handler attachment causing duplicate logs; bare `except` swallowing log errors
</forbidden>

<steps>
1. Define logger with hierarchical name at module level
2. Create console output functions that also emit to logger
3. Implement WebLogHandler for SSE streaming (if web UI needed)
4. Attach WebLogHandler only during operation execution
5. Remove handler after operation completes to prevent duplicates
6. Use operation IDs for log filtering and correlation
</steps>

<output_format>
Python code with logging configuration, handler implementations, and usage examples
</output_format>

<validation>
- Logs appear in both CLI and web UI
- No duplicate log entries
- SUCCESS messages render with correct styling
- Operation filtering works correctly
</validation>

<design_principles>
- Use Python's logging module as the single source of truth for operational messages
- Bridge Rich console output to logging for dual-output scenarios
- Attach handlers at the narrowest scope needed (operation-level, not global)
- Use hierarchical logger names to enable selective capture
- Include structured context (operation IDs) for filtering and correlation
</design_principles>

</contract>

## Key Principles

### Logger Hierarchy and Propagation

Python loggers form a hierarchy based on dot-separated names. A handler attached to `"app"` captures logs from `"app.module"` and `"app.module.submodule"`:

```python
# Module-level logger definition
import logging

logger = logging.getLogger("demo_manager.operations")  # Child of "demo_manager"

# Handler attached to parent captures all children
handler = WebLogHandler()
parent_logger = logging.getLogger("demo_manager")
parent_logger.addHandler(handler)  # Captures demo_manager.* logs
```

### Bridging Rich Console to Logger

When using Rich for CLI output, bridge to the logger for web UI capture:

```python
import logging
from rich.console import Console

logger = logging.getLogger("app.operations")
console = Console()

def log_info(message: str) -> None:
    """Output to both Rich console and Python logger."""
    console.print(f"ℹ️  {message}", style="blue")
    logger.info(message)

def log_success(message: str) -> None:
    """Output success with prefix for web UI detection."""
    console.print(f"✓ {message}", style="green")
    logger.info(f"SUCCESS: {message}")  # Prefix enables SUCCESS level mapping

def log_error(message: str) -> None:
    """Output error to both outputs."""
    console.print(f"✗ {message}", style="red")
    logger.error(message)
```

### WebLogHandler for SSE Streaming

Custom handler that bridges Python logging to web UI:

```python
class WebLogHandler(logging.Handler):
    """Handler that sends logs to SSE stream."""

    def __init__(self, operation_id: str | None = None):
        super().__init__()
        self.operation_id = operation_id

    def emit(self, record: logging.LogRecord) -> None:
        message = record.getMessage()

        # Detect SUCCESS prefix from log_success()
        if message.startswith("SUCCESS: "):
            level = "SUCCESS"
            message = message[9:]
        else:
            level_map = {"INFO": "INFO", "WARNING": "WARNING", "ERROR": "ERROR"}
            level = level_map.get(record.levelname, "INFO")

        add_to_sse_stream(level, message, self.operation_id)
```

### Operation-Scoped Handler Attachment

Attach handlers only during operation execution to prevent duplicate logs:

```python
def execute_operation(operation_id: str, operation_type: str):
    """Execute operation with scoped log handler."""
    handler = WebLogHandler(operation_id)
    handler.setLevel(logging.INFO)
    logger = logging.getLogger("demo_manager")
    logger.addHandler(handler)

    try:
        # Execute operation - all log_info/log_success calls captured
        result = run_operation(operation_type)
    finally:
        # Always remove handler to prevent duplicates on next operation
        logger.removeHandler(handler)
```

### Web Application Logging Patterns

For web applications with SSE-based log streaming:

**SSE Log Publishing Function:**

```python
from datetime import datetime, UTC

def add_log(level: str, message: str, operation_id: str | None = None) -> None:
    """Publish log entry to SSE logs channel.

    Args:
        level: Log level (INFO, WARNING, ERROR, SUCCESS)
        message: Log message text
        operation_id: Optional operation ID for filtering
    """
    log_entry = {
        "level": level,
        "message": message,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if operation_id:
        log_entry["operation_id"] = operation_id

    publish_to_sse_channel("logs", "log", log_entry)
```

**Thread-Safe Publishing from Background Tasks:**

When publishing logs from `asyncio.to_thread()` or background threads:

```python
async def status_stream(demo_id: str):
    """Stream status with logs to both SSE and Live Logs."""
    # CRITICAL: Capture event loop BEFORE entering thread pool
    main_loop = asyncio.get_running_loop()
    operation_id = f"status-{demo_id[:8]}"

    def progress_callback(step: str, message: str) -> None:
        """Thread-safe callback from background thread."""
        # Publish to Live Logs (with operation_id for filtering)
        add_log("INFO", message, operation_id)
        # Use call_soon_threadsafe for async queue operations
        main_loop.call_soon_threadsafe(queue.put_nowait, (step, message))

    # Run blocking operation in thread pool
    result = await asyncio.to_thread(
        check_status, callback=progress_callback
    )
```

**Operation Context Logging:**

Include `operation_id` in logs for correlation and filtering:

```python
# Generate consistent operation IDs
operation_id = f"status-{demo_id[:8]}"  # For status checks
operation_id = str(uuid.uuid4())[:8]    # For general operations

# Include in all log calls during operation
add_log("INFO", "Starting database check...", operation_id)
add_log("SUCCESS", "Database connection verified", operation_id)
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using print() for Operational Messages**
```python
# Bad: print() not captured by logging handlers
def process_data():
    print("Processing started...")  # Lost to web UI
    result = do_work()
    print(f"Processed {len(result)} items")  # Lost to web UI
```
**Problem:** `print()` bypasses logging entirely; web UI never sees these messages.

**Correct Pattern:**
```python
def process_data():
    log_info("Processing started...")  # Captured by WebLogHandler
    result = do_work()
    log_success(f"Processed {len(result)} items")  # Shows as SUCCESS in web UI
```


**Anti-Pattern 2: Global Handler Attachment**
```python
# Bad: Handler attached at module import time
handler = WebLogHandler()
logging.getLogger("app").addHandler(handler)  # Attached forever

def operation_a():
    log_info("Operation A")  # Logged once

def operation_b():
    log_info("Operation B")  # Also logged, but handler from A still attached
```
**Problem:** Handler accumulates, causing duplicate logs or wrong operation IDs.

**Correct Pattern:**
```python
def run_with_handler(operation_id: str, func):
    handler = WebLogHandler(operation_id)
    logger = logging.getLogger("app")
    logger.addHandler(handler)
    try:
        return func()
    finally:
        logger.removeHandler(handler)  # Clean removal
```


**Anti-Pattern 3: Duplicate Logging (Console + Logger)**
```python
# Bad: Both console function and explicit logger call
def deploy_app():
    log_info("Deploying...")  # Already emits to logger
    logger.info("Deploying...")  # Duplicate!
```
**Problem:** Same message appears twice in logs.

**Correct Pattern:**
```python
def deploy_app():
    log_info("Deploying...")  # Single call handles both console and logger
```

## Post-Execution Checklist

- [ ] All operational messages use `log_info/success/warning/error`, not `print()`
- [ ] Logger names follow hierarchical pattern (`app.module.submodule`)
- [ ] Console output functions bridge to Python logger
- [ ] WebLogHandler attached only during operation scope
- [ ] Handler removed in `finally` block to prevent leaks
- [ ] SUCCESS messages use `"SUCCESS: "` prefix for level detection
- [ ] Operation IDs included for log filtering
- [ ] No duplicate logger calls alongside console functions
- [ ] Thread safety verified for custom handlers

## Validation

**Success Checks:**
- CLI shows Rich-formatted output with icons and colors
- Web UI Live Logs panel shows all operational messages
- SUCCESS messages display with green styling in web UI
- Operation filtering correctly isolates logs by operation ID
- No duplicate entries in log stream

**Negative Tests:**
- `print()` statements do not appear in web UI logs
- Removing handler prevents logs from appearing in SSE stream
- Multiple operations do not cross-contaminate log streams

## Output Format Examples

```python
# Module: utils/console.py
"""Console output with logging bridge."""

import logging
from rich.console import Console

logger = logging.getLogger("demo_manager.operations")
console = Console()

def log_info(message: str) -> None:
    """Print info and emit to logger for web UI capture."""
    console.print(f"ℹ️  {message}", style="blue")
    logger.info(message)

def log_success(message: str) -> None:
    """Print success and emit with SUCCESS prefix."""
    console.print(f"✓ {message}", style="green")
    logger.info(f"SUCCESS: {message}")

def log_warning(message: str) -> None:
    """Print warning and emit to logger."""
    console.print(f"⚠️  {message}", style="yellow")
    logger.warning(message)

def log_error(message: str) -> None:
    """Print error and emit to logger."""
    console.print(f"✗ {message}", style="red")
    logger.error(message)
```

```python
# Module: web/routes/operations.py
"""Operation execution with scoped logging."""

import logging
from web.routes.logs import WebLogHandler

def execute_operation(operation_id: str, operation_type: str):
    handler = WebLogHandler(operation_id)
    handler.setLevel(logging.INFO)
    op_logger = logging.getLogger("demo_manager")
    op_logger.addHandler(handler)

    try:
        # All log_* calls now captured for this operation
        result = run_manager_operation(operation_type)
        return result
    finally:
        op_logger.removeHandler(handler)
```

## References

### External Documentation
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html) - Official logging tutorial
- [Python Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html) - Advanced patterns
- [Rich Console Documentation](https://rich.readthedocs.io/en/stable/console.html) - Rich console output

### Related Rules

- **Python Core**: `rules/200-python-core.md` - Foundation for Python development
- **FastAPI Monitoring**: `rules/210d-python-fastapi-monitoring.md` - Health checks and logging patterns
- **Snowflake Observability**: `rules/111a-snowflake-observability-logging.md` - Snowflake logging patterns
- **SSE Patterns**: `rules/221g-python-htmx-sse.md` - Server-Sent Events with log streaming
