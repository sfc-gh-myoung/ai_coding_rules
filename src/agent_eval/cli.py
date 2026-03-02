"""CLI commands for AGENTS.md evaluation tool."""

import hashlib
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.syntax import Syntax
from rich.table import Table

from agent_eval import __app_name__, __version__
from agent_eval.cortex import list_available_models, verify_connection
from agent_eval.evaluator import CortexEvaluator
from agent_eval.models import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT_SECONDS,
    State,
)

console = Console()
err_console = Console(stderr=True)

TOOLS_DIR = Path(__file__).parent
TEST_CASES_FILE = TOOLS_DIR / "test_cases.yaml"
RESULTS_DIR = TOOLS_DIR / "results"
COMPARISON_FILE = RESULTS_DIR / "COMPARISON.md"
DEFAULT_AGENTS_FILE = TOOLS_DIR.parent.parent / "AGENTS.md"

app = typer.Typer(
    name="agent_eval",
    help="AGENTS.md Evaluation CLI - Test agent protocol compliance",
)

state = State()


def print_header(connection_info: dict[str, str] | None = None) -> None:
    """Print colorful application header with name, version, and connection info."""
    header_text = f"[bold magenta]{__app_name__}[/bold magenta] [dim]v{__version__}[/dim]"
    subtitle = "[cyan]AGENTS.md Protocol Compliance Evaluator[/cyan]"

    if connection_info:
        conn_line = (
            f"\n[dim]Connection:[/dim] [green]{connection_info['connection_name']}[/green] "
            f"[dim]|[/dim] [blue]{connection_info['account']}[/blue] "
            f"[dim]|[/dim] [yellow]{connection_info['user']}[/yellow]"
        )
    else:
        conn_line = ""

    console.print()
    console.print(
        Panel(
            f"{header_text}\n{subtitle}{conn_line}",
            box=box.DOUBLE_EDGE,
            border_style="bright_blue",
            padding=(0, 2),
        )
    )


def log_debug(message: str) -> None:
    """Log a debug message (only if verbose mode is enabled)."""
    if state.verbose:
        console.print(f"[dim]DEBUG: {message}[/dim]")


def log_timing(test_id: str, duration: float) -> None:
    """Log timing information for a test (only if verbose mode is enabled)."""
    state.timing_stats[test_id] = duration
    if state.verbose:
        console.print(f"[dim]TIMING: {test_id} completed in {duration:.2f}s[/dim]")


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.1f}s"


def log_info(message: str) -> None:
    """Log an informational message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def log_success(message: str) -> None:
    """Log a success message."""
    console.print(f"[green]✓[/green] {message}")


def log_warning(message: str) -> None:
    """Log a warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def log_error(message: str) -> None:
    """Log an error message to stderr."""
    err_console.print(f"[red]✗[/red] {message}")


def log_section(title: str) -> None:
    """Log a section header."""
    console.print()
    console.print(Panel(title, style="bold cyan", box=box.DOUBLE))


def load_test_cases() -> dict[str, Any]:
    """Load test case definitions from YAML file."""
    log_debug(f"Loading test cases from {TEST_CASES_FILE}")
    with open(TEST_CASES_FILE) as f:
        data = yaml.safe_load(f)
    log_debug(f"Loaded {len(data.get('tests', []))} test cases")
    return data


def get_agents_md_hash() -> str:
    """Calculate SHA256 hash of AGENTS.md for verification."""
    content = state.agents_file.read_bytes()
    hash_value = f"sha256:{hashlib.sha256(content).hexdigest()[:12]}"
    log_debug(f"{state.agents_file.name} hash: {hash_value}")
    return hash_value


def generate_result_filename(model: str) -> Path:
    """Generate a unique filename for results based on timestamp and model."""
    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    model_slug = model.replace(".", "-")
    filepath = RESULTS_DIR / f"{timestamp}_{model_slug}.yaml"
    log_debug(f"Generated result filename: {filepath}")
    return filepath


