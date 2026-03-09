# Python Pydantic Settings Management

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:pydantic-settings, kw:env-file, kw:app-config
**Keywords:** Pydantic Settings, BaseSettings, environment variables, configuration, env_file, nested settings, config precedence
**TokenBudget:** ~1800
**ContextTier:** Medium
**Depends:** 230-python-pydantic.md

## Scope

**What This Rule Covers:**
Application configuration management using pydantic-settings, including BaseSettings patterns, environment variable loading, nested configuration, and startup validation.

**When to Load This Rule:**
- Setting up application configuration with pydantic-settings
- Loading configuration from environment variables or .env files
- Implementing nested settings (e.g., database, cache, API configs)
- Validating configuration at application startup

## References

### Dependencies

**Must Load First:**
- **230-python-pydantic.md** - Core Pydantic model patterns

**Related:**
- **220a-python-typer-config.md** - CLI configuration integration
- **210-python-fastapi-core.md** - FastAPI settings injection

## Contract

### Inputs and Prerequisites

- Pydantic v2 project (from 230-python-pydantic.md)
- `pydantic-settings>=2.0.0` installed via `uv add pydantic-settings`

### Mandatory

- **Always:** Use `pydantic-settings` for configuration management
- **Always:** Validate all configuration values at startup
- **Rule:** Support multiple configuration sources with clear precedence
- **Rule:** Use `SettingsConfigDict` for settings configuration (not plain dicts)

### Forbidden

- Side-effects in settings validators (directory creation, network calls)
- Hardcoded secrets in settings defaults
- Using plain dicts for model_config in settings classes

### Execution Steps

1. Install pydantic-settings: `uv add pydantic-settings`
2. Define settings classes with typed fields and defaults
3. Configure env_file, env_prefix, and nested delimiter
4. Add validators for complex settings (validate only, no side-effects)
5. Create global settings instance and validate at startup
6. Wire settings into application via dependency injection

### Output Format

Settings classes with environment variable loading, validation, and startup checks.

### Validation

**Pre-Task-Completion Checks:**
- [ ] Settings load from environment variables with prefix
- [ ] .env file loading works correctly
- [ ] Nested settings resolve with delimiter
- [ ] Invalid values raise ValidationError at startup

### Design Principles

- **Validate, don't create:** Settings validators should check values, not create resources
- **Fail at startup:** Invalid configuration should prevent application start
- **Namespace env vars:** Use env_prefix to avoid collisions

### Post-Execution Checklist

- [ ] pydantic-settings installed
- [ ] Settings class with SettingsConfigDict
- [ ] Environment variable prefix configured
- [ ] Nested settings properly configured
- [ ] Startup validation in place
- [ ] No side-effects in validators

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Side-Effects in Settings Validators

**Problem:** Creating directories or files inside a `@field_validator` on a settings class. Validators run during instantiation and testing, causing unexpected file system changes.

**Correct Pattern:** Validate only in validators; create resources at application startup.

```python
# Wrong: Creates directories during validation
@field_validator("data_dir")
@classmethod
def validate_data_dir(cls, v: Path) -> Path:
    v.mkdir(parents=True, exist_ok=True)  # Side-effect!
    return v

# Correct: Validate only; create at startup
@field_validator("data_dir")
@classmethod
def validate_data_dir(cls, v: Path) -> Path:
    if not v.parent.exists():
        raise ValueError(f"Parent directory does not exist: {v.parent}")
    return v

# In main.py or app startup:
settings = AppSettings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
```

### Anti-Pattern 2: Missing Env Prefix

**Problem:** Settings without `env_prefix` collide with system or other application environment variables (e.g., `HOST`, `PORT`, `DEBUG`).

**Correct Pattern:** Namespace all settings with an application-specific `env_prefix` via `SettingsConfigDict`.

```python
# Wrong: Generic names without prefix
class AppSettings(BaseSettings):
    host: str = "0.0.0.0"  # Collides with HOST env var
    debug: bool = False     # Collides with DEBUG env var

# Correct: Namespaced with prefix
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MYAPP_")
    host: str = "0.0.0.0"  # Reads MYAPP_HOST
    debug: bool = False     # Reads MYAPP_DEBUG
```

## Settings Patterns

### Application Settings with Nested Configuration

```python
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from pathlib import Path

class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, ge=1, le=65535)
    username: str = Field(..., description="Database username")
    password: str = Field(..., description="Database password")
    database: str = Field(..., description="Database name")

    @property
    def url(self) -> str:
        """Generate database URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

class AppSettings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = Field(default="MyApp", description="Application name")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", pattern=r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$')

    # Server settings
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000, ge=1, le=65535)

    # Security settings
    secret_key: str = Field(..., min_length=32, description="Secret key for encryption")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["localhost", "127.0.0.1"])

    # Nested database settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    # File paths
    data_dir: Path = Field(default=Path("./data"))
    log_file: Optional[Path] = Field(default=None)

    @field_validator("data_dir")
    @classmethod
    def validate_data_dir(cls, v: Path) -> Path:
        """Validate data directory path (create at startup, not here)."""
        if not v.parent.exists():
            raise ValueError(f"Parent directory does not exist: {v.parent}")
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is sufficiently complex."""
        if len(set(v)) < 10:
            raise ValueError("Secret key must have sufficient entropy")
        return v

# Usage: set env vars with MYAPP_ prefix and __ for nesting
# MYAPP_DEBUG=true
# MYAPP_DATABASE__HOST=db.example.com
# MYAPP_DATABASE__PORT=5432
settings = AppSettings()
```

### Startup Validation Pattern

```python
def create_app() -> FastAPI:
    """Create application with validated settings."""
    try:
        settings = AppSettings()
    except ValidationError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Create resources AFTER validation, not inside validators
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.state.settings = settings
    return app
```
