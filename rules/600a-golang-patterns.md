---
schema_version: v4.0
rule_version: v3.0.0
description: "Advanced Go patterns for production services including HTTP server configuration, middleware chains, graceful shutdown, database access patterns, and server hardening."
last_updated: 2026-10-06
keywords:
  - kw:http.Server timeouts
  - kw:graceful shutdown
  - kw:middleware chain composition
  - kw:database connection pooling
  - kw:context-aware queries
  - kw:signal handling SIGTERM
  - kw:taskfile
token_budget: ~900
context_tier: Low
depends:
  required:
    - 600-golang-core.md  # Core Go patterns and conventions
  optional:
    - 820-taskfile-automation.md
---
# Go Patterns: HTTP Services and Production Readiness

## Scope

**What This Rule Covers:**
HTTP timeouts/TLS, middleware, graceful shutdown, context-aware SQL and bounded connection pools.

**When to Load This Rule:**
When building/reviewing Go HTTP services, shutdown lifecycle, middleware or database access.

## Contract

### Inputs and Prerequisites

- Actual Go/core guidance, existing server/router/middleware/database driver and workload.
- Timeout/streaming/proxy/TLS requirements, deployment signal/lifecycle and safe test environment.

### Mandatory

- Configure deliberate header/read/write/idle limits; blanket fixed WriteTimeout can break SSE/long streaming. Choose limits from real workload/edge proxy behavior and test cancellation/resource bounds.
- Handle server errors and http.ErrServerClosed explicitly, never log.Fatal in worker goroutines or expected shutdown where defers/cleanup must run.
- Graceful shutdown needs signal notification cleanup, bounded shutdown context and coordination that waits for Shutdown completion before main exits. Active hijacked/WebSocket sessions require separate lifecycle handling.
- Middleware order must deliberately cover required panic/log/auth paths. net/http already recovers many handler panics; do not falsely claim auth panic necessarily crashes the process. Custom recovery is a controlled response/log boundary with safe redaction and no duplicate response write.
- Preserve handler interfaces/streaming semantics when wrapping ResponseWriter; track status/bytes accurately and no secrets in request logs.
- Propagate request context into SQL/network operations, bind query values, handle ErrNoRows, close rows and check iteration errors.
- sql.DB is a shared pool; close only at its ownership lifecycle, not per request. Set measured pool/idle/lifetime policy and verify connectivity with PingContext when startup requires, not assuming sql.Open establishes a connection.
- TLS/cert paths/minimum policy reflect actual deployment; secrets/certs never embedded. Proxy trust/header/auth/health behavior explicit.
- Test actual failures/cancellation/concurrency/streaming with safe owned processes; do not pgrep/kill all matching servers or run unapproved load/DoS tests.

### Execution Steps

1. Inspect current server/router/middleware/pool and deployment timeout/signal requirements.
2. Implement scoped explicit timeout/TLS/context policy and ownership-aware resource initialization.
3. Coordinate start/error/shutdown paths so all owned workers/connections stop or drain before exit.
4. Validate middleware/auth/recovery/log order and ResponseWriter capabilities against actual streaming needs.
5. Run focused integration/race tests for requests, SQL errors, timeout/cancellation and shutdown in-flight work; real load testing only when approved.

### Validation

- Timeouts prevent actual resource exposure without breaking supported streaming; TLS/auth policy tested.
- SIGINT/SIGTERM/normal errors drain and clean resources, main waits for completion, no Fatal cleanup bypass.
- Middleware logs/status/panic behavior correct, no secret leak or incompatible writer wrapper.
- Pool limits/context/query binds/rows lifecycle and ErrNoRows behavior verified.
- Race/integration tests scope real; missing deployed/load checks explicitly unverified.

## References

- [Go net/http](https://pkg.go.dev/net/http)
- [Go database/sql](https://pkg.go.dev/database/sql)
- [Go os/signal](https://pkg.go.dev/os/signal)
- [Go TLS](https://pkg.go.dev/crypto/tls)
- [Go race detector](https://go.dev/doc/articles/race_detector)
