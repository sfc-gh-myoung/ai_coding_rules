# HTMX Common Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-03-09
**Keywords:** crud, forms, validation, progressive enhancement, search, autocomplete, inline editing
**TokenBudget:** ~3400
**ContextTier:** Medium
**Depends:** 221-python-htmx-core.md, 221a-python-htmx-templates.md

## Scope

**What This Rule Covers:**
Core HTMX implementation patterns: CRUD operations, form validation, search/autocomplete, and progressive enhancement. For advanced patterns (infinite scroll, modals, wizards, real-time), see 221i.

**When to Load This Rule:**
- Implementing CRUD operations with HTMX
- Building forms with server-side validation
- Implementing search and autocomplete
- Adding progressive enhancement to existing forms

## References

### Dependencies

**Must Load First:**
- **221-python-htmx-core.md** - HTMX core concepts
- **221a-python-htmx-templates.md** - Jinja2 patterns

**Related:**
- **221i-python-htmx-patterns-advanced.md** - Advanced patterns (scroll, modals, wizards, real-time)
- **221b-python-htmx-flask.md** - Flask-specific patterns
- **221c-python-htmx-fastapi.md** - FastAPI patterns
- **221d-python-htmx-testing.md** - Testing these patterns
- **221f-python-htmx-integrations.md** - Frontend library integrations

### External Documentation

- [HTMX Examples](https://htmx.org/examples/) - Official pattern library
- [Hypermedia Systems](https://hypermedia.systems/) - Book on hypermedia patterns
- [HTMX Essays](https://htmx.org/essays/) - Architecture and design philosophy

## Contract

### Inputs and Prerequisites

- HTMX library loaded
- HTMX core patterns (221-python-htmx-core.md)
- Template strategies (221a-python-htmx-templates.md)
- Server-side validation
- Python web framework configured

### Mandatory

- HTMX library
- Server-side routing
- Template engine (Jinja2)
- Form validation logic
- Unique element IDs
- HTTP methods support (GET, POST, PUT, DELETE)

### Forbidden

- Client-side validation only
- Accepting form input without server-side type checking, length limits (`len(name) >= 2`), and format validation (`@` in email) on every form submission
- Routes that can raise exceptions without returning an HTML error partial with appropriate HTTP status code (400 for validation, 404 for not found, 500 for server error)
- Hard-coded IDs
- Forms and links that only work with JavaScript — always include `action=` and `method=` HTML attributes alongside `hx-*` attributes for non-JS fallback. Exception: autocomplete and infinite scroll, which fundamentally require JavaScript.
- Using JSON responses for HTMX

### Execution Steps

1. Identify pattern requirements (CRUD, search, modal, etc.)
2. Create partial templates for pattern components
3. Define routes with appropriate HTTP methods
4. Implement server-side validation and business logic
5. Configure HTMX attributes (hx-*, hx-trigger, hx-target, hx-swap)
6. Set response headers (HX-Trigger, HX-Redirect, etc.) as needed
7. Test pattern with and without HTMX (progressive enhancement)
8. Handle errors gracefully with retargeting

### Output Format

- Reusable pattern implementations with HTML templates
- Python route handlers
- HTMX attributes
- Server-side logic

### Validation

**Pre-Task-Completion Checks:**
- Pattern requirements understood (CRUD, forms, search, etc.)
- Templates created for partials (row, form, results, modal)
- Server-side validation implemented
- HTMX attributes configured (hx-get, hx-post, hx-target, hx-swap)
- Event handling defined (HX-Trigger headers, client-side listeners)
- Error handling implemented

**Success Criteria:**
- Pattern works with HTMX enabled
- Graceful degradation without JavaScript
- Server-side validation enforced
- Error cases handled appropriately
- Tests cover happy path and edge cases
- Progressive enhancement verified

### Design Principles

- **Inline editing** - Click to edit, use `outerHTML` swap to replace element
- **Form validation** - Server-side validation, return form with errors on invalid input
- **Delete with confirm** - Use `hx-confirm` attribute for user confirmation
- **Infinite scroll** - Trigger on scroll event, append results with `beforeend` swap
- **Search/autocomplete** - Debounce input with `delay:` modifier, target results container
- **Real-time updates** - Use SSE extension or polling with `hx-trigger="every Ns"`
- **Modals/drawers** - Target modal container, use `outerHTML` to replace content
- **Multi-step forms** - Each step returns next form fragment, track state server-side

### Post-Execution Checklist

- [ ] Pattern implemented with appropriate HTMX attributes
- [ ] Server-side validation enforced
- [ ] Error handling returns HTML with proper status codes
- [ ] Progressive enhancement tested (works without JavaScript)
- [ ] Element IDs unique and properly targeted
- [ ] Response headers set (HX-Trigger, HX-Redirect, etc.)
- [ ] Tests cover success and error cases
- [ ] Templates organized (partials separate from full pages)
- [ ] Security reviewed (CSRF, XSS, input validation)

> **Investigation Required**
> Before implementing HTMX patterns, the agent MUST:
> 1. Check existing HTMX patterns in the project — never add a duplicate CRUD/search/modal implementation
> 2. Verify current form validation approach (server-side vs client-side) and match it
> 3. Check existing modal/drawer implementation — don't mix Alpine.js modals with _hyperscript modals
> 4. Read current session configuration if implementing wizard/multi-step patterns
> 5. Check whether progressive enhancement is a project requirement (accessibility compliance may mandate it)

### Pattern Selection Guide

- **Edit data inline:** Inline CRUD (221e §1)
- **Validate form input:** Server-side validation (221e §2)
- **Find items by text:** Search / autocomplete (221e §3)
- **Works without JS:** Progressive enhancement (221e §5)
- **Load content on scroll:** Infinite scroll (221i §1)
- **Live data updates:** SSE or polling (221i §2)
- **Overlay content:** Modals / drawers (221i §3)
- **Multi-page form:** Multi-step wizard (221i §4)

Implement patterns from 221e (core) first. Add 221i (advanced) patterns only when the use case specifically requires them.

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

### 3. Search and Autocomplete

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

    return render_template('partials/_autocomplete_results.html',
                           cities=cities)
```

### 5. Progressive Enhancement

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
    htmx = request.headers.get('HX-Request') == 'true'

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
