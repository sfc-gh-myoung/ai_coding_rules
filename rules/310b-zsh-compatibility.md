# Zsh Compatibility and Cross-Shell Scripting

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**Keywords:** Zsh, shell compatibility, bash vs zsh, portable scripts, cross-shell, migration, emulate, POSIX compliance, shell detection
**TokenBudget:** ~3900
**ContextTier:** Low
**Depends:** 300-bash-scripting-core.md
**LoadTrigger:** ext:.zsh, kw:zsh-compatibility

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
- **310c-zsh-compatibility-platforms.md** - Platforms, testing, and performance

### External Documentation

- [Zsh Compatibility](https://zsh.sourceforge.net/FAQ/zshfaq03.html) - Official FAQ on compatibility issues
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
3. Choose strategy based on requirements:
   - **POSIX portable:** Use when script must run on 3+ different shells (zsh, bash, sh, dash)
   - **Emulate mode:** Use for zsh scripts that need bash library compatibility (`emulate -L sh`)
   - **Shell-specific versions:** Use when loop iterations exceed 10,000, script runtime exceeds 5 seconds, or input files exceed 100MB
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

**Why It Fails:** Scripts fail on systems where /bin/sh is dash or bash. CI/CD environments may not have zsh. Docker containers use minimal shells (sh, dash, busybox sh — shells without zsh/bash extensions). Portability broken silently.

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

**Why It Fails:** Scripts work when sourced but fail when executed. Behavior differs between users with different .zshrc configs. CI environments have different defaults. Specific problematic option mismatches: `EXTENDED_GLOB` (off by default in scripts — `*.txt~backup*` fails), `NULL_GLOB` (unmatched globs cause errors instead of expanding to nothing), `KSH_ARRAYS` (changes array indexing from 1-based to 0-based).

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

```zsh
#!/usr/bin/env zsh
# Cross-shell compatible script example
setopt ERR_EXIT PIPE_FAIL  # Explicit options (don't rely on .zshrc)

# Detect shell and adapt
if [[ -n "$ZSH_VERSION" ]]; then
    setopt EXTENDED_GLOB NULL_GLOB
elif [[ -n "$BASH_VERSION" ]]; then
    shopt -s extglob nullglob 2>/dev/null
fi

# Portable prerequisite check
for cmd in jq curl git; do
    command -v "$cmd" >/dev/null 2>&1 || {
        printf 'ERROR: Required command not found: %s\n' "$cmd" >&2
        exit 1
    }
done
```

```zsh
# Validation with shellcheck and zsh syntax check
shellcheck --shell=bash script.sh
zsh -n script.zsh
```

## Bash to Zsh Migration Strategies

### Compatibility Assessment
- **Rule:** Scan for bash-specific constructs before migration:
```zsh
# Quick compatibility scan — run against any bash script
grep -n 'declare -[aA]\|BASH_\|shopt\|\[\[.*=~\|BASH_SOURCE\|BASH_REMATCH' "$script"
```
Key constructs requiring conversion: `declare` to `typeset`, `BASH_SOURCE` to `${(%):-%x}`, `shopt` to `setopt`, `BASH_REMATCH` to `$MATCH`/`$match`.

### Migration Patterns
- **Rule:** Convert bash-specific constructs to zsh equivalents:

- `declare -a arr=()` -> `typeset -a arr=()`
- `declare -A map=()` -> `typeset -A map=()`
- `${arr[0]}` (0-based) -> `${arr[1]}` (1-based, or `setopt KSH_ARRAYS`)
- `[[ "$s" =~ pat ]]; ${BASH_REMATCH[1]}` -> `[[ "$s" =~ pat ]]; ${match[1]}`
- `${var^^}` -> `${var:u}` / `${var,,}` -> `${var:l}`
- `BASH_SOURCE[0]` -> `${(%):-%x}`

### Migration Phases
- **Rule:** Migrate gradually using emulate:
```zsh
# Phase 1: Run bash scripts under zsh with bash compatibility
emulate -L sh          # POSIX mode for maximum compat
setopt BASH_REMATCH    # Keep BASH_REMATCH behavior

# Phase 2: Convert to native zsh
emulate -L zsh
setopt EXTENDED_GLOB
```

## Cross-Shell Compatibility Patterns

### Canonical Shell Detection Utility
- **Requirement (MANDATORY):** Define `detect_shell` once and reuse it -- MUST NOT duplicate shell-detection logic:
```zsh
# Canonical shell detection — use this everywhere, do not duplicate
detect_shell() {
    if [[ -n "${ZSH_VERSION:-}" ]]; then echo "zsh"
    elif [[ -n "${BASH_VERSION:-}" ]]; then echo "bash"
    else echo "sh"
    fi
}
```

### Portable Function Writing
- **Rule:** Write functions that work in both bash and zsh using `detect_shell`:
```zsh
# Portable string manipulation using detect_shell
portable_uppercase() {
    local input="$1"
    case "$(detect_shell)" in
        zsh)  echo "${input:u}" ;;
        bash) echo "${input^^}" ;;
        *)    echo "$input" | tr '[:lower:]' '[:upper:]' ;;
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

## Environment Detection, Testing, and Error Recovery

> For environment detection and adaptation, capability-based feature loading, multi-shell testing, compatibility checking, and test failure triage, see **310c-zsh-compatibility-platforms.md**.

### Missing Shell Binaries
- **Rule:** Detect and handle missing shells before testing or migration:
```zsh
require_shell() {
    local shell="$1"
    command -v "$shell" >/dev/null 2>&1 || {
        echo "ERROR: $shell not found. Install it or skip $shell tests." >&2
        return 1
    }
}
```

### Migration Failure Recovery
- **Rule:** Always create backups; rollback on sed/conversion failures:
```zsh
# Safe sed wrapper — rolls back on failure
safe_sed() {
    local file="$1"; shift
    cp "$file" "${file}.sedbackup" || return 1
    if ! sed -i.tmp "$@" "$file"; then
        cp "${file}.sedbackup" "$file"
        echo "sed failed, restored original: $file" >&2
        return 1
    fi
    rm -f "${file}.tmp" "${file}.sedbackup"
}
```

> **Platform note:** `sed -i` differs across platforms. GNU (Linux) accepts `sed -i 's/...'` directly; BSD (macOS) requires a backup extension: `sed -i '' 's/...'`. Using `sed -i.tmp` works on both platforms (creates a `.tmp` backup file). Always use `sed -i.tmp` for portable scripts.

## Migration Tools and Utilities

### Automated Migration Commands
- **Rule:** Use concrete sed commands for bash-to-zsh conversion:
```zsh
# Step-by-step migration — run each command, review diff after each step
migrate_bash_to_zsh() {
    local src="$1"
    local dest="${2:-${src%.sh}.zsh}"

    # 1. Create backup (abort if backup fails)
    cp "$src" "${src}.backup" || { echo "Backup failed" >&2; return 1; }

    # 2. Copy to destination
    cp "$src" "$dest" || { echo "Copy failed" >&2; return 1; }

    # 3. Convert shebang
    sed -i.tmp '1s|#!/bin/bash|#!/usr/bin/env zsh|; 1s|#!/usr/bin/bash|#!/usr/bin/env zsh|' "$dest"

    # 4. Convert declare to typeset
    sed -i.tmp 's/declare -a/typeset -a/g; s/declare -A/typeset -A/g; s/declare -r/typeset -r/g' "$dest"

    # 5. Add emulate directive after shebang
    sed -i.tmp '2i\
emulate -L zsh' "$dest"

    # 6. Cleanup temp files
    rm -f "${dest}.tmp"

    # 7. Show what needs manual review
    echo "Automated conversion complete: $dest"
    echo "Manual review required for:"
    grep -n 'BASH_SOURCE\|BASH_REMATCH\|\${\!.*}\|\[\[.*=~' "$dest" 2>/dev/null \
        && echo "  (see lines above)" \
        || echo "  No additional issues found"
    echo "Run: diff '${src}.backup' '$dest'"
}
```

### Rollback on Failure
```zsh
# If migration produces broken output, restore from backup
rollback_migration() {
    local src="$1"
    if [[ -f "${src}.backup" ]]; then
        cp "${src}.backup" "$src"
        echo "Restored from backup: ${src}.backup"
    else
        echo "No backup found for $src" >&2
        return 1
    fi
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

## Best Practices and Performance

> For project structure, documentation standards, performance benchmarking, and multi-shell testing, see **310c-zsh-compatibility-platforms.md**.
