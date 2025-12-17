# Bash Scripting Core Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential Bash patterns. Load for shell scripting tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Bash, shell scripting, set -euo pipefail, error handling, strict mode, functions, variables, script structure, trap, exit codes, shellcheck, input validation
**TokenBudget:** ~3100
**ContextTier:** High
**Depends:** rules/000-global-core.md

## Purpose
Establish foundational bash scripting patterns covering script structure, variables, functions, and essential error handling practices to create reliable, maintainable, and portable shell scripts.

## Rule Scope

Foundation bash scripting patterns and essential practices

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use `set -euo pipefail`** - Strict error handling in all scripts
- **Quote all variables** - Prevent word splitting (`"$var"`, not `$var`)
- **Use `local` in functions** - Prevent variable pollution
- **Trap signals properly** - Clean up resources on exit/error
- **Validate inputs** - Check arguments and exit codes
- **Use shellcheck** - Static analysis catches common errors
- **Never ignore exit codes** - Check `$?` or use `if command; then`

**Quick Checklist:**
- [ ] `#!/usr/bin/env bash` shebang
- [ ] `set -euo pipefail` at top
- [ ] All variables quoted
- [ ] Functions use `local` variables
- [ ] Trap handlers for cleanup
- [ ] Input validation implemented
- [ ] Shellcheck passing

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

<design_principles>
- Use `#!/usr/bin/env bash` shebang and `set -euo pipefail` for strict error handling
- Include script metadata, help functions, and proper signal trapping
- Quote variables, validate inputs, and use local variables in functions
- Implement comprehensive error handling with meaningful exit codes
- Follow consistent style with proper documentation and modular design
</design_principles>

</contract>

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Unquoted Variables Leading to Word Splitting

**Problem:** Using `$variable` instead of `"$variable"`, causing word splitting and glob expansion on whitespace or special characters.

**Why It Fails:** Filenames with spaces break scripts. Glob patterns in variables expand unexpectedly. Security vulnerabilities from injection. Scripts work in testing but fail on real data.

**Correct Pattern:**
```bash
# BAD: Unquoted variables
file=$1
rm $file  # "my file.txt" becomes rm my file.txt (deletes wrong files!)
cp $source $dest  # Glob expansion if source contains *

# GOOD: Always quote variables
file="$1"
rm "$file"  # Correctly handles "my file.txt"
cp "$source" "$dest"  # No unexpected expansion

# Use shellcheck to catch these: shellcheck script.sh
```

### Anti-Pattern 2: Missing Error Handling with set -e

**Problem:** Scripts that continue executing after command failures, potentially corrupting data or leaving systems in inconsistent states.

**Why It Fails:** Failed commands go unnoticed. Subsequent commands operate on missing or corrupt data. Partial deployments. Silent data loss. Debugging requires tracing through entire execution.

**Correct Pattern:**
```bash
# BAD: No error handling
#!/bin/bash
cd /deploy/dir
rm -rf old_version
mv new_version current  # If cd failed, deletes wrong directory!

# GOOD: Strict error handling
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

cd /deploy/dir || exit 1
rm -rf old_version
mv new_version current

# Or explicit error handling
if ! cd /deploy/dir; then
    echo "ERROR: Cannot access deploy directory" >&2
    exit 1
fi
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
> 1. **Read existing scripts BEFORE suggesting changes** - Check current patterns, error handling
> 2. **Verify shell type** - Confirm bash vs sh, check shebang and features used
> 3. **Never assume error handling exists** - Check for `set -euo pipefail`, trap handlers
> 4. **Check for shellcheck compliance** - Run shellcheck to identify existing issues
> 5. **Test with actual inputs** - Verify scripts work with edge cases
>
> **Anti-Pattern:**
> "Adding set -euo pipefail... (without checking if script is compatible)"
> "Quoting variables... (without testing for unintended changes)"
>
> **Correct Pattern:**
> "Let me check your script's current error handling first."
> [reads script, checks for existing patterns, runs shellcheck]
> "I see you're missing error handling. Adding set -euo pipefail and trap handlers..."

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
- [Bash Manual](https://www.gnu.org/software/bash/manual/) - Complete reference for Bash features and syntax
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) - Professional shell scripting standards and conventions
- [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls) - Common scripting mistakes and how to avoid them

### Related Rules
- **Bash Security**: `rules/300a-bash-security.md`
- **Bash Testing**: `rules/300b-bash-testing-tooling.md`
- **Taskfile Automation**: `rules/820-taskfile-automation.md`

## 1. Script Foundation & Safety

### Shebang and Interpreter
- **Requirement:** Always start scripts with proper shebang: `#!/bin/bash` or `#!/usr/bin/env bash`
- **Rule:** Use `#!/usr/bin/env bash` for portability across systems
- **Avoid:** Generic `#!/bin/sh` unless specifically targeting POSIX compliance
- **Always:** Specify bash when using bash-specific features

