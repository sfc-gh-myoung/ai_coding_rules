# HTMX Template Strategies

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:htmx-templates
**Keywords:** jinja2, templates, partials, fragments, template composition, conditional rendering, htmx templates, template organization, reusable components, template context
**TokenBudget:** ~4500
**ContextTier:** High
**Depends:** 221-python-htmx-core.md

## Scope

**What This Rule Covers:**
Jinja2 template organization patterns for HTMX applications, covering partial rendering, fragment composition, conditional template logic, and reusable component strategies for hypermedia-driven interfaces.

**When to Load This Rule:**
- Organizing templates for HTMX applications
- Creating partial templates for HTMX responses
- Implementing conditional rendering for HTMX vs full-page requests
- Building reusable template components
- Managing template context for HTMX endpoints

## References

### Dependencies

**Must Load First:**
- **221-python-htmx-core.md** - HTMX foundation patterns

**Related:**
- **221b-python-htmx-flask.md** - Flask-specific template patterns
- **221c-python-htmx-fastapi.md** - FastAPI template setup
- **221e-python-htmx-patterns.md** - Template patterns for CRUD, forms, etc.
- **200-python-core.md** - Python coding standards

### External Documentation

- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Official Jinja2 reference
- [HTMX Examples](https://htmx.org/examples/) - Template patterns with HTMX
- [Flask Templates](https://flask.palletsprojects.com/en/latest/tutorial/templates/) - Flask template guide
- [FastAPI Templates](https://fastapi.tiangolo.com/advanced/templates/) - Jinja2 with FastAPI

## Contract

### Inputs and Prerequisites

- Jinja2 template engine configured
- HTMX library available
- Understanding of template inheritance
- Template directory structure
- HTMX core patterns (221-python-htmx-core.md)

### Mandatory

- Jinja2 installed
- Template loader configured
- HTMX library in base template
- Unique element IDs for HTMX targets
- Partial template directory

### Forbidden

- Mixing full-page and partial logic in single template
- Returning partials without proper IDs
- More than 1 level of inheritance for partials (partials should be standalone fragments, never extending other templates)
- Passing unnecessary context to partials
- Hard-coding URLs in templates

### Execution Steps

1. Create template directory structure (base, pages, partials)
2. Define base template with HTMX library and configuration
3. Build full-page templates using inheritance
4. Create focused partials for HTMX responses (no/minimal inheritance)
5. Add HTMX detection logic in views or templates
6. Implement conditional rendering for HTMX vs. full-page requests
7. Test partial rendering in isolation and within full pages

### Output Format

- Organized template files: base.html, page templates, partial templates
- Conditional rendering logic in views
- Reusable template components

### Validation

**Pre-Task-Completion Checks:**
- Template directory structure defined (base, pages, partials)
- Base template includes HTMX library and configuration
- Partial templates created for HTMX responses
- Template naming convention established (e.g., `_partial_name.html`)
- HTMX detection logic available in templates or views
- Component IDs consistently applied for targeting

**Success Criteria:**
- Templates organized by purpose (base, pages, partials)
- Partials render correctly in isolation
- HTMX requests return appropriate partials
- Full-page requests return complete documents
- Element IDs unique and consistent
- Tests validate template rendering for both request types

### Design Principles

- **Organize by purpose** - Separate base templates, full pages, partials, and fragments
- **Detect HTMX in templates** - Use `request.headers.get('HX-Request')` for conditional rendering
- **Create reusable partials** - Small, focused template fragments for HTMX responses
- **Use template inheritance** - Base templates for full pages, partials extend sparingly or not at all
- **Minimize context** - Partials receive only necessary data, avoid passing entire app state
- **Include IDs for targeting** - All HTMX-swappable elements need unique IDs

### Post-Execution Checklist

- [ ] Template directory organized by purpose (base, pages, partials)
- [ ] Base template includes HTMX library and configuration
- [ ] Partials created as standalone fragments (no/minimal inheritance)
- [ ] All HTMX-swappable elements have unique IDs
- [ ] HTMX detection logic implemented (view or template level)
- [ ] Template context minimized for partials
- [ ] Reusable components created using macros/includes
- [ ] Naming conventions consistent (underscore prefix for partials)
- [ ] Tests validate partial and full-page rendering
- [ ] No hard-coded URLs (using `url_for()` or equivalent)

> **Investigation Required**
> Before creating or modifying HTMX templates, the agent MUST:
> 1. Check existing template directory structure — adopt existing conventions (e.g., `partials/` vs `fragments/` vs `components/`)
> 2. Read existing `base.html` for HTMX script includes, CSRF meta tags, and `htmx:configRequest` listener
> 3. Check existing partial naming patterns — use `_prefix` only if the project already does; match existing convention
> 4. Verify current CSRF protection setup before adding `htmx:configRequest` event listener (may already exist)
> 5. Read existing macros in `templates/macros/` before creating new ones — extend rather than duplicate

## Key Principles

### 1. Template Directory Structure

**Recommended Organization:**

Directory structure for `templates/`:
- `base.html` - Base template with HTMX config
- **pages/** - Full-page templates
  - `home.html`, `users.html`, `dashboard.html`
- **partials/** - HTMX response fragments
  - `_user_row.html`, `_user_form.html`, `_notification.html`, `_stats_card.html`
- **components/** - Reusable components (used in pages and partials)
  - `_navbar.html`, `_footer.html`, `_form_field.html`

**Naming Conventions:**
- Partials: Prefix with underscore `_partial_name.html`
- Pages: Plain names `page_name.html`
- Components: Prefix with underscore `_component_name.html`
- Base: `base.html` or `layout.html`

### 2. Base Template Pattern

**Base Template with HTMX:**
```html
{# templates/base.html #}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{% block title %}App Title{% endblock %}</title>

    {% block styles %}
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    {% endblock %}
</head>
<body>
    {% include 'components/_navbar.html' %}

    <main id="main-content">
        {% block content %}{% endblock %}
    </main>

    {% include 'components/_footer.html' %}

    {# HTMX Library — 1.9.x (current stable); 2.0.x renames hx-ws → ws-connect, hx-sse → sse-connect #}
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>

    {# HTMX Configuration #}
    <script>
        // CSRF token for all HTMX requests
        document.body.addEventListener('htmx:configRequest', (event) => {
            event.detail.headers['X-CSRFToken'] =
                document.querySelector('meta[name="csrf-token"]').content;
        });

        // Global event handling (add app-specific logic as needed)
        document.body.addEventListener('htmx:afterSwap', (event) => {
            // Initialize dynamic content after swap if needed
        });
    </script>

    {% block scripts %}{% endblock %}
</body>
</html>
```

### 3. Full-Page Template Pattern

**Page with HTMX Elements:**
```html
{# templates/pages/users.html #}
{% extends "base.html" %}

{% block title %}Users - App{% endblock %}

{% block content %}
<div class="container">
    <h1>Users</h1>

    {# Search form triggers HTMX request #}
    <form hx-get="{{ url_for('users_search') }}"
          hx-target="#users-table"
          hx-trigger="input changed delay:500ms from:#search-input">
        <input type="search"
               id="search-input"
               name="q"
               placeholder="Search users...">
    </form>

    {# Table replaced by HTMX responses #}
    <div id="users-table">
        {% include 'partials/_users_table.html' %}
    </div>
</div>
{% endblock %}
```

### 4. Partial Template Patterns

**Simple Partial (No Inheritance):**
```html
{# templates/partials/_user_row.html #}
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

**Partial with Loop:**
```html
{# templates/partials/_users_table.html #}
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody id="users-tbody">
        {% for user in users %}
            {% include 'partials/_user_row.html' %}
        {% else %}
            <tr>
                <td colspan="3">No users found</td>
            </tr>
        {% endfor %}
    </tbody>
</table>
```

### 5. Conditional Rendering

**Method 1: View-Level Detection (Recommended):**
```python
# Flask example
@app.route('/users')
def users_list():
    users = get_users()

    if request.headers.get('HX-Request') == 'true':
        return render_template('partials/_users_table.html', users=users)

    return render_template('pages/users.html', users=users)
```

**Method 2: Template-Level Detection (Include-Based):**

> **Note:** `{% extends %}` must be the first tag in a Jinja2 template and cannot appear inside conditionals. Use `{% include %}` for conditional rendering at the template level.

```html
{# templates/users.html #}
{# This template does NOT use extends — it builds the page inline #}
{% if request.headers.get('HX-Request') %}
    {# Partial response for HTMX #}
    {% include 'partials/_users_table.html' %}
{% else %}
    {# Full page response assembled via includes #}
    <!DOCTYPE html>
    <html>
    <head><title>Users</title></head>
    <body>
        {% include 'components/_navbar.html' %}
        <main>
            <h1>Users</h1>
            {% include 'partials/_users_table.html' %}
        </main>
    </body>
    </html>
{% endif %}
```

> For most projects, Method 1 (view-level detection) is simpler and avoids this limitation entirely.

### 6. Reusable Components

**Component Macro:**
```html
{# templates/components/_form_field.html #}
{% macro text_field(name, label, value='', required=False, error=None) %}
<div class="form-field">
    <label for="{{ name }}">{{ label }}</label>
    <input type="text"
           id="{{ name }}"
           name="{{ name }}"
           value="{{ value }}"
           {% if required %}required{% endif %}
           class="{% if error %}error{% endif %}">
    {% if error %}
        <span class="error-message">{{ error }}</span>
    {% endif %}
</div>
{% endmacro %}
```

**Using Component:**
```html
{# templates/partials/_user_form.html #}
{% from 'components/_form_field.html' import text_field %}

<form id="user-form-{{ user.id }}"
      hx-put="{{ url_for('update_user', user_id=user.id) }}"
      hx-target="#user-{{ user.id }}">

    {{ text_field('name', 'Name', user.name, required=True, error=errors.name) }}
    {{ text_field('email', 'Email', user.email, required=True, error=errors.email) }}

    <button type="submit">Save</button>
    <button type="button"
            hx-get="{{ url_for('user_detail', user_id=user.id) }}"
            hx-target="#user-{{ user.id }}">
        Cancel
    </button>
</form>
```

### 7. Template Context Management

**Minimal Context for Partials:**
```python
# Good: Pass only necessary data
@app.route('/user/<int:user_id>/edit')
def edit_user(user_id):
    user = get_user(user_id)
    return render_template('partials/_user_form.html',
                          user=user,
                          errors={})

# Avoid: Passing entire app state
@app.route('/user/<int:user_id>/edit')
def edit_user(user_id):
    # DON'T DO THIS
    return render_template('partials/_user_form.html',
                          user=user,
                          all_users=get_all_users(),  # Unnecessary
                          config=app.config,           # Unnecessary
                          session=session)             # Unnecessary
```

**Context Processor for Common Data:**
```python
# Flask
@app.context_processor
def inject_common():
    return {
        'app_name': 'MyApp',
        'current_year': datetime.now().year,
        'is_htmx': request.headers.get('HX-Request') == 'true'
    }

# Now available in all templates
# {{ app_name }}, {{ current_year }}, {{ is_htmx }}
```

### Error Template Partials

Validation error and toast partials are needed in nearly every HTMX application:

**`templates/partials/_validation_errors.html`:**
```html
{% if errors %}
<div id="validation-errors" class="errors" role="alert">
    {% for field, messages in errors.items() %}
    <div class="error-group">
        <strong>{{ field }}:</strong>
        <ul>
            {% for msg in messages %}
            <li>{{ msg }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endfor %}
</div>
{% endif %}
```

**`templates/partials/_error_toast.html`:**
```html
<div id="toast-container"
     class="toast toast-error"
     role="alert"
     _="on load wait 5s then remove me">
    <span class="toast-icon">✕</span>
    <span class="toast-message">{{ message }}</span>
</div>
```

**Usage with HX-Retarget (server pushes error to specific container):**
```python
if errors:
    response = make_response(
        render_template('partials/_validation_errors.html', errors=errors), 400
    )
    response.headers['HX-Retarget'] = '#form-errors'
    response.headers['HX-Reswap'] = 'innerHTML'
    return response
```

### Pagination Partial (Load More)

**`templates/partials/_load_more.html`:**
```html
{% if has_more %}
<div id="load-more-sentinel"
     hx-get="{{ url_for('users.list_users', page=next_page) }}"
     hx-trigger="revealed"
     hx-swap="outerHTML"
     hx-indicator="#loading-spinner">
    <div id="loading-spinner" class="htmx-indicator">
        Loading more...
    </div>
</div>
{% endif %}
```

**Route:**
```python
@app.route('/users')
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    users = User.query.paginate(page=page, per_page=per_page)

    if request.headers.get('HX-Request') == 'true':
        return render_template('partials/_user_rows.html',
                             users=users.items,
                             has_more=users.has_next,
                             next_page=page + 1)
    return render_template('pages/users.html',
                         users=users.items,
                         has_more=users.has_next,
                         next_page=page + 1)
```

**Key rules:**
- The sentinel replaces itself (`hx-swap="outerHTML"`) with new rows + a new sentinel
- `hx-trigger="revealed"` fires when the element scrolls into view
- `{% if has_more %}` prevents rendering when no more pages exist

### Template Testing

Render partials in isolation to verify HTML structure:

```python
import pytest
from flask import Flask

@pytest.fixture
def app():
    app = Flask(__name__, template_folder='../templates')
    app.config['TESTING'] = True
    return app


def test_user_row_partial(app):
    """Test that user row partial renders correct HTML structure."""
    with app.app_context():
        from flask import render_template
        html = render_template('partials/_user_row.html', user={
            'id': 42, 'name': 'Jane Doe', 'email': 'jane@example.com',
        })
        assert 'id="user-42"' in html
        assert 'Jane Doe' in html
        assert 'hx-delete=' in html  # Delete button present


def test_validation_errors_partial(app):
    """Test error partial with multiple fields."""
    with app.app_context():
        from flask import render_template
        html = render_template('partials/_validation_errors.html', errors={
            'name': ['Name is required'],
            'email': ['Invalid email format'],
        })
        assert 'Name is required' in html
        assert 'Invalid email format' in html
```

**Key rules:**
- Test partials with minimal context — only pass required template variables
- Assert HTML structure (IDs, HTMX attributes) not just content
- Use `app.app_context()` for Flask or `Jinja2Environment` for framework-agnostic testing

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Missing Element IDs

**Problem:** HTMX-swappable elements lack unique IDs for targeting.

**Why It Fails:** HTMX cannot reliably target or replace elements; breaks OOB swaps.

**Correct Pattern:**
```html
<div id="user-123" hx-get="/users/123" hx-target="#user-123" hx-swap="outerHTML">
    <p>{{ user.name }}</p>
</div>
```

### Anti-Pattern 2: Partials Extending Base Template

**Problem:** Partial templates inherit from base.html with full page structure.

**Why It Fails:** HTMX receives entire HTML document instead of fragment; breaks swapping.

**Correct Pattern:**
```html
{# templates/partials/_user_row.html - standalone fragment #}
<tr id="user-{{ user.id }}">
    <td>{{ user.name }}</td>
    <td>{{ user.email }}</td>
</tr>
```

### Anti-Pattern 3: Inconsistent Template Naming

**Problem:** Mixed naming conventions for partials (underscores, hyphens, PascalCase).

**Why It Fails:** Hard to identify partials; confuses team; maintenance nightmare.

**Correct Pattern:**

Files in `templates/partials/`:
- `_user_table.html`
- `_user_form.html`
- `_user_row.html`

## Output Format Examples

### Complete Template Structure

Directory structure for `templates/`:
- `base.html` - HTMX config, CSRF, global layout
- **pages/**
  - `home.html` - Full page with HTMX elements
  - `users.html` - Full page with user table
- **partials/**
  - `_user_row.html` - Single user table row
  - `_user_form.html` - User edit/create form
  - `_users_table.html` - Complete user table
  - `_notification.html` - Toast notification
- **components/**
  - `_navbar.html` - Reusable navigation
  - `_form_field.html` - Form field macro
  - `_modal.html` - Modal component

### View with Conditional Rendering

See Section 5, Method 1 for the recommended view-level detection pattern with search filtering.
