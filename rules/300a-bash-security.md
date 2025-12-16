# Bash Security Best Practices

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Bash, security, input validation, command injection, path security, secure shell scripts, sanitization, permissions, privilege escalation, secrets management
**TokenBudget:** ~2750
**ContextTier:** High
**Depends:** rules/300-bash-scripting-core.md

## Purpose
Establish comprehensive bash scripting security practices covering input validation, path security, permissions, and secure coding patterns to prevent vulnerabilities and ensure safe script execution.

## Rule Scope

Shell script security, input validation, access control

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Validate all inputs** - Never trust user data, validate patterns and types
- **Quote variables** - Prevent injection (`"$var"`, not `$var`)
- **Use absolute paths** - Avoid PATH manipulation attacks
- **Set restrictive permissions** - 700 for scripts, 600 for data
- **Sanitize file names** - Check for `../`, null bytes, special chars
- **Never eval user input** - Disable eval/source of untrusted data
- **Never trust environment** - Validate PATH, IFS, and all env vars

**Quick Checklist:**
- [ ] All inputs validated with regex
- [ ] Variables properly quoted
- [ ] Absolute paths used
- [ ] File permissions set correctly
- [ ] No eval of user input
- [ ] Secrets in secure storage
- [ ] Command injection prevented

## Contract

<contract>
<inputs_prereqs>
[Context, files, dependencies needed]
</inputs_prereqs>

<mandatory>
[Tools permitted for this domain]
</mandatory>

<forbidden>
[Tools not allowed for this domain]
</forbidden>

<steps>
[Ordered steps the agent must follow]
</steps>

<output_format>
[Expected output format]
</output_format>

<validation>
[Checks to confirm success]
</validation>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Command Injection via Unsanitized Input

**Problem:** Passing user input directly to commands or eval without sanitization, allowing arbitrary command execution.

**Why It Fails:** Attackers can inject shell metacharacters (`;`, `|`, `$()`) to execute arbitrary commands. Remote code execution vulnerabilities. Complete system compromise from simple input fields.

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

**Why It Fails:** Secrets visible in `ps aux` output. Logged in shell history files. Committed to version control. Readable by any user with file access. Cannot rotate without script changes.

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

## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

> **Investigation Required**
> When applying this rule:
> 1. **Read existing scripts BEFORE adding security** - Check current validation, permissions
> 2. **Verify input sources** - Identify all user input points, environment variables
> 3. **Never assume sanitization exists** - Check for validation functions
> 4. **Check file permissions** - Review current permissions on scripts and data
> 5. **Test injection scenarios** - Verify defenses work against actual attacks
>
> **Anti-Pattern:**
> "Adding input validation... (without checking what inputs exist)"
> "Sanitizing user input... (without testing injection scenarios)"
>
> **Correct Pattern:**
> "Let me check your script's security posture first."
> [reads script, identifies input points, checks permissions]
> "I see user input at lines X, Y. Adding validation and sanitization..."

## Output Format Examples

```bash
#!/usr/bin/env bash
# Script following bash best practices from rule

set -euo pipefail  # Exit on error, undefined vars, pipe failures
IFS=$'\n\t'      # Safe word splitting

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LOG_FILE="${SCRIPT_DIR}/output.log"

# Functions with clear contracts
main() {
    # Investigation phase
    check_prerequisites

    # Implementation phase
    perform_operations

    # Validation phase
    verify_results
}

check_prerequisites() {
    local -a required_commands=(jq curl git)

    for cmd in "${required_commands[@]}"; do
        if ! command -v "${cmd}" &>/dev/null; then
            echo "ERROR: Required command not found: ${cmd}" >&2
            exit 1
        fi
    done
}

perform_operations() {
    echo "Performing operations following project patterns..."
    # Implementation details here
}

verify_results() {
    echo "Validating results..."
    # Validation logic here
}

# Execute main function
main "$@"
```

```bash
# Validation with shellcheck
shellcheck script.sh
```

## References

### External Documentation
- [OWASP Command Injection Prevention](https://owasp.org/www-community/attacks/Command_Injection) - Security vulnerabilities and mitigation strategies
- [CIS Security Controls](https://www.cisecurity.org/controls/) - Industry security configuration standards
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework) - Comprehensive security risk management

### Related Rules
- **Bash Core**: `rules/300-bash-scripting-core.md`
- **Bash Testing**: `rules/300b-bash-testing-tooling.md`

## 1. Input Validation and Sanitization

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

## 2. Path Security and Traversal Prevention

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

    local safe_filename
    safe_filename="$(sanitize_filename "$user_filename")" || return 1

    local full_path="$target_dir/$safe_filename"

    # Ensure we're not overwriting system files
    if [[ -e "$full_path" ]]; then
        echo "Warning: File '$safe_filename' already exists" >&2
        read -r -p "Overwrite? (y/N): " confirm
        if [[ "$confirm" != [yY] ]]; then
            return 1
        fi
    fi

    echo "$content" > "$full_path"
    chmod 644 "$full_path"
}
```

## 3. Command Injection Prevention

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

### Parameter Expansion Safety
- **Rule:** Use parameter expansion safely with user input:
```bash
# Safe parameter handling
process_user_data() {
    local user_input="$1"
    local operation="$2"

    # Validate operation is from allowed set
    case "$operation" in
        "uppercase"|"lowercase"|"length")
            # Safe operations
            ;;
        *)
            echo "Error: Invalid operation '$operation'" >&2
            return 1
            ;;
    esac

    case "$operation" in
        "uppercase")
            echo "${user_input^^}"
            ;;
        "lowercase")
            echo "${user_input,,}"
            ;;
        "length")
            echo "${#user_input}"
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

    # Use sqlite3 with parameters (if available) or careful escaping
    sqlite3 "$db_file" "SELECT * FROM users WHERE id = $user_id;"
}

