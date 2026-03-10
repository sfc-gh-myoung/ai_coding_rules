# Bash Security Advanced Patterns

> **SUB-RULE: ADVANCED SECURITY**
>
> Advanced security patterns for privilege management, network security,
> audit logging, parameter expansion safety, and security testing.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Bash, security, privilege management, network security, audit logging, resource limits, URL validation, security testing, parameter expansion, file permissions
**TokenBudget:** ~2200
**ContextTier:** Medium
**Depends:** 300a-bash-security.md
**LoadTrigger:** kw:bash-security-advanced, kw:privilege-management, kw:audit-logging

## Scope

**What This Rule Covers:**
Advanced bash security patterns covering privilege management, resource limits, network security, secure logging, parameter expansion safety, permission validation, and security testing methodologies.

**When to Load This Rule:**
- Implementing privilege escalation/de-escalation in scripts
- Validating URLs and network inputs
- Setting up audit logging for security events
- Restricting system resource usage in scripts
- Testing scripts against malicious inputs

## References

### Dependencies

**Must Load First:**
- **300a-bash-security.md** - Core security patterns (input validation, command injection, credentials)

**Related:**
- **300-bash-scripting-core.md** - Foundation bash scripting patterns
- **300b-bash-testing-tooling.md** - Testing frameworks and CI/CD tooling

## Contract

### Inputs and Prerequisites

- Core security patterns from 300a-bash-security.md understood
- Scripts already have basic security (input validation, quoted variables, no eval)
- Understand EUID values (0=root), sudo delegation, and file ownership (`stat -c '%U' file`)
- Knowledge of target system's network exposure (listening ports, firewall rules, inbound access)

### Mandatory

- **MUST** check and drop root privileges when elevated access is not needed
- **MUST** set resource limits for scripts running untrusted workloads
- **MUST** validate URLs before making network requests
- **MUST** log security-relevant events with timestamps and user context
- **MUST** test all input validation with known malicious payloads
- **MUST** use parameterized permission sets for file creation helpers

### Forbidden

- Running scripts as root without explicit justification
- Making network requests to unvalidated URLs
- Security logging to world-writable files
- Skipping security testing for input validation functions
- Using parameter expansion on untrusted input without operation whitelisting

### Execution Steps

1. Audit script for privilege requirements and implement least-privilege patterns
2. Set resource limits (CPU, memory, open files) for scripts processing external data
3. Validate all URLs and network endpoints before requests
4. Implement audit logging for security events
5. Create permission helper functions for consistent file creation
6. Test all security controls with malicious inputs

### Output Format

Scripts with advanced security controls:
- Privilege checks and de-escalation at entry points
- Resource limits set before processing untrusted data
- URL validation before network requests
- Audit log entries for security events
- Consistent file permission helpers

### Validation

**Pre-Task-Completion Checks:**
- **CRITICAL:** Scripts drop privileges when root is not required
- **CRITICAL:** Resource limits set for untrusted workloads
- **CRITICAL:** All URLs validated before network requests
- Audit logging covers authentication, authorization, and data access events

### Post-Execution Checklist

- [ ] Privilege checks implemented (root detection, privilege dropping)
- [ ] Resource limits set (CPU, memory, open files)
- [ ] URL validation rejects localhost and non-HTTPS
- [ ] Audit logging captures security events with context
- [ ] Security testing covers known attack payloads
- [ ] File permission helpers use umask + explicit chmod

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Running Everything as Root

**Problem:** Scripts that require root for one operation run entirely as root, expanding the attack surface for the entire script execution.

**Correct Pattern:**
```bash
# BAD: Entire script runs as root
sudo ./deploy.sh  # All operations elevated

# GOOD: Elevate only for specific operations
deploy() {
    # Non-privileged operations
    validate_config "$config_file"
    build_artifacts

    # Elevate only when needed
    sudo cp artifacts/* /usr/local/bin/
    sudo systemctl restart myservice

    # Back to non-privileged
    verify_deployment
}
```

### Anti-Pattern 2: Security Logging Without Context

**Problem:** Logging security events without timestamps, user context, or event classification, making incident investigation impossible.

**Correct Pattern:**
```bash
# BAD: No context in security logs
echo "Login failed" >> /var/log/app.log

# GOOD: Structured security logging with context
# GOOD: Use audit_log() — see Secure Logging section for implementation
audit_log "AUTH_FAILURE" "source_ip=$remote_ip username=$attempted_user"
```

