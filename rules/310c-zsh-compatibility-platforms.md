# Zsh Compatibility: Platforms, Testing, and Performance

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Zsh, shell testing, multi-shell, environment detection, platform compatibility, performance benchmarking, BSD vs GNU, cross-shell testing
**TokenBudget:** ~2400
**ContextTier:** Low
**Depends:** 310b-zsh-compatibility.md
**LoadTrigger:** ext:.zsh, kw:zsh-platform, kw:zsh-testing

## Scope

**What This Rule Covers:**
Environment detection and adaptation, cross-shell testing strategies, platform-specific differences (macOS/Linux, BSD/GNU tools), performance benchmarking, and project organization for mixed-shell environments.

**When to Load This Rule:**
- Testing scripts across multiple shells
- Handling macOS vs Linux platform differences
- Benchmarking shell performance
- Organizing multi-shell projects
- Detecting and adapting to runtime environment

## References

### Dependencies

**Must Load First:**
- **310b-zsh-compatibility.md** - Cross-shell compatibility patterns and shell detection

**Related:**
- **310-zsh-scripting-core.md** - Foundation zsh scripting patterns
- **310a-zsh-advanced-features.md** - Advanced zsh features
- **300-bash-scripting-core.md** - Foundation bash scripting patterns

### External Documentation

