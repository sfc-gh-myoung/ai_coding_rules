# TypeScript Core: Strictness & Modern Patterns

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential TypeScript patterns. Load for TypeScript tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** TypeScript, Zod, Strict Mode, Type Inference, Union Types, Satisfies, Generics, Utility Types, Matt Pocock, Total TypeScript
**TokenBudget:** ~1850
**ContextTier:** High
**Depends:** rules/000-global-core.md

## Purpose
Establishes the definitive standards for writing production-grade TypeScript in 2025. This rule enforces **Strict Mode**, prioritizes **Type Inference** over manual typing, mandates **Runtime Validation** (Zod) at I/O boundaries, and explicitly forbids legacy features like Enums and Namespaces.

## Rule Scope
Applies to all TypeScript files in frontend and backend environments. Covers type definitions, generics, validation schemas, and compiler configuration.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **[Config]** - Always set `"strict": true` and `"noImplicitAny": true`.
- **[Validation]** - Define **Zod** schema first, then infer type: `type User = z.infer<typeof UserSchema>`.
- **[No Enums]** - Use **String Unions**: `type Status = 'active' | 'pending';`.
- **[No Any]** - Use `unknown` for uncertain data and narrow it.
- **[Safe Casts]** - Use `satisfies` instead of `as` whenever possible.
- **[Utilities]** - Use `Pick`, `Omit`, and `Partial` to derive types; don't duplicate them.

**Quick Checklist:**
- [ ] `tsconfig.json` has `"strict": true`
- [ ] No `enum` keywords used (replaced with object const or union)
- [ ] No explicit `any` types
- [ ] External data inputs validated with Zod
- [ ] Variables initialized without redundant type annotations
- [ ] `satisfies` used for configuration objects
## Contract

<contract>
<inputs_prereqs>
TypeScript 5.0+, Node.js 20+
</inputs_prereqs>

<mandatory>
`tsc` (checking), `zod` (validation), `ts-reset` (improved built-ins), `ts-pattern` (matching)
</mandatory>

<forbidden>
`any` (strict ban), `enum` (use unions), `namespace` (use modules), `Hungarian Notation` (no `IInterface`), `d.ts` implementation pollution.
</forbidden>

<steps>
1. **Enable Strictness:** Verify `tsconfig.json` has `"strict": true`.
2. **Validate I/O:** All external data (API responses, URL params) MUST be validated with **Zod** schemas.
3. **Narrow Unknowns:** Treat 3rd party untyped data as `unknown` and narrow via predicates or Zod.
4. **Infer Types:** Do not manually type variables if the compiler can infer them (`const x = 5` not `const x: number = 5`).
5. **Use Satisfies:** Use `satisfies` operator to validate types without widening them.
</steps>

<output_format>
`.ts` or `.tsx` files, strict typing, no errors.
</output_format>

<validation>
Run `tsc --noEmit` and check for zero errors.
</validation>

</contract>

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

## Post-Execution Checklist
- [ ] `"strict": true` is set in tsconfig
- [ ] `any` is nowhere to be found
- [ ] Zod is used for all API responses
- [ ] No `enum` definitions exist
- [ ] No `ISomething` interface names
- [ ] `satisfies` is used for config objects
- [ ] Generics have `extends` constraints where applicable

## Validation
- **Success checks:**
 - `tsc --noEmit` passes with exit code 0
 - Zod schemas match their inferred types
- **Negative tests:**
 - Assigning a string to a number variable should fail compilation
 - Accessing a property on `unknown` without narrowing should fail

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

## References

### External Documentation
- [TypeScript Handbook](https://www.typescriptlang.org/docs/) - Official docs.
- [Total TypeScript (Matt Pocock)](https://www.totaltypescript.com/) - Advanced patterns and tips.
- [Zod Documentation](https://zod.dev/) - Schema validation.
- [TS Reset](https://github.com/total-typescript/ts-reset) - Better built-in types.

### Related Rules
- **Global Core**: `rules/000-global-core.md`
- **React Core**: `rules/440-react-core.md` (TypeScript usage in React)

> ** Claude 4 Specific Guidance**
> **Claude 4 Optimizations:**
> - **Inference Mastery:** Claude is excellent at deriving types. Ask it to "infer types from this Zod schema" rather than writing them manually.
> - **Utility Types:** Claude knows `Pick`, `Omit`, `ReturnType` well. Ask it to use them to reduce duplication.
> - **Refactoring:** Ask Claude to "remove explicit types where inference is sufficient" to clean up code.

## 1. Configuration & Project Setup

### 1.1 Compiler Options
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

### 1.2 Global Resets
- **Consider:** using `@total-typescript/ts-reset` to fix standard library annoyances (like `JSON.parse` returning `any` instead of `unknown`).

## 2. Core Typing Patterns

### 2.1 Unions vs Enums
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

### 2.2 Validation & Type Inference
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

### 2.3 The `satisfies` Operator
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

## 3. Advanced Patterns

### 3.1 Generic Constraints
- **Rule:** Always constrain generics to the minimal required shape.
- **Avoid:** `T extends any` or unconstrained `T`.

```typescript
// Good: Constrained generic
function getProperty<T extends object, K extends keyof T>(obj: T, key: K) {
 return obj[key];
}
```

### 3.2 Branded Types
- **Consider:** Use "Branded Types" for primitive identifiers (IDs) to prevent mixing them up.

```typescript
declare const __brand: unique symbol;
type Brand<T, B> = T & { [__brand]: B };

type UserId = Brand<string, 'UserId'>;
type PostId = Brand<string, 'PostId'>;

const getUser = (id: UserId) => { ... };
const myId = '123' as UserId; // Explicit cast required at boundary
```
