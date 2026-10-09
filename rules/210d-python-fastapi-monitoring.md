---
schema_version: v4.0
rule_version: v5.0.0
description: "Truthful FastAPI health/latency metrics, private correlated logs, safe cache boundaries, and thread/stream lifecycle."
last_updated: 2026-10-07
keywords:
  - kw:FastAPI health endpoints
  - kw:correlation ID middleware
  - kw:structured JSON logging
  - kw:Redis caching layer
  - kw:MetricsMiddleware performance tracking
  - kw:sensitive data sanitization
  - kw:fastapi
token_budget: ~1350
context_tier: Medium
depends:
  required:
    - 210-python-fastapi-core.md
---
# FastAPI Monitoring and Performance

## Scope

**What This Rule Covers:**
Health, resource/latency/error metrics, safe tracing/logging, cache correctness, connection budgets and async/thread/stream observability.

**When to Load This Rule:**
When adding or diagnosing FastAPI monitoring/performance. Read `207-python-logging.md` for logging and `210b-python-fastapi-testing.md` for integration tests.

## Contract

### Inputs and Prerequisites

- Existing instrumentation/middleware/health/metrics, platform collectors, app lifespan and actual async/client interfaces.
- Agreed SLA/error/resource targets, traffic baseline, metric grain, privacy/retention, approved exporter destination and monitoring scope.
- Cache eligibility/authorization/freshness/invalidation contract and measured bottleneck, if caching is proposed.

### Mandatory

- Inspect existing collectors/metrics/error tracking and ops log format; extend rather than duplicate middleware or initialize exporters twice. No new Redis/structlog/Sentry/Prometheus requirement merely to satisfy a checklist.
- Probes distinguish liveness from readiness with bounded actual dependency checks. Return appropriate unhealthy status, don't leak dependency errors/public system details, and avoid turning a transient database outage into endless process restarts.
- Log structured permitted fields with trusted/validated bounded correlation IDs and task-local context cleanup. Never trust arbitrary client-provided IDs for authority; propagate correlation through actual downstream calls without high-cardinality metric labels.
- Keep passwords, tokens, raw bodies, sensitive URL queries, PII and error trace values out of default logs. Shallow key redaction is insufficient for nested/case-varied data; prefer an explicit field allowlist and privacy-approved error capture.
- Do not read/buffer entire request or streaming response solely for logging. Use nonintrusive ASGI instrumentation where needed; imported BaseHTTPMiddleware belongs to Starlette, not an invented fastapi.middleware.base module.
- Measure durations with a monotonic clock. Define response-start versus full streamed-body completion; a call_next return is not complete stream duration. Count exceptions/cancellations and status outcomes in finally/send interception without swallowing errors.
- Metric labels use bounded route templates/method/status classes, not user IDs/full paths/query strings. Aggregate histogram/counter windows and percentiles correctly across workers; a single log entry isn't Prometheus collection or an exposed /metrics endpoint.
- Derive warning/critical thresholds from SLA, baseline/minimum volume and agreed error budget; no universal 1%/5%/two-second/95%-memory values. Separate no-data/monitor failure from zero requests/errors. Autoscale/restart/pool changes require explicit policy, not implicit action from a threshold.
- Profile before caching. Cache only eligible idempotent results, with stable serialized keys including tenant/user/permission/version/query boundaries and invalidation policy. Do not hash repr(args/kwargs) containing sessions/secrets or share personalized results across callers.
- Distinguish cache miss from valid false/zero/empty values. Bound memory/TTL/cardinality, handle concurrent misses and invalidate after writes; arbitrary 300 seconds or >100ms does not establish suitability. Avoid caching tokens, errors, or private data outside approved storage.
- Cache failures can use defined fallback with observable sanitized errors, not silent broad exception swallowing. Redis is optional; if used initialize/close async clients in lifespan and test failure/timeout/invalidation behavior.
- Budget database/client pools across workers/replicas and monitor wait/checked-out/leak/slow-query metrics. Increase capacity only after diagnosis; debug SQL echo can expose data. Async event-loop blocking and task accumulation need separate metrics.
- For thread-to-async/SSE capture the running loop before starting threads; use call_soon_threadsafe or supported thread-safe coroutine scheduling and bounded queues/backpressure. Never invoke asyncio.get_event_loop from a worker and assume it is the server loop.
- Streaming clients require disconnect/cancellation/error completion and cleanup; heartbeat isn't final success. Stop producers on disconnect and don't create unbounded background tasks/threads. Inspect observability overhead, event loss and protected endpoint access.
- Test metric/log/probe/cache behavior using synthetic outcomes, including failure/empty/idle/stream/cancel cases. Externally exporting logs/metrics or deploying alerts needs approved recipient/data boundaries.

### Execution Steps

1. Inventory existing probes/logs/metrics, privacy/SLA and measured bottlenecks without modifying collectors.
2. Implement minimal correct lifecycle-safe instrumentation and optional justified cache/pool improvements.
3. Verify timing/denominators/cardinality, redaction, probes, cache boundaries, and stream/thread cleanup in focused tests.
4. Run project validation and approved representative workload; compare latency/resource/collector overhead against baseline.
5. Report observed metrics, alert policy and unverified exporter/network/load behavior separately.

### Validation

- Probes and latency/error metrics reflect real checks/stages; failed/cancelled/streamed requests are not omitted.
- Correlation/context and allowed log fields avoid sensitive leakage and cross-request reuse; bounded labels preserve useful aggregation.
- Cache authorization/key/value/TTL/invalidation and outage behavior are correct; clients/threads/queues close under failure.
- Resource alerts/budgets are workload-based and approved; no automatic destructive repair or public metric endpoint.
- Output includes metric definitions, tests, before/after evidence and remaining runtime/collector gaps.

## References

- [FastAPI middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Starlette middleware constraints](https://www.starlette.io/middleware/)
- [Python logging](https://docs.python.org/3/library/logging.html)
- [Asyncio thread-safe scheduling](https://docs.python.org/3/library/asyncio-dev.html#concurrency-and-multithreading)
- [Redis async lifecycle](https://redis-py.readthedocs.io/en/stable/examples/asyncio_examples.html)
- [Prometheus instrumentation practices](https://prometheus.io/docs/practices/instrumentation/)
