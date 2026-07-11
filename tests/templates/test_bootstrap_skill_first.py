"""Acceptance tests for the skill-first bootstrap protocol (TDD red phase).

These tests assert the INTENDED STATE after plan-task-0f26caf9 Step 2 implementation:
  - Both AGENTS templates make rule-loader skill the PRIMARY Step 2 mechanism.
  - grep against RULES_INDEX_COMPACT.md is explicitly a FALLBACK (Step 2B), labelled as such.
  - Both templates are parity-consistent in their Step 2 regions.

Tests referencing `rule-loader/SKILL.md` or a FALLBACK marker are expected to FAIL
until the templates are updated per the plan (implementor's job — do NOT fix here).
"""

from __future__ import annotations

import difflib
import re
from pathlib import Path

import pytest

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
MODE_TEMPLATE = TEMPLATES_DIR / "AGENTS_MODE.md.template"
NO_MODE_TEMPLATE = TEMPLATES_DIR / "AGENTS_NO_MODE.md.template"

_START_MARKERS = {"<!-- MODE-ONLY:start -->", "<!-- NO-MODE-ONLY:start -->"}
_END_MARKERS = {"<!-- MODE-ONLY:end -->", "<!-- NO-MODE-ONLY:end -->"}

# Stable tokens required by the plan in the new Step 2 block.
# GREP_TOKEN is intentionally the flag-agnostic prefix `grep -i` so it matches both
# the legacy `grep -iE` and the COMPACT-era `grep -iwE` (word-boundary) fallback.
SKILL_PATH_TOKEN = "rule-loader/SKILL.md"
FALLBACK_RE = re.compile(r"(FALLBACK|Step 2B\b|2B\.)", re.IGNORECASE)
GREP_TOKEN = "grep -i"
RULES_INDEX_TOKEN = "RULES_INDEX.md"


def _strip_sentinels(text: str) -> str:
    """Remove sentinel-fenced regions and the leading template-marker line."""
    lines = text.split("\n")
    if lines and lines[0].startswith("<!-- Template:"):
        lines = lines[1:]
    kept: list[str] = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped in _START_MARKERS:
            skipping = True
            continue
        if stripped in _END_MARKERS:
            skipping = False
            continue
        if not skipping:
            kept.append(line)
    return "\n".join(kept)


def extract_step2_region(text: str) -> str:
    """Return the text of the Step 2 block (between **Step 2:** and **Step 3:**).

    Sentinel-fenced regions are stripped first so MODE-only / NO-MODE-only
    content does not contaminate the shared skeleton check.
    Returns an empty string if Step 2 cannot be located.
    """
    body = _strip_sentinels(text)
    step2_m = re.search(r"\*\*Step 2:", body)
    step3_m = re.search(r"\*\*Step 3:", body)
    if not step2_m:
        return ""
    end = step3_m.start() if step3_m else len(body)
    return body[step2_m.start() : end]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def mode_step2() -> str:
    return extract_step2_region(MODE_TEMPLATE.read_text())


@pytest.fixture(scope="module")
def no_mode_step2() -> str:
    return extract_step2_region(NO_MODE_TEMPLATE.read_text())


# ---------------------------------------------------------------------------
# Tests: skill-first primary path (EXPECTED RED before implementation)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_step2_skill_path_present_in_mode_template(mode_step2: str) -> None:
    """Step 2 in AGENTS_MODE must contain a read_file call targeting rule-loader/SKILL.md.

    Acceptance test for plan-task-0f26caf9 sd0b2 — skill-first bootstrap.
    Fails until templates are updated per the plan.
    """
    assert SKILL_PATH_TOKEN in mode_step2, (
        f"Expected '{SKILL_PATH_TOKEN}' in Step 2 of AGENTS_MODE.md.template "
        f"(plan: skill is the PRIMARY discovery mechanism). "
        f"Step 2 region (first 400 chars):\n{mode_step2[:400]}"
    )


@pytest.mark.unit
def test_step2_skill_path_present_in_no_mode_template(no_mode_step2: str) -> None:
    """Step 2 in AGENTS_NO_MODE must contain a read_file call targeting rule-loader/SKILL.md.

    Acceptance test for plan-task-0f26caf9 sd0b2 — skill-first bootstrap.
    Fails until templates are updated per the plan.
    """
    assert SKILL_PATH_TOKEN in no_mode_step2, (
        f"Expected '{SKILL_PATH_TOKEN}' in Step 2 of AGENTS_NO_MODE.md.template "
        f"(plan: skill is the PRIMARY discovery mechanism). "
        f"Step 2 region (first 400 chars):\n{no_mode_step2[:400]}"
    )


@pytest.mark.unit
def test_step2_skill_appears_before_grep_in_mode_template(mode_step2: str) -> None:
    """rule-loader/SKILL.md must appear BEFORE grep in AGENTS_MODE Step 2 (primary before fallback).

    Acceptance test for plan-task-0f26caf9 sd0b2 — skill-first bootstrap.
    Fails until templates are updated per the plan.
    """
    assert SKILL_PATH_TOKEN in mode_step2, (
        f"'{SKILL_PATH_TOKEN}' missing from AGENTS_MODE Step 2 — cannot verify ordering"
    )
    assert GREP_TOKEN in mode_step2, (
        f"'{GREP_TOKEN}' missing from AGENTS_MODE Step 2 (expected as fallback)"
    )
    skill_pos = mode_step2.index(SKILL_PATH_TOKEN)
    grep_pos = mode_step2.index(GREP_TOKEN)
    assert skill_pos < grep_pos, (
        f"rule-loader/SKILL.md (char {skill_pos}) must appear BEFORE 'grep -iE' "
        f"(char {grep_pos}) in AGENTS_MODE Step 2"
    )


