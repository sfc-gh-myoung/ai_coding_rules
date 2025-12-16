# Streamlit Security: Input Validation and Secrets Management

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** st.secrets, SQL injection, authentication, secure streamlit, protect app, credentials management, API keys, environment variables, secure deployment, input sanitization, RBAC streamlit, access control, security patterns
**TokenBudget:** ~2550
**ContextTier:** High
**Depends:** rules/101-snowflake-streamlit-core.md, rules/107-snowflake-security-governance.md

## Purpose
Provide comprehensive security guidance for Streamlit applications including input validation, secrets management, authentication patterns, and security best practices to prevent common vulnerabilities.

## Rule Scope

Streamlit security, input validation, secrets management, authentication

## Quick Start TL;DR

**Purpose:** Concentrated reference of critical patterns for efficient rule consumption. Provides:
- **Token efficiency:** Self-sufficient guidance for common use cases
- **Position advantage:** Early placement benefits from attention bias
- **Progressive disclosure:** Assessment point for full rule loading decision

Position at top provides practical efficiency benefits for both LLMs and human developers.

**MANDATORY:**
**Essential Patterns:**
- **Use st.secrets for ALL credentials** - API keys, passwords, tokens (never hardcode)
- **Validate user inputs:** Use `st.number_input(min_value=..., max_value=...)` with bounds
- **Parameterized queries:** Use session.sql("SELECT * FROM ? WHERE id = ?", params) to prevent SQL injection
- **File upload limits:** Validate file type, size, and content before processing
- **Error handling:** Never expose secrets in error messages or logs
- **Use HTTPS in production:** Deploy with TLS/SSL for encrypted connections
- **Never hardcode credentials** - always use st.secrets or environment variables

**Quick Checklist:**
- [ ] All credentials in `.streamlit/secrets.toml` (not in code)
- [ ] Numeric inputs have min/max bounds
- [ ] File uploads validated (type, size, content)
- [ ] Database queries use parameterized statements
- [ ] Error messages don't expose secrets
- [ ] Authentication implemented for sensitive apps
- [ ] HTTPS configured for production deployment

## Contract

<contract>
<inputs_prereqs>
Streamlit app configured (see 101-snowflake-streamlit-core.md), st.secrets configured, understanding of security principles
</inputs_prereqs>

<mandatory>
st.secrets, st.text_input(), st.number_input(), st.file_uploader(), st.session_state (for auth state), type hints, validation functions
</mandatory>

<forbidden>
Hardcoded credentials, unvalidated user inputs, raw SQL string interpolation, exposing secrets in logs or UI, storing passwords in plain text
</forbidden>

<steps>
1. Use st.secrets for ALL credentials (API keys, passwords, tokens)
2. Validate and sanitize all user inputs before processing
3. Set reasonable bounds on numeric inputs (min, max values)
4. Validate file uploads for type, size, and content
5. Use parameterized queries to prevent SQL injection
6. Implement error handling that doesn't expose secrets
7. Deploy production apps using HTTPS
</steps>

<output_format>
Secure Streamlit app with validated inputs, secrets management, error handling that doesn't expose sensitive information
</output_format>

<validation>
Test with invalid inputs (should reject), verify secrets not exposed in UI/logs, test file upload limits, check error messages don't expose credentials
</validation>

<design_principles>
- **Secrets Management:** Use st.secrets for all credentials, never hardcode
- **Input Validation:** Validate and sanitize all user inputs
- **Error Handling:** Show user-friendly errors, never expose stack traces with secrets
- **Authentication:** Implement proper auth for sensitive applications
- **Deployment Security:** Use HTTPS, RBAC, audit logging
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Hardcoding credentials**
```python
# NEVER DO THIS
API_KEY = "sk-1234567890"
DB_PASSWORD = "my_password"
SNOWFLAKE_ACCOUNT = "my_account"
```
**Problem:** Credentials exposed in source code, version control, and deployment artifacts

**Correct Pattern:**
```python
# Use st.secrets
try:
    api_key = st.secrets["api"]["key"]
    db_password = st.secrets["database"]["password"]
except KeyError as e:
    st.error(f"Missing configuration: {e}")
    st.stop()
```

**Anti-Pattern 2: No input validation**
```python
# Accepts any input without validation
user_id = st.text_input("Enter user ID")
query = f"SELECT * FROM users WHERE id = '{user_id}'"  # SQL injection!
```
**Problem:** SQL injection vulnerability, potential data breach

**Correct Pattern:**
```python
# Validate and use safe query methods
user_id = st.text_input("Enter user ID")
if user_id.isdigit():
    users_df = session.table('users').filter(col('id') == int(user_id))
else:
    st.error("Invalid user ID format (must be numeric)")
```

**Anti-Pattern 3: Exposing secrets in error messages**
```python
try:
    conn = connect(password=db_password)
except Exception as e:
    st.error(f"Connection failed: {e}")  # May expose password!
```
**Problem:** Error messages may contain secrets from exception details

**Correct Pattern:**
```python
try:
    conn = connect(password=db_password)
except Exception as e:
    st.error("Database connection failed. Please contact support.")
    # Log internally without exposing to user
```

