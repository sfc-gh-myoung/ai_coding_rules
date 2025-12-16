# Alpine.js Core: Lightweight Reactivity Framework

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Alpine.js, reactivity, x-data, x-bind, x-on, x-model, x-show, x-if, magic properties, $el, $refs, $store, declarative, progressive enhancement, lightweight
**TokenBudget:** ~3350
**ContextTier:** Medium
**Depends:** rules/000-global-core.md

## Purpose

Provides comprehensive guidance for Alpine.js 3.x, a lightweight JavaScript framework for composing behavior directly in HTML markup through declarative directives, reactive data, and magic properties for progressive enhancement and interactive components.

## Rule Scope

Standalone Alpine.js 3.x usage in web applications (framework-agnostic, applies to all backends)

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **x-data** - Declare component scope with reactive data object
- **x-bind (`:`)** - Dynamically bind attributes to reactive data
- **x-on (`@`)** - Listen for DOM events and execute expressions
- **x-model** - Two-way data binding for form inputs
- **x-show vs x-if** - Toggle visibility (CSS) vs conditional rendering (DOM)
- **Magic properties** - Use `$el`, `$refs`, `$store`, `$dispatch`, `$watch`, `$nextTick` for advanced patterns

**Pre-Execution Checklist:**
- [ ] Alpine.js 3.x library loaded (CDN or npm)
- [ ] x-data components properly scoped
- [ ] x-cloak directive used to prevent flash of unstyled content
- [ ] Event handlers use correct syntax (@click, not onclick)
- [ ] Alpine.data() used for reusable components
- [ ] Magic properties understood ($el, $refs, $store)

## Contract

<inputs_prereqs>
Alpine.js 3.x library; basic HTML/JavaScript knowledge; understanding of reactive programming concepts; modern browser (Chrome, Firefox, Safari, Edge)
</inputs_prereqs>

<mandatory>
Alpine.js 3.x library (CDN or npm); x-data directive for component scope; proper directive syntax; x-cloak for FOUC prevention
</mandatory>

<forbidden>
Using Alpine.js 2.x syntax; mixing jQuery with Alpine; direct DOM manipulation inside Alpine components; missing x-data scope; using x-html with untrusted content
</forbidden>

<steps>
1. Load Alpine.js library in HTML (CDN or bundler)
2. Define component scope with x-data directive
3. Add x-cloak directive and CSS to prevent flash
4. Use directives (x-bind, x-on, x-text, x-model, x-show, x-if, x-for) within scope
5. Leverage magic properties ($el, $refs, $store) for advanced patterns
6. Extract reusable components with Alpine.data()
7. Test in browser with dev tools open
</steps>

<output_format>
HTML with Alpine.js directives, optional JavaScript for Alpine.data() registration, CSS for x-cloak
</output_format>

<validation>
- Alpine.js directives trigger reactive updates correctly
- Data binding reflects state changes in real-time
- Event handlers execute without errors
- x-cloak prevents flash of unstyled content
- Components are reusable with Alpine.data()
- No console errors in browser dev tools
</validation>

## Key Principles

### 1. Core Directives

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
    <!-- Long form -->
    <button x-bind:class="isActive ? 'active' : ''">Button</button>

    <!-- Short form (preferred) -->
    <button :class="isActive ? 'active' : ''">Button</button>

    <!-- Multiple attributes -->
    <input :disabled="!isActive" :value="count">
</div>
```

**Event Handling (x-on or `@`):**
```html
<div x-data="{ count: 0 }">
    <!-- Long form -->
    <button x-on:click="count++">Increment</button>

    <!-- Short form (preferred) -->
    <button @click="count++">Increment</button>

    <!-- Call methods -->
    <button @click="increment()">Increment</button>

    <!-- Event modifiers -->
    <button @click.prevent="submit()">Submit</button>
    <input @keyup.enter="search()">
    <div @click.outside="close()">Modal</div>
</div>
```

**Text Content (x-text):**
```html
<div x-data="{ message: 'Hello Alpine' }">
    <span x-text="message"></span>
    <!-- Output: Hello Alpine -->
</div>
```

**HTML Content (x-html):**
```html
<div x-data="{ content: '<strong>Bold</strong>' }">
    <div x-html="content"></div>
    <!-- Output: Bold (rendered HTML) -->
    <!-- WARNING: Only use with trusted content to prevent XSS -->
