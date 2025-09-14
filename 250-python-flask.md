**Description:** Comprehensive Flask web framework patterns covering application structure, blueprints, security, database integration, and deployment best practices for Python web applications.
**AppliesTo:** `**/*.py`, `**/app/**/*`, `**/blueprints/**/*`, `**/models/**/*`, `pyproject.toml`
**AutoAttach:** false
**Type:** Agent Requested
**Version:** 1.0
**LastUpdated:** 2025-09-14

# Python Flask Web Framework Best Practices

## 1. Installation and Project Setup

### Dependencies and Environment
- **Requirement:** Use `uv` for dependency management following `@200-python-core.md` patterns
- **Requirement:** Install Flask with: `uv add flask` or `uv add "flask[async]"` for async support
- **Rule:** Include essential extensions: `flask-sqlalchemy`, `flask-migrate`, `flask-wtf`, `flask-login`
- **Always:** Pin Flask to stable versions and use virtual environments

```toml
# pyproject.toml
[project]
dependencies = [
    "flask>=3.0.0",
    "flask-sqlalchemy>=3.1.0",
    "flask-migrate>=4.0.0",
    "flask-wtf>=1.2.0",
    "flask-login>=0.6.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-flask>=1.3.0",
    "flask-testing>=0.8.0",
]
```

### Application Structure
- **Rule:** Use application factory pattern for scalable Flask applications
- **Rule:** Organize code with blueprints for modular architecture
- **Always:** Separate configuration, models, views, and business logic

```
flask-project/
├── src/
│   └── myapp/
│       ├── __init__.py          # Application factory
│       ├── config.py            # Configuration classes
│       ├── models/              # Database models
│       │   ├── __init__.py
│       │   ├── user.py
│       │   └── product.py
│       ├── blueprints/          # Application blueprints
│       │   ├── __init__.py
│       │   ├── auth/
│       │   │   ├── __init__.py
│       │   │   ├── routes.py
│       │   │   └── forms.py
│       │   └── api/
│       │       ├── __init__.py
│       │       └── routes.py
│       ├── services/            # Business logic
│       │   ├── __init__.py
│       │   └── user_service.py
│       ├── static/              # Static files
│       └── templates/           # Jinja2 templates
├── tests/
├── migrations/                  # Database migrations
└── instance/                    # Instance-specific files
```

## 2. Application Factory Pattern

### Core Application Setup
- **Rule:** Use application factory for flexible configuration and testing
- **Always:** Initialize extensions outside the factory function
- **Rule:** Register blueprints and error handlers in the factory

```python
# src/myapp/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_name='development'):
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    app.config.from_object(f'myapp.config.{config_name.title()}Config')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    from myapp.blueprints.auth import auth_bp
    from myapp.blueprints.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    register_error_handlers(app)
    return app

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
```

### Configuration Management
- **Rule:** Use class-based configuration for different environments
- **Always:** Store sensitive data in environment variables

```python
# src/myapp/config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev.db'
    TEMPLATES_AUTO_RELOAD = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///prod.db'
    SSL_REDIRECT = True

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
```

## 3. Blueprint Organization

### Blueprint Structure
- **Rule:** Use blueprints to organize related functionality
- **Always:** Keep blueprint files focused and cohesive
- **Rule:** Use consistent naming conventions for blueprint modules

```python
# src/myapp/blueprints/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, template_folder='templates')

from . import routes, forms

# src/myapp/blueprints/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

from . import auth_bp
from .forms import LoginForm, RegistrationForm
from myapp.models.user import User
from myapp.services.user_service import UserService
from myapp import db

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = UserService.create_user(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
```

### Form Handling with Flask-WTF
- **Rule:** Use Flask-WTF for form validation and CSRF protection
- **Rule:** Provide clear error messages for validation failures

```python
# src/myapp/blueprints/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Register')
```

## 4. Database Models and Services

### SQLAlchemy Model Patterns
- **Rule:** Use SQLAlchemy ORM for database operations
- **Rule:** Implement model methods for common operations

```python
# src/myapp/models/user.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from myapp import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def create_user(username, email, password, **kwargs):
        user = User(username=username, email=email, **kwargs)
        user.set_password(password)
        return user
```

### Service Layer Pattern
- **Rule:** Implement service layer for business logic
- **Rule:** Handle exceptions appropriately in services

```python
# src/myapp/services/user_service.py
from myapp import db
from myapp.models.user import User

class UserService:
    @staticmethod
    def create_user(username, email, password, **kwargs):
        """Create a new user with validation."""
        # Validate input
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long')
        
        if User.query.filter_by(username=username).first():
            raise ValueError('Username already exists')
        
        # Create user
        user = User.create_user(username, email, password, **kwargs)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()
```

## 5. Security Best Practices

### Authentication and Authorization
- **Rule:** Use Flask-Login for session management
- **Always:** Implement proper password hashing
- **Rule:** Use decorators for access control

```python
# src/myapp/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """Decorator to require active user account."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_active:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Usage in routes
from myapp.decorators import admin_required, active_user_required

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Admin-only user management page."""
    users = User.query.all()
    return render_template('admin/users.html', users=users)
```

### Security Headers
- **Rule:** Enable CSRF protection for all forms
- **Always:** Implement security headers for production

```python
# Security headers middleware
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

## 6. Testing Patterns

### Test Configuration and Fixtures
- **Rule:** Use pytest with Flask-Testing for comprehensive testing
- **Rule:** Use fixtures for reusable test data

```python
# tests/conftest.py
import pytest
from myapp import create_app, db
from myapp.models.user import User

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User.create_user('testuser', 'test@example.com', 'testpass123')
        db.session.add(user)
        db.session.commit()
        return user

# tests/test_auth.py
def test_login_success(client, test_user):
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'testpassword123'
    })
    assert response.status_code == 200

def test_login_invalid_credentials(client):
    response = client.post('/auth/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    })
    assert b'Invalid email or password' in response.data

def test_protected_route_requires_login(client):
    response = client.get('/dashboard')
    assert response.status_code == 302
```

## 7. Deployment and Production

### WSGI Server Configuration
- **Rule:** Use production WSGI server like Gunicorn
- **Rule:** Configure proper logging and monitoring

```python
# wsgi.py
import os
from myapp import create_app

app = create_app(os.environ.get('FLASK_ENV', 'production'))

# Gunicorn configuration
bind = "0.0.0.0:8000"
workers = 4
timeout = 30
preload_app = True
```

### Docker Configuration
- **Rule:** Use production WSGI server and non-root user

```dockerfile
# Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd --create-home app
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY --chown=app:app . .
USER app

CMD ["gunicorn", "wsgi:app"]
```

## Related Rules

- **`@200-python-core.md`** - Core Python patterns and uv usage
- **`@201-python-lint-format.md`** - Ruff linting and formatting standards
- **`@203-python-project-setup.md`** - Python project structure and packaging
- **`@230-python-pydantic.md`** - Pydantic integration for data validation
- **`@800-project-changelog-rules.md`** - Changelog discipline for web application changes

## References and Resources

- [Flask Documentation](https://flask.palletsprojects.com/) - Official Flask documentation
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) - Database integration
- [Flask-Login](https://flask-login.readthedocs.io/) - User session management
- [Flask-WTF](https://flask-wtf.readthedocs.io/) - Form handling and CSRF protection

## Rule Type and Scope

- **Type:** Agent Requested (use `@250-python-flask.md` to apply)
- **Scope:** Python web development, Flask applications, web security, database integration
- **Applies to:** Web applications, REST APIs, authentication systems, database-driven applications
- **Validation:** Web application testing, security testing, performance testing
