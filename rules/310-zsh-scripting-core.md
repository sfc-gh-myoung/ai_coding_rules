# Zsh Scripting Core Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential Zsh patterns. Load for shell scripting tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-03-25
**Keywords:** Zsh, Z shell, zsh features, arrays, functions, oh-my-zsh, emulate, setopt, parameter expansion, globbing
**TokenBudget:** ~4300
**ContextTier:** Medium
**Depends:** 300-bash-scripting-core.md
**LoadTrigger:** ext:.zsh, kw:zsh

## Scope

**What This Rule Covers:**
Foundational zsh scripting patterns covering unique zsh features, script structure, variables, functions, and essential practices to leverage zsh's advanced capabilities while maintaining compatibility.

**When to Load This Rule:**
- Writing or converting zsh scripts and configuration files
- Leveraging zsh-specific features (arrays, parameter expansion, globbing)
- Setting up zsh environment or troubleshooting compatibility issues

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
- Understanding of shell scripting fundamentals (variables, functions, conditionals, loops, and exit codes as covered in 300-bash-scripting-core.md)
- Access to zsh shell (version 5.0 or later required)
- Knowledge of bash differences (if migrating from bash)

### Mandatory

- Use `#!/usr/bin/env zsh` shebang for portability
- Set `emulate -L zsh` in functions for consistent behavior
- Configure setopt for strictness (ERR_EXIT, NO_UNSET, PIPE_FAIL)
- Quote variables properly (`"$var"` not `$var`)
- Use zsh arrays correctly (1-indexed by default, or set KSH_ARRAYS for 0-indexed)
- Use zsh parameter expansion (`${var:t}`, `${var:h}`, `${var:u}`, `${var:l}`) instead of external commands (`basename`, `dirname`, `tr`)

### Forbidden

- Assuming bash compatibility without testing
- Using unquoted variables in command contexts
- Polluting global namespace in .zshrc
- Shadowing system commands with custom functions
- Ignoring zsh-specific array indexing differences

### Execution Steps

1. Set proper shebang (`#!/usr/bin/env zsh`) and configure setopt for error handling
2. Replace bash constructs with zsh equivalents: `basename` becomes `${path:t}`, `dirname` becomes `${path:h}`, `tr '[:lower:]' '[:upper:]'` becomes `${text:u}`, `tr '[:upper:]' '[:lower:]'` becomes `${text:l}`
3. Implement functions with `emulate -L zsh` for consistent behavior
4. Use zsh arrays correctly (1-indexed or configure KSH_ARRAYS for 0-indexed)
5. Apply zsh parameter expansion for string manipulation
6. Quote all variables to prevent word splitting issues
7. Test script with `zsh -n` for syntax validation
8. Verify compatibility if script needs to run on multiple shells

### Output Format

Zsh script satisfying all Mandatory items above, plus:
- Parameter expansion used instead of external commands (`${var:t}` not `basename`, `${var:u}` not `tr`)
- Correct array usage (1-indexed or KSH_ARRAYS set)

### Validation

**Pre-Task-Completion Checks:**
- All Mandatory items satisfied
- No bash-specific syntax without compatibility mode

**Success Criteria:**
- `zsh -n script.zsh` passes syntax check
- Script executes without errors on target zsh version (5.0+)
- Arrays accessed correctly (test with sample data)
- Parameter expansion works as expected

**During-Execution Checks:**
- Verify intermediate files exist before using them: `[[ -f "$intermediate" ]] || return 1`
- Log progress for long operations: `print -u2 "Processing $i of ${#files[@]}"`

### Design Principles

- **Leverage Zsh Features:** Use advanced capabilities (arrays, globbing, parameter expansion)
- **Explicit Configuration:** Set options explicitly, don't rely on defaults
- **Namespace Safety:** Avoid polluting global namespace in configuration files
- **Compatibility Awareness:** Test cross-shell if script must run on both bash and zsh
- **Consistent Behavior:** Use `emulate -L zsh` in functions for predictability

### Post-Execution Checklist

- [ ] All Mandatory and Pre-Task items verified
- [ ] Parameter expansion used instead of external commands where applicable
- [ ] Syntax validated with `zsh -n`
- [ ] Script tested on target zsh version (5.0+)
- [ ] No namespace pollution in .zshrc
- [ ] Compatibility verified if needed

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Assuming Zsh Defaults Match Bash

**Problem:** Writing scripts that assume bash-like behavior for word splitting, glob expansion, or array indexing without setting appropriate zsh options.

