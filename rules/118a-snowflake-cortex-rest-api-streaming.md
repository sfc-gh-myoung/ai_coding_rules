---
schema_version: v4.0
rule_version: v5.1.0
description: "Endpoint-specific Cortex REST authentication, response detection, SSE framing, completion checks, and safe interrupted-stream handling."
last_updated: 2026-10-08
keywords:
  - kw:Cortex REST authentication
  - kw:server-sent events
  - kw:SSE stream parsing
  - kw:Cortex Agent streaming
  - kw:PAT token headers
  - kw:response format detection
token_budget: ~1350
context_tier: High
depends:
  required:
    - 118-snowflake-cortex-rest-api.md  # Core REST API patterns (retry, idempotency, cost controls)
  optional:
    - 115-snowflake-cortex-agents-core.md  # Cortex Agents REST API
---
# Snowflake Cortex REST API: Authentication and Streaming

## Scope

**What This Rule Covers:**
Documented token/header selection, JSON versus SSE detection, event framing/dispatch, stream completeness, and bounded recovery without duplicate effects.

**When to Load This Rule:**
When authenticating Cortex REST calls, consuming SSE, or diagnosing parser/stream failures. Read `115-snowflake-cortex-agents-core.md` for Agent configuration and tool authorization.

## Contract

### Inputs and Prerequisites

- Exact operation/version, account URL, supported auth method, installed HTTP/SSE client, and request/response schemas.
- Authorized identity/data/tool scope and approved credential retrieval; no private connector attribute extraction or credential values in examples/logs.
- Stream event schema, terminal condition, timeout/cancellation/size budgets, and explicit retry/resume policy.

### Mandatory

- Verify PAT, OAuth, or key-pair JWT support on the target operation. Set Bearer authorization and X-Snowflake-Authorization-Token-Type when required: PROGRAMMATIC_ACCESS_TOKEN, OAUTH, or KEYPAIR_JWT as appropriate. Do not infer auth success from constructing headers.
- Never use private connector session-token attributes as a credential API. The inference documentation describes a session-token expiration case; this does not establish support for all REST endpoints. Prefer documented authentication and do not promise a universal 390303 rejection.
- Inspect HTTP status and bounded/sanitized application errors, then normalize Content-Type before selecting JSON or text/event-stream. Reject unexpected types; never call response.json() on an SSE body. Transport stream=True does not itself enable endpoint streaming.
- For object-backed Agents use the documented database/schema/agent run route and typed messages; inline Agent runs have a distinct route/configuration. Do not flatten an FQN into an invented URL or reuse question/max_tokens payloads from unrelated APIs.
- Agent run streaming defaults to true; stream=false requests a single JSON response. Confirm the exact operation's contract rather than treating every Cortex endpoint as always-SSE.
- Prefer an existing compatible SSE parser; adding a package requires normal dependency approval. A manual parser must handle UTF-8 split across chunks, CR/LF variants, blank-line dispatch, multiple data fields joined with newlines, comments/heartbeats, event type, and optional id/retry fields. Preserve payload whitespace apart from the protocol's optional single space after a colon.
- Dispatch complete framed events, not individual network chunks or data lines. An event need not start with data:. Comments are not completion; an unterminated final event is not an implicitly successful response. Bound both event and accumulated output size.
- Decode JSON per event only when its schema requires JSON. Recognize documented sentinels and typed error events before generic decoding. Unknown event types may be ignored or retained under an explicit policy; malformed required events must fail/report incomplete output, not silently disappear.
- For Agents, response.text.delta contains answer text; response.thinking.delta is not user-visible answer text. The final response event aggregates prior events. Avoid duplicate rendering and inspect final warnings/tool-access omissions. Do not invent a generic done/content field shared across endpoints.
- A clean connection close or HTTP 200 is not proof of completion. Require the endpoint's documented terminal event/condition; distinguish completed, failed, cancelled, and interrupted output. Retain partial output as partial, not a complete answer.
- Do not reconnect/replay a streamed POST after partial output automatically. Event IDs/retry fields do not prove endpoint resume support; verify server recovery semantics and tool-effect idempotency first. Apply the parent's bounded backoff only to replay-safe requests.
- Configure connect/read inactivity and total stream deadlines; support cancellation, close connections in finally/context managers, and clean up clients. Do not expose raw events, prompts, errors, or tokens in logs by default.

### Execution Steps

1. Read the target auth/run specification and existing client; identify exact headers, request shape, format, event types, and terminal condition.
2. Configure approved credential access, timeouts, bounded response parsing, event dispatch, and cleanup without sending a live request by default.
3. Exercise local fixtures for chunking, framing, content detection, malformed/error/unknown events, cancellation, and premature EOF.
4. Run a paid/live auth/stream canary only when authorized; record real completion and warning behavior separately from local fixture results.
5. Report code/configuration, output completeness, replay policy, and unresolved endpoint/account compatibility.

### Validation

- Auth method/header mapping and endpoint/request schemas match primary docs; private session-token extraction and credential logging are absent.
- JSON/SSE detection handles Content-Type parameters; fragmented UTF-8, multiline data, comments, and empty delimiters parse correctly.
- Error/malformed required events, timeout, cancellation, and premature EOF do not become success or trigger unsafe repeated tool effects.
- Answer deltas, final response, warnings, and terminal state are checked without duplicated final text or exposed thinking.
- Stream/response/client cleanup and bounded buffers/deadlines pass tests. Live authentication and account capability remain unverified unless actually tested.

## References

- [REST authentication and token type headers](https://docs.snowflake.com/en/developer-guide/snowflake-rest-api/authentication)
- [Cortex inference endpoints and session-token caveat](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-rest-api)
- [Agent run paths, payloads, typed events, and final response](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-run)
- [WHATWG server-sent event parsing](https://html.spec.whatwg.org/multipage/server-sent-events.html#event-stream-interpretation)
- [Requests streaming and timeout behavior](https://requests.readthedocs.io/en/latest/user/advanced/)
