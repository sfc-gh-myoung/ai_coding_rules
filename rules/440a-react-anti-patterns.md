---
schema_version: v4.0
rule_version: v5.0.0
description: "React anti-pattern review: data fetching, effects and cleanup, hydration safety, error/Suspense boundaries, query cache and measured performance."
last_updated: 2026-10-07
keywords:
  - kw:error boundary
  - kw:hydration mismatch
  - kw:useEffect cleanup
  - kw:TanStack Query error
  - kw:use client directive
  - kw:query cache gcTime
  - kw:tsx
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 440-react-core.md  # Core React architecture and patterns
---
# React Anti-Patterns and Recovery

## Scope

**What This Rule Covers:**
Reviewing and fixing React effect misuse, missing cleanup, hydration mismatches, error and Suspense boundary placement, TanStack Query error/cache behavior, `'use client'` errors and performance issues.

**When to Load This Rule:**
When reviewing React code for defects or diagnosing runtime, hydration, leak or performance problems; load `440-react-core.md` first.

## Contract

### Inputs and Prerequisites

- Code under review, React/framework/TanStack Query versions, rendering model and observed errors, warnings or profiles.
- Available lint (including react-hooks rules), tests, build/bundle analysis and profiling tools.

### Mandatory

- Report only defects grounded in the code or observed behavior, each with location, impact and a minimal fix.
- Effects synchronize with external systems only. Derive values during render, handle events in handlers and use framework or server-state tooling for data fetching instead of `useEffect` + `useState`.
- Effects that subscribe, start timers, add listeners or open connections return cleanup; in-flight requests are cancelled or ignored on unmount and when dependencies change (TanStack Query supplies an `AbortSignal` to `queryFn`).
- Respect react-hooks lint: complete dependency arrays and no suppressed exhaustive-deps without a documented reason.
- Use `useSyncExternalStore` (with a server snapshot) for external or browser stores.
- Avoid hydration mismatches: server and first client render produce identical output; read browser-only values (window, localStorage, time, random) after mount or in client-only components, never during server render. Use `suppressHydrationWarning` only for unavoidable single-element differences such as timestamps.
- Place error and Suspense boundaries around independently failing or loading sections; pair TanStack Query `throwOnError`/suspense queries with `QueryErrorResetBoundary` so retry resets state.
- Fix `'use client'` errors by marking the smallest interactive boundary, not whole directories or layouts that should stay on the server.
- Treat TanStack Query defaults (`gcTime` 5 minutes) as bounded; tune `gcTime`, `staleTime`, `retry` and infinite-query `maxPages` from observed data volume and freshness needs rather than fixed universal values.
- Optimize from measurement: profile, analyze bundles and virtualize long or expensive lists when profiling shows cost; do not impose fixed item-count or bundle-size thresholds without a project budget.
- Avoid unnecessary memoization and prop drilling fixes that add global state; prefer composition and colocated state.
- Verify fixes with tests that unmount during pending work, trigger errors and retries, and run the project's lint/tests/build; do not claim leak or hydration fixes without evidence.

### Execution Steps

1. Read code, versions, rendering model and any reported errors or profiles.
2. Identify grounded anti-patterns and apply minimal fixes for effects, cleanup, hydration, boundaries or caching.
3. Run lint, tests (including unmount, error and retry paths), build and available profiling.
4. Report findings with locations, fixes, evidence and remaining unverified risks.

### Validation

- No effect-based data fetching or derived state in new or changed code; cleanups present.
- Server and first client render match; browser-only values read after mount.
- Boundaries isolate failures with working retry; `'use client'` minimal.
- Cache and performance changes justified by measurement; tests and build pass or gaps reported.

## References

- [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
- [useEffect](https://react.dev/reference/react/useEffect)
- [useSyncExternalStore](https://react.dev/reference/react/useSyncExternalStore)
- [hydrateRoot](https://react.dev/reference/react-dom/client/hydrateRoot)
- [TanStack Query important defaults](https://tanstack.com/query/latest/docs/framework/react/guides/important-defaults)
- [QueryErrorResetBoundary](https://tanstack.com/query/latest/docs/framework/react/reference/QueryErrorResetBoundary)
