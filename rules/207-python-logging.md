---
schema_version: v4.0
rule_version: v5.0.0
description: "Best practices for Python logging in applications with dual output requirements (CLI and web UI), covering hierarchical logger names, handler configuration, Rich console integration, SSE/WebSocket"
last_updated: 2026-10-06
keywords:
  - kw:hierarchical logger names
  - kw:Rich console bridge
  - kw:WebLogHandler SSE
  - kw:operation-scoped handler attachment
  - kw:SUCCESS prefix pattern
  - kw:operation ID correlation
token_budget: ~1100
context_tier: High
depends:
  required:
    - 200-python-core.md  # Python foundation patterns
  optional:
    - 201-python-lint-format.md  # Code quality standards
    - 210-python-fastapi-core.md  # FastAPI SSE streaming patterns
---
# Python Logging Best Practices

## Scope

**What This Rule Covers:**
Hierarchical loggers, handler lifecycle, CLI/web sinks, structured operation context, bounded streaming and safe diagnostics.

**When to Load This Rule:**
When configuring application logs, Rich console handlers, SSE/WebSocket streams or investigating duplicate/cross-operation entries.

## Contract

### Inputs and Prerequisites

- Existing logging configuration/consumers, actual Rich/structlog/formatter dependencies and privacy policy.
- Runtime concurrency/stream topology, expected log volume and approved storage/retention.

### Mandatory

- Inspect current logging.config/basicConfig/handlers/propagation and aggregation consumers before replacing configuration. Libraries use named loggers and do not configure application root handlers at import.
- Use logging for operational diagnostics; normal CLI result output may use print/stdout. Send CLI diagnostics/progress to stderr without contaminating JSON/result streams.
- Use hierarchical module names and deliberate propagation so each event reaches intended sinks once. Do not emit the same message through console.print and a console logger redundantly.
- Configure persistent app-level sinks at startup; attach temporary operation handlers only for the operation and remove/close in finally. Filter by actual operation/request context so concurrent operations do not cross-contaminate logs.
- Use operation IDs/structured context for correlation. SUCCESS is an application convention, not a standard Python level; adopt prefixes only if existing consumers require them, otherwise use a structured outcome field.
- Rich is optional unless declared required. Use actual supported RichHandler configuration and appropriate plain stdlib fallback without silent missing-dependency claims.
- logging.Handler already manages locking during handle; custom shared-state changes still need deliberate synchronization. Avoid lock inversion, recursively logging handler failures or blocking network I/O in emit; use queues for slow sinks.
- Async queues are not generally thread-safe; capture the event loop before background work and use thread-safe scheduling or a documented queue bridge.
- Bound buffers/retention by configured operational requirements, report dropped/truncated events and disconnections; do not invent universal handler-count/log-count limits or silently drop evidence.
- Redact secrets/private payloads, safely escape untrusted display content and restrict web-stream recipients. Logging to external services requires approved destinations/permissions.
- File logs rotate with actual configured retention; containers normally use runtime-managed stream logging. Do not claim arbitrary backup counts are mandatory or hard-code unverified production services.

### Execution Steps

1. Inspect configured loggers, propagation, sink/formatter dependencies and consumers.
2. Define levels/context/outcomes and one event path to intended CLI/web/file sinks.
3. Implement lifecycle-managed handlers and context filtering; preserve library/application configuration boundaries.
4. Add bounded asynchronous/queue delivery where needed and safe thread/event-loop bridges.
5. Test level filtering, no duplicates, concurrent operation isolation, handler teardown, exceptions, disconnect/backpressure and redaction.
6. Run actual Python validation and report sink/runtime checks separately from mocks/static inspection.

### Validation

- Hierarchical loggers and propagation produce one intended event per sink.
- Temporary handlers removed/closed, app-level handlers configured once, no library root mutation.
- Operation context isolates concurrent streams and actual IDs/retention/status remain accurate.
- emit thread/async behavior safe, no deadlock or unbounded memory/disk growth; drop/disconnect limits disclosed.
- Secrets redacted and external/web access scoped, CLI results/stdout unpolluted.
- Actual sinks and Rich/plain fallback tested where available; no fake success/runtime claims.

## References

- [Python logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Python logging cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [Python handler thread safety](https://docs.python.org/3/library/logging.html#thread-safety)
- [Rich logging](https://rich.readthedocs.io/en/stable/logging.html)
- [asyncio thread scheduling](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.call_soon_threadsafe)
