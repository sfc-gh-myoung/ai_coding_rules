---
schema_version: v4.0
rule_version: v5.0.0
description: "HTMX frontend integration with explicit DOM ownership, approved assets, idempotent initialization and plugin cleanup."
last_updated: 2026-10-07
keywords:
  - kw:Alpine.js HTMX
  - kw:_hyperscript inline behavior
  - kw:CSS framework styling
  - kw:chart library reinitialization
  - kw:htmx:afterSwap event hooks
  - kw:frontend library lifecycle
  - kw:htmx
token_budget: ~1000
context_tier: Low
depends:
  required:
    - 221-python-htmx-core.md  # HTMX foundation patterns
  optional:
    - 221a-python-htmx-templates.md  # Jinja2 patterns
    - 221e-python-htmx-patterns.md  # HTMX implementation patterns
    - 221g-python-htmx-sse.md  # Server-Sent Events patterns
---
# HTMX Frontend Integrations

## Scope

**What This Rule Covers:**
Alpine/hyperscript/CSS/icons/charts integration, asset/version policy, accessibility and repeated-swap lifecycle.

**When to Load This Rule:**
When integrating an existing frontend library into HTMX; read `221g-python-htmx-sse.md` for stream routing and templates companion for context/escaping.

## Contract

### Inputs and Prerequisites

- Actual libraries/versions/build/CSP/assets, current event handlers and element/plugin ownership, swap/OOB/history behavior.
- Required component behavior, accessible interaction and authorized dependency/asset scope.

### Mandatory

- Read base assets/init/disposal before adding libraries; match existing Alpine/hyperscript/chart/CSS owner. Don't add every library, mandate a project-wide exclusive choice or blanket-ban an established jQuery/React integration; prevent conflicting ownership of the same DOM.
- Load approved compatible assets once; pin reviewed versions, use existing build/self-host/CDN policy and CSP/integrity. No stale CDN version recipe or Tailwind development CDN as production build. Build CSS includes classes emitted by server templates.
- Initialize newly inserted components idempotently with actual library lifecycle APIs; scope to inserted root and descendants, not only querySelectorAll descendants. Don't double-init Alpine that already observes DOM or duplicate tooltip/event handlers.
- Destroy/release charts/tooltips/subscriptions/listeners before their owned elements are removed; use actual cleanup events/library lifecycle, not every beforeSwap regardless of whether swap occurs. OOB/history/outerHTML have distinct removal scopes.
- Chart registries keyed by stable DOM identity must remove stale references; validate safely serialized data and update/recreate only relevant charts. Never inject unescaped JSON into single-quoted data attributes or guess Chart options/methods.
- Server supplies authorized state/HTML; local Alpine/hyperscript state is presentation, not permission or source of truth for writes. Swaps intentionally preserve/reset local state and don't erase pending edits silently.
- Native semantics first; ARIA matches actual control behavior, keyboard/focus/modal trapping/restoration and announcements. Not every element needs arbitrary roles, and role=dialog alone doesn't implement an accessible modal.
- Event names/payloads exactly match publisher/listener. SSE-extension sse:name syntax differs from normal DOM custom event names; camelCase is convention, not mandatory technology. Avoid duplicate streams per component and retain returned cleanup handles.
- Animation/removal occurs only after successful confirmed operation, not any afterRequest including failure. Error/loading indicators clean up on timeout/cancel; don't hide failures with optimistic element deletion.
- Test repeated swaps/OOB/history, missing assets/data, removed roots, resize and keyboard flows with actual browser; static HTML doesn't prove initialization, memory safety or CSS coverage.

### Execution Steps

1. Inventory existing assets/DOM owners/lifecycle and required interaction.
2. Add minimal compatible initialization/disposal and safe data/event bridge.
3. Test browser repeat/error/removal/accessibility/resize paths and project checks.
4. Report actual lifecycle evidence and unverified browser/build gaps.

### Validation

- Assets/policy and component ownership compatible; no duplicate init/listeners/streams.
- Plugin state/data serialization and disposal correct for root/descendant/OOB/history swaps.
- Keyboard/focus/loading/error behavior and CSS/chart updates verified, not inferred.

## References

- [HTMX lifecycle events](https://htmx.org/events/)
- [Alpine lifecycle](https://alpinejs.dev/essentials/lifecycle)
- [Hyperscript](https://hyperscript.org/docs/)
- [Chart.js API lifecycle](https://www.chartjs.org/docs/latest/developers/api.html)
- [Bootstrap components](https://getbootstrap.com/docs/5.3/components/)
