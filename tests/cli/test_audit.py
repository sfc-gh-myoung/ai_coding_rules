"""Phase 5: corpus trigger-reachability audit.

Unit coverage for probe construction, disposition-based resolution, integrity
(stale/invalid keys), and the scope circuit breaker exit codes. Plus a
real-repo positive control: with the committed disposition sidecar, the audit
exits 0.
"""

from __future__ import annotations

from typer.testing import CliRunner

from ai_rules.cli import app
from ai_rules.commands.rule_loader import audit as A

runner = CliRunner(env={"NO_COLOR": "1", "CI": "true", "TERM": "dumb"})

_IDENT = {
    "git_sha": "deadbeef",
    "rules_digest": "rd",
    "matcher_digest": "md",
    "schema_version": "3.6",
    "generator_version": "1",
}


def _rec(rule_id: str, kind: str, value: str, in_manifest: bool, rank=None, score=None) -> dict:
    return {
        "rule_id": rule_id,
        "trigger_kind": kind,
        "trigger_value": value,
        "probe": "p",
        "prompt_source": "synthetic",
        "in_manifest": in_manifest,
        "rank": rank,
        "score": score,
    }


# ── probe construction ───────────────────────────────────────────────────────


def test_probe_ext_file_dir_shapes() -> None:
    assert A._probe("ext", ".py", "rules/x.md", {}) == ("probe.py", "synthetic")
    assert A._probe("file", "snowflake.yml", "rules/x.md", {}) == ("snowflake.yml", "synthetic")
    assert A._probe("dir", "skills/", "rules/x.md", {}) == ("skills/probe.txt", "synthetic")


def test_probe_kw_uses_fixture_prompt_when_available() -> None:
    fx = {"rules/x.md": ["do the thing with skills"]}
    prompt, source = A._probe("kw", "skill", "rules/x.md", fx)
    assert source == "fixture"
    assert prompt == "do the thing with skills"


def test_probe_kw_synthetic_is_not_exact_phrase_only() -> None:
    prompt, source = A._probe("kw", "cortex search", "rules/x.md", {})
    assert source == "synthetic"
    assert prompt.startswith("cortex search")
    assert prompt != "cortex search"  # competing signals appended


def test_family_prefix() -> None:
    assert A._family("rules/112-snowflake-snowcli.md") == "112"
    assert A._family("rules/002h-claude-code-skills.md") == "002h"


# ── disposition key ignores git_sha (survives commits) ───────────────────────


def test_disposition_key_excludes_git_sha() -> None:
    rec = _rec("rules/x.md", "kw", "foo", False)
    ident2 = {**_IDENT, "git_sha": "different"}
    assert A.disposition_key(rec, _IDENT) == A.disposition_key(rec, ident2)


# ── evaluate: misses, resolution, integrity ──────────────────────────────────


def test_miss_without_disposition_is_unresolved() -> None:
    recs = [_rec("rules/x.md", "kw", "foo", in_manifest=False)]
    misses, integrity = A.evaluate(recs, _IDENT, {})
    assert len(misses) == 1
    assert integrity == []


def test_intentional_exception_resolves_miss() -> None:
    recs = [_rec("rules/x.md", "kw", "foo", in_manifest=False)]
    key = A.disposition_key(recs[0], _IDENT)
    disp = {key: {"disposition": "intentional-exception", "justification": "why"}}
    misses, integrity = A.evaluate(recs, _IDENT, disp)
    assert misses == []
    assert integrity == []


def test_exception_without_justification_is_integrity_error() -> None:
    recs = [_rec("rules/x.md", "kw", "foo", in_manifest=False)]
    key = A.disposition_key(recs[0], _IDENT)
    disp = {key: {"disposition": "intentional-exception"}}
    misses, integrity = A.evaluate(recs, _IDENT, disp)
    assert any("without justification" in e for e in integrity)


def test_stale_disposition_key_is_integrity_error() -> None:
    recs = [_rec("rules/x.md", "kw", "foo", in_manifest=False)]
    disp = {"rules/gone.md|kw|bar|rd|md|3.6|1": {"disposition": "ok"}}
    misses, integrity = A.evaluate(recs, _IDENT, disp)
    assert any("stale disposition key" in e for e in integrity)


def test_in_manifest_records_are_never_misses() -> None:
    recs = [_rec("rules/x.md", "kw", "foo", in_manifest=True)]
    misses, integrity = A.evaluate(recs, _IDENT, {})
    assert misses == []


# ── reconciliation ──────────────────────────────────────────────────────────


def test_reconcile_carries_only_same_current_miss() -> None:
    prior = _rec("rules/x.md", "kw", "foo", in_manifest=False)
    resolved = _rec("rules/y.md", "kw", "bar", in_manifest=True)
    old = {
        A.disposition_key(prior, _IDENT): {
            "disposition": "intentional-exception",
            "justification": "why",
        },
        A.disposition_key(resolved, _IDENT): {"disposition": "ok"},
    }
    current_identity = {
        **_IDENT,
        "rules_digest": "new-rules",
        "matcher_digest": "new-matcher",
    }

    reconciled, unresolved, retired = A.reconcile_dispositions(
        [prior, resolved], current_identity, old
    )

    assert reconciled == {
        A.disposition_key(prior, current_identity): {
            "disposition": "intentional-exception",
            "justification": "why",
        }
    }
    assert unresolved == []
    assert retired == 1


def test_reconcile_leaves_new_misses_unapproved() -> None:
    prior = _rec("rules/x.md", "kw", "foo", in_manifest=False)
    new = _rec("rules/y.md", "kw", "bar", in_manifest=False)
    old = {A.disposition_key(prior, _IDENT): {"disposition": "ok"}}
    current_identity = {**_IDENT, "matcher_digest": "new-matcher"}

    reconciled, unresolved, retired = A.reconcile_dispositions([prior, new], current_identity, old)

    assert list(reconciled) == [A.disposition_key(prior, current_identity)]
    assert unresolved == [new]
    assert retired == 0


def test_reconcile_ignores_malformed_old_key() -> None:
    current = _rec("rules/x.md", "kw", "foo", in_manifest=False)
    reconciled, unresolved, retired = A.reconcile_dispositions(
        [current], _IDENT, {"bad-key": {"disposition": "ok"}}
    )

    assert reconciled == {}
    assert unresolved == [current]
    assert retired == 1


# ── scope circuit breaker (AC23) ─────────────────────────────────────────────


def test_circuit_break_on_many_new_families() -> None:
    # 4 misses across 4 previously-unaffected families → break (> NEW_FAMILY_LIMIT=3).
    misses = [_rec(f"rules/{fam}-x.md", "kw", "v", False) for fam in ("500", "600", "700", "800")]
    broke, new_families = A.should_circuit_break(misses)
    assert broke
    assert new_families == {"500", "600", "700", "800"}


def test_no_break_within_known_affected_families() -> None:
    # Misses confined to the plan's known-affected families never break scope.
    misses = [_rec("rules/112-a.md", "kw", "v", False), _rec("rules/116-b.md", "kw", "v", False)]
    broke, new_families = A.should_circuit_break(misses)
    assert not broke
    assert new_families == set()


# ── real repo + CLI (positive control after Option 1 dispositioning) ─────────


def test_repo_audit_generates_current_artifact() -> None:
    result = runner.invoke(app, ["rule-loader", "audit"])
    assert result.exit_code == 0, result.output
    assert "corpus audit:" in result.output
    assert "zero unexplained" in result.output