**Anti-Pattern 4: No file upload limits**
```python
uploaded_file = st.file_uploader("Upload file")
df = pd.read_csv(uploaded_file)  # No size or type validation!
```
**Problem:** Can accept huge files (DoS) or malicious content

**Correct Pattern:**
```python
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
if uploaded_file:
    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("File too large. Maximum 10MB.")
    else:
        df = pd.read_csv(uploaded_file)
```

## Post-Execution Checklist
- [ ] st.secrets used for ALL credentials (never hardcoded)
- [ ] All user inputs validated and sanitized
- [ ] File uploads have size and type validation
- [ ] SQL queries use parameterized patterns (no string interpolation)
- [ ] Error messages don't expose secrets or sensitive info
- [ ] Authentication implemented for sensitive applications
- [ ] HTTPS used for production deployment
- [ ] secrets.toml in .gitignore (never committed)

## Validation
- **Success Checks:** Secrets loaded without errors, invalid inputs rejected with clear messages, file upload limits enforced, SQL injection attempts fail, error messages user-friendly without secrets
- **Negative Tests:** Try uploading oversized file (should reject), test SQL injection attempt (should fail safely), remove secret (should show graceful error), expose error with secrets (should be sanitized)

> **Investigation Required**
> When applying this rule:
> 1. Read secrets.toml and verify configuration (if accessible)
> 2. Check all st.text_input, st.number_input, st.file_uploader for validation
> 3. Verify SQL queries use safe patterns (no string interpolation)
> 4. Never speculate about security - inspect actual code patterns
> 5. Check error handling doesn't expose secrets
> 6. Verify authentication implementation if present

## Output Format Examples
```python
import streamlit as st
import pandas as pd
import re

# Secrets management
try:
    api_key = st.secrets["api"]["key"]
except KeyError as e:
    st.error(f"Missing configuration: {e}")
    st.stop()

# Input validation
user_input = st.text_input("Enter value")
if user_input:
    # Sanitize input
    sanitized = re.sub(r'[^a-zA-Z0-9\s_-]', '', user_input)

    if sanitized != user_input:
        st.warning("Special characters removed from input")

# File upload with validation
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
if uploaded_file:
    MAX_SIZE = 10 * 1024 * 1024  # 10MB

    if uploaded_file.size > MAX_SIZE:
        st.error("File too large. Maximum 10MB.")
        st.stop()

    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"Loaded {len(df)} rows")
    except Exception:
        st.error("Invalid file format")
```

## References

### External Documentation

