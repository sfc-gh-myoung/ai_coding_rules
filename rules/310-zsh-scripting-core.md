# Zsh Scripting Core Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Zsh patterns. Load for shell scripting tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** Zsh, Z shell, zsh features, arrays, functions, oh-my-zsh, emulate, setopt, parameter expansion, globbing
**TokenBudget:** ~5300
**ContextTier:** Medium
**Depends:** 300-bash-scripting-core.md

## Scope

**What This Rule Covers:**
Foundational zsh scripting patterns covering unique zsh features, script structure, variables, functions, and essential practices to leverage zsh's advanced capabilities while maintaining compatibility.

**When to Load This Rule:**
- Writing zsh scripts or configuration files
- Converting bash scripts to zsh
- Leveraging zsh-specific features (arrays, parameter expansion, globbing)
- Setting up zsh development environment
- Troubleshooting zsh compatibility issues

## References

### Dependencies

**Must Load First:**
- **300-bash-scripting-core.md** - Foundation bash scripting patterns

**Related:**
- **310a-zsh-advanced-features.md** - Advanced zsh features, completion, and modules
- **310b-zsh-compatibility.md** - Cross-shell compatibility and migration strategies

### External Documentation

- [Zsh Manual](http://zsh.sourceforge.net/Doc/) - Complete official documentation for zsh features and syntax
- [Zsh User Guide](https://zsh-guide.hyperreal.coffee/) - Comprehensive tutorial and best practices guide
- [Oh My Zsh Framework](https://ohmyz.sh/) - Popular plugin and theme framework for zsh

## Contract

### Inputs and Prerequisites

- Zsh script or configuration file requiring development
- Understanding of shell scripting fundamentals
- Access to zsh shell (version 5.0+ recommended)
- Knowledge of bash differences (if migrating from bash)

### Mandatory

- Use `#!/usr/bin/env zsh` shebang for portability
- Set `emulate -L zsh` in functions for consistent behavior
- Configure setopt for strictness (ERR_EXIT, NO_UNSET, PIPE_FAIL)
- Quote variables properly (`"$var"` not `$var`)
- Use zsh arrays correctly (1-indexed by default, or set KSH_ARRAYS for 0-indexed)
- Leverage zsh parameter expansion features

### Forbidden

- Assuming bash compatibility without testing
- Using unquoted variables in command contexts
- Polluting global namespace in .zshrc
- Shadowing system commands with custom functions
- Ignoring zsh-specific array indexing differences

### Execution Steps

1. Set proper shebang (`#!/usr/bin/env zsh`) and configure setopt for error handling
2. Identify zsh-specific features to leverage (arrays, parameter expansion, globbing)
3. Implement functions with `emulate -L zsh` for consistent behavior
4. Use zsh arrays correctly (1-indexed or configure KSH_ARRAYS for 0-indexed)
5. Apply zsh parameter expansion for string manipulation
6. Quote all variables to prevent word splitting issues
7. Test script with `zsh -n` for syntax validation
8. Verify compatibility if script needs to run on multiple shells

### Output Format

Zsh script with:
- Proper shebang (`#!/usr/bin/env zsh`)
- setopt configuration for error handling
- Functions using `emulate -L zsh`
- Correct array usage (1-indexed or KSH_ARRAYS set)
- Proper variable quoting throughout
- Zsh-specific features leveraged appropriately

### Validation

**Pre-Task-Completion Checks:**
- Shebang is `#!/usr/bin/env zsh`
- setopt configured for error handling
- Functions use `emulate -L zsh`
- Arrays indexed correctly (1-based or KSH_ARRAYS set)
- Variables quoted in all contexts
- No bash-specific syntax without compatibility mode

**Success Criteria:**
- `zsh -n script.zsh` passes syntax check
- Script executes without errors on target zsh version
- Arrays accessed correctly (test with sample data)
- Parameter expansion works as expected
- No word splitting issues with unquoted variables
- Functions behave consistently with emulate set

### Design Principles

- **Leverage Zsh Features:** Use advanced capabilities (arrays, globbing, parameter expansion)
- **Explicit Configuration:** Set options explicitly, don't rely on defaults
- **Namespace Safety:** Avoid polluting global namespace in configuration files
- **Compatibility Awareness:** Understand bash differences, test cross-shell if needed
- **Consistent Behavior:** Use `emulate -L zsh` in functions for predictability

### Post-Execution Checklist

- [ ] Shebang set to `#!/usr/bin/env zsh`
- [ ] setopt configured for error handling
- [ ] Functions use `emulate -L zsh`
- [ ] Arrays indexed correctly
- [ ] Variables quoted properly
- [ ] Zsh-specific features used appropriately
- [ ] Syntax validated with `zsh -n`
- [ ] Script tested on target zsh version
- [ ] No namespace pollution in .zshrc
- [ ] Compatibility verified if needed

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Assuming Zsh Defaults Match Bash

**Problem:** Writing scripts that assume bash-like behavior for word splitting, glob expansion, or array indexing without setting appropriate zsh options.

**Why It Fails:** Zsh arrays are 1-indexed by default (bash is 0-indexed). Word splitting doesn't occur on unquoted variables by default. Scripts behave differently than expected, causing subtle bugs.

**Correct Pattern:**
```zsh
# BAD: Assuming bash behavior
#!/bin/zsh
arr=(a b c)
echo ${arr[0]}  # Empty in zsh! Arrays are 1-indexed

# BAD: Assuming word splitting
files="file1.txt file2.txt"
rm $files  # In zsh, this tries to delete "file1.txt file2.txt" as one file

# GOOD: Explicit options for predictable behavior
#!/bin/zsh
setopt KSH_ARRAYS      # 0-indexed arrays like bash
setopt SH_WORD_SPLIT   # Word splitting on unquoted vars

# Or use zsh idioms correctly
arr=(a b c)
echo ${arr[1]}  # "a" - zsh native indexing
files=(file1.txt file2.txt)
rm "${files[@]}"  # Proper array expansion
```

### Anti-Pattern 2: Polluting Global Namespace in .zshrc

**Problem:** Defining functions and variables in .zshrc without namespacing, causing conflicts with system commands or other configurations.

**Why It Fails:** Custom `ls` function shadows /bin/ls. Variables overwrite environment settings. Plugin conflicts become impossible to debug. Shell startup slows down.

**Correct Pattern:**
```zsh
# BAD: Global namespace pollution
# .zshrc
ls() { command ls -la "$@"; }  # Shadows system ls
PATH="/my/path"  # Overwrites instead of extends

# GOOD: Namespaced functions and safe PATH
# .zshrc
my_ls() { command ls -la "$@"; }
alias ll='my_ls'  # Alias instead of shadowing

# Extend PATH safely
path=(/my/path $path)  # zsh array syntax
typeset -U path  # Remove duplicates
```

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

- ****300-bash-scripting-core.md**** - Bash scripting fundamentals for comparison

## Script Foundation & Zsh Setup

### Shebang and Environment
- **Requirement:** Use proper zsh shebang: `#!/usr/bin/env zsh` or `#!/bin/zsh`
- **Rule:** Use `#!/usr/bin/env zsh` for portability across systems
- **Always:** Specify zsh when using zsh-specific features
- **Critical:** Use `emulate -L zsh` in functions for consistent behavior

```zsh
#!/usr/bin/env zsh
# Ensure zsh behavior in mixed environments
emulate -L zsh

# Set strict error handling
set -euo pipefail
```

### Zsh Options and Modes
- **Requirement:** Set appropriate zsh options for script reliability:
```zsh
# Essential options for scripts
setopt ERR_EXIT          # Exit on command failure (equivalent to set -e)
setopt NO_UNSET          # Treat unset variables as errors (set -u)
setopt PIPE_FAIL         # Return exit status of failed command in pipeline
setopt EXTENDED_GLOB     # Enable extended globbing patterns
setopt NULL_GLOB         # Remove non-matching globs instead of error

# Disable problematic options for scripts
unsetopt GLOB_SUBST      # Disable parameter expansion in globs
unsetopt SH_WORD_SPLIT   # Maintain zsh word splitting behavior
```

### Script Metadata and Documentation
- **Requirement:** Include comprehensive header documentation:
```zsh
#!/usr/bin/env zsh
# Script: script_name.zsh
# Description: Brief description of script purpose
# Author: Your Name
# Version: 1.0
# Last Updated: YYYY-MM-DD
# Usage: ./script_name.zsh [options] [arguments]
# Dependencies: zsh 5.0+, required commands

emulate -L zsh
setopt ERR_EXIT NO_UNSET PIPE_FAIL EXTENDED_GLOB
```

## Zsh-Specific Variable Management

### Variable Declaration and Scoping
- **Rule:** Use zsh-specific variable declarations:
```zsh
# Local variables in functions
function process_data() {
    emulate -L zsh
    local input_file="$1"
    local -i count=0              # Integer variable
    local -a files=()             # Array variable
    local -A config=()            # Associative array
    local -r readonly_var="value" # Read-only variable
}

# Global variables with type declarations
typeset -g global_var="value"
typeset -gi global_counter=0
typeset -gA global_config=()
```

### Parameter Expansion Features
- **Rule:** Leverage zsh's advanced parameter expansion:
```zsh
# Advanced parameter expansion
filename="${path:t}"           # Tail (basename)
directory="${path:h}"          # Head (dirname)
extension="${filename:e}"      # Extension
basename="${filename:r}"       # Root (without extension)

# Case modification
upper_text="${text:u}"         # Uppercase
lower_text="${text:l}"         # Lowercase
title_text="${text:tc}"        # Title case

# Padding and alignment
padded="${text:>10}"           # Right-align in 10 chars
left_pad="${text:<10}"         # Left-align in 10 chars

# Default values with type checking
count=${count:-0}              # Default to 0
files=(${files[@]:-})          # Default to empty array
```

### Array Handling
- **Requirement:** Use zsh's powerful array features:
```zsh
# Array declaration and manipulation
files=(file1.txt file2.txt "file with spaces.txt")
readonly -a VALID_TYPES=(txt log conf)

# Array operations
files+=(new_file.txt)          # Append element
files[1,3]=(a b c)            # Replace elements 1-3
files=(${files:#pattern})      # Remove matching elements

# Array information
echo "Array length: ${#files}"
echo "All elements: ${files[*]}"
echo "Elements as separate args: ${files[@]}"

# Array slicing (1-indexed in zsh)
first_three=(${files[1,3]})
last_element=${files[-1]}
all_but_first=(${files[2,-1]})

# Associative arrays
typeset -A config=(
    host "localhost"
    port 8080
    debug true
)

# Access associative array
echo "Host: ${config[host]}"
echo "All keys: ${(k)config}"
echo "All values: ${(v)config}"
```

## Function Definition and Advanced Features

### Function Declaration
- **Rule:** Use zsh function syntax with proper scoping:
```zsh
# Preferred zsh function syntax
function process_file() {
    emulate -L zsh
    setopt LOCAL_OPTIONS ERR_EXIT

    local file="$1"
    local operation="${2:-process}"

    # Function logic here
    echo "Processing $file with operation: $operation"
}

# Alternative syntax (bash-compatible)
process_simple() {
    local input="$1"
    echo "Simple processing: $input"
}
```

### Advanced Function Features
- **Rule:** Use zsh function capabilities:
```zsh
# Function with options parsing
function create_backup() {
    emulate -L zsh
    local -A opts
    zparseopts -D -A opts h v || return 1

    local source="$1"
    [[ -z $source ]] && { echo "Source required" >&2; return 1; }

    [[ -n ${opts[-v]} ]] && echo "Creating backup of $source"
    cp "$source" "${source}.backup"
}
```

## Error Handling and Debugging

### Zsh Error Handling
- **Requirement:** Implement robust error handling:
```zsh
# Global error handler
function handle_error() {
    local exit_code=$?
    local line_number=$1

    echo "Error: Command failed with exit code $exit_code at line $line_number" >&2
    echo "Function: ${funcstack[2]:-main}" >&2
    echo "Script: $0" >&2

    # Print call stack
    echo "Call stack:" >&2
    local i=1
    while [[ $i -le ${#funcstack[@]} ]]; do
        echo "  $i: ${funcstack[$i]} (${funcfiletrace[$i]})" >&2
        ((i++))
    done

    exit $exit_code
}

# Set up error trapping
trap 'handle_error $LINENO' ERR

# Function-specific error handling
function safe_operation() {
    emulate -L zsh
    setopt ERR_RETURN  # Return from function on error

    local file="$1"

    # Check preconditions
    [[ -f "$file" ]] || {
        echo "Error: File not found: $file" >&2
        return 1
    }

    # Perform operation with error checking
    cp "$file" "${file}.backup" || {
        echo "Error: Failed to create backup" >&2
        return 1
    }
}
```

### Cleanup and Resource Management
- **Rule:** Implement proper cleanup:
```zsh
# Global cleanup function
function cleanup() {
    local exit_code=$?

    # Remove temporary files
    [[ -n ${temp_dir:-} ]] && rm -rf "$temp_dir"

    # Kill background processes
    [[ -n ${bg_pid:-} ]] && kill "$bg_pid" 2>/dev/null

    # Restore terminal settings if modified
    [[ -n ${original_stty:-} ]] && stty "$original_stty"

    exit $exit_code
}

# Set up signal handlers
trap cleanup EXIT INT TERM QUIT

# Create temporary resources
temp_dir=$(mktemp -d)
readonly temp_dir
```

## Zsh Globbing and Pattern Matching

### Extended Globbing
- **Rule:** Use zsh globbing features:
```zsh
setopt EXTENDED_GLOB

# Basic glob patterns
files=(*.txt~*backup*)         # Exclude backup files
logs=(**/*.log)               # Recursive search
recent=(*(m-1))               # Modified within last day
dirs=(*(N/))                  # Directories only
```

### Pattern Matching in Conditionals
- **Rule:** Use zsh pattern matching effectively:
```zsh
# Pattern matching with case
case "$filename" in
    *.txt|*.log)
        echo "Text file: $filename"
        ;;
    *.jpg|*.png|*.gif)
        echo "Image file: $filename"
        ;;
    *.(tar.gz|tgz|zip))
        echo "Archive file: $filename"
        ;;
    *)
        echo "Unknown file type: $filename"
        ;;
esac

# Pattern matching in conditionals
if [[ "$string" == (#i)*error* ]]; then  # Case-insensitive match
    echo "Contains 'error' (case-insensitive)"
fi

if [[ "$version" == <1-9>.<0-9>.<0-9> ]]; then  # Numeric ranges
    echo "Valid version format"
fi
```

## Input/Output and Command Execution

### Command Substitution and Pipelines
- **Rule:** Use zsh-optimized command execution:
```zsh
# Command substitution
current_time=$(date '+%Y-%m-%d %H:%M:%S')
file_count=$(print -l *.txt | wc -l)

# Process substitution
diff <(sort file1) <(sort file2)

# Coprocess for bidirectional communication
coproc PROC {
    while read -r line; do
        echo "Processed: $line"
    done
}

echo "test data" >&p
read -r result <&p
```

### Zsh-Specific I/O Features
- **Rule:** Leverage zsh I/O capabilities:
```zsh
# Advanced read with timeout and prompt
if read -t 10 -p "Enter value (10s timeout): " user_input; then
    echo "Got input: $user_input"
else
    echo "Timeout or EOF"
fi

# Read into array
read -A words <<< "word1 word2 word3"

# Here-documents with parameter expansion control
cat <<-'EOF'
    This text will not expand variables: $HOME
EOF

cat <<-EOF
    This text will expand variables: $HOME
EOF
```

## Configuration and Environment

### Zsh Configuration
- **Rule:** Understand startup files:
```zsh
# Startup order: zshenv then zprofile then zshrc then zlogin

# Check shell type
[[ -o interactive ]] && echo "Interactive shell"
[[ -o login ]] && echo "Login shell"
```

### Environment Detection and Adaptation
- **Rule:** Detect and adapt to environment:
```zsh
# Zsh version checking
autoload -U is-at-least
if is-at-least 5.8; then
    echo "Modern zsh version"
    setopt HIST_REDUCE_BLANKS
else
    echo "Older zsh version, using compatibility mode"
fi

# OS detection with zsh built-ins
case "$OSTYPE" in
    darwin*)
        alias ls='ls -G'
        ;;
    linux*)
        alias ls='ls --color=auto'
        ;;
    freebsd*|openbsd*)
        alias ls='ls -G'
        ;;
esac

# Terminal capability detection
if [[ "$TERM" == *color* ]] || [[ "$COLORTERM" == *color* ]]; then
    # Enable colors
    autoload -U colors && colors
fi
```

## Performance and Optimization

### Zsh Performance Best Practices
- **Rule:** Optimize for zsh performance:
```zsh
# Use zsh built-ins instead of external commands
# Fast string operations
string="hello world"
echo "${string:u}"           # Uppercase (faster than tr)
echo "${string//o/0}"        # Replace all 'o' with '0'

# Efficient array operations
large_array=(${(f)"$(< large_file)"})  # Read file into array efficiently

# Use zsh's arithmetic evaluation
(( result = num1 + num2 ))   # Faster than expr or bc

# Avoid unnecessary subshells
files=(*.txt)                # Direct glob assignment
# Instead of: files=($(ls *.txt))
```

### Memory Management
- **Rule:** Manage memory efficiently:
```zsh
# Unset large variables when done
unset large_array large_string

# Use local variables in functions
function process_large_data() {
    emulate -L zsh
    local -a data

    # Process data locally
    data=(${(f)"$(< "$1")"})

    # Process and return result
    echo "${#data}"
    # data automatically cleaned up when function exits
}
```

## Zsh Modules and Autoloading

### Loading Modules
- **Rule:** Load useful modules:
```zsh
zmodload zsh/datetime zsh/mathfunc zsh/stat

echo "Timestamp: $EPOCHSECONDS"
echo "Sine: $(( sin(1.0) ))"
```

### Autoloading
- **Rule:** Use autoloading:
```zsh
fpath=(~/.zsh/functions $fpath)
autoload -Uz colors && colors
```

## Compatibility and Portability

### Bash Compatibility Mode
- **Rule:** Handle bash compatibility when needed:
```zsh
# Enable bash compatibility for specific functions
function bash_compatible_function() {
    emulate -L sh  # Use POSIX/bash behavior

    # Bash-compatible code here
    local array=("$@")
    echo "Elements: ${array[@]}"
}

# Detect if running under bash
if [[ -n "$BASH_VERSION" ]]; then
    echo "Running under bash"
elif [[ -n "$ZSH_VERSION" ]]; then
    echo "Running under zsh"
fi
```

### Cross-Shell Function Writing
- **Rule:** Write portable functions when needed:
```zsh
# Portable function that works in both bash and zsh
portable_function() {
    # Use POSIX-compatible features only
    local input="$1"

    # Avoid zsh-specific features
    if [ -n "$input" ]; then
        echo "Processing: $input"
    else
        echo "No input provided" >&2
        return 1
    fi
}
```

## Common Anti-Patterns to Avoid

### Zsh-Specific Pitfalls
- **Avoid:** Mixing zsh and bash syntax without proper emulation
- **Avoid:** Using `setopt SH_WORD_SPLIT` in scripts (breaks zsh behavior)
- **Avoid:** Forgetting array index differences (zsh is 1-indexed by default)
- **Avoid:** Using `$*` instead of `$@` for argument passing
- **Avoid:** Ignoring zsh's NULL_GLOB behavior with non-matching patterns

### Performance Anti-Patterns
- **Avoid:** Unnecessary external command calls when zsh built-ins exist
- **Avoid:** Using `$(...)` for simple variable assignments
- **Avoid:** Creating subshells for array operations
- **Avoid:** Using `eval` with dynamic content

## Documentation and Style

### Code Documentation
- **Rule:** Document zsh-specific features and requirements:
```zsh
# Document zsh version requirements
# Requires: zsh 5.0+ for associative array features

# Document zsh-specific options used
# Uses: EXTENDED_GLOB for advanced pattern matching

function complex_function() {
    # Document zsh-specific behavior
    # Note: Uses zsh 1-indexed arrays
    emulate -L zsh

    local -a items=("$@")
    echo "First item: ${items[1]}"  # zsh arrays start at 1
}
```

### Usage Information
- **Requirement:** Provide clear usage documentation:
```zsh
show_usage() {
    cat << 'EOF'
Usage: script.zsh [OPTIONS] <command> [arguments]

Requirements:
  - zsh 5.0 or later
  - EXTENDED_GLOB option support

Commands:
  process <file>     Process the specified file
  validate <input>   Validate input format

Options:
  -v, --verbose      Enable verbose output
  -h, --help         Show this help message

Examples:
  ./script.zsh process data.txt
  ./script.zsh --verbose validate input.json

EOF
}
```
