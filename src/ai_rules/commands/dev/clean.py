"""Dev clean subcommand — remove generated files and caches."""

from __future__ import annotations

import contextlib
import shutil
import sys
import tomllib
from pathlib import Path
from typing import Annotated

import typer

from ai_rules._shared.console import console, log_error, log_success
from ai_rules._shared.paths import find_project_root

clean_app = typer.Typer(
    name="clean",
    help="Remove generated files and caches.",
    no_args_is_help=True,
)

_DEFAULT_CACHE_GLOBS = [
    "**/__pycache__",
    "**/*.pyc",
    "**/.pytest_cache",
    "**/.mypy_cache",
    ".ruff_cache",
    "htmlcov",
    ".coverage",
]

_VENV_DIRS = [".venv"]


def _dev_config(root: Path) -> dict:
    """Read [tool.ai_rules.dev] from pyproject.toml."""
    pyproject = root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)
    return data.get("tool", {}).get("ai_rules", {}).get("dev", {})


def _remove_glob(root: Path, pattern: str) -> int:
    """Remove all paths matching pattern under root; return count removed."""
    removed = 0
    if pattern.startswith("**/"):
        glob_pattern = pattern[3:]
        paths = list(root.rglob(glob_pattern))
    elif pattern.startswith("**"):
        glob_pattern = pattern[2:]
        paths = list(root.rglob(glob_pattern))
    else:
        paths = [root / pattern]

    for path in paths:
        if path.exists() or path.is_symlink():
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                with contextlib.suppress(OSError):
                    path.unlink(missing_ok=True)
            removed += 1
    return removed


def _confirm_destructive(action: str, *, force: bool) -> None:
    """Confirm a destructive op.

    Per CLIG.dev: prompt on TTY; require --force on non-TTY.
    Aborts with exit 1 if user declines or non-TTY without --force.
    """
    if force:
        return
    if not sys.stdin.isatty():
        log_error(f"Refusing to {action} on a non-interactive terminal. Pass --force to proceed.")
        raise typer.Exit(code=1)
    if not typer.confirm(f"Proceed to {action}?", default=False):
        log_error("Aborted by user.")
        raise typer.Exit(code=1)


@clean_app.command("all")
def clean_all(
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Skip confirmation prompts (required on non-interactive terminals).",
        ),
    ] = False,
) -> None:
    """Remove all caches and the virtual environment."""
    root = find_project_root()
    _confirm_destructive("remove all caches and .venv", force=force)
    _do_clean_cache(root)
    _do_clean_venv(root)
    log_success("Clean complete.")


@clean_app.command("cache")
def clean_cache() -> None:
    """Remove Python caches (__pycache__, .pyc, coverage, etc.)."""
    root = find_project_root()
    _do_clean_cache(root)
    log_success("Cache clean complete.")


@clean_app.command("venv")
def clean_venv(
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Skip confirmation prompt (required on non-interactive terminals).",
        ),
    ] = False,
) -> None:
    """Remove the virtual environment (.venv)."""
    root = find_project_root()
    _confirm_destructive("remove .venv", force=force)
    _do_clean_venv(root)
    log_success("Virtual environment removed.")


def _do_clean_cache(root: Path) -> None:
    """Remove cache files using config globs."""
    cfg = _dev_config(root)
    globs = cfg.get("clean_globs", _DEFAULT_CACHE_GLOBS)
    console.print("[blue]→[/blue] Removing cache files...")
    total = 0
    for pattern in globs:
        if pattern in _VENV_DIRS:
            continue
        total += _remove_glob(root, pattern)
    console.print(f"  Removed {total} item(s).")


def _do_clean_venv(root: Path) -> None:
    """Remove .venv directory."""
    console.print("[blue]→[/blue] Removing virtual environment...")
    removed = 0
    for d in _VENV_DIRS:
        venv_path = root / d
        if venv_path.exists():
            shutil.rmtree(venv_path, ignore_errors=True)
            removed += 1
    console.print(f"  Removed {removed} virtual environment(s).")


def get_clean_globs(
    root: Path,
    *,
    include_venv: Annotated[bool, "Include .venv in glob list"] = False,
) -> list[str]:
    """Return the configured clean globs; optionally include venv dirs."""
    cfg = _dev_config(root)
    globs: list[str] = cfg.get("clean_globs", _DEFAULT_CACHE_GLOBS)
    if include_venv:
        globs = list(globs) + _VENV_DIRS
    return globs
