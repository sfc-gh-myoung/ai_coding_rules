# 421a-javascript-alpinejs-advanced

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.1.0
**LastUpdated:** 2026-03-09
**Keywords:** Alpine.js, stores, plugins, transitions, x-teleport, $dispatch, custom directives, advanced patterns, SSE, lifecycle, error recovery
**TokenBudget:** ~2700
**ContextTier:** Low
**Depends:** 421-javascript-alpinejs-core.md
**LoadTrigger:** kw:alpinejs-advanced, kw:alpine-stores, kw:alpine-plugins

## Scope

**What This Rule Covers:**
Advanced Alpine.js patterns including global stores, cross-component communication with $dispatch, transitions, lifecycle hooks, error recovery, plugins, and integration patterns.

**When to Load This Rule:**
- Working with Alpine.js global state management ($store)
- Implementing cross-component communication ($dispatch)
- Adding transitions and animations
- Using Alpine.js plugins (x-teleport, intersect, persist)
- Handling lifecycle hooks (init/destroy)
- Debugging Alpine.js applications

## References

### Dependencies

**Must Load First:**
- **421-javascript-alpinejs-core.md** - Core Alpine.js directives and reactivity

**Related:**
- **420-javascript-core.md** - JavaScript patterns and best practices
- **500-frontend-htmx-core.md** - HTMX patterns for server-driven interactivity

## Contract

### Inputs and Prerequisites

- Alpine.js 3.x loaded (CDN or npm)
- Core Alpine.js directives understood (see `421-javascript-alpinejs-core.md`)
- Modern browser with dev tools

### Mandatory

- MUST clean up side effects in destroy() when using init() with intervals, listeners, or subscriptions
- MUST use $dispatch for cross-component communication instead of direct DOM events
- MUST use Alpine.store() for state shared across 3+ components
- MUST NOT use x-html with untrusted content in advanced patterns (XSS risk)

### Forbidden

- Skipping destroy() cleanup when init() creates intervals or event listeners
- Using window-level global variables instead of Alpine.store()
- Nested ternaries or logic exceeding 80 characters in template attributes

### Execution Steps

1. Identify state shared across 3+ components; move to Alpine.store()
2. Replace custom window events with $dispatch
3. Add init()/destroy() lifecycle hooks for side effects
4. Apply x-transition for visibility animations
5. Install Alpine.js DevTools extension for debugging

### Output Format

HTML with advanced Alpine.js patterns:
- Alpine.store() for global state management
- $dispatch for cross-component events
- init()/destroy() lifecycle hooks
- x-transition directives for animations

### Validation

**Pre-Task-Completion Checks:**
- [ ] All init() hooks with side effects have matching destroy() cleanup
- [ ] Global state uses Alpine.store(), not window variables
- [ ] Cross-component events use $dispatch, not custom DOM events
- [ ] Template logic under 80 characters per attribute

### Post-Execution Checklist

- [ ] No memory leaks (intervals, listeners cleaned up in destroy)
- [ ] Alpine.js DevTools shows expected store state
- [ ] Transitions render smoothly without layout shifts
- [ ] No console errors in browser dev tools

### Success Criteria

- Store changes via `Alpine.store('name').prop = value` reflect across all consuming components immediately
- `$dispatch` events are received by all target listeners (verify with console.log in handler)
- No interval or listener leaks after component removal (verify in DevTools, Memory tab: take heap snapshot before and after component removal)
- Transitions complete without janky repaints (check Performance tab for layout thrashing)
- `x-init` async operations complete and update component state correctly

## Key Principles

### Global Stores (Alpine.store)

```html
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.store('darkMode', {
            on: false,
            toggle() { this.on = !this.on }
        })
    })
</script>

<div x-data>
    <button @click="$store.darkMode.toggle()">
        Toggle: <span x-text="$store.darkMode.on"></span>
    </button>
</div>
```

> **Reactivity Warning:** Do not replace entire store objects — this breaks existing reactive bindings:
> ```javascript
> // BAD: Replaces the proxy, breaks reactivity
> Alpine.store('darkMode', { on: true, toggle() { this.on = !this.on } })
>
> // GOOD: Modify properties on the existing store
> Alpine.store('darkMode').on = true
> ```
> If you need to reset a store, update each property individually or use `Object.assign(Alpine.store('name'), defaults)`.

### Cross-Component Communication ($dispatch)

```html
<div x-data @notify="alert($event.detail.message)">
    <button @click="$dispatch('notify', { message: 'Hello!' })">Notify</button>
</div>

<!-- Cross-component communication -->
<div x-data @custom-event.window="console.log('Received')">
    <!-- Listens globally -->
</div>
```

> **Important:** `$dispatch` events bubble through the DOM and stop at `x-data` boundaries. Sibling components cannot hear each other's events by default. Use the `.window` modifier to listen globally: `@custom-event.window="handler()"`. Without `.window`, events dispatched from one component won't reach sibling or unrelated components.

**When to use `.window`:**
- Cross-component communication between siblings or unrelated components
- Global notifications or status updates
- Theme/mode toggling across the entire page

**When NOT to use `.window`:**
- Parent-child communication within the same x-data tree (events bubble naturally)
- Component-internal events

### DOM Update Timing ($nextTick)

```html
<div x-data="{ count: 0 }">
    <span x-text="count"></span>
    <button @click="count++; $nextTick(() => console.log('DOM updated'))">
        Increment
    </button>
</div>
```

### Lifecycle Hooks

