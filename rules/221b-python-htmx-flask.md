---
schema_version: v4.0
rule_version: v5.0.0
description: "Flask HTMX routes/extensions, protected sessions/forms/uploads, representation-aware errors and verified browser effects."
last_updated: 2026-10-07
keywords:
  - kw:Flask-HTMX extension
  - kw:blueprint organization htmx
  - kw:Flask-WTF csrf htmx
  - kw:Flask-Login htmx redirect
  - kw:flask route decorators htmx
  - kw:flask session htmx
  - kw:flask
token_budget: ~1150
context_tier: Medium
depends:
  optional:
    - 221a-python-htmx-templates.md  # Jinja2 patterns
    - 221d-python-htmx-testing.md  # Testing Flask+HTMX
    - 221e-python-htmx-patterns.md  # CRUD, forms, etc.
---
# Flask and HTMX Integration

## Scope

**What This Rule Covers:**
Existing app/blueprint/extension integration, HTML/header responses, auth/CSRF/session, flash/upload and error behavior.

**When to Load This Rule:**
When building Flask HTMX flows; read `221-python-htmx-core.md` for shared header/security/history rules, template and test companions when applicable.

## Contract

### Inputs and Prerequisites

- Existing factory/blueprints/extensions/login/errors, installed Flask/Flask-HTMX/WTF versions and current template/request behavior.
- Auth/CSRF/session/escaping/cache/ upload policy and permitted tests/mutations.

### Mandatory

- Extend existing factory/blueprints and extension lifecycle; don't install Flask-HTMX/WTF/second factory by implication. Explicit HX-Request==true checking is valid; extensions don't magically handle every history/security edge.
- Use actual initialized extension/proxy import APIs from installed version. Presentation header detection never replaces login/resource/tenant authorization. HTMX-only route rejection is a representation policy, not security.
- Return rendered fragments/full pages with actual Flask responses/status and cache/history variation. Serialize HX-Trigger payloads and validate redirects; avoid service/database boilerplate in routes where existing service owner already fits.
- Keep CSRF protection for authenticated state changes, including PUT/PATCH/DELETE/uploads. Inject approved same-origin token header/form field and verify server-side; do not add csrf.exempt to fix an integration failure or call a public POST inherently safe.
- Keep strong required session/signing keys and secure cookie configuration, trusted user/session ownership and revocation/expiry policy. Flask signed-cookie sessions are not encrypted or a secret store; no global per-user state or cross-user cache.
- Match Flask-Login unauthorized behavior to plain versus HTMX navigation and distinguish 401 login from 403 denial. Ordinary 302 may return login HTML into a fragment; HX-Redirect/error hook handling must be verified with actual client status policy, not blindly force 200 for every auth error.
- Errors preserve meaningful status and safe fragment/full-page message; HX-Retarget alone doesn't enable 4xx/5xx swap. Use approved HTMX response handling and preserve unrelated Flask handlers.
- Keep flash message context escaped and authorized; avoid duplicate consumption/display when OOB and follow-up refresh both read the session. Full-page redirects and HTMX event refresh have distinct flows and tests.
- For uploads require actual multipart encoding, server/proxy request-size limit, allowed content/type parsing and bounded streaming; client accept/extensions alone aren't validation. secure_filename can be empty/collide; generate safe owned destinations and avoid overwrites/traversal. Don't read entire oversized body then declare a memory-safe limit.
- Route/service transaction commits precede truthful success events; validate current data/resource owner before CRUD/ upload. No private errors/files exposed through rendered attributes or notifications.
- Async Flask support requires installed compatible extras/server/extensions; per-request loops don't make background tasks durable or WSGI throughput unlimited. Verify decorators await correctly and don't reuse loop-bound clients across incompatible loops.
- Test actual header/no-header/false/history/boost/CSRF/denied/error paths using isolated app/session/request fixtures and browser checks. Extension presence or string assertions alone do not verify DOM behavior.

### Execution Steps

1. Inspect factory/blueprints/extensions/security and exact fragment/full-page contract.
2. Implement minimal response/auth/CSRF/session/upload change with existing helpers and safe service boundaries.
3. Test request/session/error/commit evidence in isolation, then approved browser swap/navigation/flash/upload behavior.
4. Run project checks and report remaining framework/version/runtime gaps.

### Validation

- Actual extensions/route registration and full/fragment/cache/header behavior correct.
- Auth/CSRF/session/upload controls hold even with spoofed HX headers; no exemption/overwrite leaks.
- Error/flash/navigation and transaction semantics verified through backend and browser evidence separately.
- Async lifecycle and cleanup match real server; no unapproved install/server/file/cloud mutation.

## References

- [Flask request/response and blueprints](https://flask.palletsprojects.com/en/stable/)
- [Flask-WTF CSRF](https://flask-wtf.readthedocs.io/en/stable/csrf/)
- [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- [Flask async constraints](https://flask.palletsprojects.com/en/stable/async-await/)
- [HTMX behavior](https://htmx.org/docs/)
