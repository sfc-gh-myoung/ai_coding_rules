"""Process-wide runtime flags for the ai-rules CLI."""

from __future__ import annotations

_debug_enabled = False


def set_debug(enabled: bool) -> None:
    """Set whether debug tracebacks should be exposed for friendly CLI errors."""
    global _debug_enabled
    _debug_enabled = enabled


def is_debug_enabled() -> bool:
    """Return whether debug tracebacks should be exposed for friendly CLI errors."""
    return _debug_enabled