**x-init and init() Method:**
```html
<!-- Inline initialization -->
<div x-data="{ message: '' }" x-init="message = 'Initialized!'">
    <span x-text="message"></span>
</div>

<!-- Async initialization -->
<div x-data="{ data: null }"
     x-init="data = await (await fetch('/api/data')).json()">
    <span x-text="data"></span>
</div>

<!-- Component with init/destroy lifecycle -->
<script>
    Alpine.data('timer', () => ({
        count: 0,
        interval: null,
        init() {
            this.interval = setInterval(() => this.count++, 1000)
        },
        destroy() {
            clearInterval(this.interval)
        }
    }))
</script>
```

**x-effect - Reactive Side Effects:**
```html
<div x-data="{ count: 0 }" x-effect="console.log('Count is:', count)">
    <button @click="count++">Increment</button>
</div>
```

### Transitions (x-transition)

```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    <div x-show="open" x-transition>Fades in and out</div>

    <!-- Custom transition classes -->
    <div x-show="open"
         x-transition:enter="transition ease-out duration-300"
         x-transition:enter-start="opacity-0 transform scale-90"
         x-transition:enter-end="opacity-100 transform scale-100">
        Custom animation
    </div>
</div>
```

### Error Recovery Patterns

**CDN Load Failure - Fallback Script:**
```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js"
        onerror="loadAlpineFallback()"></script>
<script>
const ALPINE_VERSION = '3.14.8';
function loadAlpineFallback() {
    const s = document.createElement('script');
    s.src = `https://unpkg.com/alpinejs@${ALPINE_VERSION}/dist/cdn.min.js`;
    s.defer = true;
    document.head.appendChild(s);
}
</script>
```

> **Version management:** Define `ALPINE_VERSION` once and reference it in both primary and fallback URLs. Pin to exact patch version (e.g., `3.14.8`, not `3.14`).

**Alpine Initialization Failure:**
```html
<script>
document.addEventListener('alpine:init', () => {
    try {
        Alpine.data('myComponent', () => ({ /* ... */ }))
        Alpine.store('myStore', { /* ... */ })
    } catch (e) {
        console.error('Alpine init failed:', e);
        document.querySelectorAll('[x-cloak]').forEach(el => {
            el.removeAttribute('x-cloak');
        });
    }
})
</script>
```

**Async x-init Failure:**
```html
<div x-data="{ data: null, error: null }"
     x-init="
        try {
            data = await (await fetch('/api/data')).json()
        } catch (e) {
            error = 'Failed to load data'
            console.error('x-init fetch failed:', e)
        }
     ">
    <div x-show="error" x-text="error" class="error"></div>
    <div x-show="data" x-text="JSON.stringify(data)"></div>
</div>
```

### Debugging with Alpine.js DevTools

- Install the Alpine.js DevTools browser extension for component inspection
- In browser console, access component data: `$el.__x.$data` or `Alpine.evaluate(el, 'expression')`
- Inspect global stores: `Alpine.store('storeName')`
- Use `$refs` to inspect named element references from component scope

## Anti-Patterns and Common Mistakes

**Pitfall: Complex Logic in Templates**

Problem: Template attributes with excessive logic are hard to read, debug, and maintain.
Correct Pattern: Extract template logic when: (1) attribute logic exceeds 80 characters, (2) contains nested ternaries, (3) chains more than 3 method calls, or (4) uses more than 2 boolean operators.

```html
<!-- BAD: Hard to read and maintain -->
<!-- NOTE: items.sort() mutates the original array (violates 420-javascript-core immutability mandate) -->
<button @click="items.push(items.length + 1); items.sort()">Add & Sort</button>

<!-- GOOD: Extract to method -->
<div x-data="{
    items: [1, 2, 3],
    addAndSort() {
        this.items.push(this.items.length + 1)
        this.items.sort()
    }
}">
    <button @click="addAndSort()">Add & Sort</button>
</div>
```

> **Cross-rule note:** `items.sort()` mutates the original array. Per `420-javascript-core`, use `items.toSorted()` (ES2023+) or `[...items].sort()` for a non-mutating sort. In Alpine.js templates, prefer a computed getter: `get sortedItems() { return this.items.toSorted() }`.

**Pitfall: Memory Leaks (Missing destroy)**

Problem: Components with init() that create intervals or listeners leak memory when removed from the DOM.
Correct Pattern: Always pair init() side effects with destroy() cleanup.
```html
<!-- BAD: No cleanup -- interval keeps running after component removal -->
Alpine.data('timer', () => ({
    interval: null,
    init() { this.interval = setInterval(() => console.log('tick'), 1000) }
}))

<!-- GOOD: Proper cleanup -->
Alpine.data('timer', () => ({
    interval: null,
    init() { this.interval = setInterval(() => console.log('tick'), 1000) },
    destroy() { clearInterval(this.interval) }
}))
```

**Pitfall: Duplicating Inline Components**

Problem: Repeating the same inline x-data object across elements is error-prone and hard to maintain.
Correct Pattern: Extract to Alpine.data() when pattern appears 2+ times.
```html
<!-- BAD: Same logic repeated -->
<div x-data="{ open: false, toggle() { this.open = !this.open } }">...</div>
<div x-data="{ open: false, toggle() { this.open = !this.open } }">...</div>

<!-- GOOD: Extract to Alpine.data() when pattern appears 2+ times -->
<script>
    Alpine.data('dropdown', () => ({
        open: false,
        toggle() { this.open = !this.open }
    }))
</script>
<div x-data="dropdown">...</div>
<div x-data="dropdown">...</div>
```
