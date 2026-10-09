---
schema_version: v4.0
rule_version: v5.0.0
description: "JSDoc for JavaScript public APIs: accurate TypeScript-compatible types, behavioral documentation, project-configured linting and optional checkJs validation."
last_updated: 2026-10-07
keywords:
  - kw:JSDoc type annotations
  - kw:eslint-plugin-jsdoc
  - kw:@ts-check validation
  - kw:@param @returns tags
  - kw:@typedef custom types
  - kw:JavaScript API documentation
token_budget: ~1000
context_tier: High
depends:
  required:
    - 420-javascript-core.md  # JavaScript foundation and modern patterns
  optional:
    - 434-typescript-docs.md  # TSDoc patterns (TypeScript doesn't need type annotations)
---
# JavaScript Documentation and JSDoc

## Scope

**What This Rule Covers:**
JSDoc comments for JavaScript modules, functions, classes, typedefs and callbacks; type annotations consumed by TypeScript's checker; eslint-plugin-jsdoc; `// @ts-check` and `checkJs`.

**When to Load This Rule:**
When writing or reviewing JavaScript documentation or JSDoc-based type checking; use `434-typescript-docs.md` for `.ts` sources, which carry types in syntax.

## Contract

### Inputs and Prerequisites

- Existing source, documentation conventions, public API surface (exports, package entry points) and any generated-docs pipeline.
- Installed lint/type tooling and config (ESLint version and config format, eslint-plugin-jsdoc, TypeScript, jsconfig/tsconfig) and the project's lint/check commands.

### Mandatory

- Read the code and existing docs first. Document observed behavior, not intended or guessed behavior; inaccurate types or descriptions are worse than none.
- Document the public API: exported functions, classes, constructors, methods and published typedefs, describing purpose, parameters, return value, thrown errors, side effects and non-obvious constraints or units.
- In JavaScript files, give `@param`, `@returns` and `@type` tags types that match runtime behavior, using TypeScript-supported JSDoc syntax (primitive lowercase names, `object`/`Record`, unions, generics via `@template`, `import('./mod.js').Type`).
- Model optional and default parameters (`[name]` or `name=`), nullable values, rest parameters, async return values (`Promise<T>`) and callbacks (`@callback`) precisely; parameter names and order match the signature.
- Prefer named `@typedef` declarations for reused object shapes and document every property consumers rely on.
- Use `any`/`*` only where the value is genuinely unconstrained, with a reason; prefer `unknown` plus narrowing.
- Do not restate self-evident code. Comments explain why, contracts and trade-offs; remove stale or contradicting comments touched by the change.
- Use the project's existing lint integration. Add or reconfigure eslint-plugin-jsdoc (choosing a preset and rules such as `require-jsdoc` scoped to public exports) only when tooling setup is in scope; installing dependencies is a project change requiring approval.
- Enable `// @ts-check` per file or `checkJs` in jsconfig/tsconfig when the project adopts JSDoc type checking; there is no fixed file-size threshold. Fix surfaced errors rather than silencing with `@ts-ignore`; justify any `@ts-expect-error`.
- Run the project's actual lint, type check and docs generation commands; do not claim types validated or docs generated from inspection alone.

### Execution Steps

1. Read source, existing JSDoc/config and public entry points, and identify undocumented or inaccurate API documentation.
2. Add or correct JSDoc with accurate types, behavior, errors and side effects, adding typedefs for reused shapes.
3. Run available lint, `@ts-check`/`checkJs` type check and docs generation, fixing reported issues.
4. Report documented symbols, tooling changes, commands run with results and remaining gaps.

### Validation

- Public symbols documented with accurate types matching signatures and runtime behavior.
- Types use TypeScript-compatible JSDoc syntax; `any`/suppressions justified.
- No redundant, stale or contradictory comments in touched code.
- Project lint and type checks pass, or failures and unverified areas are reported.

## References

- [JSDoc](https://jsdoc.app/)
- [TypeScript JSDoc reference](https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html)
- [Type checking JavaScript files](https://www.typescriptlang.org/docs/handbook/type-checking-javascript-files.html)
- [eslint-plugin-jsdoc](https://github.com/gajus/eslint-plugin-jsdoc)
