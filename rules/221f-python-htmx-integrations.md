# HTMX Frontend Integrations

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** alpinejs, hyperscript, tailwind, bootstrap, css frameworks, icon libraries, chartjs, frontend libraries, client-side enhancements, htmx integration, javascript frameworks
**TokenBudget:** ~1900
**ContextTier:** Low
**Depends:** rules/221-python-htmx-core.md

## Purpose

Provides integration patterns for using HTMX with popular frontend libraries and frameworks including Alpine.js, _hyperscript, CSS frameworks (Tailwind, Bootstrap), icon libraries, and visualization libraries.

## Rule Scope

HTMX applications integrating with frontend libraries for enhanced interactivity and styling

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Alpine.js for client-side state** - Use for dropdowns, toggles, local UI state
- **_hyperscript for inline behavior** - Simple event handling and DOM manipulation
- **CSS framework integration** - Tailwind/Bootstrap work seamlessly with HTMX
- **Icon libraries** - Use SVG sprites or icon fonts, load once globally
- **Chart libraries** - Re-initialize charts after HTMX swaps using `htmx:afterSwap` event

**Pre-Execution Checklist:**
- [ ] Frontend libraries loaded in base template
- [ ] Alpine.js/hyperscript integrated for client-side behavior
- [ ] CSS framework configured (if using Tailwind/Bootstrap)
- [ ] Icon library loaded (FontAwesome, Heroicons, etc.)
- [ ] Chart/visualization library initialization hooked to HTMX events
- [ ] No conflicts between HTMX and frontend libraries

## Contract

<inputs_prereqs>
HTMX core patterns (221-python-htmx-core.md); frontend library documentation; understanding of HTMX event lifecycle
</inputs_prereqs>

<mandatory>
HTMX library; chosen frontend libraries; event listeners for HTMX lifecycle; base template for script/CSS loading
</mandatory>

<forbidden>
jQuery (not recommended with HTMX); heavy JavaScript frameworks (React, Vue, Angular); conflicting event handlers; global state in JavaScript
</forbidden>

<steps>
1. Load HTMX and frontend libraries in base template
2. Configure Alpine.js or _hyperscript for client-side behavior
3. Style with CSS framework (Tailwind, Bootstrap, etc.)
4. Add icon library for UI elements
5. Hook chart/visualization library to HTMX events (htmx:afterSwap)
6. Test integration with HTMX swaps
7. Verify no conflicts or memory leaks
</steps>

<output_format>
Integrated application using HTMX with Alpine.js/_hyperscript, CSS framework, icons, and charts
</output_format>

<validation>
- Frontend libraries load correctly
- Alpine.js/hyperscript work after HTMX swaps
- CSS framework styles apply to dynamically loaded content
- Icons render in HTMX-loaded partials
- Charts re-initialize after swaps
- No console errors or memory leaks
</validation>

## Key Principles

### 1. Alpine.js Integration

**Setup:**
```html
{# base.html #}
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

**Dropdown with Alpine.js:**
```html
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle Menu</button>

    <div x-show="open" @click.away="open = false">
        <a href="#"
           hx-get="/profile"
           hx-target="#content"
           @click="open = false">Profile</a>
        <a href="#"
           hx-get="/settings"
           hx-target="#content"
           @click="open = false">Settings</a>
    </div>
</div>
```

**Modal with Alpine.js:**
```html
<div x-data="{ modalOpen: false }">
    <button @click="modalOpen = true">Open Modal</button>

    <div x-show="modalOpen"
         x-cloak
         @keydown.escape.window="modalOpen = false"
         class="modal-overlay">
        <div class="modal-content" @click.away="modalOpen = false">
            <button @click="modalOpen = false">Close</button>

            <div hx-get="/modal-content"
                 hx-trigger="load"
                 hx-swap="innerHTML">
                Loading...
            </div>
        </div>
    </div>
</div>
```

**Alpine.js Persists After HTMX Swaps:**
Alpine.js automatically re-initializes on DOM changes, so it works seamlessly with HTMX swaps.

**Alpine.js SSE Manager Pattern:**

When using Alpine.js to manage SSE connections and trigger HTMX refreshes, use camelCase custom events (NOT `sse:` prefix):

```html
<div x-data="statusPage()" x-init="init()">
    <!-- Use camelCase trigger, NOT sse:system_status -->
    <div id="status-display"
         hx-get="/status/content"
         hx-trigger="load, systemStatus"
         hx-swap="innerHTML">
    </div>
</div>

