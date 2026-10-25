"""Display project interpreter and counts."""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


def main() -> None:
    """Show project counts and the selected interpreter."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("status",))
    parser.parse_args()
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
