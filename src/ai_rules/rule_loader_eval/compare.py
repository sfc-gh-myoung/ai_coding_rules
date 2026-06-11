"""Compare two rule-loader snapshots and emit a delta report.

Used by ``ai-rules rule-loader compare <baseline> <post>`` to validate
that a rule-loading mechanism change (e.g. typed Keywords refinement
consolidation plan) preserves or improves rule-loading behaviour.

Comparisons are performed at the **outcome** level so they survive
schema migrations: prompt + expected.* fields are stable inputs; the
diffed outputs are pass/fail, loaded-set membership, signal/citation
drift counts, and timing.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal

from ai_rules.rule_loader_eval.snapshot import FixtureSnapshot, Snapshot

if TYPE_CHECKING:
    from ai_rules.rule_loader_eval.rules_meta import RuleMetadata

PassDelta = Literal["pass->pass", "fail->fail", "pass->fail", "fail->pass"]
"""Per-fixture pass/fail transition kind."""

# Exit codes matching the plan's documented contract:
# 0 = no regressions, 1 = regression(s), 2 = drift only.
EXIT_NO_CHANGE = 0
EXIT_REGRESSION = 1
EXIT_DRIFT_ONLY = 2


@dataclass(frozen=True)
class FixtureDelta:
    """Per-fixture diff between baseline and post snapshots."""

    fixture_id: str
    baseline: FixtureSnapshot
    post: FixtureSnapshot
    loaded_added: tuple[str, ...]
    loaded_removed: tuple[str, ...]
    pass_delta: PassDelta
    signal_disagreements_delta: int
    citation_drifts_delta: int
    turns_delta: int
    duration_ms_delta: int
    input_tokens_delta: int = 0
    output_tokens_delta: int = 0
    total_tokens_delta: int = 0
    total_cost_usd_delta: float = 0.0

    @property
    def has_load_drift(self) -> bool:
        """True when the loaded set changed in either direction."""
        return bool(self.loaded_added or self.loaded_removed)

    @property
    def is_regression(self) -> bool:
        """True iff a previously-passing fixture now fails.

        v3.15: infra-error post snapshots are NOT regressions — they're
        environment failures, not rule-loading failures.
        """
        if getattr(self.post, "is_infra_error", False):
            return False
        return self.pass_delta == "pass->fail"

    @property
    def is_infra(self) -> bool:
        """v3.15: True when the post snapshot is an infra error."""
        return bool(getattr(self.post, "is_infra_error", False))

    @property
    def is_improvement(self) -> bool:
        """True iff a previously-failing fixture now passes."""
        return self.pass_delta == "fail->pass"

    def is_flaky(self, threshold: float = 0.30) -> bool:
        """True when the post-snapshot flake_score exceeds the threshold."""
        return self.post.flake_score >= threshold


@dataclass(frozen=True)
class CompareReport:
    """Aggregate result of comparing two snapshots."""

    baseline_label: str
    post_label: str
    fixtures_only_in_baseline: tuple[str, ...]
    fixtures_only_in_post: tuple[str, ...]
    deltas: tuple[FixtureDelta, ...]
    # Aggregate metrics
    baseline_pass_rate: tuple[int, int]  # (passed, total)
    post_pass_rate: tuple[int, int]
    total_loaded_added: int
    total_loaded_removed: int
    total_signal_disagreements_delta: int
    total_citation_drifts_delta: int
    mean_turns_delta: float
    mean_duration_ms_delta: float
    mean_input_tokens_delta: float = 0.0
    mean_output_tokens_delta: float = 0.0
    mean_total_tokens_delta: float = 0.0
    mean_total_cost_usd_delta: float = 0.0
    regressions: tuple[FixtureDelta, ...] = field(default_factory=tuple)
    improvements: tuple[FixtureDelta, ...] = field(default_factory=tuple)
    drift_only: tuple[FixtureDelta, ...] = field(default_factory=tuple)
    flaky: tuple[FixtureDelta, ...] = field(default_factory=tuple)
    infra: tuple[FixtureDelta, ...] = field(default_factory=tuple)
    """v3.15: fixtures whose post snapshot is an infra error — reported separately, not gated."""
    flake_threshold: float = 0.50
    # Skill invocation counts (K/N fixtures invoked the rule-loader skill)
    baseline_skill_invocations: int = 0
    post_skill_invocations: int = 0

    @property
    def exit_code(self) -> int:
        """Plan-documented exit-code: 0 clean, 1 regression, 2 drift only."""
        if self.regressions:
            return EXIT_REGRESSION
        # "Clean" = no drift on shared fixtures AND no orphaned fixtures.
        if (
            not any(d.has_load_drift for d in self.deltas)
            and not self.fixtures_only_in_baseline
            and not self.fixtures_only_in_post
        ):
            return EXIT_NO_CHANGE
        return EXIT_DRIFT_ONLY

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict for the --format=json renderer."""
        return {
            "baseline_label": self.baseline_label,
            "post_label": self.post_label,
            "fixtures_only_in_baseline": list(self.fixtures_only_in_baseline),
            "fixtures_only_in_post": list(self.fixtures_only_in_post),
            "baseline_pass_rate": list(self.baseline_pass_rate),
            "post_pass_rate": list(self.post_pass_rate),
            "total_loaded_added": self.total_loaded_added,
            "total_loaded_removed": self.total_loaded_removed,
            "total_signal_disagreements_delta": self.total_signal_disagreements_delta,
            "total_citation_drifts_delta": self.total_citation_drifts_delta,
            "mean_turns_delta": self.mean_turns_delta,
            "mean_duration_ms_delta": self.mean_duration_ms_delta,
            "mean_input_tokens_delta": self.mean_input_tokens_delta,
            "mean_output_tokens_delta": self.mean_output_tokens_delta,
            "mean_total_tokens_delta": self.mean_total_tokens_delta,
            "mean_total_cost_usd_delta": self.mean_total_cost_usd_delta,
            "regressions": [_delta_to_dict(d) for d in self.regressions],
            "improvements": [_delta_to_dict(d) for d in self.improvements],
            "drift_only": [_delta_to_dict(d) for d in self.drift_only],
            "deltas": [_delta_to_dict(d) for d in self.deltas],
        }


