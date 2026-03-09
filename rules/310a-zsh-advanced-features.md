# Zsh Advanced Features and Optimization

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-03-09
**Keywords:** Zsh, modules, advanced features, performance optimization, parameter expansion, globbing, autoload, scripting, caching, memoization
**TokenBudget:** ~3500
**ContextTier:** Low
**Depends:** 310-zsh-scripting-core.md
**LoadTrigger:** ext:.zsh, kw:zsh-advanced

## Scope

**What This Rule Covers:**
Comprehensive guidance on zsh's advanced features including modules, parameter expansion, globbing, performance optimization, caching, and advanced scripting patterns.

**When to Load This Rule:**
- Optimizing zsh performance and startup time
- Using advanced parameter expansion or globbing qualifiers
- Loading and configuring zsh modules
- Implementing caching or memoization patterns
- Writing advanced scripting patterns (state machines, plugins)

## References

### Dependencies

**Must Load First:**
- **310-zsh-scripting-core.md** - Foundation zsh scripting patterns

**Related:**
- **310b-zsh-compatibility.md** - Cross-shell compatibility strategies
- **310d-zsh-completion-prompt.md** - Completion system, hooks, and prompt engineering

### External Documentation

- [Zsh Completion System](https://zsh.sourceforge.net/Doc/Release/Completion-System.html) - Official completion documentation
- [Zsh Modules](https://zsh.sourceforge.net/Doc/Release/Zsh-Modules.html) - Available modules and their functions
- [Zsh Line Editor (ZLE)](https://zsh.sourceforge.net/Doc/Release/Zsh-Line-Editor.html) - Advanced line editing features

## Contract

### Inputs and Prerequisites

- Zsh environment requiring advanced features
- Understanding of basic zsh scripting (from 310-zsh-scripting-core.md)
- Access to zsh version 5.0 or later (5.8+ recommended) with module support
- Performance profiling goals or completion requirements

### Mandatory

- Initialize completion system with `autoload -Uz compinit && compinit`
- Load modules selectively (only what's needed)
- Implement hooks correctly (precmd, preexec)
- Cache completions for performance
- Profile startup time with zprof
- Use async operations for prompt commands taking >100ms (git status, kubectl, network calls)

### Forbidden

- Loading modules not required by current script functionality (impacts startup and memory)
- Running operations >100ms synchronously in prompts (git status in large repos, network calls, kubectl context)
- Complex logic in completion functions without caching
- Blocking operations in hooks
- Ignoring startup time performance

### Execution Steps

1. Profile current zsh startup time with `zprof` to establish baseline
2. Initialize completion system with proper caching configuration
3. Load only required zsh modules (check with `zmodload` list)
4. Implement hooks (precmd, preexec) with async operations for expensive tasks
5. Write or configure custom completions with caching for external data
6. Optimize prompt rendering with cached expensive operations
7. Re-profile startup time and verify improvements
8. Test completions and hooks work correctly

### Output Format

Optimized zsh configuration satisfying all Mandatory items, plus:
- Custom completions with TTL caching
- Profiling results showing startup time <100ms
- Error recovery for compinit and module load failures

### Validation

**Success Criteria:**
- `zprof` shows improved startup time (target <100ms)
- Completions work correctly and respond quickly
- Hooks execute without perceptible lag (response time <200ms)
- Prompt updates without blocking
- No modules loaded beyond those required by current script functionality

### Design Principles

- **Performance First:** Optimize for fast startup and responsive shell
- **Async by Default:** Never block on expensive operations
- **Cache Aggressively:** Cache completions and expensive computations
- **Load Lazily:** Load modules and completions only when needed
- **Profile Continuously:** Measure performance impact of changes

### Post-Execution Checklist

- [ ] All Mandatory and Success Criteria items verified
- [ ] Completions cached with TTL
- [ ] Error recovery tested (compinit rebuild, module fallback, hook isolation)
- [ ] Performance targets met (`zprof` <100ms startup, hooks <200ms)

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Overloading Prompt with Expensive Operations

**Problem:** Running slow commands (git status, kubectl context, network calls) synchronously in PROMPT or precmd hooks, causing noticeable lag on every command.

**Why It Fails:** Every Enter keypress triggers expensive operations. Shell becomes sluggish in large git repos. Users disable features to regain speed. Productivity loss compounds over time.

**Correct Pattern:**
```zsh
# BAD: Synchronous expensive operations
precmd() {
    PROMPT="$(git branch --show-current) $(kubectl config current-context) $ "
    # Blocks shell for 200-500ms on each command
}

# GOOD: Async prompt with caching
# Use powerlevel10k or starship with async git
# Or implement manual caching
typeset -g _git_branch_cache=""
typeset -g _git_branch_cache_time=0

_update_git_branch() {
    local now=$(date +%s)
    if (( now - _git_branch_cache_time > 5 )); then
        _git_branch_cache=$(git branch --show-current 2>/dev/null)
        _git_branch_cache_time=$now
    fi
}
```

### Anti-Pattern 2: Complex Logic in Completion Functions

**Problem:** Writing completion functions with expensive computations, API calls, or file system scans that run on every Tab press.

**Why It Fails:** Tab completion becomes slow. Users type full commands instead of completing. Completions timeout or return stale data. Shell appears frozen during completion.

**Correct Pattern:**
```zsh
# BAD: API call on every completion
_my_cli_complete() {
    local items=$(curl -s https://api.example.com/items)  # Network call on Tab!
    _describe 'items' items
}

# GOOD: Cache completions with TTL
_my_cli_complete() {
    local cache_file="${XDG_CACHE_HOME:-$HOME/.cache}/my_cli_completions"
    local cache_ttl=300  # 5 minutes

    if [[ ! -f "$cache_file" ]] || \
       (( $(date +%s) - $(stat -f%m "$cache_file") > cache_ttl )); then  # macOS; use stat -c%Y on Linux
        curl -s https://api.example.com/items > "$cache_file"
    fi

    local items=("${(@f)$(cat "$cache_file")}")
    _describe 'items' items
}
```

## Output Format Examples

> See **310-zsh-scripting-core.md** for the foundational zsh script template.

```zsh
# Validate zsh syntax
zsh -n script.zsh
```

## Zsh Completion, Hooks, and Prompts

> For the completion system (compinit, zstyle, custom completions), hook system (precmd, preexec, chpwd, periodic), and prompt engineering (PROMPT_SUBST, vcs_info, async prompts), see **310d-zsh-completion-prompt.md**.

## Advanced Parameter Expansion

> For foundational parameter expansion (case modification, basename/dirname, array filtering), see **310-zsh-scripting-core.md § Parameter Expansion Features**.
> This section covers only advanced patterns beyond the core rule.

```zsh
# Back-reference pattern replacement (advanced)
path="/usr/local/bin/command"
echo "${path/(#b)(*\/)(*)/$match[2] in $match[1]}"  # command in /usr/local/bin/

# Multiple pattern matching with back-references
text="The quick brown fox"
echo "${text//(#b)([aeiou])/${(U)match[1]}}"  # Uppercase vowels
```

## Zsh Modules and Built-in Extensions

### Mathematical Functions
- **Rule:** Use zsh math capabilities:
```zsh
zmodload zsh/mathfunc

# Mathematical operations
result=$(( sin(3.14159/2) ))
power=$(( pow(2, 8) ))
random=$(( rand48() ))

# Array statistics
numbers=(1 5 3 9 2)
sum=$(( ${(j:+:)numbers} ))
average=$(( sum / ${#numbers} ))
```

### System and Network Modules
- **Rule:** Use system modules:
```zsh
zmodload zsh/system zsh/net/tcp 2>/dev/null

# Basic system operations
sysopen -w fd /tmp/output.txt
syswrite -o $fd "Hello"
sysclose $fd
```

### Error Recovery for Advanced Features

```zsh
# compinit failure recovery (corrupt cache or missing dump)
autoload -Uz compinit
if ! compinit -d "${ZSH_COMPDUMP:-$HOME/.zcompdump}" 2>/dev/null; then
    print -u2 "compinit failed; rebuilding completion dump"
    command rm -f "${ZSH_COMPDUMP:-$HOME/.zcompdump}"
    compinit -C  # Recreate from scratch, skip security check
fi

# zmodload error handling with fallback
if ! zmodload zsh/datetime 2>/dev/null; then
    print -u2 "zsh/datetime unavailable; falling back to date(1)"
    EPOCHSECONDS() { date +%s; }
fi

if ! zmodload zsh/mathfunc 2>/dev/null; then
    print -u2 "zsh/mathfunc unavailable; math functions disabled"
fi

# Hook failure recovery — isolate errors so one bad hook
# does not break the prompt or shell
_safe_hook_wrapper() {
    local hook_fn="$1"
    if ! "$hook_fn" 2>/dev/null; then
        print -u2 "hook $hook_fn failed (exit $?); removing to prevent loop"
        add-zsh-hook -d precmd "$hook_fn"
    fi
}

# Register a hook with automatic failure isolation
safe_add_precmd_hook() {
    local fn="$1"
    eval "_wrapped_${fn}() { _safe_hook_wrapper ${fn}; }"
    add-zsh-hook precmd "_wrapped_${fn}"
}
```

## Advanced Globbing and File Operations

> For basic extended globbing (`EXTENDED_GLOB`, recursive search, exclusion), see **310-zsh-scripting-core.md § Zsh Globbing and Pattern Matching**.
> This section covers glob qualifiers for file metadata filtering.

```zsh
setopt EXTENDED_GLOB NULL_GLOB

# File age qualifiers
recent_files=(*(m-1))          # Modified within last day
old_files=(*(m+30))            # Modified more than 30 days ago

# File size qualifiers
large_files=(*(Lm+100))        # Larger than 100MB
empty_files=(*(L0))            # Empty files

# Complex qualifier combinations
log_files=(logs/**/*.log(Nm-7Lm+1))  # Last 7 days, >1MB

# Sorting qualifiers
newest_first=(*(om))           # Sort by modification time (newest first)
largest_first=(*(OL))          # Sort by size (largest first)

# Numeric ranges in patterns
chapters=(chapter<1-20>.txt)   # Matches chapter1.txt through chapter20.txt
```

## Performance Optimization Techniques

### Efficient Data Processing
- **Rule:** Optimize for large data sets (>10,000 lines or >10MB):
```zsh
# Fast file reading into arrays
large_array=(${(f)"$(< large_file.txt)"})  # Read entire file at once

# Efficient string processing
process_lines() {
    local line
    while IFS= read -r line; do
        # Process line without creating subshells
        case "$line" in
            \#*) continue ;;              # Skip comments
            *=*) process_config "$line" ;; # Process config
            *) process_data "$line" ;;     # Process data
        esac
    done < "$1"
}

# Memory-efficient large file processing
process_large_file() {
    local file="$1"
    local -i count=0

    # Use read builtin instead of external commands
    while IFS= read -r line; do
        (( ++count ))

        # Progress indicator every 10000 lines
        (( count % 10000 == 0 )) && echo "Processed $count lines" >&2

        # Process line
        process_line "$line"
    done < "$file"
}
```

### Caching and Memoization
- **Rule:** Implement caching for expensive operations:
```zsh
# Simple memoization
typeset -A cache

memoized_function() {
    local key="$*"

    if [[ -n ${cache[$key]} ]]; then
        echo "${cache[$key]}"
        return 0
    fi

    # Expensive computation
    local result=$(expensive_computation "$@")
    cache[$key]="$result"
    echo "$result"
}

# File-based caching with expiration
cached_command() {
    local cache_file="/tmp/cache_${1//\//_}"
    local max_age=3600  # 1 hour

    if [[ -f "$cache_file" ]] && (( $(date +%s) - $(stat -c%Y "$cache_file") < max_age )); then  # Linux; use stat -f%m on macOS
        cat "$cache_file"
        return 0
    fi

    # Run command and cache result
    "$@" | tee "$cache_file"
}
```

> **Portable stat:** Use `stat -f%m` on macOS/BSD and `stat -c%Y` on Linux. For cross-platform scripts:
> ```zsh
> file_mtime() { [[ "$OSTYPE" == darwin* ]] && stat -f%m "$1" || stat -c%Y "$1"; }
> ```

## Advanced Scripting Patterns

### Advanced Patterns
- **Rule:** Extract into functions when: (1) code exceeds 50 lines, (2) nesting exceeds 3 levels, (3) branches exceed 5 conditionals, or (4) cyclomatic complexity > 10:
```zsh
# Simple state machine
typeset -A states=(idle "start" running "finish")
current_state="idle"

run_state_machine() {
    while [[ "$current_state" != "complete" ]]; do
        ${states[$current_state]} || break
    done
}

# Plugin system
typeset -A plugins
load_plugin() {
    local plugin="$1" file="~/.zsh/plugins/$plugin.zsh"
    [[ -f "$file" ]] && source "$file" && plugins[$plugin]="$file"
}
```

## Testing and Debugging Advanced Features

### Advanced Debugging Techniques
- **Rule:** Use zsh debugging capabilities:
```zsh
# Function tracing
setopt XTRACE VERBOSE

# Trace specific functions
functions -T my_function

# Debug with custom PS4
PS4='+%N:%i> '

# Conditional debugging
debug_mode=${DEBUG:-false}

debug_log() {
    [[ "$debug_mode" == "true" ]] && echo "[DEBUG] $*" >&2
}

# Performance profiling
profile_function() {
    local func="$1"
    shift

    zmodload zsh/datetime
    local start=$EPOCHREALTIME

    $func "$@"
    local exit_code=$?

    local end=$EPOCHREALTIME
    local duration=$(( end - start ))

    echo "Function $func took ${duration}s" >&2
    return $exit_code
}
```

### Unit Testing

For zsh function testing, use `assert_equals`/`assert_contains` helpers with a `run_tests` harness that auto-discovers `test_*` functions. Key approach:
- Maintain `test_count`/`test_passed` counters via `typeset -gi`
- Iterate test functions with `${(M)${(k)functions}:#test_*}`
- Return non-zero from `run_tests` on any failure

> For comprehensive shell testing frameworks and patterns, see **300b-bash-testing-tooling.md**.
