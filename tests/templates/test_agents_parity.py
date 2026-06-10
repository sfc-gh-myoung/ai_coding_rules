"""Drift guard: the two AGENTS templates must stay identical outside MODE content.

`AGENTS_MODE.md.template` and `AGENTS_NO_MODE.md.template` share a single bootstrap
protocol skeleton. The only legitimate differences are the PLAN/ACT (MODE) framework
in the MODE template and the auto-execute behavior in the NO_MODE template. Those
exclusive regions are wrapped in sentinel comments:

    <!-- MODE-ONLY:start -->    ... only in AGENTS_MODE       ... <!-- MODE-ONLY:end -->
    <!-- NO-MODE-ONLY:start --> ... only in AGENTS_NO_MODE    ... <!-- NO-MODE-ONLY:end -->

This test strips both sentinel regions (and the template marker line) from each file,
normalizes whitespace, and asserts the remaining shared skeletons are identical. Any
edit that diverges the shared protocol without using a sentinel fails here.
"""

from __future__ import annotations

import difflib
from pathlib import Path

import pytest

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
MODE_TEMPLATE = TEMPLATES_DIR / "AGENTS_MODE.md.template"
NO_MODE_TEMPLATE = TEMPLATES_DIR / "AGENTS_NO_MODE.md.template"

START_MARKERS = {"<!-- MODE-ONLY:start -->", "<!-- NO-MODE-ONLY:start -->"}
END_MARKERS = {"<!-- MODE-ONLY:end -->", "<!-- NO-MODE-ONLY:end -->"}


def shared_skeleton(text: str) -> str:
    """Return the protocol skeleton shared by both templates.

    Drops the leading ``<!-- Template: ... -->`` marker line, removes every
    sentinel-fenced region (inclusive of the marker lines), trims trailing
    whitespace, collapses consecutive blank lines, and strips leading/trailing
    blank lines so fence-adjacent spacing cannot cause false drift.
    """
    lines = text.split("\n")
    if lines and lines[0].startswith("<!-- Template:"):
        lines = lines[1:]

    kept: list[str] = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped in START_MARKERS:
            skipping = True
            continue
        if stripped in END_MARKERS:
            skipping = False
            continue
        if skipping:
            continue
        kept.append(line.rstrip())

    collapsed: list[str] = []
    for line in kept:
        if line == "" and collapsed and collapsed[-1] == "":
            continue
        collapsed.append(line)
    while collapsed and collapsed[0] == "":
        collapsed.pop(0)
    while collapsed and collapsed[-1] == "":
        collapsed.pop()
    return "\n".join(collapsed)


@pytest.mark.unit
def test_templates_exist():
    assert MODE_TEMPLATE.exists(), f"Missing {MODE_TEMPLATE}"
    assert NO_MODE_TEMPLATE.exists(), f"Missing {NO_MODE_TEMPLATE}"


@pytest.mark.unit
def test_shared_skeleton_is_identical():
    """Non-MODE content must be byte-identical between the two templates."""
    mode_skeleton = shared_skeleton(MODE_TEMPLATE.read_text())
    no_mode_skeleton = shared_skeleton(NO_MODE_TEMPLATE.read_text())

    if mode_skeleton != no_mode_skeleton:
        diff = "\n".join(
            difflib.unified_diff(
                no_mode_skeleton.split("\n"),
                mode_skeleton.split("\n"),
                fromfile="AGENTS_NO_MODE (shared skeleton)",
                tofile="AGENTS_MODE (shared skeleton)",
                lineterm="",
            )
        )
        pytest.fail(
            "AGENTS templates drifted outside MODE-specific content. "
            "Wrap MODE-only content in <!-- MODE-ONLY:start/end --> and "
            "NO_MODE-only content in <!-- NO-MODE-ONLY:start/end -->, or "
            "make the shared lines identical.\n\n" + diff
        )


@pytest.mark.unit
def test_sentinels_are_balanced():
    """Every sentinel start must have a matching end in each template."""
    for template in (MODE_TEMPLATE, NO_MODE_TEMPLATE):
        text = template.read_text()
        for start, end in (
            ("<!-- MODE-ONLY:start -->", "<!-- MODE-ONLY:end -->"),
            ("<!-- NO-MODE-ONLY:start -->", "<!-- NO-MODE-ONLY:end -->"),
        ):
            assert text.count(start) == text.count(end), (
                f"Unbalanced {start}/{end} in {template.name}"
            )

    # Each template only carries its own exclusive sentinels.
    mode_text = MODE_TEMPLATE.read_text()
    no_mode_text = NO_MODE_TEMPLATE.read_text()
    assert "<!-- MODE-ONLY:start -->" in mode_text
    assert "<!-- NO-MODE-ONLY:start -->" not in mode_text
    assert "<!-- NO-MODE-ONLY:start -->" in no_mode_text
    assert "<!-- MODE-ONLY:start -->" not in no_mode_text
