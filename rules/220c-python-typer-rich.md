# Python Typer CLI Rich Integration

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Typer, Rich, console output, progress bars, Live display, color detection, stderr, dual console
**TokenBudget:** ~3450
**ContextTier:** Medium
**Depends:** 220-python-typer-cli.md
**LoadTrigger:** kw:rich, kw:console, kw:progress-bar

## Scope

**What This Rule Covers:**
Rich library integration with Typer CLI applications including shared console patterns, dual console (stdout/stderr), Live progress displays, color detection, and context object state management.

**When to Load This Rule:**
- Adding Rich output formatting to a Typer CLI
- Implementing progress bars or Live displays
- Setting up shared console modules
- Handling color detection for CI and testing environments

## References

### Dependencies

**Must Load First:**
- **220-python-typer-cli.md** - Core Typer CLI patterns

**Related:**
- **220b-python-typer-testing.md** - Testing with ANSI suppression

## Contract

### Inputs and Prerequisites

- Typer CLI application (from 220-python-typer-cli.md)
- Rich installed (included with `typer[all]`)

### Mandatory

- **Critical:** Use a shared console module; never create Console instances in individual commands
- **Always:** Separate stdout (data) from stderr (status/progress)
- **Rule:** Detect color support from environment (NO_COLOR, CI, TERM, pytest)
- **Always:** Use context objects for state passing between callbacks and commands

### Forbidden

- Creating multiple Console instances in different modules (use shared module)
- Mixing data output and status messages on the same stream
- Hardcoding color settings without environment detection

### Execution Steps

1. Create shared console module with environment-aware color detection
2. Set up dual console pattern (stdout for data, stderr for status)
3. Implement logging helpers (info, success, error, warning)
4. Wire context object for state passing
5. Add progress/Live display patterns as needed

### Output Format

Shared console module with environment-aware output, dual stream support, and Rich formatting utilities.

### Validation

**Pre-Task-Completion Checks:**
- [ ] Single shared console module created
- [ ] Color detection respects NO_COLOR, CI, TERM, pytest
- [ ] stdout used for data, stderr for status
- [ ] Context objects pass state between commands

**Negative Tests:**
- Console with `NO_COLOR=1` set (should produce unformatted output)
- Multiple Console instances (should trigger linting/review warning)

### Design Principles

- **Single Source:** One console module, shared across all commands
- **Stream Separation:** Data on stdout, status on stderr
- **Environment Awareness:** Respect NO_COLOR, CI, TERM conventions

> **Investigation Required**
> Before creating or modifying Rich console patterns, the agent MUST:
> 1. Check for existing `console.py` or shared console modules — never create a second one
> 2. Search for existing Rich imports (`from rich` or `import rich`) across the project
> 3. Verify whether `typer[all]` or bare `typer` + `rich` is installed: `uv pip list | grep -i rich`
> 4. Read existing stderr/stdout patterns to maintain consistent stream separation
> 5. Check if `NO_COLOR` or `TERM` environment handling already exists in the project

### Post-Execution Checklist

- [ ] Shared console module with color detection
- [ ] Dual console pattern (stdout/stderr)
- [ ] Helper functions for log levels
- [ ] Context objects for state passing
- [ ] Progress displays use stderr

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: String Options Without Enum Constraints

**Problem:** Using plain string parameters for options that have a fixed set of valid values. Users get no tab completion and invalid values pass silently.

```python
# BAD: No validation on format values
@app.command()
def export(format: str = "json"):
    if format not in ("json", "csv", "yaml"):  # Runtime check only
        raise typer.BadParameter(f"Unknown format: {format}")
```

**Correct Pattern:**
```python
from enum import Enum

class OutputFormat(str, Enum):
    json = "json"
    csv = "csv"
    yaml = "yaml"

@app.command()
def export(
    format: Annotated[OutputFormat, typer.Option(help="Output format")] = OutputFormat.json,
):
    # Typer validates automatically, provides tab completion
    console.print(f"Exporting as {format.value}")
```

### Anti-Pattern 2: Duplicate Console Instances

**Problem:** Creating Console instances in multiple modules causes inconsistent formatting and breaks color detection.

```python
# BAD: Console created in each module
# commands/data.py
console = Console()

# commands/auth.py
console = Console()  # Different instance, possibly different settings
```

**Correct Pattern:** Use a single shared console module (see Shared Console Module below).

