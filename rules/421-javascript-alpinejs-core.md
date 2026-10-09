---
schema_version: v4.0
rule_version: v5.0.0
description: "Alpine.js 3 component scope, safe directive/data binding, CSP-aware loading and progressive enhancement with tested browser behavior."
last_updated: 2026-10-07
keywords:
  - kw:x-data directive
  - kw:declarative directives
  - kw:magic properties
  - kw:Alpine.data registration
  - kw:x-cloak FOUC prevention
  - kw:progressive enhancement
token_budget: ~1150
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 421a-javascript-alpinejs-advanced.md  # Stores, plugins, transitions, lifecycle, error recovery
    - 420-javascript-core.md  # JavaScript patterns and best practices
    - 500-frontend-htmx-core.md  # HTMX patterns for server-driven interactivity
---
# Alpine.js Core

## Scope

**What This Rule Covers:**
Alpine.js 3 loading, x-data component scope, core directives, Alpine.data registration, x-cloak, safe rendering and progressive enhancement of server-rendered HTML.

**When to Load This Rule:**
When adding or reviewing Alpine.js behavior in markup; read `421a-javascript-alpinejs-advanced.md` for stores, events, transitions, lifecycle and plugins.

## Contract

### Inputs and Prerequisites

- Installed Alpine version and delivery (bundler import or pinned CDN), existing templates/components, server rendering and routing model.
- Actual Content-Security-Policy, supported browsers, accessibility requirements, data trust boundaries and the project's browser test tooling.

### Mandatory

- Read existing markup, scripts and Alpine version before editing; follow the established loading, registration and naming conventions rather than introducing a second pattern.
- Load one Alpine build once. Bundled installs register components and plugins before `Alpine.start()`; CDN script tags use `defer`, an exact pinned version and SRI/crossorigin only with a hash taken from the published artifact or registry, never an invented value.
- Under a CSP without `unsafe-eval`, use the `@alpinejs/csp` build and keep expressions within its documented subset, moving logic into registered `Alpine.data` methods. Never add inline `onerror`/`onclick` fallbacks or weaken CSP to make Alpine work.
- Place reactive directives inside the intended `x-data` scope; standalone `x-init` is valid but must not depend on component state it cannot see. Keep component state minimal and serializable where it is persisted or hydrated.
- Use `<template>` as the single-root wrapper for `x-for` and `x-if`, and give `x-for` a stable unique `:key` when items reorder, insert or remove.
- Extract behavior to `Alpine.data()` when it is reused, needs testing, needs CSP compatibility or grows beyond a readable inline expression. Methods that rely on `this` use method/function syntax; arrow functions are fine for callbacks that should not rebind `this`.
- Render untrusted data with `x-text` or bound attributes. Use `x-html` only for content that is trusted or sanitized by an approved sanitizer, and never bind user input to `href`/`src` without scheme validation.
- Add the `[x-cloak] { display: none !important; }` rule where x-cloak is used, and ensure essential content and forms still work without JavaScript when the page is progressively enhanced.
- Prefer Alpine directives and `$refs` over manual DOM mutation inside a component; isolate unavoidable third-party DOM libraries with explicit init/cleanup.
- Async handlers check `response.ok`, handle network/parse errors, show accessible pending/error state and avoid duplicate submissions; server-side validation remains authoritative.
- Keep interactive controls accessible: native elements where possible, correct labels, focus management, keyboard handling and ARIA state that reflects `x-show`/toggle state.
- Test actual behavior in a browser or the project's DOM test harness; do not claim interactivity, CSP compatibility or accessibility from static markup review alone.

### Execution Steps

1. Read existing Alpine version, loading, CSP, templates and components, and confirm the requested behavior and data trust.
2. Implement the minimal scoped component or `Alpine.data` registration with safe bindings, x-cloak and progressive fallback.
3. Run available lint/format/tests and exercise the component in a browser or harness, including no-JS, error and keyboard paths.
4. Report changed components, CSP/build choice, evidence gathered and any unverified browsers or accessibility checks.

### Validation

- Single pinned Alpine load; CSP build used when required, with no inline handlers or loosened policy.
- Directives resolve against the intended scope, `x-for` keys are stable and templates wrap loops/conditionals.
- No `x-html` or URL binding of untrusted input; async errors and pending states handled.
- Browser/harness behavior, keyboard access and no-JS fallback verified or explicitly marked unverified.

## References

- [Alpine.js installation](https://alpinejs.dev/essentials/installation)
- [Alpine.js CSP build](https://alpinejs.dev/advanced/csp)
- [x-data](https://alpinejs.dev/directives/data)
- [x-html](https://alpinejs.dev/directives/html)
- [Alpine.data](https://alpinejs.dev/globals/alpine-data)
- [x-cloak](https://alpinejs.dev/directives/cloak)