def _delta_to_dict(d: FixtureDelta) -> dict:
    return {
        "fixture_id": d.fixture_id,
        "pass_delta": d.pass_delta,
        "loaded_added": list(d.loaded_added),
        "loaded_removed": list(d.loaded_removed),
        "signal_disagreements_delta": d.signal_disagreements_delta,
        "citation_drifts_delta": d.citation_drifts_delta,
        "turns_delta": d.turns_delta,
        "duration_ms_delta": d.duration_ms_delta,
        "input_tokens_delta": d.input_tokens_delta,
        "output_tokens_delta": d.output_tokens_delta,
        "total_tokens_delta": d.total_tokens_delta,
        "total_cost_usd_delta": d.total_cost_usd_delta,
        "baseline_passed": d.baseline.passed,
        "post_passed": d.post.passed,
    }


# ---------------------------------------------------------------------------
# Core compare
# ---------------------------------------------------------------------------


def compare_snapshots(
    baseline: Snapshot,
    post: Snapshot,
    *,
    alias_map: dict[str, str] | None = None,
    flake_threshold: float = 0.50,
    ignore_flaky: bool = False,
) -> CompareReport:
    """Compute the per-fixture and aggregate delta between two snapshots.

    Args:
        baseline: snapshot captured before the change.
        post: snapshot captured after the change.
        alias_map: optional ``{old_path: new_path}`` mapping for rules that
            were renamed or merged by the change. Applied to baseline.loaded
            entries before the set diff so cosmetic renames don't show as
            drift. The map should reflect the planned rule-rename moves.
        flake_threshold: jaccard-distance threshold above which a fixture is
            classified as flaky (0.0-1.0). Default 0.30.
        ignore_flaky: when True, flaky fixtures are excluded from the
            ``regressions`` bucket (moved to ``flaky`` instead).

    Returns:
        A :class:`CompareReport` aggregating per-fixture deltas. Use
        ``report.exit_code`` for the plan-documented exit semantics.
    """
    alias_map = alias_map or {}
    baseline_by_id = {f.fixture_id: f for f in baseline.fixtures}
    post_by_id = {f.fixture_id: f for f in post.fixtures}

    only_baseline = tuple(sorted(set(baseline_by_id) - set(post_by_id)))
    only_post = tuple(sorted(set(post_by_id) - set(baseline_by_id)))
    shared_ids = sorted(set(baseline_by_id) & set(post_by_id))

    deltas: list[FixtureDelta] = []
    for fid in shared_ids:
        deltas.append(_compute_delta(baseline_by_id[fid], post_by_id[fid], alias_map))

    flaky = tuple(d for d in deltas if d.is_flaky(flake_threshold))
    flaky_ids = {d.fixture_id for d in flaky}
    infra = tuple(d for d in deltas if d.is_infra)
    infra_ids = {d.fixture_id for d in infra}

    regressions = tuple(
        d
        for d in deltas
        if d.is_regression
        and not (ignore_flaky and d.fixture_id in flaky_ids)
        and d.fixture_id not in infra_ids
    )
    improvements = tuple(d for d in deltas if d.is_improvement)
    drift_only = tuple(
        d for d in deltas if d.has_load_drift and not d.is_regression and not d.is_improvement
    )

    baseline_pass = sum(1 for d in deltas if d.baseline.passed) + sum(
        1 for fid in only_baseline if baseline_by_id[fid].passed
    )
    baseline_total = len(deltas) + len(only_baseline)
    post_pass = sum(1 for d in deltas if d.post.passed) + sum(
        1 for fid in only_post if post_by_id[fid].passed
    )
    post_total = len(deltas) + len(only_post)

    total_added = sum(len(d.loaded_added) for d in deltas)
    total_removed = sum(len(d.loaded_removed) for d in deltas)
    total_sig = sum(d.signal_disagreements_delta for d in deltas)
    total_cit = sum(d.citation_drifts_delta for d in deltas)
    n = len(deltas) or 1
    mean_turns = round(sum(d.turns_delta for d in deltas) / n, 2)
    mean_dur = round(sum(d.duration_ms_delta for d in deltas) / n, 2)
    mean_input_tk = round(sum(d.input_tokens_delta for d in deltas) / n, 2)
    mean_output_tk = round(sum(d.output_tokens_delta for d in deltas) / n, 2)
    mean_total_tk = round(sum(d.total_tokens_delta for d in deltas) / n, 2)
    mean_cost = round(sum(d.total_cost_usd_delta for d in deltas) / n, 6)

    return CompareReport(
        baseline_label=baseline.meta.label or baseline.meta.git_commit or "baseline",
        post_label=post.meta.label or post.meta.git_commit or "post",
        fixtures_only_in_baseline=only_baseline,
        fixtures_only_in_post=only_post,
        deltas=tuple(deltas),
        baseline_pass_rate=(baseline_pass, baseline_total),
        post_pass_rate=(post_pass, post_total),
        total_loaded_added=total_added,
        total_loaded_removed=total_removed,
        total_signal_disagreements_delta=total_sig,
        total_citation_drifts_delta=total_cit,
        mean_turns_delta=mean_turns,
        mean_duration_ms_delta=mean_dur,
        mean_input_tokens_delta=mean_input_tk,
        mean_output_tokens_delta=mean_output_tk,
        mean_total_tokens_delta=mean_total_tk,
        mean_total_cost_usd_delta=mean_cost,
        regressions=regressions,
        improvements=improvements,
        drift_only=drift_only,
        flaky=flaky,
        infra=infra,
        flake_threshold=flake_threshold,
        baseline_skill_invocations=sum(
            1 for d in deltas if "rule-loader" in d.baseline.skill_invocations
        ),
        post_skill_invocations=sum(1 for d in deltas if "rule-loader" in d.post.skill_invocations),
    )


