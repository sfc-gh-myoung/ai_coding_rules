# Zsh Compatibility and Cross-Shell Scripting

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** Zsh, shell compatibility, bash vs zsh, portable scripts, cross-shell, migration, emulate, POSIX compliance, scripting, shell scripting
**TokenBudget:** ~2950
**ContextTier:** Low
**Depends:** rules/300-bash-scripting-core.md

## Purpose
Establish zsh compatibility strategies, bash migration patterns, and cross-shell scripting best practices for mixed environments, ensuring seamless transitions and portable script solutions.

## Rule Scope

Cross-shell compatibility, migration strategies, mixed environments

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Use `emulate` for compatibility** - `emulate -L bash` for bash scripts
- **Check feature availability** - Test before using shell-specific features
- **Write portable POSIX code** - Use `/bin/sh` compatible patterns
- **Document shell requirements** - Specify bash/zsh in shebang/docs
- **Test in both shells** - Verify scripts work in target environments
- **Migrate incrementally** - Convert bash to zsh feature by feature
- **Never assume feature parity** - Bash and zsh differ significantly

**Quick Checklist:**
- [ ] Shell type clearly specified
- [ ] Compatibility tested in both shells
- [ ] POSIX-compliant where possible
- [ ] Shell-specific features documented
- [ ] Migration path defined
- [ ] Tests pass in target shell
- [ ] Fallbacks implemented

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
> 1. **Test in target shell BEFORE migration** - Verify current compatibility
> 2. **Check feature usage** - Identify bash-specific vs zsh-specific features
> 3. **Never assume behavior** - Test array indexing, string operations
> 4. **Review dependencies** - Check if scripts source other bash/zsh files
> 5. **Validate in both shells** - Ensure changes work in target environment
>
> **Anti-Pattern:**
> "Converting to zsh... (without testing in zsh first)"
> "Using bash arrays... (without checking shell type)"
>
> **Correct Pattern:**
> "Let me check compatibility in both shells first."
> [tests script in bash and zsh, identifies differences]
> "I see array indexing differs. Using zsh-compatible patterns..."

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
- [Zsh Compatibility Guide](http://zsh.sourceforge.net/Doc/Release/Compatibility.html) - Cross-shell compatibility and migration strategies
- [Bash Compatibility Mode](https://www.gnu.org/software/bash/manual/html_node/Shell-Compatibility-Mode.html) - Bash emulation and feature differences
- [POSIX Shell Standard](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html) - Portable shell scripting specification

### Related Rules
- **Zsh Core**: `rules/310-zsh-scripting-core.md`
- **Zsh Advanced Features**: `rules/310a-zsh-advanced-features.md`
- **Bash Core**: `rules/300-bash-scripting-core.md`

## 1. Bash to Zsh Migration Strategies

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

## 2. Cross-Shell Compatibility Patterns

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

## 3. Environment Detection and Adaptation

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

## 4. Testing Cross-Shell Compatibility

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

## 5. Migration Tools and Utilities

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

## 6. Best Practices for Mixed Environments

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

## 7. Performance Considerations

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
