---
schema_version: v4.0
rule_version: v5.0.0
description: "FastAPI HTMX HTML/template responses, validated forms, scoped async resources and durable background progress."
last_updated: 2026-10-07
keywords:
  - kw:FastAPI async routes
  - kw:Jinja2Templates FastAPI
  - kw:HTMX dependency injection
  - kw:BackgroundTasks polling
  - kw:Pydantic form validation
  - kw:htmx-fastapi integration
  - kw:fastapi
token_budget: ~1200
context_tier: Medium
depends:
  optional:
    - 221e-python-htmx-patterns.md  # CRUD, forms, etc.
    - 221d-python-htmx-testing.md  # Testing FastAPI+HTMX
    - 221h-python-htmx-fastapi-auth.md  # Auth, SSE, CSRF for FastAPI+HTMX
---
# FastAPI and HTMX Integration

## Scope

**What This Rule Covers:**
Actual Jinja/HTML response APIs, typed form/errors, sync/async boundaries, background progress and safe HX headers.

**When to Load This Rule:**
When implementing FastAPI HTMX routes. Read `210-python-fastapi-core.md`, `221-python-htmx-core.md` and `221a-python-htmx-templates.md` for shared contracts; `221h-python-htmx-fastapi-auth.md` for auth/CSRF/SSE.

## Contract

### Inputs and Prerequisites

- Current app/dependencies/template loader, FastAPI/Starlette/Jinja/HTMX versions, python-multipart when forms require it and existing auth/CSRF.
- Request/full/fragment/history/error contract, actual async resources and background lifecycle/owner/persistence requirements.

### Mandatory

- Reuse configured Jinja2Templates/detection/dependencies; no forced package install or duplicate templates instance. Verify current TemplateResponse signature with explicit request/name/context keywords where supported; positional order changed across releases.
- Return actual HTMLResponse/TemplateResponse and text/html; default FastAPI string returns can be JSON-encoded. Direct dictionaries are fine for separate JSON API contracts but aren't default HTMX fragments.
- HX-Request detection is explicit presentation information and header helpers can be simple; don't impose async def on a nonawaiting header reader. Validate boost/history/full-page/cache variation from shared core.
- Use async routes with awaitable I/O and appropriate shared client/session lifespan; sync def is valid for sync APIs. Bound HTTP timeouts/status/body/allowed destinations; never call blocking clients directly inside async handlers.
- Parse forms with installed supported Form/Pydantic integration and business constraints. FastAPI request validation can occur before the handler, so catching only Pydantic ValidationError inside it misses missing/wrong-type fields. Handle RequestValidationError for intended HTMX routes safely.
- Render validation errors with preserved escaped submitted values and clear status/target policy; sanitize raw input/error context. HX-Retarget doesn't override default error-swap behavior. Don't lowercase arbitrary email local parts or transform domain data without contract.
- Authorize resource/tenant operations and verify cookie CSRF on writes through actual integration; a header helper or custom token creator isn't complete security. Keep JSON/plain consumers' error contract intact.
- In-process BackgroundTasks is after-response, not durable distributed job execution. Use it only when loss/restart policy permits; durable long tasks require approved queue/store/ownership and recovery. Do not copy module-level demo task dictionaries to production or use an unowned UUID as authorization.
- Persist pending status before returning a progress element and distinguish pending/running/succeeded/failed/cancelled/unknown. Worker and status endpoint share actual storage; multiple processes/restarts invalidate in-memory assumptions. Progress only reflects completed work, not simulated sleep percent.
- Background jobs own fresh resources; don't retain request-scoped AsyncSession/client past teardown. CPU/blocking jobs require appropriate execution bounds, not arbitrary async wrapper. Poll status with bounded cadence and stop after terminal result/errors.
- Serialize event headers, return only after committed effects and validate redirects. Auth response status/token establishment must actually be implemented, not only authenticate and send HX-Redirect. Preserve warnings/failures instead of returning apparent success markup.
- Test current response signature/content type, forms/errors, auth/CSRF, background-start race/restart/failure, status ownership, clean resources and actual browser swaps. No blanket production-ready claim from fixture-only tests.

### Execution Steps

1. Inspect app/templates/form/auth/async/background setup and define exact response/state contract.
2. Implement minimal typed/escaped HTML integration with correct API/version and resources.
3. Test full/HTMX/history/invalid/denied inputs plus background pending/terminal/recovery ownership.
4. Verify browser error/poll/swap behavior in approved scope and run project checks; report unresolved runtime gaps.

### Validation

- Current template API/content type/request/context and full/fragment/cache behavior correct.
- All validation paths preserve safe HTML/status and enforce auth/CSRF without event-loop blocking.
- Background task durability/state/owner/resource contract explicit; no pending race or infinite terminal polling.
- Backend/browser checks separate; no unauthorized install/job/server/notification effects.

## References

- [FastAPI templates](https://fastapi.tiangolo.com/advanced/templates/)
- [Forms](https://fastapi.tiangolo.com/tutorial/request-forms/)
- [Validation errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [BackgroundTasks limitations](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Async execution](https://fastapi.tiangolo.com/async/)
- [HTMX](https://htmx.org/docs/)
