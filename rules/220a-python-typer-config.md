# Python Typer CLI Configuration Management

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Typer, CLI configuration, Pydantic Settings, environment variables, config precedence, CLI options
**TokenBudget:** ~2550
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

**Success Criteria (Runnable):**
- `uv run myapp show-config` displays all current settings with sources
- `MYAPP_DEBUG=true uv run myapp show-config` shows debug=True from env
- `uv run myapp --config test.toml show-config` loads from TOML file
- `MYAPP_DEBUG=true uv run myapp --config test.toml show-config` shows env overrides file

**Negative Tests:**
- Invalid config value (should raise ValidationError at startup)
- Missing required env var without CLI override (should fail with clear message)
- `MYAPP_API_TIMEOUT=abc uv run myapp show-config` shows validation error, exit code 1
- `uv run myapp --config nonexistent.toml` shows file not found error, exit code 1

### Design Principles

- **Precedence:** CLI > Environment > Config file > Defaults
- **Validation:** Fail fast at startup with clear error messages
- **Discoverability:** Document all env vars and their defaults

> **Investigation Required**
> Before adding or modifying configuration patterns, the agent MUST:
> 1. Read existing settings/config classes — check for existing `BaseSettings` subclasses in the project
> 2. Check current environment variable patterns — look for existing `env_prefix` values to avoid conflicts
> 3. Read `.env` files and `pyproject.toml` for existing config conventions
> 4. Check if `pydantic-settings` is already installed (`uv pip list | grep pydantic-settings`)
> 5. Verify the config precedence chain matches the project's existing behavior
> 6. Never create a second settings class when one already exists — extend the existing class

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

### Config File Loading

To load settings from a TOML config file with proper precedence:

```python
import tomllib
from pathlib import Path
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application settings with TOML file support."""
    config_file: Path | None = None
    api_url: str = "https://api.example.com"
    api_timeout: int = Field(30, ge=1, le=300)
    max_retries: int = Field(3, ge=0, le=10)
    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="MYAPP_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @model_validator(mode="before")
    @classmethod
    def load_config_file(cls, data: dict) -> dict:
        """Load values from TOML config file if specified."""
        config_path = data.get("config_file")
        if config_path is not None:
            path = Path(config_path)
            if not path.exists():
                raise ValueError(f"Config file not found: {path}")
            with open(path, "rb") as f:
                file_data = tomllib.load(f)
            # File values are lowest priority — only fill missing keys
            for key, value in file_data.items():
                data.setdefault(key, value)
        return data
```

Example TOML config file (`~/.config/myapp/config.toml`):
```toml
api_url = "https://api.staging.example.com"
api_timeout = 60
debug = true
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

### Config Validation Error Handling

Wrap settings initialization to catch validation errors from any source:

```python
from pydantic import ValidationError

@app.callback()
def main(
    ctx: typer.Context,
    config_file: Annotated[Optional[Path], typer.Option("--config", "-c")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    """My CLI application."""
    try:
        settings = AppSettings(config_file=config_file)
    except ValidationError as e:
        err_console.print("[red]Configuration error:[/red]")
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            err_console.print(f"  {field}: {error['msg']}")
        raise typer.Exit(code=1)

    ctx.ensure_object(dict)
    ctx.obj["settings"] = settings
```

Common failure modes this handles:
- `MYAPP_DEBUG=notabool` produces "debug: Input should be a valid boolean"
- `MYAPP_API_TIMEOUT=-5` produces "api_timeout: Input should be greater than or equal to 1"
- `--config nonexistent.toml` produces "config_file: Config file not found: nonexistent.toml"

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

### Nested Configuration

For complex settings with grouped sub-configurations:

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseModel):
    """Database connection settings (not a BaseSettings — no env support)."""
    host: str = "localhost"
    port: int = Field(5432, ge=1, le=65535)
    name: str = "myapp"


class AppSettings(BaseSettings):
    """Application settings with nested database config."""
    debug: bool = False
    database: DatabaseConfig = DatabaseConfig()

    model_config = SettingsConfigDict(
        env_prefix="MYAPP_",
        env_nested_delimiter="__",  # MYAPP_DATABASE__HOST=dbhost
    )
```

With `env_nested_delimiter="__"`:
- `MYAPP_DATABASE__HOST=dbhost` sets `settings.database.host`
- `MYAPP_DATABASE__PORT=5433` sets `settings.database.port`

### Secrets Management

For sensitive values (API keys, passwords), use Pydantic's `SecretStr`:

```python
from pydantic import SecretStr

class AppSettings(BaseSettings):
    api_key: SecretStr  # Required — no default
    db_password: SecretStr = SecretStr("")

    model_config = SettingsConfigDict(
        env_prefix="MYAPP_",
        secrets_dir="/run/secrets",  # Docker secrets mount point
    )
```

**Key rules:**
- `SecretStr` values display as `'**********'` in logs and `show-config` output
- Access the actual value with `settings.api_key.get_secret_value()`
- Use `secrets_dir` for Docker/Kubernetes secret file mounts
- Never log or print secret values without explicit `.get_secret_value()` call
