"""Mirror commands — squash-sync current main to GitLab mirror.

Subcommand:
- ``sync [--dry-run]`` — orphan-commit + force-push current main to gitlab remote.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ai_rules._shared.runner import CommandFailureHint, run

mirror_app = typer.Typer(
    name="mirror",
    help="Squash-sync main to GitLab mirror.",
    no_args_is_help=True,
)


def _run(cmd: list[str], *, dry_run: bool) -> None:
    """Print and optionally execute a command."""
    display = " ".join(cmd)
    if dry_run:
        typer.echo(f"  [DRY RUN] {display}")
        return
    run(
        cmd,
        failure_hint=CommandFailureHint(
            summary="Mirror command failed.",
            next_steps=(
                "Inspect the git output above.",
                "git status",
                "Verify the gitlab remote is configured.",
            ),
        ),
    )


def _capture(cmd: list[str]) -> str:
    """Run a command and return stripped stdout."""
    result = run(cmd, capture=True, check=False, friendly=False)
    return result.stdout.strip()


def _assert_clean_working_tree(dry_run: bool) -> None:
    """Abort if there are uncommitted changes."""
    if dry_run:
        return
    result = run(["git", "diff", "--quiet", "HEAD"], check=False, friendly=False)
    if result.returncode != 0:
        typer.echo(
            "ERROR: Uncommitted changes detected. Commit or stash first.",
            err=True,
        )
        raise typer.Exit(1)


def _project_version() -> str:
    """Read project version from pyproject.toml."""
    try:
        import tomllib

        pyproject = Path("pyproject.toml")
        with pyproject.open("rb") as fh:
            data = tomllib.load(fh)
        return data.get("project", {}).get("version", "unknown")
    except Exception:
        return "unknown"


@mirror_app.command("sync")
def mirror_sync(
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Print commands without executing.")
    ] = False,
) -> None:
    """Squash-sync current main to GitLab mirror via orphan commit + force push."""
    _assert_clean_working_tree(dry_run)

    version = _project_version()
    github_sha = _capture(["git", "rev-parse", "--short", "main"]) if not dry_run else "HEAD"

    if dry_run:
        typer.echo(f"DRY RUN -- mirror v{version}")
        typer.echo("  Verify clean working tree")
        typer.echo("  Delete local _gitlab-sync branch if it exists")
        typer.echo("  Create orphan branch _gitlab-sync")
        typer.echo("  Create signed mirror commit")
        typer.echo("  Force push _gitlab-sync to gitlab/main")
        typer.echo("  Checkout main")
        typer.echo("  Delete local _gitlab-sync branch")
        return

    typer.echo(f"Syncing v{version} to GitLab mirror ({github_sha})...")

    # Delete branch if it already exists (ignore errors)
    run(
        ["git", "branch", "-D", "_gitlab-sync"],
        check=False,
        capture=True,
        friendly=False,
    )

    _run(["git", "checkout", "--orphan", "_gitlab-sync"], dry_run=dry_run)
    _run(
        ["git", "commit", "-S", "-m", f"mirror: v{version} ({github_sha})"],
        dry_run=dry_run,
    )
    _run(["git", "push", "gitlab", "HEAD:main", "--force"], dry_run=dry_run)
    _run(["git", "checkout", "main"], dry_run=dry_run)

    # Clean up branch
    run(
        ["git", "branch", "-D", "_gitlab-sync"],
        check=False,
        capture=True,
        friendly=False,
    )

    typer.echo(f"GitLab mirror synced: v{version} ({github_sha})")
