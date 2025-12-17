# HTMX Core Patterns (Python)

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential HTMX patterns. Load for HTMX tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** htmx, hypermedia, hateoas, hx-request, hx-trigger, partial rendering, sse, websockets, csrf, xss, http headers, swap strategies, oob swaps, response patterns
**TokenBudget:** ~2500
**ContextTier:** High
**Depends:** rules/200-python-core.md

## Purpose

Establishes foundational HTMX patterns for Python web applications, covering request/response lifecycle, HTTP header management, security considerations, and hypermedia-driven architecture principles for building interactive web applications without JavaScript frameworks.

## Rule Scope

Python backend applications using HTMX for hypermedia-driven interactions (Flask, FastAPI, Django, or other Python web frameworks)

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Detect HTMX requests** - Check `HX-Request` header to differentiate HTMX from full-page requests
- **Return HTML fragments** - HTMX requests return partial HTML, not JSON; full-page requests return complete documents
- **Use response headers** - `HX-Trigger`, `HX-Redirect`, `HX-Refresh`, `HX-Retarget` control client behavior
- **Implement CSRF protection** - HTMX requests must include CSRF tokens for state-changing operations
- **Follow HATEOAS** - Server controls navigation/actions via HTML; client uses hypermedia controls (links, forms)
- **Validate swap strategies** - Use `innerHTML` (default), `outerHTML`, `beforebegin`, `afterend` based on DOM requirements
- **Handle errors gracefully** - Return appropriate HTTP status codes; use `HX-Retarget` for error display

**Pre-Execution Checklist:**
- [ ] HTMX request detection logic implemented (check `HX-Request` header)
- [ ] Partial HTML templates created for HTMX responses
- [ ] Full-page templates available for non-HTMX requests
- [ ] CSRF protection configured for POST/PUT/DELETE endpoints
- [ ] Response headers set appropriately (`HX-Trigger`, `HX-Redirect`, etc.)
- [ ] Security review completed (XSS prevention in partial responses)
- [ ] Testing strategy defined (unit tests for headers, integration tests for HTML)

## Contract

<inputs_prereqs>
Python web framework installed (Flask/FastAPI); HTMX library included in frontend; understanding of HTTP request/response cycle; template engine configured (Jinja2 recommended)
</inputs_prereqs>

<mandatory>
HTTP header inspection capability; template rendering system; CSRF protection middleware; HTML sanitization for user-generated content; test framework for validating headers/responses
</mandatory>

<forbidden>
Returning JSON for HTMX requests (anti-pattern); ignoring CSRF protection; client-side routing (violates hypermedia principles); skipping XSS sanitization in partials; using HTMX without server-side validation
</forbidden>

<steps>
1. Detect HTMX requests via `HX-Request: true` header
2. Route logic: Return HTML fragment for HTMX, full page otherwise
3. Set response headers: `HX-Trigger` for events, `HX-Redirect` for navigation
4. Implement CSRF token validation for state-changing requests
5. Use appropriate swap strategies in HTMX attributes
6. Handle errors with proper HTTP status codes and `HX-Retarget`
7. Test request/response cycle with header assertions
</steps>

<output_format>
HTML fragments for HTMX requests; full HTML documents for non-HTMX requests; response headers for client-side behavior control
</output_format>

<validation>
- HTMX requests return partial HTML (not full documents or JSON)
- `HX-Request` header correctly detected in backend
- CSRF protection active for POST/PUT/DELETE
- Response headers set correctly (`HX-Trigger`, `HX-Redirect`, etc.)
- Tests validate headers and HTML structure
</validation>

## Key Principles

### 1. Request/Response Lifecycle

**HTMX Request Detection:**
```python
# Flask
from flask import request

def is_htmx():
    return request.headers.get('HX-Request') == 'true'

# FastAPI
from fastapi import Request

async def is_htmx(request: Request) -> bool:
    return request.headers.get('HX-Request') == 'true'
```

**Conditional Response Pattern:**
```python
# Flask example
@app.route('/users')
def users_list():
    users = get_users()
    if is_htmx():
        return render_template('partials/users_table.html', users=users)
    return render_template('users_page.html', users=users)
```

