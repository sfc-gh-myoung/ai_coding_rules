"""Direct CLI event parser tests with a fake process, no credentials/model calls."""

import asyncio
import json

from ai_rules.rule_loader_eval import cli_transport as transport


class FakeInput:
    """Capture the request without writing it to disk."""

    def write(self, data):
        self.data = data

    async def drain(self):
        pass

    def close(self):
        pass


def test_cli_stream_captures_tool_and_usage(monkeypatch):
    events = [
        {
            "type": "assistant",
            "message": {
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "input": {"file_path": "rules/000-global-core.md"},
                    },
                    {"type": "text", "text": "OK"},
                ]
            },
        },
        {
            "type": "result",
            "num_turns": 2,
            "subtype": "success",
            "usage": {"input_tokens": 10},
            "total_cost_usd": 0.0,
        },
    ]

    class Process:
        returncode = None
        stdin = FakeInput()

        def __init__(self):
            self.stdout = asyncio.StreamReader()
            self.stderr = asyncio.StreamReader()
            self.stdout.feed_data(b"".join((json.dumps(event) + "\n").encode() for event in events))
            self.stdout.feed_eof()
            self.stderr.feed_eof()

        async def wait(self):
            self.returncode = 0
            return 0

    captured = []

    async def spawn(*args, **kwargs):
        captured.extend(args)
        return Process()

    monkeypatch.setattr(transport.shutil, "which", lambda _: "/fake/cortex")
    monkeypatch.setattr(transport.asyncio, "create_subprocess_exec", spawn)

    async def collect():
        options = transport.CortexCodeAgentOptions(
            cwd="/fake",
            max_turns=5,
            effort="low",
            model="auto",
            connection="selected",
            system_prompt="protocol",
            stderr=lambda _: None,
        )
        return [event async for event in transport.query(prompt="prompt", options=options)]

    messages = asyncio.run(collect())
    assert messages[0].content[0].name == "Read"
    assert messages[1].usage == {"input_tokens": 10}
    assert "--connection" in captured and "selected" in captured
    assert "--private" in captured
    assert "--input-format" in captured


def test_failure_includes_cli_stderr_tail(monkeypatch):
    class Process:
        returncode = None
        stdin = FakeInput()

        def __init__(self):
            self.stdout = asyncio.StreamReader()
            self.stderr = asyncio.StreamReader()
            self.stdout.feed_eof()
            self.stderr.feed_data(
                b"Cortex cannot start: method is not allowed by your organization\n"
            )
            self.stderr.feed_eof()

        async def wait(self):
            self.returncode = 1
            return 1

    async def spawn(*args, **kwargs):
        return Process()

    monkeypatch.setattr(transport.shutil, "which", lambda _: "/fake/cortex")
    monkeypatch.setattr(transport.asyncio, "create_subprocess_exec", spawn)
    options = transport.CortexCodeAgentOptions(
        cwd="/fake",
        max_turns=1,
        effort="low",
        model="auto",
        connection="c",
        system_prompt="p",
        stderr=lambda _: None,
    )

    async def collect():
        return [event async for event in transport.query(prompt="p", options=options)]

    try:
        asyncio.run(collect())
    except RuntimeError as exc:
        assert "not allowed by your organization" in str(exc)
    else:
        raise AssertionError("expected RuntimeError")
