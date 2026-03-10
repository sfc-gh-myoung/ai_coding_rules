# Flask + HTMX Integration

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:htmx-flask
**Keywords:** flask, flask-htmx, blueprints, flask-login, session management, flask routes, flask templates, flask csrf, flask extensions, request context
**TokenBudget:** ~4450
**ContextTier:** Medium
**Depends:** 221-python-htmx-core.md, 221a-python-htmx-templates.md

## Scope

**What This Rule Covers:**
Flask-specific integration patterns for HTMX applications, covering Flask-HTMX extension usage, blueprint organization, route decorators, session management, and Flask-specific authentication patterns.

**When to Load This Rule:**
- Building Flask applications with HTMX
- Using Flask-HTMX extension for request detection
- Organizing Flask routes with blueprints for HTMX
- Implementing Flask-Login with HTMX
- Managing CSRF protection for HTMX requests in Flask

## References

### Dependencies

**Must Load First:**
- **221-python-htmx-core.md** - HTMX foundation patterns
- **221a-python-htmx-templates.md** - Jinja2 patterns

**Related:**
- **221d-python-htmx-testing.md** - Testing Flask+HTMX
- **221e-python-htmx-patterns.md** - CRUD, forms, etc.
- **200-python-core.md** - Python standards

### External Documentation

