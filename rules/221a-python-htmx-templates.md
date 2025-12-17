# HTMX Template Strategies

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** jinja2, templates, partials, fragments, template composition, conditional rendering, htmx templates, template organization, reusable components, template context
**TokenBudget:** ~2300
**ContextTier:** High
**Depends:** rules/221-python-htmx-core.md

## Purpose

Defines Jinja2 template organization patterns for HTMX applications, covering partial rendering, fragment composition, conditional template logic, and reusable component strategies for hypermedia-driven interfaces.

## Rule Scope

Python web applications using Jinja2 templates with HTMX (applies to Flask, FastAPI, Django with Jinja2, and other Python frameworks)

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Organize by purpose** - Separate base templates, full pages, partials, and fragments
- **Detect HTMX in templates** - Use `request.headers.get('HX-Request')` for conditional rendering
- **Create reusable partials** - Small, focused template fragments for HTMX responses
- **Use template inheritance** - Base templates for full pages, partials extend sparingly or not at all
- **Minimize context** - Partials receive only necessary data, avoid passing entire app state
- **Include IDs for targeting** - All HTMX-swappable elements need unique IDs

**Pre-Execution Checklist:**
- [ ] Template directory structure defined (base, pages, partials)
- [ ] Base template includes HTMX library and configuration
- [ ] Partial templates created for HTMX responses
- [ ] Template naming convention established (e.g., `_partial_name.html`)
- [ ] HTMX detection logic available in templates or views
- [ ] Component IDs consistently applied for targeting
- [ ] Template context minimized for partials

## Contract

<inputs_prereqs>
Jinja2 template engine configured; HTMX library available; understanding of template inheritance; template directory structure; HTMX core patterns (221-python-htmx-core.md)
</inputs_prereqs>

<mandatory>
Jinja2 installed; template loader configured; HTMX library in base template; unique element IDs for HTMX targets; partial template directory
</mandatory>

<forbidden>
Mixing full-page and partial logic in single template; returning partials without proper IDs; deeply nested template inheritance for partials; passing unnecessary context to partials; hard-coding URLs in templates
</forbidden>

<steps>
1. Create template directory structure (base, pages, partials)
2. Define base template with HTMX library and configuration
3. Build full-page templates using inheritance
4. Create focused partials for HTMX responses (no/minimal inheritance)
5. Add HTMX detection logic in views or templates
6. Implement conditional rendering for HTMX vs. full-page requests
7. Test partial rendering in isolation and within full pages
</steps>

<output_format>
Organized template files: base.html, page templates, partial templates; conditional rendering logic in views; reusable template components
</output_format>

<validation>
- Templates organized by purpose (base, pages, partials)
- Partials render correctly in isolation
- HTMX requests return appropriate partials
- Full-page requests return complete documents
- Element IDs unique and consistent
- Tests validate template rendering for both request types
</validation>

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

    {# HTMX Library #}
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>

    {# HTMX Configuration #}
    <script>
        // CSRF token for all HTMX requests
        document.body.addEventListener('htmx:configRequest', (event) => {
            event.detail.headers['X-CSRFToken'] =
                document.querySelector('meta[name="csrf-token"]').content;
        });

        // Global event handling
        document.body.addEventListener('htmx:afterSwap', (event) => {
            console.log('HTMX swap completed');
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

**Method 2: Template-Level Detection:**
```html
{# templates/users.html #}
{% if request.headers.get('HX-Request') %}
    {# Partial response for HTMX #}
    {% include 'partials/_users_table.html' %}
{% else %}
    {# Full page response #}
    {% extends "base.html" %}
    {% block content %}
        <h1>Users</h1>
        {% include 'partials/_users_table.html' %}
    {% endblock %}
{% endif %}
```

**Method 3: Macro-Based Conditional:**
```html
{# templates/macros/render.html #}
{% macro render_content(content_template, context) %}
    {% if request.headers.get('HX-Request') %}
        {% include content_template with context %}
    {% else %}
        {% extends "base.html" %}
        {% block content %}
            {% include content_template with context %}
        {% endblock %}
    {% endif %}
{% endmacro %}
```

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

## Post-Execution Checklist

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

## Validation

**Success Checks:**
- Partials render correctly in isolation
- Full pages display properly with embedded partials
- HTMX requests return appropriate partials
- Non-HTMX requests return complete pages
- Element IDs unique across all templates
- Template context contains only necessary data

**Negative Tests:**
- Partial without ID cannot be targeted
- Requesting partial without HTMX headers returns full page
- Deep inheritance in partials causes rendering issues

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
```python
from flask import Flask, render_template, request

@app.route('/users')
def users_list():
    users = get_users()
    search_query = request.args.get('q', '')

    if search_query:
        users = [u for u in users if search_query.lower() in u.name.lower()]

    # Return partial for HTMX, full page otherwise
    if request.headers.get('HX-Request') == 'true':
        return render_template('partials/_users_table.html', users=users)

    return render_template('pages/users.html', users=users)
```

## References

### External Documentation
- [Jinja2 Documentation](https://jinja.palletsprojects.com/) - Official Jinja2 reference
- [HTMX Examples](https://htmx.org/examples/) - Template patterns with HTMX
- [Flask Templates](https://flask.palletsprojects.com/en/latest/tutorial/templates/) - Flask template guide
- [FastAPI Templates](https://fastapi.tiangolo.com/advanced/templates/) - Jinja2 with FastAPI

### Related Rules
- **HTMX Foundation**: `rules/221-python-htmx-core.md` - HTMX core patterns
- **Flask Integration**: `rules/221b-python-htmx-flask.md` - Flask-specific template patterns
- **FastAPI Integration**: `rules/221c-python-htmx-fastapi.md` - FastAPI template setup
- **Common Patterns**: `rules/221e-python-htmx-patterns.md` - Template patterns for CRUD, forms, etc.
- **Python Core**: `rules/200-python-core.md` - Python coding standards
