# Flask Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Flask, web development, blueprints, Flask-SQLAlchemy, templates, routing, Flask extensions, application factory, Jinja2, Flask-WTF, CSRF protection
**TokenBudget:** ~3700
**ContextTier:** High
**Depends:** rules/200-python-core.md

## Purpose
Provide comprehensive Flask development best practices, organized into focused patterns that cover all aspects of modern web application development including application architecture, security, templating, database integration, and deployment for building maintainable, secure web applications.

## Rule Scope

Flask web application development with modern patterns, security, and maintainable architecture

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use application factory pattern** - `create_app()` function, not global Flask instance
- **Organize with Blueprints** - Modular code in `blueprints/`, register with `app.register_blueprint()`
- **Enable CSRF protection** - Use Flask-WTF: `CSRFProtect(app)`
- **Environment-based config** - `app.config.from_object(config[env])`, never hardcode secrets
- **Template auto-escaping enabled** - Jinja2 XSS protection (default, but verify)
- **Use Flask-SQLAlchemy** - `db = SQLAlchemy(app)` for database integration
- **Never use global Flask instance** - Prevents testing, multi-environment support

**Quick Checklist:**
- [ ] App created via factory function
- [ ] Blueprints for modular organization
- [ ] CSRF protection enabled
- [ ] Environment-based configuration
- [ ] Templates use auto-escaping
- [ ] Flask-SQLAlchemy configured
- [ ] Run with `uv run flask --app app run`

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

<design_principles>
1. **Application Factory Pattern** - Use factory functions for app creation and configuration
2. **Blueprint Modularization** - Organize code into logical, reusable blueprints
3. **Security by Design** - Implement CSRF protection, input validation, and secure sessions
4. **Configuration Management** - Environment-based configuration with proper secret handling
5. **Template Security** - Proper Jinja2 templating with XSS protection
6. **Database Best Practices** - Use SQLAlchemy with proper session management
7. **Error Handling Excellence** - Custom error pages and comprehensive logging
8. **Testing Strategy** - Unit and integration testing with Flask's test client
9. **Production Readiness** - WSGI deployment with proper monitoring and logging
10. **Extension Integration** - Proper use of Flask ecosystem extensions
11. **Request Context Management** - Understand and leverage Flask's application and request contexts
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Using Flask's Development Server in Production

**Problem:** Running `flask run` or `app.run()` in production instead of a production WSGI server like Gunicorn or uWSGI.

**Why It Fails:** Development server is single-threaded, not designed for concurrent requests. No process management or auto-restart on crashes. Security features disabled. Performance is 10-100x worse than production servers.

**Correct Pattern:**
```python
# BAD: Development server in production
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Single-threaded, no fault tolerance

# GOOD: Production deployment with Gunicorn
# gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app

# wsgi.py
from app import create_app
app = create_app()

# Dockerfile
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "wsgi:app"]
```

### Anti-Pattern 2: Storing Secrets in Flask Config Files

**Problem:** Hardcoding SECRET_KEY, database passwords, or API keys in config.py or directly in application code.

**Why It Fails:** Secrets committed to version control. Visible to anyone with repo access. Cannot rotate without code changes. Different environments require code modification. Security audit failures.

**Correct Pattern:**
```python
# BAD: Hardcoded secrets
class Config:
    SECRET_KEY = "super-secret-key-12345"
    SQLALCHEMY_DATABASE_URI = "postgresql://user:password@localhost/db"

# GOOD: Environment variables with validation
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable required")

# Or use python-dotenv for local development
from dotenv import load_dotenv
load_dotenv()  # Loads from .env file (not committed to git)
```

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

> **Investigation Required**
> When applying this rule:
> 1. **Read existing Flask app structure BEFORE adding routes** - Check app.py, blueprints/, models/ organization
> 2. **Verify application factory usage** - Check if create_app() exists or if global Flask instance is used
> 3. **Never speculate about blueprint structure** - Read existing blueprints to understand registration patterns
> 4. **Check for Flask extensions** - Don't create duplicate extension instances (db, csrf, login_manager)
> 5. **Make grounded recommendations based on investigated app structure** - Match existing patterns
>
> **Anti-Pattern:**
> "Based on typical Flask apps, you probably use this blueprint structure..."
> "Let me add this route - it should work with standard patterns..."
>
> **Correct Pattern:**
> "Let me check your existing Flask app structure first."
> [reads app.py, blueprints/, checks for factory pattern and extensions]
> "I see you're using application factory with blueprints in blueprints/ and Flask-SQLAlchemy. Here's a new route following the same pattern..."