### 2. HTTP Header Management

**Request Headers (Client to Server):**
- **`HX-Request`** - Identifies HTMX-initiated request (`true`)
- **`HX-Trigger`** - ID of element that triggered request
- **`HX-Trigger-Name`** - Name attribute of trigger element
- **`HX-Target`** - ID of target element
- **`HX-Current-URL`** - Current page URL
- **`HX-Prompt`** - User input from `hx-prompt`

**Response Headers (Server to Client):**
- **`HX-Trigger`** - Trigger client-side events (e.g., `HX-Trigger: itemUpdated`)
- **`HX-Redirect`** - Client-side redirect (e.g., `HX-Redirect: /login`)
- **`HX-Refresh`** - Force page refresh (`HX-Refresh: true`)
- **`HX-Retarget`** - Change target element (e.g., `HX-Retarget: #error-div`)
- **`HX-Reswap`** - Override swap strategy (e.g., `HX-Reswap: outerHTML`)
- **`HX-Push-Url`** - Update browser history (e.g., `HX-Push-Url: /users/123`)

**Response Header Implementation:**
```python
# Flask
from flask import make_response

@app.route('/item/delete/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    delete_item_from_db(item_id)
    response = make_response('', 200)
    response.headers['HX-Trigger'] = 'itemDeleted'
    return response

# FastAPI
from fastapi import Response

@app.delete('/item/{item_id}')
async def delete_item(item_id: int, response: Response):
    await delete_item_from_db(item_id)
    response.headers['HX-Trigger'] = 'itemDeleted'
    return ''
```

### 3. Response Patterns

**Swap Strategies:**
- **`innerHTML`** - Replace inner HTML (default) - Update content within container
- **`outerHTML`** - Replace entire element - Replace element including container
- **`beforebegin`** - Insert before target - Prepend items to list
- **`afterbegin`** - Insert inside target, before first child - Insert at start of list
- **`beforeend`** - Insert inside target, after last child - Append items to list
- **`afterend`** - Insert after target - Add items after container
- **`delete`** - Remove target element - Delete element on success
- **`none`** - No swap (response ignored) - Fire event without DOM change

**Out-of-Band (OOB) Swaps:**
```python
# Update multiple parts of page simultaneously
@app.route('/update-dashboard')
def update_dashboard():
    stats = get_stats()
    notifications = get_notifications()

    html = f'''
    <div id="stats">{render_stats(stats)}</div>
    <div id="notifications" hx-swap-oob="true">
        {render_notifications(notifications)}
    </div>
    '''
    return html
```

### 4. Security Considerations

**CSRF Protection:**
```python
# Flask with Flask-WTF
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# Include token in base template
# <meta name="csrf-token" content="{{ csrf_token() }}">

# HTMX configuration (add to base template)
# <script>
#   document.body.addEventListener('htmx:configRequest', (event) => {
#     event.detail.headers['X-CSRFToken'] =
#       document.querySelector('meta[name="csrf-token"]').content;
#   });
# </script>
```

**XSS Prevention in Partials:**
```python
# ALWAYS escape user content in templates
# Jinja2 auto-escapes by default

# Explicitly escape in Python if needed
from markupsafe import escape

@app.route('/comment/add', methods=['POST'])
def add_comment():
    content = request.form['content']
    # Jinja2 will auto-escape, but validate input first
    if not validate_comment(content):
        return 'Invalid content', 400

    save_comment(content)
    return render_template('partials/comment.html', content=content)
```

**Content Security Policy:**
```python
# Allow inline HTMX event handlers
@app.after_request
def set_csp(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://unpkg.com/htmx.org; "
        "style-src 'self' 'unsafe-inline';"
    )
    return response
```

### 5. HATEOAS and Hypermedia Principles

