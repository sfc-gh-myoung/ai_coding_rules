# Bash Scripting Core Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Bash patterns. Load for shell scripting tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** Bash, shell scripting, set -euo pipefail, error handling, strict mode, functions, variables, script structure, trap, exit codes, shellcheck, input validation
**TokenBudget:** ~5000
**ContextTier:** High
**Depends:** 000-global-core.md

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
- shellcheck installed for static analysis
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
- Untested shell expansions or glob patterns

### Execution Steps

1. Start with `#!/usr/bin/env bash` shebang and `set -euo pipefail`
2. Include script metadata, help functions, and proper signal trapping
3. Quote all variables and validate inputs
4. Use local variables in functions to prevent pollution
5. Implement comprehensive error handling with meaningful exit codes
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
- shellcheck passes with no warnings
- Script handles spaces in filenames
- Error conditions exit with non-zero codes
- Cleanup handler executes on exit/signal

**Investigation Required:**
1. **Read existing scripts BEFORE suggesting changes** - Check current patterns, error handling
2. **Verify shell type** - Confirm bash vs sh, check shebang and features used
3. **Never assume error handling exists** - Check for `set -euo pipefail`, trap handlers
4. **Check for shellcheck compliance** - Run shellcheck to identify existing issues
5. **Test with actual inputs** - Verify scripts work with edge cases (spaces, special chars)

**Anti-Pattern Examples:**
- "Adding set -euo pipefail..." (without checking if script is compatible)
- "Quoting variables..." (without testing for unintended changes)
- Assuming script uses bash when it's actually sh

**Correct Pattern:**
- "Let me check your script's current error handling first."
- [reads script, checks for existing patterns, runs shellcheck]
- "I see you're missing error handling. Adding set -euo pipefail and trap handlers..."
- [implements changes, runs shellcheck, tests with edge cases]

### Design Principles

- **Strict Error Handling:** Use `set -euo pipefail` to catch errors early
- **Quote Everything:** Always quote variables to prevent word splitting
- **Local Scope:** Use `local` in functions to prevent variable pollution
- **Trap Signals:** Implement cleanup handlers for graceful exits
- **Validate Inputs:** Check arguments, files, and command availability
- **Clear Error Messages:** Write errors to stderr with context
- **Consistent Style:** Follow established patterns for readability
- **Portable Code:** Use `#!/usr/bin/env bash` and avoid bashisms when targeting sh

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (000-global-core.md)
- [ ] Bash 4.0+ available
- [ ] shellcheck installed
- [ ] Existing scripts reviewed (if modifying)

**After Completion:**
- [ ] **CRITICAL:** `shellcheck script.sh` passes with no errors
- [ ] **CRITICAL:** All variables quoted
- [ ] **CRITICAL:** `set -euo pipefail` at top of script
- [ ] **CRITICAL:** Functions use `local` variables
- [ ] Shebang is `#!/usr/bin/env bash`
- [ ] Trap handler for cleanup present
- [ ] Input validation implemented
- [ ] Exit codes meaningful and checked
- [ ] Error messages go to stderr
- [ ] Script tested with edge cases
- [ ] CHANGELOG.md and README.md updated as required

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Unquoted Variables Leading to Word Splitting

**Problem:** Using variables without quotes (`$var` instead of `"$var"`), causing unexpected word splitting and glob expansion when values contain spaces or special characters.

**Why It Fails:** File paths with spaces break scripts, command arguments split incorrectly, and glob patterns expand unexpectedly. Unquoted variables are the #1 cause of bash script bugs in production.

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

**Problem:** Running scripts without `set -euo pipefail`, allowing commands to fail silently and scripts to continue executing with undefined variables or failed pipeline commands.

**Why It Fails:** Silent failures corrupt data, scripts appear to succeed when critical steps failed, and undefined variables cause unpredictable behavior. Production incidents occur because errors weren't caught during testing.

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

**Problem:** Parsing `ls` output to iterate over files (`for file in $(ls *.txt)`), which breaks with filenames containing spaces, newlines, or special characters.

**Why It Fails:** `ls` output is designed for human reading, not parsing. Filenames with spaces split into multiple items, newlines break loops, and special characters cause unexpected behavior.

**Correct Pattern:**
```bash
# BAD: Parsing ls output breaks with spaces
for file in $(ls *.txt); do
    echo "Processing $file"  # Breaks if filename has spaces
done

# Also bad: ls in command substitution
files=$(ls *.txt)  # Loses filename structure

# GOOD: Use glob patterns directly
for file in *.txt; do
    echo "Processing $file"  # Works with spaces and special chars
done

# GOOD: Use find for complex searches
while IFS= read -r -d '' file; do
    echo "Processing $file"
done < <(find . -name "*.txt" -print0)  # Handles all filenames safely
```

## Variable Management

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
temp_file="$(mktemp)"
temp_dir="$(mktemp -d)"
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

### Process Management
- **Rule:** Handle background processes:
```bash
# Start background task
long_running_command &
local pid=$!

# Wait for completion
wait "$pid"
```

## Configuration and Environment

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

## Debugging and Troubleshooting

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

## Performance Optimization

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

## Code Style and Standards

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

## Security Best Practices

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

## Additional Anti-Patterns

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

## Documentation and Comments

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