@pytest.mark.unit
def test_step2_skill_appears_before_grep_in_no_mode_template(no_mode_step2: str) -> None:
    """rule-loader/SKILL.md must appear BEFORE grep in AGENTS_NO_MODE Step 2.

    Acceptance test for plan-task-0f26caf9 sd0b2 — skill-first bootstrap.
    Fails until templates are updated per the plan.
    """
    assert SKILL_PATH_TOKEN in no_mode_step2, (
        f"'{SKILL_PATH_TOKEN}' missing from AGENTS_NO_MODE Step 2 — cannot verify ordering"
    )
    assert GREP_TOKEN in no_mode_step2, (
        f"'{GREP_TOKEN}' missing from AGENTS_NO_MODE Step 2 (expected as fallback)"
    )
    skill_pos = no_mode_step2.index(SKILL_PATH_TOKEN)
    grep_pos = no_mode_step2.index(GREP_TOKEN)
    assert skill_pos < grep_pos, (
        f"rule-loader/SKILL.md (char {skill_pos}) must appear BEFORE 'grep -iE' "
        f"(char {grep_pos}) in AGENTS_NO_MODE Step 2"
    )


# ---------------------------------------------------------------------------
# Tests: grep labelled as FALLBACK (EXPECTED RED before implementation)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_step2_fallback_marker_precedes_grep_in_mode_template(mode_step2: str) -> None:
    """A FALLBACK / 2B marker must appear before the grep line in AGENTS_MODE Step 2.

    Acceptance test for plan-task-0f26caf9 sd0b2 — skill-first bootstrap.
    Fails until templates are updated per the plan.
    """
    fallback_m = FALLBACK_RE.search(mode_step2)
    assert fallback_m is not None, (
        "No FALLBACK/Step 2B marker found in AGENTS_MODE Step 2. "
        "The grep section must be explicitly labelled as a fallback path."
    )
    grep_pos = mode_step2.find(GREP_TOKEN)
    assert grep_pos != -1, f"'{GREP_TOKEN}' not found in AGENTS_MODE Step 2"
    assert fallback_m.start() < grep_pos, (
        f"FALLBACK marker (char {fallback_m.start()}) must precede "
        f"'grep -iE' (char {grep_pos}) in AGENTS_MODE Step 2"
    )


@pytest.mark.unit
def test_step2_fallback_marker_precedes_grep_in_no_mode_template(no_mode_step2: str) -> None:
    """A FALLBACK / 2B marker must appear before the grep line in AGENTS_NO_MODE Step 2.

    Acceptance test for plan-task-0f26caf9 sd0b2 — skill-first bootstrap.
    Fails until templates are updated per the plan.
    """
    fallback_m = FALLBACK_RE.search(no_mode_step2)
    assert fallback_m is not None, (
        "No FALLBACK/Step 2B marker found in AGENTS_NO_MODE Step 2. "
        "The grep section must be explicitly labelled as a fallback path."
    )
    grep_pos = no_mode_step2.find(GREP_TOKEN)
    assert grep_pos != -1, f"'{GREP_TOKEN}' not found in AGENTS_NO_MODE Step 2"
    assert fallback_m.start() < grep_pos, (
        f"FALLBACK marker (char {fallback_m.start()}) must precede "
        f"'grep -iE' (char {grep_pos}) in AGENTS_NO_MODE Step 2"
    )


# ---------------------------------------------------------------------------
# Regression tests: grep + RULES_INDEX preserved (expected GREEN now and after)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_step2_grep_fallback_preserved_in_mode_template(mode_step2: str) -> None:
    """Grep -iE and RULES_INDEX.md must still exist in AGENTS_MODE Step 2 (as the fallback)."""
    assert GREP_TOKEN in mode_step2, (
        f"'{GREP_TOKEN}' missing — fallback grep must be preserved in AGENTS_MODE Step 2"
    )
    assert RULES_INDEX_TOKEN in mode_step2, (
        f"'{RULES_INDEX_TOKEN}' missing — fallback path must reference it in AGENTS_MODE Step 2"
    )


@pytest.mark.unit
def test_step2_grep_fallback_preserved_in_no_mode_template(no_mode_step2: str) -> None:
    """Grep -iE and RULES_INDEX.md must still exist in AGENTS_NO_MODE Step 2 (as the fallback)."""
    assert GREP_TOKEN in no_mode_step2, (
        f"'{GREP_TOKEN}' missing — fallback grep must be preserved in AGENTS_NO_MODE Step 2"
    )
    assert RULES_INDEX_TOKEN in no_mode_step2, (
        f"'{RULES_INDEX_TOKEN}' missing — fallback path must reference it in AGENTS_NO_MODE Step 2"
    )


# ---------------------------------------------------------------------------
# Parity test: Step 2 must be identical across both templates
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_step2_parity_between_templates(mode_step2: str, no_mode_step2: str) -> None:
    """Both templates' Step 2 regions must be byte-identical (shared skeleton requirement).

    Will fail if templates diverge after implementation — changes must be applied to both.
    """
    if mode_step2 != no_mode_step2:
        diff = "\n".join(
            difflib.unified_diff(
                no_mode_step2.split("\n"),
                mode_step2.split("\n"),
                fromfile="AGENTS_NO_MODE Step 2",
                tofile="AGENTS_MODE Step 2",
                lineterm="",
            )
        )
        pytest.fail(
            "Step 2 regions differ between AGENTS_MODE and AGENTS_NO_MODE templates. "
            "Apply changes identically to both (outside sentinel regions).\n\n" + diff
        )