<script>
function statusPage() {
    return {
        init() {
            window.waitForSSEManager(() => {
                window.sseManager.connect('status', (data, event) => {
                    if (event.type === 'system_status') {
                        // ✓ GOOD: Use camelCase event name
                        htmx.trigger('#status-display', 'systemStatus');

                        // ❌ BAD: sse: prefix won't work from htmx.trigger()
                        // htmx.trigger('#status-display', 'sse:system_status');
                    }
                });
            });
        }
    };
}
</script>
```

See `rules/221g-python-htmx-sse.md` for comprehensive SSE patterns.

### 2. _hyperscript Integration

**Setup:**
```html
{# base.html #}
<script src="https://unpkg.com/hyperscript.org@0.9.12"></script>
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

**Simple Interactions:**
```html
{# Toggle class #}
<button _="on click toggle .active on #sidebar">
    Toggle Sidebar
</button>

{# Remove element #}
<div class="notification" _="on click remove me">
    Notification message
</div>

{# Smooth scroll #}
<button _="on click scroll #section into view smoothly">
    Scroll to Section
</button>
```

**Combined with HTMX:**
```html
<button hx-delete="/items/123"
        hx-target="#item-123"
        _="on htmx:afterRequest remove #item-123 with opacity fade">
    Delete with Animation
</button>

<form hx-post="/search"
      hx-target="#results"
      _="on htmx:beforeRequest add .loading to #results
         on htmx:afterRequest remove .loading from #results">
    <input type="search" name="q">
    <button type="submit">Search</button>
</form>
```

### 3. CSS Framework Integration

**Tailwind CSS:**
```html
{# base.html #}
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

```html
{# Tailwind styles apply to HTMX-loaded content #}
<button hx-get="/users"
        hx-target="#content"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
    Load Users
</button>

<div id="content" class="container mx-auto p-4">
    {# HTMX-loaded content inherits Tailwind classes #}
</div>
```

**Bootstrap 5:**
```html
{# base.html #}
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

```html
{# Bootstrap components work with HTMX #}
<button hx-get="/modal-content"
        hx-target="#modalBody"
        class="btn btn-primary"
        data-bs-toggle="modal"
        data-bs-target="#myModal">
    Open Modal
</button>

<div class="modal fade" id="myModal">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-body" id="modalBody">
                Loading...
            </div>
        </div>
    </div>
</div>
```

**Reinitializing Bootstrap Components:**
```javascript
// Reinitialize Bootstrap tooltips/popovers after HTMX swap
document.body.addEventListener('htmx:afterSwap', function(event) {
    // Reinitialize tooltips in swapped content
    const tooltips = event.detail.target.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(el => new bootstrap.Tooltip(el));

    // Reinitialize popovers
    const popovers = event.detail.target.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(el => new bootstrap.Popover(el));
});
```

### 4. Icon Libraries

**FontAwesome:**
```html
{# base.html #}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
```

```html
{# Icons work in HTMX-loaded partials #}
<button hx-delete="/items/123" hx-target="#item-123">
    <i class="fas fa-trash"></i> Delete
</button>

<button hx-get="/items/123/edit" hx-target="#item-123">
    <i class="fas fa-edit"></i> Edit
</button>
```

**Heroicons (SVG):**
```html
{# Inline SVG icons in partials #}
<button hx-delete="/items/123">
    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
    </svg>
    Delete
</button>
```

### 5. Chart and Visualization Libraries

**Chart.js Integration:**
```html
{# base.html #}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.3.0/dist/chart.umd.min.js"></script>
```

```javascript
// Initialize/update charts after HTMX swap
let chartInstances = {};

document.body.addEventListener('htmx:afterSwap', function(event) {
    const chartElements = event.detail.target.querySelectorAll('canvas.chart');

    chartElements.forEach(canvas => {
        const chartId = canvas.id;

        // Destroy existing chart if it exists
        if (chartInstances[chartId]) {
            chartInstances[chartId].destroy();
        }

        // Create new chart
        const ctx = canvas.getContext('2d');
        const data = JSON.parse(canvas.dataset.chartData);

        chartInstances[chartId] = new Chart(ctx, {
            type: canvas.dataset.chartType || 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: true
            }
        });
    });
});
```

```html
{# Partial with chart #}
<div hx-get="/chart-data" hx-trigger="every 10s">
    <canvas id="chart-1"
            class="chart"
            data-chart-type="line"
            data-chart-data='{"labels": ["Jan", "Feb"], "datasets": [...]}'></canvas>
</div>
```

**Destroying Charts Before Swap:**
```javascript
// Clean up charts before replacement
document.body.addEventListener('htmx:beforeSwap', function(event) {
    const chartElements = event.detail.target.querySelectorAll('canvas.chart');

    chartElements.forEach(canvas => {
        const chartId = canvas.id;
        if (chartInstances[chartId]) {
            chartInstances[chartId].destroy();
            delete chartInstances[chartId];
        }
    });
});
```

### 6. HTMX Event Lifecycle Hooks

**Common Integration Points:**
```javascript
// Before request - show loading state
document.body.addEventListener('htmx:beforeRequest', function(event) {
    event.detail.target.classList.add('loading');
});

// After request - hide loading state
document.body.addEventListener('htmx:afterRequest', function(event) {
    event.detail.target.classList.remove('loading');
});

// After swap - reinitialize plugins
document.body.addEventListener('htmx:afterSwap', function(event) {
    // Reinitialize select2, datepickers, etc.
    $(event.detail.target).find('.select2').select2();
    $(event.detail.target).find('.datepicker').datepicker();
});

// On error - display error message
document.body.addEventListener('htmx:responseError', function(event) {
    alert('Error: ' + event.detail.xhr.status);
});
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Not Reinitializing Plugins After Swaps

**Problem:** JavaScript plugins only initialized on page load, not after HTMX swaps.

**Why It Fails:** Plugins don't work on dynamically loaded content; broken UI.

**Correct Pattern:**
```javascript
function initPlugins(container) {
    $(container).find('.datepicker').datepicker();
}

document.body.addEventListener('htmx:afterSwap', function(event) {
    initPlugins(event.detail.target);
});
```

### Anti-Pattern 2: Memory Leaks from Chart Instances

**Problem:** Creating new chart instances without destroying old ones on swap.

**Why It Fails:** Memory leaks; performance degradation; canvas errors.

**Correct Pattern:**
```javascript
let chartInstance = null;
document.body.addEventListener('htmx:beforeSwap', function(event) {
    if (chartInstance) chartInstance.destroy();
});
document.body.addEventListener('htmx:afterSwap', function(event) {
    chartInstance = new Chart(ctx, {...});
});
```

## Post-Execution Checklist

- [ ] Frontend libraries loaded in base template
- [ ] Alpine.js or _hyperscript integrated for client-side behavior
- [ ] CSS framework styles apply to HTMX-loaded content
- [ ] Icons display correctly in partials
- [ ] Charts/visualizations reinitialize after swaps
- [ ] Event listeners hooked to HTMX lifecycle
- [ ] Memory cleanup implemented (destroy chart instances, etc.)
- [ ] No console errors after HTMX swaps
- [ ] Integration tested with multiple swap operations

## Validation

**Success Checks:**
- Alpine.js/hyperscript work after HTMX swaps
- CSS framework styles apply to dynamic content
- Icons render in HTMX-loaded partials
- Charts update correctly after data changes
- No memory leaks (check browser dev tools)

**Negative Tests:**
- Plugin cleanup prevents memory leaks
- Multiple swaps don't create duplicate event listeners

## Output Format Examples

### Complete Integration Example
```html
{# base.html #}
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HTMX with Frontend Integrations</title>

    {# CSS Frameworks #}
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    {# HTMX and Alpine.js #}
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

    {# Chart.js #}
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.3.0/dist/chart.umd.min.js"></script>
</head>
<body>
    {% block content %}{% endblock %}

    <script>
        // Reinitialize charts after HTMX swaps
        let charts = {};

        document.body.addEventListener('htmx:afterSwap', function(event) {
            // Clean up old charts
            Object.values(charts).forEach(chart => chart.destroy());
            charts = {};

            // Initialize new charts
            event.detail.target.querySelectorAll('canvas.chart').forEach(canvas => {
                const ctx = canvas.getContext('2d');
                charts[canvas.id] = new Chart(ctx, {...});
            });
        });
    </script>
</body>
</html>
```

## References

### External Documentation
- [Alpine.js Documentation](https://alpinejs.dev/) - Alpine.js guide
- [Hyperscript Documentation](https://hyperscript.org/) - _hyperscript reference
- [Tailwind CSS](https://tailwindcss.com/) - Tailwind documentation
- [Bootstrap](https://getbootstrap.com/) - Bootstrap documentation
- [Chart.js](https://www.chartjs.org/) - Chart.js guide
- [HTMX Events](https://htmx.org/events/) - HTMX event reference

### Related Rules

- **HTMX Foundation**: `rules/221-python-htmx-core.md` - HTMX core patterns
- **Template Strategies**: `rules/221a-python-htmx-templates.md` - Jinja2 patterns
- **Common Patterns**: `rules/221e-python-htmx-patterns.md` - HTMX implementation patterns
- **SSE Patterns**: `rules/221g-python-htmx-sse.md` - Server-Sent Events patterns
