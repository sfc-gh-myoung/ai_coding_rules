"""Project root detection and common path resolution."""

from pathlib import Path


def find_project_root() -> Path:
    """Find the project root by looking for pyproject.toml.

    Walks up from CWD looking for pyproject.toml.

    Returns:
        Path to project root directory.

    Raises:
        FileNotFoundError: If no pyproject.toml found.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    raise FileNotFoundError("Could not find project root (no pyproject.toml found)")


def get_rules_dir(project_root: Path | None = None) -> Path:
    """Get the rules directory path."""
    root = project_root or find_project_root()
    return root / "rules"


def get_schemas_dir(project_root: Path | None = None) -> Path:
    """Get the schemas directory path."""
    root = project_root or find_project_root()
    return root / "schemas"