### Strict Mode Configuration
- **Requirement:** Enable strict error handling at script start:
```bash
#!/usr/bin/env bash
set -euo pipefail
```
- **Critical:** `set -e` - Exit immediately on command failure
- **Critical:** `set -u` - Treat unset variables as errors
- **Critical:** `set -o pipefail` - Return exit status of failed command in pipeline
- **Consider:** Add `set -x` for debugging (remove in production)

### Script Metadata and Documentation
- **Requirement:** Include header documentation:
```bash
#!/usr/bin/env bash
# Script: script_name.sh
# Description: Brief description of script purpose
# Author: Your Name
# Version: 1.0
# Last Updated: YYYY-MM-DD
# Usage: ./script_name.sh [options] [arguments]

set -euo pipefail
```

## 2. Variable Management

### Variable Declaration and Naming
- **Requirement:** Use descriptive, lowercase variable names with underscores
- **Rule:** Constants in UPPERCASE: `readonly MAX_RETRIES=3`
- **Always:** Declare readonly variables when values won't change
- **Avoid:** Single-letter variables except for standard loop counters

```bash
# Good practices
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CONFIG_FILE="/etc/myapp/config.conf"
local user_input=""
local file_count=0

# Avoid
x=10
FILE=/tmp/file
```

### Variable Quoting and Expansion
- **Critical:** Always quote variables to prevent word splitting and globbing:
```bash
# Correct
rm "$file_name"
cp "$source_dir"/* "$dest_dir/"
echo "Processing file: $file_name"

# Dangerous - can break with spaces or special characters
rm $file_name
cp $source_dir/* $dest_dir/
```

- **Rule:** Use `"${variable}"` syntax for clarity in complex expressions
- **Always:** Quote command substitutions: `"$(command)"`
- **Critical:** Use arrays for lists instead of space-separated strings

### Array Handling
- **Requirement:** Use arrays for multiple values:
```bash
# Declare arrays
declare -a files=("file1.txt" "file2.txt" "file with spaces.txt")
readonly -a VALID_ENVIRONMENTS=("dev" "staging" "prod")

# Access arrays safely
for file in "${files[@]}"; do
    echo "Processing: $file"
done

# Check array length
if [[ ${#files[@]} -eq 0 ]]; then
    echo "No files to process"
fi
```

## 3. Basic Input Handling

### Command Line Arguments
- **Rule:** Validate command line arguments:
```bash
validate_args() {
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <required_arg> [optional_arg]" >&2
        exit 1
    fi
}

# Basic argument processing
main() {
    validate_args "$@"

    local required_arg="$1"
    local optional_arg="${2:-default_value}"

    # Process arguments
    echo "Processing: $required_arg"
}
```

### Environment Variables
- **Rule:** Check required environment variables:
```bash
check_required_env() {
    local -a missing_vars=()

    for var in "$@"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        echo "Error: Missing environment variables: ${missing_vars[*]}" >&2
        exit 1
    fi
}

# Usage
check_required_env "HOME" "USER"
```

