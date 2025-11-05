---
appliesTo:
  - "**/*.zsh"
  - "**/*.sh"
  - "scripts/**/*"
  - "**/.zshrc"
---
<!-- Generated for GitHub Copilot repository instructions. See https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions -->

**Keywords:** Shell compatibility, bash vs zsh, portable scripts, cross-shell
**Depends:** 300-bash-scripting-core

**TokenBudget:** ~1300
**ContextTier:** Low

# Zsh Compatibility and Cross-Shell Scripting

## Purpose
Establish zsh compatibility strategies, bash migration patterns, and cross-shell scripting best practices for mixed environments, ensuring seamless transitions and portable script solutions.

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Cross-shell compatibility, migration strategies, mixed environments


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
```
project/
├── bin/script.sh        # Portable main script
├── lib/
│   ├── common.sh        # Shared functions
│   ├── zsh/             # Zsh-specific
│   └── bash/            # Bash-specific
└── tests/            # Shell-specific tests
```

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

## Contract
- **Inputs/Prereqs:** [Context, files, dependencies needed]
- **Allowed Tools:** [Tools permitted for this domain]
- **Forbidden Tools:** [Tools not allowed for this domain]
- **Required Steps:** [Ordered steps the agent must follow]
- **Output Format:** [Expected output format]
- **Validation Steps:** [Checks to confirm success]

## Quick Compliance Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Response Template
```
[Minimal, copy-pasteable template showing expected output format]
```

## References

### External Documentation
- [Zsh Compatibility Guide](http://zsh.sourceforge.net/Doc/Release/Compatibility.html) - Cross-shell compatibility and migration strategies                                                                             
- [Bash Compatibility Mode](https://www.gnu.org/software/bash/manual/html_node/Shell-Compatibility-Mode.html) - Bash emulation and feature differences                                                                  
- [POSIX Shell Standard](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html) - Portable shell scripting specification

### Related Rules
- **Zsh Core**: `310-zsh-scripting-core.md`
- **Zsh Advanced Features**: `310a-zsh-advanced-features.md`
- **Bash Core**: `300-bash-scripting-core.md`