## Output Format Examples

```python
# Investigation: Check current implementation
# Read existing files, understand patterns

# Implementation: Following uv + ruff + pytest standards
from typing import Protocol
from datetime import datetime, UTC

class ServiceProtocol(Protocol):
    """Clear contract for service implementations."""

    def process(self, data: dict) -> dict:
        """Process data following validation rules."""
        ...

def implementation_function(input_data: dict) -> dict:
    """
    Implement feature following project conventions.

    Args:
        input_data: Validated input following schema

    Returns:
        Processed result with metadata

    Raises:
        ValueError: If input validation fails
    """
    # Use datetime.now(UTC) not datetime.utcnow()
    timestamp = datetime.now(UTC)

    # Implement business logic
    result = {"status": "success", "timestamp": timestamp}
    return result

# Validation: Test the implementation
def test_implementation_function():
    """Test following AAA pattern."""
    # Arrange
    test_input = {"key": "value"}

    # Act
    result = implementation_function(test_input)

    # Assert
    assert result["status"] == "success"
    assert "timestamp" in result
```

```bash
# Validation commands
uvx ruff check .
uvx ruff format --check .
uv run pytest tests/
```

## References

### External Documentation
- [Flask Documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask User's Guide](https://flask.palletsprojects.com/en/stable/#user-s-guide)
- [Flask API Reference](https://flask.palletsprojects.com/en/stable/#api-reference)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Werkzeug Documentation](https://werkzeug.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Related Rules
- **Python Core**: `rules/200-python-core.md`
- **Python Project Setup**: `rules/203-python-project-setup.md`
- **Python Linting**: `rules/201-python-lint-format.md`
- **Pydantic Integration**: `rules/230-python-pydantic.md`

## Flask Rule Categories

### Core Development Patterns (This File)
- Application structure and factory pattern
- Blueprint organization and registration
- Request handling and routing
- Template rendering with Jinja2
- Configuration management
- Integration with Python core rules

### [SECURE] Security and Forms
**Related Extensions:** Flask-WTF, Flask-Login, Flask-Security
- CSRF protection and form validation
- User authentication and session management
- Input sanitization and XSS prevention
- Security headers and HTTPS enforcement
- Password hashing and secure storage

### Database and Models
**Related Extensions:** Flask-SQLAlchemy, Flask-Migrate
- SQLAlchemy integration patterns
- Database session management
- Migration strategies
- Model relationships and queries

## Quick Reference

### Development Workflow
```bash
# Setup (following 200-python-core.md)
uv add flask
uv run flask --app app run --debug

# Testing
uv run pytest tests/ -v --cov=app

# Linting (see 201-python-lint-format.md for complete configuration)
uvx ruff check . && uvx ruff format .
```

### Essential Patterns
- **Application Factory**: Create apps through factory functions
- **Blueprint Organization**: Separate concerns into logical modules
- **Context Management**: Understand application and request contexts
- **Template Inheritance**: Use Jinja2 template inheritance effectively
- **Error Handling**: Custom error pages and proper exception handling
- **Configuration**: Environment-based settings with proper validation

## 1. Application Structure and Organization

### Project Layout
- **Always:** Use the application factory pattern for Flask applications.
- **Always:** Organize code using blueprints for modular architecture.
- **Always:** Follow the project structure from `203-python-project-setup.md` with proper `__init__.py` files.

Recommended directory structure for `app/`:
- `__init__.py` - Application factory
- `config.py` - Configuration classes
- **models/** - SQLAlchemy models
  - `__init__.py`, `user.py`, `post.py`
- **blueprints/** - Route modules
  - `__init__.py`
  - **auth/** - `__init__.py`, `routes.py` (Authentication routes), `forms.py` (WTForms forms)
  - **main/** - `__init__.py`, `routes.py` (Main application routes)
  - **api/** - `__init__.py`, `routes.py` (API endpoints)
- **templates/** - Jinja2 templates
  - `base.html` - Base template
  - **auth/**, **main/**
- **static/** - Static assets
  - **css/**, **js/**, **images/**
- `extensions.py` - Extension initialization

### Application Factory Pattern
- **Requirement:** Create Flask app instance through a factory function.
- **Always:** Separate app creation from configuration and extension initialization.
- **Reference:** [Flask Application Factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)

```python
# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf
from app.blueprints.main import main_bp
from app.blueprints.auth import auth_bp

def create_app(config_class=Config):
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register error handlers
    register_error_handlers(app)

    return app

def register_error_handlers(app):
    """Register custom error handlers."""
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
```

### Extension Management
- **Always:** Initialize extensions in a separate module for clean separation.
- **Rule:** Use `init_app()` pattern for all extensions to support application factory.

```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
cache = Cache()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'
```

## 2. Blueprint Architecture and Modular Design

### Blueprint Organization
- **Always:** Use blueprints to organize related functionality.
- **Always:** Group routes, forms, and templates by feature area.
- **Reference:** [Modular Applications with Blueprints](https://flask.palletsprojects.com/en/stable/blueprints/)

```python
# app/blueprints/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='templates')

from app.blueprints.auth import routes
```

```python
# app/blueprints/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.blueprints.auth.forms import LoginForm, RegistrationForm
from app.models.user import User
from app.extensions import db

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        flash('Invalid email or password', 'error')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
```

### Blueprint Registration
- **Always:** Register blueprints in the application factory.
- **Rule:** Use consistent URL prefixes for blueprint organization.
- **Always:** Group related blueprints with appropriate prefixes.

```python
# In create_app() function
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(api_bp, url_prefix='/api/v1')
app.register_blueprint(admin_bp, url_prefix='/admin')
```

## 3. Configuration Management

### Environment-Based Configuration
- **Always:** Use class-based configuration for different environments.
- **Always:** Store sensitive information in environment variables.
- **Reference:** [Configuration Handling](https://flask.palletsprojects.com/en/stable/config/)

```python
# app/config.py
import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # CSRF configuration
    WTF_CSRF_TIME_LIMIT = 3600

    # Mail configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

## 4. Database Integration and Models

### SQLAlchemy Integration
- **Always:** Use Flask-SQLAlchemy for database operations.
- **Always:** Implement proper model relationships and constraints.
- **Reference:** [SQLAlchemy in Flask](https://flask.palletsprojects.com/en/stable/patterns/sqlalchemy/)

```python
# app/models/user.py
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from datetime import datetime

class User(UserMixin, db.Model):
    """User model with authentication support."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Post(db.Model):
    """Post model with user relationship."""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Post {self.title}>'
```

### Database Session Management
- **Always:** Use proper session management with context handling.
- **Rule:** Always handle database exceptions and rollback on errors.

```python
# Proper session management in routes
@main_bp.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    """Create a new post."""
    form = PostForm()
    if form.validate_on_submit():
        try:
            post = Post(
                title=form.title.data,
                content=form.content.data,
                user_id=current_user.id
            )
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating your post.', 'error')
            app.logger.error(f'Error creating post: {e}')

    return render_template('main/create_post.html', form=form)
```

## 5. Security Best Practices

### CSRF Protection
- **Always:** Enable CSRF protection for all forms.
- **Always:** Use Flask-WTF for form handling and validation.
- **Reference:** [Security Considerations](https://flask.palletsprojects.com/en/stable/security/)

```python
# app/blueprints/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    """User login form with CSRF protection."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    """User registration form with validation."""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])

    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Choose a different one.')

    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Choose a different one.')
```

### Input Validation and Sanitization
- **Always:** Validate all user input using WTForms validators.
- **Always:** Use Jinja2's auto-escaping for XSS prevention.
- **Rule:** Never trust user input without proper validation.

```python
# Custom validators
from wtforms.validators import ValidationError
import re

def validate_strong_password(form, field):
    """Validate password strength."""
    password = field.data
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit.')
```

## 6. Template Management and Rendering

### Jinja2 Template Best Practices
- **Always:** Use template inheritance for consistent layouts.
- **Always:** Leverage Jinja2's auto-escaping for security.
- **Reference:** [Templates](https://flask.palletsprojects.com/en/stable/templating/)

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Flask App{% endblock %}</title>
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
</head>
<body>
    <nav class="navbar">
        <a href="{{ url_for('main.index') }}">Home</a>
        {% if current_user.is_authenticated %}
            <a href="{{ url_for('main.profile') }}">Profile</a>
            <a href="{{ url_for('auth.logout') }}">Logout</a>
        {% else %}
            <a href="{{ url_for('auth.login') }}">Login</a>
            <a href="{{ url_for('auth.register') }}">Register</a>
        {% endif %}
    </nav>

    <main class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </main>

    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
```

### Context Processors and Template Functions
- **Always:** Use context processors for commonly needed template data.
- **Rule:** Register custom template filters and functions appropriately.

```python
# In application factory or blueprint
@app.context_processor
def inject_user():
    """Inject common template variables."""
    return {
        'current_year': datetime.utcnow().year,
        'app_name': app.config.get('APP_NAME', 'Flask App')
    }

@app.template_filter('datetime')
def datetime_filter(value, format='%Y-%m-%d %H:%M'):
    """Format datetime for templates."""
    if value is None:
        return ""
    return value.strftime(format)
```

## 7. Error Handling and Logging

### Custom Error Pages
- **Always:** Implement custom error handlers for better user experience.
- **Always:** Log errors appropriately for debugging and monitoring.
- **Reference:** [Handling Application Errors](https://flask.palletsprojects.com/en/stable/errorhandling/)

```python
# Error handlers in application factory
def register_error_handlers(app):
    """Register custom error handlers."""

    @app.errorhandler(400)
    def bad_request(error):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Server Error: {error}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash('The form has expired. Please try again.', 'error')
        return redirect(request.referrer or url_for('main.index'))
```

### Logging Configuration
- **Always:** Configure proper logging for different environments.
- **Rule:** Use structured logging for better debugging and monitoring.

```python
# Logging configuration in config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def configure_logging(app):
    """Configure application logging."""
    if not app.debug and not app.testing:
        # Production logging
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')
```

## 8. Testing Strategies

### Flask Test Client
- **Always:** Use Flask's built-in test client for testing routes.
- **Always:** Test both successful and error scenarios.
- **Reference:** [Testing Flask Applications](https://flask.palletsprojects.com/en/stable/testing/)

```python
# tests/test_auth.py
import pytest
from app import create_app, db
from app.models.user import User
from app.config import TestingConfig

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()

def test_login_page(client):
    """Test login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_user_registration(client, app):
    """Test user registration process."""
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPass123',
        'password2': 'TestPass123'
    }, follow_redirects=True)

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.username == 'testuser'
```

## 9. Production Deployment

### WSGI Configuration
- **Always:** Use a production WSGI server like Gunicorn or uWSGI.
- **Always:** Configure proper environment variables for production.

```python
# wsgi.py
import os
from app import create_app
from app.config import config

config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config[config_name])

if __name__ == "__main__":
    app.run()
```

### Production Checklist
- **Critical:** Set `SECRET_KEY` to a secure random value
- **Critical:** Disable debug mode in production
- **Critical:** Use HTTPS with proper SSL certificates
- **Critical:** Configure proper database connection pooling
- **Critical:** Set up monitoring and logging
- **Critical:** Enable CSRF protection
- **Critical:** Configure secure session cookies

## 10. Integration with Python Core Rules

### Compliance with Existing Rules
- **Always:** Follow all directives from `200-python-core.md` for Python best practices.
- **Always:** Use `uv run flask` instead of bare `flask` for development.
- **Always:** Apply linting and formatting rules from `201-python-lint-format.md`.
- **Always:** Follow project setup patterns from `203-python-project-setup.md`.

### Development Commands
```bash
# Following Python core rules from 200-python-core.md
uv add flask flask-sqlalchemy flask-migrate flask-login flask-wtf
uv run flask --app app run --debug
uv run flask --app app db init
uv run flask --app app db migrate -m "Initial migration"
uv run flask --app app db upgrade

# Testing with coverage
uv run pytest tests/ -v --cov=app --cov-report=html

# Linting and formatting
uvx ruff check . && uvx ruff format .
```
