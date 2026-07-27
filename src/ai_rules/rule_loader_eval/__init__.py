"""Rule Loading Evaluator — live-agent sanity check.

Drives the Cortex Code Agent SDK against AGENTS.md plus a fixture prompt,
captures the rules the agent loaded, and compares
them to the fixture's declared expectation. Pre-commit drives a smoke
subset; CI runs only the trigger-evidence invariant.

Public API:
- ``Fixture`` / ``load_fixture`` / ``load_fixtures`` / ``validate_fixture`` — fixture loading
- ``RuleMetadata`` / ``load_rules_metadata`` — rule front-matter parser
- ``MatchResult`` / ``match_loaded_rules`` — required + dependencies matcher
- ``AgentRun`` / ``run_live`` / ``run_live_async`` (live) — runner entry points
- ``run_fixture`` (live) — engine entry point
"""

from ai_rules.rule_loader_eval.agent_runner import AgentRun, run_live, run_live_async
from ai_rules.rule_loader_eval.fixtures import (
    Fixture,
    FixtureValidationError,
    load_fixture,
    load_fixtures,
    validate_fixture,
)
from ai_rules.rule_loader_eval.matcher import MatchResult, match_loaded_rules
from ai_rules.rule_loader_eval.rules_meta import RuleMetadata, load_rules_metadata

__all__ = [
    "AgentRun",
    "Fixture",
    "FixtureValidationError",
    "MatchResult",
    "RuleMetadata",
    "load_fixture",
    "load_fixtures",
    "load_rules_metadata",
    "match_loaded_rules",
    "run_live",
    "run_live_async",
    "validate_fixture",
]

SDK_PIN = "1.0.6"
"""Pinned Cortex Code Agent SDK version.

``ai-rules rule-loader doctor`` enforces equality with this pin via
``importlib.metadata.version("cortex-code-agent-sdk")``. Bumps require
a deliberate PR.
"""
