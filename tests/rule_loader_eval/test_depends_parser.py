"""Tests for the ``required:`` / ``optional:`` Depends bucket parser."""

from __future__ import annotations

from ai_rules.rule_loader_eval.rules_meta import _split_depends, split_depends_buckets


def test_split_buckets_basic() -> None:
    req, opt = split_depends_buckets(
        "required:999-test-core.md, optional:103-snowflake-performance-tuning.md"
    )
    assert req == ["999-test-core.md"]
    assert opt == ["103-snowflake-performance-tuning.md"]


def test_split_buckets_unprefixed_defaults_to_required() -> None:
    req, opt = split_depends_buckets("999-test-core.md, 100-snowflake-core.md")
    assert req == ["999-test-core.md", "100-snowflake-core.md"]
    assert opt == []


def test_split_buckets_mixed_prefix_and_unprefixed() -> None:
    req, opt = split_depends_buckets(
        "required:999-test-core.md, 100-snowflake-core.md, optional:105-x.md"
    )
    assert req == ["999-test-core.md", "100-snowflake-core.md"]
    assert opt == ["105-x.md"]


def test_split_buckets_whitespace_tolerance() -> None:
    req, opt = split_depends_buckets("required: 999-test-core.md , optional: 103-x.md")
    assert req == ["999-test-core.md"]
    assert opt == ["103-x.md"]


def test_split_buckets_none_value() -> None:
    assert split_depends_buckets("None") == ([], [])
    assert split_depends_buckets("—") == ([], [])
    assert split_depends_buckets("") == ([], [])


def test_split_buckets_md_extension_added() -> None:
    req, _ = split_depends_buckets("required:foo, optional:bar")
    assert req == ["foo.md"]


def test_eval_split_depends_normalizes_to_rules_prefix() -> None:
    req, opt = _split_depends(
        "required:100-snowflake-core.md, optional:103-snowflake-performance-tuning.md"
    )
    assert req == ("rules/100-snowflake-core.md",)
    assert opt == ("rules/103-snowflake-performance-tuning.md",)


def test_eval_split_depends_already_qualified_path() -> None:
    req, opt = _split_depends("required:rules/100-snowflake-core.md")
    assert req == ("rules/100-snowflake-core.md",)
    assert opt == ()


def test_eval_split_depends_filters_sentinels() -> None:
    req, opt = _split_depends("None")
    assert req == ()
    assert opt == ()
