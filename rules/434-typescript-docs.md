---
schema_version: v4.0
rule_version: v5.0.0
description: "TSDoc for TypeScript public APIs: semantic documentation without duplicated types, accurate behavior and project-configured lint/doc tooling."
last_updated: 2026-10-07
keywords:
  - kw:TSDoc
  - kw:eslint-plugin-jsdoc
  - kw:TypeScript documentation
  - kw:type self-documenting
  - kw:semantic documentation
  - kw:public API documentation
token_budget: ~900
context_tier: High
depends:
  required:
    - 430-typescript-core.md  # TypeScript foundation and type patterns
  optional:
    - 424-javascript-docs.md  # JSDoc patterns (JavaScript requires type annotations)
---
# TypeScript Documentation and TSDoc

## Scope

**What This Rule Covers:**
TSDoc comments for exported TypeScript functions, classes, interfaces, type aliases and modules; release/deprecation tags; eslint-plugin-jsdoc and TypeDoc/API Extractor integration.

**When to Load This Rule:**
When writing or reviewing TypeScript documentation; use `424-javascript-docs.md` for `.js` sources that need JSDoc types.

## Contract

### Inputs and Prerequisites

- Existing source, documentation conventions, public API surface (package exports, entry points) and any TypeDoc/API Extractor pipeline.
- Installed lint/doc tooling and config (ESLint version and config format, eslint-plugin-jsdoc, tsdoc config) and the project's lint/build/docs commands.

### Mandatory

- Read the code and existing docs first. Document observed behavior; inaccurate or stale documentation is worse than none.
- Document public API symbols whose purpose, constraints, units, side effects, errors or lifecycle are not evident from names and types. Trivial exports with self-explanatory signatures may stay undocumented unless the project or a release tool requires coverage.
- Never repeat types in doc comments: no `{type}` in `@param`/`@returns`/`@throws`, no `@type` or `@typedef`; types belong in TypeScript syntax.
- Use TSDoc syntax: `@param name - description` matching signature names, `@returns`, `@throws` naming the error and condition, `@remarks`, `@example`, `{@link}`, `@see`, `@deprecated` with replacement, and release tags (`@public`, `@beta`, `@internal`) only where the project's tooling uses them.
- `@example` content is correct, uses current API names and does not include secrets or real identifiers; keep examples short.
- Document interface members and union variants that carry semantic meaning, defaults that the implementation actually applies and async/cancellation behavior.
- Comments explain why, contracts and trade-offs; do not restate code. Update or remove comments made stale by the change.
- Use the project's existing lint integration; eslint-plugin-jsdoc's TypeScript presets disable type-requiring rules. Add or reconfigure plugins, tsdoc config or doc generators only when tooling setup is in scope; installing dependencies requires approval.
- Run the project's actual lint, type check and docs/API report commands; do not claim validated docs from inspection alone.

### Execution Steps

1. Read source, existing doc comments, tooling config and public entry points, and identify missing, redundant or inaccurate docs.
2. Add or correct TSDoc focused on semantics, errors, side effects and deprecation, removing duplicated types.
3. Run available lint, type check and documentation/API extraction, fixing reported issues.
4. Report documented symbols, tooling changes, commands run with results and remaining gaps.

### Validation

- Non-obvious public API behavior documented; parameter names match signatures.
- No type annotations, `@type` or `@typedef` in TypeScript doc comments.
- Examples, defaults and deprecations accurate; no stale comments in touched code.
- Project lint/type/docs commands pass, or failures and unverified areas are reported.

## References

- [TSDoc](https://tsdoc.org/)
- [TSDoc tags](https://tsdoc.org/pages/tags/param/)
- [eslint-plugin-jsdoc](https://github.com/gajus/eslint-plugin-jsdoc)
- [TypeDoc](https://typedoc.org/)
- [API Extractor](https://api-extractor.com/)
