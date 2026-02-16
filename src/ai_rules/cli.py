"""ai-rules CLI — unified rules management tool."""

from typing import Annotated

import typer
from rich.console import Console

from ai_rules import __version__
from ai_rules.commands.new import new as new_command

console = Console()

app = typer.Typer(
    name="ai-rules",
    help="Unified CLI for AI coding rules management.",
    no_args_is_help=True,
)

# Register subcommands
app.command(name="new")(new_command)


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
