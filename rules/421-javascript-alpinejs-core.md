# Alpine.js Core: Lightweight Reactivity Framework

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-09
**Keywords:** Alpine.js, reactivity, x-data, x-bind, x-on, x-model, x-show, x-if, magic properties, $el, $refs, declarative, progressive enhancement, lightweight
**TokenBudget:** ~4250
**ContextTier:** Medium
**Depends:** 000-global-core.md
**LoadTrigger:** kw:alpinejs, kw:alpine

## Scope

**What This Rule Covers:**
Provides comprehensive guidance for Alpine.js 3.x, a lightweight JavaScript framework for composing behavior directly in HTML markup through declarative directives, reactive data, and magic properties for progressive enhancement and interactive components.

**When to Load This Rule:**
- Working with Alpine.js 3.x applications
- Adding interactivity to server-rendered HTML
- Implementing progressive enhancement patterns
- Building lightweight reactive components
- Choosing between Alpine.js and heavier frameworks

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **421a-javascript-alpinejs-advanced.md** - Stores, plugins, transitions, lifecycle, error recovery
- **420-javascript-core.md** - JavaScript patterns and best practices
- **500-frontend-htmx-core.md** - HTMX patterns for server-driven interactivity

### External Documentation

- [Alpine.js Official Docs](https://alpinejs.dev/) - Complete Alpine.js documentation
- [Alpine.js GitHub](https://github.com/alpinejs/alpine) - Source code and examples
- [Alpine Toolbox](https://www.alpinetoolbox.com/) - Community plugins and resources

## Contract

### Inputs and Prerequisites

- Alpine.js 3.x library (CDN or npm)
- Basic HTML/JavaScript knowledge
- Understanding of reactive programming concepts
- Modern browser (Chrome, Firefox, Safari, Edge)

### Mandatory

- MUST wrap Alpine directives inside x-data scope
- MUST add x-cloak CSS (`[x-cloak] { display: none !important; }`) to prevent FOUC
- MUST use Alpine.data() for reusable components (when pattern appears 2+ times)
- MUST use `<template>` wrapper for x-for and x-if directives
- MUST use regular functions (not arrow functions) for component methods

### Forbidden

- Using Alpine.js 2.x syntax
- Mixing jQuery with Alpine
- Direct DOM manipulation inside Alpine components
- Missing x-data scope
- Using x-html with untrusted content (XSS risk)

> **CSP Note:** Alpine.js evaluates inline expressions using `Function()`, which requires `unsafe-eval` in Content-Security-Policy. If your CSP blocks `unsafe-eval`, use the Alpine.js CSP build: `@alpinejs/csp` (see [Alpine CSP docs](https://alpinejs.dev/advanced/csp)). The CSP build requires all expressions to be defined in JavaScript rather than inline attributes.

### Execution Steps

1. Load Alpine.js library in HTML (CDN or bundler)
2. Define component scope with x-data directive
3. Add x-cloak directive and CSS to prevent flash
4. Use directives (x-bind, x-on, x-text, x-model, x-show, x-if, x-for) within scope
5. Leverage magic properties ($el, $refs, $store) for advanced patterns
6. Extract reusable components with Alpine.data()
7. Test in browser with dev tools open

### Output Format

HTML with Alpine.js directives:
- x-data for component scope
- Directive attributes for reactivity
- Optional JavaScript for Alpine.data() registration
- CSS for x-cloak styling

### Validation

**Pre-Task-Completion Checks:**
- [ ] Alpine.js 3.x library loaded (CDN or npm)
- [ ] Grep for @click, x-bind, x-show, x-model outside x-data scope returns 0 results
- [ ] x-cloak directive and `[x-cloak] { display: none !important; }` CSS present
- [ ] Event handlers use correct syntax (@click, not onclick)
- [ ] Extract to Alpine.data() when component pattern appears 2+ times
- [ ] Magic properties used when component needs element refs ($refs), global state ($store), or event dispatch ($dispatch)

**Success Criteria:**
- All @click handlers execute without console errors
- State changes reflect in DOM within one event loop tick
- x-cloak prevents flash of unstyled content
- No console errors in browser dev tools

### Post-Execution Checklist

- [ ] Alpine.js 3.x library loaded correctly
- [ ] Grep for directives outside x-data scope returns 0 results
- [ ] x-cloak directive and CSS implemented
- [ ] Event handlers use @ syntax
- [ ] Reactive data bindings work correctly
- [ ] Reusable components extracted with Alpine.data()
- [ ] No console errors in browser

### Design Principles

- **Progressive Enhancement:** Start with semantic HTML, add interactivity with Alpine
- **Declarative Syntax:** Express behavior through HTML attributes, not imperative JavaScript
- **Lightweight:** Small JavaScript footprint (~15KB gzipped)
- **Reactive Data:** Changes to data automatically update the DOM
- **Component Scoping:** Each x-data creates an isolated reactive scope

### Error Recovery

**Alpine.js CDN Load Failure:**
If the Alpine.js script fails to load (network error, CDN outage), the page renders with raw Alpine directives visible. Add an `onerror` fallback:

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js"
        onerror="document.querySelectorAll('[x-cloak]').forEach(el => el.removeAttribute('x-cloak'))">
</script>
```

This removes x-cloak so content is at least visible. For critical applications, add a fallback CDN:

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js"
        onerror="this.onerror=null; this.src='https://unpkg.com/alpinejs@3.14.8/dist/cdn.min.js'">
</script>
```

**x-data Parse Error:**
If inline x-data object syntax has a typo (missing comma, unquoted key in wrong context), Alpine silently fails to initialize that component. Debugging steps:
1. Check browser console for Alpine.js initialization errors
2. Common cause: trailing comma in inline object literal — `x-data="{ a: 1, }"` fails in some browsers
3. Move complex data to `Alpine.data()` registration for better error messages:
```html
<script>
document.addEventListener('alpine:init', () => {
    Alpine.data('myComponent', () => ({
        // IDE will catch syntax errors here
        a: 1,
        b: 2
    }))
})
</script>
<div x-data="myComponent">...</div>
```

**alpine:init Timing:**
If `Alpine.data()` is called after Alpine initializes, components using that data won't work. Ensure registration scripts run before Alpine loads:
```html
<!-- Registration BEFORE Alpine -->
<script>
document.addEventListener('alpine:init', () => {
    Alpine.data('myComponent', () => ({ /* ... */ }))
})
</script>
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js"></script>
```

## Key Principles

### Core Directives

**Data Declaration (x-data):**
```html
<!-- Inline data object -->
<div x-data="{ open: false, count: 0 }">
    <!-- Component scope -->
</div>

<!-- Reusable component (see Alpine.data section) -->
<div x-data="dropdown">
    <!-- Uses registered component -->
</div>

<!-- Empty scope (for directives only) -->
<div x-data>
    <button @click="alert('Hello')">Click</button>
</div>
```

**Attribute Binding (x-bind or `:`):**
```html
<div x-data="{ isActive: true }">
    <!-- Short form (preferred) -->
    <button :class="isActive ? 'active' : ''">Button</button>
    <input :disabled="!isActive" :value="count">
</div>
```

**Event Handling (x-on or `@`):**
```html
<div x-data="{ count: 0 }">
    <!-- Short form (preferred) -->
    <button @click="count++">Increment</button>
    <button @click.prevent="submit()">Submit</button>
    <input @keyup.enter="search()">
    <div @click.outside="close()">Modal</div>
</div>
```

**Text and HTML Content:**
```html
<div x-data="{ message: 'Hello Alpine' }">
    <span x-text="message"></span>
</div>

<!-- WARNING: Only use x-html with trusted content to prevent XSS -->
<div x-data="{ content: '<strong>Bold</strong>' }">
    <div x-html="content"></div>
</div>
```

**Two-Way Binding (x-model):**
```html
<div x-data="{ search: '' }">
    <input type="text" x-model="search" placeholder="Search...">
    <p>Searching for: <span x-text="search"></span></p>
</div>

<!-- Modifiers -->
<input x-model.number="age">
<input x-model.debounce.500ms="search">
<input x-model.lazy="email">
```

**Visibility Toggle (x-show) vs Conditional Rendering (x-if):**
```html
<div x-data="{ open: false, showChart: false }">
    <button @click="open = !open">Toggle</button>

    <!-- x-show: stays in DOM, toggles CSS display (fast for simple content) -->
    <div x-show="open">Simple content</div>

    <!-- x-if: adds/removes from DOM (use for expensive components) -->
    <template x-if="showChart">
        <div>Complex chart component</div>
    </template>
</div>
```

**List Rendering (x-for):**
```html
<div x-data="{ items: ['Apple', 'Banana', 'Cherry'] }">
    <ul>
        <template x-for="item in items" :key="item">
            <li x-text="item"></li>
        </template>
    </ul>
    <!-- Empty state: x-for renders nothing when array is empty (no error) -->
    <div x-show="items.length === 0">No items found.</div>
</div>
```

### Reactivity System

**Methods and Computed Properties:**
```html
<div x-data="{
    count: 0,
    items: ['foo', 'bar', 'baz'],
    search: '',
    increment() { this.count++ },
    reset() { this.count = 0 },
    get filteredItems() {
        return this.items.filter(i => i.startsWith(this.search))
    }
}">
    <button @click="increment()">Count: <span x-text="count"></span></button>
    <button @click="reset()">Reset</button>
    <input x-model="search" placeholder="Search...">
    <ul>
        <template x-for="item in filteredItems" :key="item">
            <li x-text="item"></li>
        </template>
    </ul>
</div>
```

**$watch - Reactive Side Effects:**
```html
<div x-data="{
    open: false,
    init() {
        this.$watch('open', value => {
            document.body.style.overflow = value ? 'hidden' : ''
        })
    }
}">
    <button @click="open = !open">Toggle Modal</button>
</div>
```

### Magic Properties

**$el, $refs, $root, $data:**
```html
<div x-data="{ message: 'Hello' }">
    <!-- $el: current element -->
    <button @click="$el.innerHTML = 'Clicked!'">Click me</button>

    <!-- $refs: named element references -->
    <input type="text" x-ref="content">
    <button @click="navigator.clipboard.writeText($refs.content.value)">Copy</button>

    <!-- $root: access root component data from nested scope -->
    <div x-data="{ local: 'World' }">
        <span x-text="$root.message"></span>
    </div>

    <!-- $data: introspect component data -->
    <button @click="console.log($data)">Log Data</button>
</div>
```

For `$store` (global state), `$dispatch` (cross-component events), and `$nextTick` (DOM update timing), see `421a-javascript-alpinejs-advanced.md`.

**Nested x-data Scopes:**
Nested `x-data` creates child scopes. Child components can access parent data, but child data with the same name shadows parent data:

```html
<div x-data="{ name: 'parent', shared: 'from parent' }">
    <p x-text="name"></p> <!-- "parent" -->
    <div x-data="{ name: 'child' }">
        <p x-text="name"></p>    <!-- "child" (shadowed) -->
        <p x-text="shared"></p>  <!-- "from parent" (inherited) -->
    </div>
</div>
```

To explicitly access the root component's data from a nested scope, use `$root`:
```html
<div x-data="{ name: 'parent' }">
    <div x-data="{ name: 'child' }">
        <p x-text="$root.name"></p> <!-- "parent" via $root -->
    </div>
</div>
```

### Component Patterns

**Alpine.data() - Reusable Components:**
```html
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('dropdown', (initialOpen = false) => ({
            open: initialOpen,
            toggle() { this.open = !this.open },
            close() { this.open = false }
        }))
    })
</script>

<!-- Reuse across page -->
<div x-data="dropdown">
    <button @click="toggle()">Toggle</button>
    <div x-show="open" @click.outside="close()" x-transition>Content</div>
</div>

<div x-data="dropdown(true)"><!-- Starts open --></div>
```

For lifecycle hooks (x-init, init/destroy), transitions (x-transition), and error recovery patterns, see `421a-javascript-alpinejs-advanced.md`.

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Missing x-data Scope**

Problem: Directives silently fail without component scope.
Correct Pattern: Always wrap Alpine directives in an x-data element.

```html
<!-- BAD: No x-data scope — directives silently fail -->
<button @click="count++">Increment</button>

<!-- GOOD: Proper scope -->
<div x-data="{ count: 0 }">
    <button @click="count++">Increment: <span x-text="count"></span></button>
</div>
```

**Anti-Pattern 2: Arrow Functions Break `this` Context**

Problem: Arrow functions do not bind `this` to the component data, causing undefined references.
Correct Pattern: Use regular function syntax for component methods.

```html
<!-- BAD: Arrow function — this is undefined -->
<div x-data="{
    count: 0,
    increment: () => { this.count++ }
}">
    <button @click="increment()">Broken</button>
</div>

<!-- GOOD: Regular function preserves this -->
<div x-data="{
    count: 0,
    increment() { this.count++ }
}">
    <button @click="increment()">Works</button>
</div>
```

**Anti-Pattern 3: x-html with User Input (XSS)**

Problem: Using x-html with unsanitized user input creates XSS vulnerabilities.
Correct Pattern: Use x-text for user-provided content; only use x-html with trusted, sanitized content.

```html
<!-- BAD: Renders unsanitized user input as HTML -->
<div x-data="{ userInput: '' }">
    <input x-model="userInput">
    <div x-html="userInput"></div>
</div>

<!-- GOOD: Use x-text for user content -->
<div x-data="{ userInput: '' }">
    <input x-model="userInput">
    <div x-text="userInput"></div>
</div>
```

**Pitfall 4: Direct DOM Manipulation**
```html
<!-- BAD: Bypasses reactivity -->
<div x-data="{ count: 0 }">
    <span id="counter"></span>
    <button @click="document.getElementById('counter').textContent = ++count">
        Increment
    </button>
</div>

<!-- GOOD: Let Alpine handle DOM updates -->
<div x-data="{ count: 0 }">
    <span x-text="count"></span>
    <button @click="count++">Increment</button>
</div>
```

**Pitfall 5: Complex Logic in Templates**

Extract template logic when: (1) attribute logic exceeds 80 characters, (2) contains nested ternaries, (3) chains more than 3 method calls, or (4) uses more than 2 boolean operators. See `421a-javascript-alpinejs-advanced.md` for additional anti-patterns (memory leaks, x-model modifiers, component duplication).

## Output Format Examples

### Essential Alpine.js Page Template

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.8/dist/cdn.min.js"
        integrity="sha256-..." crossorigin="anonymous"></script>
<style>[x-cloak] { display: none !important; }</style>

<div x-data="dropdown" x-cloak>
    <button @click="toggle()">Toggle</button>
    <div x-show="open" @click.outside="close()" x-transition>Content</div>
</div>

<script>
document.addEventListener('alpine:init', () => {
    Alpine.data('dropdown', () => ({
        open: false,
        toggle() { this.open = !this.open },
        close() { this.open = false }
    }))
})
</script>
```

> **Supply chain note:** Pin CDN URLs to exact patch versions (e.g., `@3.14.8`, not `@3.14`). Add `integrity` and `crossorigin` attributes for Subresource Integrity (SRI). Generate hash: `curl -s <url> | openssl dgst -sha256 -binary | openssl base64 -A`.

### Progressive Enhancement: Form with Validation

```html
<form action="/submit" method="POST" x-data="{
    email: '', password: '', errors: {},
    async handleSubmit() {
        this.errors = {}
        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: this.email, password: this.password })
            })
            if (!res.ok) this.errors = await res.json()
            else window.location.href = '/dashboard'
        } catch (e) { this.errors.general = 'Network error' }
    }
}">
    <input type="email" x-model="email" required>
    <span x-show="errors.email" x-text="errors.email" class="error"></span>
    <input type="password" x-model="password" required>
    <span x-show="errors.password" x-text="errors.password" class="error"></span>
    <button type="submit" @click.prevent="handleSubmit()">Login</button>
    <span x-show="errors.general" x-text="errors.general" class="error"></span>
</form>
```
