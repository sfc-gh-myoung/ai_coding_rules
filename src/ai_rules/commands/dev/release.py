"""Release commands — bump version and create signed releases.

Subcommands:
- ``bump VERSION [--dry-run]``  — bump version on the current release branch and push.
- ``merge VERSION [--dry-run]`` — squash-merge release branch into main, tag, publish.
"""

from __future__ import annotations

import contextlib
import os
import re
import tempfile
from pathlib import Path
from typing import Annotated

import typer

from ai_rules._shared.console import err_console
from ai_rules._shared.runner import CommandFailureHint, run

release_app = typer.Typer(
    name="release",
    help="Bump version and create signed release commits.",
    no_args_is_help=True,
)

VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+([.-][A-Za-z0-9]+)?$")
PYPROJECT_VERSION_LINE_RE = re.compile(r'^version = "[^"]*"$', re.MULTILINE)
README_BADGE_RE = re.compile(r"badge/version-[0-9]+\.[0-9]+\.[0-9]+(?:[.-][A-Za-z0-9]+)?")


# ---------------------------------------------------------------------------
# Inlined version-bump helpers (formerly scripts/bump_version.py)
# ---------------------------------------------------------------------------


def _atomic_write(path: Path, text: str) -> None:
    """Write text to path atomically via tempfile + os.replace."""
    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(directory))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp_name, path)
    except Exception:
        with contextlib.suppress(OSError):
            os.unlink(tmp_name)
        raise


def _replace_pyproject_version(path: Path, version: str) -> str:
    """Return new pyproject.toml text with version replaced, or ERROR: prefix on failure."""
    if not path.is_file():
        return f"ERROR: {path} not found"
    text = path.read_text(encoding="utf-8")
    matches = PYPROJECT_VERSION_LINE_RE.findall(text)
    if len(matches) != 1:
        return (
            f"ERROR: expected exactly one 'version = \"...\"' line in {path}, found {len(matches)}"
        )
    new_text = PYPROJECT_VERSION_LINE_RE.sub(f'version = "{version}"', text, count=1)
    if new_text == text:
        return f"ERROR: failed to replace version in {path}"
    return new_text


def _replace_readme_badge(path: Path, version: str) -> tuple[str | None, str | None]:
    """Return (new_text, message). new_text is None if no badge present."""
    if not path.is_file():
        return None, f"WARNING: {path} not found; skipping README badge update"
    text = path.read_text(encoding="utf-8")
    matches = README_BADGE_RE.findall(text)
    if not matches:
        return None, f"WARNING: no version badge found in {path}; skipping"
    if len(matches) > 1:
        return None, f"ERROR: expected one badge token in {path}, found {len(matches)}"
    new_text = README_BADGE_RE.sub(f"badge/version-{version}", text, count=1)
    return new_text, None


def _bump_version_files(version: str, *, cwd: Path | None = None) -> None:
    """Atomically bump pyproject.toml and README.md to ``version``.

    Raises ``typer.Exit(1)`` on any validation or write failure.
    """
    root = cwd or Path.cwd()
    pyproject = root / "pyproject.toml"
    readme = root / "README.md"

    pyproject_result = _replace_pyproject_version(pyproject, version)
    if pyproject_result.startswith("ERROR:"):
        err_console.print(pyproject_result)
        raise typer.Exit(1)

    readme_new, readme_msg = _replace_readme_badge(readme, version)
    if readme_msg and readme_msg.startswith("ERROR:"):
        err_console.print(readme_msg)
        raise typer.Exit(1)

    try:
        _atomic_write(pyproject, pyproject_result)
        if readme_new is not None:
            _atomic_write(readme, readme_new)
    except OSError as exc:
        err_console.print(f"ERROR: write failed: {exc}")
        raise typer.Exit(1) from exc

    if readme_msg:
        err_console.print(readme_msg)
    typer.echo(f"Bumped version to {version}")


# ---------------------------------------------------------------------------
# Release helpers
# ---------------------------------------------------------------------------


def _validate_version(version: str) -> str:
    """Validate semantic version string."""
    if not VERSION_RE.match(version):
        typer.echo(f"ERROR: Invalid version format: {version!r}. Expected X.Y.Z", err=True)
        raise typer.Exit(1)
    return version


