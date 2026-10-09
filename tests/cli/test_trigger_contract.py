"""Phase 4: scoped trigger-count contract validator.

Positive control (the real repo is consistent) plus the six sabotage controls
required by the plan: ASCII ``5-7``, en-dashed ``5–7``, ``5-20``, ``5-9``,
``max_items: 7``, and an unregistered bound-bearing file. Each must turn a gate
red. Also verifies the detector excludes date/percentage false positives.
"""

# Sabotage inputs intentionally include a literal en dash to exercise detection.
# ruff: noqa: RUF002, RUF003

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands.rule_loader import trigger_contract as tc

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})


def _project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("project root not found")


_SCHEMA_5_11 = """
metadata:
  required_fields:
    - name: Keywords
      min_items: 5
      max_items: 11
"""

_SCHEMA_5_7 = """
metadata:
  required_fields:
    - name: Keywords
      min_items: 5
      max_items: 7
"""


# ── canonical-bound extraction ───────────────────────────────────────────────


def test_canonical_bounds_from_repo_schema() -> None:
    schema = (_project_root() / "schemas" / "rule-schema.yml").read_text(encoding="utf-8")
    assert tc.canonical_bounds(schema) == (5, 11)


def test_canonical_bounds_reads_max_items_7_sabotage() -> None:
    # Sabotage control #5: max_items: 7 changes the canonical maximum, which then
    # makes every 5-11 surface contradictory.
    assert tc.canonical_bounds(_SCHEMA_5_7) == (5, 7)
    violations = tc.surface_violations("x.md", "Keywords: 5-11 typed entries", 5, 7)
    assert violations, "a 5-11 total bound must contradict a max_items:7 schema"


# ── sabotage controls on a single surface ────────────────────────────────────


@pytest.mark.parametrize(
    "text",
    [
        "Keywords count is 5-7 terms",  # ASCII 5-7
        "Keywords count is 5\u20137 terms",  # en-dash 5–7
        "Keywords within 5-20 range",  # 5-20
        "Keyword bound 5-9 combined",  # 5-9
    ],
)
def test_wrong_total_bound_is_a_violation(text: str) -> None:
    assert tc.surface_violations("surface.md", text, 5, 11), f"expected violation for: {text!r}"


def test_correct_total_bound_passes() -> None:
    assert tc.surface_violations("surface.md", "Keywords: 5-11 combined typed entries", 5, 11) == []


def test_semantic_advisory_5_7_is_allowed() -> None:
    # 5-7 qualified as semantic (kw:) is within the hard bound: not a violation.
    text = "Advisory shape: 5-7 semantic kw: keywords within the combined bound"
    assert tc.surface_violations("surface.md", text, 5, 11) == []


def test_semantic_advisory_exceeding_max_is_flagged() -> None:
    text = "Advisory: 5-12 semantic kw: keywords"
    assert tc.surface_violations("surface.md", text, 5, 11)


# ── false-positive exclusion ─────────────────────────────────────────────────


def test_date_and_percentage_are_not_bounds() -> None:
    # 'sonnet-45-2025' (date) and '95-96%' (percentage) embed 5-N substrings but
    # must not be detected as keyword bounds.
    assert not tc.has_total_bound_token("file: keyword-review-claude-sonnet-45-2025-12-15.md")
    assert not tc.has_total_bound_token("keyword alignment is 95-96% across rules")


def test_non_keyword_context_5_7_is_ignored() -> None:
    # '5-7 business days' / '5-7 visualizations' are incidental, not keyword bounds.
    assert not tc.has_total_bound_token("Standard shipping takes 5-7 business days.")
    assert not tc.has_total_bound_token("Dashboards with 5-7 visualizations max")


def test_semantic_line_is_not_a_total_bound_token() -> None:
    assert not tc.has_total_bound_token("generate 5-7 semantic (kw:) discovery keywords")


def test_non_semantic_keyword_bound_is_a_total_token() -> None:
    # Sabotage control #6 building block: a plain keyword-count bound is detected.
    assert tc.has_total_bound_token("Keywords must contain 5-8 terms")


# ── end-to-end completeness (temp tree) ──────────────────────────────────────


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_unregistered_bound_bearing_file_fails(tmp_path: Path, monkeypatch) -> None:
    """Sabotage control #6: a new file carrying a total bound but not registered."""
    _write(tmp_path, "schemas/rule-schema.yml", _SCHEMA_5_11)
    _write(tmp_path, "rules/registered.md", "Keywords: 5-11 combined typed entries")
    _write(tmp_path, "rules/sneaky.md", "Keywords must be 5-8 typed entries")

    monkeypatch.setattr(tc, "REGISTERED_SURFACES", frozenset({"rules/registered.md"}))
    monkeypatch.setattr(tc, "ALLOWLISTED_SURFACES", frozenset())

    violations = tc.validate_trigger_contract(tmp_path)
    assert any("sneaky.md" in v for v in violations)


def test_clean_temp_tree_passes(tmp_path: Path, monkeypatch) -> None:
    _write(tmp_path, "schemas/rule-schema.yml", _SCHEMA_5_11)
    _write(tmp_path, "rules/registered.md", "Keywords: 5-11 combined typed entries")

    monkeypatch.setattr(tc, "REGISTERED_SURFACES", frozenset({"rules/registered.md"}))
    monkeypatch.setattr(tc, "ALLOWLISTED_SURFACES", frozenset())

    assert tc.validate_trigger_contract(tmp_path) == []


# ── real repo + CLI ──────────────────────────────────────────────────────────


def test_repo_trigger_contract_is_consistent() -> None:
    assert tc.validate_trigger_contract(_project_root()) == []


def test_cli_validate_trigger_contract_exits_zero() -> None:
    result = runner.invoke(app, ["rule-loader", "validate-trigger-contract"])
    assert result.exit_code == 0