def _compute_delta(
    baseline: FixtureSnapshot,
    post: FixtureSnapshot,
    alias_map: dict[str, str],
) -> FixtureDelta:
    """Compute the per-fixture delta. Applies alias_map to baseline.loaded."""
    bs_loaded = {alias_map.get(r, r) for r in baseline.loaded}
    ps_loaded = set(post.loaded)
    added = tuple(sorted(ps_loaded - bs_loaded))
    removed = tuple(sorted(bs_loaded - ps_loaded))

    if baseline.passed and post.passed:
        pd: PassDelta = "pass->pass"
    elif baseline.passed and not post.passed:
        pd = "pass->fail"
    elif not baseline.passed and post.passed:
        pd = "fail->pass"
    else:
        pd = "fail->fail"

    return FixtureDelta(
        fixture_id=baseline.fixture_id,
        baseline=baseline,
        post=post,
        loaded_added=added,
        loaded_removed=removed,
        pass_delta=pd,
        signal_disagreements_delta=post.signal_disagreements - baseline.signal_disagreements,
        citation_drifts_delta=post.citation_drifts - baseline.citation_drifts,
        turns_delta=post.turns - baseline.turns,
        duration_ms_delta=post.duration_ms - baseline.duration_ms,
        input_tokens_delta=post.input_tokens - baseline.input_tokens,
        output_tokens_delta=post.output_tokens - baseline.output_tokens,
        total_tokens_delta=post.total_tokens - baseline.total_tokens,
        total_cost_usd_delta=post.total_cost_usd - baseline.total_cost_usd,
    )


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def render_table(report: CompareReport, *, verbose: bool = False) -> list[str]:
    """Render the report as a human-readable text table (Rich-friendly).

    Returns a list of lines (caller decides whether to print to stdout or
    pipe to a file). Plain text only — no Rich markup — so output is
    grep-friendly in CI.

    Args:
        report: the comparison report to render.
        verbose: when True, expand the drift-only section and include
            universal-churn rules inside per-fixture blocks. Default False
            collapses both to summary lines.
    """
    lines: list[str] = []
    bp_p, bp_t = report.baseline_pass_rate
    pp_p, pp_t = report.post_pass_rate
    delta = pp_p - bp_p

    # VERDICT — SKILL_NOT_INVOKED only fires when snapshot has invocation data
    n_total = len(report.deltas)
    has_invocation_data = any(d.post.skill_invocations for d in report.deltas)
    if has_invocation_data and report.post_skill_invocations < n_total:
        verdict = "SKILL_NOT_INVOKED"
    elif report.regressions:
        verdict = "REGRESSION"
    elif report.improvements:
        verdict = "IMPROVEMENT"
    elif report.drift_only or report.fixtures_only_in_baseline or report.fixtures_only_in_post:
        verdict = "DRIFT ONLY"
    else:
        verdict = "CLEAN"
    flaky_note = f"  [{len(report.flaky)} flaky excluded]" if report.flaky else ""
    lines.append(
        f"VERDICT: {verdict}  |  {bp_p}/{bp_t} -> {pp_p}/{pp_t}"
        + (f"  ({delta:+d})" if delta != 0 else "")
        + flaky_note
    )
    lines.append("")

    lines.append(f"baseline: {report.baseline_label}")
    lines.append(f"post:     {report.post_label}")
    lines.append("")
    lines.append(
        f"pass rate:  {bp_p}/{bp_t}  ->  {pp_p}/{pp_t}"
        + (f"  (+{delta})" if delta >= 0 else f"  ({delta})")
    )
    lines.append(
        f"loaded:     +{report.total_loaded_added} added, -{report.total_loaded_removed} removed"
    )
    lines.append(
        f"signal:     {report.total_signal_disagreements_delta:+d} disagreements; "
        f"citation:  {report.total_citation_drifts_delta:+d}"
    )
    lines.append(
        f"timing:     turns {report.mean_turns_delta:+.2f}; "
        f"duration {report.mean_duration_ms_delta:+.2f} ms (means)"
    )
    has_token_data = any(d.post.total_tokens for d in report.deltas)
    if has_token_data:
        lines.append(
            f"tokens:     input {report.mean_input_tokens_delta:+,.0f}; "
            f"output {report.mean_output_tokens_delta:+,.0f} (means)"
        )
    n_total = len(report.deltas)
    has_invocation_data = any(d.post.skill_invocations for d in report.deltas)
    if has_invocation_data:
        if report.post_skill_invocations < n_total or report.baseline_skill_invocations < n_total:
            lines.append(
                f"skill:      rule-loader invoked  "
                f"{report.baseline_skill_invocations}/{n_total}  ->  "
                f"{report.post_skill_invocations}/{n_total}"
                + ("  [SKILL_NOT_INVOKED]" if report.post_skill_invocations < n_total else "")
            )
        else:
            lines.append(
                f"skill:      rule-loader invoked  {report.post_skill_invocations}/{n_total}"
            )
    # Aggregate metric: depends propagation ok = fixtures with zero violations
    post_depends_ok = sum(1 for d in report.deltas if not d.post.depends_violations)
    if any(d.post.depends_violations for d in report.deltas):
        lines.append(
            f"depends:    propagation ok  {post_depends_ok}/{n_total}"
            + ("  [R8 VIOLATIONS]" if post_depends_ok < n_total else "")
        )

    churn = _detect_universal_churn(report)
    if churn:
        n_fx = len(report.deltas)
        qualifier = (
            "shown below because --verbose" if verbose else "suppressed from per-fixture blocks"
        )
        lines.append("")
        lines.append(
            f"note: {len(churn)} rule(s) removed from all {n_fx} fixtures"
            f" (universal churn — {qualifier}):"
        )
        for r in sorted(churn):
            lines.append(f"  {r}")

    if report.fixtures_only_in_baseline:
        lines.append("")
        lines.append("only in baseline:")
        for fid in report.fixtures_only_in_baseline:
            lines.append(f"  - {fid}")
    if report.fixtures_only_in_post:
        lines.append("")
        lines.append("only in post:")
        for fid in report.fixtures_only_in_post:
            lines.append(f"  + {fid}")

    if report.regressions:
        lines.append("")
        lines.append(f"REGRESSIONS ({len(report.regressions)}):")
        for d in report.regressions:
            lines.extend(_render_delta_block(d, indent="  ", churn=churn, verbose=verbose))
    if report.improvements:
        lines.append("")
        lines.append(f"improvements ({len(report.improvements)}):")
        for d in report.improvements:
            lines.extend(_render_delta_block(d, indent="  ", churn=churn, verbose=verbose))
    if report.drift_only:
        lines.append("")
        if verbose:
            lines.append(f"load-drift only ({len(report.drift_only)}):")
            for d in report.drift_only:
                lines.extend(_render_delta_block(d, indent="  ", churn=churn, verbose=verbose))
        else:
            lines.append(
                f"  ({len(report.drift_only)} fixtures with load drift only"
                f" — pass --verbose to expand)"
            )

    if report.flaky:
        lines.append("")
        lines.append(f"FLAKY ({len(report.flaky)})  [flake_score >= {report.flake_threshold}]:")
        for d in report.flaky:
            score = d.post.flake_score
            lines.append(f"  - {d.fixture_id}  [{d.pass_delta}]  flake_score={score:.2f}")

    if report.infra:
        lines.append("")
        lines.append(
            f"INFRA ({len(report.infra)})  [post snapshot was infra error — not a rule-loading regression]:"
        )
        for d in report.infra:
            detail = getattr(d.post, "infra_error_detail", "") or "(no detail)"
            lines.append(f"  - {d.fixture_id}: {detail}")

    if not (
        report.regressions
        or report.improvements
        or report.drift_only
        or report.flaky
        or report.infra
    ):
        lines.append("")
        lines.append("no per-fixture changes detected")
    return lines


