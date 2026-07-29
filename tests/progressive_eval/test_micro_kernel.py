"""Micro-kernel content contract tests.

The micro-kernel exists in three places that must not drift: the ``MICRO_KERNEL``
string, the packaged ``micro_kernel_content.md`` read by the production hook, and
the plugin copy. These tests pin the behavioural guidance added in v1.1.0 and
guard the copies against divergence.
"""

from __future__ import annotations

from pathlib import Path

from ai_rules.progressive_eval.micro_kernel import (
    MICRO_KERNEL,
    MICRO_KERNEL_VERSION,
    get_micro_kernel,
    token_estimate,
)

_REPO = Path(__file__).resolve().parents[2]
_SRC_MD = _REPO / "src" / "ai_rules" / "progressive_eval" / "micro_kernel_content.md"
_PLUGIN_MD = _REPO / "ai-coding-rules-plugin" / "micro_kernel_content.md"


def test_micro_kernel_copies_do_not_drift() -> None:
    """The string, the packaged .md, and the plugin .md must be byte-identical."""
    assert _SRC_MD.exists(), f"missing {_SRC_MD}"
    assert _PLUGIN_MD.exists(), f"missing {_PLUGIN_MD}"
    assert _SRC_MD.read_text(encoding="utf-8") == MICRO_KERNEL
    assert _PLUGIN_MD.read_text(encoding="utf-8") == MICRO_KERNEL


def test_micro_kernel_within_token_budget() -> None:
    """Budget is 500 tokens, expandable to 800. Keep headroom."""
    assert token_estimate() <= 500


def test_micro_kernel_anchors_rule_paths() -> None:
    """Agents guessed absolute project roots and got file-not-found; anchor the paths."""
    k = get_micro_kernel()
    assert "EXACTLY as given" in k
    assert "Never convert them to absolute paths" in k
    assert "never guess a project root" in k


def test_micro_kernel_frames_matches_as_candidates() -> None:
    """The 3-rule cap and 'read every matched rule' were contradictory; cap wins."""
    k = get_micro_kernel()
    assert "CANDIDATES" in k
    assert "up to 3" in k
    assert "Cap: 3 domain rules per response" in k


def test_micro_kernel_version_bumped() -> None:
    assert MICRO_KERNEL_VERSION >= "1.1.0"
