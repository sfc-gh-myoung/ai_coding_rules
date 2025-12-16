# Flask + HTMX Integration

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** flask, flask-htmx, blueprints, flask-login, session management, flask routes, flask templates, flask csrf, flask extensions, request context
**TokenBudget:** ~1950
**ContextTier:** Medium
**Depends:** rules/221-python-htmx-core.md, rules/221a-python-htmx-templates.md

## Purpose

Defines Flask-specific integration patterns for HTMX applications, covering Flask-HTMX extension usage, blueprint organization, route decorators, session management, and Flask-specific authentication patterns.

## Rule Scope

Flask web applications integrating HTMX for hypermedia-driven interfaces

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use Flask-HTMX extension** - Simplifies HTMX request detection with `htmx` object
- **Organize routes in blueprints** - Separate HTMX endpoints from full-page routes
- **Leverage Flask-Login** - Compatible with HTMX requests, use `@login_required` decorator
- **Configure CSRF protection** - Flask-WTF handles CSRF tokens for HTMX requests
- **Use `abort()` for errors** - Return error responses with proper status codes

**Pre-Execution Checklist:**
- [ ] Flask-HTMX extension installed and configured
- [ ] Blueprints created for API/HTMX routes
- [ ] Flask-WTF configured for CSRF protection
- [ ] Flask-Login integrated (if authentication required)
- [ ] Template directory structure follows conventions
- [ ] Route decorators applied consistently

## Contract

<inputs_prereqs>
Flask installed; Flask-HTMX extension; Flask-WTF for CSRF; Flask-Login for auth (optional); Jinja2 templates configured; HTMX core patterns (221-python-htmx-core.md); template strategies (221a-python-htmx-templates.md)
</inputs_prereqs>

<mandatory>
Flask framework; Flask-HTMX extension; Flask-WTF; Jinja2; CSRF protection enabled; blueprint registration; route decorators
</mandatory>

<forbidden>
Mixing business logic in routes; bypassing CSRF protection; returning JSON for HTMX requests; using global state instead of session; skipping authentication checks for HTMX endpoints
</forbidden>

<steps>
1. Install Flask-HTMX and Flask-WTF extensions
2. Configure Flask app with extensions (CSRF, HTMX, Login if needed)
3. Create blueprints for organizing routes (pages, api, htmx)
4. Define routes with proper decorators (@login_required, @csrf.exempt if needed)
5. Implement HTMX request detection using Flask-HTMX extension
6. Configure CSRF token inclusion in HTMX requests
7. Test routes with and without HTMX headers
</steps>

<output_format>
Flask application with blueprints, route handlers, HTMX integration via Flask-HTMX extension, CSRF-protected endpoints
</output_format>

<validation>
- Flask-HTMX extension detects HTMX requests correctly
- CSRF tokens validated for state-changing requests
- Authentication works for HTMX and full-page requests
- Blueprints registered and routes accessible
- Tests validate HTMX-specific behavior
</validation>

## Key Principles

### 1. Flask-HTMX Extension Setup

**Installation:**
```bash
pip install flask-htmx
# or
uv add flask-htmx
```

**Configuration:**
```python
from flask import Flask
from flask_htmx import HTMX

app = Flask(__name__)
htmx = HTMX(app)

# Now access via `htmx` object in routes
@app.route('/data')
def get_data():
    if htmx:  # True if HX-Request header present
        return render_template('partials/_data.html')
    return render_template('pages/data.html')
```

**Extension Features:**
```python
from flask import request

# Flask-HTMX provides `htmx` proxy object
@app.route('/example')
def example():
    # Check if HTMX request
    if htmx:  # Equivalent to request.headers.get('HX-Request') == 'true'
        pass

    # Access HTMX-specific request headers
    trigger_id = request.headers.get('HX-Trigger')
    target_id = request.headers.get('HX-Target')
    current_url = request.headers.get('HX-Current-URL')

    # Flask-HTMX also adds `htmx` to template context
    return render_template('template.html')  # {{ htmx }} available in template
```

### 2. Blueprint Organization

**Blueprint Structure:**
```python
# app/blueprints/pages.py - Full-page routes
from flask import Blueprint, render_template

pages = Blueprint('pages', __name__, template_folder='templates')

@pages.route('/')
def index():
    return render_template('pages/home.html')

@pages.route('/users')
def users():
    users = get_users()
    return render_template('pages/users.html', users=users)
```

