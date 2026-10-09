---
schema_version: v4.0
rule_version: v5.0.0
description: "React-to-backend integration: existing or Python-default backend, cookie session security with CSRF, explicit CORS, validated typed API layer and end-to-end tests."
last_updated: 2026-10-07
keywords:
  - kw:FastAPI React integration
  - kw:httpOnly cookie authentication
  - kw:TanStack Query backend communication
  - kw:CORS middleware configuration
  - kw:Python-first full-stack
  - kw:JWT refresh token rotation
  - kw:fastapi
token_budget: ~1150
context_tier: High
depends:
  required:
    - 440-react-core.md  # React patterns and architecture
    - 200-python-core.md  # Python development standards
---
# React Backend Integration

## Scope

**What This Rule Covers:**
React frontends calling backends (FastAPI/Flask default, framework routes or existing services): backend selection, typed validated API layer, cookie-based sessions, refresh rotation, CSRF, CORS and environment configuration.

**When to Load This Rule:**
When connecting React to an API, implementing login/session flows or debugging CORS; load `440-react-core.md` for component and state conventions.

## Contract

### Inputs and Prerequisites

- Existing frontend and backend code, frameworks/versions, deployment topology (same-origin, subdomains, cross-site), identity provider and auth requirements.
- Environment configuration, secret management, existing API contracts (OpenAPI/schemas) and the project's frontend/backend test commands.

### Mandatory

- Extend the existing backend and auth mechanism when present. For new backends default to Python (FastAPI for async/OpenAPI, Flask for simple synchronous services) unless the user, framework routes or team constraints call for another stack; this is an organizational preference, not a security property.
- Browser sessions use server-set `HttpOnly`, `Secure` cookies with deliberate `SameSite`, `Path` and lifetime; never store access or refresh tokens in localStorage, sessionStorage or client state stores. Prefer an established auth library or identity provider over hand-rolled JWT handling.
- Cookie-authenticated state-changing requests need CSRF protection (synchronizer or double-submit token, plus Origin/Referer checks) regardless of SPA or SSR; SameSite reduces but does not replace this.
- Refresh rotation invalidates the presented refresh token, detects reuse, scopes the refresh cookie path, and is serialized on the client so concurrent 401s trigger one refresh and one replay at most; failed refresh clears session state and routes to login without loops.
- Logout revokes the server session or refresh token and clears cookies server-side.
- CORS lists exact allowed origins per environment from configuration, never `*` with credentials; allow only needed methods and headers (including CSRF headers). Same-origin deployment or a proxy avoids CORS where possible.
- Cross-site cookies require `SameSite=None; Secure` and an explicit decision; prefer same-site API hosting.
- API URLs come from environment configuration. Frontend build-time variables (`VITE_*`, `NEXT_PUBLIC_*`) are public and must never hold secrets; backend secrets come from approved secret management, not committed files.
- Typed API functions check `response.ok`, map errors to typed results, include credentials only where required and validate untrusted response shapes (such as Zod) at the boundary; generated OpenAPI clients are acceptable.
- Fetch through the project's server-state tooling (TanStack Query or equivalent) per `440-react-core.md`; invalidate or clear auth-dependent cache on login/logout.
- Backends validate input with typed models (Pydantic), authorize every request server-side and never trust client-side role checks.
- Test the real flow: login, authenticated request, refresh, logout, CSRF rejection, disallowed-origin CORS and API failure states; do not claim auth or CORS correctness from configuration review alone.

### Execution Steps

1. Read frontend/backend code, auth mechanism, deployment topology and environment setup; choose or confirm the backend.
2. Implement the minimal API, session, CSRF, CORS and typed client changes using established libraries.
3. Run backend and frontend lint/type/tests and exercise integration and negative paths against a local stack.
4. Report endpoints, auth/cookie/CORS decisions, commands with results and remaining unverified security behavior.

### Validation

- No tokens in browser-readable storage; cookies `HttpOnly`/`Secure` with deliberate SameSite and path.
- CSRF enforced for cookie-authenticated mutations; CORS exact-origin with credentials only as needed.
- Refresh rotation single-flight with reuse detection; logout revokes server-side.
- No secrets in frontend env or source; integration and negative tests pass or gaps reported.

## References

- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [Flask-CORS](https://pypi.org/project/flask-cors/)
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS)
- [MDN Set-Cookie](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie)
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Vite env variables](https://vite.dev/guide/env-and-mode)
