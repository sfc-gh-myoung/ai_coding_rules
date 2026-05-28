"""Dev status subcommand — project status summary."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import typer

from ai_rules._shared.console import console
from ai_rules._shared.paths import find_project_root

status_app = typer.Typer(name="status", help="Show project status summary.", no_args_is_help=True)


def _count_glob(root: Path, pattern: str) -> int:
    """Count files matching pattern under root."""
    return len(list(root.glob(pattern)))


def _run_version(cmd: list[str]) -> str:
    """Run a version command and return first line of output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False, shell=False)
        return result.stdout.strip().splitlines()[0] if result.stdout.strip() else "not found"
    except (FileNotFoundError, IndexError):
        return "not found"


@status_app.command("show")
def status_show() -> None:
    """Show project status summary (rule counts, tool versions)."""
    root = find_project_root()

    rules_count = _count_glob(root, "rules/*.md")
    examples_count = _count_glob(root, "rules/examples/*.md")
    skills_count = _count_glob(root, "skills/*.md")
    test_count = len(list(root.rglob("test_*.py")))

    python_ver = _run_version(["python", "--version"])
    uv_ver = _run_version(["uv", "--version"])

    sep = "═" * 68
    console.print(f"[bold]{sep}[/bold]")
    console.print("[bold]AI Coding Rules — Project Status[/bold]")
    console.print(f"[bold]{sep}[/bold]")
    console.print("")
    console.print(f"  Rules:    [cyan]{rules_count}[/cyan] files in rules/")
    console.print(f"  Examples: [cyan]{examples_count}[/cyan] files in rules/examples/")
    console.print(f"  Skills:   [cyan]{skills_count}[/cyan] files in skills/")
    console.print(f"  Tests:    [cyan]{test_count}[/cyan] test files")
    console.print("")
    console.print(f"  Python:   [green]{python_ver}[/green]")
    console.print(f"  uv:       [green]{uv_ver}[/green]")
    console.print("")


@status_app.command("preflight")
def preflight() -> None:
    """Verify the environment is ready for development."""
    root = find_project_root()
    ok = True

    if shutil.which("uv") is None:
        console.print("[red]✗[/red] uv not found. Install: https://docs.astral.sh/uv/")
        ok = False
    else:
        console.print("[green]✓[/green] uv found")

    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        console.print("[red]✗[/red] pyproject.toml not found. Run from project root.")
        ok = False
    else:
        console.print("[green]✓[/green] pyproject.toml found")

    if not ok:
        raise typer.Exit(1)

    console.print("[green]✓[/green] Environment ready.")