def render_json(report: CompareReport) -> str:
    """Render the report as JSON (one object, pretty-printed)."""
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def render_markdown(report: CompareReport, *, verbose: bool = False) -> list[str]:
    """Render the report as a Markdown summary suitable for PR comments.

    Args:
        report: the comparison report to render.
        verbose: when True, expand the drift-only section and include
            universal-churn rules inside per-fixture blocks. Default False
            collapses both to summary lines.
    """
    lines: list[str] = []
    bp_p, bp_t = report.baseline_pass_rate
    pp_p, pp_t = report.post_pass_rate
    delta = pp_p - bp_p

    if report.regressions:
        verdict = "REGRESSION"
    elif report.improvements:
        verdict = "IMPROVEMENT"
    elif report.drift_only or report.fixtures_only_in_baseline or report.fixtures_only_in_post:
        verdict = "DRIFT ONLY"
    else:
        verdict = "CLEAN"

    lines.append(f"# Rule-loading A/B comparison: {report.baseline_label} → {report.post_label}")
    lines.append("")
    lines.append(f"**VERDICT: {verdict}** | {bp_p}/{bp_t} → {pp_p}/{pp_t} ({delta:+d})")
    lines.append("")
    lines.append("| metric | baseline | post | delta |")
    lines.append("|---|---|---|---|")
    lines.append(f"| pass rate | {bp_p}/{bp_t} | {pp_p}/{pp_t} | {delta:+d} |")
    lines.append(
        f"| loaded rules added/removed | — | — | "
        f"+{report.total_loaded_added} / -{report.total_loaded_removed} |"
    )
    lines.append(f"| signal disagreements | — | — | {report.total_signal_disagreements_delta:+d} |")
    lines.append(f"| citation drifts | — | — | {report.total_citation_drifts_delta:+d} |")
    lines.append(f"| mean turns | — | — | {report.mean_turns_delta:+.2f} |")
    lines.append(f"| mean duration ms | — | — | {report.mean_duration_ms_delta:+.2f} |")

    churn = _detect_universal_churn(report)
    if churn:
        n_fx = len(report.deltas)
        qualifier = (
            "shown below because --verbose" if verbose else "suppressed from per-fixture blocks"
        )
        lines.append("")
        lines.append(
            f"> **note:** {len(churn)} rule(s) removed from all {n_fx} fixtures"
            f" (universal churn — {qualifier}):"
            f" {', '.join(f'`{r}`' for r in sorted(churn))}"
        )

    if report.regressions:
        lines.append("")
        lines.append(f"## Regressions ({len(report.regressions)})")
        for d in report.regressions:
            lines.extend(_md_delta_block(d, churn=churn, verbose=verbose))
    if report.improvements:
        lines.append("")
        lines.append(f"## Improvements ({len(report.improvements)})")
        for d in report.improvements:
            lines.extend(_md_delta_block(d, churn=churn, verbose=verbose))
    if report.drift_only:
        lines.append("")
        if verbose:
            lines.append(f"## Load-drift only ({len(report.drift_only)})")
            for d in report.drift_only:
                lines.extend(_md_delta_block(d, churn=churn, verbose=verbose))
        else:
            lines.append(
                f"_{len(report.drift_only)} fixtures with load drift only"
                f" — pass --verbose to expand_"
            )
    if not (report.regressions or report.improvements or report.drift_only):
        lines.append("")
        lines.append("_no per-fixture changes detected_")
    return lines


