---
schema_version: v4.0
rule_version: v5.0.0
description: "HTMX backend HTML/header contracts, history/cache correctness, CSRF/auth boundaries and tested swap/error behavior."
last_updated: 2026-10-07
keywords:
  - kw:hx-request header detection
  - kw:partial HTML rendering
  - kw:HX-Trigger response headers
  - kw:CSRF token injection
  - kw:swap strategy selection
  - kw:hypermedia-driven navigation
token_budget: ~1350
context_tier: High
depends:
  required:
    - 200-python-core.md  # Python coding standards
  optional:
    - 221c-python-htmx-fastapi.md  # FastAPI-specific HTMX patterns
    - 221e-python-htmx-patterns.md  # CRUD, forms, infinite scroll
    - 221g-python-htmx-sse.md  # Server-Sent Events patterns
---
# HTMX Core Patterns (Python)

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> Essential hypermedia request and security contract.

## Scope

**What This Rule Covers:**
Header-aware full/fragment responses, swaps/events/navigation, cache/history, server validation/auth/CSRF and extension lifecycle.

**When to Load This Rule:**
When implementing Python HTMX backends. Read `221a-python-htmx-templates.md` for rendering, framework companions for integration, `221g-python-htmx-sse.md` for streaming and `221e-python-htmx-patterns.md` for interactions.

## Contract

### Inputs and Prerequisites

- Existing routes/templates/header helper, actual HTMX/extension version, swap/target/history behavior and framework response classes.
- Auth/CSRF/template escaping policy, browser/plain navigation requirements, cache boundary and permitted changes/tests.

### Mandatory

- Inspect existing helpers/templates/security before extending. Pin/verify installed HTMX/extension API, not assume 1.9.x current or v2 is only attribute renaming; current docs may also discuss later versions. Don't change dependencies/CDN providers unasked.
- Compare HX-Request explicitly to true where used; headers are client-controlled presentation hints, never trusted identity/permission. Serve useful full pages for normal navigation and fragments for intended swaps; hx-boost/history restores can need different representations.
- Set HTML content type through actual HTML response/rendering; returning a Python string from a JSON-default API may encode it as JSON. HTML is default HTMX swap contract; JSON requires an explicit tested client/extension integration, not a universal ban.
- If a URL varies on HX headers, configure Vary and private/cache behavior plus distinct validators as needed. History restoration must obtain a complete navigable page; adjust historyRestoreAsHxRequest/restore headers for actual version. Prevent partial/full or cross-user cached response mixups.
- Use proper swap semantics: innerHTML replaces content, outerHTML replaces target, relative inserts append/prepend at defined positions, delete removes and none suppresses primary swap. Match returned structure to valid DOM context and OOB IDs; preserve focus/accessibility and avoid duplicate targets.
- Server validates/authenticates/authorizes every action/resource/tenant independently of displayed controls. State-changing GET, hidden button or HX-Request isn't protection; use method/idempotency/transaction rules.
- Cookie-authenticated writes require actual CSRF verification. Inject token only to approved same-origin requests through existing integration; a meta tag/header listener alone doesn't validate it, and broad cross-origin injection can leak tokens.
- Enable HTML autoescape in the configured Jinja environment/framework; bare Jinja defaults aren't universally autoescaping. Don't concatenate raw user values, mark untrusted content safe or rely on deleting punctuation. Rich HTML requires reviewed sanitization; attributes/JS/URLs need context-aware encoding.
- Define CSP and HTMX script/eval/extension behavior together. Nonce matches the actual response's scripts; history/fragment script handling requires tests. Don't blindly whitelist a CDN or claim nonce alone makes arbitrary swapped HTML safe.
- Set HX-Trigger JSON via serializer; choose timing/event name/target deliberately. HX-Redirect/HX-Location/HX-Push-Url/refresh/retarget/reswap differ; avoid open redirects and raw user-header injection. HTMX headers aren't processed on ordinary 3xx in the same way as a final response.
- Error status defaults may not swap 4xx/5xx; HX-Retarget alone doesn't enable error swaps. Configure supported responseHandling/event hook/extension intentionally and test validation/auth/errors. Preserve status meaning; 401 login navigation and 403 denial need explicit separate policy, not convert all failures to 200.
- hx-boost can progressively enhance standard links/forms when actual non-JS fallback exists; adding it doesn't automatically make hx-only controls work without JS. File downloads/external navigation need intentional opt-out or supported response handling.
- Polling/SSE/WebSocket fit comes from required latency, users and server capacity, not universal five/30-second safe thresholds. Extensions require actual loaded assets and matching event names; avoid duplicate per-element subscriptions, bound buffers, authenticate and clean up on disconnect.

### Execution Steps

1. Read routes/templates/version/helpers and define full/fragment/history/swap plus security/cache contract.
2. Implement minimal correct HTML/header response and existing validated auth/CSRF/escaping boundaries.
3. Test full/HTMX/boost/history/error/denied cases, headers and fragment structure independently.
4. Verify browser swaps/focus/navigation/extensions and non-JS fallback in approved local scope; run project checks.
5. Report backend versus browser evidence, changed behavior and unverified deployment/client gaps.

### Validation

- HTML/content/header/status match intended representation and browser swaps, including validation errors.
- Cache/history/plain navigation preserve full pages and user boundaries; targets/OOB IDs/DOM valid.
- Server auth/CSRF/input/output protections hold even with spoofed HX headers.
- Extensions/polling and disconnect lifecycle tested under actual version; no guaranteed compatibility from static response checks.
- Output includes routes/templates/headers, tests and browser/runtime gaps; no unauthorized install or external asset/data transmission.

## References

- [HTMX request/response, history, caching and security](https://htmx.org/docs/)
- [HTMX response headers](https://htmx.org/reference/#response_headers)
- [Jinja escaping](https://jinja.palletsprojects.com/en/stable/api/#autoescaping)
- [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
