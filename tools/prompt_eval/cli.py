"""CLI for prompt evaluation tool."""

import logging
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .cortex import CortexConfig, CortexError
from .evaluator import PromptEvaluator
from .formatters import format_html, format_json, format_markdown
from .models import (
    DEFAULT_MODEL,
    SUPPORTED_MODELS,
    EvaluationReport,
)
from .rewriter import PromptRewriter

console = Console()
err_console = Console(stderr=True)

RESULTS_DIR = Path(__file__).parent / "results"

app = typer.Typer(
    name="prompt-eval",
    help="Prompt Evaluation CLI - Analyze and improve prompts for LLM/agent execution",
    no_args_is_help=True,
)


def print_header() -> None:
    """Print application header."""
    header = f"[bold magenta]prompt-eval[/bold magenta] [dim]v{__version__}[/dim]"
    subtitle = "[cyan]Universal Prompt Evaluation Tool[/cyan]"
    console.print()
    console.print(
        Panel(
            f"{header}\n{subtitle}",
            box=box.DOUBLE_EDGE,
            border_style="bright_blue",
            padding=(0, 2),
        )
    )


def log_info(message: str) -> None:
    """Log informational message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def log_success(message: str) -> None:
    """Log success message."""
    console.print(f"[green]✓[/green] {message}")


def log_error(message: str) -> None:
    """Log error message."""
    err_console.print(f"[red]✗[/red] {message}")


def read_prompt_input(source: str) -> str:
    """Read prompt from file or stdin.

    Args:
        source: File path or '-' for stdin.

    Returns:
        Prompt text.
    """
    if source == "-":
        # Read from stdin
        if sys.stdin.isatty():
            log_error("No input provided. Pipe text or specify a file.")
            raise typer.Exit(1)
        return sys.stdin.read().strip()
    else:
        # Read from file
        path = Path(source)
        if not path.exists():
            log_error(f"File not found: {path}")
            raise typer.Exit(1)
        return path.read_text().strip()


def save_result(report: EvaluationReport, format_type: str) -> Path:
    """Save evaluation result to file.

    Args:
        report: Evaluation report.
        format_type: Output format (markdown, json, html).

    Returns:
        Path to saved file.
    """
    RESULTS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_id = report.id or str(uuid.uuid4())[:8]

    ext_map = {"markdown": "md", "json": "json", "html": "html"}
    ext = ext_map.get(format_type, "md")

    filename = f"{timestamp}_{report_id}.{ext}"
    filepath = RESULTS_DIR / filename

    if format_type == "json":
        content = format_json(report)
    elif format_type == "html":
        content = format_html(report)
    else:
        content = format_markdown(report)

    filepath.write_text(content)
    return filepath


@app.command()
def eval(
    source: Annotated[
        str,
        typer.Argument(help="Prompt file path or '-' for stdin"),
    ],
    format: Annotated[
        str,
        typer.Option("-f", "--format", help="Output format: markdown, json, html"),
    ] = "markdown",
    model: Annotated[
        str,
        typer.Option("-m", "--model", help="Cortex model for analysis"),
    ] = DEFAULT_MODEL,
    connection: Annotated[
        str,
        typer.Option("-c", "--connection", help="Snowflake connection name"),
    ] = "default",
    rewrite: Annotated[
        bool,
        typer.Option("-r", "--rewrite/--no-rewrite", help="Generate improved prompt"),
    ] = True,
    save: Annotated[
        bool,
        typer.Option("-s", "--save", help="Save results to file"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("-v", "--verbose", help="Show detailed output"),
    ] = False,
) -> None:
    """Evaluate a prompt for agent execution quality.

    Analyzes the prompt across 6 dimensions and optionally generates
    an improved version optimized for cross-agent compatibility.

    Examples:
        prompt-eval eval prompt.txt
        echo "Write code" | prompt-eval eval -
        prompt-eval eval prompt.md --format json --save
    """
    print_header()

    # Validate format
    format = format.lower()
    if format not in ("markdown", "json", "html"):
        log_error(f"Invalid format: {format}. Use: markdown, json, html")
        raise typer.Exit(1)

    # Read input
    log_info(f"Reading prompt from: {'stdin' if source == '-' else source}")
    prompt_text = read_prompt_input(source)

    if not prompt_text:
        log_error("Empty prompt provided")
        raise typer.Exit(1)

    if verbose:
        log_info(f"Prompt length: {len(prompt_text)} characters")
        log_info(f"Model: {model}")
        log_info(f"Connection: {connection}")

    # Evaluate
    console.print()

    try:
        CortexConfig(connection_name=connection, model=model)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # Evaluate
            task = progress.add_task("Evaluating prompt...", total=None)

            with PromptEvaluator(model=model, connection_name=connection) as evaluator:
                evaluation = evaluator.evaluate(prompt_text)

            progress.update(task, description="[green]Evaluation complete[/green]")

            # Rewrite if requested
            improved = None
            if rewrite:
                progress.update(task, description="Generating improved prompt...")

                with PromptRewriter(model=model, connection_name=connection) as rewriter:
                    improved = rewriter.rewrite(prompt_text, evaluation)

                progress.update(task, description="[green]Improvement complete[/green]")

        # Build report
        report = EvaluationReport(
            evaluation=evaluation,
            improved=improved,
            id=str(uuid.uuid4())[:8],
        )

        # Output results
        console.print()

        if format == "json":
            output = format_json(report)
        elif format == "html":
            output = format_html(report)
        else:
            output = format_markdown(report)

        # For markdown, use rich rendering; otherwise print raw
        if format == "markdown":
            from rich.markdown import Markdown

            console.print(Markdown(output))
        else:
            console.print(output)

        # Save if requested
        if save:
            filepath = save_result(report, format)
            log_success(f"Saved: {filepath}")

        # Summary
        console.print()
        grade_color = {
            "A": "green",
            "B": "blue",
            "C": "yellow",
            "D": "orange3",
            "F": "red",
        }.get(evaluation.grade, "white")

        console.print(
            Panel(
                f"[bold]Score:[/bold] [{grade_color}]{evaluation.total_score:.1f}/{evaluation.max_score:.1f}[/] "
                f"([{grade_color}]{evaluation.grade}[/])\n"
                f"[bold]Issues:[/bold] {len(evaluation.all_issues)}",
                title="Summary",
                border_style=grade_color,
            )
        )

    except CortexError as e:
        log_error(f"Cortex error: {e}")
        raise typer.Exit(1) from None
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(1) from None


@app.command()
def models(
    connection: Annotated[
        str,
        typer.Option("-c", "--connection", help="Snowflake connection name"),
    ] = "default",
) -> None:
    """List available Cortex models."""
    print_header()

    table = Table(title="Available Models", box=box.ROUNDED)
    table.add_column("Model", style="cyan")
    table.add_column("Provider", style="yellow")
    table.add_column("Default", style="green")

    providers = {
        "claude": "Anthropic",
        "openai": "OpenAI",
        "llama": "Meta",
        "mistral": "Mistral",
        "snowflake": "Snowflake",
        "deepseek": "DeepSeek",
    }

    for model in SUPPORTED_MODELS:
        provider = "Unknown"
        for prefix, name in providers.items():
            if model.lower().startswith(prefix):
                provider = name
                break

        is_default = "✓" if model == DEFAULT_MODEL else ""
        table.add_row(model, provider, is_default)

    console.print()
    console.print(table)
    console.print()
    log_info(f"Default model: {DEFAULT_MODEL}")


@app.command()
def api(
    host: Annotated[
        str,
        typer.Option("--host", "-h", help="Host to bind to"),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to bind to"),
    ] = 8000,
    reload: Annotated[
        bool,
        typer.Option("--reload", help="Enable auto-reload for development"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Enable debug logging (timestamps, Cortex API calls)"),
    ] = False,
) -> None:
    """Start the FastAPI server with web UI.

    Launches a web interface for evaluating prompts interactively.

    Examples:
        prompt-eval api
        prompt-eval api --port 8080 --host 0.0.0.0
        prompt-eval api --debug
    """
    log_level = "DEBUG" if debug else "INFO"
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    print_header()

    log_info(f"Starting server at http://{host}:{port}")
    if debug:
        log_info("Debug logging enabled")
    log_info("Press Ctrl+C to stop")
    console.print()

    try:
        import uvicorn

        uvicorn.run(
            "tools.prompt_eval.api:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level.lower(),
        )
    except ImportError:
        log_error("uvicorn not installed. Install with: pip install uvicorn")
        raise typer.Exit(1) from None
    except Exception as e:
        log_error(f"Server error: {e}")
        raise typer.Exit(1) from None


if __name__ == "__main__":
    app()