</div>
```

**Two-Way Binding (x-model):**
```html
<div x-data="{ search: '' }">
    <input type="text" x-model="search" placeholder="Search...">
    <p>Searching for: <span x-text="search"></span></p>
</div>

<!-- Modifiers -->
<input x-model.number="age">        <!-- Convert to number -->
<input x-model.debounce.500ms="search"> <!-- Debounce 500ms -->
<input x-model.lazy="email">        <!-- Update on change, not input -->
```

**Visibility Toggle (x-show):**
```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>

    <!-- x-show: Element stays in DOM, uses CSS display -->
    <div x-show="open">
        Content (toggle CSS display)
    </div>
</div>
```

**Conditional Rendering (x-if):**
```html
<div x-data="{ show: false }">
    <button @click="show = !show">Toggle</button>

    <!-- x-if: Element added/removed from DOM -->
    <template x-if="show">
        <div>Content (added/removed from DOM)</div>
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
</div>

<!-- With index -->
<template x-for="(item, index) in items" :key="index">
    <li><span x-text="index + 1"></span>: <span x-text="item"></span></li>
</template>
```

### 2. Reactivity System

**Methods in x-data:**
```html
<div x-data="{
    count: 0,
    increment() {
        this.count++
    },
    reset() {
        this.count = 0
    }
}">
    <button @click="increment()">Count: <span x-text="count"></span></button>
    <button @click="reset()">Reset</button>
</div>
```

**Computed Properties (Getters):**
```html
<div x-data="{
    items: ['foo', 'bar', 'baz'],
    search: '',
    get filteredItems() {
        return this.items.filter(
            i => i.startsWith(this.search)
        )
    }
}">
    <input x-model="search" placeholder="Search...">
    <ul>
        <template x-for="item in filteredItems" :key="item">
            <li x-text="item"></li>
        </template>
    </ul>
</div>
```

**Watchers ($watch magic):**
```html
<div x-data="{
    count: 0,
    init() {
        this.$watch('count', value => {
            console.log('Count changed to:', value)
        })
    }
}">
    <button @click="count++">Increment</button>
</div>
```

### 3. Magic Properties

**$el - Current Element Reference:**
```html
<button @click="$el.innerHTML = 'Clicked!'">
    Click me
</button>

<div x-data="{ init() { console.log(this.$el) } }">
    <!-- Logs the div element -->
</div>
```

**$refs - Named Element References:**
```html
<div x-data>
    <input type="text" x-ref="content">
    <button @click="navigator.clipboard.writeText($refs.content.value)">
        Copy
    </button>
</div>
```

**$store - Global State:**
```html
<!-- Register store -->
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.store('darkMode', {
            on: false,
            toggle() {
                this.on = !this.on
            }
        })
    })
</script>

<!-- Access store -->
<div x-data>
    <button @click="$store.darkMode.toggle()">
        Toggle: <span x-text="$store.darkMode.on"></span>
    </button>
</div>
```

**$dispatch - Custom Events:**
```html
<div x-data @notify="alert($event.detail.message)">
    <button @click="$dispatch('notify', { message: 'Hello!' })">
        Notify
    </button>
</div>

<!-- Cross-component communication -->
<div x-data @custom-event.window="console.log('Received')">
    <!-- Listens globally -->
</div>
```

**$watch - Reactive Side Effects:**
```html
<div x-data="{
    open: false,
    init() {
        this.$watch('open', value => {
            if (value) {
                document.body.style.overflow = 'hidden'
            } else {
                document.body.style.overflow = ''
            }
        })
    }
}">
    <button @click="open = !open">Toggle Modal</button>
</div>
```

**$nextTick - Wait for DOM Update:**
```html
<div x-data="{ count: 0 }">
    <span x-text="count"></span>
    <button @click="
        count++
        $nextTick(() => {
            console.log('DOM updated, count is:', $el.previousElementSibling.textContent)
        })
    ">Increment</button>
</div>
```

**$root - Root Component Access:**
```html
<div x-data="{ message: 'Hello' }">
    <div x-data="{ localMessage: 'World' }">
        <span x-text="$root.message"></span>
        <!-- Accesses parent's message -->
    </div>
</div>
```

**$data - Component Data Object:**
```html
<div x-data="{ name: 'Alpine', version: 3 }">
    <button @click="console.log($data)">
        Log Data
        <!-- Logs: { name: 'Alpine', version: 3 } -->
    </button>
