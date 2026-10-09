---
schema_version: v4.0
rule_version: v3.0.0
description: "FastAPI CORS/proxy/browser controls, bounded rate limits, parameterized data access, context-safe rendering and defensive configuration."
last_updated: 2026-10-07
keywords:
  - kw:FastAPI hardening
  - kw:CORS middleware
  - kw:slowapi rate limiting
  - kw:security headers middleware
  - kw:parameterized queries
  - kw:Pydantic field validators
  - kw:fastapi
token_budget: ~1400
context_tier: Medium
depends:
  optional:
    - 210a-python-fastapi-security.md  # Authentication and authorization patterns
---
# FastAPI Security Hardening

## Scope

**What This Rule Covers:**
Origin/host/proxy trust, browser security headers, abuse/resource limits, SQL/XSS/SSRF boundaries, input validation and production error/docs policy.

**When to Load This Rule:**
When hardening FastAPI middleware/endpoints or deployment; read `210a-python-fastapi-security.md` for auth and `210c-python-fastapi-deployment.md` for runtime boundaries.

## Contract

### Inputs and Prerequisites

- Existing middleware/auth/session/frontend architecture, allowed origins/hosts, proxy/TLS trust, deployment replicas, input/output contexts and actual limit library.
- Approved security policy, credential/session data flow, threat/resource budgets and test scope.
- Current FastAPI/Starlette/browser/library behavior and existing integration/exception handlers; no unapproved external scanner transmission.

### Mandatory

- Inspect existing controls before adding middleware/packages. CORS governs browser response access, not server authentication or general CSRF protection. Non-browser clients ignore CORS; enforce resource authorization and CSRF where cookie/session semantics require it.
- Use explicit approved origins/methods/headers for credentialed cross-origin requests and handle preflight/errors correctly. A wildcard can suit intentionally public noncredentialed resources under policy; wildcard plus credentials must not be copied as safe authenticated configuration.
- Validate trusted hosts and forwarded headers only from approved proxies. Client IP/rate keys derived from arbitrary forwarding headers are spoofable. TLS redirection/HSTS behind a proxy needs trusted scheme handling and loop testing.
- Apply content/type/framing/referrer/CSP and other headers suitable for response context; JSON-only API and HTML docs have different needs. X-XSS-Protection is obsolete, not modern XSS defense. HSTS includeSubDomains/preload requires deliberate complete-domain HTTPS policy.
- Middleware order/global wrapping affects headers on exception responses, CORS and streaming. Verify actual allow/deny/error routes rather than assuming a registration-order slogan. Use supported Starlette imports and real installed header-library API.
- Limit abuse-sensitive auth/reset/write/upload/read endpoints with policy-derived rates and distributed state where replicas require it. Limits are mitigation, not guaranteed brute-force prevention; fixed five/minute examples are not universal requirements.
- If using slowapi/another existing limiter, wire its actual request argument, app state, exception handler/middleware/store and decorator order per version. Return meaningful 429/Retry-After and protect store failures; an unused Limiter instance doesn't enforce anything.
- Bound request body/upload size, concurrency/timeouts, decompression/parsing and expensive downstream work. Pydantic length validation occurs after parsing and is not a transport memory limit; enforce appropriate server/proxy/app controls without buffering unbounded bodies.
- Parameterize SQL values and use safe validated identifier builders/allowlists for dynamic names/order clauses. ORM use alone does not make embedded text queries safe. Valid shape/regex does not replace query binding or business authorization.
- Apply typed validation to actual domain/precision/NULL requirements and allow only intended writable fields. Preserve valid punctuation/international text; stripping quotes/angle brackets from every string is not SQL/XSS protection and can corrupt data.
- Escape output for its HTML/attribute/JS/URL context; use a reviewed sanitizer for intentionally allowed rich HTML. Do not mark untrusted templates safe or rely on regex character deletion. JSON encoding isn't universal HTML/JS embedding safety.
- For user-controlled URLs/files, verify allowed schemes/hosts/resolved networks/redirects and path ownership; prevent unsafe internal destinations and traversal before fetch/read. Input field validation alone is not SSRF or filesystem authorization.
- Disable debug/error trace exposure in production; docs/schema can be disabled/protected/public under explicit policy, not mandatory secrecy. Hiding /docs isn't enforcement and can leave /openapi.json exposed if policy intended otherwise.
- Keep secret/key values out of configs/transcripts/scans; authorized local tests use synthetic inputs. Do not send proprietary app URLs/data to securityheaders.com or another external scanner without approval.
- Verify trusted/untrusted origin/host/preflight/auth/CSRF, rate/store failure, parameter binding/output encoding and payload limits. Report residual risk; no checklist or header scan certifies security/compliance.

### Execution Steps

1. Read actual frontend/session/middleware/proxy/input trust boundaries and existing controls; define permitted test and change scope.
2. Implement minimal correct origin/host/header/rate/resource/parameterization/rendering controls using installed APIs.
3. Exercise synthetic positive/negative/error/replica/proxy cases and verify no data-corrupting sanitization or secret exposure.
4. Run project validation and authorized deployment smoke only; inspect actual returned headers/status/effects.
5. Report controls, evidence, limitations and approved follow-up without external scanning or production changes by implication.

### Validation

- CORS/host/proxy/CSRF/auth responsibilities remain separate and correctly enforced through actual client paths.
- Headers and rate/resource limits work on success/error/preflight/stream cases with supported distributed semantics.
- SQL binding, safe identifiers, context-aware rendering and URL/path boundaries resist untrusted inputs without corrupting valid data.
- Production debug/docs/secret policy is explicit; no private data sent to external scanners.
- Output includes exact configuration/tests and unresolved risks, not guaranteed security from Pydantic or HTTP headers.

## References

- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/)
- [Starlette middleware](https://www.starlette.io/middleware/)
- [SlowAPI integration](https://slowapi.readthedocs.io/en/latest/)
- [OWASP SQL injection prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [OWASP XSS prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
