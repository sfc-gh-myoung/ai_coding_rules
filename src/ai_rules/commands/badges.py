"""Badge updater command for ai-rules CLI.

Updates README.md badges with current version, test pass percentage, and coverage percentage.
"""

import re
import subprocess
from pathlib import Path
from typing import Annotated

import typer

from ai_rules._shared.console import log_error, log_info, log_success, log_warning
from ai_rules._shared.paths import find_project_root


def extract_version(pyproject_path: Path) -> str:
    """Extract version from pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml file

    Returns:
        Version string

    Raises:
        ValueError: If version not found
    """
    content = pyproject_path.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def get_test_percentage() -> tuple[int, int, float]:
    """Run pytest and extract pass percentage.

    Returns:
        Tuple of (passed, total, percentage)
    """
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        output = result.stdout + result.stderr

        match = re.search(r"(\d+) passed", output)
        passed = int(match.group(1)) if match else 0

        match = re.search(r"(\d+) failed", output)
        failed = int(match.group(1)) if match else 0

        total = passed + failed
        if total == 0:
            return 0, 0, 0.0

        percentage = (passed / total) * 100
        return passed, total, percentage

    except subprocess.TimeoutExpired:
        log_warning("pytest timed out")
        return 0, 0, 0.0
    except Exception as e:
        log_warning(f"Failed to run pytest: {e}")
        return 0, 0, 0.0


def get_coverage_percentage(project_root: Path) -> float:
    """Extract coverage percentage from htmlcov/index.html.

    Args:
        project_root: Path to project root directory

    Returns:
        Coverage percentage (0.0-100.0), or 0.0 if not found
    """
    htmlcov_index = project_root / "htmlcov" / "index.html"

    if not htmlcov_index.exists():
        log_warning(f"{htmlcov_index} not found. Run 'task test:coverage' first.")
        return 0.0

    try:
        content = htmlcov_index.read_text()
        # Look for: <span class="pc_cov">96%</span>
        match = re.search(r'<span class="pc_cov">(\d+)%</span>', content)
        if match:
            return float(match.group(1))

        log_warning("Could not find coverage percentage in htmlcov/index.html")
        return 0.0

    except Exception as e:
        log_warning(f"Failed to read coverage: {e}")
        return 0.0


def get_badge_color(percentage: float) -> str:
    """Get badge color based on percentage threshold.

    Args:
        percentage: Value between 0.0 and 100.0

    Returns:
        Color string for shields.io badge
    """
    if percentage >= 80:
        return "brightgreen"
    elif percentage >= 60:
        return "yellow"
    else:
        return "red"


def update_readme_badges(
    readme_path: Path,
    version: str,
    test_percentage: float,
    coverage_percentage: float,
) -> None:
    """Update README.md with new badge values.

    Args:
        readme_path: Path to README.md
        version: Version string from pyproject.toml
        test_percentage: Test pass percentage (0.0-100.0)
        coverage_percentage: Code coverage percentage (0.0-100.0)
    """
    content = readme_path.read_text()

    test_color = get_badge_color(test_percentage)
    coverage_color = get_badge_color(coverage_percentage)

    version_badge = f"![Version](https://img.shields.io/badge/version-{version}-blue)"
    test_badge = f"![Tests](https://img.shields.io/badge/tests-{test_percentage:.0f}%25%20passing-{test_color})"
    coverage_badge = f"![Coverage](https://img.shields.io/badge/coverage-{coverage_percentage:.0f}%25-{coverage_color})"

    lines = content.split("\n")

    version_pattern = r"!\[Version\]\(https://img\.shields\.io/badge/version-[^)]+\)"
    test_pattern = r"!\[Tests\]\(https://img\.shields\.io/badge/tests-[^)]+\)"
    coverage_pattern = r"!\[Coverage\]\(https://img\.shields\.io/badge/coverage-[^)]+\)"

    version_exists = False
    test_exists = False
    coverage_exists = False
    insert_index = None

    for i, line in enumerate(lines):
        if re.search(version_pattern, line):
            lines[i] = re.sub(version_pattern, version_badge, line)
            version_exists = True
        if re.search(test_pattern, line):
            lines[i] = re.sub(test_pattern, test_badge, line)
            test_exists = True
        if re.search(coverage_pattern, line):
            lines[i] = re.sub(coverage_pattern, coverage_badge, line)
            coverage_exists = True
        if "[![License: Apache-2.0]" in line and insert_index is None:
            insert_index = i + 1

    if not version_exists and insert_index is not None:
        lines.insert(insert_index, version_badge)
        insert_index += 1

    if not test_exists and insert_index is not None:
        lines.insert(insert_index, test_badge)
        insert_index += 1

    if not coverage_exists and insert_index is not None:
        lines.insert(insert_index, coverage_badge)

    readme_path.write_text("\n".join(lines))


def badges(
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            "-n",
            help="Show what would change without writing.",
        ),
    ] = False,
) -> None:
    """Update README badges with version, test pass rate, and coverage.

    Reads version from pyproject.toml, runs pytest to get test results,
    and extracts coverage from htmlcov/index.html.
    """
    try:
        project_root = find_project_root()
    except FileNotFoundError:
        log_error("Could not find project root (no pyproject.toml found)")
        raise typer.Exit(code=1) from None

    pyproject_path = project_root / "pyproject.toml"
    readme_path = project_root / "README.md"

    if not pyproject_path.exists():
        log_error(f"{pyproject_path} not found")
        raise typer.Exit(code=1) from None

    if not readme_path.exists():
        log_error(f"{readme_path} not found")
        raise typer.Exit(code=1) from None

    try:
        version = extract_version(pyproject_path)
        log_info(f"Version: {version}")

        passed, total, test_percentage = get_test_percentage()
        log_info(f"Tests: {passed}/{total} passed ({test_percentage:.1f}%)")

        coverage_percentage = get_coverage_percentage(project_root)
        log_info(f"Coverage: {coverage_percentage:.1f}%")

        if dry_run:
            log_info("[dry-run] Would update badges in README.md:")
            test_color = get_badge_color(test_percentage)
            coverage_color = get_badge_color(coverage_percentage)
            log_info(f"  Version: {version} (blue)")
            log_info(f"  Tests: {test_percentage:.0f}% passing ({test_color})")
            log_info(f"  Coverage: {coverage_percentage:.0f}% ({coverage_color})")
        else:
            update_readme_badges(readme_path, version, test_percentage, coverage_percentage)
            log_success(f"Updated {readme_path}")

    except Exception as e:
        log_error(f"{e}")
        raise typer.Exit(code=1) from None
