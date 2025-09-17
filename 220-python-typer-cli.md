**Description:** Comprehensive Typer CLI development patterns covering setup, design, testing, and deployment best practices for Python command-line applications.
**AppliesTo:** `**/*.py`, `**/cli/**/*`, `**/commands/**/*`, `pyproject.toml`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-14

# Python Typer CLI Development Best Practices

## Purpose
Provide comprehensive guidance for building robust, user-friendly command-line applications using Typer, covering project setup, argument handling, testing strategies, and deployment patterns for maintainable CLI tools.

## 1. Project Setup and Structure

### Installation and Dependencies
- **Requirement:** Use `uv` for dependency management following `@200-python-core.md` patterns
- **Requirement:** Install Typer with: `uv add typer` or `uv add "typer[all]"` for full features
- **Rule:** Use `typer-slim` for minimal installations when rich formatting isn't needed
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
- **Rule:** Use `src/` layout for CLI applications to avoid import conflicts
- **Rule:** Separate CLI logic from business logic in different modules
- **Always:** Create dedicated CLI module structure:

```
cli-project/
├── pyproject.toml
├── src/
│   └── myapp/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py          # Main CLI app and entry point
│       │   ├── commands/        # Command modules
│       │   │   ├── __init__.py
│       │   │   ├── config.py    # Config-related commands
│       │   │   └── data.py      # Data processing commands
│       │   └── utils.py         # CLI utilities and helpers
│       ├── core/                # Business logic (CLI-independent)
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── services.py
│       └── config/
│           ├── __init__.py
│           └── settings.py
└── tests/
    ├── __init__.py
    ├── cli/
    │   └── test_commands.py
    └── core/
        └── test_services.py
```

## 2. CLI Application Design Patterns

### Main Application Setup
- **Rule:** Create a main Typer app with proper configuration:
```python
# src/myapp/cli/main.py
import typer
from typing_extensions import Annotated

from myapp.cli.commands import config, data

app = typer.Typer(
    name="myapp",
    help="My awesome CLI application",
    add_completion=True,
    rich_markup_mode="rich",  # Enable rich formatting
)

# Add command groups
app.add_typer(config.app, name="config", help="Configuration management")
app.add_typer(data.app, name="data", help="Data processing commands")

@app.callback()
def main(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output")] = False,
    config_file: Annotated[typer.FileText, typer.Option(help="Configuration file path")] = None,
):
    """
    My awesome CLI application.
    
    Use --help with any command for more information.
    """
    if verbose:
        typer.echo("Verbose mode enabled")
    
    # Set global configuration
    if config_file:
        # Load configuration logic here
        pass

if __name__ == "__main__":
    app()
```

### Command Definition Best Practices
- **Rule:** Use type annotations for automatic validation and help generation
- **Rule:** Provide clear docstrings for commands and parameters
- **Always:** Use `Annotated` for parameter metadata with Python 3.9+

```python
# src/myapp/cli/commands/data.py
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
    """
    Process input file and generate output in specified format.
    
    This command reads the input file, processes the data according to
    the specified parameters, and writes the result to the output file.
    """
    if dry_run:
        typer.echo(f"[bold yellow]DRY RUN:[/bold yellow] Would process {input_file}")
        return
    
    # Implementation here
    typer.echo(f"Processing {input_file} with batch size {batch_size}")
```

### Error Handling and User Experience
- **Rule:** Use Typer's built-in error handling and rich formatting
- **Always:** Provide helpful error messages with context
- **Rule:** Use appropriate exit codes for different error conditions

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
        
        if not force and input_path.stat().st_size > 1000000:  # 1MB
            if not typer.confirm("File is large. Continue?"):
                typer.echo("Operation cancelled")
                raise typer.Exit(0)
        
        # Perform operation
        console.print("[green]✓[/green] Operation completed successfully")
        
    except PermissionError:
        handle_processing_error(
            Exception("Permission denied"), 
            "Check file permissions and try again"
        )
    except Exception as e:
        handle_processing_error(e, "Unexpected error occurred")
```

## 3. Configuration and Environment Management

### Configuration Patterns
- **Rule:** Support multiple configuration sources (files, environment, CLI options)
- **Rule:** Use Pydantic Settings for configuration validation
- **Always:** Follow the precedence: CLI options > Environment > Config file > Defaults

```python
# src/myapp/config/settings.py
from pydantic import BaseSettings, Field
from pathlib import Path
from typing import Optional

class AppSettings(BaseSettings):
    """Application settings with multiple sources."""
    
    # Core settings
    debug: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level")
    
    # File paths
    data_dir: Path = Field(Path.home() / ".myapp" / "data", description="Data directory")
    config_file: Optional[Path] = Field(None, description="Configuration file path")
    
    # API settings
    api_timeout: int = Field(30, ge=1, le=300, description="API timeout in seconds")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    
    class Config:
        env_prefix = "MYAPP_"
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = AppSettings()

