# Bash Security Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:bash-security, kw:shell-security
**Keywords:** Bash, security, input validation, command injection, path security, secure shell scripts, sanitization, permissions, privilege escalation, secrets management
**TokenBudget:** ~3600
**ContextTier:** High
**Depends:** 300-bash-scripting-core.md

## Scope

**What This Rule Covers:**
Comprehensive bash scripting security practices covering input validation, path security, permissions, and secure coding patterns to prevent vulnerabilities and ensure safe script execution.

**When to Load This Rule:**
- Writing security-sensitive shell scripts
- Handling user input in bash scripts
- Implementing access control or authentication
- Preventing command injection vulnerabilities
- Managing secrets and credentials in shell scripts

## References

### Dependencies

**Must Load First:**
- **300-bash-scripting-core.md** - Foundation bash scripting patterns

**Related:**
- **300b-bash-testing-tooling.md** - Testing security implementations
- **300c-bash-security-advanced.md** - Advanced security: privilege, network, logging, testing

### External Documentation

- [OWASP Command Injection Prevention](https://owasp.org/www-community/attacks/Command_Injection) - Security vulnerabilities and mitigation strategies
- [CIS Security Controls](https://www.cisecurity.org/controls/) - Industry security configuration standards
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) - Comprehensive security risk management

## Contract

### Inputs and Prerequisites

- Bash script requiring security hardening
- Identified all input sources (user args, env vars, file contents) and defined trust boundaries per OWASP guidelines
- Knowledge of target system's execution environment (user privileges, network exposure, filesystem access)

### Mandatory

- Input validation for all user-provided data
- Proper variable quoting (`"$var"` not `$var`)
- Absolute paths for critical operations
- Restrictive file permissions (700 for scripts, 600 for secrets)
- Environment variable validation
- Secure credential storage (no hardcoded secrets)

### Forbidden

- Using `eval` with user input
- Hardcoding secrets in scripts
- Trusting user input without validation
- Using relative paths for security-critical operations
- Storing secrets in command-line arguments
- Executing commands constructed from user input

### Execution Steps

1. Identify all input sources (user input, environment variables, file contents)
2. Implement input validation with regex patterns for each input type
3. Sanitize file paths and names to prevent directory traversal
4. Replace any `eval` usage with safe alternatives (arrays, case statements)
5. Move secrets from script to environment variables or secure files
6. Set appropriate file permissions (700 for executables, 600 for secrets)
7. Validate environment variables (PATH, IFS, etc.) before use
8. Test with malicious inputs to verify security controls work

### Output Format

Secure bash script with:
- All inputs validated with explicit regex patterns
- Variables properly quoted throughout
- Absolute paths for critical operations
- Secure credential management (environment variables or secure files)
- Appropriate file permissions set
- No eval or command injection vulnerabilities

### Validation

**Pre-Task-Completion Checks:**
- All user input points identified and validated
- Variables quoted in all command contexts
- No hardcoded secrets present in script
- File permissions set correctly (verify with `stat`)
- No eval usage with untrusted input
- Path traversal prevention implemented

**Success Criteria:**
- `shellcheck` passes with no security warnings
- Script rejects malicious inputs (test with `'; rm -rf /'`, `../../../etc/passwd`)
- Secrets loaded from environment or secure files only
- File permissions verified: 700 for scripts, 600 for secrets
- No command injection possible through any input vector

### Design Principles

- **Defense in Depth:** Multiple layers of security controls
- **Least Privilege:** Minimum required permissions
- **Input Validation:** Never trust user data
- **Secure by Default:** Restrictive permissions, safe defaults
- **Fail Securely:** Errors MUST NOT expose sensitive information

### Post-Execution Checklist

- [ ] All user input validated with regex patterns
- [ ] Variables quoted in all contexts
- [ ] Absolute paths used for critical operations
- [ ] File permissions set correctly (700/600)
- [ ] No hardcoded secrets in script
- [ ] Environment variables validated
- [ ] No eval with user input
- [ ] Tested with malicious inputs
- [ ] shellcheck passes with no warnings

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Command Injection via Unsanitized Input

**Problem:** Passing user input directly to commands or eval without sanitization, allowing arbitrary command execution.

**Correct Pattern:**
```bash
# BAD: Direct user input in commands
filename="$1"
cat $filename  # User passes "; rm -rf /" as filename!

# BAD: eval with user input
eval "process_$user_input"  # Arbitrary code execution

# GOOD: Validate and sanitize input
filename="$1"
# Validate: only alphanumeric, dash, underscore, dot
if [[ ! "$filename" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    echo "Invalid filename" >&2
    exit 1
fi
cat -- "$filename"  # -- prevents option injection

# GOOD: Use arrays instead of eval
declare -A handlers=(["process"]="do_process" ["validate"]="do_validate")
"${handlers[$action]}"  # Safe dispatch
```

### Anti-Pattern 2: Storing Secrets in Script Files or History

**Problem:** Hardcoding passwords, API keys, or tokens directly in shell scripts, or passing them as command-line arguments (visible in process list and history).

**Correct Pattern:**
```bash
# BAD: Secrets in script
PASSWORD="super_secret_123"
mysql -u admin -p"$PASSWORD" database

# BAD: Secrets as arguments (visible in ps)
./deploy.sh --api-key="sk-12345"

# GOOD: Environment variables
mysql -u admin -p"$MYSQL_PASSWORD" database

# GOOD: Read from secure file
PASSWORD=$(cat /run/secrets/db_password)

# GOOD: Prompt securely (for interactive)
read -s -p "Password: " PASSWORD
echo  # Newline after hidden input
```

## Output Format Examples

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ALLOWED_DIR="$SCRIPT_DIR/data"

# Input validation — see Input Validation section for validate_input()
validate_input "$1" '^[a-zA-Z0-9._-]+$' "filename"

safe_path() {
    local path="$1" base="$2"
    local resolved
    resolved="$(realpath "$path" 2>/dev/null)" || return 1
    [[ "$resolved" == "$base"* ]] || { echo "Error: Path outside allowed directory" >&2; return 1; }
    echo "$resolved"
}

main() {
    [[ $# -ge 1 ]] || { echo "Usage: $0 <filename>" >&2; exit 1; }
    validate_input "$1" '^[a-zA-Z0-9._-]+$' "filename"
    local target
    target="$(safe_path "$ALLOWED_DIR/$1" "$ALLOWED_DIR")" || exit 1
    cat -- "$target"
}

main "$@"
```

## Input Validation and Sanitization

### User Input Validation
- **Critical:** Validate and sanitize all user input before processing:
```bash
validate_input() {
    local input="$1"
    local pattern="$2"
    local field_name="${3:-input}"

    if [[ ! "$input" =~ $pattern ]]; then
        echo "Error: Invalid $field_name format" >&2
        return 1
    fi
}

# Example usage patterns
validate_username() {
    validate_input "$1" '^[a-zA-Z0-9_]{3,20}$' "username"
}

validate_email() {
    validate_input "$1" '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' "email"
}

validate_filename() {
    validate_input "$1" '^[a-zA-Z0-9._-]{1,255}$' "filename"
}
```

### Input Length Limits
- **Critical:** Enforce input length limits:
```bash
check_length() {
    local input="$1" max="$2"
    [[ ${#input} -le $max ]] || { echo "Input too long" >&2; return 1; }
}
```

### Argument Validation
- **Rule:** Validate command line arguments:
```bash
validate_file() {
    [[ -f "$1" ]] || { echo "File not found: $1" >&2; return 1; }
}

validate_dir() {
    [[ -d "$1" ]] || { echo "Directory not found: $1" >&2; return 1; }
}
```

## Path Security and Traversal Prevention

### Path Validation
- **Critical:** Validate file paths to prevent directory traversal attacks:
```bash
validate_path() {
    local path="$1"
    local base_dir="$2"
    local operation="${3:-access}"

    # Resolve to absolute path
    local abs_path
    abs_path="$(realpath "$path" 2>/dev/null)" || {
        echo "Error: Cannot resolve path '$path'" >&2
        return 1
    }

    # Check if path is within allowed directory
    if [[ "$abs_path" != "$base_dir"* ]]; then
        echo "Error: Path '$path' is outside allowed directory for $operation" >&2
        return 1
    fi

    echo "$abs_path"
}

# Note: validate_path is subject to TOCTOU (time-of-check-time-of-use) race
# conditions — the path could change between validation and use. For concurrent
# environments, see 300c-bash-security-advanced.md for mitigation strategies.

# Secure file operations with path validation
secure_copy() {
    local source="$1"
    local dest="$2"
    local allowed_source_dir="$3"
    local allowed_dest_dir="$4"

    local validated_source validated_dest
    validated_source="$(validate_path "$source" "$allowed_source_dir" "read")" || return 1
    validated_dest="$(validate_path "$dest" "$allowed_dest_dir" "write")" || return 1

    cp "$validated_source" "$validated_dest"
}
```

### Filename Sanitization
- **Critical:** Sanitize filenames to prevent injection attacks:
```bash
sanitize_filename() {
    local filename="$1"
    local max_length="${2:-255}"

    # Remove path components
    filename="${filename##*/}"

    # Remove or replace dangerous characters
    filename="${filename//[^a-zA-Z0-9._-]/}"

    # Remove leading dots and dashes
    filename="${filename#"${filename%%[!.-]*}"}"

    # Ensure not empty after sanitization
    if [[ -z "$filename" ]]; then
        filename="sanitized_file_$(date +%s)"
    fi

    # Truncate if too long
    if [[ ${#filename} -gt $max_length ]]; then
        local extension="${filename##*.}"
        local basename="${filename%.*}"
        local max_base=$((max_length - ${#extension} - 1))
        filename="${basename:0:$max_base}.$extension"
    fi

    echo "$filename"
}

# Secure file creation with sanitized names
create_user_file() {
    local user_filename="$1"
    local content="$2"
    local target_dir="$3"
    local overwrite="${4:-false}"

    local safe_filename
    safe_filename="$(sanitize_filename "$user_filename")" || return 1

    local full_path="$target_dir/$safe_filename"

    # Ensure we're not overwriting system files
    if [[ -e "$full_path" && "$overwrite" != "true" ]]; then
        echo "Warning: File '$safe_filename' already exists" >&2
        return 1
    fi

    echo "$content" > "$full_path"
    chmod 644 "$full_path"
}
```

## Command Injection Prevention

### Safe Command Construction
- **Critical:** Never use `eval` with user input:
```bash
# DANGEROUS - Never do this
execute_user_command() {
    local user_cmd="$1"
    eval "$user_cmd"  # SECURITY VULNERABILITY
}

# SAFE - Use arrays and explicit commands
execute_safe_command() {
    local operation="$1"
    shift
    local -a args=("$@")

    case "$operation" in
        "list")
            ls "${args[@]}"
            ;;
        "copy")
            if [[ ${#args[@]} -eq 2 ]]; then
                cp "${args[0]}" "${args[1]}"
            else
                echo "Error: copy requires exactly 2 arguments" >&2
                return 1
            fi
            ;;
        *)
            echo "Error: Unknown operation '$operation'" >&2
            return 1
            ;;
    esac
}
```

### SQL Injection Prevention in Shell Scripts
- **Critical:** Use parameterized queries when interfacing with databases:
```bash
# Safe database operations
execute_safe_query() {
    local db_file="$1"
    local user_id="$2"

    # Validate user_id is numeric
    if [[ ! "$user_id" =~ ^[0-9]+$ ]]; then
        echo "Error: Invalid user ID format" >&2
        return 1
    fi

    # GOOD: Validated numeric input — safe for interpolation after regex check
    sqlite3 "$db_file" "SELECT * FROM users WHERE id = $user_id;"
}

# WARNING: String interpolation after regex validation is acceptable ONLY for
# strictly numeric/alphanumeric patterns. For arbitrary text, use parameterized
# queries or escape via printf '%q'. Shell scripts should prefer whitelisted commands.
```

## Secrets and Credential Management

### Environment Variable Security
- **Requirement:** Never hardcode secrets in scripts:
```bash
# WRONG - Never do this
API_KEY="sk-1234567890abcdef"  # Hardcoded secret

# CORRECT - Use environment variable validation from 300-bash-scripting-core.md
# (check_required_env pattern), then access via ${!var}
```

### Secure Credential Loading
- **Rule:** Load credentials with permission checks:
```bash
# Cross-platform file permission check
get_file_perms() {
    local file="$1"
    if [[ "$(uname -s)" == "Darwin" ]]; then
        stat -f '%A' "$file" 2>/dev/null
    else
        stat -c '%a' "$file" 2>/dev/null
    fi
}

load_credentials() {
    local file="$1"
    local perms
    perms="$(get_file_perms "$file")" || return 1

    if [[ "$perms" != "600" && "$perms" != "400" ]]; then
        echo "Error: Insecure permissions: $perms" >&2
        return 1
    fi

    # Safe credential loading -- parse key=value, don't execute
    while IFS='=' read -r key value; do
        [[ "$key" =~ ^[A-Z_][A-Z0-9_]*$ ]] || continue
        export "$key=$value"
    done < "$file"
}
```

### Temporary Credential Handling
- **Rule:** Secure temporary credential files:
```bash
create_temp_creds() {
    local file
    file="$(mktemp)"
    chmod 600 "$file"
    # printf '%q' evaluated at trap DEFINITION time (not execution time)
    # This is intentional: prevents variable injection in trap string
    trap "rm -f $(printf '%q' "$file")" EXIT
    echo "$file"
}
```

## File Permissions and Access Control

### Secure File Creation
- **Requirement:** Set appropriate permissions on created files:
```bash
create_secure_file() {
    local filename="$1"
    local content="$2"
    local permissions="${3:-644}"

    # Create file with restrictive permissions first
    (
        umask 077  # Ensure only owner can access initially
        echo "$content" > "$filename"
    )

    # Then set the desired permissions
    chmod "$permissions" "$filename"

    echo "Created '$filename' with permissions $permissions"
}

```

## Advanced Security Topics

> For process/system security (privilege management, resource limits), network security (URL validation), secure logging/audit trails, and security testing patterns, see **300c-bash-security-advanced.md**.
