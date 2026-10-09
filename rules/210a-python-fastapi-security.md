---
schema_version: v4.0
rule_version: v5.0.0
description: "FastAPI authentication, validated token purpose/claims, revocable refresh, scoped authorization, password hashing, and secret hygiene."
last_updated: 2026-10-07
keywords:
  - kw:JWT authentication
  - kw:bcrypt password hashing
  - kw:HTTPBearer token validation
  - kw:token refresh pairs
  - kw:RBAC dependency injection
  - kw:environment secrets validation
  - kw:fastapi
token_budget: ~1400
context_tier: High
depends:
  required:
    - 210-python-fastapi-core.md  # FastAPI foundation patterns
  optional:
    - 200-python-core.md  # Python core patterns
    - 210e-python-fastapi-security-hardening.md  # CORS, headers, rate limiting, input validation
    - 210b-python-fastapi-testing.md  # Testing security implementations
---
# FastAPI Security Patterns

## Scope

**What This Rule Covers:**
Authentication scheme fit, password storage, JWT verification, access/refresh lifecycle, business authorization, registration and confidential configuration.

**When to Load This Rule:**
When implementing/reviewing FastAPI auth or token lifecycle. Read `210e-python-fastapi-security-hardening.md` for CORS/headers/limits and `210b-python-fastapi-testing.md` for security tests.

## Contract

### Inputs and Prerequisites

- Existing auth/provider/user/session model, installed security library versions, trust boundaries and required user/resource permissions.
- Issuer/audience/key/algorithm policy, access/refresh expiry/revocation contract, credential mechanism and allowed development test scope.
- Approved authentication changes, migration/rotation plan and actual dependency/build tooling.

### Mandatory

- Read existing auth/config/routes before choosing a scheme. JWT/HTTPBearer is one design, not mandatory replacement for sessions/OIDC/provider auth. A bearer extractor validates transport shape, not signature or authorization; OAuth2 password tutorial is not a default for every third-party application.
- Store only approved adaptive password hashes; current FastAPI guidance recommends pwdlib/Argon2 and PyJWT. Preserve verified legacy bcrypt/passlib compatibility when needed; changing libraries/hashes requires migration review, not unrequested dependency churn.
- Validate library password-length/encoding behavior without silent truncation, use unique salts/configured cost and safe verification, and rehash on approved policy upgrades. Offload expensive hashing from async event loop with bounded workers; never log passwords/hashes.
- Keep signing keys/credentials in approved secret mechanisms with no fallback/sample/generated-on-every-start key. Validate presence/appropriate strength at startup without printing values. Keys must remain consistent across workers and rotate through reviewed identifiers/trust windows.
- JWT is signed, not encrypted; omit secrets and unnecessary PII from claims. Verify fixed allowed algorithms, signature, required expiry and intended issuer/audience, subject type and token purpose. Do not trust algorithm/key URLs selected freely by untrusted headers.
- Validate access purpose on protected endpoints and refresh purpose on refresh endpoints; accepting any correctly signed token can let refresh tokens act as access tokens. Recheck current user existence, active/disabled state and applicable permissions.
- Use short access and bounded longer refresh lifetime from risk policy, not universal 30-minute/seven-day constants. Returning a new refresh string is not revoking the old token: implement atomic rotation with server-side token/session family/reuse detection and logout/compromise revocation where refresh is supported.
- Reject invalid/expired/missing/malformed tokens consistently with 401 and appropriate Bearer challenge; authenticated users lacking permission receive 403 under the API contract. Never let decode errors at refresh become a raw 500 or reveal claim/signature internals.
- Authorize resource/action/tenant ownership with trusted server-side entitlements at every relevant path, including services/background/reuse paths; route dependencies do not protect a direct service caller automatically. No blanket admin bypass unless approved, and path user_id is not authenticated identity.
- Registration/login validate inputs, hash before storage, enforce database uniqueness atomically and resist enumeration with agreed uniform responses and timing-conscious verification. Don't rely on check-then-insert alone for uniqueness or claim fixed timing guarantees.
- Rate-limit abuse-sensitive auth endpoints using actual trusted client/account keys and deployment-wide state; choose thresholds from policy. Browser cookie tokens need Secure/HttpOnly/SameSite and CSRF controls; CORS is not CSRF protection or authorization.
- Reuse supported typed dependencies/scope checks and explicit safe response models; never return token/hash/internal role fields accidentally. Validate mass-assignment restrictions, SQL parameterization and redirect/resource scopes beyond Pydantic types.
- Test signature/issuer/audience/expiry/purpose, disabled users, wrong roles/tenants, refresh replay/reuse/logout, and race/failure paths with synthetic data. Testing does not authorize changing production keys/grants or sending credentials to external tools.
- Treat discovered credential exposure as an incident: avoid reproducing values, recommend approved rotation/revocation and history remediation. A clean current tree alone does not prove secrets absent from history; do not rewrite history unasked.

### Execution Steps

1. Inspect current auth/users/config and required permission matrix; select minimal compatible scheme and migration risks.
2. Implement credential/hash handling, validated claims/purpose and active-user dependency with explicit resource authorization.
3. Implement approved refresh/revocation and registration uniqueness/session/browser protections where required.
4. Test allow/deny and token/race/replay boundaries, plus redacted logs and safe errors; run project validation.
5. Report auth behavior, security evidence, key/rotation and deployment gaps without unauthorized key/production changes.

### Validation

- No plaintext credentials, secret defaults or sensitive JWT/log/response fields; hashing/key handling match actual libraries/policy.
- All required JWT claims/purpose validated; refresh cannot authorize ordinary API calls and replay/revocation policy is enforced.
- Disabled/wrong-tenant/wrong-role users are denied through actual consumer paths and appropriate 401/403 responses.
- Registration races, safe error/timing behavior and browser CSRF/session controls are checked where relevant.
- Output includes permission/token contract, tests and unresolved deployment/provider gaps; no assumed compliance or blanket JWT requirement.

## References

- [FastAPI security and recommended hashing/JWT libraries](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Security dependency/scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)
- [JWT best current practices](https://www.rfc-editor.org/rfc/rfc8725)
- [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP API security](https://owasp.org/www-project-api-security/)
