# Bash Advanced Patterns and Style

> **SUB-RULE: ADVANCED PATTERNS**
>
> Advanced bash patterns covering associative arrays, performance optimization,
> code style standards, debugging, documentation, and security best practices.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Bash, advanced patterns, associative arrays, performance, code style, ShellCheck, debugging, documentation, security, parameter expansion
**TokenBudget:** ~2700
**ContextTier:** Medium
**Depends:** 300-bash-scripting-core.md
**LoadTrigger:** ext:.sh, ext:.bash

## Scope

**What This Rule Covers:**
Advanced bash scripting patterns including associative arrays, performance optimization with built-ins, code style and formatting standards, ShellCheck integration, debugging techniques, documentation conventions, and security best practices.

**When to Load This Rule:**
- Optimizing bash script performance
- Using associative arrays or advanced parameter expansion
- Setting up ShellCheck and code style standards
- Implementing debug mode and troubleshooting patterns
- Adding documentation and usage patterns to scripts
- Reviewing security practices for file permissions

## References

### Dependencies

**Must Load First:**
- **300-bash-scripting-core.md** - Foundation bash patterns (variables, functions, error handling)

**Related:**
- **300a-bash-security.md** - Comprehensive security patterns for Bash scripts
- **300b-bash-testing-tooling.md** - Testing frameworks and CI/CD tooling

## Contract

### Inputs and Prerequisites

- Bash 4.0+ available (required for associative arrays)
- shellcheck installed for static analysis
- Core bash patterns from 300-bash-scripting-core.md understood
- Scripts already have basic structure (`set -euo pipefail`, functions, traps)

### Mandatory

- **MUST** use parameter expansion over external commands for string operations
- **MUST** use `declare -A` for associative arrays (Bash 4.0+ only)
- **MUST** run shellcheck on all scripts before committing
- **MUST** include usage/help output in scripts with more than one argument
- **MUST** use `local` for all function variables (inherited from core rule)
- **MUST** set restrictive permissions on temporary and sensitive files

### Forbidden

- Using external commands (`basename`, `dirname`) when parameter expansion works
- Scripts without shellcheck validation
- Hardcoded magic numbers without named constants
- Debug output to stdout (MUST use stderr)
- Temporary files with default permissions (MUST restrict with chmod)

### Execution Steps

1. Replace all `$(basename ...)`, `$(dirname ...)`, `$(echo ... | tr)`, and `$(echo ... | cut)` calls with parameter expansion equivalents from the Performance Optimization section
2. Add associative arrays where key-value data structures are needed
3. Implement debug mode with `DEBUG` environment variable
4. Add usage/help documentation with heredoc patterns
5. Run shellcheck and resolve all warnings
6. Set appropriate file permissions for scripts and temporary files

### Output Format

```bash
#!/usr/bin/env bash
set -euo pipefail

# Debug mode
[[ "${DEBUG:-false}" == "true" ]] && set -x

# Usage documentation
show_usage() {
    cat <<'USAGE'
Usage: script.sh [options] <args>
Options:
    -h    Show this help
    -v    Verbose output
USAGE
}

# Associative array for configuration
declare -A config
config[host]="localhost"
config[port]="8080"

# Parameter expansion for string operations
filename="${path##*/}"
extension="${filename##*.}"
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

**Code Quality:**
- **CRITICAL:** shellcheck passes with zero warnings
- **CRITICAL:** No external commands used where parameter expansion suffices
- **CRITICAL:** All temporary files have restrictive permissions

**Style:**
- Consistent 4-space indentation
- Function names in snake_case, constants in UPPER_CASE
- ShellCheck directives include justification comments

### Post-Execution Checklist

- [ ] shellcheck passes with no warnings
- [ ] Parameter expansion used instead of basename/dirname where possible
- [ ] Associative arrays use `declare -A` with Bash 4.0+ check
- [ ] Debug mode available via `DEBUG=true`
- [ ] Scripts with arguments include usage/help output
- [ ] File permissions set appropriately (755 scripts, 644 configs, 600 temp files, 700 temp directories)

## Associative Arrays

### Declaration and Usage
- **Requirement:** Use `declare -A` for key-value data (Bash 4.0+ required):
```bash
declare -A config
config[host]="localhost"
config[port]="8080"
config[timeout]="30"

# Iterate over keys
for key in "${!config[@]}"; do
    echo "$key=${config[$key]}"
done

# Check if key exists
if [[ -v config[host] ]]; then
    echo "Host is set: ${config[host]}"
fi

# Get number of entries
echo "Config has ${#config[@]} entries"
```

### Bash Version Guard
- **Rule:** Always guard associative array usage with a version check:
```bash
if [[ "${BASH_VERSINFO[0]}" -lt 4 ]]; then
    echo "Error: This script requires Bash 4.0+ for associative arrays" >&2
    exit 1
fi

# Note: macOS ships Bash 3.2 by default (GPLv2 licensing constraint).
# Use `brew install bash` for Bash 5.x, then ensure shebang uses:
#   #!/usr/bin/env bash  (picks up Homebrew bash if in PATH)
# or: #!/opt/homebrew/bin/bash  (explicit path on Apple Silicon Macs)
```

## Performance Optimization

### Efficient String Operations
- **Rule:** Use bash built-ins for string operations instead of external commands:
```bash
# String manipulation with parameter expansion
filename="${path##*/}"        # basename equivalent
directory="${path%/*}"        # dirname equivalent
extension="${filename##*.}"   # file extension
basename="${filename%.*}"     # filename without extension