```python
# app/blueprints/htmx_routes.py - HTMX-only endpoints
from flask import Blueprint, render_template, request, abort
from flask_htmx import htmx

htmx_bp = Blueprint('htmx', __name__, url_prefix='/htmx')

@htmx_bp.before_request
def check_htmx():
    """Ensure all routes in this blueprint are HTMX-only"""
    if not htmx:
        abort(400, 'HTMX request required')

@htmx_bp.route('/users/search')
def users_search():
    query = request.args.get('q', '')
    users = search_users(query)
    return render_template('partials/_users_table.html', users=users)

@htmx_bp.route('/users/<int:user_id>')
def user_detail(user_id):
    user = get_user(user_id)
    return render_template('partials/_user_detail.html', user=user)
```

**Blueprint Registration:**
```python
# app/__init__.py
from flask import Flask
from flask_htmx import HTMX
from flask_wtf.csrf import CSRFProtect

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Initialize extensions
    htmx = HTMX(app)
    csrf = CSRFProtect(app)

    # Register blueprints
    from app.blueprints.pages import pages
    from app.blueprints.htmx_routes import htmx_bp

    app.register_blueprint(pages)
    app.register_blueprint(htmx_bp)

    return app
```

### 3. Route Patterns

**Dual-Purpose Route (HTMX + Full Page):**
```python
@app.route('/users')
def users_list():
    users = get_users()

    if htmx:
        return render_template('partials/_users_table.html', users=users)

    return render_template('pages/users.html', users=users)
```

**HTMX-Only Route:**
```python
@app.route('/htmx/user/<int:user_id>/edit')
def edit_user_form(user_id):
    if not htmx:
        abort(400, 'HTMX request required')

    user = get_user_or_404(user_id)
    return render_template('partials/_user_form.html', user=user)
```

**State-Changing Route with Response Headers:**
```python
from flask import make_response

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    delete_user_from_db(user_id)

    response = make_response('', 200)
    response.headers['HX-Trigger'] = 'userDeleted'
    return response
```

### 4. CSRF Protection with Flask-WTF

**Configuration:**
```python
from flask import Flask
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
csrf = CSRFProtect(app)
```

**Base Template with CSRF Token:**
```html
{# templates/base.html #}
<meta name="csrf-token" content="{{ csrf_token() }}">

<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script>
  document.body.addEventListener('htmx:configRequest', (event) => {
    event.detail.headers['X-CSRFToken'] =
      document.querySelector('meta[name="csrf-token"]').content;
  });
</script>
```

**Form with CSRF Token:**
```html
<form hx-post="{{ url_for('create_user') }}" hx-target="#users-list">
    {{ form.hidden_tag() }}  {# Flask-WTF CSRF token #}
    {{ form.name.label }} {{ form.name() }}
    {{ form.email.label }} {{ form.email() }}
    <button type="submit">Create</button>
</form>
```

**Exempting Specific Routes (Use Sparingly):**
```python
@app.route('/public/data', methods=['POST'])
@csrf.exempt  # Only for truly public endpoints
def public_data():
    return render_template('partials/_data.html')
```

### 5. Flask-Login Integration

**Setup:**
```python
from flask_login import LoginManager, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

**Protected Route:**
```python
@app.route('/dashboard')
@login_required
def dashboard():
    if htmx:
        return render_template('partials/_dashboard_content.html', user=current_user)

    return render_template('pages/dashboard.html', user=current_user)
```

**HTMX Login Redirect:**
```python
from flask import redirect, url_for, make_response

@app.route('/protected')
@login_required
def protected_route():
    # Flask-Login automatically handles redirects
    # For HTMX requests, return HX-Redirect header
    return render_template('partials/_protected_content.html')

@login_manager.unauthorized_handler
def unauthorized():
    if htmx:
        response = make_response('Unauthorized', 401)
        response.headers['HX-Redirect'] = url_for('login')
        return response

    return redirect(url_for('login'))
```

### 6. Session Management

**Using Flask Session:**
```python
from flask import session

