"""Shared Rich console instance for consistent output."""

from rich.console import Console

console = Console()
err_console = Console(stderr=True)


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