# Pattern matching
if [[ "$string" == pattern* ]]; then
    echo "String starts with pattern"
fi

# String replacement
new_string="${string//old/new}"    # Replace all occurrences
new_string="${string/old/new}"     # Replace first occurrence

# Edge case: empty or unset variables under set -u
# Use default-value syntax to prevent "unbound variable" errors:
safe_name="${full_name:-}"        # Empty string if unset (no error)
safe_path="${file_path:-/tmp}"    # Default to /tmp if unset
```

### Built-in Arithmetic
- **Rule:** Prefer bash built-in arithmetic over external commands:
```bash
# Use built-in arithmetic
((count++))
result=$((num1 + num2))

# Comparison
if ((count > max_retries)); then
    echo "Exceeded retry limit" >&2
    return 1
fi
```

### Avoid Unnecessary Subshells
- **Rule:** Use built-ins and parameter expansion to avoid subshell overhead:
```bash
# BAD: External commands for simple operations
dir=$(dirname "$path")
base=$(basename "$path")
upper=$(echo "$str" | tr '[:lower:]' '[:upper:]')

# GOOD: Parameter expansion (no subshell)
dir="${path%/*}"
base="${path##*/}"
upper="${str^^}"  # Bash 4.0+
```

## Code Style and Standards

### Formatting Standards
- **Rule:** Use consistent formatting:
  - 4-space indentation
  - Function names in snake_case
  - Constants in UPPER_CASE
  - Local variables in lowercase with underscores

### ShellCheck Integration
- **Requirement:** Use ShellCheck for static analysis on all scripts:
```bash
# Disable specific checks with justification
# shellcheck disable=SC2034  # Variable appears unused (used by sourced script)
readonly CONFIG_VAR="value"

# Disable for external file sourcing
# shellcheck source=/dev/null
source "$external_config"
```

**Note:** For comprehensive CI/CD integration and testing setup, see `300b-bash-testing-tooling.md`

## Debugging and Troubleshooting

### Debug Mode
- **Rule:** Implement debug mode using the `DEBUG` environment variable:
```bash
# Enable debug mode via environment variable
if [[ "${DEBUG:-false}" == "true" ]]; then
    set -x  # Print each command before execution
fi

debug_log() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo "[DEBUG] $*" >&2
    fi
}

# Usage: DEBUG=true ./script.sh
```

### Trace Functions
- **Rule:** Use `PS4` for enhanced debug output:
```bash
# Enhanced trace output with file, line, and function
export PS4='+${BASH_SOURCE[0]}:${LINENO}:${FUNCNAME[0]:+${FUNCNAME[0]}()}: '
```

## Documentation and Comments

### Script Header
- **Rule:** Include a header in all non-trivial scripts:
```bash
#!/usr/bin/env bash
# Script: deploy.sh
# Description: Deploy application to target environment
# Usage: ./deploy.sh [-v] [-e environment] <version>
# Dependencies: curl, jq, ssh
```

### Usage/Help Output
- **Rule:** Scripts with arguments MUST include help output:
```bash
show_usage() {
    cat <<'USAGE'
Usage: script.sh [options] <required_arg>

Options:
    -h          Show this help message
    -v          Enable verbose output
    -e ENV      Target environment (dev|staging|prod)

Arguments:
    required_arg    The thing to process

Examples:
    script.sh -e prod v1.2.3
    script.sh -v my_input
USAGE
}

# Parse -h flag
while getopts "hve:" opt; do
    case $opt in
        h) show_usage; exit 0 ;;
        v) verbose=true ;;
        e) environment="$OPTARG" ;;
        \?) show_usage; exit 1 ;;
    esac
done
```

## Security Best Practices

### File Permissions
- **Rule:** Set appropriate permissions on scripts and files:
```bash
# Script permissions
chmod 755 script.sh          # Executable by all, writable by owner
chmod 644 config.conf        # Readable by all, writable by owner
```

### Secure Temporary Files
- **Rule:** Use `mktemp` with restrictive permissions:
```bash
temp_file="$(mktemp)" || { echo "Failed to create temp file" >&2; exit 1; }
chmod 600 "$temp_file"   # Restrict to owner only

temp_dir="$(mktemp -d)" || { echo "Failed to create temp directory" >&2; exit 1; }
chmod 700 "$temp_dir"    # Restrict directory to owner only
```

**Note:** For comprehensive security practices including input validation, access control, and secure coding patterns, see `300a-bash-security.md`

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: External Commands for String Operations

**Problem:** Using external commands (`basename`, `dirname`, `tr`, `cut`) for operations that bash parameter expansion handles natively, adding unnecessary subshell overhead.

**Correct Pattern:**
```bash
# BAD: External commands (slow, creates subshells)
dir=$(dirname "$filepath")
base=$(basename "$filepath" .txt)
first_char=$(echo "$str" | cut -c1)

# GOOD: Parameter expansion (fast, no subshell)
dir="${filepath%/*}"
base="${filepath##*/}"; base="${base%.txt}"
first_char="${str:0:1}"
```

### Anti-Pattern 2: Debug Output to stdout

**Problem:** Writing debug or diagnostic output to stdout, which corrupts function return values and breaks pipelines that consume stdout.

**Correct Pattern:**
```bash
# BAD: Debug to stdout breaks pipelines
get_value() {
    echo "DEBUG: looking up value"  # Corrupts output
    echo "$result"
}

# GOOD: Debug to stderr, only data to stdout
get_value() {
    echo "DEBUG: looking up value" >&2  # Safe: goes to stderr
    echo "$result"  # Clean stdout for callers
}
```
