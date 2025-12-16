# HTMX Common Patterns

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** crud, forms, validation, infinite scroll, lazy loading, sse, progressive enhancement, modals, search, autocomplete, real-time, polling, inline editing
**TokenBudget:** ~2600
**ContextTier:** High
**Depends:** rules/221-python-htmx-core.md, rules/221a-python-htmx-templates.md

## Purpose

Provides reusable HTMX implementation patterns for common web application features including CRUD operations, form validation, infinite scroll, real-time updates, progressive enhancement, modals, search, and multi-step workflows.

## Rule Scope

Python web applications implementing common interactive patterns with HTMX (applicable to Flask, FastAPI, Django)

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Inline editing** - Click to edit, use `outerHTML` swap to replace element
- **Form validation** - Server-side validation, return form with errors on invalid input
- **Delete with confirm** - Use `hx-confirm` attribute for user confirmation
- **Infinite scroll** - Trigger on scroll event, append results with `beforeend` swap
- **Search/autocomplete** - Debounce input with `delay:` modifier, target results container
- **Real-time updates** - Use SSE extension or polling with `hx-trigger="every Ns"`
- **Modals/drawers** - Target modal container, use `outerHTML` to replace content
- **Multi-step forms** - Each step returns next form fragment, track state server-side

**Pre-Execution Checklist:**
- [ ] Pattern requirements understood (CRUD, forms, search, etc.)
- [ ] Templates created for partials (row, form, results, modal)
- [ ] Server-side validation implemented
- [ ] HTMX attributes configured (hx-get, hx-post, hx-target, hx-swap)
- [ ] Event handling defined (HX-Trigger headers, client-side listeners)
- [ ] Error handling implemented
- [ ] Progressive enhancement tested (works without JavaScript)

## Contract

<inputs_prereqs>
HTMX library loaded; HTMX core patterns (221-python-htmx-core.md); template strategies (221a-python-htmx-templates.md); server-side validation; Python web framework configured
</inputs_prereqs>

<mandatory>
HTMX library; server-side routing; template engine (Jinja2); form validation logic; unique element IDs; HTTP methods support (GET, POST, PUT, DELETE)
</mandatory>

<forbidden>
Client-side validation only; missing server-side checks; no error handling; hard-coded IDs; skipping progressive enhancement; using JSON responses for HTMX
</forbidden>

<steps>
1. Identify pattern requirements (CRUD, search, modal, etc.)
2. Create partial templates for pattern components
3. Define routes with appropriate HTTP methods
4. Implement server-side validation and business logic
5. Configure HTMX attributes (hx-*, hx-trigger, hx-target, hx-swap)
6. Set response headers (HX-Trigger, HX-Redirect, etc.) as needed
7. Test pattern with and without HTMX (progressive enhancement)
8. Handle errors gracefully with retargeting
</steps>

<output_format>
Reusable pattern implementations with HTML templates, Python route handlers, HTMX attributes, and server-side logic
</output_format>

<validation>
- Pattern works with HTMX enabled
- Graceful degradation without JavaScript
- Server-side validation enforced
- Error cases handled appropriately
- Tests cover happy path and edge cases
- Progressive enhancement verified
</validation>

## Key Principles

### 1. CRUD Operations

**Inline Editing Pattern:**
```html
{# partials/_user_row.html - Display mode #}
<tr id="user-{{ user.id }}">
    <td>{{ user.name }}</td>
    <td>{{ user.email }}</td>
    <td>
        <button hx-get="{{ url_for('edit_user', user_id=user.id) }}"
                hx-target="#user-{{ user.id }}"
                hx-swap="outerHTML">
            Edit
        </button>
        <button hx-delete="{{ url_for('delete_user', user_id=user.id) }}"
                hx-target="#user-{{ user.id }}"
                hx-swap="outerHTML"
                hx-confirm="Delete {{ user.name }}?">
            Delete
        </button>
    </td>
</tr>
```

```html
{# partials/_user_form.html - Edit mode #}
<tr id="user-{{ user.id }}">
    <td><input type="text" name="name" value="{{ user.name }}"></td>
    <td><input type="email" name="email" value="{{ user.email }}"></td>
    <td>
        <button hx-put="{{ url_for('update_user', user_id=user.id) }}"
                hx-target="#user-{{ user.id }}"
                hx-swap="outerHTML"
                hx-include="closest tr">
            Save
        </button>
        <button hx-get="{{ url_for('user_detail', user_id=user.id) }}"
                hx-target="#user-{{ user.id }}"
                hx-swap="outerHTML">
            Cancel
        </button>
    </td>
</tr>
```

```python
# Flask routes
@app.route('/users/<int:user_id>')
def user_detail(user_id):
    user = get_user(user_id)
    return render_template('partials/_user_row.html', user=user)

@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    user = get_user(user_id)
    return render_template('partials/_user_form.html', user=user)

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = get_user(user_id)
    user.name = request.form['name']
    user.email = request.form['email']

    if not validate_user(user):
        return render_template('partials/_user_form.html',
                             user=user, errors=get_errors(user)), 400

    save_user(user)
    response = make_response(render_template('partials/_user_row.html', user=user))
    response.headers['HX-Trigger'] = 'userUpdated'
    return response

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    delete_user_from_db(user_id)
    response = make_response('', 200)
    response.headers['HX-Trigger'] = 'userDeleted'
    return response
```

