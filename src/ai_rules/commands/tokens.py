"""Token budget validator and updater for AI coding rule files.

This command analyzes rule files, calculates accurate token estimates using
tiktoken with GPT-4o encoding (o200k_base), and updates TokenBudget metadata.

Token Estimation Method:
    Uses tiktoken with GPT-4o encoding for exact token counts.
    Results are rounded to nearest 50 for cleaner budget numbers.

Default threshold: ±5% (updates triggered when difference exceeds threshold)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tiktoken
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ai_rules._shared.console import console, log_error, log_info, log_success


@dataclass
class TokenBudgetAnalysis:
    """Analysis result for a single rule file."""

    file_path: Path
    current_budget: int | None
    estimated_tokens: int
    suggested_budget: int
    diff_percentage: float | None
    needs_update: bool
    error: str | None = None

    @property
    def status(self) -> str:
        """Get status string for display."""
        if self.error:
            return "ERROR"
        elif not self.current_budget:
            return "MISSING"
        elif not self.needs_update:
            return "OK"
        elif abs(self.diff_percentage or 0) <= 50:
            return "UPDATE"
        else:
            return "MAJOR"


@dataclass
class UpdateConfig:
    """Configuration for token budget updates."""

    # Minimum difference percentage to trigger update
    update_threshold: float = 5.0
    # Rounding increment for cleaner budget numbers
    rounding_increment: int = 50
    # Dry run mode (don't actually update files)
    dry_run: bool = False
    # Verbose output
    verbose: bool = False


class TokenBudgetUpdater:
    """Updater for token budgets in rule files."""

    def __init__(self, config: UpdateConfig | None = None):
        """Initialize updater with configuration."""
        self.config = config or UpdateConfig()
        self.encoding = tiktoken.encoding_for_model("gpt-4o")

    def estimate_tokens(self, content: str) -> int:
        """Estimate tokens using tiktoken with GPT-4o encoding.

        Args:
            content: File content to analyze

        Returns:
            Exact token count for GPT-4o model
        """
        tokens = self.encoding.encode(content)
        return len(tokens)

    def round_to_increment(self, value: int) -> int:
        """Round value to nearest increment for cleaner numbers.

        Args:
            value: Value to round

        Returns:
            Rounded value
        """
        return int(round(value / self.config.rounding_increment) * self.config.rounding_increment)

    def analyze_file(self, file_path: Path) -> TokenBudgetAnalysis:
        """Analyze a single file's token budget.

        Args:
            file_path: Path to rule file

        Returns:
            TokenBudgetAnalysis with results
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            return TokenBudgetAnalysis(
                file_path=file_path,
                current_budget=None,
                estimated_tokens=0,
                suggested_budget=0,
                diff_percentage=None,
                needs_update=False,
                error=f"Failed to read file: {e}",
            )

        # Extract current TokenBudget
        token_match = re.search(r"^\*\*TokenBudget:\*\*\s*~?(\d+)", content, re.MULTILINE)
        current_budget = int(token_match.group(1)) if token_match else None

        # Calculate estimates
        estimated = self.estimate_tokens(content)
        suggested = self.round_to_increment(estimated)

        # Calculate difference
        if current_budget:
            diff_pct = ((estimated - current_budget) / current_budget) * 100
            needs_update = abs(diff_pct) > self.config.update_threshold
        else:
            diff_pct = None
            needs_update = True

        return TokenBudgetAnalysis(
            file_path=file_path,
            current_budget=current_budget,
            estimated_tokens=estimated,
            suggested_budget=suggested,
            diff_percentage=diff_pct,
            needs_update=needs_update,
        )

    def update_file(self, analysis: TokenBudgetAnalysis) -> bool:
        """Update TokenBudget in a file.

        Args:
            analysis: TokenBudgetAnalysis with update information

        Returns:
            True if file was updated, False otherwise
        """
        if not analysis.needs_update:
            return False

        if self.config.dry_run:
            return True

        try:
            content = analysis.file_path.read_text(encoding="utf-8")

            if analysis.current_budget:
                # Replace existing budget
                old_line = f"**TokenBudget:** ~{analysis.current_budget}"
                new_line = f"**TokenBudget:** ~{analysis.suggested_budget}"
                new_content = content.replace(old_line, new_line)
            else:
                # Insert TokenBudget after Keywords (per metadata field order)
                keywords_pattern = r"(^\*\*Keywords:\*\*.*\n)"
                replacement = f"\\1**TokenBudget:** ~{analysis.suggested_budget}\n"
                new_content = re.sub(keywords_pattern, replacement, content, flags=re.MULTILINE)

            if new_content != content:
                analysis.file_path.write_text(new_content, encoding="utf-8")
                return True
            else:
                return False

        except Exception as e:
            log_error(f"Failed to update {analysis.file_path.name}: {e}")
            return False

    def analyze_all(self, directory: Path) -> list[TokenBudgetAnalysis]:
        """Analyze all rule files in directory.

        Args:
            directory: Directory containing rule files

        Returns:
            List of TokenBudgetAnalysis results
        """
        results = []
        md_files = sorted(f for f in directory.glob("*.md") if f.name != "RULES_INDEX.md")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing files...", total=len(md_files))

            for md_file in md_files:
                analysis = self.analyze_file(md_file)
                results.append(analysis)
                progress.update(task, advance=1, description=f"Analyzing {md_file.name}...")

        return results

    def update_all(self, directory: Path) -> tuple[list[TokenBudgetAnalysis], int]:
        """Update all rule files in directory.

        Args:
            directory: Directory containing rule files

        Returns:
            Tuple of (analyses, update_count)
        """
        analyses = self.analyze_all(directory)
        update_count = 0

        for analysis in analyses:
            if self.update_file(analysis):
                update_count += 1

        return analyses, update_count


