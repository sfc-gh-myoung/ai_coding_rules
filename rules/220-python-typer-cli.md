# Python Typer CLI Development Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v4.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Typer, CLI development, command-line interface, click, argument parsing, typer.Argument, typer.Option, rich console, exit codes
**TokenBudget:** ~3500
**ContextTier:** High
**Depends:** 200-python-core.md
**LoadTrigger:** kw:typer, kw:cli

## Scope

**What This Rule Covers:**
Core guidance for building robust command-line applications using Typer, covering project setup, argument handling, command definitions, error handling, and packaging.

**When to Load This Rule:**
- Python CLI development, command-line applications
- Setting up Typer project structure
- Defining commands with proper arguments and options
- Implementing error handling with exit codes

## References

### Dependencies

**Must Load First:**
- **200-python-core.md** - Core Python patterns and uv usage

**Related:**
- **220a-python-typer-config.md** - Configuration and environment management (Recommended)
- **220b-python-typer-testing.md** - CLI testing strategies (Recommended)
- **220c-python-typer-rich.md** - Rich integration and console patterns (Recommended)
- **201-python-lint-format.md** - Ruff linting and formatting standards
- **203-python-project-setup.md** - Python project structure and packaging
- **230-python-pydantic.md** - Pydantic integration with Typer
- **207-python-logging.md** - CLI apps needing Rich console + Python logger bridge

### External Documentation

