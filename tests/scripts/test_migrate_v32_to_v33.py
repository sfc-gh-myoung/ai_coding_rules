"""Tests for scripts/migrate_v32_to_v33.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "migrate_v32_to_v33",
        Path(__file__).resolve().parents[2] / "scripts" / "migrate_v32_to_v33.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


migrate = _load_module()


SAMPLE_HEADER = """# Sample Rule

> Some opening notes.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-25
"""


def _build(metadata_extra: str) -> str:
    return SAMPLE_HEADER + metadata_extra + "\n## Scope\n\nBody untouched.\n"


@pytest.mark.unit
def test_merge_keywords_load_triggers_first():
    out = migrate.merge_keywords("Python, Ruff, Type Hints", "ext:.py, file:pyproject.toml")
    assert out == "ext:.py, file:pyproject.toml, kw:python, kw:ruff, kw:type hints"


@pytest.mark.unit
def test_merge_keywords_pure_semantic():
    out = migrate.merge_keywords("SQL, CTE, performance", "")
    assert out == "kw:sql, kw:cte, kw:performance"


@pytest.mark.unit
def test_merge_keywords_pure_load_trigger():
    out = migrate.merge_keywords("", "ext:.sql, file:Dockerfile")
    assert out == "ext:.sql, file:Dockerfile"


@pytest.mark.unit
def test_merge_keywords_already_typed_passthrough():
    out = migrate.merge_keywords("kw:python, ext:.py", "ext:.py")
    # ext:.py from LoadTrigger first, then kw:python from Keywords; ext:.py de-duped.
    assert out == "ext:.py, kw:python"


@pytest.mark.unit
def test_rewrite_depends_none_passthrough():
    assert migrate.rewrite_depends("None") == "None"
    assert migrate.rewrite_depends("") == "None"
    assert migrate.rewrite_depends("-") == "-"


@pytest.mark.unit
def test_rewrite_depends_bare_names_get_required_prefix():
    out = migrate.rewrite_depends("000-global-core.md, 100-snowflake-core.md")
    assert out == "required:000-global-core.md, required:100-snowflake-core.md"


@pytest.mark.unit
def test_rewrite_depends_already_prefixed_idempotent():
    out = migrate.rewrite_depends("required:a.md, optional:b.md")
    assert out == "required:a.md, optional:b.md"


@pytest.mark.unit
def test_migrate_content_full_block():
    src = _build(
        "**Keywords:** Python, uv, Ruff\n"
        "**TokenBudget:** ~2000\n"
        "**ContextTier:** High\n"
        "**Depends:** 000-global-core.md\n"
        "**LoadTrigger:** ext:.py, ext:.pyi, file:pyproject.toml\n"
    )
    out, changed = migrate.migrate_content(src)
    assert changed
    assert "**LoadTrigger:**" not in out
    assert "**Keywords:** ext:.py, ext:.pyi, file:pyproject.toml, kw:python, kw:uv, kw:ruff" in out
    assert "**Depends:** required:000-global-core.md" in out
    assert "**SchemaVersion:** v3.3" in out
    # Body untouched.
    assert out.endswith("Body untouched.\n")


@pytest.mark.unit
def test_migrate_content_idempotent():
    src = _build(
        "**Keywords:** Python\n**Depends:** 000-global-core.md\n**LoadTrigger:** ext:.py\n"
    )
    once, changed_once = migrate.migrate_content(src)
    assert changed_once
    twice, changed_twice = migrate.migrate_content(once)
    assert not changed_twice
    assert once == twice


@pytest.mark.unit
def test_migrate_content_depends_none_preserved():
    src = _build("**Keywords:** workflow, safety\n**Depends:** None\n")
    out, changed = migrate.migrate_content(src)
    assert changed
    assert "**Depends:** None" in out
    assert "**Keywords:** kw:workflow, kw:safety" in out


@pytest.mark.unit
def test_migrate_content_no_load_trigger_only_keywords():
    src = _build("**Keywords:** SQL, performance\n**Depends:** None\n")
    out, changed = migrate.migrate_content(src)
    assert changed
    assert "**Keywords:** kw:sql, kw:performance" in out
    assert "**LoadTrigger:**" not in out


@pytest.mark.unit
def test_iter_rule_files_skips_special_names(tmp_path: Path):
    (tmp_path / "100-foo.md").write_text("x")
    (tmp_path / "RULES_INDEX.md").write_text("x")
    (tmp_path / "README.md").write_text("x")
    (tmp_path / "CHANGELOG.md").write_text("x")
    files = migrate.iter_rule_files(tmp_path)
    assert [p.name for p in files] == ["100-foo.md"]


@pytest.mark.unit
def test_main_dry_run_does_not_write(tmp_path: Path, capsys):
    target = tmp_path / "100-foo.md"
    src = _build("**Keywords:** Python\n**Depends:** None\n**LoadTrigger:** ext:.py\n")
    target.write_text(src, encoding="utf-8")

    rc = migrate.main([str(target), "--dry-run"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "would migrate" in captured.out
    # File unchanged on dry-run.
    assert target.read_text(encoding="utf-8") == src


@pytest.mark.unit
def test_main_writes_changes(tmp_path: Path):
    target = tmp_path / "100-foo.md"
    src = _build("**Keywords:** Python\n**Depends:** None\n**LoadTrigger:** ext:.py\n")
    target.write_text(src, encoding="utf-8")

    rc = migrate.main([str(target)])
    assert rc == 0
    out = target.read_text(encoding="utf-8")
    assert "**Keywords:** ext:.py, kw:python" in out
    assert "**LoadTrigger:**" not in out
    assert "**SchemaVersion:** v3.3" in out
