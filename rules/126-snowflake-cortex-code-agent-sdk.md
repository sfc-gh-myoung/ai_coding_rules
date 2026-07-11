# Snowflake Cortex Code Agent SDK Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential patterns for building agentic apps with the
> Cortex Code Agent SDK in TypeScript and Python. Load for any task that uses
> `cortex-code-agent-sdk` (npm or PyPI) or the `cortex` CLI as a subprocess.

## Metadata

**SchemaVersion:** v3.3
**RuleVersion:** v1.0.3
**LastUpdated:** 2026-07-10
**Keywords:** kw:agent sdk, kw:mcp server, kw:mcp servers, kw:cortex-code, kw:agent hooks, kw:structured output, kw:streaming output, kw:streaming input, kw:system prompts, kw:agent typescript, kw:agent python
**TokenBudget:** ~5050
**ContextTier:** High
**Depends:** required:100-snowflake-core.md, optional:115-snowflake-cortex-agents-core.md, optional:117-snowflake-mcp-server.md, optional:118-snowflake-cortex-rest-api.md

## Scope

**What This Rule Covers:**
Best practices for building agentic AI applications with the Cortex Code Agent SDK
(`cortex-code-agent-sdk` npm and PyPI packages) including session lifecycle, system
prompts, streaming I/O, hooks, `canUseTool` permissions, MCP server connections,
and structured output. Status: PREVIEW.

**When to Load This Rule:**
- Building Node.js or Python apps that import `cortex-code-agent-sdk`
- Wiring `query()`, `createCortexCodeSession()`, or `CortexCodeSDKClient`
- Configuring hooks, `canUseTool`, MCP servers, or structured output
- Migrating from raw CLI invocations to the SDK

**This rule does NOT cover:**
- Server-side `CREATE CORTEX AGENT` DDL — see `115-snowflake-cortex-agents-core.md`
- Snowflake-managed MCP server configuration — see `117-snowflake-mcp-server.md`
- Direct REST/SSE clients without the SDK — see `118-snowflake-cortex-rest-api.md` and `118a-snowflake-cortex-rest-api-streaming.md`

> **Investigation Required**
> Before writing SDK code, verify:
> - [ ] Cortex Code CLI installed: `cortex --version`
> - [ ] `~/.snowflake/connections.toml` (or `config.toml`) has a working connection
> - [ ] Node 18+ (TS) or Python 3.10+ (Python)
> - [ ] If CLI not on PATH, `CORTEX_CODE_CLI_PATH` is set or `cli_path`/`cliPath` is passed

## References

### Dependencies

**Must Load First:**
- **100-snowflake-core.md** - Snowflake foundation patterns

**Related:**
- **115-snowflake-cortex-agents-core.md** - Server-side `CREATE CORTEX AGENT` DDL agents
- **117-snowflake-mcp-server.md** - Snowflake-managed MCP server (different scope)
- **118-snowflake-cortex-rest-api.md** - REST clients without the SDK

### External Documentation