def _render_delta_block(
    d: FixtureDelta,
    *,
    indent: str = "",
    churn: frozenset[str] | None = None,
    verbose: bool = False,
    rules_meta: dict[str, RuleMetadata] | None = None,
    fixture_prompt: str = "",
) -> list[str]:
    churn = churn or frozenset()
    lines = [f"{indent}- {d.fixture_id}  [{d.pass_delta}]"]
    for rule in d.loaded_added:
        tag = _classify_added(rule, d.post)
        lines.append(f"{indent}    +loaded: {rule}{(' ' + tag) if tag else ''}")
        if tag == "[spurious]" and rules_meta:
            firing, _ = _kw_evidence_for_rule(rule, fixture_prompt, rules_meta)
            if firing:
                lines.append(f"{indent}        fired-on: {', '.join(f'kw:{k}' for k in firing)}")
    for rule in d.loaded_removed:
        if rule in churn and not verbose:
            continue
        tag = _classify_removed(rule, d.post, is_universal_churn=(rule in churn))
        lines.append(f"{indent}    -loaded: {rule}{(' ' + tag) if tag else ''}")
        if tag == "[missing-required]" and rules_meta:
            _, all_kw = _kw_evidence_for_rule(rule, fixture_prompt, rules_meta)
            firing, _ = _kw_evidence_for_rule(rule, fixture_prompt, rules_meta)
            if all_kw:
                lines.append(
                    f"{indent}        current-kw: {', '.join(f'kw:{k}' for k in all_kw[:5])}"
                )
            if not firing:
                lines.append(
                    f"{indent}        (no kw: matched prompt — check kw: metadata in {rule})"
                )
    detail = []
    if d.signal_disagreements_delta:
        detail.append(f"signal {d.signal_disagreements_delta:+d}")
    if d.citation_drifts_delta:
        detail.append(f"citation {d.citation_drifts_delta:+d}")
    if d.turns_delta:
        detail.append(f"turns {d.turns_delta:+d}")
    if d.duration_ms_delta:
        detail.append(f"duration {d.duration_ms_delta:+d}ms")
    if detail:
        lines.append(f"{indent}    {'; '.join(detail)}")
    if d.is_regression:
        for rule in d.loaded_removed:
            if rule in churn:
                continue
            tag = _classify_removed(rule, d.post)
            if "[missing-required]" in tag:
                lines.append(
                    f"{indent}    → fix: add kw: trigger to {rule}  (was missing-required)"
                )
            elif "[missing-dep]" in tag:
                lines.append(f"{indent}    → fix: add kw: trigger to {rule}  (was missing-dep)")
        for rule in d.loaded_added:
            if "[spurious]" in _classify_added(rule, d.post):
                lines.append(f"{indent}    → fix: narrow kw: triggers in {rule}  (was spurious)")
        for violation in d.post.depends_violations:
            lines.append(f"{indent}    → fix: R8 violation — {violation}")
    return lines


