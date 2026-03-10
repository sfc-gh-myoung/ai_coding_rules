# Zsh Completion System and Prompt Engineering

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** Zsh, completion system, compinit, zstyle, hooks, precmd, preexec, prompt, PROMPT_SUBST, vcs_info, async prompt
**TokenBudget:** ~2450
**ContextTier:** Low
**Depends:** 310-zsh-scripting-core.md, 310a-zsh-advanced-features.md
**LoadTrigger:** ext:.zsh, kw:zsh-completion, kw:zsh-prompt

## Scope

**What This Rule Covers:**
Zsh completion system configuration (compinit, zstyle, custom completions), hook system (precmd, preexec, chpwd, periodic), and prompt engineering (PROMPT_SUBST, vcs_info, async prompts).

**When to Load This Rule:**
- Configuring or customizing zsh tab completion
- Writing custom completion functions
- Setting up zsh hooks (precmd, preexec, chpwd)
- Building custom prompts with git status, colors, or async updates

## References

### Dependencies

**Must Load First:**
- **310-zsh-scripting-core.md** - Foundation zsh scripting patterns
- **310a-zsh-advanced-features.md** - Advanced features and optimization

**Related:**
- **310b-zsh-compatibility.md** - Cross-shell compatibility strategies

### External Documentation

- [Zsh Completion System](https://zsh.sourceforge.net/Doc/Release/Completion-System.html) - Official completion documentation
- [Zsh Line Editor (ZLE)](https://zsh.sourceforge.net/Doc/Release/Zsh-Line-Editor.html) - Advanced line editing features

## Contract

### Inputs and Prerequisites

- Zsh 5.0+ environment (5.8+ recommended)
- Understanding of basic zsh scripting (from 310-zsh-scripting-core.md)
- Terminal supporting ANSI color codes for prompt customization

### Mandatory

- MUST initialize completion with `autoload -Uz compinit && compinit`
- MUST enable completion caching with `zstyle ':completion:*' use-cache on`
- MUST register hooks via `add-zsh-hook` (not by overwriting hook functions directly)
- MUST NOT run operations >100ms synchronously in prompts
- MUST use async patterns for git status and network calls in prompts

### Forbidden

- Overwriting `precmd`/`preexec` functions directly (use `add-zsh-hook` to avoid clobbering other hooks)
- Running network calls, git operations in large repos, or kubectl synchronously in prompts
- Completion functions that make API calls without caching

### Execution Steps

1. Initialize completion system with `autoload -Uz compinit && compinit`
2. Configure completion styles with `zstyle` (caching, case-insensitive, menu select)
3. Write custom completion functions using `_describe` and `compdef`
4. Register hooks with `add-zsh-hook` for precmd, preexec, and chpwd
5. Set up prompt with `PROMPT_SUBST` and `vcs_info` for git integration
6. Implement async prompt updates for expensive operations
7. Test completions respond within 200ms and prompts render without lag

### Output Format

Configured zsh environment with:
- Working tab completion with caching enabled
- Hooks registered via `add-zsh-hook`
- Responsive prompt with async git status

### Validation

**Success Criteria:**
- Tab completion responds within 200ms
- Prompts render without perceptible lag (<100ms)
- Hooks execute without blocking the shell
- Custom completions work for target commands

### Post-Execution Checklist

- [ ] Completion system initialized with caching
- [ ] Custom completions tested for target commands
- [ ] Hooks registered via `add-zsh-hook` (not direct function override)
- [ ] Prompt renders without blocking on expensive operations
- [ ] Async patterns used for git status and network calls

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Overwriting Hook Functions Directly

**Problem:** Defining `precmd()` directly instead of using `add-zsh-hook`, which silently clobbers hooks registered by plugins, themes, and other configuration.

**Correct Pattern:**
```zsh
# BAD: Overwrites all other precmd hooks
precmd() { vcs_info; }

# GOOD: Adds hook without clobbering
autoload -U add-zsh-hook
add-zsh-hook precmd my_vcs_update
my_vcs_update() { vcs_info; }
```

### Anti-Pattern 2: Synchronous Expensive Prompt Operations

**Problem:** Running `git status`, `kubectl config`, or network calls synchronously in precmd or PROMPT, causing 200-500ms lag on every command.

**Correct Pattern:**
```zsh
# BAD: Blocks shell for 200-500ms each command
precmd() { PROMPT="$(git branch --show-current) $ "; }

# GOOD: Cache with TTL
typeset -g _git_cache="" _git_cache_time=0
_update_git() {
    local now=$(date +%s)
    (( now - _git_cache_time > 5 )) && {
        _git_cache=$(git branch --show-current 2>/dev/null)
        _git_cache_time=$now
    }
}
add-zsh-hook precmd _update_git
```

## Output Format Examples

> See **310-zsh-scripting-core.md** for the foundational zsh script template.

```zsh
# Validate zsh syntax
zsh -n script.zsh
```

## Zsh Completion System

### Completion System Setup
- **Rule:** Initialize and configure the completion system:
```zsh
# Initialize completion system
autoload -Uz compinit
compinit

# For compinit failure recovery (corrupt cache, missing dump file), see
# 310a-zsh-advanced-features.md § Error Recovery — covers cache rebuild
# with `rm -f ~/.zcompdump*` and `compinit -C` fallback.

# Enable completion caching for performance
# Ensure cache directory exists
[[ -d ~/.zsh/cache ]] || mkdir -p ~/.zsh/cache

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

## Prompt Engineering

### Dynamic Prompt Components
- **Rule:** Create sophisticated prompts:
```zsh
# Enable prompt substitution
setopt PROMPT_SUBST

# Git status in prompt
# Load vcs_info with fallback prompt if unavailable
autoload -Uz vcs_info 2>/dev/null || {
    PROMPT='%n@%m:%~%# '
    return
}
zstyle ':vcs_info:*' enable git
zstyle ':vcs_info:git:*' formats ' (%b%u%c)'
zstyle ':vcs_info:git:*' actionformats ' (%b|%a%u%c)'
zstyle ':vcs_info:git:*' check-for-changes true
zstyle ':vcs_info:git:*' unstagedstr '*'
zstyle ':vcs_info:git:*' stagedstr '+'

# Register vcs_info update via add-zsh-hook (NEVER override precmd directly)
_my_vcs_update() {
    vcs_info
}
add-zsh-hook precmd _my_vcs_update

# Custom prompt with colors and git info
PROMPT='%F{blue}%n@%m%f:%F{cyan}%~%f${vcs_info_msg_0_}%# '

# Right prompt with additional info
RPROMPT='%F{yellow}[%D{%H:%M:%S}]%f'

# Conditional prompt elements
prompt_status() {
    local status=""
    (( $(jobs | wc -l) > 0 )) && status+="[jobs]"
    [[ -n "$status" ]] && echo " $status"
}

RPROMPT='$(prompt_status)%F{yellow}[%D{%H:%M:%S}]%f'
```

### Async Prompt Updates
- **Rule:** Implement async prompts:
```zsh
async_git_status() {
    [[ -d .git ]] || return
    local tmpfile="${XDG_RUNTIME_DIR:-/tmp}/git_status_$$"
    local status=$(git status --porcelain 2>/dev/null | wc -l)
    echo "$status" > "$tmpfile"
}

# Cleanup trap — register once at shell startup
trap 'rm -f "${XDG_RUNTIME_DIR:-/tmp}/git_status_$$"' EXIT

# In precmd hook:
_async_prompt_update() {
    async_git_status &
    disown  # Prevent "job table full" and zombie processes
}
add-zsh-hook precmd _async_prompt_update
```
