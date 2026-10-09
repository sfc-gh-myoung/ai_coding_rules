---
schema_version: v4.0
rule_version: v5.0.0
description: "Comprehensive bash scripting security practices covering input validation, path security, permissions, and secure coding patterns to prevent vulnerabilities and ensure safe script execution."
last_updated: 2026-10-06
keywords:
  - kw:bash input sanitization
  - kw:command injection prevention
  - kw:shell path traversal
  - kw:bash credential storage
  - kw:shell script permissions
  - kw:eval alternatives
token_budget: ~1000
context_tier: High
depends:
  required:
    - 300-bash-scripting-core.md  # Foundation bash scripting patterns
  optional:
    - 300b-bash-testing-tooling.md  # Testing security implementations
    - 300c-bash-security-advanced.md  # Advanced security: privilege, network, logging, testing
---
# Bash Security Best Practices

## Scope

**What This Rule Covers:**
Input/operation allowlists, command and path safety, credentials, restrictive resources and defensive shell tests.

**When to Load This Rule:**
When handling untrusted arguments/environment/config, sensitive operations, file paths or credentials in shell scripts.

## Contract

### Inputs and Prerequisites

- All input/trust boundaries and approved operations/paths/destinations identified.
- Actual runtime/platform/tool versions, filesystem ownership and secret manager.

### Mandatory

- Validate types/lengths/allowed operations before effects. Reject invalid input rather than silently sanitizing into another filename/resource or creating collisions.
- Use fixed executable/operation choices with quoted argument arrays and -- where supported. Unquoted expansion causes splitting/option injection; it does not itself reinterpret a semicolon as shell syntax. eval or command-string reparsing introduces that risk.
- Never eval/source untrusted text or execute arbitrary constructed commands. Shell printf %q escapes shell syntax, not SQL values; database clients need actual binding or narrowly validated typed values.
- Canonicalize base and target, enforce path-component containment rather than naive string prefix (base plus separator), handle nonexisting destinations and symlinks intentionally. realpath alone does not solve TOCTOU; use safe descriptor/atomic APIs for hostile concurrent paths.
- Use least-privilege permissions based on actual audience; secrets owner-only, temporary resources created restrictively before content. Do not chmod unrelated scripts globally or assume all scripts must be700.
- Keep secrets out of source/argv/history/logs, use approved stores/injected credentials or protected parsers. An environment secret still leaks if expanded into a password flag. Disable tracing around secrets.
- Validate allowed environment keys rather than exporting arbitrary config names (PATH/IFS/loader variables can change execution). File permissions/ownership are necessary evidence, not proof content is trusted.
- Create collision-safe owned temp files/directories with mktemp/umask, preserve status and clean only their actual identities. No broad rm, insecure predictable files or unverified symlink writes.
- Audit failures without confidential payload disclosure; authorization/path checks fail closed and never elevate privilege automatically.

### Execution Steps

1. Inspect script inputs/environment/config/commands, current permissions and real approved resource scope.
2. Replace unsafe dynamic dispatch with exact operation mapping and validated argument arrays.
3. Implement component-aware path restrictions, safe file creation, secret redaction and explicit mutation approvals.
4. Test hostile values, leading dashes, traversal, adjacent-prefix paths, symlinks, invalid env keys and permission/cleanup failures in disposable fixtures only.
5. Run syntax/ShellCheck/format/tests, review residual races and disclose limits rather than claiming no injection possible from lint alone.

### Validation

- Untrusted input cannot select arbitrary code/commands/paths/options; allowed data preserved correctly.
- Component containment, symlink/nonexistent-path and concurrency behavior deliberate; no naive prefix authorization.
- Secret values absent from argv/traces/logs/versioned files and config keys restricted.
- Least privilege/temp creation/cleanup confined, failures report safe context.
- Real defensive tests plus static checks pass; no live destructive payload execution or unauthorized permission/install effects.

## References

- [OWASP command injection defense](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)
- [Bash manual](https://www.gnu.org/software/bash/manual/)
- [ShellCheck](https://www.shellcheck.net/)
- `300c-bash-security-advanced.md` for privilege/network/race boundaries.
