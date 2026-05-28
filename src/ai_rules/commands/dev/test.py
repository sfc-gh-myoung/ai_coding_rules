"""Dev test subcommand — run pytest with optional coverage."""

from __future__ import annotations

import webbrowser
from pathlib import Path
from typing import Annotated

import typer

from ai_rules._shared.console import console, log_success
from ai_rules._shared.paths import find_project_root
from ai_rules._shared.runner import CommandFailureHint, run

tests_app = typer.Typer(name="test", help="Run the test suite.", no_args_is_help=True)


@tests_app.command("run")
def test_run(
    coverage: Annotated[
        bool,
        typer.Option("--coverage/--no-coverage", help="Run with coverage report."),
    ] = False,
    open_report: Annotated[
        bool,
        typer.Option("--open", help="Open HTML coverage report in browser after run."),
    ] = False,
) -> None:
    """Run all pytest tests.

    Use --coverage to collect a coverage report, --open to open it in a browser.
    """
    root = find_project_root()

    if coverage or open_report:
        console.print("[blue]→[/blue] Running tests with coverage...")
        run(
            [
                "uv",
                "run",
                "pytest",
                "--cov=src/ai_rules",
                "--cov-report=term-missing",
                "--cov-report=html",
                "tests/",
            ],
            cwd=root,
            failure_hint=CommandFailureHint(
                summary="Tests with coverage failed.",
                next_steps=(
                    "uv run ai-rules dev test run",
                    "uv run ai-rules dev test run --coverage",
                ),
            ),
            display_command=["uv", "run", "ai-rules", "dev", "test", "run", "--coverage"],
        )
        log_success("Tests passed.")
        if open_report:
            html_report = root / "htmlcov" / "index.html"
            console.print(f"[blue]→[/blue] Opening coverage report: {html_report.as_uri()}")
            webbrowser.open(html_report.resolve().as_uri())
    else:
        console.print("[blue]→[/blue] Running tests...")
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
        log_success("Tests passed.")


def run_tests(root: Path, *, coverage: bool = False) -> int:
    """Run pytest programmatically; return exit code.

    Suitable for use by orchestrate.py without spawning a new process.
    """
    cmd = ["uv", "run", "pytest"]
    if coverage:
        cmd += [
            "--cov=src/ai_rules",
            "--cov-report=term-missing",
            "--cov-report=html",
        ]
    else:
        cmd += ["--tb=short"]
    cmd += ["tests/"]

    result = run(cmd, cwd=root, check=False, friendly=False)
    return result.returncode
