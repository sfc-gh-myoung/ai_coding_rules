"""Focused unit tests for rules_meta pure parsing helpers.

Targets the frontmatter/keyword/depends flatteners that the corpus-driven
tests don't exercise directly: malformed YAML, list vs scalar keyword forms,
and both dict and list ``depends`` shapes.
"""

from __future__ import annotations

from pathlib import Path

from ai_rules.rule_loader_eval.rules_meta import (
    _flatten_yaml_depends,
    _flatten_yaml_keywords,
    _parse_frontmatter,
    parse_rule_metadata,
)


def test_parse_frontmatter_malformed_yaml_returns_none() -> None:
    # A syntactically broken YAML body inside the fences must yield None.
    content = "---\nkeywords: [unterminated\n---\nbody\n"
    assert _parse_frontmatter(content) is None


def test_parse_frontmatter_no_closing_fence_returns_none() -> None:
    content = "---\nkeywords: a\nno closing fence here\n"
    assert _parse_frontmatter(content) is None


def test_parse_frontmatter_non_mapping_returns_none() -> None:
    content = "---\n- just\n- a\n- list\n---\n"
    assert _parse_frontmatter(content) is None


def test_parse_frontmatter_valid_mapping() -> None:
    content = "---\nkeywords:\n  - one\n  - two\n---\nbody\n"
    assert _parse_frontmatter(content) == {"keywords": ["one", "two"]}


def test_flatten_yaml_keywords_empty_list_and_scalar() -> None:
    assert _flatten_yaml_keywords(None) == ""
    assert _flatten_yaml_keywords([]) == ""
    assert _flatten_yaml_keywords(["a", " b ", ""]) == "a, b"
    assert _flatten_yaml_keywords("solo") == "solo"


def test_flatten_yaml_depends_dict_form_appends_md() -> None:
    value = {"required": ["100-a", "200-b.md", None], "optional": ["300-c"]}
    out = _flatten_yaml_depends(value)
    assert "required:100-a.md" in out
    assert "required:200-b.md" in out
    assert "optional:300-c.md" in out


def test_flatten_yaml_depends_list_form_defaults_required() -> None:
    value = ["100-a", "optional:300-c", None]
    out = _flatten_yaml_depends(value)
    assert "required:100-a.md" in out
    assert "optional:300-c.md" in out


def test_flatten_yaml_depends_empty_is_blank() -> None:
    assert _flatten_yaml_depends(None) == ""
    assert _flatten_yaml_depends([]) == ""


def test_parse_rule_metadata_uses_frontmatter_keywords_and_depends() -> None:
    content = (
        "---\n"
        "keywords:\n  - kw:streamlit\n  - ext:.py\n"
        "depends:\n  required:\n    - 000-global-core\n"
        "context_tier: High\n"
        "rule_version: v1.2.3\n"
        "---\n"
        "# Body\n"
    )
    md = parse_rule_metadata(Path("rules/100-x.md"), content)
    assert "kw:streamlit" in md.triggers
    assert md.typed_ext == (".py",)
    assert md.depends_required == ("rules/000-global-core.md",)
    assert md.rule_version == "1.2.3"
    assert md.context_tier == "High"
