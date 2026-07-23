"""Comparison runner: executes behavioral fixtures in both arms.

Arm A (front-loaded): Simulates full AGENTS.md bootstrap + upfront rule loading.
Arm B (progressive): Uses micro-kernel + manifest + lazy loader.

This module simulates both architectures by varying the system prompt
and rule injection strategy, then scores behavioral compliance for each.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ai_rules.progressive_eval.behavioral_scorer import (
    BehavioralCheck,
    ConversationTranscript,
    score_fixture,
)
from ai_rules.progressive_eval.compare import (
    ArmResult,
    ComparisonReport,
    FixtureComparison,
)
from ai_rules.progressive_eval.manifest_generator import ProgressiveManifest, generate_manifest
from ai_rules.progressive_eval.micro_kernel import token_estimate


@dataclass(frozen=True)
class BehavioralFixture:
    """A loaded behavioral fixture with its checks."""

    id: str
    prompt: str
    required_rules: tuple[str, ...]
    behavioral_checks: tuple[BehavioralCheck, ...]
    architecture_mode: str  # "both", "progressive", "front-loaded"

    @classmethod
    def from_yaml(cls, path: Path) -> BehavioralFixture:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        checks = tuple(BehavioralCheck.from_dict(c) for c in data.get("behavioral_checks", []))
        expected = data.get("expected", {})
        return cls(
            id=data["id"],
            prompt=data["prompt"],
            required_rules=tuple(expected.get("required", [])),
            behavioral_checks=checks,
            architecture_mode=data.get("architecture_mode", "both"),
        )


def load_behavioral_fixtures(fixtures_dir: Path) -> list[BehavioralFixture]:
    """Load all behavioral fixtures from a directory."""
    fixtures = []
    for path in sorted(fixtures_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if data.get("variant") == "behavioral":
            fixtures.append(BehavioralFixture.from_yaml(path))
    return fixtures


def estimate_arm_a_tokens(fixture: BehavioralFixture, rules_dir: Path) -> int:
    """Estimate token cost for Arm A (front-loaded): all rules loaded upfront."""
    # AGENTS.md (~1600 tokens) + 000-global-core.md (~2550) + domain rules
    base_overhead = 1600 + 2550
    rule_tokens = 0
    for rule_path in fixture.required_rules:
        full_path = rules_dir / rule_path.removeprefix("rules/")
        if full_path.exists():
            rule_tokens += len(full_path.read_text(encoding="utf-8")) // 4
    return base_overhead + rule_tokens


def estimate_arm_b_tokens(fixture: BehavioralFixture, manifest: ProgressiveManifest) -> int:
    """Estimate token cost for Arm B (progressive): micro-kernel + manifest only until trigger."""
    # AGENTS-progressive.md (~350) + micro-kernel (~281) + manifest
    base_overhead = 350 + token_estimate() + manifest.token_estimate
    return base_overhead


def simulate_arm_a(
    fixture: BehavioralFixture,
    rules_dir: Path,
    transcript: ConversationTranscript | None = None,
) -> ArmResult:
    """Simulate Arm A execution and score.

    In live mode, this would drive the SDK with full AGENTS.md.
    In simulation mode (no transcript), estimates tokens from rule sizes.
    """
    token_cost = estimate_arm_a_tokens(fixture, rules_dir)

    if transcript:
        score = score_fixture(fixture.id, list(fixture.behavioral_checks), transcript)
        return ArmResult(
            passed=score.passed,
            score=score.score,
            total_input_tokens=transcript.total_input_tokens or token_cost,
            total_output_tokens=transcript.total_output_tokens,
            turns=len(transcript.turns),
            rule_tokens_loaded=token_cost - 1600,  # exclude AGENTS.md overhead
        )

    # Simulation mode: no transcript, estimate only
    return ArmResult(
        passed=True,  # assume pass in simulation
        score=1.0,
        total_input_tokens=token_cost,
        total_output_tokens=0,
        turns=0,
        rule_tokens_loaded=token_cost - 1600,
    )


def simulate_arm_b(
    fixture: BehavioralFixture,
    manifest: ProgressiveManifest,
    transcript: ConversationTranscript | None = None,
) -> ArmResult:
    """Simulate Arm B execution and score.

    In live mode, this would drive the SDK with AGENTS-progressive.md + manifest.
    In simulation mode, estimates tokens from micro-kernel + manifest.
    """
    token_cost = estimate_arm_b_tokens(fixture, manifest)

    if transcript:
        score = score_fixture(fixture.id, list(fixture.behavioral_checks), transcript)
        return ArmResult(
            passed=score.passed,
            score=score.score,
            total_input_tokens=transcript.total_input_tokens or token_cost,
            total_output_tokens=transcript.total_output_tokens,
            turns=len(transcript.turns),
            rule_tokens_loaded=transcript.rule_tokens_loaded,
        )

    # Simulation mode
    return ArmResult(
        passed=True,
        score=1.0,
        total_input_tokens=token_cost,
        total_output_tokens=0,
        turns=0,
        rule_tokens_loaded=token_cost - 350,
    )


def run_comparison(
    fixtures_dir: Path,
    rules_dir: Path,
    index_path: Path,
    *,
    models: list[str] | None = None,
) -> ComparisonReport:
    """Run A/B comparison across all behavioral fixtures.

    In the current implementation, this runs in SIMULATION mode
    (estimates token costs without live SDK calls). To run live,
    integrate with the agent_runner SDK and pass real transcripts.
    """
    if models is None:
        models = ["claude-opus-4-6"]

    fixtures = load_behavioral_fixtures(fixtures_dir)
    report = ComparisonReport(models=models)

    for fixture in fixtures:
        if fixture.architecture_mode not in ("both", "front-loaded", "progressive"):
            continue

        for model in models:
            manifest = generate_manifest(index_path, user_request=fixture.prompt)

            arm_a = simulate_arm_a(fixture, rules_dir)
            arm_b = simulate_arm_b(fixture, manifest)

            report.fixture_results.append(
                FixtureComparison(
                    fixture_id=fixture.id,
                    model=model,
                    arm_a=arm_a,
                    arm_b=arm_b,
                )
            )

    report.compute_aggregate()
    report.compute_statistical_tests()
    return report
