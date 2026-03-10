# 221i: HTMX Advanced Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** infinite scroll, sse, polling, modals, drawers, wizard, multi-step, real-time, lazy loading
**TokenBudget:** ~2500
**ContextTier:** Medium
**Depends:** 221e-python-htmx-patterns.md, 221-python-htmx-core.md
**LoadTrigger:** kw:htmx-scroll, kw:htmx-modal, kw:htmx-wizard, kw:htmx-polling

## Scope

**What This Rule Covers:**
Advanced HTMX patterns: infinite scroll, real-time updates (SSE/polling), modals and drawers, and multi-step form wizards. For core patterns (CRUD, forms, search, progressive enhancement), see 221e.

**When to Load This Rule:**
- Creating infinite scroll or lazy loading
- Implementing real-time updates with SSE or polling
- Building modals and drawers with HTMX
- Creating multi-step forms/wizards

## References

### Dependencies

**Must Load First:**
- **221e-python-htmx-patterns.md** - Core HTMX patterns (CRUD, forms, search)
- **221-python-htmx-core.md** - HTMX core concepts

**Related:**
- **221g-python-htmx-sse.md** - Comprehensive SSE patterns
- **221d-python-htmx-testing.md** - Testing these patterns
- **221f-python-htmx-integrations.md** - Frontend library integrations

### External Documentation

