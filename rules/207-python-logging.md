# Python Logging Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** logging, Python logging, logger, handlers, formatters, log levels, WebLogHandler, Rich console, SSE streaming, structured logging, operation ID, thread safety, log hierarchy, log propagation
**TokenBudget:** ~2900
**ContextTier:** High
**Depends:** 200-python-core.md

## Scope

**What This Rule Covers:**
Best practices for Python logging in applications with dual output requirements (CLI and web UI), covering hierarchical logger names, handler configuration, Rich console integration, SSE/WebSocket streaming, structured logging, operation IDs, thread safety, and avoiding duplicate logs.

**When to Load This Rule:**
- Setting up logging for Python applications
- Integrating Rich console with Python logging
- Implementing web UI log streaming (SSE/WebSocket)
- Troubleshooting duplicate log entries
- Adding operation IDs for log correlation
- Configuring handlers and formatters
- Debugging log propagation issues

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Python foundation patterns

**Related:**
- **201-python-lint-format.md** - Code quality standards
- **210-python-fastapi-core.md** - FastAPI SSE streaming patterns

### External Documentation

- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html) - Official logging guide
- [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html) - Advanced logging patterns
- [Rich Logging Handler](https://rich.readthedocs.io/en/stable/logging.html) - Rich console integration

## Contract

### Inputs and Prerequisites

- Python 3.11+ codebase
- logging module (standard library)
- Optional: Rich console for CLI output
- Optional: Web framework with SSE support for streaming

### Mandatory

- **Use Python `logging` module** - never `print()` for operational messages
- **Bridge Rich console to logger** - emit to both console AND logger for web UI capture
- **Use hierarchical logger names** - `app.module.submodule` enables selective handler attachment
- **Attach handlers at runtime** - add/remove WebLogHandler during operations, not globally
- **Prefix SUCCESS messages** - use `"SUCCESS: {message}"` pattern since Python has no SUCCESS level
- **Include operation IDs** - tag logs with operation context for filtering in web UI

### Forbidden

- Using `print()` for operational messages
- Global handler attachment causing duplicate logs
- Bare `except` swallowing log errors
- Modifying root logger configuration in libraries

### Execution Steps

1. Define logger with hierarchical name at module level
2. Create console output functions that also emit to logger
3. Implement WebLogHandler for SSE streaming (if web UI needed)
4. Attach WebLogHandler only during operation execution
5. Remove handler after operation completes to prevent duplicates
6. Use operation IDs for log filtering and correlation

### Output Format

Logging implementations produce:
- Logger configuration with hierarchical names
- Handler implementations (console, web, file)
- Formatter definitions for structured output
- Usage examples for common patterns

### Validation

**Pre-Task-Completion Checks:**
- [ ] Logger uses hierarchical naming (`app.module`)
- [ ] No `print()` statements for operational messages
- [ ] Console functions bridge to Python logger
- [ ] WebLogHandler attached only during operation execution
- [ ] SUCCESS messages use consistent prefix pattern
- [ ] Thread safety considered for custom handlers

**Success Criteria:**
- Logs appear in both CLI and web UI
- No duplicate log entries
- SUCCESS messages render with correct styling
- Operation IDs enable log filtering
- Thread-safe handler operations

**Negative Tests:**
- Handlers should not leak between operations
- Duplicate handlers should be detected and prevented
- Log levels should filter appropriately

### Design Principles

- **Hierarchical naming:** Use dot-separated logger names for selective configuration
- **Handler isolation:** Attach handlers at operation scope, not globally
- **Bridge patterns:** Connect Rich console to Python logging for dual output
- **Structured logging:** Include operation IDs and context for filtering
- **Thread safety:** Ensure custom handlers are thread-safe

### Post-Execution Checklist

- [ ] Logger uses hierarchical naming (`app.module`)
- [ ] No `print()` statements for operational messages
- [ ] Console functions bridge to Python logger
- [ ] WebLogHandler attached only during operation execution
- [ ] SUCCESS messages use consistent prefix pattern
- [ ] Thread safety considered for custom handlers
- [ ] Operation IDs included for log correlation
- Operation filtering works correctly

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
