---
schema_version: v4.0
rule_version: v5.0.0
description: "Foundational Go development practices using idiomatic patterns, modern tooling (Go 1.22+), and industry-standard conventions to ensure reliable, maintainable, and performant Go codebases."
last_updated: 2026-10-06
keywords:
  - kw:go.mod
  - kw:idiomatic Go
  - kw:goroutines channels
  - kw:golangci-lint
  - kw:table-driven tests
  - kw:error wrapping fmt.Errorf
  - kw:golang
token_budget: ~1000
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
  optional:
    - 600a-golang-patterns.md  # HTTP server patterns, graceful shutdown, advanced Go patterns
---
# Go Core: Idiomatic Development

## Scope

**What This Rule Covers:**
Go modules, small interfaces, explicit errors/context, bounded concurrency, resource cleanup and real formatting/static/test evidence.

**When to Load This Rule:**
When modifying Go source, modules, error/concurrency design or Go validation/testing.

## Contract

### Inputs and Prerequisites

- Actual go.mod/toolchain/workspace, source/callers/tests and lint/CI configuration.
- Supported platforms/race capability, approved dependency/network scope and resource lifetimes.

### Mandatory

- Follow existing package/layout and module path. cmd/internal are useful conventions, pkg is optional; third-party project-layout repositories are not official universal Go standards.
- Use idiomatic names, useful zero values and small consumer-side interfaces. Accept interfaces/return concrete types when useful, not an absolute ban on interface returns.
- Handle or explicitly justify ignored errors. Wrap relevant errors with fmt.Errorf %w and use errors.Is/As for inspection; don't panic for expected library errors or hide them in blank assignments.
- Export sentinels/types only when callers need that public contract; unexported errors are valid implementation details. Don't invent public APIs merely for lint.
- Context is first parameter for cancellable I/O, with propagation/timeouts and no stored request-context globals. Resource acquisition/initialization explicit rather than init network/file side effects.
- Every goroutine has known termination/ownership, bounded concurrency and handled errors; context cancellation/select must unblock waits. Sending side/coordinator closes channels only when no sender can remain.
- Shared mutable state needs ownership/locking or safe channels; channels are not universally preferable. Avoid goroutine leaks, double close and unbounded buffers.
- Close responses/files/rows/transactions and handle relevant cleanup errors; panic recovery only at intended boundaries, not a blanket library substitute for returning errors.
- Run gofmt, go vet, configured golangci-lint and actual tests; race tests when supported/required and coverage under project threshold. Race pass checks exercised paths, not proof no race exists anywhere.
- Inspect actual lint version/config before applying examples. go mod tidy can mutate files/download; only run under scope and review go.mod/go.sum diffs. No automatic latest toolchain/dependency upgrades.

### Execution Steps

1. Read module/toolchain/source/tests/lint config and verify actual environment/caller contracts.
2. Implement minimal typed idiomatic behavior with explicit errors/resources/context and cohesive package responsibility.
3. Define concurrency ownership/termination/backpressure and tests for failure/cancellation paths.
4. Run configured formatting/static checks, focused tests then required full/race/coverage gates; benchmark only for demonstrated performance questions.
5. Review module/check diffs and report actual platform/race/test limitations, no publication or dependency upgrades unasked.

### Validation

- gofmt/static/lint/tests pass under actual toolchain; public exports documented and errors meaningful.
- Module path/support and dependency hashes coherent, no unexplained tidy/version churn.
- Context cancellation/resource cleanup and concurrent error paths tested; no goroutine leaks or unsynchronized mutable state.
- Table-driven/subtests used where useful with clear assertions; coverage/race scope and unavailable platform gaps reported.
- No hidden init side effects, expected-error panic or secret-bearing logs.

## References

- [Go documentation](https://go.dev/doc/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go modules](https://go.dev/ref/mod)
- [Go race detector](https://go.dev/doc/articles/race_detector)
- [Go code review comments](https://go.dev/wiki/CodeReviewComments)
- [golangci-lint](https://golangci-lint.run/)
