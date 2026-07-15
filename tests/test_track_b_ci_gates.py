"""Track B CI gates: v3.5 frontmatter roundtrip, depends parity, index golden-file, stats determinism.

Tests here are named to match the plan §12 Phase 2 Step 9 CI matrix pytest -k selectors:
- frontmatter_roundtrip
- depends_parity
- golden_file
- index_regen_coupling
- stats_determinism
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_DIR = REPO_ROOT / "rules"
BASELINE_INDEX = REPO_ROOT / ".workbench" / "baselines" / "pre-track-b" / "RULES_INDEX.md"
BASELINE_VERSIONS = REPO_ROOT / ".workbench" / "baselines" / "pre-track-a" / "rule_versions.json"
CANARY_REPORT = REPO_ROOT / ".workbench" / "results" / "canary_migration_report.json"
FULL_REPORT = REPO_ROOT / ".workbench" / "results" / "full_migration_report.json"


def _iter_frontmatter_rules() -> list[Path]:
    """Return rules that use YAML frontmatter (v3.5)."""
    out: list[Path] = []
    for p in sorted(RULES_DIR.glob("*.md")):
        if p.name in {"RULES_INDEX.md"}:
            continue
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
        # Migrated entries carry old/new version pairs; already-migrated rules
        # (e.g. canary re-run) are recorded with a `skipped: already-frontmatter` note.
        if ("old_version" in entry and "new_version" in entry)
        or entry.get("skipped") == "already-frontmatter"
    }
    missing = migrated_names - reported_names
    assert not missing, f"migrated rules missing from report: {sorted(missing)[:5]}"


@pytest.mark.integration
def test_golden_file_index_matches_baseline() -> None:
    """RULES_INDEX.md matches the pre-Track-B baseline byte-for-byte (dual-parse invariant)."""
    if not BASELINE_INDEX.exists():
        pytest.skip("pre-track-b baseline not present")
    current = (RULES_DIR / "RULES_INDEX.md").read_text(encoding="utf-8")
    baseline = BASELINE_INDEX.read_text(encoding="utf-8")
    assert current == baseline, "RULES_INDEX.md drifted from pre-track-b baseline"


@pytest.mark.integration
def test_index_regen_coupling_git_diff_clean() -> None:
    """After `ai-rules index generate`, git working tree for RULES_INDEX.md is unchanged."""
    subprocess.run(
        ["uv", "run", "ai-rules", "index", "generate"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    result = subprocess.run(
        ["git", "diff", "--exit-code", "rules/RULES_INDEX.md"],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    assert result.returncode == 0, (
        f"RULES_INDEX.md changed after regenerate: {result.stdout.decode()[:500]}"
    )


@pytest.mark.integration
def test_stats_determinism_masks_volatile_keys() -> None:
    """`.index-stats.json` is deterministic modulo volatile keys (generated_at, git_sha)."""
    from ai_rules.commands import index as index_module

    stats_path = RULES_DIR / index_module.STATS_FILENAME
    original = json.loads(stats_path.read_text(encoding="utf-8"))
    subprocess.run(
        ["uv", "run", "ai-rules", "index", "generate"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
    )
    regenerated = json.loads(stats_path.read_text(encoding="utf-8"))
    for key in index_module.STATS_VOLATILE_KEYS:
        original.pop(key, None)
        regenerated.pop(key, None)
    assert original == regenerated, "non-volatile stats fields drifted across regeneration"