def list_result_files() -> list[Path]:
    """List all result files in the results directory."""
    if not RESULTS_DIR.exists():
        log_debug(f"Results directory does not exist: {RESULTS_DIR}")
        return []
    files = list(RESULTS_DIR.glob("*.yaml"))
    log_debug(f"Found {len(files)} result files")
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)


def save_results(results: dict[str, Any], filepath: Path) -> None:
    """Save results to YAML file."""
    log_debug(f"Saving results to {filepath}")
    with open(filepath, "w") as f:
        yaml.dump(results, f, default_flow_style=False, sort_keys=False)
    log_success(f"Saved: {filepath}")


def resolve_result_path(filepath: str | Path) -> Path:
    """Resolve a result file path."""
    path = Path(filepath)
    if path.exists():
        log_debug(f"Found file at: {path}")
        return path
    results_path = RESULTS_DIR / path.name
    if results_path.exists():
        log_debug(f"Found file in results dir: {results_path}")
        return results_path
    log_debug(f"File not found, returning original: {path}")
    return path


def load_results(filepath: Path) -> dict[str, Any] | None:
    """Load results from YAML file."""
    if not filepath.exists():
        log_debug(f"File does not exist: {filepath}")
        return None
    log_debug(f"Loading results from {filepath}")
    with open(filepath) as f:
        return yaml.safe_load(f)


