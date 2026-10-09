---
schema_version: v4.0
rule_version: v5.0.0
description: "Comprehensive guidance on zsh's advanced features including modules, parameter expansion, globbing, performance optimization, caching, and advanced scripting patterns."
last_updated: 2026-10-06
keywords:
  - kw:zsh modules
  - kw:async prompt operations
  - kw:completion caching
  - kw:zprof startup profiling
  - kw:glob qualifiers
  - kw:parameter expansion back-references
token_budget: ~900
context_tier: Low
depends:
  required:
    - 310-zsh-scripting-core.md  # Foundation zsh scripting patterns
  optional:
    - 310b-zsh-compatibility.md  # Cross-shell compatibility strategies
    - 310d-zsh-completion-prompt.md  # Completion system, hooks, and prompt engineering
---
# Zsh Advanced Features and Optimization

## Scope

**What This Rule Covers:**
Lazy modules, advanced expansion/globs, controlled caching, profiling and safe completion/prompt recovery.

**When to Load This Rule:**
When actual zsh performance/module/advanced-expansion needs arise, not merely to add startup complexity.

## Contract

### Inputs and Prerequisites

- Zsh core read, actual version/modules/options and current config/plugins.
- Measured startup/operation baseline and approved cache/network/resource scope.

### Mandatory

- Load only required available modules and document feature/lifetime effects. Module absence is a capability gap, not permission to create a function masquerading as a special parameter.
- Profile zprof/function timings before optimizing and compare equivalent conditions; fixed100/200ms goals are UX targets only when explicitly adopted, not universal proof.
- Prefer bounded streaming for large data, not always whole-file array loads. Measure memory/time and preserve exact line/argument semantics.
- Advanced glob/back-reference/parameter flags require deliberate options/version tests; don't evaluate untrusted strings as patterns/commands or assume units/sort qualifiers from names.
- Caches have semantic keys, TTL/invalidation, restrictive collision-safe paths and atomic validated writes. Preserve last known-good data on refresh failure; -s/nonempty alone does not prove correctness or safety to source.
- Never source cached data or untrusted plugins merely because they exist; validate trusted code roots/ownership/scope and keep data parsing distinct from code execution.
- Prompt/hooks must stay responsive; expensive network/Git work is cached/bounded/asynchronous when needed, not every prompt. Use established lifecycle-managed async facilities rather than spawning/disowning unlimited jobs.
- compinit recovery must preserve security checks and current owned cache. Do not use compinit -C to bypass insecure completion paths or blanket-delete ~/.zcompdump* without approval.
- Hook errors retain true status and are isolated through validated registered functions, not eval-generated wrappers. Do not overwrite another hook/plugin or log secrets with XTRACE.

### Execution Steps

1. Inspect modules/options/config and measure actual performance/capability problem.
2. Apply focused lazy module/expansion/glob or cache changes with explicit inputs/invalidation.
3. Review cache/code trust, completion security and async job cleanup/backpressure.
4. Run zsh syntax/runtime/error tests and reprofile equivalent workloads.
5. Document actual improvement, unavailable features and safe fallback without unsupported fastest/zero-lag claims.

### Validation

- Required modules only, options local and actual expansion/glob semantics tested.
- Cache identities/permissions/atomicity/invalidation accurate, no data source/eval injection or discarded good evidence.
- Completion security preserved, hooks/status/async lifetime and cancellation safe.
- Profiling observed before/after with same workload; no arbitrary unconditional performance guarantee.
- Syntax/behavior tests fail nonzero on failures and secrets absent from traces.

## References

- [Zsh modules](https://zsh.sourceforge.io/Doc/Release/Zsh-Modules.html)
- [Zsh expansion](https://zsh.sourceforge.io/Doc/Release/Expansion.html)
- [Zsh completion](https://zsh.sourceforge.io/Doc/Release/Completion-System.html)
- `310d-zsh-completion-prompt.md` for completion/hook lifecycle.
