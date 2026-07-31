"""Dev subapp — development orchestration (replaces former Makefile)."""

from __future__ import annotations

import typer

from ai_rules.commands.dev.clean import clean_app
from ai_rules.commands.dev.env import env_app
from ai_rules.commands.dev.mirror import mirror_app
from ai_rules.commands.dev.orchestrate import run_validate
from ai_rules.commands.dev.quality import quality_app
from ai_rules.commands.dev.release import release_app
from ai_rules.commands.dev.status import status_app
from ai_rules.commands.dev.test import tests_app

dev_app = typer.Typer(
    name="dev",
    help="Development orchestration (replaces former Makefile).",
    no_args_is_help=True,
)

dev_app.add_typer(env_app, name="env")
dev_app.add_typer(quality_app, name="quality")
dev_app.add_typer(tests_app, name="test")
dev_app.add_typer(clean_app, name="clean")
dev_app.add_typer(status_app, name="status")
dev_app.add_typer(release_app, name="release")
dev_app.add_typer(mirror_app, name="mirror")


@dev_app.command("validate")
def dev_validate() -> None:
    """Run the full validation pipeline (quality + tests + schema)."""
    run_validate()


@dev_app.command("ci")
def dev_ci() -> None:
    """CI pipeline entry point — alias for validate."""
    run_validate()
