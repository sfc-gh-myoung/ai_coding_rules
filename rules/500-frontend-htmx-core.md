# HTMX Frontend Reference

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Frontend HTMX patterns. Load for HTMX tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** htmx attributes, client-side, events, css transitions, debugging, browser compatibility, hx-get, hx-post, hx-swap, hx-trigger, hx-target
**TokenBudget:** ~3600
**ContextTier:** Low
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Provides a standalone frontend reference for HTMX attributes, client-side events, CSS transitions, debugging techniques, and browser compatibility considerations for pure HTMX usage without backend specifics.

**When to Load This Rule:**
- Working with HTMX frontend applications
- Adding hypermedia-driven interactivity
- Implementing server-driven UI updates
- Debugging HTMX requests and responses
- Choosing between HTMX and JavaScript frameworks

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **221-python-htmx-core.md** - HTMX with Python backends
- **421-javascript-alpinejs-core.md** - Alpine.js for client-side reactivity

### External Documentation

- [HTMX Official Docs](https://htmx.org/docs/) - Complete HTMX documentation
- [HTMX Examples](https://htmx.org/examples/) - Practical HTMX patterns
- [HTMX Essays](https://htmx.org/essays/) - Hypermedia philosophy

## Contract

### Inputs and Prerequisites

- HTMX library loaded (1.9.x+)
- Basic HTML/CSS knowledge
- Understanding of HTTP methods
- Browser dev tools access

### Mandatory

- HTMX library (1.9.x+)
- Modern browser (Chrome, Firefox, Safari, Edge)
- HTTP server for testing

### Forbidden

- Using HTMX with incompatible browsers (IE11 and below)
- Missing CSRF protection for state-changing requests
- Skipping progressive enhancement fallbacks

### Execution Steps

1. Load HTMX library in HTML document
2. Add HTMX attributes to HTML elements (hx-get, hx-target, hx-swap)
3. Configure triggers (hx-trigger) for user interactions
4. Define CSS transitions for smooth animations
5. Add event listeners for HTMX lifecycle hooks
6. Test in browser with dev tools open
7. Enable debugging (htmx.logAll()) if issues arise

### Output Format

HTML with HTMX attributes:
- Core attributes (hx-get, hx-post, etc.)
- Targeting and swapping configuration
- CSS transitions for animations
- JavaScript event listeners for HTMX lifecycle

### Validation

**Pre-Task-Completion Checks:**
- [ ] HTMX library loaded (CDN or local)
- [ ] HTMX attributes configured on elements
- [ ] Swap strategies understood (innerHTML, outerHTML, etc.)
- [ ] Event listeners set up for lifecycle hooks
- [ ] CSS transitions defined for smooth UX
- [ ] Debugging tools ready (browser dev tools, htmx.logAll())

**Success Criteria:**
- HTMX attributes correctly trigger requests
- Responses swap into target elements as expected
- CSS transitions animate smoothly
- Event listeners fire at appropriate lifecycle points
- No console errors
- Works in all target browsers

**Network Failure Handling:**
- Implement `htmx:sendError` listener to show user-friendly error messages
- Use `hx-indicator` to show loading state during requests
- Provide retry mechanism for failed requests (e.g., `htmx:afterOnLoad` with status check)
- Set appropriate timeouts via `hx-request="timeout:10000"`

### Design Principles

- **Hypermedia-Driven:** Server returns HTML fragments, not JSON
- **Progressive Enhancement:** Works without JavaScript, enhanced with HTMX
- **Declarative:** Express behavior through HTML attributes
- **Minimal JavaScript:** Most interactivity through HTMX attributes
- **Server-Centric:** Logic lives on server, not client

### Post-Execution Checklist

- [ ] HTMX library loaded correctly
- [ ] HTMX attributes configured on elements
- [ ] Swap strategies working as expected
- [ ] Event listeners registered for lifecycle hooks
- [ ] CSS transitions smooth and performant
- [ ] Debugging enabled if needed (htmx.logAll())
- [ ] CSRF protection implemented for state-changing requests
- [ ] Progressive enhancement fallbacks in place
- [ ] Tested in all target browsers
- [ ] No console errors

## Key Principles

### Core HTMX Attributes

**HTTP Method Attributes:**
- **`hx-get`** - Issue GET request (e.g., `<button hx-get="/data">Load</button>`)
- **`hx-post`** - Issue POST request (e.g., `<form hx-post="/submit">...</form>`)
- **`hx-put`** - Issue PUT request (e.g., `<button hx-put="/update">Save</button>`)
- **`hx-delete`** - Issue DELETE request (e.g., `<button hx-delete="/remove">Delete</button>`)
- **`hx-patch`** - Issue PATCH request (e.g., `<button hx-patch="/partial">Update</button>`)

**Targeting and Swapping:**
- **`hx-target`** - Element to swap content into (e.g., `hx-target="#results"`)
- **`hx-swap`** - How to swap content (e.g., `hx-swap="outerHTML"`)
- **`hx-select`** - CSS selector to extract from response (e.g., `hx-select="#content"`)

**Swap Strategies:**
- `innerHTML` - Replace inner HTML (default)
- `outerHTML` - Replace entire element
- `beforebegin` - Insert before target
- `afterbegin` - Insert at start of target
- `beforeend` - Insert at end of target
- `afterend` - Insert after target
- `delete` - Delete target element
- `none` - Do not swap

**Example:**
```html
<button hx-get="/users"
        hx-target="#user-list"
        hx-swap="innerHTML">
    Load Users
</button>

<div id="user-list">
    <!-- Users will be loaded here -->
</div>
```

### Trigger Patterns

**Basic Triggers:**
```html
<!-- Click (default for buttons) -->
<button hx-get="/data">Click me</button>

<!-- Input events -->
<input hx-get="/search"
       hx-trigger="input"
       hx-target="#results">

<!-- Change events -->
<select hx-get="/filter"
        hx-trigger="change"
        hx-target="#results">
    <option value="all">All</option>
</select>

<!-- Load on element appearance -->
<div hx-get="/content"
     hx-trigger="load">
</div>
```

**Advanced Triggers:**
```html
<!-- Debounced input (wait 500ms after typing stops) -->
<input hx-get="/search"
       hx-trigger="input changed delay:500ms"
       hx-target="#results">

<!-- Multiple triggers -->
<div hx-get="/status"
     hx-trigger="load, every 5s">
</div>

<!-- Trigger on scroll into view -->
<div hx-get="/more-items"
     hx-trigger="revealed">
    Loading more...
</div>

<!-- Trigger from another element -->
<input type="text" id="search-input">
<button hx-get="/search"
        hx-trigger="click, keyup from:#search-input">
    Search
</button>
```

### Request Configuration

**Including Values:**
```html
<!-- Include form values from closest form -->
<button hx-post="/submit"
        hx-include="closest form">
    Submit
</button>

<!-- Include specific element values -->
<button hx-post="/update"
        hx-include="#name, #email">
    Update
</button>

<!-- Include all inputs in parent -->
<div>
    <input name="field1">
    <input name="field2">
    <button hx-post="/save" hx-include="previous input, previous input">
        Save
    </button>
</div>
```

**Request Parameters:**
```html
<!-- Add parameters to request -->
<button hx-get="/filter"
        hx-vals='{"category": "books", "sort": "newest"}'>
    Filter Books
</button>

<!-- Dynamic parameters with JavaScript -->
<button hx-get="/data"
        hx-vals="js:{timestamp: Date.now()}">
    Load with Timestamp
</button>
```

**Request Headers:**
```html
<!-- Add custom headers -->
<button hx-get="/api/data"
        hx-headers='{"X-Custom-Header": "value"}'>
    API Request
</button>
```

### Response Indicators

**Loading Indicators:**
```html
<div hx-get="/data"
     hx-indicator="#spinner">
    Load Data
</div>

<div id="spinner" class="htmx-indicator">
    <img src="spinner.gif" alt="Loading...">
</div>
```

```css
/* Hide indicator by default, show during request */
.htmx-indicator {
    display: none;
}

.htmx-request .htmx-indicator,
.htmx-request.htmx-indicator {
    display: inline;
}
```

**Request Classes:**
HTMX automatically adds classes during request lifecycle:
- `htmx-request` - Added during request
- `htmx-swapping` - Added during swap
- `htmx-settling` - Added during settle (400ms default)

### CSS Transitions

**Fade Transition:**
```css
/* Define transition on settling class */
.htmx-settling * {
    transition: opacity 300ms ease-in;
}

/* Initial state when swapping starts */
.htmx-swapping * {
    opacity: 0;
}
```

**Slide Transition:**
```css
.htmx-settling .slide-in {
    transition: transform 300ms ease-out;
}

.htmx-swapping .slide-in {
    transform: translateX(-100%);
}
```

**Custom Transition with View Transitions API:**
```html
<div hx-get="/content"
     hx-swap="innerHTML transition:true">
</div>
```

### Client-Side Events

**Event Listening:**
```javascript
// Before request is sent
document.body.addEventListener('htmx:beforeRequest', function(event) {
    console.log('About to send request to:', event.detail.path);
});

// After swap is complete
document.body.addEventListener('htmx:afterSwap', function(event) {
    console.log('Content swapped into:', event.detail.target);
});

// On error
document.body.addEventListener('htmx:responseError', function(event) {
    console.error('Request failed:', event.detail.xhr.status);
});

// Before swap (can modify response)
document.body.addEventListener('htmx:beforeSwap', function(event) {
    if (event.detail.xhr.status === 404) {
        event.detail.shouldSwap = true; // Force swap even on error
        event.detail.target = document.getElementById('error-div');
    }
});
```

**Custom Events (Server-Triggered):**
```javascript
// Server sends: HX-Trigger: itemDeleted
document.body.addEventListener('itemDeleted', function(event) {
    console.log('Item was deleted on server');
    // Update other parts of UI
});

// Server sends: HX-Trigger: {"showNotification": {"message": "Saved!"}}
document.body.addEventListener('showNotification', function(event) {
    alert(event.detail.value.message);
});
```

### Debugging Techniques

**Enable Logging:**
```javascript
// Enable verbose logging
htmx.logAll();
```

**Console Output:**
```
htmx:configRequest GET /users
htmx:beforeRequest GET /users
htmx:xhr:loadstart GET /users
htmx:xhr:loadend GET /users
htmx:beforeSwap GET /users
htmx:afterSwap GET /users
htmx:afterSettle GET /users
```

**Inspecting HTMX Requests:**
```javascript
// Inspect specific element's HTMX config
console.log(htmx.config);

// Check if element has HTMX
const element = document.getElementById('my-button');
console.log(element.getAttribute('hx-get'));

// Manually trigger HTMX request
htmx.trigger(element, 'click');
```

**Network Tab:**
- Open browser dev tools, then select Network tab
- Look for requests with `HX-Request: true` header
- Check response headers for `HX-Trigger`, `HX-Redirect`, etc.

### Browser Compatibility

**Supported Browsers:**
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

**Polyfills (if needed):**
```html
<!-- For older browsers, load Promise polyfill -->
<script src="https://cdn.jsdelivr.net/npm/promise-polyfill@8/dist/polyfill.min.js"></script>
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
```

**Progressive Enhancement:**
```html
<!-- Form works without HTMX (falls back to full page submit) -->
<form action="/submit" method="POST"
      hx-post="/submit"
      hx-target="#result">
    <input type="text" name="data">
    <button type="submit">Submit</button>
</form>
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: No Target Specified

**Problem:** Omitting `hx-target` causes the triggering element to replace itself with the response.

**Why It Fails:** Button disappears after click; unexpected UI behavior; confuses users.

**Correct Pattern:**
```html
<button hx-get="/data" hx-target="#content">Load</button>
<div id="content"></div>
```

### Anti-Pattern 2: Incorrect Swap Strategy

**Problem:** Using default `innerHTML` swap when `outerHTML` is needed, causing nested elements.

**Why It Fails:** Creates deeply nested DOM structures; breaks CSS selectors; memory leaks.

**Correct Pattern:**
```html
<div id="content" hx-get="/data" hx-target="#content" hx-swap="outerHTML">
</div>
```

### Anti-Pattern 3: No Loading Indicator

**Problem:** Not providing visual feedback during HTMX requests.

**Why It Fails:** Users don't know if action worked; may click repeatedly; poor UX.

**Correct Pattern:**
```html
<button hx-get="/data" hx-target="#content" hx-indicator="#spinner">Load</button>
<span id="spinner" class="htmx-indicator">Loading...</span>
```

### Anti-Pattern 4: Missing Progressive Enhancement

**Problem:** HTMX-only forms that break completely without JavaScript.

**Why It Fails:** Accessibility issues; breaks for users with JS disabled; SEO problems.

**Correct Pattern:**
```html
<form action="/submit" method="post" hx-post="/submit" hx-target="#result">
  <button type="submit">Submit</button>
</form>
```

## Output Format Examples

### Complete HTMX Page
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>HTMX Example</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        .htmx-indicator { display: none; }
        .htmx-request .htmx-indicator { display: inline; }

        .htmx-settling * {
            transition: opacity 300ms ease-in;
        }
        .htmx-swapping * {
            opacity: 0;
        }
    </style>
</head>
<body>
    <button hx-get="/users"
            hx-target="#user-list"
            hx-swap="innerHTML"
            hx-indicator="#spinner">
        Load Users
    </button>

    <span id="spinner" class="htmx-indicator">Loading...</span>

    <div id="user-list">
        <!-- Users will appear here -->
    </div>

    <script>
        // Enable debugging
        htmx.logAll();

        // Listen for events
        document.body.addEventListener('htmx:afterSwap', function(event) {
            console.log('Content loaded!');
        });
    </script>
</body>
</html>
```
