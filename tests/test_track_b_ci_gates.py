"""Track B CI gates: v3.5 frontmatter roundtrip, depends parity.

Tests here cover the Track B migration validation gates that remain valid
under hook-based rule discovery, after the legacy standalone rule index was
removed in favour of per-rule frontmatter.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = REPO_ROOT / "rules"
CANARY_REPORT = REPO_ROOT / ".workbench" / "results" / "canary_migration_report.json"
FULL_REPORT = REPO_ROOT / ".workbench" / "results" / "full_migration_report.json"


def _iter_frontmatter_rules() -> list[Path]:
    """Return rules that use YAML frontmatter (v3.5)."""
    out: list[Path] = []
    for p in sorted(RULES_DIR.glob("*.md")):
        first = p.read_text(encoding="utf-8").split("\n", 1)[0]
        if first.strip() == "---":
            out.append(p)
    return out


@pytest.mark.unit
def test_frontmatter_roundtrip_all_migrated_rules() -> None:
    """Every migrated rule's frontmatter parses with yaml.safe_load and has the 7 required keys."""
    required_keys = {
        "schema_version",
        "rule_version",
        "last_updated",
        "keywords",
        "token_budget",
        "context_tier",
        "depends",
    }
    files = _iter_frontmatter_rules()
    assert files, "expected at least one migrated (v3.5 frontmatter) rule"
    for path in files:
        text = path.read_text(encoding="utf-8")
        block = text.split("---", 2)[1]
        data = yaml.safe_load(block)
        assert isinstance(data, dict), f"{path.name}: frontmatter is not a mapping"
        missing = required_keys - set(data.keys())
        assert not missing, f"{path.name}: missing frontmatter keys {missing}"
        assert str(data["schema_version"]).strip() == "v3.5", (
            f"{path.name}: schema_version={data['schema_version']!r} (expected v3.5)"
        )


@pytest.mark.integration
def test_depends_parity_canary_report_exists_and_matches() -> None:
    """Canary migration report captures pre/post depends parity for rules/206-python-pytest.md."""
    if not CANARY_REPORT.exists():
        pytest.skip("canary report not present in this workspace")
    report = json.loads(CANARY_REPORT.read_text(encoding="utf-8"))
    rule_report = report["206-python-pytest.md"]
    old_dep_names = {entry.split(":", 1)[1] for entry in rule_report["old_depends"]}
    new_dep_names = {entry["name"] for entry in rule_report["new_depends_with_comments"]}
    assert old_dep_names == new_dep_names, (
        f"canary depends parity failed: old={old_dep_names} new={new_dep_names}"
    )


@pytest.mark.integration
def test_depends_parity_full_migration_report_covers_all_migrated_rules() -> None:
    """Full migration report has an entry for every migrated rule."""
    if not FULL_REPORT.exists():
        pytest.skip("full migration report not present in this workspace")
    report = json.loads(FULL_REPORT.read_text(encoding="utf-8"))
    migrated_names = {p.name for p in _iter_frontmatter_rules()}
    reported_names = {
        name
        for name, entry in report.items()
        if ("old_version" in entry and "new_version" in entry)
        or entry.get("skipped") == "already-frontmatter"
    }
    missing = migrated_names - reported_names
    assert not missing, f"migrated rules missing from report: {sorted(missing)[:5]}"
