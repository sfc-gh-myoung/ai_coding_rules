"""Branch-coverage tests for sdk_capture.py."""

from __future__ import annotations

import io
import os

import pytest

from ai_rules.rule_loader_eval.sdk_capture import quiet_sdk, replay_buffer

# ---------------------------------------------------------------------------
# replay_buffer
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_replay_buffer_none_is_noop(capsys) -> None:
    """replay_buffer(None) returns without printing anything."""
    replay_buffer(None)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.unit
def test_replay_buffer_empty_buf_is_noop(capsys) -> None:
    """replay_buffer with an empty StringIO returns without printing."""
    buf = io.StringIO()
    replay_buffer(buf)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.unit
def test_replay_buffer_prints_content_to_stderr(capfd) -> None:
    """replay_buffer writes non-empty lines to sys.__stderr__ (fd-level)."""
    buf = io.StringIO("hello\nworld\n")
    replay_buffer(buf, prefix="[test] ")
    captured = capfd.readouterr()
    assert "[test] hello" in captured.err
    assert "[test] world" in captured.err


@pytest.mark.unit
def test_replay_buffer_skips_whitespace_only_lines(capfd) -> None:
    """replay_buffer skips lines that are only whitespace."""
    buf = io.StringIO("   \nhello\n   \n")
    replay_buffer(buf)
    captured = capfd.readouterr()
    assert "[sdk] hello" in captured.err
    # Whitespace-only lines do not appear
    assert captured.err.count("\n") == 1


# ---------------------------------------------------------------------------
# quiet_sdk: env-var restoration
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_quiet_sdk_restores_pre_existing_env_vars() -> None:
    """quiet_sdk restores CORTEX_CODE_QUIET and CORTEX_LOG_LEVEL that were set before entry."""
    os.environ["CORTEX_CODE_QUIET"] = "original_quiet"
    os.environ["CORTEX_LOG_LEVEL"] = "original_level"
    try:
        with quiet_sdk(capture=True) as buf:
            # Inside: values may be overwritten by setdefault
            pass
        # After: must be restored
        assert os.environ.get("CORTEX_CODE_QUIET") == "original_quiet"
        assert os.environ.get("CORTEX_LOG_LEVEL") == "original_level"
    finally:
        os.environ.pop("CORTEX_CODE_QUIET", None)
        os.environ.pop("CORTEX_LOG_LEVEL", None)


@pytest.mark.unit
def test_quiet_sdk_capture_false_yields_none() -> None:
    """quiet_sdk(capture=False) is a no-op that yields None."""
    with quiet_sdk(capture=False) as buf:
        assert buf is None
