---
schema_version: v4.0
rule_version: v5.0.0
description: "Provides a standalone frontend reference for HTMX attributes, client-side events, CSS transitions, debugging techniques, and browser compatibility considerations for pure HTMX usage without backend"
last_updated: 2026-10-06
keywords:
  - kw:hx-get
  - kw:hx-swap
  - kw:hx-trigger
  - kw:htmx lifecycle events
  - kw:hypermedia-driven UI
  - kw:progressive enhancement fallbacks
  - kw:htmx
token_budget: ~1200
context_tier: Low
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 221-python-htmx-core.md  # HTMX with Python backends
    - 421-javascript-alpinejs-core.md  # Alpine.js for client-side reactivity
---
# HTMX Frontend Reference

## Scope

**What This Rule Covers:**
HTML-driven requests, target/swap/trigger behavior, progressive enhancement, history, lifecycle/error handling and version-compatible extensions.

**When to Load This Rule:**
When editing HTMX frontend markup, requests/swaps/history or debugging client-side lifecycle behavior. Backend-specific patterns are optional companions.

## Contract

### Inputs and Prerequisites

- Actual installed HTMX version/script source, existing markup/CSP/CSRF and supported browser matrix.
- Endpoint/HTML response contract, relevant Alpine/extension lifecycle and authorized browser validation.

### Mandatory

- Inspect current HTMX version/patterns before loading/upgrading scripts. Library/extension URLs and compatibility need current official docs, not assumed legacy dist/ext paths.
- Specify hx-target for non-self swaps and choose hx-swap intentionally (inner/outer/insertion/delete/none). Target IDs and returned HTML must preserve required structure/accessibility.
- Configure triggers/debounce/polling based on actual interaction needs; avoid unbounded polling or duplicate event listener registration across swaps.
- Provide loading/error/empty/success states and prevent duplicate submissions. Indicator/transition timing should suit UX and reduced-motion preferences, not invented universal 200/500ms thresholds.
- Preserve form action/method and meaningful link href for non-JavaScript fallbacks where required. hx-boost enhances those semantics; do not assume every custom interaction degrades automatically.
- Mutating requests need appropriate backend CSRF/auth checks; HX-Request is not authentication. Escape untrusted HTML and use safe headers/values, never eval-like dynamic attributes from user input.
- Preserve hx-push-url/history/back-forward behavior and native window.history. Do not disable history as a collision fix; scope/name JS factories and update every HTML call site.
- Handle request errors/timeouts through supported lifecycle hooks and provide deliberate retry only for safe operations. hx-request configuration is valid object syntax; no malformed timeout string examples.
- Register/clean lifecycle handlers deliberately (beforeRequest/configRequest/afterSwap/historyRestore/popstate) and reinitialize third-party components only as needed. Returned fragments should not leak handlers or implicit globals.
- Empty response behavior and status swap policies require explicit endpoint/UI contract; do not universally prevent valid empty swaps or force every error body into content.
- Browser support, settle defaults and HTMX1->2 changes must be checked against installed version/official migration docs; no fixed unsupported browser/version guarantees.
- Real-time SSE/WebSocket use official compatible extensions only when needed, with connection cleanup/auth/error/backpressure and no unapproved external loading.

### Execution Steps

1. Read script/version, markup/endpoint contracts and current targets/history/CSRF/lifecycle conventions.
2. Make focused request/trigger/target/swap changes preserving accessibility and non-JS fallback where applicable.
3. Implement clear loading/error/empty states and safe lifecycle/component cleanup; preserve native globals/history.
4. Under browser authorization, inspect network HX-Request/response headers and test swaps, forms, back/forward and console/lifecycle behavior in supported browsers.
5. Run configured static checks/tests and report unavailable browser/endpoint/runtime checks as unverified rather than passed.

### Validation

- Requests target/swap intended content and all HTML/JS references coherent; no repeated listeners/global collision.
- Form/link fallback, focus/accessibility, CSRF/auth and escaped HTML maintained.
- Loading/error/empty/timeout/cancellation outcomes visible; safe retries not blind mutation replay.
- hx-push-url/native history/back-forward/restoration preserved and tested when browser available.
- Actual version/extension/browser compatibility checked, no speculative upgrade/network workaround.
- Static inspections distinct from real network/browser verification; unavailable checks disclosed.

## References

- [HTMX documentation](https://htmx.org/docs/)
- [HTMX reference](https://htmx.org/reference/)
- [HTMX lifecycle events](https://htmx.org/events/)
- [HTMX1 migration guide](https://htmx.org/migration-guide-htmx-1/)
- [HTMX SSE extension](https://htmx.org/extensions/sse/)
- [HTMX WebSocket extension](https://htmx.org/extensions/ws/)
- `501-frontend-browser-globals-collisions.md` for focused global-collision repair.