def _md_delta_block(
    d: FixtureDelta,
    *,
    churn: frozenset[str] | None = None,
    verbose: bool = False,
) -> list[str]:
    churn = churn or frozenset()
    lines = [f"- **{d.fixture_id}** — `{d.pass_delta}`"]
    for rule in d.loaded_added:
        tag = _classify_added(rule, d.post)
        lines.append(f"  - +loaded: `{rule}`{(' ' + tag) if tag else ''}")
    for rule in d.loaded_removed:
        if rule in churn and not verbose:
            continue
        tag = _classify_removed(rule, d.post, is_universal_churn=(rule in churn))
        lines.append(f"  - -loaded: `{rule}`{(' ' + tag) if tag else ''}")
    detail = []
    if d.signal_disagreements_delta:
        detail.append(f"signal {d.signal_disagreements_delta:+d}")
    if d.citation_drifts_delta:
        detail.append(f"citation {d.citation_drifts_delta:+d}")
    if d.turns_delta:
        detail.append(f"turns {d.turns_delta:+d}")
    if d.duration_ms_delta:
        detail.append(f"duration {d.duration_ms_delta:+d}ms")
    if detail:
        lines.append(f"  - {'; '.join(detail)}")
    if d.is_regression:
        for rule in d.loaded_removed:
            if rule in churn:
                continue
            tag = _classify_removed(rule, d.post)
            if "[missing-required]" in tag:
                lines.append(f"  - → fix: add kw: trigger to `{rule}`  (was missing-required)")
            elif "[missing-dep]" in tag:
                lines.append(f"  - → fix: add kw: trigger to `{rule}`  (was missing-dep)")
        for rule in d.loaded_added:
            if "[spurious]" in _classify_added(rule, d.post):
                lines.append(f"  - → fix: narrow kw: triggers in `{rule}`  (was spurious)")
    return lines


def _detect_universal_churn(
    report: CompareReport,
    *,
    threshold: float = 0.80,
) -> frozenset[str]:
    """Return rules removed from >= threshold fraction of all fixtures."""
    if not report.deltas:
        return frozenset()
    n = len(report.deltas)
    removal_counts: dict[str, int] = {}
    for d in report.deltas:
        for rule in d.loaded_removed:
            removal_counts[rule] = removal_counts.get(rule, 0) + 1
    cutoff = n * threshold
    return frozenset(rule for rule, count in removal_counts.items() if count >= cutoff)


def _kw_evidence_for_rule(
    rule_path: str,
    prompt: str,
    rules_meta: dict[str, RuleMetadata] | None,
) -> tuple[list[str], list[str]]:
    """Return (firing_kw, all_kw) for a rule given the fixture prompt.

    ``firing_kw`` = kw: entries whose tokens all appear in the lowercased prompt.
    ``all_kw`` = all typed_kw entries in the rule.
    Returns ([], []) when rules_meta is None or rule not found.
    """
    if rules_meta is None:
        return [], []
    meta = rules_meta.get(rule_path)
    if meta is None:
        return [], []
    prompt_lower = prompt.lower()
    firing = [kw for kw in meta.typed_kw if all(t in prompt_lower for t in kw.split())]
    return firing, list(meta.typed_kw)


