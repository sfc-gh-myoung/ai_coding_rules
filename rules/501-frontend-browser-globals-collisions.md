---
schema_version: v4.0
rule_version: v5.0.0
description: "Prevent accidental collisions with built-in browser globals (e.g., window.history) that can break HTMX navigation, Alpine components, and browser back/forward behavior. Codifies safe naming, scoping, and namespacing patterns."
last_updated: 2026-10-06
keywords:
  - kw:browser globals collision
  - kw:window.history shadowing
  - kw:htmx history restore
  - kw:Alpine.js component namespacing
  - kw:implicit global prevention
  - kw:inline script scoping
token_budget: ~1300
context_tier: High
depends:
  required:
    - 500-frontend-htmx-core.md  # HTMX history and lifecycle event definitions
---
# 501-frontend-browser-globals-collisions: Frontend Browser Globals Collisions

## Scope

**What This Rule Covers:**
Prevent accidental collisions with built-in browser globals (e.g., `window.history`) that break HTMX navigation, Alpine components, and browser back/forward behavior. Applies to inline `<script>` blocks and small JS helpers (<50 lines) in HTMX-driven, server-rendered templates.

**When to Load This Rule:**
- Writing or reviewing inline `<script>` blocks or JS helpers in HTMX/Alpine templates
- Debugging broken browser back/forward navigation in HTMX apps
- Creating top-level JavaScript functions or variables in server-rendered pages

## Contract

### Inputs and Prerequisites

- Familiarity with browser global objects (`window`, `history`, `location`) and HTMX history (`hx-push-url`, `hx-boost`, history restoration).
- Edit access to templates and JS files.
- Browser DevTools is required for manual navigation verification; the automated ESLint checks in Validation do not require browser access.

### Mandatory

**Forbidden at top level** — identifiers MUST NOT shadow these 19 browser globals:

`window`, `document`, `navigator`, `location`, `event`, `name`, `status`, `length`, `history`, `top`, `parent`, `frames`, `self`, `screen`, `alert`, `confirm`, `prompt`, `open`, `close`

- Use `const` or `let` for all declarations; `var` is forbidden.
- A top-level `function history(){}` overwrites `window.history`, breaking HTMX history management and browser back/forward. Never define top-level functions or variables matching the list above.
- Namespace any identifier exposed for HTML attribute references (Alpine `x-data`, `x-on`, etc.) under a single app object: `window.<app>.<feature> = (...) => ({ ... })`. This pattern is safe across HTMX swaps, which re-execute inline scripts.
- ES modules (`<script type="module">`) prevent *implicit* global creation by enforcing strict mode and module scope. They do **not** prevent explicit `window.foo = ...` writes; namespacing is still required for any intentional globals.
- For non-module scripts, add `"use strict";` at the top to prevent accidental implicit global creation.
- Preserve HTMX history and `hx-push-url`; never disable history as a collision workaround. If browser execution is unavailable, report back/forward, console and lifecycle checks as unverified, not passed.

**Renaming procedure:** When renaming a colliding identifier (e.g., `history` to `unistore.historyComponent`), update every call site: HTML attributes (`x-data="..."`, `hx-*`), other inline scripts, and any server-rendered template strings that reference it.

### Execution Steps

1. Identify all JS entry points: base template `<script>` tags, page templates, and static JS bundles.
2. Scan for identifiers matching the 19 browser globals; also scan for implicit globals (assignments without `const`/`let`/`var`).
3. Rename colliding identifiers and update all call sites — HTML attributes and template strings included.
4. Namespace component factories under a single app object (e.g., `window.unistore.historyComponent = () => ({ ... })`).
5. Verify HTMX navigation manually (see Validation), then run ESLint for automated coverage.

### Validation

**Manual checks (require browser DevTools):**
- Browser back/forward works without refresh on HTMX-swapped pages.
- `window.history` is still the built-in object: run `typeof window.history === "object"` in the console.
- No console errors during `htmx:afterSwap`, `htmx:historyRestore`, or `popstate`.
- Content restores correctly when `htmx:historyRestore` fires after back/forward.

**Automated ESLint** (does not require browser access):

```json
{
  "rules": {
    "no-restricted-globals": [
      "error",
      "event", "name", "status", "length", "top", "parent",
      "frames", "self", "screen", "alert", "confirm", "prompt",
      "open", "close",
      { "name": "history", "message": "Use window.history explicitly to avoid collisions." },
      { "name": "location", "message": "Use window.location explicitly to avoid collisions." }
    ],
    "no-implicit-globals": "error"
  }
}
```

If ESLint is not configured in the project, the automated check cannot run; perform the manual collision scan in Step 2 instead and document that no automated check was available.

**Checklist:**
- [ ] No top-level `history`, `location`, or `event` identifiers introduced
- [ ] No implicit globals (assignments without `const`/`let`) introduced
- [ ] HTMX navigation verified: click links, `hx-push-url`, back/forward restores content
- [ ] All HTML attribute and template call sites updated for any renamed identifiers

## References

- [MDN: Window.history](https://developer.mozilla.org/en-US/docs/Web/API/Window/history) — browser history API; `window.history` must remain the built-in object
- [HTMX Events](https://htmx.org/events/) — `htmx:afterSwap` and `htmx:historyRestore` lifecycle hooks

**Correct namespacing pattern** (Alpine component factory, safe across HTMX swaps):

```html
<div x-data="unistore.historyComponent()"></div>
<script>
  "use strict";
  window.unistore = window.unistore ?? {};
  window.unistore.historyComponent = () => ({ /* component state */ });
</script>
```

Avoids a direct `function historyComponent(){}` at top level, preserves `window.history`, and survives HTMX partial-page swaps that re-run inline scripts.