# CLI integration
@app.callback()
def main(
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug mode")] = None,
    config: Annotated[Optional[Path], typer.Option("--config", help="Config file")] = None,
):
    """Main CLI callback with configuration override."""
    global settings
    
    # Override settings from CLI
    overrides = {}
    if debug is not None:
        overrides["debug"] = debug
    if config is not None:
        overrides["config_file"] = config
    
    if overrides:
        settings = AppSettings(**{**settings.dict(), **overrides})
```

### Environment Variables
- **Rule:** Use consistent naming with prefixes
- **Always:** Document required variables

```python
# Environment variables: MYAPP_DEBUG, MYAPP_LOG_LEVEL, MYAPP_DATA_DIR

@app.command()
def show_config():
    """Display current configuration."""
    table = Table(title="Configuration")
    table.add_column("Setting")
    table.add_column("Value")
    
    for field_name, field_value in settings:
        table.add_row(field_name, str(field_value))
    console.print(table)
```

## 4. Testing Strategies

### CLI Testing with Typer's Test Client
- **Rule:** Use Typer's built-in testing utilities for CLI tests
- **Always:** Test both success and failure scenarios
- **Rule:** Mock external dependencies and file system operations

```python
# tests/cli/test_commands.py
import pytest
from typer.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock

from myapp.cli.main import app

runner = CliRunner()

def test_process_command_success(tmp_path):
    """Test successful file processing."""
    input_file = tmp_path / "input.txt"
    input_file.write_text("test data")
    
    result = runner.invoke(app, ["data", "process", str(input_file)])
    
    assert result.exit_code == 0
    assert "Processing" in result.stdout

def test_process_command_missing_file():
    """Test error handling for missing input file."""
    result = runner.invoke(app, ["data", "process", "nonexistent.txt"])
    
    assert result.exit_code != 0
    assert "does not exist" in result.stdout

@patch('myapp.core.services.external_api_call')
def test_command_with_mock(mock_api):
    """Test command with external dependencies."""
    mock_api.return_value = {"status": "success"}
    result = runner.invoke(app, ["data", "sync"])
    assert result.exit_code == 0
```

### Integration Testing
- **Rule:** Test complete workflows end-to-end
- **Always:** Use temporary directories for file operations

```python
def test_complete_pipeline(tmp_path):
    runner = CliRunner()
    input_file = tmp_path / "input.json"
    input_file.write_text('{"test": "data"}')
    
    result = runner.invoke(app, ["process", str(input_file)])
    assert result.exit_code == 0
```

## 5. Performance and User Experience

### Progress Indicators
- **Rule:** Use Rich progress bars for long-running operations
- **Always:** Provide feedback for operations over 2 seconds

```python
from rich.progress import Progress

@app.command()
def long_operation(items: int = 100):
    """Process items with progress tracking."""
    with Progress() as progress:
        task = progress.add_task("Processing...", total=items)
        for i in range(items):
            # Simulate work
            time.sleep(0.1)
            progress.update(task, advance=1)
    console.print("[green]✓[/green] Complete!")
```

### Async Command Support
- **Rule:** Use async commands for I/O-bound operations
- **Always:** Handle async exceptions properly

```python
import asyncio
import aiohttp

@app.command()
def fetch_data(urls: List[str], concurrent: int = 5):
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

## 6. Packaging and Distribution

### Console Scripts Configuration
- **Rule:** Define entry points in `pyproject.toml` for easy installation
- **Always:** Use descriptive script names that don't conflict with system commands
- **Rule:** Support both module execution and script entry points

```toml
# pyproject.toml
[project.scripts]
myapp = "myapp.cli.main:app"
myapp-dev = "myapp.cli.dev:dev_app"  # Development utilities

# Alternative: using entry points
[project.entry-points."console_scripts"]
myapp = "myapp.cli.main:app"
```

### Installation Setup
- **Rule:** Follow `@203-python-project-setup.md` patterns
- **Always:** Include CLI testing dependencies

```bash
# Development setup with uv
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
myapp --install-completion
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

## 7. Documentation and Help

### Auto-Generated Documentation
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

### Version Management
- **Rule:** Use `importlib.metadata` for version retrieval

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

## Related Rules

- **`@200-python-core.md`** - Core Python patterns and uv usage
- **`@201-python-lint-format.md`** - Ruff linting and formatting standards  
- **`@203-python-project-setup.md`** - Python project structure and packaging
- **`@800-project-changelog-rules.md`** - Changelog discipline for CLI changes

## References

### External Documentation
- [Typer Documentation](https://typer.tiangolo.com/) - Modern CLI framework with automatic help generation
- [Rich Documentation](https://rich.readthedocs.io/) - Terminal styling, progress bars, and rich text rendering
- [Click Documentation](https://click.palletsprojects.com/) - Underlying CLI framework and advanced patterns
- [Python Packaging Guide](https://packaging.python.org/) - Distribution, entry points, and packaging best practices

## Rule Type and Scope

- **Type:** Agent Requested (use `@220-python-typer-cli.md` to apply)
- **Scope:** Python CLI development, command-line applications, user interfaces
- **Applies to:** CLI applications, command-line tools, interactive scripts
- **Validation:** CLI testing, user experience testing, cross-platform validation
