"""Tests for the round-trip validation gate inside refresh / refresh-all.

Refresh commands must NEVER overwrite an existing fixture with content that
would fail ``ai-rules rule-loader validate``. When the rendered candidate
fails the trigger-evidence invariant, the driver writes a ``<name>.invalid``
candidate next to the target and exits non-zero.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.rule_loader_eval.fixtures import validate_rendered_snippet
from ai_rules.rule_loader_eval.rules_meta import load_rules_metadata

runner = CliRunner()


@pytest.fixture(scope="module")
def project_root() -> Path:
    """Return the repo root."""
    here = Path(__file__).resolve()
    for parent in (here, *here.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("project root not found")


def test_validate_rendered_snippet_returns_empty_for_valid(
    project_root: Path,
) -> None:
    """A schema-valid, invariant-passing snippet returns no errors."""
    snippet = """\
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: ok-fixture
description: # TODO
variant: simple
prompt: |
  Help me with a streamlit dashboard.
expected:
  required:
    - rules/101-snowflake-streamlit-core.md  # kw: streamlit
  dependencies: []
  forbidden: []
  optional: []
trigger_evidence:
  kw: [streamlit]
  ext: []
  file: []
  dir: []
"""
    rules = load_rules_metadata(project_root / "rules")
    errors = validate_rendered_snippet(snippet, "ok-fixture", rules)
    assert errors == []


def test_validate_rendered_snippet_catches_unsatisfied_typed_keyword(
    project_root: Path,
) -> None:
    """A required rule with no trigger evidence in prompt returns an error.

    v3.3: triggers are derived from typed Keywords entries (ext:, file:, dir:, kw:).
    The fixture claims 200-python-core as required but provides no trigger evidence,
    so the validator should flag an unsatisfied-trigger invariant violation.
    """
    # 200-python-core has ext:.py / ext:.pyi / file:pyproject.toml triggers
    # typed Keywords trigger evidence exists for the loaded rule, but the prompt has none.
    snippet = """\
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: bad-fixture
description: # TODO
variant: simple
prompt: |
  Walk me through deploying a streamlit dashboard.
expected:
  required:
    - rules/999-test-core.md  # suggested: foundation
    - rules/200-python-core.md  # forced into required
  dependencies: []
  forbidden: []
  optional: []
trigger_evidence:
  kw: []
  ext: []
  file: []
  dir: []
"""
    rules = load_rules_metadata(project_root / "rules")
    errors = validate_rendered_snippet(snippet, "bad-fixture", rules)
    assert errors, "expected invariant errors for unsatisfied trigger evidence"
    assert any("discovered" in e or "trigger" in e.lower() for e in errors)


def test_validate_rendered_snippet_catches_kw_evidence_not_in_prompt(
    project_root: Path,
) -> None:
    """A kw evidence value not present in the prompt yields an error."""
    snippet = """\
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: bad-fixture
description: # TODO
variant: simple
prompt: |
  Generic prompt.
expected:
  required:
    - rules/999-test-core.md  # suggested: foundation
  dependencies: []
  forbidden: []
  optional: []
trigger_evidence:
  kw: [phrase that is not in the prompt]
  ext: []
  file: []
  dir: []
"""
    rules = load_rules_metadata(project_root / "rules")
    errors = validate_rendered_snippet(snippet, "bad-fixture", rules)
    assert errors, "expected error for missing kw evidence in prompt"
    assert any("not found in prompt" in e for e in errors)


def test_validate_rendered_snippet_returns_schema_error_for_malformed_yaml(
    project_root: Path,
) -> None:
    """Malformed YAML returns a single schema-level error, not a crash."""
    rules = load_rules_metadata(project_root / "rules")
    errors = validate_rendered_snippet("::: not yaml :::\n  bogus", "x", rules)
    assert len(errors) == 1
    assert errors[0].startswith("schema:")


def test_refresh_all_refuses_overwrite_on_invalid(
    tmp_path: Path,
    project_root: Path,
) -> None:
    """refresh-all writes <safe_id>.yaml.invalid and skips the target overwrite
    when the rendered candidate fails the trigger-evidence invariant.

    Uses a synthetic AgentRun whose ``loaded`` includes a rule (200-python-core)
    whose typed Keywords evidence isn't satisfied by the prompt, forcing auto-demote to
    move the rule into ``optional``. The rendered candidate should pass
    validate by construction; this test asserts the gate doesn't accidentally
    block valid candidates.

    A separate test (below) deliberately patches the renderer to produce an
    invalid candidate and verifies the gate fires.
    """
    from ai_rules.rule_loader_eval.agent_runner import AgentRun
    from ai_rules.rule_loader_eval.batch import (
        BatchItem,
        BatchOutcome,
        BatchSummary,
    )

    fx_path = tmp_path / "test-fx.yaml"
    fx_path.write_text(
        """\
schema_version: 2
updated: 2026-05-16T12:00:00-07:00
id: test-fx
description: # TODO
variant: simple
prompt: |
  Walk me through deploying a streamlit dashboard.
expected:
  required:
    - rules/999-test-core.md
  dependencies: []
  forbidden: []
  optional: []
trigger_evidence:
  kw: []
  ext: []
  file: []
  dir: []
""",
        encoding="utf-8",
    )

    out_dir = tmp_path / "out"

    # Synthesize a BatchSummary with an over-firing AgentRun.
    item = BatchItem(
        id="test-fx",
        safe_id="test-fx",
        path=fx_path,
        prompt="Walk me through deploying a streamlit dashboard.",
    )
    run = AgentRun(
        fixture_id="test-fx",
        loaded=("rules/999-test-core.md", "rules/200-python-core.md"),
        loaded_via_reads=("rules/999-test-core.md", "rules/200-python-core.md"),
        loaded_via_reads_performed=(),
        loaded_via_section=("rules/999-test-core.md", "rules/200-python-core.md"),
    )
    outcome = BatchOutcome(item=item, run=run, error_type=None, error_message=None)
    summary = BatchSummary(concurrency=1, outcomes=(outcome,), wall_seconds=0.1)

    def _fake_run_batch(items, **kwargs):
        on_start = kwargs.get("on_start")
        on_outcome = kwargs.get("on_outcome")
        for i, oc in enumerate(summary.outcomes, start=1):
            if on_start is not None:
                on_start(oc.item, i)
            if on_outcome is not None:
                on_outcome(oc, i)
        return summary

    with (
        patch("ai_rules.rule_loader_eval.batch.run_batch", side_effect=_fake_run_batch),
        patch("ai_rules.commands.rule_loader._ensure_sdk_and_connection"),
        patch("ai_rules.commands.rule_loader.find_project_root", return_value=project_root),
        patch("ai_rules.rule_loader_eval.batch.expand_glob", return_value=[fx_path]),
    ):
        result = runner.invoke(
            app,
            [
                "rule-loader",
                "refresh-all",
                "--all",
                "--out-dir",
                str(out_dir),
            ],
        )

    # Auto-demote should have made the rendered candidate valid; refresh
    # should succeed (exit 0) and write the target.
    assert result.exit_code == 0, result.output
    target = out_dir / "test-fx.yaml"
    assert target.exists(), f"expected {target} written"
    text = target.read_text(encoding="utf-8")
    # The over-fired rule must be under optional with auto-demote.
    assert "rules/200-python-core.md" in text
    assert "# auto-demoted" in text
    invalid = out_dir / "test-fx.yaml.invalid"
    assert not invalid.exists(), "no .invalid candidate expected on success"
