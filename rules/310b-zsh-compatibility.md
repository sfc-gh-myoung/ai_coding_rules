# Zsh Compatibility and Cross-Shell Scripting

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** Zsh, shell compatibility, bash vs zsh, portable scripts, cross-shell, migration, emulate, POSIX compliance, scripting, shell scripting
**TokenBudget:** ~4850
**ContextTier:** Low
**Depends:** 300-bash-scripting-core.md

## Scope

**What This Rule Covers:**
Zsh compatibility strategies, bash migration patterns, and cross-shell scripting best practices for mixed environments, ensuring seamless transitions and portable script solutions.

**When to Load This Rule:**
- Migrating bash scripts to zsh
- Writing portable scripts for multiple shells
- Ensuring cross-shell compatibility
- Understanding bash vs zsh differences
- Setting up mixed shell environments

## References

### Dependencies

**Must Load First:**
- **300-bash-scripting-core.md** - Foundation bash scripting patterns

**Related:**
- **310-zsh-scripting-core.md** - Foundation zsh scripting patterns
- **310a-zsh-advanced-features.md** - Advanced zsh features

### External Documentation

- [Zsh Compatibility](http://zsh.sourceforge.net/FAQ/zshfaq03.html) - Official FAQ on compatibility issues
- [POSIX Shell Specification](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html) - Portable shell scripting standards
- [Bash to Zsh Migration Guide](https://scriptingosx.com/2019/06/moving-to-zsh/) - Practical migration strategies

## Contract

### Inputs and Prerequisites

- Scripts requiring cross-shell compatibility or migration
- Understanding of both bash and zsh syntax differences
- Access to both bash and zsh for testing
- Knowledge of POSIX shell standards for portable code

### Mandatory

- Use `emulate` for compatibility mode when needed
- Test scripts in both bash and zsh environments
- Write POSIX-compliant code for maximum portability
- Document shell requirements clearly in shebang and comments
- Set required options explicitly in scripts (don't rely on .zshrc)
- Implement feature detection for shell-specific functionality

### Forbidden

- Using zsh-only syntax in bash scripts
- Assuming bash behavior in zsh scripts
- Relying on interactive shell options in scripts
- Ignoring array indexing differences (0-based vs 1-based)
- Skipping cross-shell testing

### Execution Steps

1. Identify target shells and compatibility requirements
2. Analyze existing scripts for shell-specific syntax and features
3. Choose strategy: POSIX portable, emulate mode, or shell-specific versions
4. Set required options explicitly in scripts (setopt for zsh)
5. Convert shell-specific syntax to portable alternatives or add feature detection
6. Test scripts in both bash and zsh environments
7. Document shell requirements and compatibility notes
8. Implement fallbacks for shell-specific features if needed

### Output Format

Cross-shell compatible scripts with:
- Clear shebang indicating target shell
- Explicit option settings (setopt for zsh)
- POSIX-compliant syntax where possible
- Feature detection for shell-specific functionality
- Documentation of shell requirements
- Tests passing in both bash and zsh

### Validation

**Pre-Task-Completion Checks:**
- Shell type clearly specified in shebang
- Required options set explicitly
- Shell-specific features identified
- Compatibility tested in target shells
- POSIX compliance verified where applicable
- Fallbacks implemented for shell-specific features

**Success Criteria:**
- Scripts execute successfully in both bash and zsh
- Array operations work correctly (accounting for indexing differences)
- No unexpected behavior from option differences
- POSIX compliance verified with `checkbashisms` or similar
- Tests pass in both shell environments
- Documentation clearly states shell requirements

### Design Principles

- **Explicit Over Implicit:** Set all required options explicitly
- **Test Both Ways:** Verify in both bash and zsh
- **POSIX When Possible:** Use portable patterns for maximum compatibility
- **Document Differences:** Clearly note shell-specific behavior
- **Graceful Degradation:** Implement fallbacks for missing features

### Post-Execution Checklist

- [ ] Shell type specified in shebang
- [ ] Options set explicitly
- [ ] Tested in bash environment
- [ ] Tested in zsh environment
- [ ] POSIX compliance verified
- [ ] Array indexing handled correctly
- [ ] Shell-specific features documented
- [ ] Fallbacks implemented
- [ ] Migration path documented
- [ ] All tests passing

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Using Zsh-Only Syntax in Portable Scripts

**Problem:** Writing scripts with `#!/bin/sh` or `#!/bin/bash` shebang but using zsh-specific syntax like extended globbing, associative array syntax, or zsh parameter expansion.

**Why It Fails:** Scripts fail on systems where /bin/sh is dash or bash. CI/CD environments may not have zsh. Docker containers use minimal shells. Portability broken silently.

**Correct Pattern:**
```zsh
# BAD: Zsh syntax with bash shebang
#!/bin/bash
files=(*.txt(N))  # Zsh glob qualifier - fails in bash!
print -P "%F{red}Error%f"  # Zsh print - not in bash

# GOOD: Match shebang to syntax
#!/bin/zsh
files=(*.txt(N))  # Zsh script, zsh syntax OK

# OR write portable POSIX
#!/bin/sh
files=$(find . -name "*.txt")  # POSIX compatible
printf "\033[31mError\033[0m\n"  # POSIX printf
```

### Anti-Pattern 2: Ignoring setopt Differences Between Interactive and Script Modes

**Problem:** Writing scripts that depend on options set in .zshrc (like EXTENDED_GLOB or NULL_GLOB) without explicitly setting them in the script.

**Why It Fails:** Scripts work when sourced but fail when executed. Behavior differs between users with different .zshrc configs. CI environments have different defaults. Subtle bugs from option mismatches.

**Correct Pattern:**
```zsh
# BAD: Assumes interactive options are set
#!/bin/zsh
# Relies on EXTENDED_GLOB from .zshrc
if [[ $file == *.txt~backup* ]]; then  # Extended glob - may not work!
    process "$file"
fi

# GOOD: Explicitly set required options
#!/bin/zsh
setopt EXTENDED_GLOB  # Enable extended globbing
setopt NULL_GLOB      # No error on no matches
setopt ERR_EXIT       # Exit on error

if [[ $file == *.txt~backup* ]]; then
    process "$file"
fi
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

## Bash to Zsh Migration Strategies

### Compatibility Assessment
- **Rule:** Evaluate bash scripts for zsh compatibility:
```zsh
# Check for bash-specific features that need attention
check_bash_compatibility() {
    local script="$1"
    local issues=()

    # Check for problematic patterns
    grep -n 'declare -[aA]' "$script" && issues+=("declare arrays")
    grep -n '\[\[.*=~' "$script" && issues+=("regex matching")
    grep -n 'BASH_' "$script" && issues+=("bash variables")
    grep -n 'shopt' "$script" && issues+=("bash options")

    if (( ${#issues} > 0 )); then
        echo "Compatibility issues found:"
        printf '  - %s\n' "${issues[@]}"
        return 1
    else
        echo "No obvious compatibility issues"
        return 0
    fi
}
```

### Migration Patterns
- **Rule:** Convert bash-specific constructs to zsh equivalents:
```zsh
# Bash to zsh array conversion
# Bash: declare -a array=()
# Zsh equivalent:
typeset -a array=()
# Or simply: array=()

# Bash to zsh associative array conversion
# Bash: declare -A assoc_array=()
# Zsh equivalent:
typeset -A assoc_array=()

# Bash regex matching conversion
# Bash: [[ "$string" =~ pattern ]]
# Zsh equivalent:
if [[ "$string" =~ pattern ]]; then
    # Use match array in zsh
    echo "Matched: $MATCH"
    echo "Groups: ${match[*]}"
fi

# Or use zsh pattern matching:
if [[ "$string" == (#b)(*pattern*) ]]; then
    echo "Matched: ${match[1]}"
fi
```

### Migration Phases
- **Rule:** Migrate gradually:
```zsh
# Phase 1: Bash compatibility
emulate -L sh
setopt BASH_REMATCH

# Phase 2: Native zsh
emulate -L zsh
setopt EXTENDED_GLOB
```

## Cross-Shell Compatibility Patterns

### Portable Function Writing
- **Rule:** Write functions that work in both bash and zsh:
```zsh
# Detect shell type
detect_shell() {
    if [[ -n "$ZSH_VERSION" ]]; then
        echo "zsh"
    elif [[ -n "$BASH_VERSION" ]]; then
        echo "bash"
    else
        echo "unknown"
    fi
}

# Portable array handling
portable_array_append() {
    local array_name="$1"
    shift

    case "$(detect_shell)" in
        zsh)
            # Zsh: use parameter expansion
            eval "${array_name}+=(\"\$@\")"
            ;;
        bash)
            # Bash: use array assignment
            eval "${array_name}+=(\"\$@\")"
            ;;
        *)
            # Fallback for other shells
            eval "${array_name}=\"\${${array_name}} \$*\""
            ;;
    esac
}

# Portable string manipulation
portable_uppercase() {
    local input="$1"

    case "$(detect_shell)" in
        zsh)
            echo "${input:u}"
            ;;
        bash)
            echo "${input^^}"
            ;;
        *)
            echo "$input" | tr '[:lower:]' '[:upper:]'
            ;;
    esac
}
```

### Feature Detection Patterns
- **Rule:** Use feature detection instead of shell detection:
```zsh
# Test for specific features rather than shell type
has_associative_arrays() {
    # Try to create an associative array
    local -A test_array 2>/dev/null || return 1
    test_array[key]="value"
    [[ "${test_array[key]}" == "value" ]]
}

has_extended_glob() {
    # Test for extended globbing
    setopt EXTENDED_GLOB 2>/dev/null || return 1
    # Test a simple extended glob pattern
    [[ "test" == t(e|a)st ]] 2>/dev/null
}

has_parameter_expansion() {
    # Test for advanced parameter expansion
    local test="hello"
    [[ "${test:u}" == "HELLO" ]] 2>/dev/null
}

# Use features conditionally
smart_glob() {
    local pattern="$1"

    if has_extended_glob; then
        # Use zsh extended globbing
        setopt EXTENDED_GLOB
        files=($~pattern)
    else
        # Fall back to basic globbing
        files=($pattern)
    fi

    printf '%s\n' "${files[@]}"
}
```

### Configuration File Compatibility
- **Rule:** Write portable configuration:
```zsh
# Portable shell configuration
# ~/.shellrc - sourced by both .bashrc and .zshrc

# Common aliases that work in both shells
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'

# Portable functions
cd_and_list() {
    cd "$@" && ls
}

# Shell-specific configurations
case "$0" in
    *zsh*)
        # Zsh-specific settings
        setopt AUTO_CD
        setopt CORRECT
        ;;
    *bash*)
        # Bash-specific settings
        shopt -s autocd 2>/dev/null
        shopt -s cdspell 2>/dev/null
        ;;
esac

# Feature-based configuration
if command -v fzf >/dev/null; then
    # Configure fzf for available shell
    if [[ -n "$ZSH_VERSION" ]]; then
        source <(fzf --zsh)
    elif [[ -n "$BASH_VERSION" ]]; then
        source <(fzf --bash)
    fi
fi
```

## Environment Detection and Adaptation

### Runtime Environment Detection
- **Rule:** Detect and adapt to runtime environment:
```zsh
# Comprehensive environment detection
detect_environment() {
    local env_info=()

    # Shell information
    env_info+=("shell:$(detect_shell)")

    # Version information
    if [[ -n "$ZSH_VERSION" ]]; then
        env_info+=("zsh_version:$ZSH_VERSION")
    elif [[ -n "$BASH_VERSION" ]]; then
        env_info+=("bash_version:$BASH_VERSION")
    fi

    # Terminal information
    env_info+=("term:${TERM:-unknown}")
    env_info+=("colorterm:${COLORTERM:-none}")

    # OS information
    env_info+=("os:$OSTYPE")

    # Interactive vs non-interactive
    if [[ -o interactive ]] 2>/dev/null || [[ $- == *i* ]]; then
        env_info+=("mode:interactive")
    else
        env_info+=("mode:non-interactive")
    fi

    printf '%s\n' "${env_info[@]}"
}

# Adaptive configuration based on environment
configure_shell() {
    local -A env

    # Parse environment info
    while IFS=: read -r key value; do
        env[$key]="$value"
    done < <(detect_environment)

    # Configure based on detected environment
    case "${env[shell]}" in
        zsh)
            configure_zsh "${env[@]}"
            ;;
        bash)
            configure_bash "${env[@]}"
            ;;
    esac
}

