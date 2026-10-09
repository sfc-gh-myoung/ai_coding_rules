---
schema_version: v4.0
rule_version: v5.0.0
description: "Modern JS in 2026: ECMAScript Modules, immutable ES2023+ methods, JSDoc type annotations, and Biome/node:test tooling."
last_updated: 2026-10-06
keywords:
  - kw:ESM modules
  - kw:immutable array methods
  - kw:node:test runner
  - kw:Biome linter
  - kw:JSDoc type annotations
  - kw:Object.groupBy
token_budget: ~1000
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns and validation gates
  optional:
    - 424-javascript-docs.md  # JSDoc documentation standards
    - 440-react-core.md  # React-specific patterns and best practices
---
# JavaScript Core: Modern Standards

## Scope

**What This Rule Covers:**
Runtime-compatible modules, nonmutating data handling, asynchronous failures, validated boundaries and project-configured JavaScript tooling.

**When to Load This Rule:**
When modifying JavaScript, async/module code, JSDoc checking or runtime/tool configuration.

## Contract

### Inputs and Prerequisites

- Actual package.json/lockfile, runtime/browser support, module mode and current lint/test tools.
- Existing callers/types/bundler/import paths and authorized dependency/network scope.

### Mandatory

- Inspect runtime and module mode before coding. Prefer ESM for new compatible code; preserve deliberate CommonJS interoperability instead of changing package type across existing consumers unasked.
- Use const/let, avoid unsafe eval/dynamic execution and implicit browser globals. Namespace intentional HTML-accessible globals and preserve native history/location objects.
- Prefer nonmutating array operations where ownership requires input preservation, but verify runtime support for toSorted/toSpliced/with/groupBy. Do not impose APIs unavailable in the supported runtime or claim all Node20 supports every later ECMAScript feature.
- Use native fetch/test/assert when suitable for new code, but do not remove established Axios/test/lint dependencies without a requested migration. Match Biome/ESLint/Prettier and actual version/config.
- JSDoc/ts-check provide useful static contracts; validate external JSON at runtime rather than trusting annotations. Use actual project conventions, not arbitrary line/parameter thresholds.
- Check fetch HTTP status separately from transport success, bind/encode URL parts safely, bound timeouts/cancellation and avoid unapproved destinations.
- Await/return promises and preserve caught errors as cause when wrapping. Promise.all is appropriate for all-required work; allSettled requires explicit handling of every rejection, not silently dropping failures.
- Top-level await can delay/fail module initialization; use only deliberately, avoid import-time network/process.exit in reusable libraries and prefer explicit initialization where needed.
- Local ESM import extensions/resolution depend on actual Node/bundler/browser semantics; do not assume Node omits local .js extensions. Handle dynamic import rejection and circular-module initialization risks.
- structuredClone supports only cloneable values; verify types/transfer behavior rather than promising universal cloning or rejecting every Error object. Avoid JSON roundtrip as a generic deep copy.
- Never clear global caches, alter registries/proxies, install runtime versions or reset configs as blind recovery. Diagnose exact error and preserve unrelated work.

### Execution Steps

1. Read manifests/config/source/tests and determine runtime/module/tool support.
2. Implement minimal typed/documented APIs with deliberate input ownership and validated I/O.
3. Handle async/error/cancellation paths explicitly and preserve module compatibility.
4. Run configured lint/format/type checks and relevant tests, then required full gates.
5. Report actual runtime/platform evidence and unresolved checks; update affected usage docs without committing/installing unasked.

### Validation

- Module/import/runtime feature compatibility tested, no unsafe eval/implicit globals or unexpected import-time side effects.
- Input mutation ownership explicit, boundary data validated and fetch errors/timeouts handled.
- All promise outcomes accounted for, causes preserved and cancellation safe.
- Configured actual lint/format/tests/types pass; no unrequested tooling replacement or registry/cache mutation.
- No secrets in logs/URLs/examples and no fabricated performance/runtime claims.

## References

- [MDN JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
- [Node ESM](https://nodejs.org/api/esm.html)
- [Node test runner](https://nodejs.org/api/test.html)
- [Biome](https://biomejs.dev/)
- [TypeScript JavaScript checking](https://www.typescriptlang.org/docs/handbook/type-checking-javascript-files.html)