</div>
```

### 4. Component Patterns

**Alpine.data() - Reusable Components:**
```html
<!-- Register component -->
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.data('dropdown', () => ({
            open: false,
            toggle() {
                this.open = !this.open
            },
            close() {
                this.open = false
            }
        }))
    })
</script>

<!-- Use component multiple times -->
<div x-data="dropdown">
    <button @click="toggle()">Toggle</button>
    <div x-show="open" @click.outside="close()">
        Dropdown content
    </div>
</div>

<div x-data="dropdown">
    <!-- Another instance -->
</div>
```

**Component Parameters:**
```html
<script>
    Alpine.data('dropdown', (initialOpen = false) => ({
        open: initialOpen,
        toggle() {
            this.open = !this.open
        }
    }))
</script>

<!-- Pass parameters -->
<div x-data="dropdown(true)">
    <!-- Starts open -->
</div>
```

**Alpine.store() - Global Stores:**
```html
<script>
    document.addEventListener('alpine:init', () => {
        Alpine.store('tabs', {
            current: 'first',
            items: ['first', 'second', 'third']
        })
    })
</script>

<!-- Access from any component -->
<div x-data>
    <button
        x-for="tab in $store.tabs.items"
        @click="$store.tabs.current = tab"
        :class="$store.tabs.current === tab && 'active'">
        <span x-text="tab"></span>
    </button>
</div>
```

### 5. Lifecycle Hooks

**x-init - Initialization:**
```html
<div x-data="{ message: '' }" x-init="message = 'Initialized!'">
    <span x-text="message"></span>
</div>

<!-- With async initialization -->
<div x-data="{ data: null }"
     x-init="data = await (await fetch('/api/data')).json()">
    <span x-text="data"></span>
</div>
```

**init() Method:**
```html
<script>
    Alpine.data('timer', () => ({
        count: 0,
        interval: null,
        init() {
            this.interval = setInterval(() => {
                this.count++
            }, 1000)
        },
        destroy() {
            clearInterval(this.interval)
        }
    }))
</script>

<div x-data="timer">
    <span x-text="count"></span> seconds
</div>
```

**x-effect - Reactive Side Effects:**
```html
<div x-data="{ count: 0 }" x-effect="console.log('Count is:', count)">
    <button @click="count++">Increment</button>
    <!-- Console logs on every count change -->
</div>
```

### 6. Advanced Patterns

**Preventing Flash (x-cloak):**
```html
<style>
    [x-cloak] { display: none !important; }
</style>

<div x-data="{ show: false }" x-cloak>
    <!-- Hidden until Alpine initializes -->
    <div x-show="show">Content</div>
</div>
```

**Transitions (x-transition):**
```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>

    <div x-show="open" x-transition>
        <!-- Animated with CSS transitions -->
        Fades in and out
    </div>

    <!-- Custom transition -->
    <div x-show="open"
         x-transition:enter="transition ease-out duration-300"
         x-transition:enter-start="opacity-0 transform scale-90"
         x-transition:enter-end="opacity-100 transform scale-100">
        Custom animation
    </div>
</div>
```

## Anti-Patterns and Common Mistakes

### Critical Violations

**Anti-Pattern 1: Missing x-data Scope**

Problem: Directives fail without component scope
Correct Pattern: Always wrap Alpine directives in x-data

**Anti-Pattern 2: Wrong this Context**

Problem: Arrow functions break `this` binding in methods
Correct Pattern: Use regular functions in methods to preserve `this`

**Anti-Pattern 3: x-html with User Input**

Problem: XSS vulnerability when using x-html with untrusted content
Correct Pattern: Only use x-html with trusted, sanitized content

**Anti-Pattern 4: Direct DOM Manipulation**

Problem: Bypasses Alpine's reactivity system
Correct Pattern: Use reactive data instead of direct DOM manipulation

### Common Pitfalls

**Pitfall 1: Missing x-data Scope**
```html
<!-- BAD: No x-data scope -->
<button @click="count++">Increment</button>

<!-- GOOD: Proper scope -->
<div x-data="{ count: 0 }">
    <button @click="count++">Increment: <span x-text="count"></span></button>
</div>
```

**Pitfall 2: Incorrect this Context**
```html
<div x-data="{
    count: 0,
    // BAD: Arrow function breaks this
    increment: () => {
        this.count++ // this is undefined
    }
}">
    <button @click="increment()">Broken</button>
</div>

<!-- GOOD: Regular function -->
<div x-data="{
    count: 0,
    increment() {
        this.count++ // this works correctly
    }
}">
    <button @click="increment()">Works</button>