- [Zsh Compatibility FAQ](https://zsh.sourceforge.net/FAQ/zshfaq03.html) - Official FAQ on compatibility issues
- [POSIX Shell Specification](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html) - Portable shell scripting standards

## Contract

### Inputs and Prerequisites

- Scripts requiring cross-shell or cross-platform testing
- Access to both bash and zsh for multi-shell testing
- Understanding of `detect_shell` utility from 310b-zsh-compatibility.md

### Mandatory

- MUST test scripts in both bash and zsh before claiming compatibility
- MUST use `detect_shell` (from 310b) for environment-specific configuration
- MUST NOT assume GNU or BSD tool behavior without checking `$OSTYPE`
- MUST handle missing shell binaries gracefully in test harnesses

### Forbidden

- Assuming GNU `sed`/`stat`/`date` behavior on macOS (BSD tools differ)
- Skipping cross-shell testing for scripts claiming compatibility
- Blocking on expensive operations in performance-critical paths without benchmarking

### Execution Steps

1. Set up multi-shell test harness with `require_shell` checks
2. Run syntax checks (`bash -n`, `zsh -n`) before execution tests
3. Test environment detection with `detect_shell` from 310b
4. Configure shell-specific settings via `configure_shell`
5. Benchmark performance-critical functions across target shells
6. Organize project with shell-specific directories for non-portable code
7. Document compatibility requirements and test results

### Output Format

Tested, platform-aware scripts with:
- Multi-shell test results (PASS/FAIL per shell)
- Performance benchmarks for critical paths
- Platform-annotated code where BSD/GNU differences exist

### Validation

**Success Criteria:**
- Scripts pass syntax and runtime tests in all target shells
- Environment detection correctly identifies shell and platform
- Performance benchmarks show acceptable results for target workloads
- Project structure separates portable and shell-specific code

### Post-Execution Checklist

- [ ] Multi-shell tests pass (zsh, bash, sh as applicable)
- [ ] Environment detection works on target platforms
- [ ] Performance benchmarks documented
- [ ] Platform-specific code annotated with `$OSTYPE` checks
- [ ] Project structure follows multi-shell organization pattern

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Assuming GNU Tools on macOS

**Problem:** Using GNU-specific flags (`sed -i`, `stat -c`, `date -d`) in scripts intended for macOS, where BSD versions of these tools have different syntax.

**Correct Pattern:**
```zsh
# BAD: GNU-only sed (fails on macOS)
sed -i 's/old/new/' file.txt

# GOOD: Portable sed (works on both)
sed -i.tmp 's/old/new/' file.txt && rm -f file.txt.tmp

# GOOD: Platform-aware wrapper
portable_sed_i() {
    if [[ "$OSTYPE" == darwin* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}
```

### Anti-Pattern 2: No Multi-Shell Testing

**Problem:** Claiming "compatible with bash and zsh" without actually testing in both. Scripts that work in one shell often fail silently in the other due to subtle syntax differences.

**Correct Pattern:**
```zsh
# GOOD: Always test in both shells before shipping
for shell in zsh bash; do
    command -v "$shell" >/dev/null || continue
    "$shell" -n script.sh && "$shell" script.sh
done
```

## Output Format Examples

```zsh
# Validate cross-shell compatibility
shellcheck --shell=bash script.sh
zsh -n script.zsh
bash -n script.sh
```

## Environment Detection and Adaptation

### Shell-Specific Configuration
- **Rule:** Use `detect_shell` (from 310b-zsh-compatibility.md) to configure per-shell settings:
```zsh
# Apply shell-specific settings -- uses canonical detect_shell
configure_shell() {
    case "$(detect_shell)" in
        zsh)
            setopt AUTO_CD CORRECT HIST_VERIFY
            zmodload zsh/complist 2>/dev/null
            ;;
        bash)
            shopt -s autocd cdspell histverify 2>/dev/null
            [[ -f /etc/bash_completion ]] && source /etc/bash_completion
            ;;
    esac
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
    has_feature "extended_glob" && enable_extended_globbing
    has_feature "associative_arrays" && setup_config_system
    has_feature "parameter_flags" && setup_advanced_text_processing
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

### Missing Shell Binaries
- **Rule:** Detect and handle missing shells before testing:
```zsh
require_shell() {
    local shell="$1"
    command -v "$shell" >/dev/null 2>&1 || {
        echo "ERROR: $shell not found. Install it or skip $shell tests." >&2
        return 1
    }
}
```

### Cross-Shell Test Failure Triage
- **Rule:** When multi-shell tests fail, identify which shell and why:
```zsh
run_multi_shell_tests_with_recovery() {
    local script="$1" failed_shells=()
    for shell in zsh bash sh; do
        require_shell "$shell" || continue
        if ! "$shell" -n "$script" 2>/dev/null; then
            echo "$shell: SYNTAX ERROR -- run: $shell -n $script" >&2
            failed_shells+=("$shell")
        elif ! "$shell" "$script" 2>/tmp/shell_err_$$; then
            echo "$shell: RUNTIME FAIL -- see /tmp/shell_err_$$" >&2
            failed_shells+=("$shell")
        else
            echo "$shell: PASS"
        fi
    done
    if (( ${#failed_shells[@]} > 0 )); then
        echo "Failed shells: ${failed_shells[*]}"
        echo "Fallback: restrict shebang to passing shells only"
        return 1
    fi
}
```

## Best Practices for Mixed Environments

### Project Structure
- **Rule:** Organize for multi-shell support:
```text
project/
├── bin/
│   └── script.sh          # Portable main script
├── lib/
│   ├── common.sh          # Shared functions
│   ├── zsh/               # Zsh-specific libraries
│   └── bash/              # Bash-specific libraries
└── tests/                 # Shell-specific tests
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

## Performance Considerations

### Shell-Specific Optimizations
- **Rule:** Use zsh-specific features when loop iterations exceed 10,000, script runtime exceeds 5 seconds, or input files exceed 100MB:
```zsh
# Performance-aware function selection
fast_string_processing() {
    local input="$1"
    if [[ -n "$ZSH_VERSION" ]]; then
        echo "${input:u}"           # zsh parameter expansion (fastest)
    elif [[ -n "$BASH_VERSION" ]] && (( BASH_VERSINFO[0] >= 4 )); then
        echo "${input^^}"           # bash 4.0+ (fast)
    else
        echo "$input" | tr '[:lower:]' '[:upper:]'  # POSIX fallback (slowest)
    fi
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