### Anti-Pattern 3: Progress Output on stdout

**Problem:** Progress bars and status messages on stdout corrupt data output when piping.

```python
# BAD: Progress on stdout breaks piping
# myapp export | jq .  # Progress bars mixed into JSON
```

**Correct Pattern:** All progress and status output goes to stderr via the shared error console.

## Shared Console Module

### Environment-Aware Color Detection

```python
# src/myapp/_shared/console.py
"""Shared console for all CLI output. Import this module; do not create Console()."""

import os
import sys
from rich.console import Console

def _should_use_color() -> bool:
    """Detect whether the environment supports color output."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("CI"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    if "pytest" in sys.modules:
        return False
    return True

_use_color = _should_use_color()

_stdout = Console(no_color=not _use_color, force_terminal=_use_color)
_stderr = Console(stderr=True, no_color=not _use_color, force_terminal=_use_color)


def get_console() -> Console:
    """Get the stdout console for data output."""
    return _stdout


def get_error_console() -> Console:
    """Get the stderr console for status/progress output."""
    return _stderr


def log_info(msg: str) -> None:
    """Log informational message to stderr."""
    _stderr.print(f"[blue]INFO:[/blue] {msg}")


def log_success(msg: str) -> None:
    """Log success message to stderr."""
    _stderr.print(f"[green]OK:[/green] {msg}")


def log_error(msg: str) -> None:
    """Log error message to stderr."""
    _stderr.print(f"[red]ERROR:[/red] {msg}")


def log_warning(msg: str) -> None:
    """Log warning message to stderr."""
    _stderr.print(f"[yellow]WARN:[/yellow] {msg}")
```

### Rich Markup Escaping

User-provided strings may contain characters that Rich interprets as markup. Always escape untrusted input:

```python
from rich.markup import escape

def display_file_info(path: str, size: int) -> None:
    """Display file info — path may contain [brackets] or other Rich markup chars."""
    safe_path = escape(path)  # Escapes [, ], and other markup characters
    get_console().print(f"File: {safe_path} ({size:,} bytes)")


# BAD — user input interpreted as markup:
# path = "data/[backup]/report.csv"
# console.print(f"File: {path}")  # Rich tries to parse [backup] as a style tag

# GOOD — escaped input is safe:
# console.print(f"File: {escape(path)}")  # Displays literal [backup]
```

**When to escape:**
- File paths from user input or filesystem scans
- Database column names or values displayed in tables
- Any string not authored by the developer

**When escaping is NOT needed:**
- Hardcoded format strings with known Rich markup (e.g., `"[red]Error:[/red]"`)
- Enum values from a known set
- Numeric/boolean values converted to string

```python
from rich.table import Table
from rich.markup import escape

def display_results(results: list[dict[str, str]]) -> None:
    """Display results in a table — escape all user data."""
    table = Table(title="Search Results")
    table.add_column("Name", style="cyan")
    table.add_column("Path")
    table.add_column("Status", style="green")

    for r in results:
        table.add_row(
            escape(r["name"]),      # User data — escape
            escape(r["path"]),      # File path — escape
            r["status"],            # Known enum ("ok"/"error") — safe
        )
    get_console().print(table)
```

### Dual Console Usage in Commands

```python
from myapp._shared.console import get_console, get_error_console, log_info

console = get_console()       # Data output (stdout)
err_console = get_error_console()  # Status output (stderr)

@app.command()
def export(output: Path):
    """Export data. Status goes to stderr, data to stdout."""
    log_info(f"Exporting to {output}")       # stderr
    data = generate_export()
    console.print_json(data=data)            # stdout - pipeable
    log_info("Export complete")              # stderr
```

### File Output (No ANSI Codes)

When writing Rich-formatted output to a file, create a file-specific Console to strip ANSI codes:

```python
from pathlib import Path
from rich.console import Console
from rich.table import Table

def export_report(data: list[dict], output_path: Path) -> None:
    """Export report to file without ANSI escape codes."""
    table = Table(title="Report")
    table.add_column("Name")
    table.add_column("Value", justify="right")
    for row in data:
        table.add_row(row["name"], str(row["value"]))

    # File console — no_color=True strips all ANSI, width prevents wrapping
    with open(output_path, "w") as f:
        file_console = Console(file=f, no_color=True, width=120)
        file_console.print(table)

    get_error_console().print(f"[green]✓[/green] Report saved to {output_path}")
```