**Server Controls Navigation:**
```python
# Server returns HTML with hypermedia controls (links/forms)
@app.route('/users/<int:user_id>')
def user_detail(user_id):
    user = get_user(user_id)
    html = f'''
    <div id="user-{user.id}">
        <h2>{escape(user.name)}</h2>
        <button hx-put="/users/{user.id}/edit"
                hx-target="#user-{user.id}">Edit</button>
        <button hx-delete="/users/{user.id}"
                hx-target="#user-{user.id}"
                hx-swap="outerHTML"
                hx-confirm="Delete user?">Delete</button>
    </div>
    '''
    return html
```

**State Transitions via HTML:**
```python
# Server determines available actions based on state
@app.route('/orders/<int:order_id>/actions')
def order_actions(order_id):
    order = get_order(order_id)

    # State machine: Draft -> Submitted -> Processing -> Completed
    if order.status == 'draft':
        return '''
        <button hx-post="/orders/{}/submit"
                hx-target="#order-actions">Submit Order</button>
        '''.format(order_id)

    elif order.status == 'submitted':
        return '''
        <button hx-post="/orders/{}/process"
                hx-target="#order-actions">Process</button>
        <button hx-post="/orders/{}/cancel"
                hx-target="#order-actions">Cancel</button>
        '''.format(order_id, order_id)

    return '<p>No actions available</p>'
```

### 6. HTMX Extensions

**Server-Sent Events (SSE):**

SSE enables real-time updates from server to client. Choose between two approaches:

1. **HTMX SSE Extension** - Simple, declarative, single-element updates
2. **Alpine.js SSE Manager** - Complex logic, multiple elements, toast notifications

See `rules/221g-python-htmx-sse.md` for comprehensive SSE patterns.

```python
# FastAPI SSE endpoint with named events
from sse_starlette.sse import EventSourceResponse

@app.get('/api/sse/status')
async def sse_status():
    async def event_generator():
        while True:
            yield {
                "event": "system_status",  # Named event type
                "data": json.dumps(await get_status())
            }
            await asyncio.sleep(5)

    return EventSourceResponse(event_generator())
```

```html
<!-- HTMX SSE Extension (simple updates) -->
<div hx-ext="sse" sse-connect="/api/sse/status"
     hx-get="/status/content" hx-trigger="sse:system_status">
</div>

<!-- Alpine.js SSE Manager (complex logic) -->
<div x-data="statusPage()" x-init="init()">
    <div id="status" hx-get="/status/content" hx-trigger="load, systemStatus"></div>
</div>
```

**Critical SSE Anti-Patterns:**
- **Mixing SSE approaches:** Causes duplicate connections - Choose ONE per element
- **Event type mismatch:** Updates never trigger - Match backend event types exactly
- **Using `sse:` with Alpine.js:** HTMX ignores events - Use camelCase custom events

**WebSockets (with extension):**
```python
# FastAPI WebSocket endpoint
from fastapi import WebSocket

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response_html = process_and_render(data)
        await websocket.send_text(response_html)

# Frontend: <div hx-ext="ws" ws-connect="/ws"></div>
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Returning JSON for HTMX Requests

**Problem:** Returning JSON responses when HTMX expects HTML fragments.

**Why It Fails:** HTMX swaps HTML into the DOM; JSON appears as raw text or breaks the UI.

**Correct Pattern:**
```python
@app.route('/data')
def get_data():
    if is_htmx():
        return render_template('partials/items.html', items=items)
    return render_template('items_page.html', items=items)
```

### Anti-Pattern 2: Missing CSRF Protection

**Problem:** Omitting CSRF tokens on state-changing HTMX requests.

**Why It Fails:** Exposes application to cross-site request forgery attacks.

**Correct Pattern:**
```python
# Configure CSRF in HTMX meta tag (base template)
# <meta name="csrf-token" content="{{ csrf_token() }}">
# htmx.config.getCsrfToken = () => document.querySelector('meta[name="csrf-token"]').content

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    # CSRF validation happens in middleware
    delete_item(id)
    return ''
```

### Anti-Pattern 3: Incorrect Swap Strategy

**Problem:** Using default `innerHTML` swap when `outerHTML` is needed.

**Why It Fails:** Creates nested elements; breaks CSS selectors and event handlers.

**Correct Pattern:**
```html
<div id="user-123" hx-get="/users/123" hx-target="#user-123" hx-swap="outerHTML">
    <!-- Element replaced cleanly -->
