"""Dev quality subcommand — code quality checks and auto-fix."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Annotated

import typer

from ai_rules._shared.console import console, log_success
from ai_rules._shared.paths import find_project_root
from ai_rules._shared.runner import CommandFailureHint, run

quality_app = typer.Typer(
    name="quality",
    help="Code quality checks (lint, format, typecheck, markdown).",
    no_args_is_help=True,
)


def _dev_config(root: Path) -> dict:
    """Read [tool.ai_rules.dev] from pyproject.toml."""
    pyproject = root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)
    return data.get("tool", {}).get("ai_rules", {}).get("dev", {})


def _markdown_targets(root: Path) -> tuple[list[str], list[str]]:
    """Return (rules_targets, docs_targets) from config."""
    cfg = _dev_config(root)
    rules = cfg.get(
        "markdown_rules_targets",
        [
            "rules/",
            "templates/AGENTS_MODE.md.template",
            "templates/AGENTS_NO_MODE.md.template",
        ],
    )
    docs = cfg.get(
        "markdown_docs_targets",
        ["docs/", "README.md", "CONTRIBUTING.md", "CHANGELOG.md"],
    )
    return rules, docs


@quality_app.command("all")
def quality_all(
    fix: Annotated[bool, typer.Option("--fix", help="Auto-fix all fixable issues.")] = False,
) -> None:
    """Run all quality checks (lint, format, typecheck, markdown).

    Pass --fix to auto-fix lint, format, and markdown issues.
    """
    root = find_project_root()
    _run_lint(root, fix=fix)
    _run_format(root, fix=fix)
    _run_typecheck(root)
    _run_markdown(root, fix=fix)
    log_success("All quality checks passed.")


@quality_app.command("lint")
def quality_lint(
    fix: Annotated[bool, typer.Option("--fix", help="Auto-fix lint issues.")] = False,
) -> None:
    """Run ruff linter."""
    root = find_project_root()
    _run_lint(root, fix=fix)
    log_success("Lint passed.")


@quality_app.command("format")
def quality_format(
    fix: Annotated[bool, typer.Option("--fix", help="Apply formatting.")] = False,
) -> None:
    """Run ruff formatter."""
    root = find_project_root()
    _run_format(root, fix=fix)
    log_success("Format check passed.")


@quality_app.command("typecheck")
def quality_typecheck() -> None:
    """Run ty type checker."""
    root = find_project_root()
    _run_typecheck(root)
    log_success("Type check passed.")


@quality_app.command("markdown")
def quality_markdown(
    fix: Annotated[bool, typer.Option("--fix", help="Auto-fix markdown issues.")] = False,
) -> None:
    """Run pymarkdownlnt Markdown linter."""
    root = find_project_root()
    _run_markdown(root, fix=fix)
    log_success("Markdown check passed.")


def _run_lint(root: Path, *, fix: bool) -> None:
    """Execute ruff check."""
    cmd = ["uv", "run", "ruff", "check"]
    if fix:
        cmd.append("--fix")
    cmd.append(".")
    label = "lint (fix)" if fix else "lint"
    console.print(f"[blue]→[/blue] Running {label}...")
    hint = (
        CommandFailureHint(
            summary="Lint auto-fix failed.",
            next_steps=("Inspect the Ruff output above.", "uv run ai-rules dev quality lint"),
        )
        if fix
        else CommandFailureHint(
            summary="Lint failed.",
            next_steps=(
                "uv run ai-rules dev quality lint --fix",
                "uv run ai-rules dev validate",
            ),
        )
    )
    run(
        cmd,
        cwd=root,
        failure_hint=hint,
        display_command=["uv", "run", "ai-rules", "dev", "quality", "lint"]
        + (["--fix"] if fix else []),
    )


def _run_format(root: Path, *, fix: bool) -> None:
    """Execute ruff format."""
    cmd = ["uv", "run", "ruff", "format"]
    if not fix:
        cmd.append("--check")
    cmd.append(".")
    label = "format (fix)" if fix else "format check"
    console.print(f"[blue]→[/blue] Running {label}...")
    hint = (
        CommandFailureHint(
            summary="Format failed.",
            next_steps=("uv run ai-rules dev quality format",),
        )
        if fix
        else CommandFailureHint(
            summary="Format check failed: Ruff found files that need formatting.",
            next_steps=(
                "uv run ai-rules dev quality format --fix",
                "uv run ai-rules dev validate",
            ),
        )
    )
    run(
        cmd,
        cwd=root,
        failure_hint=hint,
        display_command=["uv", "run", "ai-rules", "dev", "quality", "format"]
        + (["--fix"] if fix else []),
    )


def _run_typecheck(root: Path) -> None:
    """Execute ty check."""
    console.print("[blue]→[/blue] Running typecheck...")
    run(
        ["uv", "run", "ty", "check", "."],
        cwd=root,
        failure_hint=CommandFailureHint(
            summary="Type check failed.",
            next_steps=(
                "Review the first ty diagnostic above.",
                "uv run ai-rules dev quality typecheck",
            ),
        ),
        display_command=["uv", "run", "ai-rules", "dev", "quality", "typecheck"],
    )


def _markdown_failure_hint(*, fix: bool) -> CommandFailureHint:
    """Return user-facing remediation for markdown check failures."""
    if fix:
        return CommandFailureHint(
            summary="Markdown auto-fix failed.",
            next_steps=(
                "Inspect the pymarkdownlnt output above.",
                "uv run ai-rules dev quality markdown",
            ),
        )
    return CommandFailureHint(
        summary="Markdown check failed.",
        next_steps=(
            "uv run ai-rules dev quality markdown --fix",
            "uv run ai-rules dev validate",
        ),
    )


def _run_markdown(root: Path, *, fix: bool) -> None:
    """Execute pymarkdownlnt on rules and docs targets."""
    rules_targets, docs_targets = _markdown_targets(root)
    verb = "fix" if fix else "scan"

    if rules_targets:
        cmd = [
            "uv",
            "run",
            "pymarkdownlnt",
            "--config",
            "pymarkdown.rules.json",
            verb,
            *rules_targets,
        ]
        console.print(f"[blue]→[/blue] Markdown {verb} (rules)...")
        run(
            cmd,
            cwd=root,
            failure_hint=_markdown_failure_hint(fix=fix),
            display_command=["uv", "run", "ai-rules", "dev", "quality", "markdown"]
            + (["--fix"] if fix else []),
        )

    if docs_targets:
        cmd = [
            "uv",
            "run",
            "pymarkdownlnt",
            "--config",
            "pymarkdown.docs.json",
            verb,
            *docs_targets,
        ]
        console.print(f"[blue]→[/blue] Markdown {verb} (docs)...")
        run(
            cmd,
            cwd=root,
            failure_hint=_markdown_failure_hint(fix=fix),
            display_command=["uv", "run", "ai-rules", "dev", "quality", "markdown"]
            + (["--fix"] if fix else []),
        )