**Streamlit Security:**
- [Streamlit Secrets Management](https://docs.streamlit.io/develop/concepts/connections/secrets-management) - Official secrets management guide
- [Streamlit App Security](https://docs.streamlit.io/develop/concepts/design/custom-components#security) - Security considerations for apps
- [Deploy with Authentication](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/deploy-an-app) - Deployment authentication patterns

**Security Best Practices:**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Web application security risks
- [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) - Input validation best practices
- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html) - SQL injection prevention guide

**Snowflake Security:**
- [Snowflake Security Overview](https://docs.snowflake.com/en/user-guide/security) - Snowflake security model
- [Snowflake RBAC](https://docs.snowflake.com/en/user-guide/security-access-control) - Role-based access control

### Related Rules
- **Streamlit Core**: `rules/101-snowflake-streamlit-core.md`
- **Snowflake Security Governance**: `rules/107-snowflake-security-governance.md`
- **Python Core**: `rules/200-python-core.md`

> **[AI] Claude 4 Specific Guidance**
> **Claude 4 Streamlit Security Optimizations:**
> - Parallel security audit: Can review multiple input validation patterns simultaneously
> - Context awareness: Track secrets usage patterns across multiple files
> - Investigation-first: Excel at discovering hardcoded credentials and validation gaps
> - Pattern recognition: Quickly identify SQL injection vulnerabilities and unsafe patterns

## 1. Secrets Management

**MANDATORY:**
- **Mandatory:** Use `st.secrets` for all sensitive configuration (API keys, passwords, tokens)
- **Mandatory:** Never hardcode credentials in source code
- **Always:** For SiS, use Snowflake secrets management
- **Always:** For SPCS, use Kubernetes secrets or environment variables
- **Always:** Validate that required secrets exist before use

**Secrets Pattern:**
```python
# [PASS] Proper secrets usage
try:
    api_key = st.secrets["api"]["key"]
    db_password = st.secrets["database"]["password"]
    snowflake_account = st.secrets["snowflake"]["account"]
except KeyError as e:
    st.error(f"Missing required secret: {e}")
    st.stop()

# Never do this
api_key = "sk-1234567890abcdef"  # Hardcoded secret!
password = "my_password"  # Security violation!
```

**.streamlit/secrets.toml Structure:**
```toml
# Local development only - NEVER commit to version control!

[api]
key = "sk-your-api-key"
endpoint = "https://api.example.com"

[database]
username = "db_user"
password = "secure_password"
host = "db.example.com"

[snowflake]
account = "your_account"
user = "your_user"
password = "your_password"
```

**FORBIDDEN:**
**Security Rules:**
- Never commit secrets.toml to version control (add to .gitignore)
- Never log secrets or expose them in error messages
- Never display secrets in UI (even in debug mode)
- Never pass secrets in URL parameters

## 2. Input Validation

**MANDATORY:**
- **Mandatory:** Validate and sanitize all user inputs before processing
- **Mandatory:** Use type hints and validation for structured inputs
- **Always:** Set reasonable bounds on numeric inputs (min, max values)
- **Always:** Validate file uploads for type, size, and content

**Numeric Input Validation:**
```python
# [PASS] Validated numeric input with bounds
age = st.number_input(
    "Age",
    min_value=0,
    max_value=120,
    value=25,
    help="Enter age between 0 and 120"
)

# [PASS] Custom validation with feedback
quantity = st.number_input("Quantity", min_value=1, value=1)
if quantity > 1000:
    st.warning("Large quantity detected. Are you sure?")
```

**Text Input Sanitization:**
```python
import re
import html

# [PASS] Text input sanitization
user_input = st.text_input("Enter name")
if user_input:
    # Remove special characters
    sanitized = re.sub(r'[^a-zA-Z0-9\s_-]', '', user_input)

    # HTML escape for display
    safe_display = html.escape(sanitized)

    if sanitized != user_input:
        st.warning("Special characters were removed from input.")

    st.write(f"Sanitized input: {safe_display}")
```

**File Upload Validation:**
```python
# [PASS] File upload with comprehensive validation
uploaded_file = st.file_uploader("Upload CSV", type=['csv'])

if uploaded_file:
    # Size validation (10MB limit)
    MAX_SIZE = 10 * 1024 * 1024  # 10MB

    if uploaded_file.size > MAX_SIZE:
        st.error(f"File too large. Maximum size is {MAX_SIZE / (1024*1024):.0f}MB.")
        st.stop()

    try:
        # Content validation
        df = pd.read_csv(uploaded_file)

        # Validate required columns
        required_cols = ['date', 'value', 'category']
        missing_cols = set(required_cols) - set(df.columns)

        if missing_cols:
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
            st.stop()

        st.success(f"Successfully loaded {len(df)} rows")

    except Exception as e:
        st.error("Invalid file format. Please upload a valid CSV.")
        # Don't expose full exception to user
```

## 3. SQL Injection Prevention

**MANDATORY:**
**Always use parameterized queries to prevent SQL injection:**

**Vulnerable Pattern (Never Do This):**
```python
# DANGEROUS: SQL injection vulnerability
user_input = st.text_input("Enter user ID")
query = f"SELECT * FROM users WHERE id = '{user_input}'"  # VULNERABLE!
result = session.sql(query).to_pandas()
```

**Secure Pattern:**
```python
# [PASS] Safe: Use parameterized queries or query builders
user_input = st.text_input("Enter user ID")

# Snowpark DataFrame API (safe)
users_df = session.table('users').filter(col('id') == user_input)

# Or validate and sanitize input
if user_input.isdigit():
    query = f"SELECT * FROM users WHERE id = {int(user_input)}"
    result = session.sql(query).to_pandas()
else:
    st.error("Invalid user ID format")
```

## 4. Authentication and Authorization

**RECOMMENDED:**
**For sensitive applications, implement authentication:**

```python
import streamlit as st
import hashlib

def hash_password(password: str) -> str:
    """Hash password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_authentication():
    """Simple authentication check."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            # In production, check against database
            # NEVER hardcode passwords like this
            if username == st.secrets["admin"]["username"]:
                hashed = hash_password(password)
                if hashed == st.secrets["admin"]["password_hash"]:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:
                st.error("Invalid credentials")

        st.stop()

# Check auth before showing app
check_authentication()

# Main app code
st.write(f"Welcome, {st.session_state.username}!")
```

## 5. Error Handling and Logging

**MANDATORY:**
**Show user-friendly errors, never expose secrets or stack traces:**

```python
# [PASS] Safe error handling
try:
    api_key = st.secrets["api"]["key"]
    result = external_api_call(api_key)
except KeyError:
    st.error("Configuration error. Please contact support.")
    # Log internally but don't expose to user
except Exception as e:
    st.error("Operation failed. Please try again or contact support.")
    # Log for debugging but don't show to user
    with st.expander("Technical details (for support)"):
        # Show sanitized error info
        st.code(f"Error type: {type(e).__name__}")

# Never do this
try:
    result = risky_operation()
except Exception as e:
    st.error(f"Error: {e}")  # May expose secrets!
    st.exception(e)  # Exposes full stack trace!
```

## 6. Deployment Security

**MANDATORY:**
**Production Deployment Checklist:**
- [ ] Deploy using HTTPS (never HTTP for production)
- [ ] Use Snowflake RBAC for data access control
- [ ] Implement authentication for sensitive applications
- [ ] Add audit logging for sensitive operations
- [ ] Keep dependencies updated for security patches
- [ ] Set proper CORS policies if using external APIs
- [ ] Use rate limiting for API endpoints
- [ ] Implement session timeouts for authenticated apps
