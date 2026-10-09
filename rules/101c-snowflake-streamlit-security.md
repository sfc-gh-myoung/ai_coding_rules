---
schema_version: v4.0
rule_version: v6.0.0
description: "Streamlit app security on Snowflake: runtime-correct secrets, least-privilege owner rights, parameterized queries, validated inputs and uploads, safe rendering and sanitized errors."
last_updated: 2026-10-07
keywords:
  - kw:st.secrets
  - kw:SQL injection prevention
  - kw:Streamlit authentication
  - kw:input sanitization
  - kw:file upload validation
  - kw:container runtime secrets
token_budget: ~1050
context_tier: High
depends:
  required:
    - 107-snowflake-security-governance.md  # Snowflake security and RBAC
---
# Streamlit Security

## Scope

**What This Rule Covers:**
Security for Streamlit in Snowflake and locally run apps: secrets per runtime, owner's and restricted caller's rights, authentication and authorization, input and upload validation, SQL injection prevention, safe rendering, error handling and abuse controls.

**When to Load This Rule:**
When an app handles credentials, user input, uploads, sensitive data or access control; load `107-snowflake-security-governance.md` for RBAC and policies.

## Contract

### Inputs and Prerequisites

- App code, runtime, owner role, data sensitivity, intended viewers and existing auth, secrets and integrations.
- Data policies (masking, row access), allowed external endpoints and organizational security requirements.

### Mandatory

- Never hard-code credentials or commit secrets files. Container runtime: create Snowflake SECRET objects, attach them with an external access integration and the Streamlit `SECRETS` parameter, and read with `st.secrets`. Warehouse runtime: use the `_snowflake` secret functions (secrets.toml is unsupported there). Local development: `.streamlit/secrets.toml` excluded from version control.
- Creating or altering secrets, integrations, Streamlit objects and grants are approved mutations.
- SiS apps run queries with the owner's rights by default; give the owner role only the privileges viewers may exercise, rely on masking/row access policies for sensitive data, and use restricted caller's rights only where supported and needed.
- Authorize viewers with Snowflake access to the app and data rather than custom password schemes; do not store passwords in secrets or session state. Local or external deployments use an established identity provider or Streamlit's supported authentication.
- Parameterize all SQL with bound values or Snowpark expressions; validate identifiers against allowlists and never interpolate user input into SQL text.
- Validate inputs by type, range, length and allowed values (widget bounds help but server-side checks still apply); prefer allowlists over stripping characters.
- Validate uploads by declared type, size, parsed content and schema; never execute or render uploaded content as code or HTML, and process with resource limits.
- Render user or data content with text elements; avoid `unsafe_allow_html` and never pass untrusted content to HTML, markdown links or components without sanitization and URL scheme checks.
- Show generic error messages to viewers and log details through the event table or logging without secrets, tokens or sensitive data; avoid `st.exception` and raw exception text in production.
- Protect expensive or sensitive actions with confirmation, rate limiting and audit logging; keep per-user state in `st.session_state`, not shared globals or shared caches.
- Restrict external access to required hosts via network rules; never place secrets in URLs or query parameters.
- Test negative paths: injection attempts, invalid and oversized uploads, missing secrets, unauthorized viewers and error sanitization; do not claim security from review alone.

### Execution Steps

1. Read code, runtime, owner role, data sensitivity, secrets and integrations; identify trust boundaries.
2. Implement runtime-correct secrets, least-privilege access, parameterized queries, validation and safe rendering.
3. Run lint/security checks and negative tests in a non-production environment.
4. Report controls, privilege and integration changes, test evidence and residual risks.

### Validation

- No hard-coded or committed secrets; runtime-correct secret access.
- Owner role least-privilege; policies protect sensitive data.
- All SQL parameterized; inputs and uploads validated; no unsafe HTML.
- Errors sanitized; negative tests executed or gaps reported.

## References

- [SiS secrets and configuration](https://docs.snowflake.com/en/developer-guide/streamlit/app-development/secrets-and-configuration)
- [Restricted caller's rights](https://docs.snowflake.com/en/developer-guide/streamlit/features/restricted-callers-rights)
- [Streamlit secrets management](https://docs.streamlit.io/develop/concepts/connections/secrets-management)
- [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
