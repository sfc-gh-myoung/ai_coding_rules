"""Engine: iterate fixtures and drive the live agent.

No baselines. No history. No transcripts. Live SDK only. The matcher
checks the agent's loaded set against the union of required and
dependencies. The diagnostics module enforces 3-signal agreement and
citation-drift checks unconditionally — pass/fail per fixture is the
combination of all three.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from ai_rules.rule_loader_eval.agent_runner import AgentRun, run_live
from ai_rules.rule_loader_eval.defaults import DEFAULT_EFFORT, DEFAULT_MAX_TURNS
from ai_rules.rule_loader_eval.depends_validator import (
    DependsViolation,
    validate_depends_propagation,
)
from ai_rules.rule_loader_eval.diagnostics import (
    SignalReport,
    citation_drift,
    signal_disagreement,
)
from ai_rules.rule_loader_eval.fixtures import Fixture
from ai_rules.rule_loader_eval.matcher import (
    CitationDrift,
    MatchResult,
    match_loaded_rules,
)
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata, load_rules_metadata


@dataclass(frozen=True)
class RunResult:
    """Engine output for one fixture.

    A fixture passes iff:
    - ``match.passed`` is True (required + dependencies all loaded), AND
    - ``signal_report.ok`` is True (3-signal agreement holds), AND
    - ``citation_drifts`` is empty (no line-count fabrication), AND
    - ``run.output_violations`` is empty (bootstrap/no-match output shape is valid), AND
    - ``depends_violations`` is empty (all required: deps of loaded rules are also loaded).

    All checks are unconditional. There are no escape flags.
    """

    fixture_id: str
    run: AgentRun
    match: MatchResult
    signal_report: SignalReport
    citation_drifts: tuple[CitationDrift, ...] = field(default_factory=tuple)
    depends_violations: tuple[DependsViolation, ...] = field(default_factory=tuple)
    """R8 violations: rules in loaded set whose required: deps are absent."""

    @property
    def passed(self) -> bool:
        """Composite pass/fail across all four checks."""
        return (
            self.match.passed
            and self.signal_report.ok
            and not self.citation_drifts
            and not self.run.output_violations
            and not self.depends_violations
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
    )
    if getattr(run, "is_infra_error", False):
        raise InfraError(run.infra_error_detail or "agent SDK reported infra error")
    match = match_loaded_rules(
        loaded=run.loaded,
        required=fixture.required,
        dependencies=fixture.dependencies,
        forbidden=fixture.forbidden,
        optional=fixture.optional,
        strict_forbidden=strict_forbidden,
    )
    return RunResult(
        fixture_id=fixture.id,
        run=run,
        match=match,
        signal_report=signal_disagreement(run, fixture_optional=fixture.optional),
        citation_drifts=citation_drift(run, rules_meta),
        depends_violations=tuple(validate_depends_propagation(run.loaded, rules_meta)),
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
        missing_required=tuple(fixture.required),
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
