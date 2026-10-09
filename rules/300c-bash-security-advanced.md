---
schema_version: v4.0
rule_version: v3.0.0
description: "Advanced bash security patterns covering privilege management, resource limits, network security, secure logging, parameter expansion safety, permission validation, and security testing methodologies."
last_updated: 2026-10-06
keywords:
  - kw:privilege dropping
  - kw:ulimit resource constraints
  - kw:URL validation localhost blocking
  - kw:audit logging security events
  - kw:parameter expansion whitelisting
  - kw:malicious payload testing
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 300a-bash-security.md  # Core security patterns (input validation, command injection, credentials)
  optional:
    - 300-bash-scripting-core.md  # Foundation bash scripting patterns
    - 300b-bash-testing-tooling.md  # Testing frameworks and CI/CD tooling
---
# Bash Security Advanced Patterns

## Scope

**What This Rule Covers:**
Least privilege, resource limits, endpoint authorization, audit safety and adversarial local fixtures.

**When to Load This Rule:**
When shell scripts handle privilege transitions, untrusted workloads, network destinations or security audit trails.

## Contract

### Inputs and Prerequisites

- Core shell-security guidance read, threat/resource model and approved endpoint/privilege scope.
- Actual platform capability, permissions, credential injection and audit storage policy.

### Mandatory

- Use least privilege and isolate required elevation to approved operations. Do not sudo/re-exec/drop users automatically without verified identity, groups and explicit scope.
- Bound CPU/memory/open-file/network time according to actual workload/platform limits; ulimit flags/units vary and may not provide a complete sandbox. Disable secret-bearing core dumps where policy requires.
- Parse URLs with a real parser and enforce approved schemes/hosts/ports. For untrusted destinations, account for userinfo, IPv6, alternate IP forms, private/link-local/metadata addresses, DNS rebinding and redirect destinations; substring regex checks are insufficient SSRF protection.
- Private/local destinations may be intentional approved services; do not blanket-ban all localhost or assume HTTPS implies trusted authorization. Secrets may reach only approved destinations.
- Audit authentication/authorization/mutation failures with safe timestamps, operation/user context and exact outcome; redact secrets/private data and prevent multiline/log injection.
- Audit files must be controlled, not world-writable or arbitrary user-supplied paths; rotation/retention and failure behavior explicit.
- Restrict exposed transformations/operations to known choices; quoted parameter expansion is not itself code execution and does not need invented bans unrelated to operation authority.
- File creation uses restrictive initial modes and validated policy-specific permissions. Do not grant arbitrary mode values or chmod unrelated assets through a generic helper.
- Defensive malicious-input tests use literal strings in disposable fixtures, never executed shell code or real destructive/resource-exhaustion payloads.
- Path/permission checks can race; document residual TOCTOU and use descriptor/atomic confinement where hostile concurrent writes matter.

### Execution Steps

1. Inspect privilege/resource/network/audit boundaries and exact platform behavior.
2. Implement scoped elevation/limits and parsed endpoint authorization including redirect/DNS policy.
3. Add safe audit/redaction and permission helpers with confined owned-resource cleanup.
4. Test invalid operations/paths/URLs/permissions and log injection using local fixtures and mocks.
5. Run static/behavior checks and report residual races, unavailable runtime enforcement and true failure outcomes.

### Validation

- Elevation minimal/approved, limits actual and no sandbox guarantee beyond evidence.
- Endpoint parser/allowlist rejects out-of-scope destinations and secret-bearing redirects/rebinding paths.
- Logs safe/controlled/redacted, mutation outcomes auditable and permission policy enforced.
- Defensive tests do not execute destructive input; cleanup confined, races handled or disclosed.
- ShellCheck/syntax/tests pass, no claim universal attack prevention from a regex or lint alone.

## References

- [OWASP SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Bash resource limits](https://www.gnu.org/software/bash/manual/html_node/Bash-Builtins.html)
- [OWASP command injection](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
