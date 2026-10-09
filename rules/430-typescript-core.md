---
schema_version: v4.0
rule_version: v5.0.0
description: "Establishes the definitive standards for writing production-grade TypeScript in 2026. This rule enforces Strict Mode, prioritizes Type Inference over manual typing, mandates Runtime Validation (Zod)"
last_updated: 2026-10-06
keywords:
  - kw:strict mode enforcement
  - kw:Zod runtime validation
  - kw:type inference over annotation
  - kw:enum namespace forbidden
  - kw:satisfies operator
  - kw:discriminated union patterns
token_budget: ~1000
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 434-typescript-docs.md  # TSDoc documentation standards
    - 440-react-core.md  # TypeScript usage in React applications
    - 420-javascript-core.md  # JavaScript patterns that complement TypeScript
---
# TypeScript Core: Strictness and Modern Patterns

## Scope

**What This Rule Covers:**
Strict static checking, external-data validation, inference/narrowing, discriminated unions and deliberate configuration/library contracts.

**When to Load This Rule:**
When modifying .ts/.tsx, tsconfig, typed boundaries or JavaScript-to-TypeScript migration.

## Contract

### Inputs and Prerequisites

- Actual tsconfig/compiler/runtime/framework and package lock/tooling.
- Existing validation library, public interfaces and authorized migration scope.

### Mandatory

- Use strict checking for new production TypeScript and preserve project strictness. Existing strict migration must be staged/approved with each error resolved, not disabled globally to pass.
- Treat external JSON/form/URL/storage data as unknown and validate at trust boundaries with the established schema/predicate library. Zod is an option, not automatic permission to add/replace dependencies.
- Avoid authored any and unsafe casts; narrow unknown, model nullability and use specific justified temporary ts-expect-error instead of blanket ts-ignore. Third-party any requires a contained boundary, not rewriting vendor declarations blindly.
- Prefer inferred local types and explicit public contracts where useful. Use satisfies to check shape without a type annotation, but do not claim it automatically preserves every string literal; use as const when exact readonly literal semantics are intended.
- Prefer string unions/const objects and ES modules in new application code over enums/namespaces. Preserve required declaration augmentation/library compatibility; .d.ts contains declarations, not implementation.
- Use discriminated unions for variant outcomes, exhaustive branching and generic constraints only for operations actually required. Unconstrained generics are valid when no shape is needed.
- Derive static types from runtime schemas where appropriate; branded IDs need validated creation, not casts that manufacture evidence of validity.
- Respect actual Node/bundler moduleResolution/lib/target settings. skipLibCheck or global reset packages are deliberate compatibility choices with coverage implications, not mandatory setup defaults.
- Handle parse failures deliberately with parse/throw or safeParse/result according to API contract. Capture async errors as unknown and normalize explicitly; PromiseRejectedResult.reason can be any in standard declarations, not magically unknown under strict mode.
- Cancellable fetch/streaming work needs AbortController/timeout cleanup and fully handled outcomes. Do not lose partial failures or leak resources in typed wrappers.

### Execution Steps

1. Read tsconfig/manifests/source/tests and current validator/library convention before changing types/config.
2. Implement focused strict public contracts, inference and unknown-data validation/narrowing.
3. Define variant/generic/error/cancellation semantics and deliberate third-party compatibility boundaries.
4. Run the project's compiler/type checks (such as tsc --noEmit), lint/format and regression tests under actual runtime/build settings.
5. Review runtime schemas against static types and disclose unavailable runtime checks; no false correctness claim from compiler success alone.

### Validation

- Configured strict type check passes with no new unsafe any/casts/blanket suppression.
- External data runtime validation matches documented schema and types; malformed/null inputs handled.
- Public interfaces/union exhaustive cases/generics align with callers and actual compiler behavior.
- Module/runtime/lib settings and third-party augmentation deliberate, no speculative reset package or validator install.
- Async failure/cancellation resources tested, actual lint/format/types/tests pass and unavailable checks disclosed.

## References

- [TypeScript handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [TypeScript tsconfig](https://www.typescriptlang.org/tsconfig/)
- [TypeScript satisfies](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
- [TypeScript narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [Zod](https://zod.dev/)