- [Typer Documentation](https://typer.tiangolo.com/) - Modern CLI framework with automatic help generation
- [Rich Documentation](https://rich.readthedocs.io/) - Terminal styling, progress bars, and rich text rendering
- [Click Documentation](https://click.palletsprojects.com/) - Underlying CLI framework and advanced patterns

## Contract

### Inputs and Prerequisites

- Python project with `pyproject.toml` configured
- Understanding of CLI requirements and user workflows
- Knowledge of command-line argument patterns

### Mandatory

- **uv** for dependency management
- **typer[all]>=0.9.0** installed via `uv add "typer[all]"`
- Type annotations on all command parameters
- Console scripts configured in pyproject.toml
- Explicit exit codes for error conditions

### Forbidden

- Using argparse or click directly (use Typer instead)
- Hardcoded file paths without configuration options
- Missing exit codes (always exit 0)
- Skipping help text and documentation
- Mutable default values for command parameters

### Execution Steps

1. Install Typer with full features: `uv add "typer[all]"`
2. Create CLI module structure (cli/main.py, cli/commands/)
3. Define main Typer app with proper configuration
4. Implement commands with Annotated parameters for metadata
5. Add error handling with appropriate exit codes
6. Configure console scripts in pyproject.toml [project.scripts]
7. Write CLI tests using typer.testing.CliRunner (see 220b)
8. Validate with: `uvx ruff check .` and `uv run pytest tests/cli/`

### Output Format

Python CLI application with:
- Main Typer app with command groups
- Command functions with comprehensive docstrings
- Type-annotated parameters using Annotated
- Error handling with typer.Exit(code)
- Console script entry points in pyproject.toml

### Validation

**Pre-Task-Completion Checks:**
- All commands have type annotations
- Help text is clear and includes examples
- Exit codes are explicit (0 for success, non-zero for errors)
- Configuration options support environment variables
- Tests cover success and failure scenarios

**Success Criteria:**
- `uvx ruff check .` passes with zero errors
- `uv run pytest tests/cli/` passes all CLI tests
- `myapp --help` displays comprehensive help text
- Error conditions return appropriate exit codes

**Negative Tests:**
- Command without exit code handling (should always return 0 even on failure)
- Missing type annotations (should lack auto-validation)
- Hardcoded paths (should fail on other machines)

### Design Principles

- **Exit Codes Matter:** Non-zero for errors enables shell automation
- **Type Safety:** Annotated parameters for auto-validation and help
- **Separation of Concerns:** CLI layer thin, business logic separate
- **User Experience:** Clear help text, progress feedback, error messages

### Post-Execution Checklist

- [ ] Typer[all] installed with rich support
- [ ] Main CLI app configured with command groups
- [ ] All commands have type annotations
- [ ] Help text and examples provided
- [ ] Exit codes implemented for all error paths
- [ ] Console scripts configured in pyproject.toml
- [ ] Cross-platform compatibility verified
- [ ] Linting and tests pass

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Missing Exit Codes for Script Automation

**Problem:** CLI commands that always exit with code 0, even on errors, or use inconsistent exit codes that break shell script automation.

**Why It Fails:** Shell scripts can't detect failures (`set -e` doesn't catch errors). CI/CD pipelines show green on failures. Automation chains continue after failed steps. Silent failures corrupt data.

**Correct Pattern:**
```python
# BAD: Always exits 0
@app.command()
def process_file(path: str):
    try:
        data = load_file(path)
    except FileNotFoundError:
        print("File not found")
        return  # Exits 0, automation thinks success!

# GOOD: Explicit exit codes with raise_typer_exit
@app.command()
def process_file(path: str):
    try:
        data = load_file(path)
    except FileNotFoundError:
        typer.echo("Error: File not found", err=True)
        raise typer.Exit(code=1)  # Non-zero signals failure
    except PermissionError:
        typer.echo("Error: Permission denied", err=True)
        raise typer.Exit(code=2)  # Different codes for different errors
```

### Anti-Pattern 2: Hardcoded Paths Without Configuration Options

**Problem:** CLI tools with hardcoded file paths, directories, or URLs that can't be overridden via arguments or environment variables.

**Why It Fails:** Tools only work in original developer's environment. Can't run in CI/CD with different directory structures. No way to test with mock data.

**Correct Pattern:**
```python
# BAD: Hardcoded paths
@app.command()
def export_data():
    output_path = "/home/developer/exports/data.csv"  # Only works for one user!
    save_to_csv(output_path)

# GOOD: Configurable with sensible defaults
@app.command()
def export_data(
    output: Path = typer.Option(
        Path("./exports/data.csv"),
        "--output", "-o",
        help="Output file path",
        envvar="EXPORT_OUTPUT_PATH"
    )
):
    output.parent.mkdir(parents=True, exist_ok=True)
    save_to_csv(output)
```

### Anti-Pattern 3: Option `-h` Conflicts with Help

**Problem:** Defining `-h` as a short option for custom parameters (e.g., `--host`) shadows Typer's built-in `--help` shortcut.

**Why It Fails:** Users expect `-h` to show help; instead they get cryptic errors or unexpected behavior.

**Correct Pattern:**
```python
# BAD: -h shadows --help
@app.command()
def connect(
    host: Annotated[str, typer.Option("--host", "-h", help="Server host")] = "localhost",
):
    ...

# GOOD: Use different short option
@app.command()
def connect(
    host: Annotated[str, typer.Option("--host", "-H", help="Server host")] = "localhost",
):
    ...
```

## Project Setup and Structure

### Installation and Dependencies

- **Requirement:** Use `uv` for dependency management following `200-python-core.md` patterns
- **Requirement:** Install Typer with: `uv add "typer[all]"` for full features including Rich
- **Decision:** Use `typer[all]>=0.9.0` (default). Use `typer-slim` only for Docker images where binary size matters and no Rich output formatting is needed.
- **Always:** Include Typer in `[project.dependencies]` not `[project.optional-dependencies]`

```toml
# pyproject.toml
[project]
dependencies = [
    "typer[all]>=0.9.0",  # Includes rich and shellingham
]

[project.scripts]
myapp = "myapp.cli.main:app"
```

### Recommended Project Structure

- **Default:** Use flat layout (`myapp/` at project root) for CLI applications. See `203-python-project-setup.md` for guidance.
- **Rule:** Use `src/` layout for CLI projects with 5+ command modules or distributed as libraries
- **Rule:** Separate CLI logic from business logic in different modules

#### Flat Layout (Default)

Directory structure for `cli-project/`:
- `pyproject.toml`
- **myapp/** - Application package
  - `__init__.py`
  - **cli/** - CLI layer
    - `__init__.py`
    - `main.py` - Main CLI app and entry point
    - **commands/** - Command modules
      - `__init__.py`
      - `config.py` - Config-related commands
      - `data.py` - Data processing commands
    - `utils.py` - CLI utilities and helpers
  - **core/** - Business logic (CLI-independent)
    - `__init__.py`, `models.py`, `services.py`
  - **config/** - Configuration
    - `__init__.py`, `settings.py`
- **tests/** - Test suite
  - **cli/** - `test_commands.py`
  - **core/** - `test_services.py`

## CLI Application Design Patterns

### Main Application Setup

- **Rule:** Create a main Typer app with proper configuration:
```python
import typer
from typing_extensions import Annotated

from myapp.cli.commands import config, data

app = typer.Typer(
    name="myapp",
    help="My awesome CLI application",
    add_completion=True,
    rich_markup_mode="rich",
)

app.add_typer(config.app, name="config", help="Configuration management")
app.add_typer(data.app, name="data", help="Data processing commands")

@app.callback()
def main(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
):
    """My awesome CLI application."""
    if verbose:
        typer.echo("Verbose mode enabled")

if __name__ == "__main__":
    app()
```

### Command Definition Best Practices

- **Rule:** Use type annotations for automatic validation and help generation
- **Always:** Use `Annotated` for parameter metadata with Python 3.9+

```python
import typer
from pathlib import Path
from typing_extensions import Annotated
from enum import Enum

app = typer.Typer()

class OutputFormat(str, Enum):
    json = "json"
    csv = "csv"
    yaml = "yaml"

@app.command()
def process(
    input_file: Annotated[Path, typer.Argument(help="Input file to process", exists=True)],
    output_file: Annotated[Path, typer.Option("--output", "-o", help="Output file path")] = None,
    format: Annotated[OutputFormat, typer.Option(help="Output format")] = OutputFormat.json,
    batch_size: Annotated[int, typer.Option(min=1, max=10000, help="Processing batch size")] = 100,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be done")] = False,
):
    """Process input file and generate output in specified format."""
    if dry_run:
        typer.echo(f"[bold yellow]DRY RUN:[/bold yellow] Would process {input_file}")
        return
    typer.echo(f"Processing {input_file} with batch size {batch_size}")
```

### Error Handling and User Experience

- **Rule:** Use appropriate exit codes for different error conditions
- **Always:** Provide helpful error messages with context

```python
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()

def handle_processing_error(error: Exception, context: str = ""):
    """Handle processing errors with rich formatting."""
    error_panel = Panel(
        f"[red]Error:[/red] {str(error)}\n\n[dim]{context}[/dim]",
        title="Processing Failed",
        border_style="red"
    )
    console.print(error_panel)
    raise typer.Exit(1)

@app.command()
def risky_operation(
    input_path: Path,
    force: Annotated[bool, typer.Option("--force", help="Force operation")] = False,
):
    """Perform a risky operation with proper error handling."""
    try:
        if not input_path.exists():
            typer.echo(f"Error: Input path {input_path} does not exist", err=True)
            raise typer.Exit(1)

        if not force and input_path.stat().st_size > 1000000:
            if not typer.confirm("File is large. Continue?"):
                raise typer.Exit(0)

        console.print("[green]SUCCESS[/green] Operation completed successfully")
    except PermissionError:
        handle_processing_error(Exception("Permission denied"), "Check file permissions")
    except Exception as e:
        handle_processing_error(e, "Unexpected error occurred")
```

## Packaging and Distribution

### Console Scripts Configuration

```toml
# pyproject.toml
[project.scripts]
myapp = "myapp.cli.main:app"
myapp-dev = "myapp.cli.dev:dev_app"  # Development utilities
```

### Installation Setup

```bash
# Development setup with uv
uv sync --all-groups
uv run myapp --install-completion
```

### Cross-Platform Considerations

- **Rule:** Use `pathlib.Path` for all file operations
- **Rule:** Handle platform-specific features gracefully

```python
import platform
from pathlib import Path

def get_config_dir() -> Path:
    """Get platform-appropriate configuration directory."""
    system = platform.system()
    if system == "Windows":
        return Path.home() / "AppData" / "Local" / "myapp"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "myapp"
    else:
        return Path.home() / ".config" / "myapp"
```

### Version Management

```python
from importlib.metadata import version

def version_callback(value: bool):
    if value:
        console.print(f"myapp version {version('myapp')}")
        raise typer.Exit()

@app.callback()
def main(
    version: Annotated[bool, typer.Option(
        "--version", callback=version_callback, is_eager=True
    )] = False,
):
    pass
```

### Performance and Async Support

- **Rule:** Use Rich progress bars for long-running operations (see 220c)
- **Rule:** Use async commands for I/O-bound operations

```python
import asyncio
import aiohttp

@app.command()
def fetch_data(urls: list[str], concurrent: int = 5):
    """Fetch data from multiple URLs concurrently."""

    async def fetch_all():
        semaphore = asyncio.Semaphore(concurrent)
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_url(session, url, semaphore) for url in urls]
            return await asyncio.gather(*tasks)

    results = asyncio.run(fetch_all())
    for result in results:
        console.print(f"{result['status']}: {result['url']}")
```

### Documentation and Help

- **Rule:** Use comprehensive docstrings for help generation
- **Always:** Include examples in command help text

```python
@app.command()
def transform(
    input_file: Path,
    output_format: OutputFormat = OutputFormat.json,
):
    """
    Transform data between formats.

    Examples:
        myapp transform data.csv --output-format json
        myapp transform config.json --output-format yaml
    """
    # Implementation here
```
