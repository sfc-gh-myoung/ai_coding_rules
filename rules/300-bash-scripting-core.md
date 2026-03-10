# Bash Scripting Core Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Bash patterns. Load for shell scripting tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**Keywords:** Bash, shell scripting, set -euo pipefail, error handling, strict mode, functions, variables, script structure, trap, exit codes, shellcheck, input validation
**TokenBudget:** ~3500
**ContextTier:** High
**Depends:** 000-global-core.md
**LoadTrigger:** ext:.sh, ext:.bash, ext:.zsh

## Scope

**What This Rule Covers:**
Foundational bash scripting patterns covering script structure, variables, functions, and essential error handling practices to create reliable, maintainable, and portable shell scripts.

**When to Load This Rule:**
- Writing or modifying Bash scripts
- Implementing error handling in shell scripts
- Creating script structure and organization patterns
- Setting up signal trapping and cleanup handlers
- Validating script inputs and exit codes
- Debugging Bash scripts with shellcheck
- Establishing Bash coding standards for projects

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates

**Related:**
- **300a-bash-security.md** - Security patterns for Bash scripts
- **300b-bash-testing-tooling.md** - Testing and tooling for Bash
- **300d-bash-advanced.md** - Advanced patterns, performance, code style, debugging
- **820-taskfile-automation.md** - Task automation with Taskfiles

### External Documentation

