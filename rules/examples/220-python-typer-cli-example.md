# 220 Example: Typer CLI (Python)

> **EXAMPLE FILE** - Reference implementation for `220-python-typer-cli.md`
> Not a rule file. Not validated against rule-schema.yml.

## Context

**Parent Rule:** 220-python-typer-cli.md
**Demonstrates:** Complete Typer CLI application with shared console module, dual console pattern (stdout/stderr), subcommand registration, Rich Table and Live progress displays, and CliRunner testing
**Use When:** Building CLI applications with Typer that need consistent output styling, progress displays, and testable command structure
**Version:** 1.0
**Last Validated:** 2026-03-08

## Prerequisites

- [ ] Python 3.10+ installed
- [ ] uv installed for dependency management
- [ ] pyproject.toml present at project root
- [ ] Typer and Rich packages available

## Implementation

### Project Structure

```
myapp/
├── pyproject.toml
├── myapp/
│   ├── __init__.py
│   ├── _shared/
│   │   ├── __init__.py
│   │   └── console.py          # Centralized Rich console
│   └── cli/
│       ├── __init__.py
│       ├── main.py             # Main app entry point
│       └── commands/
│           ├── __init__.py
│           └── data.py         # Data subcommands
└── tests/
    └── cli/
        └── test_commands.py    # CliRunner tests
```

### Shared Console Module

```python
# myapp/_shared/console.py
"""Centralized console output for consistent CLI styling."""
import os
import sys

from rich.console import Console
from rich.table import Table
from rich.live import Live

__all__ = [
    "log_info",
    "log_success", 
    "log_error",
    "log_warning",
    "get_console",
    "get_error_console",
    "create_table",
    "create_live",
]


def _should_use_color() -> bool:
    """Determine if console should use colors based on environment.
    
    Checks (in order):
    - NO_COLOR env var: Standard convention (https://no-color.org/)
    - CI env var: Disable colors in CI for clean logs
    - TERM=dumb: Terminal has no capabilities
    - pytest in sys.modules: Running under pytest (preserves pytest's own colors)
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("CI"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    if "pytest" in sys.modules:
        return False
    return True


# Configure consoles with environment-aware color detection
_use_color = _should_use_color()
_stdout = Console(no_color=not _use_color, force_terminal=_use_color)
_stderr = Console(stderr=True, no_color=not _use_color, force_terminal=_use_color)


def log_info(msg: str) -> None:
    """Info message to stdout."""
    _stdout.print(f"[blue]ℹ[/blue] {msg}")


def log_success(msg: str) -> None:
    """Success message to stdout."""
    _stdout.print(f"[green]✓[/green] {msg}")


def log_error(msg: str) -> None:
    """Error message to stderr."""
    _stderr.print(f"[red]✗[/red] {msg}")


def log_warning(msg: str) -> None:
    """Warning message to stderr."""
    _stderr.print(f"[yellow]![/yellow] {msg}")


def get_console() -> Console:
    """Get stdout console for tables, progress, etc."""
    return _stdout


def get_error_console() -> Console:
    """Get stderr console for error output."""
    return _stderr


def create_table(title: str, columns: list[str]) -> Table:
    """Create a styled table with standard formatting."""
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for col in columns:
        table.add_column(col)
    return table


def create_live(renderable, **kwargs) -> Live:
    """Create a Live display with standard settings."""
    return Live(renderable, console=_stdout, refresh_per_second=4, **kwargs)
```

### Main CLI Application

```python
# myapp/cli/main.py
"""Main CLI application entry point."""
import typer
from importlib.metadata import version
from typing_extensions import Annotated

from myapp._shared.console import get_console, log_info
from myapp.cli.commands import data

app = typer.Typer(
    name="myapp",
    help="Example CLI application with Rich integration.",
    add_completion=True,
    rich_markup_mode="rich",
)

# Register subcommands
app.add_typer(data.app, name="data", help="Data processing commands")

console = get_console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"myapp version {version('myapp')}")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable verbose output")
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version", callback=version_callback, is_eager=True, help="Show version"
        ),
    ] = False,
):
    """
    Example CLI application demonstrating Typer + Rich patterns.

    Use --help with any command for more information.
    """
    # Initialize context state
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

    if verbose:
        log_info("Verbose mode enabled")


if __name__ == "__main__":
    app()
```

### Subcommand Module with Rich Table and Live

