---
schema_version: v4.0
rule_version: v3.0.0
description: "Alpine.js stores, event communication, lifecycle cleanup, transitions, effects and plugins with safe state and tested behavior."
last_updated: 2026-10-07
keywords:
  - kw:Alpine.store
  - kw:$dispatch cross-component
  - kw:lifecycle hooks init destroy
  - kw:x-transition animations
  - kw:Alpine.js DevTools debugging
  - kw:x-effect reactive side effects
token_budget: ~1000
context_tier: Low
depends:
  required:
    - 421-javascript-alpinejs-core.md  # Core Alpine.js directives and reactivity
  optional:
    - 420-javascript-core.md  # JavaScript patterns and best practices
    - 500-frontend-htmx-core.md  # HTMX patterns for server-driven interactivity
---
# Alpine.js Advanced Patterns

## Scope

**What This Rule Covers:**
Alpine.store global state, `$dispatch` events, `$nextTick`, `init`/`destroy` lifecycle, `x-effect`, `x-transition`, official plugins and debugging.

**When to Load This Rule:**
When Alpine state spans components, needs lifecycle cleanup, animation or plugins; load `421-javascript-alpinejs-core.md` first.

## Contract

### Inputs and Prerequisites

- Core Alpine context from `421-javascript-alpinejs-core.md`, installed Alpine and plugin versions, and existing stores/events/components.
- State ownership, persistence and privacy requirements, motion/accessibility needs and available browser test tooling.

### Mandatory

- Register stores, components and plugins in `alpine:init` (CDN) or before `Alpine.start()` (bundled). Use a store only for state genuinely shared across components; keep local state in `x-data`.
- Mutate store properties or call store methods rather than replacing a registered store object at runtime, which drops references held by components and store `init()` logic.
- Do not persist secrets, tokens or sensitive personal data with `@alpinejs/persist`/localStorage; namespace persisted keys, handle absent or malformed values and plan schema changes.
- `$dispatch` events bubble from the dispatching element. Listen on an ancestor, or use `.window` for siblings and separate components; use descriptive kebab-case names and pass data in `$event.detail`.
- Use `$nextTick` when work depends on Alpine's DOM update, not arbitrary `setTimeout` delays.
- Anything created in `init` that outlives the element (timers, observers, global listeners, third-party widgets) is released in `destroy()` or by Alpine-managed listeners such as `@event.window`.
- `x-effect` and `$watch` callbacks stay side-effect-light, avoid writing the state they read (feedback loops) and are not used for derived values better expressed as getters.
- Use `x-transition` with `x-show`; honor `prefers-reduced-motion` and keep visibility state and focus correct for assistive technology.
- Async store/component actions check `response.ok`, catch and surface errors, keep previous valid state on failure and guard against stale or concurrent responses.
- Install only plugins the task needs, at versions compatible with the installed Alpine core, and follow each plugin's documented registration; `x-teleport` targets must exist and keep focus/accessibility intact.
- Debug with browser DevTools or an approved Alpine DevTools extension; remove temporary debug globals and logging before completion.
- Test cross-component events, store updates, persistence, cleanup and transitions in a browser or harness; do not claim lifecycle or leak correctness from static review alone.

### Execution Steps

1. Read existing stores, events, plugins and component lifecycles, and decide which state is local, shared or persisted.
2. Implement the minimal store/event/lifecycle/transition change with registered plugins and explicit cleanup.
3. Run available lint/tests and exercise multi-component, error, reduced-motion and teardown paths.
4. Report state ownership, events, plugins, verification evidence and remaining unverified behavior.

### Validation

- Stores registered once, mutated in place and limited to shared state; persisted data non-sensitive and versioned.
- Events reach intended listeners with documented detail; no reliance on sibling bubbling.
- Timers/listeners/observers cleaned up; effects free of feedback loops.
- Transitions respect reduced motion; plugin versions compatible; behavior verified or marked unverified.

## References

- [Alpine.store](https://alpinejs.dev/globals/alpine-store)
- [$dispatch](https://alpinejs.dev/magics/dispatch)
- [x-init and init()](https://alpinejs.dev/directives/init)
- [x-effect](https://alpinejs.dev/directives/effect)
- [x-transition](https://alpinejs.dev/directives/transition)
- [Persist plugin](https://alpinejs.dev/plugins/persist)