**Official Documentation:**
- [Bash Manual](https://www.gnu.org/software/bash/manual/) - Complete Bash reference
- [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls) - Common mistakes and solutions

**Best Practices Guides:**
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) - Professional shell scripting standards
- [ShellCheck](https://www.shellcheck.net/) - Static analysis tool for shell scripts

## Contract

### Inputs and Prerequisites

- Bash 4.0+ available (check with `bash --version`)
- shellcheck 0.8+ installed for static analysis (install: https://github.com/koalaman/shellcheck#installing)
- Existing scripts or new script requirements identified
- Target platform compatibility requirements (Linux, macOS, etc.)

### Mandatory

- **Use `set -euo pipefail`** - Strict error handling in all scripts
- **Quote all variables** - Prevent word splitting (`"$var"`, not `$var`)
- **Use `local` in functions** - Prevent variable pollution
- **Trap signals properly** - Clean up resources on exit/error
- **Validate inputs** - Check arguments and exit codes
- **Use shellcheck** - Static analysis to catch common errors
- **`#!/usr/bin/env bash` shebang** - Portable script execution

### Forbidden

- Unquoted variables (use `"$var"` not `$var`)
- Ignoring exit codes or continuing after errors
- Global variables in functions (use `local`)
- Missing error handling (`set -euo pipefail` required)
- Scripts without cleanup handlers (trap)
- Shell expansions or glob patterns not verified with `shellcheck`

### Execution Steps

1. Start with `#!/usr/bin/env bash` shebang and `set -euo pipefail`
2. Include script metadata, help functions, and proper signal trapping
3. Quote all variables and validate inputs
4. Use local variables in functions to prevent pollution
5. Implement error handling with meaningful exit codes (see Return Values and Exit Codes section)
6. Run shellcheck for static analysis
7. Test scripts with edge cases (spaces in filenames, empty inputs)

### Output Format

```bash
#!/usr/bin/env bash
# Script: example.sh
# Description: Example bash script following best practices
# Usage: ./example.sh [options] <args>

set -euo pipefail  # Exit on error, undefined vars, pipe failures
IFS=$'\n\t'        # Safe word splitting

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Cleanup handler
cleanup() {
    local exit_code=$?
    # Cleanup actions here
    exit "${exit_code}"
}
trap cleanup EXIT INT TERM

# Function with local variables
process_file() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "ERROR: File not found: $file" >&2
        return 1
    fi
    
    # Process file...
}

# Main function
main() {
    if [[ $# -lt 1 ]]; then
        echo "Usage: $SCRIPT_NAME <file>" >&2
        exit 1
    fi
    
    process_file "$1"
}

main "$@"
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**Code Quality:**
- **CRITICAL:** `shellcheck script.sh` passes with no errors
- **CRITICAL:** All variables quoted (`"$var"`)
- **CRITICAL:** `set -euo pipefail` present at top of script
- **CRITICAL:** Functions use `local` for all variables
- **Format Check:** Shebang is `#!/usr/bin/env bash`
- **Format Check:** Trap handler for cleanup present

**Error Handling:**
- **CRITICAL:** Exit codes checked for all critical commands
- **CRITICAL:** Error messages go to stderr (`>&2`)
- **CRITICAL:** Meaningful exit codes used (0=success, 1=error, etc.)

**Input Validation:**
- **Argument Count:** Script checks `$#` and provides usage
- **File Existence:** Scripts validate files exist before use
- **Command Availability:** Required commands checked with `command -v`

**Success Criteria:**
- shellcheck passes, spaces in filenames handled, errors exit non-zero, cleanup handler runs

### Post-Execution Checklist

- [ ] Rule dependencies loaded (000-global-core.md)
- [ ] **CRITICAL:** `shellcheck script.sh` passes with no errors
- [ ] **CRITICAL:** All variables quoted, `set -euo pipefail` at top
- [ ] **CRITICAL:** Functions use `local` variables
- [ ] Shebang is `#!/usr/bin/env bash`, trap handler present
- [ ] Input validation, meaningful exit codes, errors to stderr
- [ ] Script tested with edge cases (spaces, empty inputs)
- [ ] CHANGELOG.md and README.md updated as required

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Unquoted Variables Leading to Word Splitting

**Problem:** Using variables without quotes (`$var` instead of `"$var"`), causing unexpected word splitting and glob expansion when values contain spaces or special characters.

**Correct Pattern:**
```bash
# BAD: Unquoted variables cause word splitting
file_path="/path/to/my documents/file.txt"
cat $file_path  # Fails: cat tries to open 3 files: /path/to/my, documents/file.txt

files="*.txt"
rm $files  # Dangerous: glob expands, might delete unintended files

# GOOD: Always quote variables
file_path="/path/to/my documents/file.txt"
cat "$file_path"  # Works: treated as single argument

files="*.txt"
rm "$files"  # Safe: treats *.txt as literal string, not glob
```

### Anti-Pattern 2: Missing Error Handling and Strict Mode

**Problem:** Running scripts without `set -euo pipefail`, allowing commands to fail silently and scripts to continue with undefined variables or failed pipeline commands.

**Correct Pattern:**
```bash
# BAD: No error handling, continues after failures
#!/bin/bash
mkdir /tmp/data
cp important.txt /tmp/data/  # Fails silently if file doesn't exist
process_data /tmp/data/important.txt  # Processes wrong/missing file
echo "Success!"  # Prints even though cp failed

# GOOD: Strict mode catches errors immediately
#!/usr/bin/env bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

mkdir /tmp/data
cp important.txt /tmp/data/  # Script stops here if file missing
process_data /tmp/data/important.txt  # Only runs if cp succeeded
echo "Success!"  # Only prints if all commands succeeded
```

### Anti-Pattern 3: Using `ls` for File Iteration Instead of Globs

**Problem:** Parsing `ls` output to iterate over files (`for file in $(ls *.txt)`) breaks with filenames containing spaces, newlines, or special characters.

**Correct Pattern:**
```bash
# BAD: Parsing ls output breaks with spaces
for file in $(ls *.txt); do
    echo "Processing $file"
done

# GOOD: Use glob patterns directly
for file in *.txt; do
    echo "Processing $file"
done

# GOOD: Use find for complex searches
while IFS= read -r -d '' file; do
    echo "Processing $file"
done < <(find . -name "*.txt" -print0)
```

## Variable Management

### Variable Declaration and Naming
- **Requirement:** Use descriptive, lowercase variable names with underscores (minimum 3 characters, e.g., `idx` not `i` — except standard loop counters)
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
- **Critical:** Always quote variables to prevent word splitting and globbing (see Anti-Pattern 1 above for examples)
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
# Note: For associative arrays (declare -A), see 300d-bash-advanced.md
```

## Input Handling and Validation

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

## Error Handling and Logging

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
- **Rule:** Implement cleanup for temporary resources (see Temporary Files section for `mktemp` patterns):
```bash
cleanup() {
    [[ -n "${temp_dir:-}" ]] && rm -rf "$temp_dir"
}
trap cleanup EXIT
```

## Function Design and Modularity

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
- **Rule:** Use `getopts` when scripts accept command-line flags:
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

## File and Directory Operations

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
temp_file="$(mktemp)" || { echo "ERROR: mktemp failed" >&2; exit 1; }
temp_dir="$(mktemp -d)" || { echo "ERROR: mktemp -d failed" >&2; exit 1; }
trap 'rm -f "$temp_file"; rm -rf "$temp_dir"' EXIT
```

## Command Execution and Pipelines

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

## Configuration and Environment

### Basic Configuration
- **Rule:** Handle configuration files safely:
```bash
# WARNING: source executes arbitrary code. Prefer key=value parsing when possible.
load_simple_config() {
    local config_file="$1"
    if [[ -f "$config_file" && -O "$config_file" ]]; then
        # shellcheck source=/dev/null
        source "$config_file"
    else
        echo "ERROR: Config file missing or not owned by current user: $config_file" >&2
        return 1
    fi
}
```

## Advanced Topics

> For debugging/troubleshooting, code style standards, ShellCheck integration, performance optimization, advanced anti-patterns, security best practices, and documentation conventions, see **300d-bash-advanced.md**.
> For comprehensive testing frameworks and debugging techniques, see **300b-bash-testing-tooling.md**.