- [Cortex Code Agent SDK overview](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/cortex-code-agent-sdk)
- [TypeScript reference](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/typescript-reference)
- [Python reference](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/python-reference)
- [System prompts](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/system-prompts)
- [Streaming input / multi-turn sessions](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/streaming-input)
- [Streaming output](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/streaming-output)
- [Structured output](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/structured-output)
- [Hooks](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/hooks)
- [User input and approvals (`canUseTool`)](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/user-input)
- [MCP servers](https://docs.snowflake.com/en/user-guide/cortex-code-agent-sdk/mcp-custom-tools)

## Contract

### Inputs and Prerequisites

- Cortex Code CLI on PATH (or `CORTEX_CODE_CLI_PATH` set)
- Snowflake CLI connection in `~/.snowflake/connections.toml` (or `config.toml`)
- Node.js 18+ (TypeScript SDK is ESM-only) OR Python 3.10+
- Role with Cortex privileges and access to any objects the agent will touch

### Mandatory

- Use the SDK's typed message dispatch (`message.type === "assistant" | "result" | "stream_event"`)
- Always handle the terminal `ResultMessage` and inspect `is_error` / `subtype`
- Pin model with `model: "auto"` or an explicit identifier; never hardcode an unpinned default
- Provide a `canUseTool` callback whenever a permission-checked tool may be reached — without it the request fails
- Append to the default system prompt (`{type: "preset", append: "..."}` or `appendSystemPrompt`) instead of replacing it, unless you have a clear reason to remove built-in tool guidance
- Validate structured output against the same schema you sent (Zod `safeParse` or Pydantic `model_validate`); the SDK validates JSON Schema, but your app should still parse defensively
- Close sessions: `await session.close()` (TS) or `await client.disconnect()` / async `with` (Python)

### Forbidden

- `permissionMode: "bypassPermissions"` without `allowDangerouslySkipPermissions: true` (the safety flag is required) — and never enable bypass in user-facing or production code paths
- Embedding secrets, API keys, or PII in `systemPrompt` / `appendSystemPrompt`
- Passing untrusted user input directly into `extraArgs` / `extra_args`, `mcp_servers` headers, or shell `command` fields
- Replacing the default system prompt unless you have explicitly accepted the loss of built-in tool usage guidance and safety guardrails
- Treating `StreamEvent` as the only output channel — complete tool calls and tool results still arrive as `AssistantMessage` and `UserMessage`

### Execution Steps

1. Install: `npm install cortex-code-agent-sdk` or `pip install cortex-code-agent-sdk`
2. Configure Snowflake connection in `~/.snowflake/connections.toml`
3. Pick the input pattern: single `query()` (one prompt), streamed input (async iterable), or multi-turn session
4. Configure `systemPrompt` (preset+append) and `model` (`"auto"` recommended)
5. Wire `canUseTool` (or `allowedTools`/`disallowedTools`) for permission policy
6. Register lifecycle hooks (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `UserPromptSubmit`, `Stop`, `SubagentStart`, `SubagentStop`, `PreCompact`, `Notification`, `PermissionRequest`) as needed. Note: `PermissionRequest` hooks can serve as an alternative to `canUseTool` for permission handling.
7. Iterate the async generator/iterator; dispatch by `message.type`; break on `ResultMessage`
8. For streaming UI: set `includePartialMessages` / `include_partial_messages = true` and handle `stream_event` deltas
9. For typed results: set `outputFormat`/`output_format` with a JSON Schema (generate from Zod/Pydantic)
10. Close the session and surface `ResultMessage.is_error`/`subtype` to the caller

### Output Format

Working SDK code (TypeScript or Python) plus configuration files
(`~/.snowflake/connections.toml`). Long-running interactive apps should use a
session; one-shot scripts should use `query()`.

### Validation

**Pre-Task-Completion Checks:**
- TypeScript: `tsc --noEmit` passes; ESM module resolution configured (`"type": "module"` or `.mts`)
- Python: `mypy` (or `ty`) passes; package installs cleanly into a `uv` / `venv` environment
- Smoke test: a one-prompt `query()` returns a `ResultMessage` with `is_error: false`
- Permission policy review: `canUseTool` covers `Write`, `Bash`, `Edit`, and any `mcp__*` tools you expose
- Session cleanup verified: no orphan `cortex` CLI subprocesses after the test exits

**Success Criteria:**
- Agent completes the prompt and emits a non-error `ResultMessage`
- All tool calls pass through the configured permission policy
- Structured output (when used) round-trips through Zod / Pydantic without warnings
- No secrets in logs or system prompts

### Design Principles

- **One CLI process per session.** Multi-turn sessions reuse the same CLI subprocess; do not spin up a fresh `query()` per turn when context matters.
- **`canUseTool` is opt-in but required for production.** The SDK does not prompt interactively; without a callback, permission-checked requests fail.
- **Hooks vs. `canUseTool`:** `canUseTool` is the simpler approach for allow/deny on a single permission event; hooks cover 10 lifecycle events and `PermissionRequest` hooks can also handle allow/deny decisions (via `hookSpecificOutput.decision.behavior`). Use `canUseTool` for straightforward permission policy; use hooks for audit logging, input rewriting, post-execution side effects, and broader lifecycle observation.
- **Append, don't replace.** Replacing the system prompt drops built-in tool usage guidance and safety guardrails — append instead unless you accept the trade-off.
- **Stream when you have a UI.** `includePartialMessages` produces `text_delta` events for UX; otherwise let messages arrive as complete `AssistantMessage`s.
- **Cap turns and effort.** Set `maxTurns` / `max_turns` and `effort` to bound cost; expect `error_max_turns` as a real outcome, not a bug.

### Post-Execution Checklist

- [ ] CLI version and SDK version recorded for reproducibility
- [ ] `connection` set explicitly (not relying on `default_connection_name` in production)
- [ ] `canUseTool` defined or `allowedTools`/`disallowedTools` covers all reachable tools
- [ ] Hooks return `{}` (no-op), `{decision: "block", reason}`, or a documented `hookSpecificOutput`
- [ ] Structured output schemas validated (Zod / Pydantic) on the consumer side
- [ ] Sessions closed (`session.close()` / `client.disconnect()` / `async with`)
- [ ] No secrets, PII, or internal hostnames in `systemPrompt`

## Canonical Snippets

### Single-prompt query (entry point)

```ts
// TypeScript
import { query } from "cortex-code-agent-sdk";

for await (const msg of query({
  prompt: "Summarize this codebase in one paragraph.",
  options: { cwd: process.cwd(), model: "auto", connection: "my-connection" },
})) {
  if (msg.type === "assistant") {
    for (const b of msg.content) if (b.type === "text") process.stdout.write(b.text);
  }
  if (msg.type === "result") {
    if (msg.is_error) console.error("Agent error:", msg.subtype, msg.result);
    break;
  }
}
```

```python
# Python
import asyncio
from cortex_code_agent_sdk import query, AssistantMessage, ResultMessage, CortexCodeAgentOptions

async def main():
    async for msg in query(
        prompt="Summarize this codebase in one paragraph.",
        options=CortexCodeAgentOptions(cwd=".", model="auto", connection="my-connection"),
    ):
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if hasattr(b, "text"): print(b.text, end="")
        elif isinstance(msg, ResultMessage):
            if msg.is_error: print(f"\nAgent error: {msg.subtype}")
            break

asyncio.run(main())
```

### System prompt (append, don't replace)

```ts
const session = await createCortexCodeSession({
  cwd: process.cwd(),
  appendSystemPrompt: "Focus on Python files. Always run pytest after edits.",
});
```

```python
options = CortexCodeAgentOptions(
    cwd=".",
    system_prompt={"type": "preset", "append": "Focus on Python files. Always run pytest after edits."},
)
```

### Multi-turn session

```ts
import { createCortexCodeSession } from "cortex-code-agent-sdk";

const session = await createCortexCodeSession({ cwd: process.cwd() });
try {
  await session.send("Read the auth module");
  for await (const e of session.stream()) if (e.type === "result") break;

  await session.send("Now find every caller of it");
  for await (const e of session.stream()) if (e.type === "result") break;
} finally {
  await session.close();
}
```

```python
from cortex_code_agent_sdk import CortexCodeSDKClient, CortexCodeAgentOptions

async with CortexCodeSDKClient(CortexCodeAgentOptions(cwd=".")) as client:
    await client.query("Read the auth module")
    async for _ in client.receive_response(): pass
    await client.query("Now find every caller of it")
    async for _ in client.receive_response(): pass
```

### Streaming output (token-level deltas)

```ts
for await (const msg of query({
  prompt: "Explain how databases work",
  options: { cwd: process.cwd(), includePartialMessages: true },
})) {
  if (msg.type === "stream_event") {
    const e = msg.event;
    if (e.type === "content_block_delta" && e.delta.type === "text_delta") {
      process.stdout.write(e.delta.text);
    }
  }
}
```

```python
async for msg in query(
    prompt="Explain how databases work",
    options=CortexCodeAgentOptions(cwd=".", include_partial_messages=True),
):
    if hasattr(msg, "event"):
        e = msg.event
        if e.get("type") == "content_block_delta" and e["delta"].get("type") == "text_delta":
            print(e["delta"]["text"], end="")
```

### Structured output (Zod / Pydantic)

```ts
import { z } from "zod";

const Plan = z.object({
  feature: z.string(),
  steps: z.array(z.object({ n: z.number(), text: z.string() })),
});

for await (const msg of query({
  prompt: "Plan dark-mode support.",
  options: { cwd: ".", outputFormat: { type: "json_schema", schema: z.toJSONSchema(Plan) } },  // z.toJSONSchema() requires Zod v4+; for Zod v3, use zodToJsonSchema(Plan) from 'zod-to-json-schema'
})) {
  if (msg.type === "result" && msg.subtype === "success" && msg.structured_output) {
    const parsed = Plan.safeParse(msg.structured_output);
    if (!parsed.success) throw new Error("Schema mismatch");
    console.log(parsed.data);
  }
}
```

```python
from pydantic import BaseModel

class Step(BaseModel):
    n: int
    text: str

class Plan(BaseModel):
    feature: str
    steps: list[Step]

async for msg in query(
    prompt="Plan dark-mode support.",
    options=CortexCodeAgentOptions(
        cwd=".",
        output_format={"type": "json_schema", "schema": Plan.model_json_schema()},
    ),
):
    if isinstance(msg, ResultMessage) and msg.subtype == "success" and msg.structured_output:
        plan = Plan.model_validate(msg.structured_output)
        print(plan.feature)
```

### Hooks: block destructive Bash + audit log

```ts
hooks: {
  PreToolUse: [{
    matcher: "Bash",
    hooks: [async (input) => {
      const cmd = String((input.tool_input as any)?.command ?? "");
      if (/\brm\s+-rf\b|DROP\s+TABLE/i.test(cmd)) {
        return { decision: "block", reason: "Destructive command blocked" };
      }
      return {};
    }],
  }],
  PostToolUse: [{
    hooks: [async (input) => {
      console.log(JSON.stringify({ ts: Date.now(), tool: input.tool_name, sid: input.session_id }));
      return {};
    }],
  }],
}
```

```python
from cortex_code_agent_sdk import HookMatcher

async def block_destructive(input_data, tool_use_id, context):
    cmd = (input_data.get("tool_input") or {}).get("command", "")
    if "rm -rf" in cmd or "DROP TABLE" in cmd.upper():
        return {"decision": "block", "reason": "Destructive command blocked"}
    return {}

options = CortexCodeAgentOptions(
    hooks={"PreToolUse": [HookMatcher(matcher="Bash", hooks=[block_destructive], timeout=30.0)]},
)
```

### `canUseTool` permission callback

```ts
canUseTool: async (toolName, input) => {
  if (toolName === "Write" && String((input as any).resource ?? "").endsWith(".env")) {
    return { behavior: "deny", message: "Editing .env is not allowed" };
  }
  if (["Read", "Glob", "Grep"].includes(toolName)) return { behavior: "allow" };
  return { behavior: "deny", message: "Tool not in allowlist" };
}
```

```python
from cortex_code_agent_sdk import PermissionResultAllow, PermissionResultDeny

async def can_use_tool(tool_name, tool_input, context):
    if tool_name == "Write" and str(tool_input.get("resource", "")).endswith(".env"):
        return PermissionResultDeny(message="Editing .env is not allowed")
    if tool_name in {"Read", "Glob", "Grep"}:
        return PermissionResultAllow()
    return PermissionResultDeny(message="Tool not in allowlist")
```

### External MCP server

```ts
mcpServers: {
  "my-tools": { command: "node", args: ["my-mcp-server.js"] },
  "remote-api": {
    type: "http",
    url: "https://mcp.example.com/mcp",
    headers: { Authorization: `Bearer ${process.env.MCP_TOKEN}` },
  },
},
allowedTools: ["mcp__my-tools__*"],
```

```python
options = CortexCodeAgentOptions(
    mcp_servers={
        "my-tools": {"command": "node", "args": ["my-mcp-server.js"]},
        "remote-api": {
            "type": "http",
            "url": "https://mcp.example.com/mcp",
            "headers": {"Authorization": f"Bearer {os.environ['MCP_TOKEN']}"},
        },
    },
    allowed_tools=["mcp__my-tools__*"],
)
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Bypassing permissions silently

**Problem:** Setting `permissionMode: "bypassPermissions"` without the safety flag, or shipping bypass to production.

**Why it fails:** The SDK rejects bypass without `allowDangerouslySkipPermissions: true`. Even when set, bypass disables every permission check — including writes, shell, and MCP tools. Production agents need an auditable policy.

**Correct Pattern:**
```ts
// Sandboxed CI only
{ permissionMode: "bypassPermissions", allowDangerouslySkipPermissions: true }

// Production: explicit canUseTool + allowlist
{ allowedTools: ["Read", "Glob", "Grep"], canUseTool: myPolicy }
```

### Anti-Pattern 2: Replacing the default system prompt by accident

**Problem:** Passing a string to `systemPrompt` thinking it appends.

**Why it fails:** A bare string fully replaces the built-in prompt — losing tool usage guidance and safety guardrails. The agent then mis-uses tools or refuses to call them.

**Correct Pattern:**
```ts
// Append (preserves built-ins)
{ appendSystemPrompt: "Focus on Python files." }
// or
{ systemPrompt: { type: "preset", append: "Focus on Python files." } }
```

### Anti-Pattern 3: Treating `StreamEvent` as the only message channel

**Problem:** Filtering only on `message.type === "stream_event"` and ignoring `assistant` / `user` / `result`.

**Why it fails:** Complete tool calls arrive as `AssistantMessage` blocks and tool results arrive as `UserMessage` blocks — never as `StreamEvent`. The agent appears to "skip" tool execution because the consumer drops those messages.

**Correct Pattern:**
```ts
for await (const msg of query({ prompt, options: { includePartialMessages: true } })) {
  switch (msg.type) {
    case "stream_event": /* render delta */ break;
    case "assistant":    /* tool_use blocks */ break;
    case "user":         /* tool_result blocks */ break;
    case "result":       /* terminal */ return;
  }
}
```

### Anti-Pattern 4: Leaking secrets into the system prompt

**Problem:** Embedding API keys, PATs, or PII inside `appendSystemPrompt` to "pass them to the agent."

**Why it fails:** The system prompt is sent to the model on every turn, logged on the CLI side, and may surface in error messages or transcripts. Anything in the prompt should be treated as published data.

**Correct Pattern:** Pass secrets via `env` (process env vars the agent can read at tool time), MCP server `headers`, or external secret stores. Reference them by name in the prompt.

### Anti-Pattern 5: Per-turn `query()` instead of a session

**Problem:** Calling `query()` in a loop for a multi-turn chat.

**Why it fails:** `query()` manages a fresh session lifecycle each call — no shared context, slower startup, no `setPermissionMode`/`setModel` mid-conversation.

**Correct Pattern:** Use `createCortexCodeSession()` (TS) or `CortexCodeSDKClient` (Python) for any conversation requiring context across turns.

### Anti-Pattern 6: Forgetting to bound cost

**Problem:** No `maxTurns`, no `effort`, no abort signal.

**Why it fails:** A confused agent can loop until it hits internal limits — burning credits and clock time. `error_max_turns` is a normal failure mode you should plan for.

**Correct Pattern:**
```ts
{ maxTurns: 10, effort: "medium", abortController: new AbortController() }
```

### Anti-Pattern 7: Hooks that never return

**Problem:** Hook callbacks that block on user input or external services without a timeout.

**Why it fails:** Each hook matcher has a default timeout of 60s; exceeding it stalls the agent. Hooks should be fast and return a documented output object.

**Correct Pattern:** Set an explicit `timeout` on the matcher; return `{}` for no-op, `{decision: "block", reason}` to halt the operation, or a `hookSpecificOutput` for input rewriting / context injection.
