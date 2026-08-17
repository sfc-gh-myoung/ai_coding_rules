"""Engine: iterate fixtures and drive the live agent.

No baselines. No history. No transcripts. Live SDK only. The matcher
checks the agent's loaded set against the union of required and
dependencies. The diagnostics module enforces 3-signal agreement and
citation-drift checks unconditionally: pass/fail per fixture is the
combination of all three.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from ai_rules.rule_loader_eval.agent_runner import AgentRun, run_live, run_live_async
from ai_rules.rule_loader_eval.defaults import DEFAULT_EFFORT, DEFAULT_MAX_TURNS
from ai_rules.rule_loader_eval.depends_validator import (
    DependsViolation,
    expand_required_closure,
    validate_depends_propagation,
)
from ai_rules.rule_loader_eval.diagnostics import (
    CitationDrift,
    SignalReport,
    signal_disagreement,
    version_citation_drift,
)
from ai_rules.rule_loader_eval.fixtures import Fixture
from ai_rules.rule_loader_eval.matcher import (
    MatchResult,
    match_loaded_rules,
)
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata, load_rules_metadata

_FOUNDATION_RULE = "rules/000-global-core.md"

_GATE3_VIOLATION = "missing Rules Loaded (Gate 3 or **Rules Loaded**) section"


def _is_missing_gate3_violation(violations: Iterable[str]) -> bool:
    """Return True iff violations contains the exact Gate 3 missing-section string."""
    return _GATE3_VIOLATION in violations


@dataclass(frozen=True)
class RunResult:
    """Engine output for one fixture.

    A fixture passes iff:
    - ``match.passed`` is True (required + dependencies all loaded), AND
    - ``signal_report.ok`` is True (3-signal agreement holds), AND
    - ``citation_drifts`` is empty (no line-count fabrication), AND
    - ``run.output_violations`` is empty (bootstrap/no-match output shape is valid).

    R8 depends-propagation is reported via ``depends_ok`` / ``depends_violations``
    but does NOT gate pass/fail (Phase 1 decouple).
    ``effective_loaded`` is the closure-expanded loaded set used for scoring (Phase 2).

    All checks are unconditional. There are no escape flags.
    """

    fixture_id: str
    run: AgentRun
    match: MatchResult
    signal_report: SignalReport
    citation_drifts: tuple[CitationDrift, ...] = field(default_factory=tuple)
    depends_violations: tuple[DependsViolation, ...] = field(default_factory=tuple)
    """R8 violations: rules in loaded set whose required: deps are absent."""
    effective_loaded: tuple[str, ...] = field(default_factory=tuple)
    """Loaded set after required-closure expansion (Phase 2)."""
    required: tuple[str, ...] = field(default_factory=tuple)
    """Foundation-filtered required rules, for Phase 6 manifest-recall attribution."""
    scoring_version: str = "v2"
    """Accounting version for FM-6 extras. v1 = pre-Option-A; v2 = dep-closure subtracted from extras."""
    mode: str = "plugin"
    """Eval mode: 'plugin' (normal) or 'without-plugin' (prompt-only discovery)."""
    max_turns_used: int = 0
    """Turn budget active during this run (0 = not recorded, safe default for legacy rows)."""

    # ── Phase 6: manifest-recall vs agent-compliance attribution ─────────────
    # These gates separate deterministic matcher recall from agent read/cite
    # compliance so a matcher regression is never masked by out-of-manifest
    # model recovery (RC6). The manifest gates apply only when the injected
    # manifest was captured (real runs); legacy/unit rows without
    # ``run.manifest_paths`` fall back to the pre-Phase-6 gate conjunction.

    @property
    def _manifest_set(self) -> frozenset[str]:
        mp = getattr(self.run, "manifest_paths", None) or frozenset()
        return frozenset(p for p in mp if p != _FOUNDATION_RULE)

    @property
    def _loaded_set(self) -> frozenset[str]:
        base = self.effective_loaded or getattr(self.run, "loaded", ()) or ()
        return frozenset(p for p in base if p != _FOUNDATION_RULE)

    @property
    def _required_set(self) -> frozenset[str]:
        return frozenset(r for r in self.required if r != _FOUNDATION_RULE)

    @property
    def manifest_available(self) -> bool:
        """True when the injected manifest was captured (real run, not a legacy/unit row)."""
        return bool(getattr(self.run, "manifest_paths", None))

    @property
    def manifest_empty(self) -> bool:
        """True when the injected manifest held no non-foundation rules."""
        return len(self._manifest_set) == 0

    @property
    def manifest_recall(self) -> bool:
        """Every required rule is present in the injected deterministic manifest."""
        return self._required_set <= self._manifest_set

    @property
    def agent_compliance(self) -> bool:
        """The agent loaded every required rule that the manifest offered."""
        return (self._required_set & self._manifest_set) <= self._loaded_set

    @property
    def out_of_manifest_recovery(self) -> dict[str, object]:
        """Required rules the agent found outside the manifest (never credited as a pass)."""
        rules = sorted((self._required_set & self._loaded_set) - self._manifest_set)
        return {"count": len(rules), "rules": rules}

    @property
    def _legacy_gates(self) -> bool:
        """Pre-Phase-6 conjunction: match + signal + citation + output-shape."""
        return (
            self.match.passed
            and self.signal_report.ok
            and not self.citation_drifts
            and not self.run.output_violations
        )

    @property
    def passed(self) -> bool:
        """Composite pass/fail.

        Six co-equal gates when the manifest was captured: match, signal,
        citation, output-shape (the legacy four) plus manifest-recall and
        agent-compliance. Legacy/unit rows without a captured manifest use the
        pre-Phase-6 four-gate conjunction. R8 depends-propagation is reported
        separately via :attr:`depends_ok` and does NOT gate pass/fail.
        """
        if not self.manifest_available:
            return self._legacy_gates
        return self._legacy_gates and self.manifest_recall and self.agent_compliance

    @property
    def result(self) -> str:
        """Total result classification with fixed precedence (Section 6 truth table).

        Legacy/unit rows (no captured manifest) collapse to ``pass``/``fail``
        for backward compatibility; the ``legacy`` string itself is a
        reader-side classification produced when loading pre-Phase-6 records.
        """
        if getattr(self.run, "is_infra_error", False):
            return "error"
        # Discovery budget exhaustion (without-plugin only, Gate 3 missing)
        if (
            self.mode == "without-plugin"
            and self.max_turns_used > 0
            and self.run.turns >= self.max_turns_used
            and _is_missing_gate3_violation(self.run.output_violations)
        ):
            return "discovery-budget-exhausted"
        if not self.manifest_available:
            return "pass" if self._legacy_gates else "fail"
        if self._required_set and self.manifest_empty:
            return "empty-manifest"
        if not self.manifest_recall:
            recovery = self.out_of_manifest_recovery["count"]
            return "recovery-only" if recovery else "matcher-miss"
        if not self.agent_compliance:
            return "agent-miss"
        if not self._legacy_gates:
            return "signal-violation"
        return "pass"

    @property
    def depends_ok(self) -> bool:
        """True when no R8 depends-propagation violations are present.

        Reported alongside :attr:`passed` but does not affect it.
        A fixture can pass while ``depends_ok=False`` when the agent loaded the
        correct primary rule but skipped a ``required:`` parent.
        """
        return not self.depends_violations


def _build_run_result(
    fixture: Fixture,
    run: AgentRun,
    rules_meta: dict[str, RuleMetadata],
    *,
    strict_forbidden: bool,
    mode: str = "plugin",
    max_turns_used: int = 0,
) -> RunResult:
    """Match a completed ``AgentRun`` against a fixture and build a ``RunResult``.

    Shared by the sync (:func:`run_fixture`) and async
    (:func:`run_fixture_async`) paths so their diagnostics are identical.

    Raises:
        InfraError: When ``run`` is flagged as an infra error.
    """
    if getattr(run, "is_infra_error", False):
        raise InfraError(run.infra_error_detail or "agent SDK reported infra error")

    # Phase 2: expand the loaded set via required: closure before scoring.
    # Forbidden is always checked on the RAW loaded set to prevent closure
    # from masking a rule the agent should not have loaded.
    effective_loaded = expand_required_closure(run.loaded, rules_meta)

    # The micro-kernel replaces 000-global-core.md, so models correctly skip
    # reading it. Filter it from the required set before scoring.
    effective_required = tuple(r for r in fixture.required if r != _FOUNDATION_RULE)

    # Score forbidden on raw, everything else on closure-expanded set.
    # match_full: pass rules_meta so dep-closure is subtracted from extras (Option A).
    match_full = match_loaded_rules(
        loaded=effective_loaded,
        required=effective_required,
        dependencies=fixture.dependencies,
        forbidden=fixture.forbidden,
        optional=fixture.optional,
        strict_forbidden=strict_forbidden,
        rules_meta=rules_meta,
    )
    if match_full.forbidden_present:
        # Re-score forbidden using only raw loaded so closure can't introduce
        # false-positive forbidden hits.
        # match_forbidden_raw: rules_meta passed for signature consistency;
        # closure subtraction does not affect the forbidden_present field since
        # forbidden is checked against loaded_set directly (not extras).
        match_forbidden_raw = match_loaded_rules(
            loaded=run.loaded,
            required=effective_required,
            dependencies=fixture.dependencies,
            forbidden=fixture.forbidden,
            optional=fixture.optional,
            strict_forbidden=strict_forbidden,
            rules_meta=rules_meta,
        )
        match = MatchResult(
            missing_required=match_full.missing_required,
            missing_dependencies=match_full.missing_dependencies,
            forbidden_present=match_forbidden_raw.forbidden_present,
            optional_loaded=match_full.optional_loaded,
            unloaded_optional=match_full.unloaded_optional,
            extras=match_full.extras,
            passed=match_full.missing_required == ()
            and match_full.missing_dependencies == ()
            and match_forbidden_raw.forbidden_present == (),
            warnings=match_full.warnings,
        )
    else:
        match = match_full

    return RunResult(
        fixture_id=fixture.id,
        run=run,
        match=match,
        signal_report=signal_disagreement(run, fixture_optional=fixture.optional),
        citation_drifts=(version_citation_drift(run, rules_meta)),
        depends_violations=tuple(validate_depends_propagation(effective_loaded, rules_meta)),
        effective_loaded=effective_loaded,
        required=effective_required,
        scoring_version="v2",
        mode=mode,
        max_turns_used=max_turns_used,
    )


def run_fixture(
    fixture: Fixture,
    *,
    project_root: Path,
    rules_meta: dict[str, RuleMetadata] | None = None,
    strict_forbidden: bool = False,
    max_turns: int = DEFAULT_MAX_TURNS,
    effort: str = DEFAULT_EFFORT,
    model: str = "auto",
    connection: str | None = None,
    manifest_paths: frozenset[str] | None = None,
    mode: str = "plugin",
) -> RunResult:
    """Run a single fixture against the live agent and match results."""
    if rules_meta is None:
        rules_meta = load_rules_metadata(project_root / "rules")
    run = run_live(
        fixture.id,
        fixture.prompt,
        project_root=project_root,
        max_turns=max_turns,
        effort=effort,
        model=model,
        connection=connection,
        manifest_paths=manifest_paths,
    )
    return _build_run_result(
        fixture,
        run,
        rules_meta,
        strict_forbidden=strict_forbidden,
        mode=mode,
        max_turns_used=max_turns,
    )


async def run_fixture_async(
    fixture: Fixture,
    *,
    project_root: Path,
    rules_meta: dict[str, RuleMetadata] | None = None,
    strict_forbidden: bool = False,
    max_turns: int = DEFAULT_MAX_TURNS,
    effort: str = DEFAULT_EFFORT,
    model: str = "auto",
    connection: str | None = None,
    system_prompt: str | None = None,
    manifest_paths: frozenset[str] | None = None,
    mode: str = "plugin",
) -> RunResult:
    """Async twin of :func:`run_fixture`.

    Awaits ``run_live_async`` instead of the sync ``run_live`` so many fixtures
    can share one event loop under the concurrent driver, then applies the SAME
    matching/diagnostics block as the sync path via :func:`_build_run_result`.
    Raises :class:`InfraError` on an infra-flagged run (before any match exists).
    """
    if rules_meta is None:
        rules_meta = load_rules_metadata(project_root / "rules")
    run = await run_live_async(
        fixture.id,
        fixture.prompt,
        project_root=project_root,
        max_turns=max_turns,
        effort=effort,
        model=model,
        connection=connection,
        system_prompt=system_prompt,
        manifest_paths=manifest_paths,
    )
    return _build_run_result(
        fixture,
        run,
        rules_meta,
        strict_forbidden=strict_forbidden,
        mode=mode,
        max_turns_used=max_turns,
    )


class InfraError(RuntimeError):
    """Raised when the agent SDK / model / connection is unavailable.

    Caught by ``run_fixtures`` to fail-fast: when one fixture reports an
    infra error, remaining fixtures are NOT run and the caller exits with
    EXIT_INFRA_ERROR (3).
    """


def _synthetic_failure(fixture: Fixture, exc: BaseException, *, infra: bool = False) -> RunResult:
    """Build a synthetic FAIL row when a fixture raises.

    When ``infra=True``, the row is marked as INFRA ERROR (notes prefix and
    ``run.is_infra_error=True``) so downstream rendering and snapshot
    serialization can distinguish it from a regular fixture failure.

    ``missing_required`` is reported with ``_FOUNDATION_RULE`` filtered out, the
    same way :func:`_build_run_result` does it. Without the filter a synthetic
    row is distinguishable from a normally-scored one by the presence of the
    foundation rule, which previously made these rows look like genuine
    discovery failures that had somehow missed the micro-kernel.
    """
    note_prefix = "INFRA ERROR" if infra else "runtime error"
    run = AgentRun(
        fixture_id=fixture.id,
        loaded=(),
        loaded_via_reads=(),
        loaded_via_reads_performed=(),
        loaded_via_section=(),
        disagreements=(),
        turns=0,
        duration_ms=0,
        model="error",
        notes=(f"{note_prefix}: {type(exc).__name__}: {exc}",),
        is_infra_error=infra,
        infra_error_detail=str(exc) if infra else "",
    )
    match = MatchResult(
        missing_required=tuple(r for r in fixture.required if r != _FOUNDATION_RULE),
        missing_dependencies=tuple(fixture.dependencies),
        forbidden_present=(),
        optional_loaded=(),
        extras=(),
        passed=False,
        warnings=(f"fixture raised {type(exc).__name__}: {exc}",),
    )
    return RunResult(
        fixture_id=fixture.id,
        run=run,
        match=match,
        signal_report=SignalReport(ok=False, disagreements=()),
        citation_drifts=(),
    )


def run_fixtures(
    fixtures: Iterable[Fixture],
    *,
    project_root: Path,
    strict_forbidden: bool = False,
    max_turns: int = DEFAULT_MAX_TURNS,
    effort: str = DEFAULT_EFFORT,
    model: str = "auto",
    connection: str | None = None,
) -> list[RunResult]:
    """Run a sequence of fixtures and return per-fixture results.

    A single fixture's runtime error is captured as a synthetic FAIL row
    so the rest of the run continues.
    """
    rules_meta = load_rules_metadata(project_root / "rules")
    out: list[RunResult] = []
    for f in fixtures:
        try:
            out.append(
                run_fixture(
                    f,
                    project_root=project_root,
                    rules_meta=rules_meta,
                    strict_forbidden=strict_forbidden,
                    max_turns=max_turns,
                    effort=effort,
                    model=model,
                    connection=connection,
                )
            )
        except InfraError as exc:
            # Fail-fast: record this fixture as INFRA failure and abort the rest.
            out.append(_synthetic_failure(f, exc, infra=True))
            break
        except Exception as exc:
            out.append(_synthetic_failure(f, exc))
    return out
