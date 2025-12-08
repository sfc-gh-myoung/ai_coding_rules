#!/usr/bin/env python3
"""Update README badges with current version and test pass percentage."""

import re
import subprocess
import sys
from pathlib import Path


def extract_version(pyproject_path: Path) -> str:
    """Extract version from pyproject.toml."""
    content = pyproject_path.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def get_test_percentage() -> tuple[int, int, float]:
    """Run pytest and extract pass percentage."""
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
        print("Warning: pytest timed out", file=sys.stderr)
        return 0, 0, 0.0
    except Exception as e:
        print(f"Warning: Failed to run pytest: {e}", file=sys.stderr)
        return 0, 0, 0.0


def update_readme_badges(readme_path: Path, version: str, test_percentage: float) -> None:
    """Update README.md with new badge values."""
    content = readme_path.read_text()

    status_color = (
        "brightgreen" if test_percentage >= 80 else "yellow" if test_percentage >= 60 else "red"
    )

    version_badge = f"![Version](https://img.shields.io/badge/version-{version}-blue)"
    test_badge = f"![Tests](https://img.shields.io/badge/tests-{test_percentage:.0f}%25%20passing-{status_color})"

    lines = content.split("\n")

    version_pattern = r"!\[Version\]\(https://img\.shields\.io/badge/version-[^)]+\)"
    test_pattern = r"!\[Tests\]\(https://img\.shields\.io/badge/tests-[^)]+\)"

    version_exists = False
    test_exists = False
    insert_index = None

    for i, line in enumerate(lines):
        if re.search(version_pattern, line):
            lines[i] = re.sub(version_pattern, version_badge, line)
            version_exists = True
        if re.search(test_pattern, line):
            lines[i] = re.sub(test_pattern, test_badge, line)
            test_exists = True
        if "[![License: Apache-2.0]" in line and insert_index is None:
            insert_index = i + 1

    if not version_exists and insert_index is not None:
        lines.insert(insert_index, version_badge)
        insert_index += 1

    if not test_exists and insert_index is not None:
        lines.insert(insert_index, test_badge)

    readme_path.write_text("\n".join(lines))


def main() -> int:
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"
    readme_path = project_root / "README.md"

    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found", file=sys.stderr)
        return 1

    if not readme_path.exists():
        print(f"Error: {readme_path} not found", file=sys.stderr)
        return 1

    try:
        version = extract_version(pyproject_path)
        print(f"Version: {version}")

        passed, total, percentage = get_test_percentage()
        print(f"Tests: {passed}/{total} passed ({percentage:.1f}%)")

        update_readme_badges(readme_path, version, percentage)
        print(f"✓ Updated {readme_path}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
