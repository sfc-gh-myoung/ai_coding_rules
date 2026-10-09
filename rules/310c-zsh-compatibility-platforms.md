---
schema_version: v4.0
rule_version: v3.0.0
description: "Environment detection and adaptation, cross-shell testing strategies, platform-specific differences (macOS/Linux, BSD/GNU tools), performance benchmarking, and project organization for mixed-shell"
last_updated: 2026-10-06
keywords:
  - kw:cross-shell testing
  - kw:platform compatibility
  - kw:environment detection
  - kw:performance benchmarking
  - kw:BSD vs GNU
  - kw:multi-shell project organization
token_budget: ~900
context_tier: Low
depends:
  required:
    - 310b-zsh-compatibility.md  # Cross-shell compatibility patterns and shell detection
  optional:
    - 310-zsh-scripting-core.md  # Foundation zsh scripting patterns
    - 310a-zsh-advanced-features.md  # Advanced zsh features
    - 300-bash-scripting-core.md  # Foundation bash scripting patterns
---
# Zsh Compatibility: Platforms, Testing, and Performance

## Scope

**What This Rule Covers:**
Actual multi-shell/platform validation, BSD/GNU differences, runtime adaptation, benchmark evidence and test failure triage.

**When to Load This Rule:**
When testing shell compatibility, handling platform-specific commands or measuring shell performance.

## Contract

### Inputs and Prerequisites

- Explicit target shells/versions/platform matrix and compatibility guidance read.
- Safe test scripts/resources and actual external command capabilities.

### Mandatory

- Verify required binaries/version/options before syntax/runtime tests. Missing claimed platform/shell is unverified, not counted as pass or silently omitted.
- Check actual sed/stat/date flags rather than assuming every macOS/Linux binary is stock BSD/GNU. Platform label alone does not prove installed command capability.
- Cross-shell tests need a harness that parses under its own declared interpreter and reliably exits nonzero on any required failure; counters/strict arithmetic cannot mask results.
- Syntax checks do not prove runtime equivalence. Test quoting/indexing/options, file names, sourced/executed contexts, traps, cancellation and command failures.
- Shell-specific feature routing must parse safely and preserve current options/startup namespace. Do not globally enable interactive correction/auto-cd during ordinary script tests.
- Capture safe per-shell failure evidence in owned collision-safe temp files, not predictable /tmp names; redaction/cleanup preserve status and original work.
- Benchmarks use a real shared function/script definition, equivalent inputs and adequate timing precision; launching a new shell cannot call a nonexported function by name alone.
- Optimize only measured bottlenecks; no universal 100ms/1000-loop thresholds or arbitrary switch to a shell-specific implementation.
- Preserve existing project organization, separate incompatible implementations only when necessary; do not create a generic bin/lib tree unasked.

### Execution Steps

1. Read target contract, harness/source/config and actual shells/tools/platform support.
2. Verify binaries/options/capabilities and run safe per-shell syntax checks.
3. Run deterministic runtime fixtures, capture exact stdout/stderr/status and compare behavior.
4. Diagnose each failed or unavailable target, fix owned incompatibility and rerun affected checks.
5. For performance work, benchmark equivalent workloads with actual function definitions and precision, reporting distributions/limitations.
6. Document supported/tested/untested platforms and accurate final status.

### Validation

- Target binaries/options verified and every required syntax/runtime test outcome recorded.
- Harness nonzero on failure, missing targets not hidden as pass and temp logs controlled/cleaned.
- BSD/GNU path/flag and array/glob/option differences actually exercised.
- No unauthorized startup/environment/install changes or unsafe compatibility fallback.
- Benchmarks execute real equivalent code, no unsupported fastest-shell claim or impossible function invocation.
- Validation subsection contains real checks, not an empty heading followed by sibling pre-task content.

## References

- [Zsh manual](https://zsh.sourceforge.io/Doc/)
- [GNU Bash](https://www.gnu.org/software/bash/manual/)
- [POSIX shell](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- `310b-zsh-compatibility.md` for migration semantics.
