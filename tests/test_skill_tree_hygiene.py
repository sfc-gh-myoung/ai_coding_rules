"""Regression checks for generated files in canonical skill trees."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"


def test_canonical_skill_trees_have_no_generated_files() -> None:
    """Reject cache and Finder artifacts committed or left in skills/."""
    generated = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in SKILLS_ROOT.rglob("*")
        if path.name == ".DS_Store" or path.suffix == ".pyc" or "__pycache__" in path.parts
    ]

    assert generated == [], f"generated files found in canonical skill trees: {generated}"


def test_gitignore_excludes_generated_skill_tree_files() -> None:
    """Keep generated files out of future commits."""
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "__pycache__/" in gitignore
    assert ".DS_Store" in gitignore