configure_zsh() {
    # Zsh-specific configuration
    setopt AUTO_CD CORRECT HIST_VERIFY

    # Load zsh modules if available
    zmodload zsh/complist 2>/dev/null
    zmodload zsh/mathfunc 2>/dev/null
}

configure_bash() {
    # Bash-specific configuration
    shopt -s autocd cdspell histverify 2>/dev/null

    # Enable programmable completion
    if [[ -f /etc/bash_completion ]]; then
        source /etc/bash_completion
    fi
}
```

### Capability-Based Feature Loading
- **Rule:** Load features based on capabilities:
```zsh
# Feature capability matrix
declare -A shell_features=(
    [zsh:extended_glob]=true
    [zsh:associative_arrays]=true
    [zsh:parameter_flags]=true
    [bash:associative_arrays]=true
    [bash:regex_match]=true
)

has_feature() {
    local feature="$1"
    local shell_key="$(detect_shell):$feature"

    [[ "${shell_features[$shell_key]}" == "true" ]]
}

# Load features conditionally
load_advanced_features() {
    if has_feature "extended_glob"; then
        enable_extended_globbing
    fi

    if has_feature "associative_arrays"; then
        setup_config_system
    fi

    if has_feature "parameter_flags"; then
        setup_advanced_text_processing
    fi
}
```

## Testing Cross-Shell Compatibility

### Multi-Shell Testing
- **Rule:** Test across shells:
```zsh
test_shells=(zsh bash)