def _classify_removed(
    rule: str,
    post: FixtureSnapshot,
    *,
    is_universal_churn: bool = False,
) -> str:
    """Return a bracket tag for a -loaded rule."""
    if is_universal_churn:
        return "[expected-deletion]"
    if rule in post.missing_required:
        return "[missing-required]"
    if rule in post.missing_dependencies:
        return "[missing-dep]"
    return ""


def _classify_added(rule: str, post: FixtureSnapshot) -> str:
    """Return a bracket tag for a +loaded rule."""
    expected = (
        set(post.expected_required) | set(post.expected_dependencies) | set(post.expected_optional)
    )
    if rule not in expected:
        return "[spurious]"
    return ""


def parse_alias_map(path) -> dict[str, str]:
    """Parse ``{old_rule: new_rule}`` map from a JSON file. Empty dict for None."""
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("alias-map JSON must be an object {old: new}")
    out: dict[str, str] = {}
    for k, v in data.items():
        if not isinstance(k, str) or not isinstance(v, str):
            raise ValueError(f"alias-map entries must be strings, got {k!r}: {v!r}")
        out[k] = v
    return out


def iter_lines(value: Iterable[str]) -> str:
    """Helper for tests / programmatic callers: join an iterable of lines."""
    return "\n".join(value) + "\n"


# ---------------------------------------------------------------------------
# Multi-run merge (noise-resistant baseline construction)
# ---------------------------------------------------------------------------

import statistics  # noqa: E402
from datetime import datetime  # noqa: E402

from ai_rules.rule_loader_eval.snapshot import (  # noqa: E402
    SNAPSHOT_SCHEMA_VERSION,
    SnapshotMeta,
    compute_summary,
)


def merge_snapshots(snapshots: list[Snapshot], *, label: str = "merged") -> Snapshot:
    """Aggregate N snapshots into a single noise-resistant synthetic snapshot.

    Policy (confirmed by plan Q1-Q4 answers):

    - **Pass status (Q1: majority pass)**: a fixture is `passed=True` in the
      merged snapshot when it passed in strictly more than half of the runs
      that contained it. Tolerates occasional flake while catching
      reproducible failures.
    - **Loaded set (Q2: majority)**: a rule appears in the merged
      ``loaded`` tuple when it appeared in strictly more than half of the
      runs that contained the fixture. Filters one-off speculative loads
      while keeping the stable core.
    - **Missing fixtures (Q3: fill from available runs)**: a fixture present
      in some runs but not others is included, with majority computed over
      only the runs that contained it. Coverage stays high; runs without
      the fixture neither contribute nor veto.
    - **Numeric metrics (Q4: median)**: ``turns``, ``duration_ms``,
      ``signal_disagreements``, ``citation_drifts`` are aggregated by
      median across the runs that contained each fixture. Robust to a
      single slow run dominating the mean.

    The merged ``expected_*`` fields are taken from the first run that
    contained the fixture (they are stable across runs by construction —
    they come from the fixture YAML, not the agent). The merged
    ``model`` and ``stop_reason`` are taken from the first run as well.

    Args:
        snapshots: list of Snapshots to merge (typically 3-5 baseline runs).
        label: label embedded into the merged ``SnapshotMeta``.

    Returns:
        A synthetic Snapshot whose meta records ``label`` and the source
        commit/branch/captured_at of the first input run, plus a
        ``notes`` field listing the source labels.

    Raises:
        ValueError: if ``snapshots`` is empty or every snapshot is empty.
    """
    if not snapshots:
        raise ValueError("merge_snapshots: at least one snapshot is required")

    # Group per-fixture rows across runs, keyed by fixture_id.
    per_fixture: dict[str, list[FixtureSnapshot]] = {}
    for snap in snapshots:
        for fx in snap.fixtures:
            per_fixture.setdefault(fx.fixture_id, []).append(fx)

    if not per_fixture:
        raise ValueError("merge_snapshots: no fixtures found across input snapshots")

    merged_rows: list[FixtureSnapshot] = []
    for fixture_id in sorted(per_fixture):
        merged_rows.append(_merge_fixture_rows(fixture_id, per_fixture[fixture_id]))

    first_meta = snapshots[0].meta
    source_labels = [s.meta.label or s.meta.git_commit or "?" for s in snapshots]
    merged_meta = SnapshotMeta(
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        captured_at=datetime.now().astimezone().replace(microsecond=0).isoformat(),
        git_commit=first_meta.git_commit,
        git_branch=first_meta.git_branch,
        model=first_meta.model,
        max_turns=first_meta.max_turns,
        effort=first_meta.effort,
        fixtures_dir=first_meta.fixtures_dir,
        rules_dir=first_meta.rules_dir,
        label=label,
        notes=(
            f"merged from {len(snapshots)} run(s): "
            + ", ".join(source_labels)
            + "; pass=majority, loaded=majority, fill_missing=true, numerics=median"
        ),
    )

    return Snapshot(
        meta=merged_meta,
        fixtures=tuple(merged_rows),
        summary=compute_summary(merged_rows),
    )