**Correct Pattern:**
```zsh
# BAD: Assuming bash behavior
arr=(a b c); echo ${arr[0]}  # Empty in zsh! Arrays are 1-indexed
files="file1.txt file2.txt"
rm $files  # Zsh treats this as one filename (no word splitting)

# GOOD: Explicit options for predictable behavior
#!/bin/zsh
setopt KSH_ARRAYS      # 0-indexed arrays like bash
# NOTE: Keep SH_WORD_SPLIT off (zsh default). Use `emulate -L sh` for POSIX blocks.

# Or use zsh idioms correctly
arr=(a b c)
echo ${arr[1]}  # "a" - zsh native indexing
files=(file1.txt file2.txt)
rm "${files[@]}"  # Proper array expansion
```

### Anti-Pattern 2: Polluting Global Namespace in .zshrc

**Problem:** Defining functions and variables in .zshrc without namespacing, causing conflicts with system commands or other configurations.

**Correct Pattern:**
```zsh
# BAD: ls() { command ls -la "$@"; }  -- shadows system ls
# BAD: PATH="/my/path"  -- overwrites instead of extends

# GOOD: Namespaced functions and safe PATH
my_ls() { command ls -la "$@"; }
alias ll='my_ls'  # Alias instead of shadowing
path=(/my/path $path)  # zsh array syntax
typeset -U path  # Remove duplicates
```

## Output Format Examples

```zsh
#!/usr/bin/env zsh
emulate -L zsh
setopt ERR_EXIT NO_UNSET PIPE_FAIL EXTENDED_GLOB

readonly SCRIPT_DIR="${0:A:h}"

main() {
    emulate -L zsh
    local -a required_commands=(jq curl git)
    for cmd in "${required_commands[@]}"; do
        command -v "$cmd" &>/dev/null || { print -u2 "ERROR: Missing: $cmd"; return 1 }
    done
    print "Processing complete."
}

main "$@"
```

```zsh
# Validate syntax
zsh -n script.zsh
```

## Script Foundation & Zsh Setup

### Shebang and Environment
- **Rule:** Use proper zsh shebang: `#!/usr/bin/env zsh` or `#!/bin/zsh`
- **Rule:** Use `#!/usr/bin/env zsh` for portability across systems
- **Always:** Specify zsh when using zsh-specific features
- **Critical:** Use `emulate -L zsh` in functions for consistent behavior

```zsh
#!/usr/bin/env zsh
# Ensure zsh behavior in mixed environments
emulate -L zsh

# Set strict error handling (zsh-native; `set -euo pipefail` works but prefer native)
setopt ERR_EXIT NO_UNSET PIPE_FAIL
```

### Zsh Options and Modes
- **Rule:** Set zsh options for script reliability:
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
- **Rule:** Include comprehensive header documentation:
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

- **Rule:** Comment zsh-specific behavior (e.g., `# zsh arrays start at 1`)
- **Rule:** Provide usage information via a `show_usage()` function with `cat << 'EOF'`

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

# Global variables: typeset -g (string), -gi (int), -gA (assoc array)
typeset -g global_var="value"; typeset -gi global_counter=0; typeset -gA global_config=()
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

# Edge case: empty or root paths
# ${empty_var:t}  -> "" (empty string)
# ${"/:t"}        -> "" (empty string -- root has no tail)
# ${"/:h"}        -> "/" (root is its own head)
# Always guard: [[ -n "${filepath}" ]] || return 1
```

### Array Handling
- **Rule:** Use zsh's powerful array features:
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
typeset -A config=(host "localhost" port 8080 debug true)
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
    zparseopts -D -A opts h v || { echo "Usage: create_backup [-h] [-v] <source>" >&2; return 1; }

    local source="$1"
    [[ -n ${opts[-h]} ]] && { echo "Usage: create_backup [-h] [-v] <source>"; return 0; }
    [[ -z $source ]] && { echo "Error: source path required" >&2; return 1; }

    [[ -n ${opts[-v]} ]] && echo "Creating backup of $source"
    cp "$source" "${source}.backup"
}
```

## Error Handling and Debugging

### Zsh Error Handling
- **Rule:** Implement robust error handling:
```zsh
# Global error handler using funcstack
function handle_error() {
    local exit_code=$?
    echo "Error: exit $exit_code at line $1 in ${funcstack[2]:-main}" >&2
    exit $exit_code
}
trap 'handle_error $LINENO' ERR

# Function-specific: use ERR_RETURN to return (not exit) on error
function safe_operation() {
    emulate -L zsh
    setopt ERR_RETURN
    local file="$1"
    [[ -f "$file" ]] || { echo "Error: File not found: $file" >&2; return 1 }
    cp "$file" "${file}.backup"
}
```