run_multi_shell_tests() {
    local script="$1" passed=0 total=0

    for shell in "${test_shells[@]}"; do
        command -v "$shell" >/dev/null || continue
        ((total++))

        if "$shell" "$script"; then
            echo "$shell: PASS"
            ((passed++))
        else
            echo "$shell: FAIL"
        fi
    done

    echo "Results: $passed/$total passed"
}
```

### Compatibility Checking
- **Rule:** Validate compatibility:
```zsh
check_compatibility() {
    local script="$1" issues=()

    grep -q 'declare -[aA]' "$script" && issues+=("bash declare")
    grep -q 'setopt' "$script" && issues+=("zsh options")

    if (( ${#issues} > 0 )); then
        echo "Issues: ${issues[*]}"
        return 1
    fi

    echo "Compatible"
}
```

## Migration Tools and Utilities

### Automated Migration Assistant
- **Rule:** Create tools to assist with migration:
```zsh
# Bash to zsh migration tool
migrate_bash_to_zsh() {
    local input_file="$1"
    local output_file="${2:-${input_file%.sh}.zsh}"

    # Create backup
    cp "$input_file" "${input_file}.backup"

    # Perform automated conversions
    sed -i.tmp '
        # Change shebang
        1s|#!/bin/bash|#!/usr/bin/env zsh|
        1s|#!/usr/bin/bash|#!/usr/bin/env zsh|

        # Convert declare to typeset
        s/declare -a/typeset -a/g
        s/declare -A/typeset -A/g
        s/declare -r/typeset -r/g

        # Add emulate directive after shebang
        2i\
emulate -L zsh

    ' "$input_file"

    # Manual review needed message
    cat << EOF
Migration completed for $input_file -> $output_file

Manual review required for:
- Array indexing (bash: 0-based, zsh: 1-based by default)
- Regex matching patterns
- Word splitting behavior
- Glob patterns

Use 'diff $input_file.backup $output_file' to review changes.
EOF
}

# Interactive migration wizard
migration_wizard() {
    local script="$1"

    echo "Zsh Migration Wizard for: $script"
    echo "================================="

    # Analyze script
    echo "Analyzing script..."
    local issues=($(analyze_bash_script "$script"))

    if (( ${#issues} == 0 )); then
        echo "No migration issues detected"
        return 0
    fi

    echo "Issues found:"
    for issue in "${issues[@]}"; do
        echo "  - $issue"

        read -q "REPLY?Fix this issue automatically? (y/n) "
        echo

        if [[ "$REPLY" == "y" ]]; then
            fix_migration_issue "$script" "$issue"
        fi
    done
}
```

### Compatibility Shims
- **Rule:** Provide compatibility layers:
```zsh
# Zsh shims for bash
if [[ -n "$BASH_VERSION" ]]; then
    typeset() {
        case "$1" in
            -a) declare -a "${@:2}" ;;
            -A) declare -A "${@:2}" ;;
            *) declare "$@" ;;
        esac
    }
fi
```

## Best Practices for Mixed Environments

### Project Structure
- **Rule:** Organize for multi-shell support:

Directory structure for `project/`:
- **bin/** - `script.sh` (Portable main script)
- **lib/** - Library files
  - `common.sh` - Shared functions
  - **zsh/** - Zsh-specific
  - **bash/** - Bash-specific
- **tests/** - Shell-specific tests

### Documentation Standards
- **Rule:** Document compatibility:
```zsh
#!/usr/bin/env zsh
# Compatibility: Zsh 5.0+, Bash 4.0+
# Features: Extended globbing (zsh only)

# Compatibility check
[[ -n "$ZSH_VERSION" || -n "$BASH_VERSION" ]] || {
    echo "Requires zsh or bash" >&2; exit 1
}
```

## Performance Considerations

### Shell-Specific Optimizations
- **Rule:** Optimize for target shell capabilities:
```zsh
# Performance-aware function selection
fast_string_processing() {
    local input="$1"

    if [[ -n "$ZSH_VERSION" ]]; then
        # Use zsh parameter expansion (fastest)
        echo "${input:u}"
    elif [[ -n "$BASH_VERSION" ]] && (( BASH_VERSINFO[0] >= 4 )); then
        # Use bash 4.0+ parameter expansion
        echo "${input^^}"
    else
        # Fall back to external command (slowest)
        echo "$input" | tr '[:lower:]' '[:upper:]'
    fi
}

# Conditional feature loading
load_performance_features() {
    case "$(detect_shell)" in
        zsh)
            # Load zsh-specific optimizations
            setopt EXTENDED_GLOB
            zmodload zsh/mathfunc
            ;;
        bash)
            # Load bash-specific optimizations
            shopt -s extglob
            ;;
    esac
}
```

### Performance Benchmarking
- **Rule:** Compare shell performance:
```zsh
benchmark_function() {
    local func="$1" iterations="${2:-100}"

    for shell in zsh bash; do
        command -v "$shell" >/dev/null || continue

        local start=$(date +%s)
        for ((i=1; i<=iterations; i++)); do
            "$shell" -c "$func"
        done
        local end=$(date +%s)

        echo "$shell: $((end - start))s"
    done
}
```
