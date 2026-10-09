---
schema_version: v4.0
rule_version: v5.0.0
description: "Testable Flask factories/blueprints, scoped extensions and transactions, secure session/forms, safe templates and deployment."
last_updated: 2026-10-07
keywords:
  - kw:application factory
  - kw:Flask blueprints
  - kw:Flask-SQLAlchemy
  - kw:CSRF protection
  - kw:Jinja2 templates
  - kw:Gunicorn deployment
  - kw:flask
token_budget: ~1100
context_tier: High
depends:
  required:
    - 200-python-core.md  # Python foundation patterns
  optional:
    - 203-python-project-setup.md  # Python project structure and packaging
    - 201-python-lint-format.md  # Code quality and formatting standards
---
# Flask Best Practices

## Scope

**What This Rule Covers:**
Existing app construction/blueprints, config/extensions, request/ORM/security/template lifecycle, tests and production runtime.

**When to Load This Rule:**
When building/modifying Flask apps; read `221b-python-htmx-flask.md` only for HTMX-specific behavior.

## Contract

### Inputs and Prerequisites

- Existing factory/config/blueprints/extensions/models/tests and installed Flask/Werkzeug/SQLAlchemy versions.
- Actual API/template/auth/session/form/database requirements and authorized startup/test/migration/deployment scope.

### Mandatory

- Inspect established structure before edits. Factory and unbound init_app extensions support isolated apps; a module-level WSGI app constructed by a factory is valid. Don't force Flask-WTF/SQLAlchemy/Gunicorn when equivalent existing components meet need.
- Validate effective environment-specific configuration before serving; required secrets have no sample/blank default. Ensure chosen testing/subclass config is validated, not a hardcoded base class. Don't log private values or read .env contents just for conventions.
- Keep extension state/resources scoped to actual app/request contexts; use current_app/g appropriately, not global mutable per-user state. Register existing blueprints once and avoid circular imports/duplicate factories.
- Validate/authenticate/authorize actual resources and input; browser/session cookies require CSRF on changes, secure/HttpOnly/SameSite policy and trusted redirect targets. Signed Flask cookies aren't encrypted; don't store secrets/private drafts assuming server storage.
- Store approved adaptive password hashes, no plaintext; login also checks active user and correct resource permissions. Rate limits need trusted proxy keys and appropriate shared store/thresholds across workers, not fixed universal numbers.
- Use explicit parameterized ORM/query APIs and request-scoped sessions. Commit only approved valid operations, rollback failures and let extension teardown remove sessions; do not blindly rollback unrelated session state in every generic handler.
- Reuse actual migrations; generating or applying/downgrading DB migrations and ownership changes need separate approval. Don't call create_all/drop_all against an unverified test/production URL or per-worker startup.
- Jinja autoescape remains enabled for HTML; no raw user interpolation/safe filter or arbitrary template source execution. URL/JS/rich HTML contexts require safe encoding/sanitization beyond plain autoescape.
- Errors preserve status/content contract and generic production details; log sanitized correlation evidence. API JSON and HTML/HTMX errors differ; debug/dev server are not production defaults.
- Async Flask functions require supported extras/extensions/server behavior; request-loop cancellation and WSGI worker occupancy differ from ASGI. Don't spawn unowned background tasks or reuse clients across incompatible loops.
- Test factory/config/blueprint/auth/CSRF/errors/transactions/templates under isolated app/request/client sessions with cleanup in finally. Disabling CSRF for unrelated unit tests must not become proof CSRF works; dedicated integration tests keep it enabled.
- Use supported production WSGI/platform process management, measured workers/pools/timeouts/probes and non-root container policy where relevant. Public binds, deploy/push/service starts and database operations need approved scope; no guaranteed speedup/server tolerance from a snippet.

### Execution Steps

1. Read application/toolchain/context/config/extensions and intended behavior/security requirements.
2. Implement minimal factory/blueprint/service/template change with scoped resources/transaction and protection.
3. Test isolated positive/negative/state/CSRF/context/cleanup paths; run project checks.
4. Verify only approved startup/deployment scope and report actual versus untested production behavior.

### Validation

- Actual config/app/blueprint/extension lifecycle and resource cleanup work without shared state.
- Auth/CSRF/session/input/query/template/error boundaries protect data and preserve statuses.
- Committed/failed transactions and isolated fixtures verified; no unauthorized DB schema mutation.
- Project checks pass, deployment/async/platform gaps explicit and no secret/dev server exposure.

## References

- [Flask factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)
- [Flask security](https://flask.palletsprojects.com/en/stable/web-security/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)
- [Flask async](https://flask.palletsprojects.com/en/stable/async-await/)
- [Flask deployment](https://flask.palletsprojects.com/en/stable/deploying/)
- [SQLAlchemy sessions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
