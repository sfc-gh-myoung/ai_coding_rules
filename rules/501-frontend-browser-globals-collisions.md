# 501-frontend-browser-globals-collisions: Frontend Browser Globals Collisions

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** browser globals, javascript globals, window.history, HTMX history, Alpine.js, name collisions, reserved identifiers, implicit globals, historyRestore, hx-push-url, popstate, best practices, anti-patterns
**TokenBudget:** ~1400
**ContextTier:** High
**Depends:** 500-frontend-htmx-core.md

## Purpose

Prevent accidental collisions with built-in browser globals (e.g., `window.history`) that can break HTMX navigation, Alpine components, and browser back/forward behavior.
Codifies safe naming, scoping, and namespacing patterns for inline scripts and small frontend helpers.

## Scope

HTMX-driven UIs and server-rendered apps that embed JavaScript/Alpine helpers (<50 lines) in templates (including inline `<script>` blocks).

## References

### Related Rules
- `rules/500-frontend-htmx-core.md` - HTMX frontend usage and lifecycle events
- `rules/221f-python-htmx-integrations.md` - Alpine.js + HTMX integration patterns

### External Documentation
- [MDN: `Window.history`](https://developer.mozilla.org/en-US/docs/Web/API/Window/history) - Browser history object
- [HTMX Events](https://htmx.org/events/) - `htmx:afterSwap` and `htmx:historyRestore` lifecycle hooks

## Contract

### Inputs and Prerequisites
Basic knowledge of browser global objects (`window`, `history`, `location`) and HTMX history (`hx-push-url`, history restoration).

### Mandatory
Ability to edit templates/JS; browser devtools access to verify history behavior; HTMX/Alpine loaded if used in the app.

**Essential Patterns:**
- **No globals by default:** Keep helpers module-scoped or namespaced; don't define top-level functions/vars that shadow browser globals
- **Avoid reserved browser identifiers:** Never name functions/vars: `history`, `location`, `event`, `name`, `top`, `parent`, `frames`, `self`, `window`, `document`, `navigator`, `screen`, `alert`, `confirm`, `prompt`, `open`, `close`, `length`, `status`
- **Namespace if you must expose:** If something must be referenced from HTML (`x-data="..."`), expose it under a single app namespace (e.g., `window.unistore.*`)

### Forbidden
Creating new top-level globals named after browser APIs; using implicit globals; "fixing" by disabling HTMX history unless explicitly requested.

### Execution Steps
1. Identify all JS entry points: base template scripts, page templates, and any static JS bundles.
2. Scan for collisions with browser globals (especially `history`, `location`, `event`) and for implicit globals.
3. Rename colliding identifiers and update all call sites (HTML attributes like `x-data="..."` included).
4. Prefer namespacing component factories under a single app object: `window.<app>.<feature> = (...) => ({ ... })`.
5. Validate navigation: click-through navbar, use browser back/forward, and confirm HTMX content restores correctly.

### Output Format
Template and/or JS changes that remove browser-global collisions (renames + namespacing), plus updated references in HTML.

### Validation
- Browser back/forward works without manual refresh on HTMX-swapped pages
- `window.history` remains an object (not a function) in console: `typeof window.history === "object"`
- No console errors during `htmx:afterSwap` / `htmx:historyRestore` / `popstate`

### Post-Execution Checklist
- [ ] No top-level `history`, `location`, or `event` identifiers introduced
- [ ] No implicit globals (missing `const`/`let`) introduced
- [ ] HTMX navigation works (click links, `hx-push-url`, back/forward restore)
- [ ] Alpine component factories referenced from HTML are namespaced (or otherwise collision-safe)
- [ ] Rule references added where relevant (HTMX + integrations rules)

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Defining `function history()` (breaks HTMX/browser history)**
```html
<div x-data="history()"></div>
<script>
  function history() {
    return { /* ... */ };
  }
</script>
```
**Problem:** In browsers, `window.history` is a built-in object. A top-level `function history()` can overwrite it, breaking HTMX history management and back/forward navigation.

**Correct Pattern:**
```html
<div x-data="unistore.historyComponent()"></div>
<script>
  window.unistore = window.unistore ?? {};
  window.unistore.historyComponent = () => {
    return { /* ... */ };
  };
</script>
```
**Benefits:** Prevents collisions, keeps a single global namespace, and remains stable across HTMX swaps.

**Anti-Pattern 2: Implicit globals via missing `const`/`let`**
```javascript
function init() {
  activeTab = window.location.pathname; // implicit global!
}
```
**Problem:** Creates/overwrites `window.activeTab`, leading to hard-to-debug cross-page coupling and swap-related bugs.

**Correct Pattern:**
```javascript
function init() {
  const activeTab = window.location.pathname;
  // ...
}
```
**Benefits:** Scoped state, predictable behavior across HTMX swaps, and fewer accidental collisions.

## Validation

**Success Checks:**
- In browser console: `typeof window.history === "object"`
- Back/forward restores content correctly on HTMX-driven navigation (`htmx:historyRestore` fires and UI updates)
- No console errors on navigation across all tabs

**Negative Tests:**
- If you intentionally add `function history(){}` at top-level, back/forward and/or HTMX history will break (this should be caught in review)
- If you remove `const`/`let` for a variable assignment, it should show up as `window.<name>` unexpectedly

## Output Format Examples

```bash
# In browser console (DevTools):
typeof window.history
// Expected: "object"
```

```html
<!-- Namespaced Alpine component factory -->
<div x-data="unistore.historyComponent()"></div>
```
