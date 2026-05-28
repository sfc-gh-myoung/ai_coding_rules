"""Dev orchestrate — validate and ci commands."""

from __future__ import annotations

import sys
from pathlib import Path

import typer

from ai_rules._shared.console import console, err_console, log_success
from ai_rules._shared.paths import find_project_root
from ai_rules._shared.runner import CommandFailureHint, run
from ai_rules.commands.dev.quality import _run_format, _run_lint, _run_markdown, _run_typecheck


def _run_validate_pipeline(root: Path) -> int:
    """Run the full validation pipeline; return number of failures."""
    failures: list[str] = []

    steps: list[tuple[str, list, str]] = [
        (
            "validate rules/",
            ["uv", "run", "ai-rules", "validate", "rules/"],
            "uv run ai-rules validate rules/",
        ),
        (
            "validate rules/examples/",
            ["uv", "run", "ai-rules", "validate", "rules/examples/", "--examples"],
            "uv run ai-rules validate rules/examples/ --examples",
        ),
        (
            "validate templates/",
            ["uv", "run", "ai-rules", "validate", "templates/", "--templates"],
            "uv run ai-rules validate templates/ --templates",
        ),
    ]

    for label, cmd, next_step in steps:
        console.print(f"[blue]→[/blue] Running {label}...")
        result = run(cmd, cwd=root, check=False)
        if result.returncode != 0:
            failures.append(label)
            err_console.print(f"[red]✗[/red] {label} failed (exit {result.returncode})")
            err_console.print(f"  Next step: [bold]{next_step}[/bold]")

    return len(failures)


def run_validate(root: Path | None = None) -> None:
    """Run the full dev validate pipeline.

    Steps (in order):
    1. preflight
    2. quality (all checks)
    3. test
    4. validate rules/, rules/examples/, templates/

    Raises:
        SystemExit: If any step fails.
    """
    if root is None:
        root = find_project_root()

    console.print("[bold blue]Running full validation pipeline...[/bold blue]")
    console.print("")

    console.print("[bold]Step 1: Preflight[/bold]")
    try:
        import shutil as _shutil

        if _shutil.which("uv") is None:
            err_console.print("[red]✗[/red] uv not found.")
            raise typer.Exit(1)
        if not (root / "pyproject.toml").exists():
            err_console.print("[red]✗[/red] pyproject.toml not found.")
            raise typer.Exit(1)
        console.print("[green]✓[/green] Preflight passed.")
    except SystemExit:
        raise

    console.print("")
    console.print("[bold]Step 2: Quality checks[/bold]")
    _run_lint(root, fix=False)
    _run_format(root, fix=False)
    _run_typecheck(root)
    _run_markdown(root, fix=False)
    console.print("[green]✓[/green] Quality checks passed.")

    console.print("")
    console.print("[bold]Step 3: Tests[/bold]")
    run(
        ["uv", "run", "pytest", "tests/", "--tb=short"],
        cwd=root,
        failure_hint=CommandFailureHint(
            summary="Tests failed.",
            next_steps=(
                "uv run ai-rules dev test run",
                "Inspect pytest output above, then rerun the failing test by path if needed.",
            ),
        ),
        display_command=["uv", "run", "ai-rules", "dev", "test", "run"],
    )
    console.print("[green]✓[/green] Tests passed.")

    console.print("")
    console.print("[bold]Step 4: Schema validation[/bold]")
    failures = _run_validate_pipeline(root)
    if failures:
        err_console.print(f"\n[red]✗[/red] {failures} validation step(s) failed.")
        sys.exit(1)
    console.print("[green]✓[/green] Validation passed.")

    console.print("")
    log_success("All validation checks passed!")
