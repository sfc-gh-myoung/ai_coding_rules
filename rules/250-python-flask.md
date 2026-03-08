# Flask Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.2
**LastUpdated:** 2026-01-27
**LoadTrigger:** kw:flask, kw:web
**Keywords:** Flask, web, blueprints, Flask-SQLAlchemy, templates, routing, application factory
**TokenBudget:** ~1900
**ContextTier:** High
**Depends:** 200-python-core.md

## Scope

**What This Rule Covers:**
Flask application development: factory pattern, blueprints, security, SQLAlchemy, templates, deployment.

**When to Load:**
- Building Flask applications
- Implementing factory pattern and blueprints
- Securing Flask apps (CSRF, auth)
- Deploying to production

## References

### Dependencies
**Must Load First:** 200-python-core.md

**Related:** 203-python-project-setup.md, 201-python-lint-format.md

### External Documentation
- [Flask Documentation](https://flask.palletsprojects.com/en/stable/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## Contract

### Inputs and Prerequisites
Python 3.11+, Flask framework, HTTP protocols understanding

### Mandatory
- Application factory pattern
- Blueprints for modular organization
- Flask-WTF for forms, Flask-SQLAlchemy for DB
- CSRF protection enabled
- Environment-based configuration
- Jinja2 templates with auto-escaping

### Forbidden
- Global Flask instance
- Hardcoded secrets
- Development server in production
- Plaintext passwords
- Disabled CSRF protection

### Execution Steps
1. Create app via factory function
2. Organize into blueprints
3. Configure environment-based settings
4. Enable CSRF with Flask-WTF
5. Integrate Flask-SQLAlchemy
6. Implement error handling/logging
7. Create Jinja2 templates
8. Test with Flask test client
9. Deploy with Gunicorn

### Output Format
Flask app with factory pattern, blueprints, secure config, production-ready deployment

### Validation
- App created via factory
- Blueprints registered
- CSRF enabled
- Environment config working
- Tests passing

### Post-Execution Checklist
- [ ] Factory function creates app
- [ ] Blueprints organized
- [ ] CSRF protection enabled
- [ ] Environment-based config
- [ ] Templates use auto-escaping
- [ ] Flask-SQLAlchemy configured
- [ ] Error handlers registered
- [ ] Tests passing

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Development Server in Production
```python
# WRONG
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```
**Problem:** Single-threaded, no fault tolerance, 10-100x slower than production servers.

**Correct Pattern:**
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app
```

### Anti-Pattern 2: Hardcoded Secrets
```python
# WRONG
class Config:
    SECRET_KEY = "super-secret-key-12345"
```
**Problem:** Secrets in version control, cannot rotate, security audit failure.

**Correct Pattern:**
```python
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY required")
```

## Implementation Details

### Project Structure
```
app/
├── __init__.py         # Factory
├── config.py           # Configuration
├── extensions.py       # Extensions
├── models/             # SQLAlchemy models
├── blueprints/
│   ├── auth/          # Auth routes/forms
│   ├── main/          # Main routes
│   └── api/           # API endpoints
├── templates/
└── static/
```

### Application Factory
```python
# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager, csrf

from app.blueprints.main import main_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    app.register_blueprint(main_bp)
    register_error_handlers(app)
    return app
```

### Extensions
```python
# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

### Blueprint Pattern
```python
# app/blueprints/auth/__init__.py
from flask import Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='templates')
from app.blueprints.auth import routes
```

```python
# app/blueprints/auth/routes.py
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
    return render_template('auth/login.html', form=form)
```

### Configuration
```python
# app/config.py
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
```

### Forms with CSRF
```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
```

### Model Example
```python
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

### Error Handlers
```python
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
```

### Testing
```python
import pytest
from app import create_app, db
from app.config import TestingConfig

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_login_page(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
```

### Base Template
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}App{% endblock %}</title>
</head>
<body>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% for category, message in messages %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
    {% endwith %}
    {% block content %}{% endblock %}
</body>
</html>
```

### Production Deployment
```python
# wsgi.py
from app import create_app
app = create_app()
```

```bash
# Development
uv run flask --app app run --debug

# Production
gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app

# Testing
uv run pytest tests/ -v --cov=app
```