**Create with Append:**
```html
{# Create form #}
<form hx-post="{{ url_for('create_user') }}"
      hx-target="#users-tbody"
      hx-swap="beforeend">
    <input type="text" name="name" placeholder="Name" required>
    <input type="email" name="email" placeholder="Email" required>
    <button type="submit">Add User</button>
</form>

<table>
    <tbody id="users-tbody">
        {% for user in users %}
            {% include 'partials/_user_row.html' %}
        {% endfor %}
    </tbody>
</table>
```

```python
@app.route('/users', methods=['POST'])
def create_user():
    name = request.form['name']
    email = request.form['email']

    user = User(name=name, email=email)
    if not validate_user(user):
        return render_template('partials/_form_errors.html',
                             errors=get_errors(user)), 400

    save_user(user)
    response = make_response(render_template('partials/_user_row.html', user=user))
    response.headers['HX-Trigger'] = 'userCreated'
    return response
```

### 2. Form Validation

**Server-Side Validation Pattern:**
```html
{# partials/_user_form.html #}
<form id="user-form"
      hx-post="{{ url_for('submit_user_form') }}"
      hx-target="#user-form"
      hx-swap="outerHTML">

    <div class="form-field">
        <label for="name">Name</label>
        <input type="text"
               id="name"
               name="name"
               value="{{ user.name if user else '' }}"
               class="{% if errors.name %}error{% endif %}">
        {% if errors.name %}
            <span class="error-message">{{ errors.name }}</span>
        {% endif %}
    </div>

    <div class="form-field">
        <label for="email">Email</label>
        <input type="email"
               id="email"
               name="email"
               value="{{ user.email if user else '' }}"
               class="{% if errors.email %}error{% endif %}">
        {% if errors.email %}
            <span class="error-message">{{ errors.email }}</span>
        {% endif %}
    </div>

    <button type="submit">Submit</button>
</form>
```

```python
@app.route('/users/form', methods=['POST'])
def submit_user_form():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()

    errors = {}
    if not name:
        errors['name'] = 'Name is required'
    elif len(name) < 2:
        errors['name'] = 'Name must be at least 2 characters'

    if not email:
        errors['email'] = 'Email is required'
    elif '@' not in email:
        errors['email'] = 'Invalid email format'

    if errors:
        return render_template('partials/_user_form.html',
                             user={'name': name, 'email': email},
                             errors=errors), 400

    # Success: create user and redirect or return success message
    user = create_user(name, email)
    response = make_response(f'<div class="success">User {name} created!</div>')
    response.headers['HX-Trigger'] = 'userCreated'
    return response
```

### 3. Infinite Scroll / Lazy Loading

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

    html = ''
    for item in items:
        html += render_template('partials/_item.html', item=item)

    if has_more:
        html += f'''
        <div hx-get="{url_for('load_more', page=page+1)}"
             hx-trigger="revealed"
             hx-swap="afterend"
             class="loading-trigger">
            Loading more...
        </div>
        '''

    return html
```

### 4. Search and Autocomplete

**Search with Debounce:**
```html
<div>
    <input type="search"
           name="q"
           placeholder="Search users..."
           hx-get="{{ url_for('search_users') }}"
           hx-trigger="input changed delay:500ms, search"
           hx-target="#search-results"
           hx-indicator=".search-spinner">
    <span class="search-spinner htmx-indicator">Searching...</span>
</div>