@app.route('/cart/add/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    cart = session.get('cart', [])
    cart.append(item_id)
    session['cart'] = cart

    response = make_response(
        render_template('partials/_cart_count.html', count=len(cart))
    )
    response.headers['HX-Trigger'] = 'cartUpdated'
    return response

@app.route('/cart')
def view_cart():
    cart_ids = session.get('cart', [])
    items = [get_item(id) for id in cart_ids]

    if htmx:
        return render_template('partials/_cart_items.html', items=items)

    return render_template('pages/cart.html', items=items)
```

### 7. Error Handling

**Global Error Handlers:**
```python
@app.errorhandler(404)
def not_found(error):
    if htmx:
        response = make_response(
            render_template('partials/_error.html',
                          message='Resource not found'),
            404
        )
        response.headers['HX-Retarget'] = '#error-container'
        return response

    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    if htmx:
        response = make_response(
            render_template('partials/_error.html',
                          message='Server error'),
            500
        )
        response.headers['HX-Retarget'] = '#error-container'
        return response

    return render_template('errors/500.html'), 500
```

**Route-Specific Error Handling:**
```python
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = get_user_or_404(user_id)
        user.name = request.form['name']
        db.session.commit()

        return render_template('partials/_user_row.html', user=user)

    except ValueError as e:
        response = make_response(
            f'<div class="error">{escape(str(e))}</div>',
            400
        )
        response.headers['HX-Retarget'] = '#error-container'
        return response
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Manual HTMX Header Checking

**Problem:** Manually checking `HX-Request` header instead of using Flask-HTMX extension.

**Why It Fails:** Repetitive code; easy to miss edge cases; harder to maintain.

**Correct Pattern:**
```python
from flask_htmx import htmx

@app.route('/data')
def get_data():
    if htmx:
        return render_template('partials/_data.html')
    return render_template('pages/data.html')
```

### Anti-Pattern 2: Missing CSRF Token Configuration

**Problem:** HTMX requests don't include CSRF tokens, causing validation failures.

**Why It Fails:** All POST/PUT/DELETE requests rejected; forms don't work.

**Correct Pattern:**
```html
<meta name="csrf-token" content="{{ csrf_token() }}">
<script src="https://unpkg.com/htmx.org@1.9.10"></script>
<script>
  document.body.addEventListener('htmx:configRequest', (event) => {
    event.detail.headers['X-CSRFToken'] =
      document.querySelector('meta[name="csrf-token"]').content;
  });
</script>
```

## Post-Execution Checklist

- [ ] Flask-HTMX extension installed and configured
- [ ] Blueprints created and registered
- [ ] CSRF protection enabled (Flask-WTF)
- [ ] CSRF token included in HTMX requests
- [ ] Flask-Login integrated (if authentication required)
- [ ] Unauthorized handler returns `HX-Redirect` for HTMX
- [ ] Error handlers check `htmx` and respond appropriately
- [ ] Session used for user-specific state
- [ ] Tests cover HTMX-specific routes and behavior

## Validation

**Success Checks:**
- `htmx` object correctly detects HTMX requests
- CSRF-protected routes reject requests without token
- Authentication required for protected HTMX routes
- Error handlers return partial HTML for HTMX requests
- Session data persists across HTMX requests

**Negative Tests:**
- HTMX request without CSRF token returns 403
- Unauthenticated HTMX request redirects to login
- Non-HTMX request to HTMX-only route returns 400

## Output Format Examples

### Complete Flask App Structure
```python
# app/__init__.py
from flask import Flask
from flask_htmx import HTMX
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'

    htmx = HTMX(app)
    csrf = CSRFProtect(app)
    login_manager = LoginManager(app)

    from app.blueprints.pages import pages
    from app.blueprints.htmx_routes import htmx_bp

    app.register_blueprint(pages)
    app.register_blueprint(htmx_bp)

    return app
```

## References

### External Documentation
- [Flask-HTMX Extension](https://github.com/edmondchuc/flask-htmx) - Official extension documentation
- [Flask Documentation](https://flask.palletsprojects.com/) - Flask framework guide
- [Flask-WTF](https://flask-wtf.readthedocs.io/) - CSRF protection and forms
- [Flask-Login](https://flask-login.readthedocs.io/) - User authentication

### Related Rules
- **HTMX Foundation**: `rules/221-python-htmx-core.md` - HTMX core patterns
- **Template Strategies**: `rules/221a-python-htmx-templates.md` - Jinja2 patterns
- **Testing Patterns**: `rules/221d-python-htmx-testing.md` - Testing Flask+HTMX
- **Common Patterns**: `rules/221e-python-htmx-patterns.md` - CRUD, forms, etc.
- **Python Core**: `rules/200-python-core.md` - Python standards
