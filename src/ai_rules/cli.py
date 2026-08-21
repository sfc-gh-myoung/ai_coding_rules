"""ai-rules CLI: unified rules management tool."""

from typing import Annotated

import typer

from ai_rules import __version__
from ai_rules._shared.console import console
from ai_rules._shared.runtime import set_debug
from ai_rules.commands.badges import badges_app
from ai_rules.commands.new import new as new_command
from ai_rules.commands.plugin import plugin_app
from ai_rules.commands.review_artifact import review_artifact_app
from ai_rules.commands.rule_loader import rule_loader_app
from ai_rules.commands.tokens import tokens
from ai_rules.commands.validate import validate
from ai_rules.commands.validate_skills import validate_skills

app = typer.Typer(
    name="ai-rules",
    help="Unified CLI for AI coding rules management.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

# Register commands
app.add_typer(badges_app, name="badges")
app.command(name="new")(new_command)
app.command(name="tokens", no_args_is_help=True)(tokens)
app.command(name="validate")(validate)
app.command(name="validate-skills", no_args_is_help=True)(validate_skills)
app.add_typer(rule_loader_app, name="rule-loader")
app.add_typer(plugin_app, name="plugin")
app.add_typer(review_artifact_app, name="review-artifact")


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
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Show Python tracebacks for internal command failures."),
    ] = False,
) -> None:
    """Unified CLI for AI coding rules management."""
    set_debug(debug)