- [HTMX Examples](https://htmx.org/examples/) - Official pattern library
- [HTMX SSE Extension](https://htmx.org/extensions/server-sent-events/) - SSE with HTMX

## Contract

### Inputs and Prerequisites

- HTMX library loaded
- Core HTMX patterns (221e-python-htmx-patterns.md)
- Server-side session management (for wizards)
- Python web framework configured

### Mandatory

- HTMX library with SSE extension (for real-time)
- Server-side routing and template engine
- Unique element IDs for swap targets
- Session storage for multi-step forms

### Forbidden

- Using `time.sleep()` in SSE generators — blocks the worker thread. Use async frameworks or polling instead.
- Modals that cannot be dismissed with Escape key or overlay click
- Wizard forms that lose data on browser back button without warning

### Execution Steps

1. Implement infinite scroll with sentinel element and `hx-trigger="revealed"`
2. Configure SSE or polling endpoints with appropriate Content-Type
3. Create modal container in base template with accessibility attributes
4. Set up wizard form with server-side session storage

### Output Format

```html
<!-- Infinite scroll sentinel -->
<div id="load-more" hx-get="/items?page={{ next_page }}" hx-trigger="revealed" hx-swap="outerHTML">
    <span class="loading">Loading...</span>
</div>
```

### Validation

**Success Criteria:**
- Infinite scroll loads pages without duplicate content
- SSE/polling delivers updates without memory leaks
- Modals are accessible (keyboard dismissible, focus trapped)
- Wizard state survives page refresh (server-side session)

### Post-Execution Checklist

- [ ] Infinite scroll sentinel element uses `hx-trigger="revealed"`
- [ ] SSE/polling endpoints return appropriate `Content-Type`
- [ ] Modal container exists in base template
- [ ] Wizard data stored in server-side session
- [ ] All patterns tested with and without HTMX headers

> **Investigation Required**
> Before implementing advanced HTMX patterns, the agent MUST:
> 1. Check existing modal/drawer implementation — don't mix Alpine.js modals with _hyperscript modals
> 2. Read current session configuration if implementing wizard/multi-step patterns
> 3. Check if SSE extension is already loaded — never include it twice
> 4. Verify existing infinite scroll implementation to avoid duplicate sentinel patterns
> 5. Check whether the project uses async framework (FastAPI) or sync (Flask) for SSE decisions

## Key Principles

### 1. Infinite Scroll / Lazy Loading

**Infinite Scroll Pattern:**
```html
{# Initial page load #}
<div id="results-container">
    {% for item in items %}
        {% include 'partials/_item.html' %}
    {% endfor %}

    {% if has_more %}
        <div hx-get="{{ url_for('load_more', page=next_page) }}"
             hx-trigger="revealed"
             hx-swap="afterend"
             class="loading-trigger">
            Loading more...
        </div>
    {% endif %}
</div>
```

```python
@app.route('/items')
def items_list():
    page = int(request.args.get('page', 1))
    per_page = 20
    htmx = request.headers.get('HX-Request') == 'true'

    items = get_items(page=page, per_page=per_page)
    total = get_total_items()
    has_more = (page * per_page) < total

    if htmx:
        # Return partial for lazy loading
        html = render_template('partials/_items_list.html',
                             items=items,
                             has_more=has_more,
                             next_page=page + 1)
        return html

    # Full page load
    return render_template('pages/items.html',
                         items=items,
                         has_more=has_more,
                         next_page=page + 1)

@app.route('/load_more')
def load_more():
    page = int(request.args.get('page', 2))
    per_page = 20

    items = get_items(page=page, per_page=per_page)
    total = get_total_items()
    has_more = (page * per_page) < total

    return render_template('partials/_load_more_sentinel.html',
                           items=items,
                           has_more=has_more,
                           next_page=page + 1)
```

### 2. Real-Time Updates

**Server-Sent Events (SSE):**
```html
{# Include HTMX SSE extension #}
<script src="https://unpkg.com/htmx.org@1.9.10/dist/ext/sse.js"></script>

<div hx-ext="sse"
     sse-connect="{{ url_for('notifications_stream') }}"
     sse-swap="notification"
     id="notifications">
    {# Notifications appear here #}
</div>
```

```python
# For Flask: use flask-sse or gevent. For async frameworks, see 221g-python-htmx-sse.md
async def generate():
    while True:
        data = await get_latest_data()
        yield f"event: statusUpdate\ndata: {render_partial(data)}\n\n"
        await asyncio.sleep(2)

# For Flask without async, use polling instead:
# hx-trigger="every 2s" hx-get="/api/status" (see polling pattern below)
```

**Polling Pattern:**
```html
<div id="status"
     hx-get="{{ url_for('get_status') }}"
     hx-trigger="every 2s"
     hx-swap="innerHTML">
    Loading status...
</div>
```

```python
@app.route('/status')
def get_status():
    status = get_current_status()
    return render_template('partials/_status.html', status=status)
```

### 3. Modals and Drawers

**Modal Pattern:**
```html
{# Modal container in base template #}
<div id="modal-container"></div>

{# Button to open modal #}
<button hx-get="{{ url_for('user_detail_modal', user_id=user.id) }}"
        hx-target="#modal-container"
        hx-swap="innerHTML">
    View Details
</button>
```

```html
{# partials/_modal.html #}
<div class="modal-overlay" onclick="this.remove()">
    <div class="modal-content" onclick="event.stopPropagation()">
        <button class="modal-close"
                onclick="document.getElementById('modal-container').innerHTML = ''">
            ×
        </button>

        <h2>{{ title }}</h2>
        <div class="modal-body">
            {{ content|safe }}
        </div>
    </div>
</div>
```

```python
@app.route('/users/<int:user_id>/modal')
def user_detail_modal(user_id):
    user = get_user(user_id)
    content = render_template('partials/_user_detail.html', user=user)
    return render_template('partials/_modal.html',
                         title=f'User: {user.name}',
                         content=content)
```

### 4. Multi-Step Forms / Wizards

**Wizard Pattern:**
```html
{# Step 1: Basic Info #}
<form id="wizard-form"
      hx-post="{{ url_for('wizard_step_2') }}"
      hx-target="#wizard-form"
      hx-swap="outerHTML">
    <h3>Step 1: Basic Information</h3>

    <input type="text" name="name" placeholder="Name" required>
    <input type="email" name="email" placeholder="Email" required>

    <button type="submit">Next</button>
</form>
```

```python
@app.route('/wizard/step2', methods=['POST'])
def wizard_step_2():
    # Store step 1 data in session
    session['wizard'] = {
        'name': request.form['name'],
        'email': request.form['email']
    }

    # Return step 2 form
    return render_template('partials/_wizard_step_2.html')

@app.route('/wizard/step3', methods=['POST'])
def wizard_step_3():
    # Add step 2 data to session
    session['wizard']['address'] = request.form['address']
    session['wizard']['phone'] = request.form['phone']

    # Return step 3 form
    return render_template('partials/_wizard_step_3.html')

@app.route('/wizard/complete', methods=['POST'])
def wizard_complete():
    # Get all wizard data from session
    data = session.get('wizard', {})
    data['preferences'] = request.form.getlist('preferences')

    # Save to database
    user = create_user_from_wizard(data)

    # Clear session
    session.pop('wizard', None)

    # Return success message with redirect
    response = make_response('<div class="success">Account created!</div>')
    response.headers['HX-Redirect'] = url_for('dashboard')
    return response
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Blocking SSE Generator

**Problem:** Using `time.sleep()` in SSE generators blocks the Flask worker thread.

**Correct Pattern:**
```python
# BAD: Blocks the worker thread
def generate():
    while True:
        time.sleep(1)  # Blocks entire thread!
        yield f"data: {get_update()}\n\n"

# GOOD: Use polling for Flask sync apps
# In template:
# <div hx-get="/updates" hx-trigger="every 2s">
@app.route("/updates")
def get_updates():
    return render_template("partials/updates.html", data=get_latest())
```

Use async framework with `asyncio.sleep()`, or use polling (`hx-trigger="every 2s"`) for Flask sync apps. See 221g for comprehensive SSE guidance.

### Anti-Pattern 2: Modal Without Keyboard Dismiss

**Problem:** Modals that can only be closed by clicking a button, not Escape key.

**Correct Pattern:**
```html
<div class="modal-overlay"
     _="on keyup[key=='Escape'] from window remove me">
```

## Output Format

See sections 1-4 for complete pattern implementations. Combine with core patterns from 221e for full application coverage.