<div id="search-results">
    {# Results appear here #}
</div>
```

```python
@app.route('/users/search')
def search_users():
    query = request.args.get('q', '').strip()

    if not query:
        return '<p>Enter a search term</p>'

    users = search_users_in_db(query)

    if not users:
        return f'<p>No users found for "{escape(query)}"</p>'

    return render_template('partials/_users_table.html', users=users)
```

**Autocomplete Pattern:**
```html
<div class="autocomplete">
    <input type="text"
           name="city"
           hx-get="{{ url_for('autocomplete_cities') }}"
           hx-trigger="keyup changed delay:300ms"
           hx-target="#autocomplete-results"
           placeholder="Enter city name">

    <div id="autocomplete-results" class="autocomplete-results"></div>
</div>
```

```python
@app.route('/autocomplete/cities')
def autocomplete_cities():
    query = request.args.get('city', '').strip()

    if len(query) < 2:
        return ''

    cities = get_matching_cities(query, limit=10)

    html = '<ul class="autocomplete-list">'
    for city in cities:
        html += f'''
        <li hx-get="{url_for('select_city', city=city)}"
            hx-target="#city-input">
            {escape(city)}
        </li>
        '''
    html += '</ul>'

    return html
```

### 5. Real-Time Updates

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
# Flask SSE endpoint
import time

@app.route('/notifications/stream')
def notifications_stream():
    def event_stream():
        while True:
            notification = get_latest_notification()
            if notification:
                html = render_template('partials/_notification.html',
                                     notification=notification)
                yield f'event: notification\ndata: {html}\n\n'
            time.sleep(5)  # Check every 5 seconds

    return Response(event_stream(), mimetype='text/event-stream')
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

### 6. Modals and Drawers

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

### 7. Multi-Step Forms / Wizards

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

### 8. Progressive Enhancement

**Graceful Degradation Pattern:**
```html
{# Form works with and without HTMX #}
<form action="{{ url_for('create_user') }}"
      method="POST"
      hx-post="{{ url_for('create_user') }}"
      hx-target="#user-list"
      hx-swap="beforeend">

    <input type="text" name="name" required>
    <input type="email" name="email" required>
    <button type="submit">Create User</button>
</form>
```

```python
@app.route('/users', methods=['POST'])
def create_user():
    name = request.form['name']
    email = request.form['email']

    user = create_user_in_db(name, email)

    if htmx:
        # Return partial for HTMX
        return render_template('partials/_user_row.html', user=user)

    # Full page redirect for non-HTMX
    flash(f'User {name} created successfully')
    return redirect(url_for('users_list'))
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Client-Side Validation Only

**Problem:** Relying solely on client-side validation without server-side checks.

**Why It Fails:** Easily bypassed; security vulnerability; data corruption risk.

**Correct Pattern:**
```python
@app.route('/users', methods=['POST'])
def create_user():
    data = request.form
    errors = validate_user_data(data)

    if errors:
        return render_template('partials/_form.html',
                             data=data, errors=errors), 400

    user = User(**data)
    save_user(user)
    return render_template('partials/_user_row.html', user=user)
```

### Anti-Pattern 2: Wrong Swap Strategy for Forms

**Problem:** Using `innerHTML` swap on self-replacing elements.

**Why It Fails:** Creates nested elements; breaks form structure; event handlers lost.

**Correct Pattern:**
```html
<form id="form" hx-post="/submit" hx-target="#form" hx-swap="outerHTML">
    ...
</form>
```

## Post-Execution Checklist

- [ ] Pattern implemented with appropriate HTMX attributes
- [ ] Server-side validation enforced
- [ ] Error handling returns HTML with proper status codes
- [ ] Progressive enhancement tested (works without JavaScript)
- [ ] Element IDs unique and properly targeted
- [ ] Response headers set (HX-Trigger, HX-Redirect, etc.)
- [ ] Tests cover success and error cases
- [ ] Templates organized (partials separate from full pages)
- [ ] Security reviewed (CSRF, XSS, input validation)

## Validation

**Success Checks:**
- Pattern works with HTMX enabled
- Graceful degradation without JavaScript
- Server-side validation catches invalid input
- Error messages display correctly
- Events trigger appropriately (HX-Trigger headers)
- Tests pass for all scenarios

**Negative Tests:**
- Invalid input returns 400 with error HTML
- Missing required fields rejected
- Unauthorized access returns 401/403
- Non-existent resources return 404

## Output Format Examples

### Complete CRUD Implementation
```python
# Flask routes for CRUD operations
@app.route('/users/<int:user_id>')
def user_detail(user_id):
    user = get_user(user_id)
    return render_template('partials/_user_row.html', user=user)

@app.route('/users/<int:user_id>/edit')
def edit_user(user_id):
    user = get_user(user_id)
    return render_template('partials/_user_form.html', user=user)

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = get_user(user_id)
    user.name = request.form['name']
    user.email = request.form['email']

    if not validate_user(user):
        return render_template('partials/_user_form.html',
                             user=user, errors=get_errors(user)), 400

    save_user(user)
    response = make_response(render_template('partials/_user_row.html', user=user))
    response.headers['HX-Trigger'] = 'userUpdated'
    return response

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    delete_user_from_db(user_id)
    response = make_response('', 200)
    response.headers['HX-Trigger'] = 'userDeleted'
    return response
```

## References

### External Documentation
- [HTMX Examples](https://htmx.org/examples/) - Official pattern library
- [Hypermedia Systems](https://hypermedia.systems/) - Book on hypermedia patterns
- [HTMX Essays](https://htmx.org/essays/) - Architecture and design philosophy

### Related Rules
- **HTMX Foundation**: `rules/221-python-htmx-core.md` - Core HTMX concepts
- **Template Strategies**: `rules/221a-python-htmx-templates.md` - Jinja2 patterns
- **Flask Integration**: `rules/221b-python-htmx-flask.md` - Flask-specific patterns
- **FastAPI Integration**: `rules/221c-python-htmx-fastapi.md` - FastAPI patterns
- **Testing**: `rules/221d-python-htmx-testing.md` - Testing these patterns
- **Integrations**: `rules/221f-python-htmx-integrations.md` - Frontend library integrations
