---
schema_version: v4.0
rule_version: v5.0.0
description: "Minimal safe Jinja HTMX fragments, full-page/history composition, valid swap targets and reusable escaped context."
last_updated: 2026-10-07
keywords:
  - kw:Jinja2 partials
  - kw:HTMX fragment rendering
  - kw:template directory organization
  - kw:conditional HTMX detection
  - kw:reusable template macros
  - kw:partial inheritance anti-patterns
token_budget: ~1150
context_tier: High
depends:
  required:
    - 221-python-htmx-core.md  # HTMX foundation patterns
  optional:
    - 221c-python-htmx-fastapi.md  # FastAPI template setup
    - 221e-python-htmx-patterns.md  # Template patterns for CRUD, forms, etc.
    - 221b-python-htmx-flask.md  # Flask-specific template patterns
---
# HTMX Template Strategies

## Scope

**What This Rule Covers:**
Existing loader/layout conventions, fragment/page composition, macros/context, DOM targets/errors/pagination and escaping/render tests.

**When to Load This Rule:**
When organizing/rendering Jinja HTMX templates; read framework companions for response signatures and `221e-python-htmx-patterns.md` for interaction contracts.

## Contract

### Inputs and Prerequisites

- Existing base/page/partial/macros, loader/autoescape/context processors, HTMX/extension version and request/history/swap requirements.
- Required view-model fields, route names and auth/CSRF/CSP/cache controls; supported browser/HTML validation tools.

### Mandatory

- Match current partial/component paths/naming; do not mandate underscore prefixes or a new directory tree. Reuse macros/includes when they remove real duplication; keep fragments independently understandable.
- Full pages can extend base layouts; swapped fragments must not accidentally emit complete document/navigation chrome. Fragment-specific inheritance/conditional layouts are valid if resulting HTML fits the contract; Jinja supports conditional inheritance, so no false universal extends-in-if prohibition or one-level cap.
- Choose representation at view or a clear existing template boundary. Check HX-Request value and history/boost context, not presence/truthiness alone. Both branches provide equivalent required data/actions and correct cache variation.
- Enable actual HTML autoescaping and preserve it in includes/macros. Minimize context to approved required view-model data, not full settings/sessions/all users. Optional fields/errors have intentional defaults; missing required context must not produce misleading blank success.
- Generate URLs through framework route helpers and validate IDs/URL schemes. Escape user content/quoted attributes; macros aren't automatic authorization or safe-JS encoding. No raw safe filter on untrusted content.
- IDs must be unique/stable where selectors/OOB require them; not every swappable element needs an ID because this/closest selectors are supported. Ensure labels/inputs and dynamic IDs match and avoid repeating generic field IDs across forms.
- Match inner versus outer swap to expected wrapper ownership; returned table rows/list items need valid context and parser handling. Includes/OOB nested behavior can move/remove reused content; test actual response and destination rather than string presence only.
- Forms keep server validation errors/entered values/CSRF and accessible labels/live feedback. Error/toast fragments use safe messages and deliberate status/error-swap handling; HX-Retarget alone doesn't make 400/422 swap. Hyperscript attributes require that library, not HTMX by itself.
- Pagination/infinite scroll uses actual stable order/page/cursor and has_more, replaces the sentinel with appropriate new items/next sentinel, prevents duplicate IDs/requests and ends cleanly. Concurrent/empty/error/retry behavior must not silently duplicate rows or discard navigation fallback.
- Base assets/config loaded once under version/CSP policy; no stale claim HTMX 1.9 is current or blind inline script/CDN addition. Initialization after swaps must be idempotent and teardown associated listeners/subscriptions.
- Test fragments with required request/app context for url_for and intended macro imports; bare app context may not satisfy route generation. Render tests assert structure/escaping/targets, browser tests verify actual swapping/focus/history. Don't claim behavior from a text search alone.

### Execution Steps

1. Read loader/base/macros and route/request/security contracts; identify smallest reusable fragment change.
2. Implement view-model/context and page/fragment composition with safe URLs/escaping and valid target wrappers.
3. Render normal/HTMX/history and valid/error/empty/hostile-content fixtures; check IDs/DOM/CSRF.
4. Verify browser swap/error/pagination/focus behavior and project lint/tests; report unavailable browser coverage.

### Validation

- Full and partial outputs fit intended wrapper/request/history contracts and cache policy.
- Autoescape/context/URL/CSRF preserve security; missing data and error status are explicit.
- IDs/table/list/OOB/form/pagination composition valid under actual browser parsing and extension setup.
- Render/browser checks separately reported; no unsupported Jinja restriction or hidden asset install.

## References

- [Jinja inheritance, macros and context](https://jinja.palletsprojects.com/en/stable/templates/)
- [Jinja autoescaping](https://jinja.palletsprojects.com/en/stable/api/#autoescaping)
- [HTMX behavior](https://htmx.org/docs/)
- [Flask template context](https://flask.palletsprojects.com/en/stable/templating/)
- [FastAPI template signatures](https://fastapi.tiangolo.com/advanced/templates/)