</div>
```

### Anti-Pattern 4: Missing Error Handling

**Problem:** Not handling server errors in HTMX responses.

**Why It Fails:** Users see no feedback; errors silently fail; poor UX.

**Correct Pattern:**
```python
@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.form['data']
        update_db(data)
        return '<p class="success">Updated</p>'
    except ValidationError as e:
        response = make_response(f'<p class="error">{escape(str(e))}</p>', 400)
        response.headers['HX-Retarget'] = '#error-container'
        return response
```

## Post-Execution Checklist

- [ ] HTMX requests detected via `HX-Request` header
- [ ] Partial HTML templates created and tested
- [ ] Response headers implemented (`HX-Trigger`, `HX-Redirect`, etc.)
- [ ] CSRF protection configured and validated
- [ ] XSS prevention verified in all partial responses
- [ ] Swap strategies tested (innerHTML, outerHTML, etc.)
- [ ] Error handling implemented with appropriate status codes
- [ ] OOB swaps work correctly for multi-element updates
- [ ] HATEOAS principles followed (server controls navigation)
- [ ] Tests written for request headers and response structure

## Validation

**Success Checks:**
- `curl -H "HX-Request: true" /endpoint` returns HTML fragment
- `curl /endpoint` (without HX-Request) returns full page
- POST/PUT/DELETE requests require valid CSRF token
- Response headers set correctly (`HX-Trigger`, etc.)
- User-generated content escaped in templates
- Tests pass for HTMX-specific behavior

**Negative Tests:**
- Request without CSRF token returns 403 Forbidden
- Invalid input returns 400 with error message
- Missing `HX-Request` header returns full page (not partial)
- XSS attempts blocked (script tags escaped)

## Output Format Examples

### Endpoint with HTMX Detection
```python
# Flask example
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/users')
def users_list():
    users = get_users()

    # Detect HTMX request
    if request.headers.get('HX-Request') == 'true':
        # Return partial for HTMX
        return render_template('partials/users_table.html', users=users)

    # Return full page for browser navigation
    return render_template('users_page.html', users=users)
```

### Response with Trigger Event
```python
@app.route('/item/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    update_item_in_db(item_id, data)

    response = make_response(
        render_template('partials/item.html', item=get_item(item_id))
    )
    response.headers['HX-Trigger'] = 'itemUpdated'
    return response
```

### CSRF Token Configuration
```html
<!-- base.html -->
<meta name="csrf-token" content="{{ csrf_token() }}">
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script>
  document.body.addEventListener('htmx:configRequest', (event) => {
    event.detail.headers['X-CSRFToken'] =
      document.querySelector('meta[name="csrf-token"]').content;
  });
</script>
```

## References

### External Documentation
- [HTMX Official Documentation](https://htmx.org/docs/) - Comprehensive HTMX reference
- [HTMX Examples](https://htmx.org/examples/) - Common patterns and use cases
- [Hypermedia Systems Book](https://hypermedia.systems/) - Carson Gross et al., HATEOAS principles
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) - CSRF protection strategies

### Related Rules

- **Python Foundation**: `rules/200-python-core.md` - Python coding standards
- **Template Strategies**: `rules/221a-python-htmx-templates.md` - Jinja2 patterns for HTMX
- **Flask Integration**: `rules/221b-python-htmx-flask.md` - Flask-specific HTMX patterns
- **FastAPI Integration**: `rules/221c-python-htmx-fastapi.md` - FastAPI-specific HTMX patterns
- **Testing Patterns**: `rules/221d-python-htmx-testing.md` - Testing HTMX endpoints
- **Common Patterns**: `rules/221e-python-htmx-patterns.md` - CRUD, forms, infinite scroll
- **Frontend Integrations**: `rules/221f-python-htmx-integrations.md` - Alpine.js, Tailwind, etc.
- **SSE Patterns**: `rules/221g-python-htmx-sse.md` - Server-Sent Events patterns
