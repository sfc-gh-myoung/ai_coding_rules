---
schema_version: v4.0
rule_version: v3.0.0
description: "Zsh completion system configuration (compinit, zstyle, custom completions), hook system (precmd, preexec, chpwd, periodic), and prompt engineering (PROMPT_SUBST, vcs_info, async prompts)."
last_updated: 2026-10-06
keywords:
  - kw:compinit
  - kw:zstyle completion
  - kw:add-zsh-hook
  - kw:precmd preexec
  - kw:vcs_info
  - kw:async prompt
token_budget: ~900
context_tier: Low
depends:
  required:
    - 310-zsh-scripting-core.md  # Foundation zsh scripting patterns
  optional:
    - 310a-zsh-advanced-features.md  # Advanced features and optimization
---
# Zsh Completion System and Prompt Engineering

## Scope

**What This Rule Covers:**
Secure completion initialization, custom completions, non-clobbering hooks and responsive lifecycle-managed prompts.

**When to Load This Rule:**
When configuring compinit/zstyle/compdef, hooks, vcs_info or async prompt components.

## Contract

### Inputs and Prerequisites

- Actual interactive zsh/version/terminal/config/plugin context and zsh core guidance read.
- Approved completion/cache roots and any network/destination authority.

### Mandatory

- Initialize compinit deliberately after trusted fpath configuration; preserve security audits, avoid repeated plugin initialization and do not bypass checks with -C after a failure.
- Completion cache only where useful/supported, with restrictive owned paths, valid data/TTL and no forced API call on every Tab.
- Use add-zsh-hook to register/unregister namespaced functions; do not overwrite precmd/preexec/chpwd/periodic hooks owned by others. Reloading config must not duplicate registrations.
- Completion functions define actual supported subcommands/flags/paths, handle cursor/quoting/empty input and use documented _describe/_arguments/compdef facilities.
- Keep prompt work bounded; cache or asynchronously compute expensive Git/network status with actual cancellation/refresh/lifecycle. Cache alone does not make a blocking command asynchronous.
- No predictable shared /tmp job files, unbounded background/disowned processes or stale result overwriting current directory state. Track job/ownership and update prompt through appropriate ZLE/event mechanism.
- PROMPT_SUBST and terminal escapes require trust/escaping; never evaluate untrusted path/Git/API content as prompt code or emit arbitrary terminal control sequences.
- Avoid special/read-only variable names such as status. Preserve original command status before prompt helpers; errors/debug logging must not leak secrets or record raw command history without explicit privacy approval.
- Use actual PERIOD/periodic semantics, not invented option names. Do not launch package-update/network checks as an unsolicited periodic hook.

### Execution Steps

1. Read current interactive config/hooks/completion definitions and actual runtime support.
2. Initialize trusted completion once, configure focused zstyle/custom completion and safe cache behavior.
3. Register scoped named hooks, keeping other plugins/status intact and reload idempotent.
4. Implement bounded cached/async prompt updates only for measured slow work, with cleanup and stale-result protection.
5. Run syntax plus interactive tests for completion, quoting, redraw, status preservation, directory changes and failure/cancellation.

### Validation

- Completion security/availability verified and commands/flags complete, no network surprise on Tab.
- Existing hooks preserved, duplicate registration absent, actual exit status retained.
- Prompt redraw/context/job lifecycle correct, no temp race/unbounded process or untrusted evaluation.
- Actual responsiveness measured where needed, not certified from fixed thresholds; unavailable interactive checks disclosed.
- No unapproved startup/cache deletion/network/logging effects.

## References

- [Zsh completion system](https://zsh.sourceforge.io/Doc/Release/Completion-System.html)
- [Zsh line editor](https://zsh.sourceforge.io/Doc/Release/Zsh-Line-Editor.html)
- [Zsh hook functions](https://zsh.sourceforge.io/Doc/Release/Functions.html)
- [Zsh prompt expansion](https://zsh.sourceforge.io/Doc/Release/Prompt-Expansion.html)