def _run(cmd: list[str], *, dry_run: bool, cwd: Path | None = None) -> None:
    """Print and optionally execute a command."""
    display = " ".join(cmd)
    if dry_run:
        typer.echo(f"  [DRY RUN] {display}")
        return
    run(
        cmd,
        cwd=cwd,
        failure_hint=CommandFailureHint(
            summary="Release command failed.",
            next_steps=(
                "Inspect the git or GitHub CLI output above.",
                "git status",
                "Rerun with --dry-run to preview commands.",
            ),
        ),
    )


def _current_branch() -> str:
    """Return the current git branch name."""
    result = run(
        ["git", "branch", "--show-current"],
        capture=True,
        check=False,
        friendly=False,
    )
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@release_app.command("bump")
def release_bump(
    version: Annotated[str, typer.Argument(help="Version to release (X.Y.Z).")],
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Print commands without executing.")
    ] = False,
) -> None:
    """Bump version on the current release branch and push.

    Equivalent to (formerly): ``make release VERSION=X.Y.Z``.
    """
    _validate_version(version)
    branch = _current_branch()

    if dry_run:
        typer.echo(f"DRY RUN -- Release branch prep v{version}")
        typer.echo(f'  pyproject.toml: version = "?" -> "{version}"')
        typer.echo(f"  README.md:      badge/version-? -> badge/version-{version}")
        typer.echo(f"  Commit:         chore: bump version to {version}")
        typer.echo(f"  Push:           origin {branch}")
        return

    typer.echo(f"Bumping version to v{version} on {branch}...")
    _bump_version_files(version)
    _run(["git", "add", "pyproject.toml", "README.md"], dry_run=dry_run)
    _run(["git", "commit", "-S", "-m", f"chore: bump version to {version}"], dry_run=dry_run)
    _run(["git", "push", "origin", "HEAD"], dry_run=dry_run)
    typer.echo(f"Version bumped. Run 'ai-rules dev release merge {version}' when ready.")


@release_app.command("merge")
def release_merge(
    version: Annotated[str, typer.Argument(help="Version to merge (X.Y.Z).")],
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Print commands without executing.")
    ] = False,
) -> None:
    """Squash-merge release branch into main, tag, and create GitHub release.

    Must be run from the ``release/vX.Y.Z`` branch, not main.
    """
    _validate_version(version)
    branch = _current_branch()

    if not dry_run and branch == "main":
        typer.echo(
            f"ERROR: Run from release/v{version}, not main.",
            err=True,
        )
        raise typer.Exit(1)

    if dry_run:
        typer.echo(f"DRY RUN -- release-merge v{version}")
        typer.echo("  Branch check: abort if current branch is main")
        typer.echo("  Checkout: main")
        typer.echo("  Pull: origin main")
        typer.echo(f"  Squash merge: release/v{version} into main with -X theirs")
        typer.echo(f"  Commit: chore: squash merge release/v{version} into main")
        typer.echo(f"  Tag: v{version}")
        typer.echo(f"  Push: origin main and refs/tags/v{version}")
        typer.echo(f"  GitHub: gh release create v{version} --draft --generate-notes")
        return

    _run(["git", "checkout", "main"], dry_run=dry_run)
    _run(["git", "pull", "origin", "main"], dry_run=dry_run)
    _run(
        ["git", "merge", "--squash", "-X", "theirs", f"release/v{version}"],
        dry_run=dry_run,
    )
    _run(
        [
            "git",
            "commit",
            "-S",
            "-m",
            f"chore: squash merge release/v{version} into main",
        ],
        dry_run=dry_run,
    )
    _run(["git", "tag", "-s", f"v{version}", "-m", f"Release {version}"], dry_run=dry_run)
    _run(["git", "push", "origin", "main"], dry_run=dry_run)
    _run(["git", "push", "origin", f"refs/tags/v{version}"], dry_run=dry_run)
    _run(
        [
            "gh",
            "release",
            "create",
            f"v{version}",
            "--title",
            f"v{version}",
            "--draft",
            "--generate-notes",
        ],
        dry_run=dry_run,
    )
    typer.echo(f"Release v{version} complete! Run 'ai-rules dev mirror sync' to sync GitLab.")
