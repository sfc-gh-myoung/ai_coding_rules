"""Shared subprocess runner for dev subcommands."""

from __future__ import annotations

import shlex
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import typer
from rich.markup import escape as rich_escape

from ai_rules._shared.console import err_console
from ai_rules._shared.runtime import is_debug_enabled


@dataclass(frozen=True)
class CommandFailureHint:
    """User-facing guidance shown when a subprocess fails."""

    summary: str
    next_steps: tuple[str, ...] = ()
    details: str | None = None


def _format_command(argv: Sequence[str]) -> str:
    """Return a shell-readable command string for display only."""
    return " ".join(shlex.quote(part) for part in argv)


def _print_friendly_failure(
    *,
    summary: str,
    command: Sequence[str],
    next_steps: Sequence[str] = (),
    details: str | None = None,
) -> None:
    """Print a concise, actionable subprocess failure message."""
    err_console.print(f"\n[red]✗[/red] {rich_escape(summary)}")
    err_console.print("\n[bold]Command:[/bold]")
    err_console.print(f"  {rich_escape(_format_command(command))}")
    if details:
        err_console.print("\n[bold]Details:[/bold]")
        err_console.print(f"  {rich_escape(details)}")
    if next_steps:
        label = "Next step" if len(next_steps) == 1 else "Next steps"
        err_console.print(f"\n[bold]{label}:[/bold]")
        for step in next_steps:
            err_console.print(f"  {rich_escape(step)}")
    err_console.print("\nRun with [bold]--debug[/bold] to show the Python traceback.")


def run(
    argv: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    capture: bool = False,
    check: bool = True,
    failure_hint: CommandFailureHint | None = None,
    friendly: bool = True,
    display_command: Sequence[str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess, streaming output to the terminal unless captured.

    Args:
        argv: Command and arguments as a sequence. Never joined into a shell string.
        cwd: Working directory for the subprocess. Defaults to current directory.
        env: Environment variables for the subprocess. None inherits current env.
        capture: If True, capture stdout and stderr instead of streaming.
        check: If True, fail on non-zero exit code.
        failure_hint: Optional user-facing remediation shown on failure.
        friendly: If True, convert expected command failures into Typer exits unless debug is enabled.
        display_command: Optional command to show in failure output. Defaults to ``argv``.

    Returns:
        CompletedProcess result with returncode, stdout, stderr.

    Raises:
        FileNotFoundError: If the command binary cannot be resolved and friendly handling is disabled.
        subprocess.CalledProcessError: If check=True, the process exits non-zero, and friendly handling is disabled or debug is enabled.
        typer.Exit: If friendly handling is enabled and debug is disabled.
    """
    args = list(argv)
    if not args:
        raise ValueError("argv must be non-empty")

    command_for_display = list(display_command) if display_command is not None else list(args)
    binary = args[0]
    resolved = shutil.which(binary)
    if resolved is None:
        summary = f"Command not found: {binary}"
        if friendly and not is_debug_enabled():
            hint_steps = (
                failure_hint.next_steps
                if failure_hint
                else (f"Install {binary} or add it to PATH.",)
            )
            _print_friendly_failure(
                summary=summary,
                command=command_for_display,
                next_steps=hint_steps,
                details=failure_hint.details if failure_hint else None,
            )
            raise typer.Exit(127)
        err_console.print(
            f"[red]✗[/red] Command not found: [bold]{rich_escape(binary)}[/bold]. Is it installed and on PATH?"
        )
        raise FileNotFoundError(f"Command not found: {binary}")
    args[0] = resolved

    kwargs: dict = {
        "args": args,
        "shell": False,
        "text": True,
        "cwd": cwd,
        "env": dict(env) if env is not None else None,
        "check": False,
    }
    if capture:
        kwargs["capture_output"] = True
    else:
        kwargs["stdout"] = None
        kwargs["stderr"] = None

    result = subprocess.run(**kwargs)
    if check and result.returncode != 0:
        if friendly and not is_debug_enabled():
            summary = (
                failure_hint.summary
                if failure_hint is not None
                else f"Command failed with exit code {result.returncode}."
            )
            _print_friendly_failure(
                summary=summary,
                command=command_for_display,
                next_steps=failure_hint.next_steps if failure_hint else (),
                details=failure_hint.details if failure_hint else None,
            )
            raise typer.Exit(result.returncode)
        raise subprocess.CalledProcessError(
            result.returncode,
            result.args,
            output=result.stdout,
            stderr=result.stderr,
        )

    return result
