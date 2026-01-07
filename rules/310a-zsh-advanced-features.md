# Zsh Advanced Features and Optimization

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.0
**LastUpdated:** 2026-01-06
**Keywords:** Zsh, completion system, modules, hooks, advanced features, performance optimization, compinit, zstyle, autoload, scripting
**TokenBudget:** ~5000
**ContextTier:** Low
**Depends:** 310-zsh-scripting-core.md

## Scope

**What This Rule Covers:**
Comprehensive guidance on zsh's advanced features including the completion system, modules, hooks, and performance optimization techniques to build sophisticated and efficient zsh environments.

**When to Load This Rule:**
- Implementing zsh completion system
- Optimizing zsh performance and startup time
- Using zsh hooks (precmd, preexec)
- Loading and configuring zsh modules
- Writing custom completion functions

## References

### Dependencies

**Must Load First:**
- **310-zsh-scripting-core.md** - Foundation zsh scripting patterns

**Related:**
- **310b-zsh-compatibility.md** - Cross-shell compatibility strategies

### External Documentation

- [Zsh Completion System](http://zsh.sourceforge.net/Doc/Release/Completion-System.html) - Official completion documentation
- [Zsh Modules](http://zsh.sourceforge.net/Doc/Release/Zsh-Modules.html) - Available modules and their functions
- [Zsh Line Editor (ZLE)](http://zsh.sourceforge.net/Doc/Release/Zsh-Line-Editor.html) - Advanced line editing features

## Contract

### Inputs and Prerequisites

- Zsh environment requiring advanced features
- Understanding of basic zsh scripting (from 310-zsh-scripting-core.md)
- Access to zsh version 5.0+ with module support
- Performance profiling goals or completion requirements

### Mandatory

- Initialize completion system with `autoload -Uz compinit && compinit`
- Load modules selectively (only what's needed)
- Implement hooks correctly (precmd, preexec)
- Cache completions for performance
- Profile startup time with zprof
- Use async operations for expensive prompt commands

### Forbidden

- Loading unnecessary modules (impacts performance)
- Running expensive operations synchronously in prompts
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

Optimized zsh configuration with:
- Completion system initialized with caching
- Selective module loading
- Async hooks for expensive operations
- Custom completions with TTL caching
- Profiling results showing improved startup time
- Working prompt and completion system

### Validation

**Pre-Task-Completion Checks:**
- Completion system initialized
- Modules loaded selectively
- Hooks implemented without blocking
- Completions cached appropriately
- Startup time profiled
- Async operations working

**Success Criteria:**
- `zprof` shows improved startup time (target <100ms)
- Completions work correctly and respond quickly
- Hooks execute without noticeable lag
- Prompt updates without blocking
- Custom completions functional
- No unnecessary modules loaded

### Design Principles

- **Performance First:** Optimize for fast startup and responsive shell
- **Async by Default:** Never block on expensive operations
- **Cache Aggressively:** Cache completions and expensive computations
- **Load Lazily:** Load modules and completions only when needed
- **Profile Continuously:** Measure performance impact of changes

### Post-Execution Checklist

- [ ] Completion system initialized
- [ ] Modules loaded selectively
- [ ] Hooks implemented correctly
- [ ] Completions cached with TTL
- [ ] Startup time profiled and optimized
- [ ] Custom completions working
- [ ] Prompt rendering async
- [ ] No blocking operations in hooks
- [ ] Performance targets met
- [ ] All features tested

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
       (( $(date +%s) - $(stat -f%m "$cache_file") > cache_ttl )); then
        curl -s https://api.example.com/items > "$cache_file"
    fi

    local items=("${(@f)$(cat "$cache_file")}")
    _describe 'items' items
}
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

## Zsh Completion System

### Completion System Setup
- **Rule:** Initialize and configure the completion system:
```zsh
# Initialize completion system
autoload -Uz compinit
compinit

# Enable completion caching for performance
zstyle ':completion:*' use-cache on
zstyle ':completion:*' cache-path ~/.zsh/cache

# Case-insensitive completion
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# Menu selection for completions
zstyle ':completion:*' menu select

# Group completions by type
zstyle ':completion:*' group-name ''
zstyle ':completion:*:descriptions' format '%B%d%b'
```

### Custom Completion Functions
- **Rule:** Create custom completions:
```zsh
_my_script() {
    local -a commands=(
        'start:Start service'
        'stop:Stop service'
        'status:Show status'
    )

    case $words[2] in
        start|stop) _files -g "*.conf" ;;
        *) _describe 'commands' commands ;;
    esac
}

compdef _my_script my_script
```

### Completion Styles
- **Rule:** Configure completion behavior:
```zsh
# Basic completion styles
zstyle ':completion:*' file-sort modification
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*:*:kill:*' menu yes select
zstyle ':completion:*:kill:*' force-list always
```

## Zsh Hook System

### Hook Functions
- **Rule:** Use zsh hooks for automated actions:
```zsh
# Directory change hooks
autoload -U add-zsh-hook

# Function to run when changing directories
chpwd_update_git_status() {
    if [[ -d .git ]]; then
        echo "Git repository detected"
        git status --porcelain | head -5
    fi
}

# Register hook
add-zsh-hook chpwd chpwd_update_git_status

# Pre-command hook (runs before each command)
preexec_log_command() {
    local cmd="$1"
    echo "[$(date '+%H:%M:%S')] Executing: ${cmd%% *}" >> ~/.zsh_command_log
}

add-zsh-hook preexec preexec_log_command

# Pre-prompt hook (runs before each prompt)
precmd_update_title() {
    # Set terminal title to current directory
    print -Pn "\e]0;%n@%m: %~\a"
}

add-zsh-hook precmd precmd_update_title
```

### Periodic Functions
- **Rule:** Use periodic functions for background tasks:
```zsh
# Enable periodic functions
setopt PERIODIC_FUNCTIONS

# Function that runs every N seconds
PERIOD=300  # 5 minutes

periodic() {
    # Check for system updates
    if command -v apt >/dev/null; then
        apt list --upgradable 2>/dev/null | wc -l > ~/.update_count
    elif command -v brew >/dev/null; then
        brew outdated | wc -l > ~/.update_count
    fi
}
```

## Advanced Parameter Expansion

### Complex Parameter Transformations
- **Rule:** Master zsh's parameter expansion flags:
```zsh
# String transformations
text="Hello World"
echo "${text:l}"           # lowercase: hello world
echo "${text:u}"           # uppercase: HELLO WORLD
echo "${text:c}"           # capitalize: Hello world

# Array transformations
files=(file1.txt file2.log file3.conf)
echo "${files:r}"          # Remove extensions: file1 file2 file3
echo "${files:e}"          # Extensions only: txt log conf
echo "${files:t}"          # Basenames: file1.txt file2.log file3.conf

# Numeric transformations
numbers=(1 2 3 4 5)
echo "${(j:+:)numbers}"    # Join with +: 1+2+3+4+5
echo "${(s:+:)string}"     # Split on +

# Sorting and uniqueness
items=(c a b a c)
echo "${(u)items}"         # Unique: c a b
echo "${(o)items}"         # Sort: a a b c c
echo "${(ou)items}"        # Sort unique: a b c
```

### Advanced Substitution Patterns
- **Rule:** Use sophisticated pattern matching:
```zsh
# Pattern replacement with conditions
path="/usr/local/bin/command"
echo "${path/(#b)(*\/)(*)/$match[2] in $match[1]}"  # command in /usr/local/bin/

# Multiple pattern matching
text="The quick brown fox"
echo "${text//(#b)([aeiou])/${(U)match[1]}}"  # Uppercase vowels

# Conditional replacement
version="1.2.3-beta"
stable_version="${version/%-*}"  # Remove everything after first dash

# Array pattern operations
files=(test.txt backup.txt.bak config.conf)
txt_files=(${files:#*.bak})      # Exclude .bak files
conf_files=(${(M)files:#*.conf}) # Match only .conf files
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

## Advanced Globbing and File Operations

### Recursive and Conditional Globbing
- **Rule:** Master zsh's globbing qualifiers:
```zsh
# Enable extended globbing
setopt EXTENDED_GLOB NULL_GLOB

# File age qualifiers
recent_files=(*(m-1))          # Modified within last day
old_files=(*(m+30))            # Modified more than 30 days ago
accessed_today=(*(a-1))        # Accessed today

# File size qualifiers
large_files=(*(Lm+100))        # Larger than 100MB
small_files=(*(Lk-10))         # Smaller than 10KB
empty_files=(*(L0))            # Empty files

# File type and permission qualifiers
executable_files=(*(x))        # Executable files
readable_dirs=(*(r/))          # Readable directories
writable_files=(*(w.))         # Writable regular files
symlinks=(*(N@))               # Symbolic links (NULL_GLOB)

# Complex combinations
log_files=(logs/**/*.log(Nm-7Lm+1))  # Log files modified in last 7 days, >1MB

# Sorting qualifiers
newest_first=(*(om))           # Sort by modification time (newest first)
largest_first=(*(OL))          # Sort by size (largest first)
alphabetical=(*(on))           # Sort by name
```

### Advanced Pattern Matching
- **Rule:** Use sophisticated pattern constructs:
```zsh
# Approximate matching
setopt GLOB_COMPLETE
files=(test*.txt~*backup*)     # Exclude backup files

# Case-insensitive globbing
setopt NO_CASE_GLOB
images=(*.jpg *.PNG *.gif)     # Matches any case

# Numeric ranges in patterns
chapters=(chapter<1-20>.txt)   # Matches chapter1.txt through chapter20.txt
versions=(v<1-9>.<0-9>.<0-9>)  # Version patterns

# Alternative patterns
configs=(*.{conf,cfg,ini})     # Multiple extensions
backups=(**/*.(bak|backup|~))  # Multiple backup patterns recursively
```

## Performance Optimization Techniques

### Efficient Data Processing
- **Rule:** Optimize for large data sets:
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

    if [[ -f "$cache_file" ]] && (( $(date +%s) - $(stat -c %Y "$cache_file") < max_age )); then
        cat "$cache_file"
        return 0
    fi

    # Run command and cache result
    "$@" | tee "$cache_file"
}
```

## Advanced Prompt Engineering

### Dynamic Prompt Components
- **Rule:** Create sophisticated prompts:
```zsh
# Enable prompt substitution
setopt PROMPT_SUBST

# Git status in prompt
autoload -Uz vcs_info
zstyle ':vcs_info:*' enable git
zstyle ':vcs_info:git:*' formats ' (%b%u%c)'
zstyle ':vcs_info:git:*' actionformats ' (%b|%a%u%c)'
zstyle ':vcs_info:git:*' check-for-changes true
zstyle ':vcs_info:git:*' unstagedstr '*'
zstyle ':vcs_info:git:*' stagedstr '+'

precmd() {
    vcs_info
}

# Custom prompt with colors and git info
PROMPT='%F{blue}%n@%m%f:%F{cyan}%~%f${vcs_info_msg_0_}%# '

# Right prompt with additional info
RPROMPT='%F{yellow}[%D{%H:%M:%S}]%f'

# Conditional prompt elements
prompt_status() {
    local status=""

    # Show background jobs
    (( $(jobs | wc -l) > 0 )) && status+="⚡"

    # Show load average
    local load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | tr -d ',')
    (( ${load%.*} > 2 )) && status+=""

    # Show battery status (macOS)
    if command -v pmset >/dev/null; then
        local battery=$(pmset -g batt | grep -o '[0-9]*%' | head -1)
        (( ${battery%\%} < 20 )) && status+="🔋"
    fi

    [[ -n "$status" ]] && echo " $status"
}

RPROMPT='$(prompt_status)%F{yellow}[%D{%H:%M:%S}]%f'
```

### Async Prompt Updates
- **Rule:** Implement async prompts:
```zsh
async_git_status() {
    [[ -d .git ]] || return
    local status=$(git status --porcelain 2>/dev/null | wc -l)
    echo "$status" > /tmp/git_status_$$
}

update_prompt() {
    async_git_status &
}

add-zsh-hook precmd update_prompt
```

## Advanced Scripting Patterns

### Advanced Patterns
- **Rule:** Implement complex logic patterns:
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

### Unit Testing Framework
- **Rule:** Implement testing for zsh functions:
```zsh
# Simple test framework
typeset -gi test_count=0 test_passed=0

assert_equals() {
    local expected="$1" actual="$2" message="${3:-test}"
    (( ++test_count ))

    if [[ "$expected" == "$actual" ]]; then
        echo "PASS: $message"
        (( ++test_passed ))
    else
        echo "✗ FAIL: $message"
        echo "  Expected: '$expected'"
        echo "  Actual:   '$actual'"
    fi
}

assert_contains() {
    local haystack="$1" needle="$2" message="${3:-contains test}"
    (( ++test_count ))

    if [[ "$haystack" == *"$needle"* ]]; then
        echo "PASS: $message"
        (( ++test_passed ))
    else
        echo "✗ FAIL: $message"
        echo "  String '$haystack' does not contain '$needle'"
    fi
}

run_tests() {
    echo "Running zsh tests..."

    # Reset counters
    test_count=0 test_passed=0

    # Run all test functions
    for test_func in ${(M)${(k)functions}:#test_*}; do
        echo "Running $test_func..."
        $test_func
    done

    echo
    echo "Results: $test_passed/$test_count tests passed"

    if (( test_passed == test_count )); then
        echo "All tests passed!"
        return 0
    else
        echo "Some tests failed!"
        return 1
    fi
}
```
