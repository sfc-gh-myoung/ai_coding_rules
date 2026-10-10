"""Display grouped Make target help or project interpreter and counts."""

import argparse
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

SECTION = re.compile(r"^##@\s+(.+)$")
TARGET = re.compile(r"^([a-z][a-z0-9-]*):[^=]*?##\s+(.+)$")


def make_targets(makefile: Path) -> dict[str, list[tuple[str, str]]]:
    """Group documented targets by their `##@` section, in file order."""
    groups: dict[str, list[tuple[str, str]]] = {}
    group = "General"
    for line in makefile.read_text().splitlines():
        if section := SECTION.match(line):
            group = section.group(1)
        elif target := TARGET.match(line):
            groups.setdefault(group, []).append((target.group(1), target.group(2)))
    return groups


def main() -> None:
    """Show help or status without maintaining a second target registry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("help", "status"))
    arguments = parser.parse_args()
    if arguments.mode == "help":
        for group, entries in make_targets(Path("Makefile")).items():
            print(f"\n{group.upper()}")
            for name, description in entries:
                print(f"  make {name:24} {description}")
        print(
            "\nVariables: UV, PYTHON_VERSION (or UV_PYTHON), CLI_ARGS, VERSION, FORCE, DRY_RUN."
            "\nDetails: docs/USING_DEV_CLI.md."
        )
        return
    for label, pattern in (
        ("Rules", "rules/*.md"),
        ("Examples", "rules/examples/*.md"),
        ("Skills", "skills/*/SKILL.md"),
        ("Tests", "tests/**/test_*.py"),
    ):
        print(f"{label}: {sum(path.is_file() for path in Path('.').glob(pattern))}")
    print(f"Python: {platform.python_version()} ({sys.executable})", flush=True)
    subprocess.run([os.environ.get("UV", "uv"), "--version"], check=True)
    version = subprocess.run(["make", "--version"], check=True, capture_output=True, text=True)
    print(version.stdout.splitlines()[0])


if __name__ == "__main__":
    main()
