# Python Typer CLI Configuration Management

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Typer, CLI configuration, Pydantic Settings, environment variables, config precedence, CLI options
**TokenBudget:** ~1300
**ContextTier:** Medium
**Depends:** 220-python-typer-cli.md
**LoadTrigger:** kw:cli-config, kw:pydantic-settings

## Scope

**What This Rule Covers:**
Configuration and environment management for Typer CLI applications using Pydantic Settings, including configuration precedence, environment variables, and CLI override patterns.

**When to Load This Rule:**
- Adding configuration to a Typer CLI application
- Integrating Pydantic Settings with CLI options
- Setting up environment variable support
- Implementing configuration precedence (CLI > env > file > defaults)

## References

### Dependencies

**Must Load First:**
- **220-python-typer-cli.md** - Core Typer CLI patterns

**Related:**
- **230-python-pydantic.md** - Pydantic model patterns
- **230a-python-pydantic-settings.md** - Pydantic Settings details

## Contract

### Inputs and Prerequisites

- Typer CLI application (from 220-python-typer-cli.md)
- pydantic-settings installed: `uv add pydantic-settings`

### Mandatory

- **Always:** Support multiple configuration sources (files, environment, CLI options)
- **Always:** Follow precedence: CLI options > Environment > Config file > Defaults
- **Rule:** Use Pydantic Settings for configuration validation

### Forbidden

- Hardcoded configuration values without override options
- Ignoring environment variables for deployable CLIs

### Execution Steps

1. Create settings class with `pydantic-settings`
2. Define environment variable prefix (e.g., `MYAPP_`)
3. Wire CLI options as overrides to settings
4. Test configuration loading from all sources

### Output Format

Settings class with validated configuration, CLI overrides, and env var support.

### Validation

**Pre-Task-Completion Checks:**
- [ ] Settings class validates all config values
- [ ] Environment variables work with prefix
- [ ] CLI options override environment and file values
- [ ] Defaults are sensible for development

**Negative Tests:**
- Invalid config value (should raise ValidationError at startup)
- Missing required env var without CLI override (should fail with clear message)

### Design Principles

- **Precedence:** CLI > Environment > Config file > Defaults
- **Validation:** Fail fast at startup with clear error messages
- **Discoverability:** Document all env vars and their defaults

### Post-Execution Checklist

- [ ] Settings class created with Pydantic Settings
- [ ] Environment variable prefix configured
- [ ] CLI overrides wired in callback
- [ ] Configuration documented

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Global Settings Mutation Without Copy**

**Problem:** Mutating a global settings instance in the CLI callback creates hidden state that's hard to test and debug.

```python
# BAD: Mutating global state
settings = AppSettings()

@app.callback()
def main(debug: bool = None):
    global settings
    if debug is not None:
        settings.debug = debug  # Mutation!
```

**Correct Pattern:**
```python
# GOOD: Create new instance with overrides
@app.callback()
def main(ctx: typer.Context, debug: bool = None):
    ctx.ensure_object(dict)
    overrides = {}
    if debug is not None:
        overrides["debug"] = debug
    ctx.obj["settings"] = AppSettings(**{**AppSettings().model_dump(), **overrides})
```

**Anti-Pattern 2: Missing Environment Variable Documentation**

**Problem:** Users can't discover available env vars without reading source code.

**Correct Pattern:** Add a `show-config` command that lists all settings and their sources.

## Configuration Patterns

### Pydantic Settings Integration

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Optional

class AppSettings(BaseSettings):
    """Application settings with multiple sources."""

    debug: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level")
    data_dir: Path = Field(Path.home() / ".myapp" / "data", description="Data directory")
    config_file: Optional[Path] = Field(None, description="Configuration file path")
    api_timeout: int = Field(30, ge=1, le=300, description="API timeout in seconds")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")

    model_config = SettingsConfigDict(
        env_prefix="MYAPP_",
        env_file=".env",
        case_sensitive=False,
    )

settings = AppSettings()
```

### CLI Override Pattern

```python
@app.callback()
def main(
    ctx: typer.Context,
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug mode")] = None,
    config: Annotated[Optional[Path], typer.Option("--config", help="Config file")] = None,
):
    """Main CLI callback with configuration override."""
    ctx.ensure_object(dict)
    overrides = {}
    if debug is not None:
        overrides["debug"] = debug
    if config is not None:
        overrides["config_file"] = config

    if overrides:
        ctx.obj["settings"] = AppSettings(**{**settings.model_dump(), **overrides})
    else:
        ctx.obj["settings"] = settings
```

### Show Config Command

```python
from rich.table import Table

@app.command()
def show_config(ctx: typer.Context):
    """Display current configuration."""
    current_settings = ctx.obj.get("settings", settings)
    table = Table(title="Configuration")
    table.add_column("Setting")
    table.add_column("Value")

    for field_name, field_value in current_settings:
        table.add_row(field_name, str(field_value))
    console.print(table)
```
