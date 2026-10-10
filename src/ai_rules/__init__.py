"""ai-rules: Unified CLI for AI coding rules management."""

from importlib.metadata import PackageNotFoundError, version

# pyproject.toml is the only source of the version; read it from the installed
# distribution. A source tree that was never installed reports 0.0.0+unknown.
try:
    __version__ = version("ai_coding_rules")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