# For systems without parameterized queries, careful validation
escape_sql_string() {
    local input="$1"
    # Replace single quotes with two single quotes
    echo "${input//\'/\'\'}"
}
```

## 4. Secrets and Credential Management

### Environment Variable Security
- **Requirement:** Never hardcode secrets in scripts:
```bash
# WRONG - Never do this
API_KEY="sk-1234567890abcdef"  # Hardcoded secret

# CORRECT - Use environment variables
check_required_secrets() {
    local -a required_vars=("$@")
    local -a missing_vars=()

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        echo "Error: Missing required environment variables: ${missing_vars[*]}" >&2
        echo "Please set these variables before running the script" >&2
        exit 1
    fi
}

# Usage
check_required_secrets "DATABASE_URL" "API_KEY" "JWT_SECRET"
```

### Secure Credential Loading
- **Rule:** Load credentials with permission checks:
```bash
load_credentials() {
    local file="$1"
    local perms
    perms="$(stat -c '%a' "$file" 2>/dev/null)" || return 1

    if [[ "$perms" != "600" && "$perms" != "400" ]]; then
        echo "Error: Insecure permissions: $perms" >&2
        return 1
    fi

    # shellcheck source=/dev/null
    source "$file"
}
```

### Temporary Credential Handling
- **Rule:** Secure temporary credential files:
```bash
create_temp_creds() {
    local file
    file="$(mktemp)"
    chmod 600 "$file"
    trap "rm -f '$file'" EXIT
    echo "$file"
}
```

## 5. File Permissions and Access Control

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

# Predefined permission sets
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
- **Rule:** Check file permissions:
```bash
check_perms() {
    local file="$1" expected="$2"
    local actual
    actual="$(stat -c '%a' "$file" 2>/dev/null)" || return 1
    [[ "$actual" == "$expected" ]] || {
        echo "Wrong permissions: $actual, expected $expected" >&2
        return 1
    }
}
```

## 6. Process and System Security

### Privilege Management
- **Rule:** Run with minimum required privileges:
```bash
check_running_as_root() {
    if [[ $EUID -eq 0 ]]; then
        echo "Warning: Running as root. Consider using a non-privileged user." >&2
        read -r -p "Continue as root? (y/N): " confirm
        if [[ "$confirm" != [yY] ]]; then
            exit 1
        fi
    fi
}

# Drop privileges when possible
drop_privileges() {
    local target_user="$1"

    if [[ $EUID -eq 0 ]]; then
        echo "Dropping privileges to user: $target_user"
        exec sudo -u "$target_user" "$0" "$@"
    fi
}
```

### Resource Limits
- **Rule:** Set basic resource limits:
```bash
set_limits() {
    ulimit -t 300    # CPU time
    ulimit -v 1048576 # Memory (1GB)
    ulimit -n 1024   # Open files
    ulimit -c 0      # Core dumps
}
```

## 7. Network Security

### URL Validation
- **Rule:** Validate URLs before requests:
```bash
validate_url() {
    local url="$1"
    [[ "$url" =~ ^https?:// ]] || { echo "Invalid URL" >&2; return 1; }
    [[ ! "$url" =~ localhost|127\.0\.0\.1 ]] || { echo "Localhost blocked" >&2; return 1; }
}
```

## 8. Secure Logging

### Basic Audit Logging
- **Rule:** Log security events:
```bash
audit_log() {
    local event="$1" details="$2"
    local msg="[$(date)] EVENT=$event USER=${USER:-unknown} DETAILS=$details"
    echo "$msg" >> "${LOG_FILE:-/var/log/audit.log}"
}
```

## 9. Security Testing and Validation

### Security Testing
- **Consider:** Test with malicious inputs:
```bash
test_security() {
    local func="$1"
    local -a bad_inputs=("" "$(printf 'A%.0s' {1..100})" "'; rm -rf /")
    for input in "${bad_inputs[@]}"; do
        "$func" "$input" 2>/dev/null || echo "Rejected: $input"
    done
}
```
