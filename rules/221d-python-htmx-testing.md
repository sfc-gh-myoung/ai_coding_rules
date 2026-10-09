---
schema_version: v4.0
rule_version: v5.0.0
description: "Isolated HTMX response/header/DOM tests plus real browser swap/history/security verification without fabricated integration success."
last_updated: 2026-10-07
keywords:
  - kw:htmx endpoint testing
  - kw:HX-Request header
  - kw:HX-Trigger response headers
  - kw:partial HTML assertions
  - kw:htmx_client fixture
  - kw:OOB swap testing
token_budget: ~1100
context_tier: High
depends:
  required:
    - 206-python-pytest.md  # Pytest best practices
  optional:
    - 221b-python-htmx-flask.md  # Flask-specific testing
    - 221c-python-htmx-fastapi.md  # FastAPI-specific testing
    - 200-python-core.md  # Python standards
---
# HTMX Testing Patterns

## Scope

**What This Rule Covers:**
Header variations, HTML/DOM/header assertions, state changes/auth/CSRF, mocks and browser history/error/OOB behavior.

**When to Load This Rule:**
When testing HTMX endpoints; read framework companions and `221-python-htmx-core.md` for request/security contracts.

## Contract

### Inputs and Prerequisites

- Current conftest/client/loader/parser, actual framework/HTMX versions, route/header/status/swap contract and async fixture setup.
- Safe app/database/session/synthetic fixtures, auth/CSRF and approved local browser scope.

### Mandatory

- Reuse installed parser/client/fixtures and project coverage goals; no mandatory BeautifulSoup/pytest-mock install, duplicate htmx_client or invented 80% gate. Use actual framework response API: Flask data versus HTTPX text/content differ.
- Test no HX header, true/false/malformed header and relevant boost/history restoration, not only htmx_client. Fixture header merging copies maps and permits per-test overrides instead of overwriting false/denial cases.
- Assert meaningful status/content type, full-page versus intended fragment structure and data; searching for absence of <html> alone doesn't verify valid response. Parse expected selectors/IDs/attributes/escaped content and table/list/OOB contexts.
- Parse structured HX-Trigger JSON and assert event payload/target/timing, not substring membership. Check redirects/retarget/reswap/Vary/cache semantics against the actual contract.
- Test supported validation/missing/not-found/auth/forbidden/server failure paths with safe details and correct state rollback; not every route must fabricate every HTTP status. Error-header existence alone doesn't prove the browser swaps 4xx/5xx.
- Backend request tests don't run HTMX: use actual approved browser tests for swaps/OOB focus/history/back navigation/error policy, pending/loading/terminal states and no-JS fallback. Distinguish HTML parser behavior from browser parsing.
- Keep real CSRF integration active in dedicated tests: obtain token with the same client/session cookie used for the write, then test missing/invalid/expired/cross-session tokens. A separate test_request_context token can lack the client session needed for acceptance.
- Assert auth/resource/tenant denial with spoofed HX hints and actual session/cookie/token boundaries. Do not override auth for all tests then claim protected endpoints verified.
- Isolate database/app/session/env and restore overrides. Assert persisted side effects/transactions, duplicates and source counts for CRUD, not only response fragments; unit mocks aren't real integration.
- Mock where called with async-aware doubles and assert awaits/payload/status/cleanup. No real external requests unless separately authorized; fixtures use synthetic data and safe paths.
- For repeated swaps/pagination/concurrent requests assert stable keys/order, no duplicate IDs/listeners/sentinels, clean terminal polling and safe retries. Streaming tests are finite/bounded and don't infer real network timing from buffered ASGI clients.
- Run focused then required project checks; retain failures/skips and report browser/live/dialect gaps rather than replace missing evidence with manual visual impressions.

### Execution Steps

1. Read route/header/DOM/security contract and existing client/parser/session fixtures.
2. Add minimal positive/negative representation/status/state/header/escaping assertions with isolated data.
3. Verify real auth/CSRF and browser swap/history/error/OOB flows where authorized and available.
4. Run project validation/coverage and report exact mocked/backend/browser evidence and gaps.

### Validation

- True/false/no-header/restore representations and exact HTML/header/status/state semantics correct.
- CSRF token shares actual client session, authorization denial and escaping tested independently.
- DOM swaps/OOB/history/focus/polling behavior verified in a browser or explicitly unverified.
- Fixtures/async mocks/cleanup deterministic; no unauthorized DB/network/browser effects or hidden skips.

## References

- [HTMX](https://htmx.org/docs/)
- [Flask test clients and sessions](https://flask.palletsprojects.com/en/stable/testing/)
- [FastAPI async tests](https://fastapi.tiangolo.com/advanced/async-tests/)
- [Pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [Playwright assertions](https://playwright.dev/docs/test-assertions)
