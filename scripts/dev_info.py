"""Display grouped Task discovery or project interpreter and counts."""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

import yaml


def main() -> None:
    """Show help or status without maintaining a second task registry."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("help", "status"))
    arguments = parser.parse_args()
    if arguments.mode == "help":
        tasks = yaml.safe_load(Path("Taskfile.yml").read_text())["tasks"]
        groups: dict[str, list[tuple[str, str]]] = {}
        for name, definition in sorted(tasks.items()):
            if definition.get("internal") or name == "default":
                continue
            group = name.split(":")[0] if ":" in name else "quickstart"
            groups.setdefault(group, []).append((name, definition.get("desc", "")))
        for group, entries in groups.items():
            print(f"\n{group.upper()}")
            for name, description in entries:
                print(f"  {name:28} {description}")
        print("\nDetails: task --summary <task>. Machine-readable list: task --list --json.")
        return
    for label, pattern in (
        ("Rules", "rules/*.md"),
        ("Examples", "rules/examples/*.md"),
        ("Skills", "skills/*/SKILL.md"),
        ("Tests", "tests/**/test_*.py"),
    ):
        print(f"{label}: {sum(path.is_file() for path in Path('.').glob(pattern))}")
    print(f"Python: {platform.python_version()} ({sys.executable})")
    subprocess.run([os.environ.get("UV", "uv"), "--version"], check=True)
    subprocess.run(["task", "--version"], check=True)


if __name__ == "__main__":
    main()