```python
# myapp/cli/commands/data.py
"""Data processing commands with Rich output."""
import time
from enum import Enum
from pathlib import Path

import typer
from typing_extensions import Annotated

from myapp._shared.console import (
    create_live,
    create_table,
    get_console,
    log_error,
    log_info,
    log_success,
)

app = typer.Typer()
console = get_console()


class OutputFormat(str, Enum):
    """Supported output formats."""

    json = "json"
    csv = "csv"
    yaml = "yaml"


@app.command()
def list_items(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option("--limit", "-l", min=1, max=100)] = 10,
):
    """List items in a Rich table."""
    if ctx.obj.get("verbose"):
        log_info(f"Listing up to {limit} items")

    # Sample data
    items = [{"id": i, "name": f"Item {i}", "status": "active"} for i in range(1, limit + 1)]

    table = create_table("Items", ["ID", "Name", "Status"])
    for item in items:
        table.add_row(str(item["id"]), item["name"], f"[green]{item['status']}[/green]")

    console.print(table)
    log_success(f"Listed {len(items)} items")


@app.command()
def export(
    input_file: Annotated[Path, typer.Argument(help="Input file to export", exists=True)],
    output_file: Annotated[Path, typer.Option("--output", "-o", help="Output file")] = None,
    format: Annotated[OutputFormat, typer.Option("--format", "-f", help="Output format")] = OutputFormat.json,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be done")] = False,
):
    """Export data to specified format."""
    if dry_run:
        log_info(f"[DRY RUN] Would export {input_file} to {format.value}")
        return

    output = output_file or input_file.with_suffix(f".{format.value}")

    log_info(f"Exporting {input_file} to {output}")
    # Export logic here...
    log_success(f"Exported to {output}")


@app.command()
def sync(
    items: Annotated[list[str], typer.Argument(help="Items to sync")],
):
    """Sync items with live progress display."""
    if not items:
        log_error("No items provided")
        raise typer.Exit(1)

    status = {item: "pending" for item in items}

    def make_table():
        table = create_table("Sync Progress", ["Item", "Status"])
        for item, state in status.items():
            colors = {
                "pending": "dim",
                "syncing": "yellow",
                "done": "green",
                "failed": "red",
            }
            table.add_row(item, f"[{colors[state]}]{state}[/{colors[state]}]")
        return table

    with create_live(make_table()) as live:
        for item in items:
            status[item] = "syncing"
            live.update(make_table())

            # Simulate sync work
            time.sleep(0.5)

            # Mark as done (in real code, handle failures)
            status[item] = "done"
            live.update(make_table())

    done_count = sum(1 for s in status.values() if s == "done")
    log_success(f"Synced {done_count}/{len(items)} items")
```

### pyproject.toml Configuration

```toml
[project]
name = "myapp"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "typer[all]>=0.9.0",
]

[project.scripts]
myapp = "myapp.cli.main:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### CliRunner Tests

```python
# tests/cli/test_commands.py
"""CLI command tests using CliRunner."""
import pytest
from typer.testing import CliRunner

from myapp.cli.main import app

# CRITICAL: NO_COLOR and TERM=dumb prevent ANSI escape codes in test output
# Without these, assertions fail: "--dry-run" not in "\x1b[1m-\x1b[0m\x1b[1m-dry..."
runner = CliRunner(env={"NO_COLOR": "1", "TERM": "dumb"})


class TestMainApp:
    """Test main app functionality."""

    def test_help(self):
        """Test help displays correctly."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Example CLI application" in result.stdout

    def test_verbose_flag(self):
        """Test verbose flag is recognized."""
        result = runner.invoke(app, ["--verbose", "data", "list-items"])
        assert result.exit_code == 0
        assert "Verbose mode enabled" in result.stdout


class TestDataCommands:
    """Test data subcommands."""

    def test_list_items_default(self):
        """Test list-items with default limit."""
        result = runner.invoke(app, ["data", "list-items"])
        assert result.exit_code == 0
        assert "Items" in result.stdout  # Table title

    def test_list_items_with_limit(self):
        """Test list-items with custom limit."""
        result = runner.invoke(app, ["data", "list-items", "--limit", "5"])
        assert result.exit_code == 0
        assert "Listed 5 items" in result.stdout

    def test_export_dry_run(self, tmp_path):
        """Test export with dry run."""
        input_file = tmp_path / "data.txt"
        input_file.write_text("test data")

        result = runner.invoke(
            app, ["data", "export", str(input_file), "--dry-run"]
        )
        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout

    def test_export_missing_file(self):
        """Test export with non-existent file."""
        result = runner.invoke(app, ["data", "export", "nonexistent.txt"])
        assert result.exit_code != 0

    def test_sync_no_items(self):
        """Test sync with no items fails."""
        result = runner.invoke(app, ["data", "sync"])
        assert result.exit_code != 0


class TestEnumValidation:
    """Test enum option validation."""

    def test_export_valid_format(self, tmp_path):
        """Test export with valid format."""
        input_file = tmp_path / "data.txt"
        input_file.write_text("test")

        result = runner.invoke(
            app, ["data", "export", str(input_file), "--format", "csv", "--dry-run"]
        )
        assert result.exit_code == 0

    def test_export_invalid_format(self, tmp_path):
        """Test export with invalid format fails."""
        input_file = tmp_path / "data.txt"
        input_file.write_text("test")

        result = runner.invoke(
            app, ["data", "export", str(input_file), "--format", "invalid"]
        )
        assert result.exit_code != 0
        # Typer provides helpful error about valid choices
```

### Usage Examples

```bash
# Install in development mode
uv sync

# Show help
myapp --help
myapp data --help

# List items with table output
myapp data list-items
myapp data list-items --limit 5

# Export with format validation
myapp data export data.json --format csv --dry-run
myapp data export data.json --output exported.csv --format csv

# Sync with live progress
myapp data sync item1 item2 item3

# Verbose mode
myapp --verbose data list-items

# Pipe stdout (errors still visible on stderr)
myapp data list-items 2>/dev/null | jq .
```

## Validation

```bash
# Verify help displays correctly
myapp --help

# Test subcommand help
myapp data --help

# Verify list-items works with Rich table output
myapp data list-items --limit 3

# Verify verbose mode
myapp --verbose data list-items --limit 2

# Run pytest tests
uv run pytest tests/cli/test_commands.py -v
```

**Expected Results:**
- `myapp --help` displays application help with Rich formatting
- `myapp data --help` shows data subcommand options
- `myapp data list-items --limit 3` displays a Rich table with 3 items
- `myapp --verbose data list-items` shows "Verbose mode enabled" before output
- All pytest tests pass with exit code 0