def _print_summary(
    analyses: list[TokenBudgetAnalysis],
    update_count: int,
    threshold: float,
    dry_run: bool,
) -> None:
    """Print summary of analysis and updates."""
    console.print()
    console.rule("[bold]TOKEN BUDGET UPDATE SUMMARY[/bold]")
    console.print()

    # Statistics
    total = len(analyses)
    ok = sum(1 for a in analyses if a.status == "OK")
    updates = sum(1 for a in analyses if a.needs_update and not a.error)
    errors = sum(1 for a in analyses if a.error)
    missing = sum(1 for a in analyses if a.status == "MISSING")

    console.print(f"Total rule files analyzed: [cyan]{total}[/cyan]")
    console.print(f"  [green]OK[/green]      Within ±{threshold}%: {ok}")
    console.print(f"  [yellow]UPDATE[/yellow]  Need updating: {updates}")
    console.print(f"  [blue]MISSING[/blue] No budget declared: {missing}")
    console.print(f"  [red]ERROR[/red]   Errors: {errors}")
    console.print()

    if dry_run:
        log_info(f"[dry-run] Would update {update_count} files")
    else:
        log_success(f"Files updated: {update_count}")


def _print_detailed_results(analyses: list[TokenBudgetAnalysis]) -> None:
    """Print detailed results for all files using Rich table."""
    console.print()
    table = Table(title="Detailed Token Analysis")
    table.add_column("File", style="cyan", max_width=45)
    table.add_column("Current", justify="right")
    table.add_column("Estimated", justify="right")
    table.add_column("Diff %", justify="right")
    table.add_column("Suggested", justify="right")
    table.add_column("Status", justify="center")

    for analysis in analyses:
        current_str = (
            f"~{analysis.current_budget}" if analysis.current_budget else "[dim]MISSING[/dim]"
        )
        diff_str = (
            f"{analysis.diff_percentage:+.1f}%"
            if analysis.diff_percentage is not None
            else "[dim]N/A[/dim]"
        )
        suggested_str = f"~{analysis.suggested_budget}"

        # Color status
        status_colors = {
            "OK": "[green]OK[/green]",
            "UPDATE": "[yellow]UPDATE[/yellow]",
            "MISSING": "[blue]MISSING[/blue]",
            "MAJOR": "[red]MAJOR[/red]",
            "ERROR": "[red]ERROR[/red]",
        }
        status_str = status_colors.get(analysis.status, analysis.status)

        table.add_row(
            analysis.file_path.name,
            current_str,
            str(analysis.estimated_tokens),
            diff_str,
            suggested_str,
            status_str,
        )

    console.print(table)


def _print_update_details(analyses: list[TokenBudgetAnalysis], dry_run: bool) -> None:
    """Print details for files that were/will be updated."""
    updates = [a for a in analyses if a.needs_update and not a.error]

    if not updates:
        return

    console.print()
    title = "FILES TO BE UPDATED" if dry_run else "FILES UPDATED"
    table = Table(title=title)
    table.add_column("File", style="cyan", max_width=50)
    table.add_column("Change", style="yellow")
    table.add_column("Diff", justify="right")

    for analysis in updates:
        if analysis.current_budget:
            change = f"~{analysis.current_budget} → ~{analysis.suggested_budget}"
            diff = f"{analysis.diff_percentage:+.1f}%"
        else:
            change = f"[dim]MISSING[/dim] → ~{analysis.suggested_budget}"
            diff = "[dim]N/A[/dim]"

        table.add_row(analysis.file_path.name, change, diff)

    console.print(table)