**Key rules:**
- `no_color=True` ensures no ANSI codes in file output
- Set explicit `width=120` to prevent line wrapping based on terminal width
- This is the ONE exception to the "never create Console instances outside the shared module" rule — file-targeted Consoles are inherently single-use
- Always confirm file write to stderr, not stdout

## Context Object State Pattern

### Passing State Between Callback and Commands

```python
@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
):
    """Main entry point."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@app.command()
def process(ctx: typer.Context, input_file: Path):
    """Process a file."""
    verbose = ctx.obj.get("verbose", False)
    if verbose:
        log_info(f"Processing {input_file}")
```

## Live Progress Display

### Status Table with Live Updates

```python
from rich.live import Live
from rich.table import Table
from myapp._shared.console import get_error_console

def make_status_table(items: dict[str, str]) -> Table:
    """Build a status table for Live display."""
    table = Table(title="Sync Progress")
    table.add_column("Item")
    table.add_column("Status")
    for name, status in items.items():
        style = {"done": "green", "syncing": "yellow", "error": "red"}.get(status, "")
        table.add_row(name, status, style=style)
    return table

def sync_with_progress(items: list[str]) -> None:
    """Sync items with live progress display on stderr."""
    err_console = get_error_console()
    status = {item: "pending" for item in items}

    with Live(make_status_table(status), console=err_console, refresh_per_second=4) as live:
        for item in items:
            status[item] = "syncing"
            live.update(make_status_table(status))
            try:
                do_sync(item)
                status[item] = "done"
            except Exception:
                status[item] = "error"
            live.update(make_status_table(status))
```

### Simple Spinner with console.status()

For single-task operations where a Live table is overkill, use `console.status()`:

```python
from myapp._shared.console import get_error_console, get_console

def deploy_app(target: str) -> None:
    """Deploy with a simple spinner on stderr."""
    err = get_error_console()
    out = get_console()

    with err.status("[bold cyan]Deploying...[/bold cyan]") as status:
        # Phase 1
        status.update("[bold cyan]Building artifacts...[/bold cyan]")
        build_artifacts()

        # Phase 2
        status.update(f"[bold cyan]Uploading to {target}...[/bold cyan]")
        upload_to_target(target)

        # Phase 3
        status.update("[bold cyan]Running health checks...[/bold cyan]")
        run_health_checks(target)

    # Spinner clears automatically when context manager exits
    out.print(f"[green]✓[/green] Deployed to {target}")
```

**When to use `console.status()` vs `Live`:**

- **`console.status()`:** Use for single task with phases — simple spinner
- **`Live` + `Table`:** Use for multiple items with individual status tracking
- **`Progress`:** Use for known total with measurable progress (file downloads, batch processing)

**Key rules:**
- Always use `get_error_console()` for spinners — keeps stdout clean for piped data
- `status.update()` changes the spinner text for each phase
- Spinner auto-clears when the `with` block exits
- Works correctly with `NO_COLOR=1` — falls back to text-only status

### Table Column Overflow

For tables with potentially long strings, configure column overflow behavior:

```python
from rich.table import Table
from rich.markup import escape

def display_logs(entries: list[dict]) -> None:
    """Display log entries with overflow handling."""
    table = Table(title="Recent Logs", show_lines=True)
    table.add_column("Time", style="cyan", width=19, no_wrap=True)
    table.add_column("Level", style="bold", width=8, no_wrap=True)
    table.add_column("Message", overflow="fold", max_width=80)
    table.add_column("Source", overflow="ellipsis", max_width=30)

    for entry in entries:
        table.add_row(
            entry["time"],
            entry["level"],
            escape(entry["message"]),    # User data — escape
            escape(entry["source"]),     # File path — escape
        )
    get_console().print(table)
```

**Overflow modes:**

- **`"fold"`:** Wraps text to next line within cell — use for log messages, descriptions
- **`"ellipsis"`:** Truncates with `…` — use for file paths, identifiers
- **`"crop"`:** Hard truncates (no indicator) — rarely use, prefer ellipsis instead

**Key rules:**
- Use `no_wrap=True` for fixed-width columns (timestamps, status codes)
- Use `max_width` to cap column width for variable-length content
- Use `overflow="ellipsis"` for paths and identifiers that can be truncated
- Use `overflow="fold"` for content the user needs to read fully
- Always `escape()` user-provided data in table cells