def compare_results(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Compare current results to baseline."""
    baseline_by_id = {r["test_id"]: r for r in baseline.get("results", [])}
    current_by_id = {r["test_id"]: r for r in current.get("results", [])}

    comparison: dict[str, Any] = {
        "baseline_pass_rate": baseline.get("summary", {}).get("pass_rate", 0),
        "current_pass_rate": current.get("summary", {}).get("pass_rate", 0),
        "delta": 0,
        "regressions": [],
        "improvements": [],
        "maintained": [],
        "persistent_failures": [],
    }

    comparison["delta"] = round(
        comparison["current_pass_rate"] - comparison["baseline_pass_rate"], 1
    )

    all_ids = set(baseline_by_id.keys()) | set(current_by_id.keys())

    for test_id in sorted(all_ids):
        b_result = baseline_by_id.get(test_id, {}).get("result")
        c_result = current_by_id.get(test_id, {}).get("result")
        name = current_by_id.get(test_id, baseline_by_id.get(test_id, {})).get("name", "")

        entry = {"test_id": test_id, "name": name}

        if b_result == "PASS" and c_result == "FAIL":
            comparison["regressions"].append(entry)
        elif b_result == "FAIL" and c_result == "PASS":
            comparison["improvements"].append(entry)
        elif b_result == "PASS" and c_result == "PASS":
            comparison["maintained"].append(entry)
        elif b_result == "FAIL" and c_result == "FAIL":
            comparison["persistent_failures"].append(entry)

    log_debug(
        f"Comparison: {len(comparison['regressions'])} regressions, "
        f"{len(comparison['improvements'])} improvements"
    )

    return comparison


def generate_report(
    comparison: dict[str, Any],
    baseline_meta: dict[str, Any],
    current_meta: dict[str, Any],
) -> str:
    """Generate markdown comparison report."""
    lines = [
        "# AGENTS.md Test Comparison Report",
        "",
        f"Generated: {datetime.now(UTC).isoformat()}",
        "",
        "## Evaluation Details",
        "",
        "| Run | Timestamp | Evaluator | AGENTS.md Hash |",
        "|-----|-----------|-----------|----------------|",
        f"| Baseline | {baseline_meta.get('timestamp', 'N/A')} | "
        f"{baseline_meta.get('evaluator', 'N/A')} | "
        f"{baseline_meta.get('agents_md_hash', 'N/A')} |",
        f"| Current | {current_meta.get('timestamp', 'N/A')} | "
        f"{current_meta.get('evaluator', 'N/A')} | "
        f"{current_meta.get('agents_md_hash', 'N/A')} |",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Baseline Pass Rate | {comparison['baseline_pass_rate']}% |",
        f"| Current Pass Rate | {comparison['current_pass_rate']}% |",
        f"| Delta | {comparison['delta']:+.1f}% |",
        "",
    ]

    if comparison["delta"] > 0:
        lines.append("**Result: IMPROVEMENT**")
    elif comparison["delta"] < 0:
        lines.append("**Result: REGRESSION**")
    else:
        lines.append("**Result: NO CHANGE**")

    lines.extend(["", "## Regressions (CRITICAL)", ""])
    if comparison["regressions"]:
        for r in comparison["regressions"]:
            lines.append(f"- **{r['test_id']}**: {r['name']} (PASS -> FAIL)")
    else:
        lines.append("None")

    lines.extend(["", "## Improvements", ""])
    if comparison["improvements"]:
        for r in comparison["improvements"]:
            lines.append(f"- **{r['test_id']}**: {r['name']} (FAIL -> PASS)")
    else:
        lines.append("None")

    lines.extend(["", "## Persistent Failures", ""])
    if comparison["persistent_failures"]:
        for r in comparison["persistent_failures"]:
            lines.append(f"- **{r['test_id']}**: {r['name']}")
    else:
        lines.append("None")

    lines.extend(
        [
            "",
            "## Approval Criteria",
            "",
            f"- No regressions: {'PASS' if not comparison['regressions'] else 'FAIL'}",
            f"- Delta >= 0: {'PASS' if comparison['delta'] >= 0 else 'FAIL'}",
            "",
        ]
    )

    approved = not comparison["regressions"] and comparison["delta"] >= 0
    lines.append(f"**Overall: {'APPROVED' if approved else 'NOT APPROVED'}**")

    return "\n".join(lines)


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    connection: Annotated[
        str,
        typer.Option("-c", "--connection", help="Snowflake connection name"),
    ] = "default",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show verbose debug output"),
    ] = False,
    agents: Annotated[
        str | None,
        typer.Option("-a", "--agents", help="Path to AGENTS.md file"),
    ] = None,
) -> None:
    """AGENTS.md Evaluation CLI.

    Test agent protocol compliance using Snowflake Cortex models.
    """
    state.connection = connection
    state.verbose = verbose

    if agents:
        agents_path = Path(agents)
        if not agents_path.exists():
            log_error(f"AGENTS file not found: {agents_path}")
            raise typer.Exit(1)
        state.agents_file = agents_path
    else:
        state.agents_file = DEFAULT_AGENTS_FILE

    # Verify connection before proceeding
    try:
        connection_info = verify_connection(connection)
    except RuntimeError as e:
        print_header()  # Show header without connection info
        log_error(f"Connection failed: {e}")
        log_error("Cannot proceed without valid Snowflake connection. Exiting.")
        raise typer.Exit(1) from None

    print_header(connection_info)

    if state.agents_file != DEFAULT_AGENTS_FILE:
        log_info(f"Using protocol: {state.agents_file}")

    if verbose:
        log_debug("Verbose mode enabled")

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit(0)


def _run_sequential(
    test_list: list[dict[str, Any]],
    results: dict[str, Any],
    model: str,
    timeout: int,
    max_retries: int,
) -> None:
    """Run tests sequentially with progress bar."""
    with (
        CortexEvaluator(
            model,
            state.connection,
            timeout=timeout,
            max_retries=max_retries,
            agents_file=state.agents_file,
            state=state,
        ) as evaluator,
        Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[dim]{task.fields[elapsed]}[/dim]"),
            console=console,
        ) as progress,
    ):
        task = progress.add_task("Running tests...", total=len(test_list), elapsed="")

        for test in test_list:
            test_start = time.perf_counter()
            progress.update(task, description=f"[cyan]{test['test_id']}[/]")

            try:
                result = evaluator.evaluate_test(test)
                results["results"].append(result)

                if result["result"] == "PASS":
                    results["summary"]["passed"] += 1
                else:
                    results["summary"]["failed"] += 1

            except (RuntimeError, ValueError, KeyError) as e:
                log_debug(f"Test {test['test_id']} error: {e}")
                results["results"].append(
                    {
                        "test_id": test["test_id"],
                        "name": test["name"],
                        "category": test["category"],
                        "priority": test["priority"],
                        "result": "ERROR",
                        "error": str(e),
                    }
                )
                results["summary"]["failed"] += 1

            elapsed = time.perf_counter() - test_start
            progress.update(task, elapsed=f"{elapsed:.1f}s")
            progress.advance(task)


def _run_parallel(
    test_list: list[dict[str, Any]],
    results: dict[str, Any],
    model: str,
    timeout: int,
    max_retries: int,
    workers: int,
) -> None:
    """Run tests in parallel with live progress for active tests."""
    # Warm up connection
    with CortexEvaluator(
        model,
        state.connection,
        timeout=timeout,
        max_retries=max_retries,
        agents_file=state.agents_file,
        state=state,
    ) as _:
        pass

    # Thread-safe tracking of active test tasks
    active_tasks: dict[str, int] = {}  # test_id -> task_id
    lock = threading.Lock()
    completed_count = [0]  # Use list for mutable reference in nested function
    passed_count = [0]
    failed_count = [0]

    # Create progress display with overall bar and space for active tests
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=30),
        TaskProgressColumn(),
        TextColumn("{task.fields[status]}"),
        console=console,
        refresh_per_second=4,
    )

    def evaluate_with_tracking(test: dict[str, Any]) -> dict[str, Any]:
        """Evaluate test with progress tracking."""
        test_id = test["test_id"]
        test_name = test["name"][:35] + "..." if len(test["name"]) > 35 else test["name"]

        # Add task for this test when it starts running
        with lock:
            task_id = progress.add_task(
                f"  [cyan]{test_id}[/cyan]",
                total=None,  # Indeterminate (spinner)
                status=f"[dim]{test_name}[/dim]",
            )
            active_tasks[test_id] = task_id

        try:
            evaluator = CortexEvaluator(
                model,
                state.connection,
                timeout=timeout,
                max_retries=max_retries,
                agents_file=state.agents_file,
                state=state,
            )
            evaluator.quiet = True
            with evaluator:
                try:
                    return evaluator.evaluate_test(test)
                except (RuntimeError, ValueError, KeyError) as e:
                    log_debug(f"Test {test_id} error: {e}")
                    return {
                        "test_id": test_id,
                        "name": test["name"],
                        "category": test["category"],
                        "priority": test["priority"],
                        "result": "ERROR",
                        "error": str(e),
                    }
        finally:
            # Remove task when done
            with lock:
                task_id = active_tasks.pop(test_id, None)
                if task_id is not None:
                    progress.remove_task(task_id)

    with progress:
        # Overall progress bar at top
        overall_task = progress.add_task(
            "[bold]Overall Progress[/bold]",
            total=len(test_list),
            status=f"[dim]0/{len(test_list)} | ✓ 0 | ✗ 0[/dim]",
        )

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_test = {
                executor.submit(evaluate_with_tracking, test): test for test in test_list
            }

            for future in as_completed(future_to_test):
                test = future_to_test[future]
                try:
                    result = future.result()
                    results["results"].append(result)

                    if result["result"] == "PASS":
                        results["summary"]["passed"] += 1
                        passed_count[0] += 1
                    else:
                        results["summary"]["failed"] += 1
                        failed_count[0] += 1

                except Exception as e:
                    log_error(f"Unexpected error in {test['test_id']}: {e}")
                    results["results"].append(
                        {
                            "test_id": test["test_id"],
                            "name": test["name"],
                            "category": test["category"],
                            "priority": test["priority"],
                            "result": "ERROR",
                            "error": str(e),
                        }
                    )
                    results["summary"]["failed"] += 1
                    failed_count[0] += 1

                completed_count[0] += 1
                progress.update(
                    overall_task,
                    completed=completed_count[0],
                    status=(
                        f"[dim]{completed_count[0]}/{len(test_list)}[/dim] | "
                        f"[green]✓ {passed_count[0]}[/green] | "
                        f"[red]✗ {failed_count[0]}[/red]"
                    ),
                )

    results["results"].sort(key=lambda x: x["test_id"])


@app.command()
def run(
    model: Annotated[
        str,
        typer.Option("-m", "--model", help="Cortex model to use"),
    ] = DEFAULT_MODEL,
    tests: Annotated[
        str | None,
        typer.Option("-t", "--tests", help="Comma-separated test IDs"),
    ] = None,
    category: Annotated[
        str | None,
        typer.Option("--category", "-C", help="Filter by category (comma-separated)"),
    ] = None,
    priority: Annotated[
        str | None,
        typer.Option(
            "--priority",
            "-P",
            help="Filter by priority (comma-separated: critical,high,medium,low)",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Validate test cases without API calls"),
    ] = False,
    parallel: Annotated[
        int,
        typer.Option("--parallel", "-p", help="Number of parallel workers (0=sequential)"),
    ] = 0,
    timeout: Annotated[
        int,
        typer.Option("--timeout", help="Request timeout in seconds"),
    ] = DEFAULT_TIMEOUT_SECONDS,
    max_retries: Annotated[
        int,
        typer.Option("--max-retries", help="Max retry attempts for transient failures"),
    ] = DEFAULT_MAX_RETRIES,
) -> None:
    """Run automated evaluation via Snowflake Cortex."""
    available_models, _ = list_available_models(state.connection)
    if model.lower() not in [m.lower() for m in available_models]:
        log_error(f"Unknown model: {model}")
        log_info(f"Available: {', '.join(available_models)}")
        log_info("Run 'models' command to see all available models")
        raise typer.Exit(1)

    log_section(f"Automated Evaluation\nModel: {model}")

    test_data = load_test_cases()
    all_tests = test_data.get("tests", [])

    test_list = all_tests

    if tests:
        test_ids = [t.strip() for t in tests.split(",")]
        test_list = [t for t in test_list if t["test_id"] in test_ids]
        if not test_list:
            log_error(f"No tests found matching: {test_ids}")
            raise typer.Exit(1)

    if category:
        categories = [c.strip().lower() for c in category.split(",")]
        test_list = [t for t in test_list if t.get("category", "").lower() in categories]
        if not test_list:
            log_error(f"No tests found in categories: {categories}")
            raise typer.Exit(1)
        log_info(f"Filtered to categories: {', '.join(categories)}")

    if priority:
        priorities = [p.strip().lower() for p in priority.split(",")]
        test_list = [t for t in test_list if t.get("priority", "").lower() in priorities]
        if not test_list:
            log_error(f"No tests found with priorities: {priorities}")
            raise typer.Exit(1)
        log_info(f"Filtered to priorities: {', '.join(priorities)}")

    log_info(
        f"Running {len(test_list)} tests"
        + (f" with {parallel} parallel workers" if parallel > 0 else " sequentially")
    )

    state.timing_stats = {}
    overall_start = time.perf_counter()

    if dry_run:
        log_warning("DRY RUN - No API calls will be made")
        table = Table(title="Test Cases to Run", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Category", style="yellow")
        table.add_column("Priority", style="magenta")

        for test in test_list:
            table.add_row(
                test["test_id"],
                test["name"],
                test["category"],
                test["priority"],
            )

        console.print(table)
        log_success(f"Validated {len(test_list)} test cases")
        raise typer.Exit(0)

    results: dict[str, Any] = {
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "agents_file": str(state.agents_file),
            "agents_md_hash": get_agents_md_hash(),
            "evaluator": f"cortex:{model}",
            "model": model,
        },
        "summary": {
            "total_tests": len(test_list),
            "passed": 0,
            "failed": 0,
            "pass_rate": 0.0,
        },
        "results": [],
    }

    executable_tests = [t for t in test_list if "SIMULATE" not in t.get("test_note", "")]
    skipped_count = len(test_list) - len(executable_tests)
    if skipped_count > 0:
        log_info(f"Skipping {skipped_count} simulation tests")

    if parallel > 0 and len(executable_tests) > 1:
        _run_parallel(executable_tests, results, model, timeout, max_retries, parallel)
    else:
        _run_sequential(executable_tests, results, model, timeout, max_retries)

    overall_duration = time.perf_counter() - overall_start

    total = results["summary"]["passed"] + results["summary"]["failed"]
    if total > 0:
        results["summary"]["pass_rate"] = round(results["summary"]["passed"] / total * 100, 1)

    results["metadata"]["total_duration_seconds"] = round(overall_duration, 2)
    results["metadata"]["parallel_workers"] = parallel

    timestamped_file = generate_result_filename(model)
    save_results(results, timestamped_file)

    console.print()
    summary_table = Table(title="Results Summary", box=box.ROUNDED)
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Value", justify="right")

    pass_rate = results["summary"]["pass_rate"]
    rate_style = "green" if pass_rate >= 80 else "yellow" if pass_rate >= 60 else "red"

    summary_table.add_row("Pass Rate", f"[{rate_style}]{pass_rate}%[/]")
    summary_table.add_row("Passed", f"[green]{results['summary']['passed']}[/]")
    summary_table.add_row("Failed", f"[red]{results['summary']['failed']}[/]")
    summary_table.add_row("Total", str(results["summary"]["total_tests"]))
    summary_table.add_row("Duration", format_duration(overall_duration))
    if parallel > 0:
        summary_table.add_row("Workers", str(parallel))

    console.print(summary_table)

    if state.verbose and state.timing_stats:
        console.print()
        timing_table = Table(title="Test Timing Details", box=box.SIMPLE)
        timing_table.add_column("Test ID", style="cyan")
        timing_table.add_column("Duration", justify="right")

        sorted_timings = sorted(state.timing_stats.items(), key=lambda x: x[1], reverse=True)
        for test_id, duration in sorted_timings:
            timing_table.add_row(test_id, f"{duration:.2f}s")

        console.print(timing_table)

        if sorted_timings:
            avg_time = sum(t[1] for t in sorted_timings) / len(sorted_timings)
            console.print(f"\n[dim]Average test time: {avg_time:.2f}s[/dim]")
            console.print(
                f"[dim]Slowest test: {sorted_timings[0][0]} ({sorted_timings[0][1]:.2f}s)[/dim]"
            )


@app.command("list")
def list_cmd() -> None:
    """List all saved result files."""
    files = list_result_files()

    if not files:
        log_warning("No result files found in results/ directory")
        log_info("Run 'run' command to generate results")
        raise typer.Exit(0)

    table = Table(title=f"Saved Results ({len(files)} files)", box=box.ROUNDED)
    table.add_column("Filename", style="cyan", overflow="fold")
    table.add_column("Pass Rate", justify="right", style="green")
    table.add_column("Tests", justify="right", style="white")
    table.add_column("Model", style="yellow", overflow="fold")
    table.add_column("Evaluator", style="blue", overflow="fold")
    table.add_column("Runtime", justify="right", style="dim")
    table.add_column("Agents File", style="magenta", overflow="fold")
    table.add_column("Date", style="dim", overflow="fold")

    for f in files:
        try:
            data = load_results(f)
            if data:
                summary = data.get("summary", {})
                pass_rate = f"{summary.get('pass_rate', 'N/A')}%"
                tests = str(summary.get("total_tests", 0))
                model = data.get("metadata", {}).get("model", "unknown")
                evaluator = data.get("metadata", {}).get("evaluator", "-")
                total_duration = data.get("metadata", {}).get("total_duration_seconds")
                runtime = format_duration(total_duration) if total_duration else "-"
                agents_file = data.get("metadata", {}).get("agents_file", "-")
                if agents_file != "-":
                    agents_file = Path(agents_file).name
                timestamp = data.get("metadata", {}).get("timestamp", "")[:19]
                table.add_row(
                    f.name, pass_rate, tests, model, evaluator, runtime, agents_file, timestamp
                )
        except (yaml.YAMLError, OSError) as e:
            log_debug(f"Error loading {f}: {e}")
            table.add_row(f.name, "[red]ERROR[/]", "", "", "", "", "", "")

    console.print(table)
    console.print()
    log_info("Use 'show <filename>' to inspect a result file")
    log_info("Use 'compare -b <baseline> -t <target>' to compare files")


@app.command("models")
def models_cmd() -> None:
    """List available Cortex REST API models."""
    models, _ = list_available_models(state.connection)

    table = Table(title=f"Cortex REST API Models ({len(models)})", box=box.ROUNDED)
    table.add_column("#", style="dim", justify="right")
    table.add_column("Model", style="cyan")

    for i, model in enumerate(sorted(models), 1):
        table.add_row(str(i), model)

    console.print(table)
    console.print()
    log_info("Models shown are for REST API (/api/v2/cortex/inference:complete)")
    log_info("SQL COMPLETE() function may have different models - use SHOW MODELS")


@app.command()
def show(
    filename: Annotated[
        str,
        typer.Argument(help="Result filename or path to inspect"),
    ],
    full: Annotated[
        bool,
        typer.Option("--full", "-f", help="Show full model responses"),
    ] = False,
) -> None:
    """Show details of a single result file."""
    filepath = resolve_result_path(filename)
    if not filepath.exists():
        log_error(f"File not found: {filename}")
        log_info(f"Try: {RESULTS_DIR / filename}")
        raise typer.Exit(1)

    data = load_results(filepath)
    if not data:
        log_error(f"Could not load: {filepath}")
        raise typer.Exit(1)

    log_section(f"Result: {filepath.name}")

    meta = data.get("metadata", {})
    summary = data.get("summary", {})

    meta_table = Table(title="Metadata", box=box.SIMPLE)
    meta_table.add_column("Field", style="bold")
    meta_table.add_column("Value")

    meta_table.add_row("Timestamp", meta.get("timestamp", "N/A"))
    meta_table.add_row("Model", meta.get("model", "N/A"))
    meta_table.add_row("Evaluator", meta.get("evaluator", "N/A"))
    meta_table.add_row("AGENTS.md Hash", meta.get("agents_md_hash", "N/A"))

    total_duration = meta.get("total_duration_seconds")
    if total_duration:
        meta_table.add_row("Total Runtime", format_duration(total_duration))

    parallel_workers = meta.get("parallel_workers", 0)
    if parallel_workers > 0:
        meta_table.add_row("Parallel Workers", str(parallel_workers))

    console.print(meta_table)

    pass_rate = summary.get("pass_rate", 0)
    rate_style = "green" if pass_rate >= 80 else "yellow" if pass_rate >= 60 else "red"

    summary_table = Table(title="Summary", box=box.SIMPLE)
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Value", justify="right")

    summary_table.add_row("Pass Rate", f"[{rate_style}]{pass_rate}%[/]")
    summary_table.add_row("Passed", f"[green]{summary.get('passed', 0)}[/]")
    summary_table.add_row("Failed", f"[red]{summary.get('failed', 0)}[/]")
    summary_table.add_row("Total", str(summary.get("total_tests", 0)))

    console.print(summary_table)

    results_table = Table(title="Test Results", box=box.ROUNDED)
    results_table.add_column("ID", style="cyan")
    results_table.add_column("Name")
    results_table.add_column("Result", justify="center")
    results_table.add_column("Score", justify="right")
    results_table.add_column("Request ID", style="dim")

    for result in data.get("results", []):
        result_str = result.get("result", "N/A")
        if result_str == "PASS":
            result_styled = "[green]PASS[/]"
        elif result_str == "FAIL":
            result_styled = "[red]FAIL[/]"
        else:
            result_styled = f"[yellow]{result_str}[/]"

        score = f"{result.get('score', 0)}/{result.get('max_score', 0)}"
        request_id = result.get("request_id", "") or ""
        if request_id and len(request_id) > 12:
            request_id = request_id[:12] + "..."

        results_table.add_row(
            result.get("test_id", ""),
            result.get("name", ""),
            result_styled,
            score,
            request_id,
        )

    console.print(results_table)

    if full:
        console.print()
        console.print("[bold]Full Responses:[/]")
        for result in data.get("results", []):
            if "model_response" in result:
                console.print()
                console.print(
                    Panel(
                        result["model_response"],
                        title=f"[cyan]{result['test_id']}[/]",
                        box=box.ROUNDED,
                    )
                )


@app.command()
def compare(
    baseline: Annotated[
        str,
        typer.Option("--baseline", "-b", help="Baseline result file"),
    ],
    target: Annotated[
        str,
        typer.Option("--target", "-t", help="Target result file to compare"),
    ],
) -> None:
    """Compare two result files."""
    path1 = resolve_result_path(baseline)
    path2 = resolve_result_path(target)

    baseline_data = load_results(path1)
    current_data = load_results(path2)

    if not baseline_data:
        log_error(f"Cannot load: {path1}")
        raise typer.Exit(1)
    if not current_data:
        log_error(f"Cannot load: {path2}")
        raise typer.Exit(1)

    comparison = compare_results(baseline_data, current_data)

    log_section("Comparison Results")

    table = Table(box=box.SIMPLE)
    table.add_column("", style="bold")
    table.add_column("Baseline", style="cyan")
    table.add_column("Target", style="magenta")

    table.add_row("Filename", path1.name, path2.name)
    table.add_row(
        "Model",
        baseline_data["metadata"].get(
            "model", baseline_data["metadata"].get("evaluator", "unknown")
        ),
        current_data["metadata"].get("model", current_data["metadata"].get("evaluator", "unknown")),
    )
    table.add_row(
        "Pass Rate",
        f"{comparison['baseline_pass_rate']}%",
        f"{comparison['current_pass_rate']}%",
    )

    console.print(table)

    delta = comparison["delta"]
    if delta > 0:
        console.print(f"\n[bold green]Delta: +{delta}%[/] (IMPROVEMENT)")
    elif delta < 0:
        console.print(f"\n[bold red]Delta: {delta}%[/] (REGRESSION)")
    else:
        console.print(f"\n[bold yellow]Delta: {delta}%[/] (NO CHANGE)")

    console.print(f"Regressions: [red]{len(comparison['regressions'])}[/]")
    console.print(f"Improvements: [green]{len(comparison['improvements'])}[/]")

    if comparison["regressions"]:
        console.print("\n[bold red]Regressions (CRITICAL):[/]")
        for r in comparison["regressions"]:
            console.print(f"  [red]✗[/] {r['test_id']}: {r['name']}")

    if comparison["improvements"]:
        console.print("\n[bold green]Improvements:[/]")
        for r in comparison["improvements"]:
            console.print(f"  [green]✓[/] {r['test_id']}: {r['name']}")


@app.command()
def report(
    baseline: Annotated[
        str,
        typer.Option("--baseline", "-b", help="Baseline result file"),
    ],
    target: Annotated[
        str,
        typer.Option("--target", "-t", help="Target result file to compare"),
    ],
) -> None:
    """Generate markdown comparison report."""
    path1 = resolve_result_path(baseline)
    path2 = resolve_result_path(target)

    baseline_data = load_results(path1)
    current_data = load_results(path2)

    if not baseline_data or not current_data:
        log_error("Need both result files to generate report")
        raise typer.Exit(1)

    comparison = compare_results(baseline_data, current_data)
    report_text = generate_report(
        comparison,
        baseline_data.get("metadata", {}),
        current_data.get("metadata", {}),
    )

    with open(COMPARISON_FILE, "w") as f:
        f.write(report_text)

    log_success(f"Report saved: {COMPARISON_FILE}")
    console.print()
    console.print(Syntax(report_text, "markdown"))


if __name__ == "__main__":
    app()