### Cleanup and Resource Management
- **Rule:** Implement proper cleanup:
```zsh
function cleanup() {
    local exit_code=$?
    [[ -n ${temp_dir:-} ]] && rm -rf "$temp_dir"
    [[ -n ${bg_pid:-} ]] && kill "$bg_pid" 2>/dev/null
    [[ -n ${original_stty:-} ]] && stty "$original_stty"
    exit $exit_code
}
trap cleanup EXIT INT TERM QUIT
temp_dir=$(mktemp -d) || { print -u2 "Failed to create temp directory"; exit 1 }
readonly temp_dir
```

### Resource and Encoding Safety

```zsh
# Disk space check before large writes
local available_kb=$(df -k "${target_dir}" | tail -1 | awk '{print $4}')
(( available_kb > 10240 )) || { print -u2 "ERROR: <10MB free in ${target_dir}"; return 1 }

# Guard against empty/zero-length arrays before iteration
[[ ${#files[@]} -gt 0 ]] || { print -u2 "WARN: No files to process"; return 0 }

# Locale-safe byte operations (avoid UTF-8 multi-byte issues)
LC_ALL=C command grep -c 'pattern' "$file"
```

## Zsh Globbing and Pattern Matching

> For comprehensive globbing patterns and advanced matching, see **310a-zsh-advanced-features.md**.

### Extended Globbing
- **Rule:** Enable and use zsh globbing features:
```zsh
setopt EXTENDED_GLOB

files=(*.txt~*backup*)         # Exclude backup files
logs=(**/*.log)               # Recursive search
recent=(*(m-1))               # Modified within last day
dirs=(*(N/))                  # Directories only
```

### Pattern Matching
- **Rule:** Use `(#i)` for case-insensitive and `<n-m>` for numeric range matching in `[[ ]]` conditionals.

## Input/Output and Command Execution

> For advanced I/O patterns (coprocesses, bidirectional pipes), see **310a-zsh-advanced-features.md**.

- **Rule:** Use zsh-optimized command execution:
```zsh
# Command substitution
current_time=$(date '+%Y-%m-%d %H:%M:%S')

# Process substitution
diff <(sort file1) <(sort file2)

# Read into array
read -A words <<< "word1 word2 word3"
```

## Configuration and Environment

> For detailed configuration management and environment adaptation, see **310b-zsh-compatibility.md**.

- **Rule:** Startup file order: `zshenv` > `zprofile` > `zshrc` > `zlogin`
- **Rule:** Use `[[ -o interactive ]]` and `[[ -o login ]]` to detect shell type
- **Rule:** Use `autoload -U is-at-least` to check zsh version requirements
- **Rule:** Use `$OSTYPE` for OS detection (`darwin*`, `linux*`, `freebsd*`)
- **Rule:** Load modules with `zmodload zsh/datetime zsh/mathfunc zsh/stat`
- **Rule:** Add custom function dirs to `fpath` and use `autoload -Uz`

## Performance and Optimization

- **Rule:** Use parameter expansion (`${string:u}`, `${string//o/0}`) instead of `tr`/`sed`
- **Rule:** Use `(( ))` arithmetic instead of `expr` or `bc`
- **Rule:** Use direct glob assignment (`files=(*.txt)`) instead of `$(ls *.txt)`
- **Rule:** Read files into arrays with `(${(f)"$(< file)"})` instead of line-by-line loops
- **Rule:** Unset variables holding large data (>1MB) when no longer needed
- **Rule:** Use `local` variables in functions (auto-cleaned on function exit)

## Compatibility and Portability

- **Rule:** Use `emulate -L sh` inside functions that must be bash-compatible
- **Rule:** Detect shell with `$BASH_VERSION` / `$ZSH_VERSION` checks
- **Rule:** For POSIX-portable functions, use `[ ]` instead of `[[ ]]` and avoid zsh-specific features

## Common Anti-Patterns to Avoid

### Zsh-Specific Pitfalls
- **Avoid:** Mixing zsh and bash syntax without proper emulation
- **Avoid:** Using `setopt SH_WORD_SPLIT` in scripts (breaks zsh behavior). Use `emulate -L sh` for POSIX compatibility blocks instead.
- **Avoid:** Forgetting array index differences (zsh is 1-indexed by default)
- **Avoid:** Using `$*` instead of `$@` for argument passing
- **Avoid:** Ignoring zsh's NULL_GLOB behavior with non-matching patterns

### Performance Anti-Patterns

**BAD:** Using external commands when parameter expansion works:

```zsh
# BAD: External command for simple string operation
local upper=$(echo "$text" | tr '[:lower:]' '[:upper:]')
local base=$(basename "$filepath")
```

**GOOD:** Use zsh parameter expansion:

```zsh
# GOOD: Built-in parameter expansion -- no subprocess
local upper="${text:u}"
local base="${filepath:t}"
```

- **Avoid:** Using `eval` with dynamic content (use parameter expansion or arrays instead)
- **Avoid:** Ignoring startup time impact of plugins and completions (profile with `zprof`)