</div>
```

**Pitfall 3: Mutating State from Template**
```html
<!-- BAD: Complex logic in template -->
<div x-data="{ items: [1, 2, 3] }">
    <button @click="items.push(items.length + 1); items.sort()">
        Add & Sort
    </button>
</div>

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

**Pitfall 4: Using x-show vs x-if Incorrectly**
```html
<!-- BAD: x-show for expensive components -->
<div x-show="showChart">
    <!-- Complex chart component always in DOM -->
</div>

<!-- GOOD: x-if removes from DOM when hidden -->
<template x-if="showChart">
    <div>
        <!-- Complex chart component -->
    </div>
</template>

<!-- x-show is fine for simple toggling -->
<div x-show="open">Simple content</div>
```

**Pitfall 5: Forgetting x-cloak**
```html
<!-- BAD: Flash of unstyled content -->
<div x-data="{ show: false }">
    <div x-show="show">Content</div>
</div>

<!-- GOOD: Prevent flash -->
<style>[x-cloak] { display: none !important; }</style>
<div x-data="{ show: false }" x-cloak>
    <div x-show="show">Content</div>
</div>
```

**Pitfall 6: Not Using x-model Modifiers**
```html
<!-- BAD: Manual parsing -->
<div x-data="{ age: 0 }">
    <input type="number" @input="age = parseInt($event.target.value)">
</div>

<!-- GOOD: Use .number modifier -->
<div x-data="{ age: 0 }">
    <input type="number" x-model.number="age">
</div>

<!-- BAD: No debouncing for search -->
<input x-model="search">

<!-- GOOD: Debounce search input -->
<input x-model.debounce.500ms="search">
```

**Pitfall 7: Nested x-data Scope Confusion**
```html
<div x-data="{ foo: 'bar' }">
    <span x-text="foo"></span> <!-- Works: "bar" -->

    <div x-data="{ foo: 'baz' }">
        <span x-text="foo"></span> <!-- Shows: "baz" (shadows parent) -->
        <span x-text="$root.foo"></span> <!-- Access parent: "bar" -->
    </div>
</div>
```

**Pitfall 8: Incorrect Event Handler Syntax**
```html
<!-- BAD: Using onclick instead of @click -->
<button onclick="count++">Won't work</button>

<!-- GOOD: Alpine syntax -->
<button @click="count++">Works</button>

<!-- BAD: Forgetting parentheses for methods with params -->
<button @click="setCount">Doesn't call method</button>

<!-- GOOD: Call with parentheses -->
<button @click="setCount(5)">Works</button>
```

**Pitfall 9: Memory Leaks (Missing destroy)**
```html
<script>
    // BAD: No cleanup
    Alpine.data('timer', () => ({
        interval: null,
        init() {
            this.interval = setInterval(() => {
                console.log('tick')
            }, 1000)
        }
        // Missing destroy() - interval keeps running
    }))

    // GOOD: Proper cleanup
    Alpine.data('timer', () => ({
        interval: null,
        init() {
            this.interval = setInterval(() => {
                console.log('tick')
            }, 1000)
        },
        destroy() {
            clearInterval(this.interval)
        }
    }))
</script>
```

**Pitfall 10: Not Using Alpine.data for Reusable Components**
```html
<!-- BAD: Duplicating inline component logic -->
<div x-data="{ open: false, toggle() { this.open = !this.open } }">
    <button @click="toggle()">Toggle</button>
</div>

<div x-data="{ open: false, toggle() { this.open = !this.open } }">
    <button @click="toggle()">Toggle</button>
</div>

<!-- GOOD: Extract to Alpine.data() -->
<script>
    Alpine.data('dropdown', () => ({
        open: false,
        toggle() { this.open = !this.open }
    }))
</script>

<div x-data="dropdown">
    <button @click="toggle()">Toggle</button>
</div>

<div x-data="dropdown">
    <button @click="toggle()">Toggle</button>
</div>
```

## Post-Execution Checklist

- [ ] Alpine.js 3.x library loaded successfully
- [ ] x-data components properly scoped
- [ ] x-cloak directive and CSS added to prevent flash
- [ ] Directives use correct syntax (@click, :class, not onclick, class=)
- [ ] Methods use regular functions (not arrow functions for this binding)
- [ ] x-show vs x-if used appropriately (visibility vs DOM)
- [ ] x-model modifiers applied (.number, .debounce, .lazy)
- [ ] Reusable components extracted with Alpine.data()
- [ ] Magic properties used correctly ($el, $refs, $store)
- [ ] No XSS vulnerabilities (x-html only with trusted content)
- [ ] Lifecycle cleanup implemented (destroy() for intervals/listeners)
- [ ] Tested in target browsers

