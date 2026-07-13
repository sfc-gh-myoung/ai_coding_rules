"""Shared Rich console instance for consistent output."""

import io
import os
import sys

from rich.console import Console
from rich.markup import escape as _rich_escape


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


def _build_real_stderr() -> "io.TextIOBase | None":
    """Return a writable file pinned to the real stderr fd at import time.

    Rich's ``Live`` redraws progress UIs by emitting cursor-up + clear-line
    ANSI sequences relative to whatever ``Console.file`` currently is. If we
    let ``err_console`` resolve ``sys.stderr`` dynamically (via
    ``Console(stderr=True)``), then any ``contextlib.redirect_stderr`` --
    such as the one used by ``quiet_sdk`` to silence agent-SDK chatter --
    would also redirect Live's frames into the buffer, breaking the UI.

    Duplicating fd 2 here gives ``err_console`` a private channel to the
    real terminal that survives every ``sys.stderr`` reassignment in the
    process. The SDK silencer can therefore redirect ``sys.stderr`` freely
    without touching the live region.

    Returns ``None`` (so callers fall back to ``stderr=True``) when:
    - Running under pytest (the dup happens before pytest's capfd hooks
      install, so the duped fd would bypass test capture machinery).
    - ``os.dup`` or ``os.fdopen`` fails (e.g., closed stderr in oddball
      embedded contexts).
    """
    if "pytest" in sys.modules:
        return None
    try:
        fd = os.dup(2)
    except OSError:
        return None
    try:
        raw = os.fdopen(fd, "wb", buffering=0)
    except OSError:
        os.close(fd)
        return None
    return io.TextIOWrapper(
        raw, encoding="utf-8", errors="replace", line_buffering=False, write_through=True
    )


_real_stderr = _build_real_stderr()

console = Console(
    width=_width,
    force_terminal=_use_color,
    no_color=not _use_color,
)
if _real_stderr is not None:
    err_console = Console(
        file=_real_stderr,  # type: ignore[arg-type]  # ty:ignore[invalid-argument-type]
        width=_width,
        force_terminal=_use_color,
        no_color=not _use_color,
    )
else:
    err_console = Console(
        stderr=True,
        width=_width,
        force_terminal=_use_color,
        no_color=not _use_color,
    )


def log_info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {_rich_escape(message)}")


def log_success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {_rich_escape(message)}")


def log_warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {_rich_escape(message)}")


def log_error(message: str) -> None:
    """Print error message to stderr.

    Escapes Rich markup so messages containing ``[fixture-id]`` or other
    bracketed prefixes render literally instead of being interpreted as
    color/style tags (which silently strips them from the output).
    """
    err_console.print(f"[red]✗[/red] {_rich_escape(message)}")
