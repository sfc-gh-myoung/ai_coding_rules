---
schema_version: v4.0
rule_version: v3.0.0
description: "Bounded HTMX pagination/live updates, accessible modal lifecycle and durable validated multi-step state."
last_updated: 2026-10-07
keywords:
  - kw:infinite scroll
  - kw:SSE polling
  - kw:modal drawer
  - kw:multi-step wizard
  - kw:revealed trigger
  - kw:htmx-ext sse
token_budget: ~1000
context_tier: Medium
depends:
  optional:
    - 221e-python-htmx-patterns.md  # Core HTMX patterns (CRUD, forms, search)
    - 221g-python-htmx-sse.md  # Comprehensive SSE patterns
---
# HTMX Advanced Patterns

## Scope

**What This Rule Covers:**
Scroll/lazy pagination, SSE/polling selection, modal/drawer accessibility and protected persistent wizard state.

**When to Load This Rule:**
Only when these interactions are needed; read `221e-python-htmx-patterns.md` for basic forms/CRUD and `221g-python-htmx-sse.md` for stream contracts.

## Contract

### Inputs and Prerequisites

- Existing pattern/assets/modal owner, stable data order/pagination, framework/server/transport and accessibility/fallback requirements.
- Auth/CSRF, session/store persistence and wizard ownership/version, validation and approved mutation scope.

### Mandatory

- Extend one current pattern/component owner rather than introduce another Alpine/hyperscript/modal stack. Add only needed features and actual loaded extensions.
- Scroll/lazy loading validates bounded page/cursor/query input, stable sort/key and tenant scope. Return intended items plus one next sentinel when has_more; remove/replace consumed sentinel so repeated revealed events don't duplicate pages.
- Use revealed/intersect semantics appropriate to viewport versus scroll container. Prevent concurrent duplicate fetch and handle late/empty/error/retry/end state, valid DOM/IDs and keyboard-accessible load-more fallback; arbitrary int conversion isn't complete input validation.
- Choose polling versus SSE from freshness/users/server capacity and actual sync/async deployment. Bound interval/load, stop polling on terminal/disconnect and preserve failure state; no fixed two/five-second universal recipe or new gevent/Quart install by implication.
- SSE requires explicit safe HTML versus JSON/event contract, scoped authorization, backpressure/replay and cleanup. Don't block async generator with time.sleep or emit unframed multiline HTML; sync server SSE consumes resources needing actual deployment analysis.
- Modals/drawers use semantic dialog labeling, focus trap/restoration, Escape and intentional outside-click behavior, inert/background policy and scroll control. Preserve pending form state or prompt on loss; escape content, no blanket safe filter or inline-handler injection.
- Wizard state lives in a trusted approved persistence/session design with owner ID, step/version/expiry and CSRF. Flask signed cookies aren't server-side storage; don't place sensitive drafts there assuming encryption. Nested session mutation must trigger actual persistence.
- Validate each submitted step before storing, enforce permitted transition order and revalidate the entire current state at final commit. Prevent tampered/back-skipped/expired/other-user drafts, concurrent-tab overwrite and duplicate completion through idempotent transaction.
- Refresh/back/cancel/resume have explicit state/fallback behavior; clear draft only after successful commit and retain failed state for recovery. No account creation from an unvalidated session dict or success markup before persistence.
- Test browser repeat-scroll/sentinel/modal/focus/back/JS-off/stream/wizard concurrency and server state/security; static fragments alone aren't accessibility or lifecycle proof.

### Execution Steps

1. Read existing advanced component/state and define minimal lifecycle/access/fallback contract.
2. Implement bounded pagination/live/modal/wizard behavior only as required.
3. Verify backend state/security and actual browser failure/repeat/focus/history/concurrency behavior.
4. Run project checks and report unverified persistence/transport/browser gaps.

### Validation

- Pagination has stable bounded access, no duplicate sentinel/results and clear end/error/fallback.
- Live updates match real format/server and stop cleanly; modal keyboard/focus/state accessible.
- Wizard owner/CSRF/transitions/full validation/persistence/commit idempotency survive refresh/back/failure.
- Tests separated by backend/browser scope; no guessed production storage or unauthorized deployment.

## References

- [HTMX examples](https://htmx.org/examples/)
- [HTMX triggers](https://htmx.org/attributes/hx-trigger/)
- [HTMX SSE](https://htmx.org/extensions/sse/)
- [Accessible modal pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)
- [Flask session semantics](https://flask.palletsprojects.com/en/stable/api/#sessions)