**Note:** For comprehensive input validation and security practices, see `300a-bash-security.md`

## 4. Error Handling and Logging

### Function Error Handling
- **Rule:** Check conditions in functions:
```bash
process_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo "Error: File not found: $file" >&2
        return 1
    fi

    cp "$file" "$backup_dir/"
}
```

### Cleanup and Signal Handling
- **Rule:** Implement cleanup for temporary resources:
```bash
cleanup() {
    [[ -n "${temp_dir:-}" ]] && rm -rf "$temp_dir"
}

trap cleanup EXIT
temp_dir="$(mktemp -d)"
```

### Basic Logging
- **Rule:** Simple logging with timestamps:
```bash
log() {
    echo "[$(date '+%H:%M:%S')] $*" >&2
}

# Usage
log "Starting process"
log "Process completed"
```

## 5. Function Design and Modularity

### Function Structure
- **Requirement:** Use functions for reusable code blocks:
```bash
function_name() {
    local param1="$1"
    local param2="${2:-default_value}"

    # Validate parameters
    if [[ $# -lt 1 ]]; then
        echo "Usage: function_name <param1> [param2]" >&2
        return 1
    fi

    # Function logic here
    echo "Result: $param1"
}
```

### Parameter Handling
- **Rule:** Use local variables for function parameters
- **Consider:** Use `getopts` for option parsing:
```bash
process_options() {
    local verbose=false

    while getopts "v" opt; do
        case $opt in
            v) verbose=true ;;
            \?) return 1 ;;
        esac
    done

    shift $((OPTIND-1))
    echo "Processing: $*"
}
```

### Return Values and Exit Codes
- **Rule:** Use meaningful exit codes:
```bash
# Standard exit codes
readonly EXIT_SUCCESS=0
readonly EXIT_ERROR=1

check_file() {
    if [[ ! -r "$1" ]]; then
        echo "Cannot read file: $1" >&2
        return $EXIT_ERROR
    fi
}
```

## 6. File and Directory Operations

### Safe File Operations
- **Rule:** Check file existence before operations:
```bash
safe_copy() {
    local source="$1" dest="$2"

    if [[ ! -f "$source" ]]; then
        echo "Error: Source file not found: $source" >&2
        return 1
    fi

    cp "$source" "$dest"
}
```

### Directory Operations
- **Rule:** Use `find` for file processing:
```bash
# Process files safely
find "$directory" -name "*.txt" -type f -print0 | \
    while IFS= read -r -d '' file; do
        process_file "$file"
    done
```

### Temporary Files
- **Rule:** Use `mktemp` for temporary files:
```bash
temp_file="$(mktemp)"
temp_dir="$(mktemp -d)"
trap 'rm -f "$temp_file"; rm -rf "$temp_dir"' EXIT
```

## 7. Command Execution and Pipelines

### Command Substitution
- **Rule:** Use `$()` instead of backticks for command substitution:
```bash
# Preferred
current_date="$(date '+%Y-%m-%d')"
file_count="$(find "$dir" -type f | wc -l)"

# Avoid
current_date=`date '+%Y-%m-%d'`
```

### Pipeline Safety
- **Rule:** Handle pipeline failures:
```bash
# Check pipeline success
if ! command1 | command2; then
    echo "Pipeline failed" >&2
    exit 1
fi
```

### Process Management
- **Rule:** Handle background processes:
```bash
# Start background task
long_running_command &
local pid=$!

# Wait for completion
wait "$pid"
```

## 8. Configuration and Environment

### Basic Configuration
- **Rule:** Handle simple configuration files:
```bash
load_simple_config() {
    local config_file="$1"

    if [[ -f "$config_file" ]]; then
        # shellcheck source=/dev/null
        source "$config_file"
    else
        echo "Warning: Config file not found: $config_file" >&2
    fi
}
```

### Environment Detection
- **Rule:** Basic OS detection:
```bash
detect_os() {
    case "$(uname -s)" in
        Linux*)  echo "linux" ;;
        Darwin*) echo "macos" ;;
        *)       echo "unknown" ;;
    esac
}

readonly OS="$(detect_os)"
```

