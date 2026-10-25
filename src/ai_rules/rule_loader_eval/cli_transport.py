"""Direct CoCo CLI event transport, with no Agent SDK dependency."""

from __future__ import annotations

import asyncio
import json
import shutil
from dataclasses import dataclass
from types import SimpleNamespace


@dataclass
class AssistantMessage:
    """Assistant event content from the CLI stream."""

    content: list


@dataclass
class ResultMessage:
    """Terminal event attributes exposed to the scoring runner."""

    num_turns: int
    stop_reason: str
    usage: dict
    total_cost_usd: float


class CortexCodeAgentOptions(SimpleNamespace):
    """Internal runner settings, not an SDK object."""


async def query(*, prompt: str, options: CortexCodeAgentOptions):
    """Stream direct CLI JSON events; reject missing results and CLI failures."""
    executable = shutil.which("cortex")
    if not executable:
        raise RuntimeError("CoCo CLI is required; install cortex before live evaluation.")
    command = [
        executable,
        "--input-format",
        "stream-json",
        "--output-format",
        "stream-json",
        "--private",
        "--no-mcp",
        "--max-turns",
        str(options.max_turns),
        "--effort",
        options.effort,
        "--allowed-tools",
        "Read",
        "Glob",
        "Grep",
        "--disallowed-tools",
        "Write",
        "Edit",
        "sql_execute",
        "Bash",
        "--setting-sources",
        "project",
    ]
    if options.model != "auto":
        command += ["--model", options.model]
    if options.connection:
        command += ["--connection", options.connection]
    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=options.cwd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=4 * 1024 * 1024,
    )
    assert process.stdin and process.stdout and process.stderr

    stderr_tail: list[str] = []

    async def drain_errors():
        assert process.stderr is not None
        async for line in process.stderr:
            text = line.decode(errors="replace")
            stderr_tail[:] = [*stderr_tail, text.strip()][-3:]
            options.stderr(text)

    errors = asyncio.create_task(drain_errors())
    request = {
        "type": "user",
        "message": {"role": "user", "content": options.system_prompt + "\n\n" + prompt},
    }
    result_seen = False
    try:
        process.stdin.write((json.dumps(request) + "\n").encode())
        await process.stdin.drain()
        process.stdin.close()
        async for line in process.stdout:
            try:
                event = json.loads(line)
            except ValueError as exc:
                raise RuntimeError("CoCo CLI emitted invalid JSON event.") from exc
            if event.get("type") == "assistant":
                blocks = event.get("message", {}).get("content", [])
                yield AssistantMessage([SimpleNamespace(**block) for block in blocks])
            elif event.get("type") == "result":
                result_seen = True
                if event.get("is_error") and event.get("subtype") != "error_max_turns":
                    raise RuntimeError("CoCo CLI reported an error result.")
                yield ResultMessage(
                    event.get("num_turns", 0),
                    event.get("subtype", ""),
                    event.get("usage", {}),
                    event.get("total_cost_usd", 0.0),
                )
        status = await process.wait()
        await errors
        if status or not result_seen:
            detail = " ".join(part for part in stderr_tail if part)[:400]
            raise RuntimeError(
                "CoCo CLI failed or ended without a terminal result."
                + (f" CLI said: {detail}" if detail else "")
            )
    finally:
        if process.returncode is None:
            process.kill()
            await process.wait()
        errors.cancel()
        await asyncio.gather(errors, return_exceptions=True)
