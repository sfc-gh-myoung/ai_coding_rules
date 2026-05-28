"""Dev env subcommand — environment setup and dependency management."""

from __future__ import annotations

import typer

from ai_rules._shared.console import console, log_success
from ai_rules._shared.runner import CommandFailureHint, run

env_app = typer.Typer(
    name="env", help="Environment setup and dependency management.", no_args_is_help=True
)


_UV_SETUP_HINT = CommandFailureHint(
    summary="Environment setup failed.",
    next_steps=(
        "uv run ai-rules dev status preflight",
        "Install uv from https://docs.astral.sh/uv/ if preflight reports uv is missing.",
    ),
)
_UV_SYNC_HINT = CommandFailureHint(
    summary="Dependency sync failed.",
    next_steps=("uv run ai-rules dev env lock", "uv run ai-rules dev env sync"),
)
_UV_LOCK_HINT = CommandFailureHint(
    summary="Dependency lock failed.",
    next_steps=("Review the dependency conflict above.", "uv run ai-rules dev env lock"),
)


@env_app.command("setup")
def env_setup() -> None:
    """Pin Python 3.11, create virtual environment."""
    console.print("[blue]→[/blue] Installing Python 3.11...")
    run(
        ["uv", "python", "install", "3.11"],
        failure_hint=_UV_SETUP_HINT,
        display_command=["uv", "run", "ai-rules", "dev", "env", "setup"],
    )
    console.print("[blue]→[/blue] Pinning Python 3.11...")
    run(
        ["uv", "python", "pin", "3.11"],
        failure_hint=_UV_SETUP_HINT,
        display_command=["uv", "run", "ai-rules", "dev", "env", "setup"],
    )
    console.print("[blue]→[/blue] Creating virtual environment...")
    run(
        ["uv", "venv"],
        failure_hint=_UV_SETUP_HINT,
        display_command=["uv", "run", "ai-rules", "dev", "env", "setup"],
    )
    log_success("Environment setup complete.")


@env_app.command("sync")
def env_sync() -> None:
    """Sync dev dependencies (fast)."""
    console.print("[blue]→[/blue] Syncing dependencies...")
    run(
        ["uv", "sync", "--all-groups"],
        failure_hint=_UV_SYNC_HINT,
        display_command=["uv", "run", "ai-rules", "dev", "env", "sync"],
    )
    log_success("Dependencies synced.")


@env_app.command("lock")
def env_lock() -> None:
    """Lock and sync all dependencies."""
    console.print("[blue]→[/blue] Locking dependencies...")
    run(
        ["uv", "lock"],
        failure_hint=_UV_LOCK_HINT,
        display_command=["uv", "run", "ai-rules", "dev", "env", "lock"],
    )
    console.print("[blue]→[/blue] Syncing dependencies...")
    run(
        ["uv", "sync", "--all-groups"],
        failure_hint=_UV_SYNC_HINT,
        display_command=["uv", "run", "ai-rules", "dev", "env", "sync"],
    )
    log_success("Dependencies locked and synced.")
