"""Shared Rich console instance for consistent output."""

import os

from rich.console import Console

# Use fixed width to prevent text wrapping in narrow terminals (e.g., CI)
# This ensures "not found" doesn't become "not\nfound" due to line wrapping
_width = 200 if os.environ.get("CI") or os.environ.get("TERM") == "dumb" else None

console = Console(width=_width)
err_console = Console(stderr=True, width=_width)


def log_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def log_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def log_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def log_error(message: str) -> None:
    """Print error message to stderr."""
    err_console.print(f"[red]✗[/red] {message}")