- [Flask-HTMX Extension](https://github.com/edmondchuc/flask-htmx) - Official extension documentation
- [Flask Documentation](https://flask.palletsprojects.com/) - Flask framework guide
- [Flask-WTF](https://flask-wtf.readthedocs.io/) - CSRF protection and forms
- [Flask-Login](https://flask-login.readthedocs.io/) - User authentication

## Contract

### Inputs and Prerequisites

- Flask installed
- Flask-HTMX extension
- Flask-WTF for CSRF
- Flask-Login for auth (optional)
- Jinja2 templates configured
- HTMX core patterns (221-python-htmx-core.md)
- Template strategies (221a-python-htmx-templates.md)

### Mandatory

- Flask framework
- Flask-HTMX extension
- Flask-WTF
- Jinja2
- CSRF protection enabled
- Blueprint registration
- Route decorators

### Forbidden

- Mixing database queries, data transformations, and external API calls in routes (keep in service layer)
- Bypassing CSRF protection
- Returning JSON for HTMX requests
- Using global state instead of session
- Skipping authentication checks for HTMX endpoints

### Execution Steps

1. Install Flask-HTMX and Flask-WTF extensions
2. Configure Flask app with extensions (CSRF, HTMX, Login if needed)
3. Create blueprints for organizing routes (pages, api, htmx)
4. Define routes with proper decorators (@login_required, @csrf.exempt if needed)
5. Implement HTMX request detection using Flask-HTMX extension
6. Configure CSRF token inclusion in HTMX requests
7. Test routes with and without HTMX headers

### Output Format

- Flask application with blueprints
- Route handlers
- HTMX integration via Flask-HTMX extension
- CSRF-protected endpoints

### Validation

**Pre-Task-Completion Checks:**
- Flask-HTMX extension installed and configured
- Blueprints created for API/HTMX routes
- Flask-WTF configured for CSRF protection
- Flask-Login integrated (if authentication required)
- Template directory structure follows conventions
- Route decorators applied consistently

**Success Criteria:**
- Flask-HTMX extension detects HTMX requests correctly
- CSRF tokens validated for state-changing requests
- Authentication works for HTMX and full-page requests
- Blueprints registered and routes accessible
- Tests validate HTMX-specific behavior

### Design Principles

- **Use Flask-HTMX extension** - Simplifies HTMX request detection with `htmx` object
- **Organize routes in blueprints** - Separate HTMX endpoints from full-page routes
- **Leverage Flask-Login** - Compatible with HTMX requests, use `@login_required` decorator
- **Configure CSRF protection** - Flask-WTF handles CSRF tokens for HTMX requests
- **Use `abort()` for errors** - Return error responses with proper status codes

### Post-Execution Checklist

- [ ] Flask-HTMX extension installed and configured
- [ ] Blueprints created and registered
- [ ] CSRF protection enabled (Flask-WTF)
- [ ] CSRF token included in HTMX requests
- [ ] Flask-Login integrated (if authentication required)
- [ ] Unauthorized handler returns `HX-Redirect` for HTMX
- [ ] Error handlers check `htmx` and respond appropriately
- [ ] Session used for user-specific state
- [ ] Tests cover HTMX-specific routes and behavior

> **Investigation Required**
> Before modifying Flask+HTMX integration, the agent MUST:
> 1. Check if `create_app()` factory already exists — extend it, never create a second factory
> 2. Verify Flask-HTMX extension status: `uv pip list | grep flask-htmx`
> 3. Read existing blueprint structure and naming conventions
> 4. Check current CSRF protection — Flask-WTF may already be configured with `htmx:configRequest` listener
> 5. Read existing Flask-Login setup and unauthorized handler before adding auth patterns
> 6. Check existing error handlers (404, 500) — extend rather than replace

## Key Principles

### 1. Flask-HTMX Extension Setup

**Installation:**
```bash
uv add flask-htmx
```

**Configuration:**
```python
from flask import Flask
from flask_htmx import HTMX

app = Flask(__name__)
htmx = HTMX(app)
# The `htmx` variable here is the app-level HTMX instance.
# In blueprints, import the proxy: `from flask_htmx import htmx`

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
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
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

**Exempting Specific Routes (Only for public read-only endpoints accepting no user input):**
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

### 7. Flash Messages with HTMX

Flask's `flash()` system needs special handling for HTMX partial responses:

**`templates/partials/_flash_messages.html`:**
```html
{% with messages = get_flashed_messages(with_categories=true) %}
{% if messages %}
<div id="flash-messages" role="alert">
    {% for category, message in messages %}
    <div class="flash flash-{{ category }}">{{ message }}</div>
    {% endfor %}
</div>
{% endif %}
{% endwith %}
```

**Route pattern — trigger flash refresh via HX-Trigger:**
```python
@app.route('/users', methods=['POST'])
def create_user():
    user = create_user_from_form(request.form)
    flash(f'User {user.name} created.', 'success')

    if htmx:
        response = make_response(render_template('partials/_user_row.html', user=user))
        response.headers['HX-Trigger'] = json.dumps({
            'userCreated': None,
            'showFlash': None,  # Trigger flash container refresh
        })
        return response
    return redirect(url_for('users.list_users'))
```

**Base template — flash container with HTMX listener:**
```html
<div id="flash-container"
     hx-get="{{ url_for('main.flash_messages') }}"
     hx-trigger="showFlash from:body"
     hx-swap="innerHTML">
    {% include 'partials/_flash_messages.html' %}
</div>
```

```python
@app.route('/flash-messages')
def flash_messages():
    return render_template('partials/_flash_messages.html')
```

**Key rules:**
- Use `HX-Trigger: {"showFlash": null}` to refresh the flash container after HTMX actions
- The flash container listens for `showFlash` events from any element (`from:body`)
- For non-HTMX requests, `redirect()` triggers normal flash display on next page load

### 8. File Upload with HTMX

HTMX supports file uploads with `hx-encoding="multipart/form-data"`:

```html
<form hx-post="{{ url_for('files.upload') }}"
      hx-encoding="multipart/form-data"
      hx-target="#upload-result"
      hx-indicator="#upload-spinner">
    <input type="file" name="file" accept=".csv,.xlsx" required>
    <button type="submit">Upload</button>
    <span id="upload-spinner" class="htmx-indicator">Uploading...</span>
</form>
<div id="upload-result"></div>
```

```python
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'.csv', '.xlsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file or not file.filename:
        return render_template('partials/_error_toast.html',
                             message='No file selected'), 400

    filename = secure_filename(file.filename)
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return render_template('partials/_error_toast.html',
                             message=f'Invalid file type: {ext}'), 400

    content = file.read()
    if len(content) > MAX_FILE_SIZE:
        return render_template('partials/_error_toast.html',
                             message='File too large (max 10 MB)'), 400
    file.seek(0)

    save_path = Path(app.config['UPLOAD_FOLDER']) / filename
    file.save(save_path)
    return render_template('partials/_upload_success.html',
                         filename=filename, size=len(content))
```

**Key rules:**
- `hx-encoding="multipart/form-data"` is REQUIRED — without it, files are not sent
- Always use `secure_filename()` from Werkzeug
- Validate file extension and size server-side (never trust client `accept` attribute)

### 9. Flask Async Routes (Flask 2.0+)

Flask 2.0+ supports `async def` routes. HTMX endpoints work identically — no client-side changes needed:

```python
@htmx_bp.route('/users/search')
async def search_users():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return render_template('partials/_empty_results.html')

    users = await db.execute(select(User).where(User.name.ilike(f'%{query}%')))
    return render_template('partials/_users_table.html', users=users.scalars().all())
```

**Key rules:**
- Requires `uv add flask[async]` (installs `asgiref`)
- Use `async def` only for I/O-bound operations (database, HTTP calls) — sync `def` for CPU-bound work
- The `htmx` proxy from Flask-HTMX works in both sync and async routes

### 10. Error Handling

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

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Manual HTMX Header Checking

**Problem:** Manually checking `HX-Request` header instead of using Flask-HTMX extension.

**Correct Pattern:**
```python
# BAD: Manual header checking
@app.route("/items")
def get_items():
    is_htmx = request.headers.get("HX-Request") == "true"
    if is_htmx:
        return render_template("partials/items.html")
    return render_template("items.html")

# GOOD: Use Flask-HTMX extension
from flask_htmx import HTMX
htmx = HTMX(app)

@app.route("/items")
def get_items():
    if htmx:  # Extension handles all edge cases
        return render_template("partials/items.html")
    return render_template("items.html")
```

Use `if htmx:` from the Flask-HTMX extension (see Section 1) — it handles all edge cases.

### Anti-Pattern 2: Missing CSRF Token Configuration

**Problem:** HTMX requests don't include CSRF tokens, causing validation failures.

**Why It Fails:** All POST/PUT/DELETE requests rejected; forms don't work.

**Correct Pattern:**
```html
<!-- In base.html head -->
<meta name="csrf-token" content="{{ csrf_token() }}">

<script>
document.body.addEventListener('htmx:configRequest', function(evt) {
    evt.detail.headers['X-CSRFToken'] = document.querySelector('meta[name="csrf-token"]').content;
});
</script>
```

## Output Format Examples

See `create_app()` in Section 2 (Blueprint Registration) for the full application factory pattern.