## 9. Basic Debugging

### Debug Mode
- **Rule:** Simple debug mode implementation:
```bash
# Enable debug mode via environment variable
if [[ "${DEBUG:-false}" == "true" ]]; then
    set -x
fi

debug_log() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo "[DEBUG] $*" >&2
    fi
}
```

**Note:** For comprehensive testing frameworks and debugging techniques, see `300b-bash-testing-tooling.md`

## 10. Performance Best Practices

### Efficient String Operations
- **Rule:** Use bash built-ins for string operations:
```bash
# String manipulation with parameter expansion
filename="${path##*/}"        # basename
directory="${path%/*}"        # dirname
extension="${filename##*.}"   # file extension
basename="${filename%.*}"     # filename without extension

# Pattern matching
if [[ "$string" == pattern* ]]; then
    echo "String starts with pattern"
fi
```

### Built-in Preferences
- **Rule:** Prefer bash built-ins:
```bash
# Use built-in arithmetic
((count++))
result=$((num1 + num2))
```

## 11. Code Style and Standards

### Formatting Standards
- **Rule:** Use consistent formatting:
  - 4-space indentation
  - Function names in snake_case
  - Constants in UPPER_CASE
  - Local variables in lowercase with underscores

### ShellCheck Basics
- **Requirement:** Use ShellCheck for static analysis
- **Rule:** Include basic ShellCheck directives:
```bash
# Disable specific checks with justification
# shellcheck disable=SC2034  # Variable appears unused
readonly CONFIG_VAR="value"  # Used by sourced script

# Disable for external file sourcing
# shellcheck source=/dev/null
source "$external_config"
```

**Note:** For comprehensive tooling integration and CI/CD setup, see `300b-bash-testing-tooling.md`

## 12. Basic Security Practices

### File Permissions
- **Rule:** Set appropriate basic permissions:
```bash
# Script permissions
chmod 755 script.sh          # Executable by all, writable by owner
chmod 644 config.conf        # Readable by all, writable by owner
```

### Secure Temporary Files
- **Rule:** Use mktemp for temporary files:
```bash
# Create temporary file
temp_file="$(mktemp)"
chmod 600 "$temp_file"

# Create temporary directory
temp_dir="$(mktemp -d)"
chmod 700 "$temp_dir"
```

**Note:** For comprehensive security practices including input validation and access control, see `300a-bash-security.md`

## 13. Common Anti-Patterns to Avoid

### Dangerous Practices
- **Avoid:** Using `eval` with untrusted input
- **Avoid:** Parsing `ls` output (use arrays or `find` instead)
- **Avoid:** Using `cat` unnecessarily (`< file` is more efficient)
- **Avoid:** Ignoring command failures without explicit handling
- **Avoid:** Using `which` (use `command -v` instead)

### Performance Anti-Patterns
- **Avoid:** Calling external commands in loops when bash built-ins suffice
- **Avoid:** Using `expr` for arithmetic (use `$(())` instead)
- **Avoid:** Unnecessary subshells and command substitutions

## 14. Documentation Standards

### Usage Documentation
- **Requirement:** Provide clear usage information:
```bash
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] <command> [arguments]

Commands:
    process <file>    Process the specified file
    validate <input>  Validate input format

Options:
    -v, --verbose     Enable verbose output
    -h, --help        Show this help message

Examples:
    $0 process data.txt
    $0 --verbose validate input.json

EOF
}
```

### Code Comments
- **Rule:** Document complex logic:
```bash
# Calculate file hash for integrity checking
calculate_hash() {
    local file="$1"
    # Use SHA-256 for security
    sha256sum "$file" | cut -d' ' -f1
}
```

## Related Rules

- **`300a-bash-security.md`** - Comprehensive security practices, input validation, and access control
- **`300b-bash-testing-tooling.md`** - Testing frameworks, debugging, ShellCheck integration, and CI/CD
