---
schema_version: v4.0
rule_version: v5.0.0
description: "FastAPI tests with correct sync/async clients, lifespan, isolated database/session state, restored overrides and behavior assertions."
last_updated: 2026-10-07
keywords:
  - kw:TestClient fixture
  - kw:dependency overrides
  - kw:pytest-asyncio configuration
  - kw:test database isolation
  - kw:AAA pattern enforcement
  - kw:httpx AsyncClient
token_budget: ~1350
context_tier: High
depends:
  required:
    - 210-python-fastapi-core.md  # FastAPI foundation patterns
  optional:
    - 200-python-core.md  # Python core testing patterns
    - 206-python-pytest.md  # Pytest patterns and best practices
---
# FastAPI Testing Strategies

## Scope

**What This Rule Covers:**
API success/error/security tests, sync versus async clients, lifespan/loop ownership, isolated persistence, dependency overrides, and bounded streaming verification.

**When to Load This Rule:**
When testing FastAPI routes/dependencies or configuring pytest clients/fixtures. Read `206-python-pytest.md` for suite conventions and `240a-python-faker-testing.md` for synthetic factories when needed.

## Contract

### Inputs and Prerequisites

- Existing application factory/lifespan, tests/config, actual FastAPI/Starlette/HTTPX and async-plugin versions, auth dependencies and persistence behavior.
- Intended API/output/status contract, isolated synthetic fixtures and test resource permission; no production database or external calls by default.
- Project async runner/loop scopes, cleanup, approved coverage target and relevant integration boundary.

### Mandatory

- Read conftest/config and match current fixture/AAA conventions; use factories when they remove meaningful duplication/variation, not fixed field/test-count thresholds. Keep deterministic readable synthetic inputs and no real sensitive customer data.
- TestClient is an HTTPX-based synchronous interface that can exercise async FastAPI routes from normal def tests; it is not based on requests and is not categorically invalid for async endpoints. Use HTTPX AsyncClient with ASGITransport for tests that themselves await async resources.
- Run TestClient as a context manager to exercise lifespan. AsyncClient/ASGITransport does not trigger lifespan automatically; use existing supported lifespan management for startup/shutdown without silently adding a dependency.
- Use installed pytest-asyncio or AnyIO configuration consistently. auto mode is optional for asyncio-only suites, not universally mandatory; strict markers/async fixture decorators and backend/loop scope must match chosen runner. Never let unawaited async fixtures pass as real sessions.
- Create loop-bound engines/clients inside the correct lifespan/async fixture. Do not share an AsyncSession across concurrent requests or another event loop through sync TestClient; align engine/session/fixture/runner scopes.
- Use a verified isolated disposable test database/schema with rollback or cleanup and worker-unique identities for parallel tests. A real isolated database is valid; production is not. SQLite alternatives cannot prove another dialect's constraints/types/transactions/migrations.
- Fixtures close sessions/clients and dispose engines in finally even on assertion/startup failure. Ensure committed application writes are actually rolled back/cleaned by the fixture strategy; no drop-all on an unverified connection.
- app.dependency_overrides keys must be the original dependency callable. Restore previous overrides in teardown, not leave mutated global state; prefer fresh app instances where supported. Override external integrations for unit tests without bypassing the auth behavior being tested.
- Cover intended methods/status/schema/headers and persisted side effects, not status 200 alone: valid create/read/update/delete, validation/missing/not-found/conflict and transaction error paths where applicable. Test no password/hash/token leakage and omitted-versus-NULL updates.
- Test authenticated allow and missing/invalid/expired/wrong-purpose credentials, active-user state, tenant/resource ownership, role denial and refresh replay when implemented. Don't rely solely on fabricated token headers or overriding get_current_user for auth integration tests.
- Mock at actual external boundary with async-aware doubles and assert payload/timeout/error/cleanup behavior. Distinguish mocked route tests from real transaction/database/server tests; coverage percentages don't establish correctness.
- TestClient supports WebSocket sessions with bounded send/receive and context cleanup. Test disconnect/auth/message limits. For true network/proxy/multi-worker race behavior use separately approved real-server integration; in-process transport is not equivalent evidence.
- Streaming/SSE tests must use finite fixtures or bounded cancellation/timeouts and inspect framing/events/errors. HTTPX ASGI transport can buffer responses and hang on indefinite streams; don't claim real chunk timing/backpressure from an in-process stream loop alone.
- Assert exceptions versus safe 500 responses with actual client raise-server-exceptions settings; retain errors rather than weakening assertions. Run focused tests then relevant suite/lint/type/coverage gates from project automation; preserve the actual configured coverage threshold, not an invented 80% minimum.

### Execution Steps

1. Inspect app/dependencies/lifespan and test runner/client/database fixtures; identify exact behavior and isolation limits.
2. Add focused success/boundary/error/security assertions using correct client/loop and restored overrides.
3. Verify database writes/rollback and cleanup under failure; add targeted concurrency/stream/server tests only where risk warrants.
4. Run focused then relevant project checks and configured coverage; report real skips/mock/network/dialect gaps.
5. Document test scope and remaining runtime risks, without calling isolated synthetic tests production validation.

### Validation

- Correct HTTPX/TestClient/runner setup executes async code and lifespan intentionally, with no unawaited fixture or loop mismatch.
- Fresh app/override/database/session state is isolated and cleaned after errors and parallel execution.
- API outputs, security denial, state changes and transaction failures are asserted, not just happy statuses.
- WebSocket/stream tests terminate and distinguish in-process framing from actual network timing.
- Project tests/checks/coverage pass at existing targets; no production resource changes or unapproved external calls.

## References

- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Async tests and lifespan caveat](https://fastapi.tiangolo.com/advanced/async-tests/)
- [Dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [Starlette TestClient](https://www.starlette.io/testclient/)
- [HTTPX ASGI transport](https://www.python-httpx.org/advanced/transports/)
- [pytest-asyncio modes/scopes](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html)