def tokens(
    path: Annotated[
        Path,
        typer.Argument(
            help="Rule file or directory to validate.",
        ),
    ],
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help="Show what would be updated without making changes.",
        ),
    ] = False,
    detailed: Annotated[
        bool,
        typer.Option(
            "--detailed",
            "-d",
            help="Show detailed analysis for all files.",
        ),
    ] = False,
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            "-t",
            help="Minimum difference percentage to trigger update.",
        ),
    ] = 5.0,
) -> None:
    """Validate and update token budgets for AI coding rule files.

    Analyzes rule files using tiktoken with GPT-4o encoding (o200k_base)
    to calculate accurate token counts. Updates TokenBudget metadata
    when the difference exceeds the threshold.

    Examples:
        # Validate single rule file
        ai-rules tokens rules/100-snowflake-core.md

        # Validate single file with dry run
        ai-rules tokens rules/200-python-core.md --dry-run --detailed

        # Analyze and update all production rule files
        ai-rules tokens rules/

        # Dry run to see what would be updated (directory)
        ai-rules tokens rules/ --dry-run

        # Update with custom threshold
        ai-rules tokens rules/ --threshold 20
    """
    # Verify path exists
    if not path.exists():
        log_error(f"Path not found: {path}")
        raise typer.Exit(1)

    # Create configuration
    config = UpdateConfig(
        update_threshold=threshold,
        dry_run=dry_run,
        verbose=detailed,
    )

    # Create updater
    updater = TokenBudgetUpdater(config)

    # Handle single file vs directory
    if path.is_file():
        # Single file mode
        console.print()
        console.rule("[bold]TOKEN BUDGET ANALYSIS[/bold]")
        console.print()
        console.print(f"[bold]File:[/bold] {path}")
        console.print(f"[bold]Update threshold:[/bold] ±{threshold:.1f}%")
        console.print("[bold]Token counting:[/bold] tiktoken (GPT-4o, o200k_base encoding)")
        console.print(f"[bold]Rounding increment:[/bold] {config.rounding_increment}")

        if dry_run:
            console.print()
            log_info("[dry-run] No files will be modified")

        # Analyze single file
        analysis = updater.analyze_file(path)

        # Display results
        if analysis.error:
            log_error(analysis.error)
            raise typer.Exit(1)

        console.print()
        current_str = (
            f"~{analysis.current_budget}" if analysis.current_budget else "[yellow]MISSING[/yellow]"
        )
        diff_str = (
            f"{analysis.diff_percentage:+.1f}%"
            if analysis.diff_percentage is not None
            else "[dim]N/A[/dim]"
        )

        console.print(f"[bold]Current Budget:[/bold] {current_str}")
        console.print(f"[bold]Estimated Tokens:[/bold] {analysis.estimated_tokens}")
        console.print(f"[bold]Suggested Budget:[/bold] ~{analysis.suggested_budget}")
        console.print(f"[bold]Difference:[/bold] {diff_str}")
        console.print(f"[bold]Status:[/bold] {analysis.status}")
        console.print()

        # Update if needed
        if analysis.needs_update:
            if dry_run:
                log_info(
                    f"[dry-run] Would update TokenBudget: {current_str} → ~{analysis.suggested_budget}"
                )
            else:
                if updater.update_file(analysis):
                    log_success(
                        f"Updated TokenBudget: {current_str} → ~{analysis.suggested_budget}"
                    )
                else:
                    log_error("Failed to update file")
                    raise typer.Exit(1)
        else:
            log_success("No update needed (within threshold)")

        console.print()

    elif path.is_dir():
        # Directory mode
        console.print()
        console.rule("[bold]TOKEN BUDGET UPDATER[/bold]")
        console.print()
        console.print(f"[bold]Directory:[/bold] {path}")
        console.print(f"[bold]Update threshold:[/bold] ±{threshold:.1f}%")
        console.print("[bold]Token counting:[/bold] tiktoken (GPT-4o, o200k_base encoding)")
        console.print(f"[bold]Rounding increment:[/bold] {config.rounding_increment}")

        if dry_run:
            console.print()
            log_info("[dry-run] No files will be modified")

        # Perform updates
        analyses, update_count = updater.update_all(path)

        # Print results
        if detailed:
            _print_detailed_results(analyses)

        if config.verbose or update_count > 0:
            _print_update_details(analyses, dry_run)

        _print_summary(analyses, update_count, threshold, dry_run)

        # Print recommendations
        if not dry_run and update_count > 0:
            console.print()
            console.rule("[bold]NEXT STEPS[/bold]")
            console.print()
            console.print("1. Review changes: [cyan]git diff rules/[/cyan]")
            console.print("2. Validate updates: [cyan]ai-rules validate rules/[/cyan]")
            console.print("3. Commit changes with descriptive message")
            console.print()

    else:
        log_error(f"Path is neither a file nor directory: {path}")
        raise typer.Exit(1)
