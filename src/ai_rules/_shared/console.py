"""Shared Rich console instance for consistent output."""

import os
import sys

from rich.console import Console


def _should_use_color() -> bool:
    """Determine if color output should be used.

    Respects:
    - NO_COLOR env var (https://no-color.org/)
    - CI env var (CI environments typically don't want color)
    - TERM=dumb (dumb terminals can't handle ANSI)
    - pytest context (disable colors to avoid ANSI in test assertions)
    """
    return not (
        os.environ.get("NO_COLOR")
        or os.environ.get("CI")
        or os.environ.get("TERM") == "dumb"
        or "pytest" in sys.modules
    )


_use_color = _should_use_color()
# Use fixed width in non-color mode to prevent text wrapping in narrow terminals
# This ensures "not found" doesn't become "not\nfound" due to line wrapping
_width = 200 if not _use_color else None

console = Console(
    width=_width,
    force_terminal=_use_color,
    no_color=not _use_color,
)
err_console = Console(
    stderr=True,
    width=_width,
    force_terminal=_use_color,
    no_color=not _use_color,
)


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
