"""Contract checks for the `$ai-coding-rules-help` reference card.

The card is hand-written, so these tests are its drift guard: the skill table
must list exactly the skills the plugin build ships (derived from
``BUILD_COPIES``), each with its explicit trigger.
"""

from __future__ import annotations

import re
from pathlib import Path

from typer.testing import CliRunner

from ai_rules.commands.plugin import plugin_app
from ai_rules.plugin.replicas import BUILD_COPIES

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_REL = "skills/ai-coding-rules-help/SKILL.md"
SKILL_FILE = REPO_ROOT / SKILL_REL
CARD_HEADING = re.compile(r"^## Reference card$", re.MULTILINE)
MAX_CARD_LINES = 60


def _card(text: str) -> str:
    """Return the reference card: everything after its H2 heading line."""
    headings = CARD_HEADING.findall(text)
    assert len(headings) == 1, "expected exactly one '## Reference card' heading line"
    return CARD_HEADING.split(text, 1)[1].strip("\n")


def _shipped_skills() -> set[str]:
    """Names of every skill whose SKILL.md the plugin build ships."""
    pattern = re.compile(r"^skills/([^/]+)/SKILL\.md$")
    return {m.group(1) for c in BUILD_COPIES if (m := pattern.match(c.dest))}


def _card_skill_rows(card: str) -> dict[str, str]:
    """Map skill name to trigger cell for each row of the card's skill table."""
    rows: dict[str, str] = {}
    for line in card.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3 and (m := re.fullmatch(r"`([a-z0-9-]+)`", cells[0])):
            rows[m.group(1)] = cells[1]
    return rows


def test_help_skill_is_registered_for_the_build() -> None:
    """The help skill is a declared build copy of its canonical source."""
    assert any(c.primary == SKILL_REL and c.dest == SKILL_REL for c in BUILD_COPIES)


def test_card_lists_exactly_the_shipped_skills() -> None:
    """Every shipped skill appears in the card, and nothing else does."""
    rows = _card_skill_rows(_card(SKILL_FILE.read_text(encoding="utf-8")))
    assert set(rows) == _shipped_skills()


def test_card_triggers_name_each_skill() -> None:
    """Each row's trigger names that skill's `$<name>` invocation."""
    rows = _card_skill_rows(_card(SKILL_FILE.read_text(encoding="utf-8")))
    for name, trigger in rows.items():
        assert f"`${name}`" in trigger, f"{name}: trigger {trigger!r} lacks `${name}`"


def test_card_skill_names_match_shipped_frontmatter() -> None:
    """Each shipped skill's frontmatter name matches its directory."""
    for name in _shipped_skills():
        text = (REPO_ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert re.search(rf"^name: {re.escape(name)}$", text, re.MULTILINE), name


def test_card_is_short_and_read_only() -> None:
    """The card fits in one or two screens and the skill forbids side effects."""
    text = SKILL_FILE.read_text(encoding="utf-8")
    assert len(_card(text).splitlines()) <= MAX_CARD_LINES
    assert "## Instructions" not in _card(text)
    assert "Do not run tools" in text
    assert "write, create or modify any file, flag or setting" in text


def test_build_emits_help_skill_unchanged(tmp_path: Path) -> None:
    """The built plugin carries the help skill byte-for-byte."""
    out = tmp_path / "plugin"
    result = CliRunner().invoke(plugin_app, ["build", "--plugin-dir", str(out)])
    assert result.exit_code == 0, result.output
    assert (out / SKILL_REL).read_bytes() == SKILL_FILE.read_bytes()