def _merge_fixture_rows(fixture_id: str, rows: list[FixtureSnapshot]) -> FixtureSnapshot:
    """Apply per-fixture majority/median aggregation across N rows."""
    n = len(rows)
    threshold = n // 2 + 1  # strict-majority threshold

    # Q1: majority pass
    passed_count = sum(1 for r in rows if r.passed)
    merged_passed = passed_count >= threshold

    # Q2: majority loaded
    rule_counts: dict[str, int] = {}
    for r in rows:
        for rule in r.loaded:
            rule_counts[rule] = rule_counts.get(rule, 0) + 1
    merged_loaded = tuple(sorted(rule for rule, count in rule_counts.items() if count >= threshold))

    # Same majority rule applied to forbidden_present / missing_required /
    # missing_dependencies so a one-off agent slip doesn't poison the merged
    # row. expected_* fields come from the fixture YAML (deterministic) so we
    # take the first occurrence.
    def _majority_set(field: str) -> tuple[str, ...]:
        counts: dict[str, int] = {}
        for r in rows:
            for v in getattr(r, field):
                counts[v] = counts.get(v, 0) + 1
        return tuple(sorted(v for v, c in counts.items() if c >= threshold))

    # Q4: median numerics
    def _median_int(field: str) -> int:
        return int(statistics.median(getattr(r, field) for r in rows))

    def _median_float(field: str) -> float:
        return float(statistics.median(getattr(r, field) for r in rows))

    # Signal-investigation fields: reads/section follow same strict-majority
    # policy as ``loaded``; disagreement_details are unioned across runs so
    # any disagreement in any run remains visible for post-hoc inspection.
    def _majority_signal(field: str) -> tuple[str, ...]:
        counts: dict[str, int] = {}
        for r in rows:
            for v in getattr(r, field):
                counts[v] = counts.get(v, 0) + 1
        return tuple(sorted(v for v, c in counts.items() if c >= threshold))

    def _union_strings(field: str) -> tuple[str, ...]:
        seen: set[str] = set()
        for r in rows:
            seen.update(getattr(r, field))
        return tuple(sorted(seen))

    return FixtureSnapshot(
        fixture_id=fixture_id,
        passed=merged_passed,
        loaded=merged_loaded,
        expected_required=rows[0].expected_required,
        expected_dependencies=rows[0].expected_dependencies,
        expected_optional=rows[0].expected_optional,
        expected_forbidden=rows[0].expected_forbidden,
        missing_required=_majority_set("missing_required"),
        missing_dependencies=_majority_set("missing_dependencies"),
        forbidden_present=_majority_set("forbidden_present"),
        signal_disagreements=_median_int("signal_disagreements"),
        citation_drifts=_median_int("citation_drifts"),
        turns=_median_int("turns"),
        duration_ms=_median_int("duration_ms"),
        model=rows[0].model,
        stop_reason=rows[0].stop_reason,
        loaded_via_reads=_majority_signal("loaded_via_reads"),
        loaded_via_section=_majority_signal("loaded_via_section"),
        disagreement_details=_union_strings("disagreement_details"),
        flake_score=_compute_flake_score(rows),
        n_runs=n,
        # NOTE: token/cost fields must be listed explicitly here — FixtureSnapshot
        # uses dataclass defaults for fields omitted from this return, which silently
        # zeroes them after any merge. Add new FixtureSnapshot fields here too.
        input_tokens=_median_int("input_tokens"),
        output_tokens=_median_int("output_tokens"),
        total_tokens=_median_int("total_tokens"),
        total_cost_usd=_median_float("total_cost_usd"),
    )


def _compute_flake_score(rows: list[FixtureSnapshot]) -> float:
    """Return 1 - jaccard(intersection, union) of loaded sets across rows."""
    if len(rows) <= 1:
        return 0.0
    sets = [set(r.loaded) for r in rows]
    union: set[str] = set().union(*sets)
    if not union:
        return 0.0
    intersection = sets[0].copy()
    for s in sets[1:]:
        intersection &= s
    return round(1.0 - len(intersection) / len(union), 4)


def render_merge_summary(merged: Snapshot, n_inputs: int) -> list[str]:
    """Render a one-paragraph summary of the merge result for CLI output."""
    s = merged.summary
    if s is None:
        return [f"merged {n_inputs} run(s) -> 0 fixtures"]
    lines = [
        f"merged {n_inputs} run(s) -> {s.total} fixture(s)",
        f"  pass:    {s.passed}/{s.total}",
        f"  median turns:    {s.mean_turns}  (across merged rows)",
        f"  median duration: {s.mean_duration_ms} ms  (across merged rows)",
        f"  signal disagreements: {s.total_signal_disagreements}",
        f"  citation drifts:      {s.total_citation_drifts}",
    ]
    if s.mean_input_tokens:
        lines.append(f"  median input tokens:  {s.mean_input_tokens:.0f}")
        lines.append(f"  median output tokens: {s.mean_output_tokens:.0f}")
    return lines