## Process and System Security

### Privilege Management
- **Rule:** Run with minimum required privileges:
```bash
check_running_as_root() {
    if [[ $EUID -eq 0 ]]; then
        echo "Warning: Running as root. Consider using a non-privileged user." >&2
        return 1
    fi
}

# Drop privileges when possible
drop_privileges() {
    local target_user="$1"; shift

    if [[ $EUID -eq 0 ]]; then
        echo "Dropping privileges to user: $target_user"
        exec sudo -u "$target_user" "$0" "$@"
    fi
}
```

### Resource Limits
- **Rule:** Set resource limits for scripts processing external data:
```bash
set_limits() {
    ulimit -t 300      # CPU seconds (SIGXCPU on exceed, then SIGKILL)
    ulimit -v 1048576  # 1GB memory (allocation fails, script exits)
    ulimit -n 1024     # Open files (EMFILE error on open/socket)
    ulimit -c 0        # No core dumps (security: prevents credential leaks)

    # Trap SIGXCPU for graceful shutdown when CPU limit approached
    trap 'echo "CPU limit reached — shutting down" >&2; exit 152' XCPU
}
```

## Parameter Expansion Safety

### Safe Operations on User Input
- **Rule:** Whitelist allowed operations when using parameter expansion with user input:
```bash
process_user_data() {
    local user_input="$1"
    local operation="$2"

    # Validate operation is from allowed set
    case "$operation" in
        "uppercase"|"lowercase"|"length")
            ;;
        *)
            echo "Error: Invalid operation '$operation'" >&2
            return 1
            ;;
    esac

    case "$operation" in
        "uppercase")  echo "${user_input^^}" ;;
        "lowercase")  echo "${user_input,,}" ;;
        "length")     echo "${#user_input}" ;;
    esac
}
```

## Network Security

### URL Validation
- **Rule:** Validate URLs before making requests:
```bash
validate_url() {
    local url="$1"
    [[ "$url" =~ ^https?:// ]] || { echo "Invalid URL scheme" >&2; return 1; }
    # Block localhost (IPv4, IPv6, hostname) and cloud metadata endpoints
    [[ ! "$url" =~ (localhost|\[::1\]|127\.|0\.0\.0\.0|169\.254\.) ]] || {
        echo "Blocked: internal/metadata URL" >&2; return 1
    }
}
```

## Secure Logging

### Audit Logging
- **Rule:** Log security events with full context:
```bash
audit_log() {
    local event="$1" details="$2"
    local msg="[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] EVENT=$event USER=${USER:-unknown} PID=$$ DETAILS=$details"
    echo "$msg" >> "${LOG_FILE:-/var/log/audit.log}"
}
```

## Permission Helpers

### Predefined Permission Sets
- **Rule:** Use consistent permission helpers for file creation:
```bash
# Requires create_secure_file from 300a-bash-security.md
create_executable_script() {
    local script_name="$1"
    local script_content="$2"
    create_secure_file "$script_name" "$script_content" "755"
}

create_config_file() {
    local config_name="$1"
    local config_content="$2"
    create_secure_file "$config_name" "$config_content" "644"
}

create_secret_file() {
    local secret_name="$1"
    local secret_content="$2"
    create_secure_file "$secret_name" "$secret_content" "600"
}
```

### Permission Validation
- **Rule:** Verify file permissions match expectations:
```bash
check_perms() {
    local file="$1" expected="$2"
    local actual
    actual="$(get_file_perms "$file")" || return 1
    [[ "$actual" == "$expected" ]] || {
        echo "Wrong permissions on $file: $actual (expected $expected)" >&2
        return 1
    }
}
```

## Security Testing and Validation

### Testing with Malicious Inputs
- **Critical:** Test all input validation functions against known attack payloads:
```bash
test_security() {
    local func="$1"
    local -a bad_inputs=(
        ""
        "$(printf 'A%.0s' {1..1000})"
        "'; rm -rf /"
        "../../../etc/passwd"
        "; cat /etc/shadow"
        '$(whoami)'
        '`id`'
    )
    local failed=0
    for input in "${bad_inputs[@]}"; do
        if "$func" "$input" 2>/dev/null; then
            echo "FAIL: Accepted malicious input: $input" >&2
            ((failed++))
        fi
    done
    [[ $failed -eq 0 ]] && echo "All security tests passed" || echo "$failed security test(s) failed" >&2
    return $failed
}
```
