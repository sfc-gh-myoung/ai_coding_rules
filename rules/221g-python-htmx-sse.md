---
schema_version: v4.0
rule_version: v5.0.0
description: "Authenticated SSE with explicit event formats, bounded replay/backpressure, thread-safe publication and client/server cleanup."
last_updated: 2026-10-07
keywords:
  - kw:HTMX SSE extension
  - kw:Alpine.js SSE manager
  - kw:event type matching
  - kw:thread-safe SSE publishing
  - kw:EventSourceResponse
  - kw:SSE connection limits
token_budget: ~1200
context_tier: High
depends:
  optional:
    - 221f-python-htmx-integrations.md  # Alpine.js patterns
---
# HTMX SSE Patterns (Python)

## Scope

**What This Rule Covers:**
Extension/manager stream ownership, HTML versus JSON event contracts, authentication/replay, bounded async/thread producers and teardown.

**When to Load This Rule:**
When implementing/debugging HTMX SSE. Read `221-python-htmx-core.md` for security/client contracts and frontend integration companion for lifecycle.

## Contract

### Inputs and Prerequisites

- Existing SSE endpoints/manager/extension/library versions, actual HTTP transport/proxy, event schemas/consumers and documentation owner.
- Trusted user/resource authorization, approved data/transmission scope, replay/terminal policy, queue/concurrency/time budgets and producer lifecycle.

### Mandatory

- Inspect existing streams and event docs; reuse one intentional connection/owner per logical subscription. HTMX SSE extension can serve multiple descendants; an Alpine manager is optional for custom routing, not mandatory for multiple targets. No duplicate subscriptions on the same component.
- Use text/event-stream framing with supported library and exact named event schemas. sse-swap inserts event data as HTML, so send safe rendered HTML; JSON events require explicit parsing/rendering or trigger a separate authorized HTML fetch. Do not swap raw JSON as if it were a fragment.
- Match backend event names and documented extension sse:name triggers; ordinary htmx.trigger custom names follow their own event contract. camelCase is convention. Heartbeat is connection liveness, not operation completion.
- Native EventSource cannot set arbitrary Authorization headers. Prefer approved same-origin secure session cookies or a reviewed fetch-stream client for header auth; don't put bearer JWTs in query URLs by default, even short-lived ones. If a scoped single-use stream ticket is required, review expiry/log/referrer exposure explicitly.
- Authenticate and authorize each stream/resource and filter emitted events per trusted user/tenant; don't broadcast private data to a global queue. Handle credential expiry/revocation with defined reconnect policy. Cookie cross-origin credentials/CORS and CSRF where applicable need explicit design.
- Bound concurrent streams, output/event bytes, producer queues and subscriber backlog. HTTP/1.1 browser connection limits differ from negotiated HTTP/2 streams; no hard universal six-connection failure formula or safe three-connection promise. Multiplex only compatible authorized subscriptions.
- Document event ID/retry/replay/retention semantics. EventSource auto-reconnect doesn't recover lost data without server replay; use Last-Event-ID/durable source with safe duplicate handling when required. Reconnection mustn't restart side-effectful work or create duplicate jobs.
- Capture asyncio.get_running_loop before threads, use call_soon_threadsafe/run_coroutine_threadsafe as appropriate and a bounded queue. put_nowait can fail after scheduling; handle QueueFull/backpressure/coalescing/durable retention deliberately, not an unbounded callback.
- Supervise producer and consumer together; producer failure must deliver safe terminal failure or cancel stream, not leave queue.get hanging forever. asyncio.to_thread cancellation doesn't forcibly stop work; use cooperative stop and bounded shutdown where needed.
- Handle disconnect/cancellation with idempotent cleanup of tasks, subscriptions, client EventSource and thread resources. Don't suppress cancellation then claim success or emit duplicate cleanup/error side effects. No raw exception.message in public error events.
- Provide explicit running/completed/failed/cancelled event states. Close client on terminal result before auto-reconnect and distinguish transport onerror from an application event named error. Disable proxy buffering/cache where actual streaming requires, with authorized configuration.
- Browser manager retains/removes listeners/connection handles on swap/unmount; missing element or malformed event is a defined failure. Test event naming, partial/reconnect/duplicates/expiry, slow subscriber and server cleanup; buffered in-process tests don't prove chunk timing.
- Record channel path, event/payload/HTML format, authorization, terminal/replay and lifecycle in existing docs; no mandatory new docs/SSE_EVENTS.md when another owner exists. Installing sse-starlette/Flask-SSE/gevent or switching framework is separate approval, not inherent SSE requirement.

### Execution Steps

1. Inspect producer/client/events/auth/proxy and choose one subscription/replay/data-format contract.
2. Implement scoped stream with safe event framing, bounded producer/backpressure and supervised terminal/cancellation handling.
3. Test finite fixtures/thread failures and approved browser reconnect/expiry/swap/slow-client cases.
4. Verify cleanup, event docs and project checks; report transport/runtime gaps separately.

### Validation

- Actual client data format/event names match secure server scope; credentials aren't exposed in URLs/logs.
- Queue/stream/replay/concurrency limits and failure/terminal handling preserve data without duplicate jobs.
- Disconnect/producer error/cancel closes resources and stops inappropriate reconnect; thread behavior bounded.
- Browser/real transport evidence separate from parser fixtures; no assumed live success or new package/deployment.

## References

- [HTMX SSE extension](https://htmx.org/extensions/sse/)
- [WHATWG EventSource](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [Asyncio thread interaction](https://docs.python.org/3/library/asyncio-dev.html#concurrency-and-multithreading)
- [sse-starlette](https://github.com/sysid/sse-starlette)
