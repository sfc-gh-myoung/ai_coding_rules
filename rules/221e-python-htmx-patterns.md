---
schema_version: v4.0
rule_version: v5.0.0
description: "Safe HTMX CRUD, inline forms, bounded search and genuine non-JavaScript fallback with verified state and swaps."
last_updated: 2026-10-07
keywords:
  - kw:HTMX CRUD
  - kw:server-side form validation
  - kw:search debounce autocomplete
  - kw:progressive enhancement fallback
  - kw:inline editing outerHTML swap
  - kw:HX-Trigger response headers
token_budget: ~950
context_tier: Medium
depends:
  optional:
    - 221i-python-htmx-patterns-advanced.md  # Advanced patterns (scroll, modals, wizards, real-time)
    - 221b-python-htmx-flask.md  # Flask-specific patterns
    - 221c-python-htmx-fastapi.md  # FastAPI patterns
---
# HTMX Common Patterns

## Scope

**What This Rule Covers:**
CRUD/inline edit, form errors, search/autocomplete, safe server state and progressive enhancement.

**When to Load This Rule:**
When implementing these interactions; read `221-python-htmx-core.md` and `221a-python-htmx-templates.md` for shared response/security contracts, `221i-python-htmx-patterns-advanced.md` only for advanced flows.

## Contract

### Inputs and Prerequisites

- Existing interaction/template/service/validation patterns, stable resource identities and current swap/error/history configuration.
- Auth/CSRF, business constraints, transaction/retry policy, accessibility and non-JS requirements.

### Mandatory

- Reuse existing pattern rather than add a competing modal/form/search owner. Server validates actual field types/length/domain/permissions on every write; minimum two-character names or @-only email checks are not universal validation rules.
- Load/authorize current resource and validate a separate submitted model before mutating ORM state; autoflush can persist invalid assignments. Commit before success event/markup and handle conflicts/concurrent updates deliberately.
- Inline edit targets stable row/component and returns matching wrapper for outerHTML. Cancel restores current server display without unintended write; valid IDs/DOM and focus are tested.
- Create appends a real committed item with a stable key; prevent duplicate submission through actual idempotency/constraints. Delete uses appropriate method and server authorization/CSRF; hx-confirm is user confirmation, not authority. Empty 200 with outerHTML and 204/delete strategies have different swap behavior.
- Render errors with preserved escaped input, labels/field association and safe status. Configure actual error swap/retarget rules; don't return raw exception HTML or assume a 400 automatically replaces the form.
- Search/autocomplete uses bounded query/results, parameterized data access, trusted tenant filters and stable ordering. Debounce/cancellation/synchronization must prevent stale older responses overwriting newer queries; chosen delays/limits are workload policy.
- Empty query/results and failure/loading states are explicit; don't silently leave stale suggestions. Keyboard/focus/selection semantics and screen-reader feedback must work, not just mouse clicks.
- Prefer safe templates/URLs and context-aware escaping; no raw f-string user/name/error interpolation or User(**unfiltered_form) mass assignment. HX headers don't authenticate the request.
- Non-JS fallback uses real href/action/method controls and server full-page success/error/redirect paths. HTML forms support GET/POST, not native PUT/DELETE: implement approved fallback endpoints/method override if needed. hx-only buttons don't become progressive by adding unrelated form attributes.
- Test intended interactions with and without HTMX, real state/transaction outcomes, repeated/concurrent/error/denied requests and actual browser swaps; advanced features only when requirements justify.

### Execution Steps

1. Read existing interaction/security and define state/DOM/fallback contracts.
2. Implement minimal scoped CRUD/form/search service and safe templates/headers.
3. Test validation/auth/CSRF/state/retry plus browser focus/swap/search ordering and no-JS behavior.
4. Run project checks and report backend/browser/runtime gaps.

### Validation

- Correct committed state, denied/invalid rollback, stable IDs/response wrappers and safe headers verified.
- Form errors/search results/loading/empty/keyboard and stale-request behavior work.
- Actual non-JS paths and browser swaps tested or gaps explicit; no fabricated success from HTML alone.

## References

- [HTMX examples](https://htmx.org/examples/)
- [HTMX synchronization](https://htmx.org/attributes/hx-sync/)
- [HTMX](https://htmx.org/docs/)
- [Hypermedia Systems](https://hypermedia.systems/)