## Validation

**Success Checks:**
- Alpine.js directives trigger reactive updates without errors
- Data binding reflects state changes in real-time
- Event handlers execute correctly
- x-cloak prevents flash of unstyled content
- Components are reusable and maintainable
- No console errors in browser dev tools
- Reactivity works as expected (getters, watchers)

**Negative Tests:**
- Missing x-data scope triggers warning/error
- Arrow functions in methods don't break this binding
- x-html with user input doesn't create XSS vulnerability
- Memory leaks caught (intervals cleaned up)

## Output Format Examples

### Complete Alpine.js Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alpine.js Example</title>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        [x-cloak] { display: none !important; }
        .active { background: blue; color: white; }
    </style>
</head>
<body>
    <!-- Simple Counter -->
    <div x-data="{ count: 0 }" x-cloak>
        <button @click="count++">Increment</button>
        <span x-text="count"></span>
    </div>

    <!-- Dropdown Component -->
    <div x-data="dropdown" x-cloak>
        <button @click="toggle()">Toggle Dropdown</button>
        <div x-show="open" @click.outside="close()" x-transition>
            <p>Dropdown content</p>
        </div>
    </div>

    <!-- Search with Computed Properties -->
    <div x-data="{
        search: '',
        items: ['foo', 'bar', 'baz', 'foobar'],
        get filteredItems() {
            return this.items.filter(i => i.includes(this.search))
        }
    }" x-cloak>
        <input x-model.debounce.300ms="search" placeholder="Search...">
        <ul>
            <template x-for="item in filteredItems" :key="item">
                <li x-text="item"></li>
            </template>
        </ul>
    </div>

    <script>
        // Register reusable components
        document.addEventListener('alpine:init', () => {
            Alpine.data('dropdown', () => ({
                open: false,
                toggle() {
                    this.open = !this.open
                },
                close() {
                    this.open = false
                }
            }))
        })
    </script>
</body>
</html>
```

### Progressive Enhancement Pattern

```html
<!-- Server-rendered HTML with Alpine enhancement -->
<form action="/submit" method="POST" x-data="{
    email: '',
    password: '',
    errors: {},
    async handleSubmit(e) {
        e.preventDefault()
        this.errors = {}

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: this.email,
                    password: this.password
                })
            })

            if (!response.ok) {
                this.errors = await response.json()
            } else {
                window.location.href = '/dashboard'
            }
        } catch (error) {
            this.errors.general = 'Network error'
        }
    }
}">
    <div>
        <label for="email">Email:</label>
        <input
            type="email"
            id="email"
            name="email"
            x-model="email"
            required>
        <span x-show="errors.email" x-text="errors.email" class="error"></span>
    </div>

    <div>
        <label for="password">Password:</label>
        <input
            type="password"
            id="password"
            name="password"
            x-model="password"
            required>
        <span x-show="errors.password" x-text="errors.password" class="error"></span>
    </div>

    <button type="submit" @click.prevent="handleSubmit">Login</button>
    <span x-show="errors.general" x-text="errors.general" class="error"></span>
</form>
```

## References

### External Documentation
- [Alpine.js Start Here](https://alpinejs.dev/start-here) - Official getting started guide
- [Alpine.js Directives](https://alpinejs.dev/directives/) - Complete directive reference
- [Alpine.js Magics](https://alpinejs.dev/magics/) - Magic properties reference
- [Alpine.js Globals](https://alpinejs.dev/globals/) - Alpine.data, Alpine.store, Alpine.bind
- [Alpine.js Essentials](https://alpinejs.dev/essentials/installation) - Installation and core concepts
- [Alpine.js GitHub](https://github.com/alpinejs/alpine) - Source code and issues

### Related Rules
- **Global Core**: `rules/000-global-core.md` - Foundation for all rules
- **JavaScript Core**: `rules/420-javascript-core.md` - Modern JavaScript patterns
- **HTMX Frontend**: `rules/500-frontend-htmx-core.md` - Alternative lightweight framework
- **HTMX Integration**: `rules/221f-python-htmx-integrations.md` - Alpine.js + HTMX patterns (future reference)
