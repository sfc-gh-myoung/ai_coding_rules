"""Phase 3: shared manifest builder fixture gate.

Covers the deterministic manifest-recall check that runs the REAL production
pipeline (``build_eval_manifest``) against fixtures and reports required rules
absent from the injected manifest (RC5). The check is report-only by default
(CI stays green until Phase 5 metadata restoration) and hard under
``--enforce-manifest``.

Positive controls are expressed in isolation so they remain durable across the
Phase 5 metadata cutover: they construct a guaranteed miss / guaranteed clean
recall rather than depending on the transient state of any real fixture.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.match_rules import load_rules_db
from ai_rules.rule_loader_eval.fixtures import (
    Fixture,
    TriggerEvidence,
    manifest_recall_errors,
)

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})


def _project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("project root not found")


def _mk_fixture(prompt: str, required: tuple[str, ...]) -> Fixture:
    return Fixture(
        path=Path("<synthetic>"),
        schema_version=1,
        updated="2026-08-02T00:00:00+00:00",
        id="synthetic",
        description="synthetic recall probe",
        variant="simple",
        prompt=prompt,
        required=required,
        dependencies=(),
        forbidden=(),
        optional=(),
        trigger_evidence=TriggerEvidence(),
    )


# ── pure function: manifest_recall_errors ───────────────────────────────────


def test_recall_complete_for_foundation_only() -> None:
    """Foundation is loaded unconditionally, so a fixture requiring only it recalls."""
    rules_db = load_rules_db(_project_root() / "rules")
    fixture = _mk_fixture("do anything at all", ("rules/000-global-core.md",))
    assert manifest_recall_errors(fixture, rules_db) == []


def test_recall_miss_is_a_positive_control() -> None:
    """A required rule that the prompt cannot match must be reported as absent.

    This is the gate's positive control: remove/displace the trigger (here by
    giving a prompt with no matching signal) and the gate turns red.
    """
    rules_db = load_rules_db(_project_root() / "rules")
    # A neutral prompt with no domain signal cannot recall a specific domain rule.
    fixture = _mk_fixture("hello there", ("rules/002h-claude-code-skills.md",))
    errors = manifest_recall_errors(fixture, rules_db)
    assert errors, "expected an unmatched required rule to be reported as a miss"
    assert "rules/002h-claude-code-skills.md" in errors[0]
    assert "absent from deterministic manifest" in errors[0]


def test_recall_reports_one_error_per_missing_rule() -> None:
    rules_db = load_rules_db(_project_root() / "rules")
    fixture = _mk_fixture(
        "neutral prompt",
        ("rules/002h-claude-code-skills.md", "rules/116-snowflake-cortex-search.md"),
    )
    errors = manifest_recall_errors(fixture, rules_db)
    assert len(errors) == 2


# ── CLI: report-only default vs --enforce-manifest ──────────────────────────


def test_validate_help_documents_enforce_flag() -> None:
    result = runner.invoke(app, ["rule-loader", "validate", "--help"])
    assert result.exit_code == 0
    assert "--enforce-manifest" in result.output
    assert "--report-only" in result.output


def test_validate_enforces_by_default_and_passes() -> None:
    """Phase 5 cutover: manifest recall is enforced by default; repo recalls all fixtures."""
    result = runner.invoke(app, ["rule-loader", "validate"])
    assert result.exit_code == 0
    assert "manifest recall" in result.output


def test_validate_report_only_flag_never_fails() -> None:
    """--report-only records misses without failing, regardless of recall state."""
    result = runner.invoke(app, ["rule-loader", "validate", "--report-only"])
    assert result.exit_code == 0


def test_enforce_manifest_passes_when_recall_is_clean(monkeypatch) -> None:
    """With no misses, --enforce-manifest exits 0 (isolated from real state)."""
    monkeypatch.setattr(
        "ai_rules.rule_loader_eval.fixtures.manifest_recall_errors",
        lambda fixture, rules_db: [],
    )
    result = runner.invoke(app, ["rule-loader", "validate", "--enforce-manifest"])
    assert result.exit_code == 0


def test_enforce_manifest_fails_on_injected_miss(monkeypatch) -> None:
    """A single injected miss makes --enforce-manifest exit 1 (EXIT_FIXTURE_FAIL)."""
    calls = {"n": 0}

    def _one_miss(fixture, rules_db):
        calls["n"] += 1
        # Report a miss for exactly one fixture so the gate turns red once.
        if calls["n"] == 1:
            return ["required rule rules/sabotage.md absent from deterministic manifest"]
        return []

    monkeypatch.setattr("ai_rules.rule_loader_eval.fixtures.manifest_recall_errors", _one_miss)
    result = runner.invoke(app, ["rule-loader", "validate", "--enforce-manifest"])
    assert result.exit_code == 1
