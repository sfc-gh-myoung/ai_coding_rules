# TypeScript Core: Strictness & Modern Patterns

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential TypeScript patterns. Load for TypeScript tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** TypeScript, Zod, Strict Mode, Type Inference, Union Types, Satisfies, Generics, Utility Types, Matt Pocock, Total TypeScript
**TokenBudget:** ~2600
**ContextTier:** High
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Establishes the definitive standards for writing production-grade TypeScript in 2025. This rule enforces **Strict Mode**, prioritizes **Type Inference** over manual typing, mandates **Runtime Validation** (Zod) at I/O boundaries, and explicitly forbids legacy features like Enums and Namespaces.

**When to Load This Rule:**
- Working with TypeScript files (.ts, .tsx)
- Setting up TypeScript project configuration
- Implementing type-safe validation patterns
- Refactoring JavaScript to TypeScript
- Reviewing TypeScript code for best practices

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules

**Related:**
- **440-react-core.md** - TypeScript usage in React applications
- **420-javascript-core.md** - JavaScript patterns that complement TypeScript

### External Documentation

- [TypeScript Handbook](https://www.typescriptlang.org/docs/) - Official documentation
- [Total TypeScript (Matt Pocock)](https://www.totaltypescript.com/) - Advanced patterns and tips
- [Zod Documentation](https://zod.dev/) - Schema validation library
- [TS Reset](https://github.com/total-typescript/ts-reset) - Better built-in types

## Contract

### Inputs and Prerequisites

- TypeScript 5.0+ installed
- Node.js 20+ environment
- Understanding of type systems
- Familiarity with modern JavaScript

### Mandatory

- `tsc` compiler for type checking
- `zod` library for runtime validation
- `ts-reset` for improved built-in types (recommended)
- `ts-pattern` for pattern matching (recommended)

### Forbidden

- `any` type (strict ban - use `unknown` instead)
- `enum` keyword (use string unions or const objects)
- `namespace` keyword (use ES modules)
- Hungarian Notation (no `IInterface` naming)
- Implementation code in `.d.ts` files

### Execution Steps

1. **Enable Strictness:** Verify `tsconfig.json` has `"strict": true` and `"noImplicitAny": true`
2. **Validate I/O:** All external data (API responses, URL params) MUST be validated with Zod schemas
3. **Narrow Unknowns:** Treat 3rd party untyped data as `unknown` and narrow via predicates or Zod
4. **Infer Types:** Do not manually type variables if the compiler can infer them (`const x = 5` not `const x: number = 5`)
5. **Use Satisfies:** Use `satisfies` operator to validate types without widening them
6. **Check Configuration:** Review existing `tsconfig.json` before making changes
7. **Validate Output:** Run `tsc --noEmit` to ensure zero type errors

### Output Format

TypeScript files (`.ts` or `.tsx`) with:
- Strict typing enabled
- Zero compilation errors
- Zod schemas for external data
- Type inference where possible
- No forbidden patterns

### Validation

**Pre-Task-Completion Checks:**
- `tsconfig.json` has `"strict": true`
- No `any` types in code
- Zod schemas defined for all API responses
- No `enum` definitions exist
- No `ISomething` interface names
- `satisfies` used for config objects
- Generics have `extends` constraints where applicable

**Success Criteria:**
- `tsc --noEmit` passes with exit code 0
- Zod schemas match their inferred types
- Type inference works without explicit annotations
- All external data validated at runtime

**Negative Tests:**
- Assigning string to number variable fails compilation
- Accessing property on `unknown` without narrowing fails
- Using `any` type triggers linter error

### Design Principles

- **Type Safety First:** Strict mode is non-negotiable for production code
- **Runtime Validation:** Static types alone are insufficient - validate at I/O boundaries
- **Inference Over Annotation:** Let TypeScript infer types when obvious
- **Modern Patterns Only:** Avoid legacy features like enums and namespaces
- **Composition Over Duplication:** Use utility types to derive new types

### Post-Execution Checklist

- [ ] `"strict": true` is set in tsconfig.json
- [ ] `any` is nowhere to be found in code
- [ ] Zod is used for all API responses and external data
- [ ] No `enum` definitions exist
- [ ] No `ISomething` interface names (Hungarian notation)
- [ ] `satisfies` is used for configuration objects
- [ ] Generics have `extends` constraints where applicable
- [ ] `tsc --noEmit` passes with zero errors
- [ ] Type inference used instead of explicit annotations where possible

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: The explicit `any`**
```typescript
// Bad: Disabling the type checker
function process(data: any) {
 return data.foo.bar; // Unsafe access
}
```
**Problem:** Spreads potential runtime errors throughout the app. "Type virus".

**Correct Pattern:**
```typescript
// Good: Unknown + Narrowing
import { z } from 'zod';
const Schema = z.object({ foo: z.object({ bar: z.string() }) });

function process(data: unknown) {
 const parsed = Schema.parse(data); // Validates
 return parsed.foo.bar; // Safe
}
```

**Anti-Pattern 2: The `I` Prefix (Hungarian Notation)**
```typescript
// Bad: C# style naming
interface IUserData {
 name: string;
}
```
**Problem:** Redundant. In TS, everything is a type/interface.

**Correct Pattern:**
```typescript
// Good: Clean naming
type UserData = {
 name: string;
};
```

**Anti-Pattern 3: Return Type `void` used incorrectly**
```typescript
// Bad: Misunderstanding void in callbacks
// In TS, a void returning callback can actually return a value, it just gets ignored.
```
**Problem:** Can lead to subtle bugs if you rely on return values being undefined.

**Correct Pattern:**
```typescript
// Use 'undefined' if you strictly mean "returns nothing"
type StrictCallback = () => undefined;
```

> **Investigation Required**
> When applying this rule:
> 1. **Read `tsconfig.json`** to understand strictness level and paths.
> 2. **Check for existing validation libraries** (Zod, Yup, Valibot) before introducing a new one.
> 3. **Do not blindly add types** if inference works. Read the code to see if the type is obvious.

## Output Format Examples

```markdown
MODE: PLAN

Investigation:
- Verified `tsconfig.json`: Strict mode is enabled.
- Found explicit `any` in `src/utils.ts`.
- Goal: Refactor `fetchData` to use Zod validation and strict typing.

Implementation:
Defining Zod schema for API response and inferring return types.
```

```typescript
import { z } from 'zod';

// 1. Define Schema
const ApiResponseSchema = z.object({
 data: z.array(z.object({
 id: z.number(),
 title: z.string()
 })),
 page: z.number()
});

// 2. Derive Type
type ApiResponse = z.infer<typeof ApiResponseSchema>;

// 3. Strict Implementation
export async function fetchData(url: string): Promise<ApiResponse> {
 const res = await fetch(url);
 if (!res.ok) throw new Error('Network error');

 const json: unknown = await res.json();

 // Runtime Validation
 return ApiResponseSchema.parse(json);
}
```

```bash
# Validation
npx tsc --noEmit
```

## Configuration & Project Setup

### Compiler Options
- **Requirement:** Strict mode is non-negotiable.
- **Recommendation:** Use `skipLibCheck: true` to avoid breaking on broken 3rd party types.

```json
// tsconfig.json
{
 "compilerOptions": {
 "target": "ES2022",
 "lib": ["DOM", "DOM.Iterable", "ESNext"],
 "module": "ESNext",
 "strict": true,
 "noImplicitAny": true,
 "strictNullChecks": true,
 "skipLibCheck": true,
 "moduleResolution": "bundler",
 "resolveJsonModule": true,
 "isolatedModules": true,
 "noEmit": true
 }
}
```

### Global Resets
- **Use** `@total-typescript/ts-reset` to fix standard library annoyances (like `JSON.parse` returning `any` instead of `unknown`).

## Core Typing Patterns

### Unions vs Enums
- **Rule:** DO NOT use `enum`. They add runtime code and have nominal typing quirks.
- **Correct Pattern:** Use String Unions or `as const` objects.

```typescript
// Bad: Legacy Enum
enum Status {
 Active,
 Inactive
}

// Good: String Union (Preferred)
type Status = 'active' | 'inactive';

// Good: Constant Object (If values needed at runtime)
const STATUS = {
 Active: 'active',
 Inactive: 'inactive'
} as const;
type StatusType = typeof STATUS[keyof typeof STATUS];
```

### Validation & Type Inference
- **Requirement:** Define the source of truth in Zod (runtime), then derive the static type.

```typescript
import { z } from 'zod';

// 1. Define Schema (Runtime)
export const UserSchema = z.object({
 id: z.string().uuid(),
 username: z.string().min(3),
 email: z.string().email(),
 role: z.enum(['admin', 'user', 'guest']), // Zod enum is safe
});

// 2. Infer Type (Compile time)
export type User = z.infer<typeof UserSchema>;

// 3. Validate Input
function createUser(input: unknown) {
 const user = UserSchema.parse(input); // Throws if invalid
 return user; // Type is User
}
```

### The `satisfies` Operator
- **Rule:** Use `satisfies` to ensure an object matches a type without widening it (preserving exact values).

```typescript
type Routes = Record<string, { path: string; protected: boolean }>;

// Bad: Type annotation loses literal values
// const routes: Routes = { ... }

// Good: Checks structure but keeps 'home' as literal key
const routes = {
 home: { path: '/', protected: false },
 dashboard: { path: '/dash', protected: true }
} satisfies Routes;

// TS knows routes.home.path is exactly '/'
```

## Advanced Patterns

### Generic Constraints
- **Rule:** Always constrain generics to the minimal required shape.
- **Avoid:** `T extends any` or unconstrained `T`.

```typescript
// Good: Constrained generic
function getProperty<T extends object, K extends keyof T>(obj: T, key: K) {
 return obj[key];
}
```

### Branded Types
- **Use** "Branded Types" for primitive identifiers (IDs) to prevent mixing them up.

```typescript
declare const __brand: unique symbol;
type Brand<T, B> = T & { [__brand]: B };

type UserId = Brand<string, 'UserId'>;
type PostId = Brand<string, 'PostId'>;

const getUser = (id: UserId) => { ... };
const myId = '123' as UserId; // Explicit cast required at boundary
```
