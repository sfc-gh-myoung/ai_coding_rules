"""Quiet the Cortex Code Agent SDK while a progress UI is active.

When the rule-loader CLI renders a Rich progress bar (or its plain log-line
equivalent), unsolicited writes from the SDK -- ``Auto-apply [...]: 2 skill
repos``, ``[memory] Reranking: malformed LLM response, using fusion scores``,
and similar internal status lines -- collide with the progress UI. They
clobber the bar's redraw arithmetic, fight for terminal columns, and
generally make the run unwatchable.

This module provides a single context manager, :func:`quiet_sdk`, that
captures everything the SDK would have printed to stdout into a buffer
for the duration of the surrounding work. Three best-effort layers cover
the common silencing channels:

1. ``contextlib.redirect_stdout`` swaps :data:`sys.stdout` for an
   in-memory buffer process-wide. Useful for code paths that ``print``
   directly.
2. The ``cortex_code_agent_sdk`` logger is muted to ``ERROR`` level for
   the duration.
3. Two opt-in env vars (``CORTEX_CODE_QUIET=1`` and
   ``CORTEX_LOG_LEVEL=ERROR``) are set in case the SDK consults them.

The captured buffer is yielded to the caller; on failure (or when
``--debug`` is set) the caller is expected to replay it for forensic
purposes.

Synchronous-by-design: this is a regular ``contextlib.contextmanager``,
not an async one. The wrapped block can call ``asyncio.run(...)`` or
contain any other code; ``redirect_stdout`` is process-wide for the
entire ``with`` block, which is exactly what we want -- silence
everything for the duration of the batch. Callers that still need to
write to the real terminal during the block must use :data:`sys.__stdout__`
directly (see ``_on_outcome`` in ``commands/rule_loader.py``).
"""

from __future__ import annotations

import contextlib
import io
import logging
import os
import sys
from collections.abc import Iterator


@contextlib.contextmanager
def quiet_sdk(*, capture: bool = True) -> Iterator[io.StringIO | None]:
    """Suppress SDK-internal output while the body of the context runs.

    Args:
        capture: when False, the context manager is a no-op (yields None).
            Allows callers to gate the silencing on the active progress
            mode without branching at every call site.

    Yields:
        ``io.StringIO`` containing every byte the SDK wrote to stdout
        during the block, or None when ``capture`` is False.

    Example::

        with quiet_sdk(capture=mode is not ProgressMode.NONE) as buf:
            summary = run_batch(...)
        if buf is not None and any_failure:
            replay_buffer(buf)
    """
    if not capture:
        yield None
        return

    buf = io.StringIO()
    old_env = {
        "CORTEX_CODE_QUIET": os.environ.get("CORTEX_CODE_QUIET"),
        "CORTEX_LOG_LEVEL": os.environ.get("CORTEX_LOG_LEVEL"),
    }
    os.environ.setdefault("CORTEX_CODE_QUIET", "1")
    os.environ.setdefault("CORTEX_LOG_LEVEL", "ERROR")

    sdk_logger = logging.getLogger("cortex_code_agent_sdk")
    prev_level = sdk_logger.level
    sdk_logger.setLevel(logging.ERROR)

    # Silence ALL logging during the run. Logging StreamHandlers cache
    # ``sys.stderr`` at handler-construction time, so they bypass the
    # ``redirect_stderr`` swap below. ``logging.disable`` is the only blanket
    # silencer that catches third-party loggers (httpx, anthropic, urllib3,
    # ...) without enumerating them. Restored in ``finally``.
    prev_disable = logging.root.manager.disable
    logging.disable(logging.CRITICAL)

    # Redirect BOTH stdout and stderr -- the SDK emits status messages
    # (``\u2713 Auto-apply [_CORTEX_CODE_DEFAULT]``, ``[memory] Reranking: ...``)
    # via direct prints, not the logging module, and they go to whichever
    # stream the SDK chose. Without ``redirect_stderr`` they leak into the
    # terminal mid-frame and corrupt Rich Live's cursor-up math, leaving
    # stale progress bars in scrollback. Rich's own ``err_console`` writes
    # through a duplicated fd 2 (see ``_shared/console.py``) so the live
    # region keeps rendering correctly while these redirects are active.
    redirect_out = contextlib.redirect_stdout(buf)
    redirect_err = contextlib.redirect_stderr(buf)
    redirect_out.__enter__()
    redirect_err.__enter__()
    try:
        yield buf
    finally:
        redirect_err.__exit__(None, None, None)
        redirect_out.__exit__(None, None, None)
        logging.disable(prev_disable)
        sdk_logger.setLevel(prev_level)
        for key, prev in old_env.items():
            if prev is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = prev


def replay_buffer(buf: io.StringIO | None, *, prefix: str = "[sdk] ") -> None:
    """Replay a captured buffer to the real stderr, line by line.

    Used in ``--debug`` failure paths so the user can inspect what the SDK
    actually emitted while the progress UI hid it.
    """
    if buf is None:
        return
    text = buf.getvalue()
    if not text:
        return
    for line in text.splitlines():
        if line.strip():
            print(f"{prefix}{line}", file=sys.__stderr__)
