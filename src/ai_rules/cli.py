"""ai-rules CLI — unified rules management tool."""

from typing import Annotated

import typer

from ai_rules import __version__
from ai_rules._shared.console import console
from ai_rules.commands.badges import badges_app
from ai_rules.commands.deploy import deploy
from ai_rules.commands.index import index_app
from ai_rules.commands.keywords import keywords
from ai_rules.commands.new import new as new_command
from ai_rules.commands.refs import refs_app
from ai_rules.commands.tokens import tokens
from ai_rules.commands.validate import validate

app = typer.Typer(
    name="ai-rules",
    help="Unified CLI for AI coding rules management.",
    no_args_is_help=True,
)

# Register commands
app.add_typer(badges_app, name="badges")
app.add_typer(refs_app, name="refs")
app.command(name="new")(new_command)
app.command(name="tokens")(tokens)
app.command(name="deploy")(deploy)
app.add_typer(index_app, name="index")
app.command(name="keywords")(keywords)
app.command(name="validate")(validate)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"ai-rules {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Unified CLI for AI coding rules management."""
