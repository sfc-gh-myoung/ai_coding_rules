---
schema_version: v4.0
rule_version: v3.0.0
description: "FastAPI HTMX trusted auth/CSRF, representation-aware denial and protected bounded SSE progress."
last_updated: 2026-10-07
keywords:
  - kw:FastAPI HTMX authentication
  - kw:HX-Redirect header
  - kw:SSE streaming FastAPI
  - kw:call_soon_threadsafe queue
  - kw:Starlette-WTF CSRF
  - kw:HTTPBearer dependency injection
  - kw:fastapi
token_budget: ~1050
context_tier: Medium
depends:
  optional:
    - 221c-python-htmx-fastapi.md  # Core FastAPI+HTMX patterns (Jinja2Templates, DI, async routes)
    - 210a-python-fastapi-security.md  # FastAPI security patterns
    - 221g-python-htmx-sse.md  # General SSE patterns
---
# FastAPI HTMX Authentication, SSE and CSRF

## Scope

**What This Rule Covers:**
Existing auth/session dependencies, HTMX login/denial navigation, cookie CSRF and authorized operation streams.

**When to Load This Rule:**
When protecting FastAPI HTMX forms/SSE; read `210a-python-fastapi-security.md` for token verification and `221g-python-htmx-sse.md` for stream/replay lifecycle.

## Contract

### Inputs and Prerequisites

- Existing auth/session/CSRF/exception handlers and actual library/template/HTMX versions.
- Resource/tenant access policy, cookie/header transport, operation ownership, stream format and permitted tests/changes.

### Mandatory

- Reuse current trusted auth and security libraries, not duplicate get_current_user or impose JWT on every session app. Bearer extraction isn't verification; check actual required signature/issuer/audience/expiry/purpose/subject and active user.
- HTTPAuthorizationCredentials and token strings have distinct dependency types. Use current FastAPI credential API and expected 401 challenge; validate role/resource/tenant ownership independently of HX presentation hints.
- Detect HX-Request==true and implement tested login navigation for 401, denied inline feedback for 403 where policy requires. Preserve status and non-HTMX JSON/plain behavior; don't raw-render str(exc.detail) as HTML or change all exceptions to 200/login redirects.
- Actual error-swap/responseHandling/client behavior determines how auth headers are processed. A 302 login response can be fetched as fragment instead of navigating; use supported HX-Redirect/client logic with safe approved local return URL and preserve WWW-Authenticate where relevant.
- Cookie-authenticated state changes require actual CSRF verification bound to session, not only csrf_secret or a template function name. Verify installed Starlette-WTF/other middleware constructor, token generation/context/form validation and session prerequisite; no guessed Flask-style csrf_token global.
- Inject token to approved same-origin requests; test missing/invalid/cross-session tokens and avoid exemption for convenience. Header-token auth versus browser cookie sessions have different CSRF/credential policies.
- Authorize stream and operation identity per trusted caller; do not start destructive work inside a GET stream or expose another user's progress by guessing op_id. Native EventSource lacks arbitrary headers; no JWT query parameter workaround by default.
- SSE events need actual data format: HTMX sse-swap consumes safe HTML, JSON needs explicit renderer or refresh trigger. Use current loaded extension, exact events, bounded queues/timeouts and no raw secret/error text.
- Capture running loop before threads and hand off thread-safely with bounded queue/backpressure. Supervise producer failure/completion/disconnect, close client listeners/connections, and cooperative-stop threaded work; to_thread cancellation doesn't kill it.
- Tests verify denied auth/CSRF/resource paths, partial/full/error representations, stream expiry/disconnect/producer failure and same-session browser behavior. Static header tests don't establish navigation/stream safety.

### Execution Steps

1. Inspect auth/CSRF/handlers/session and define actual navigation/operation-stream boundaries.
2. Add minimal compatible verification/authorization and safe HTML/HX error contract.
3. Implement protected bounded SSE only where required, with actual extension/format/cleanup.
4. Test synthetic security/stream/browser cases and project checks; report unverified client/runtime behavior.

### Validation

- Trusted tokens/sessions/users and resource ownership enforced independent of HX headers.
- 401/403/non-HTMX behavior and safe errors preserved; login redirects validated.
- CSRF really verified with actual session/token and stream format/bounds/cleanup correct.
- Backend/browser evidence distinct; no unapproved install/model/server/secret exposure.

## References

- [FastAPI security](https://fastapi.tiangolo.com/tutorial/security/)
- [FastAPI errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Starlette-WTF](https://github.com/muicss/starlette-wtf)
- [HTMX SSE](https://htmx.org/extensions/sse/)
- [HTMX](https://htmx.org/docs/)
