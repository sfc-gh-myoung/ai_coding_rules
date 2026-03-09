# Python Typer CLI Rich Integration

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Typer, Rich, console output, progress bars, Live display, color detection, stderr, dual console
**TokenBudget:** ~1900
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
