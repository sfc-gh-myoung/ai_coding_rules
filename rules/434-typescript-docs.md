# TypeScript Documentation and TSDoc

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-04-11
**Keywords:** TypeScript, TSDoc, documentation, eslint-plugin-jsdoc, API docs, type documentation
**TokenBudget:** ~3600
**ContextTier:** High
**Depends:** 430-typescript-core.md
**LoadTrigger:** kw:tsdoc, kw:documentation, kw:comments, ext:.ts, ext:.tsx

## Scope

**What This Rule Covers:**
TSDoc-based documentation standards for TypeScript projects. Covers doc comment syntax, eslint-plugin-jsdoc configuration for TypeScript, API documentation patterns, and when documentation adds value vs. when types are self-documenting.

**When to Load This Rule:**
- Writing or reviewing TypeScript documentation
- Setting up documentation standards for a TypeScript project
- Configuring eslint-plugin-jsdoc for TypeScript
- Documenting public APIs and libraries

## References

### Dependencies

**Must Load First:**
- **430-typescript-core.md** - TypeScript foundation and type patterns

**Related:**
- **424-javascript-docs.md** - JSDoc patterns (JavaScript requires type annotations)

### External Documentation

- [TSDoc](https://tsdoc.org/) - Microsoft's doc comment standard for TypeScript
- [eslint-plugin-jsdoc](https://github.com/gajus/eslint-plugin-jsdoc) - ESLint rules for JSDoc/TSDoc
- [TypeDoc](https://typedoc.org/) - Documentation generator for TypeScript
- [API Extractor](https://api-extractor.com/) - Microsoft's API documentation tool

## Contract

### Inputs and Prerequisites

- TypeScript 5.0+ project
- ESLint 9+ with flat config
- `eslint-plugin-jsdoc` for documentation linting

### Mandatory

- **Use TSDoc syntax** - `@param`, `@returns`, `@throws`, `@remarks`, `@example`
- **Document public APIs** - Exported functions, classes, interfaces, type aliases
- **Do NOT duplicate type information** - Types are in code; document semantics only
- **Enable eslint-plugin-jsdoc** - Use `flat/recommended-typescript` preset

### Forbidden

- Type annotations in doc comments (`@param {string} name` - types belong in code)
- Missing documentation for exported APIs
- Comments that restate code without adding context
- `@type` tags (use TypeScript type annotations)
- `@typedef` in TypeScript (use `type` or `interface`)

### Execution Steps

1. Install eslint-plugin-jsdoc: `npm install -D eslint-plugin-jsdoc`
2. Configure ESLint with TypeScript preset (see Configuration below)
3. Add TSDoc comments to all exported symbols
4. Document parameters by name (no types needed)
5. Document return values with semantic meaning
6. Run `npx eslint .` to validate

### Output Format

- TSDoc comments following Microsoft's TSDoc standard
- Comments explaining intent and trade-offs
- ESLint configuration with jsdoc plugin

### Validation

**Success Criteria:**
- `npx eslint .` passes all jsdoc rules
- All exported symbols have documentation
- Documentation explains semantics, not types

**During-Execution Checks:**
- Verify each doc comment adds value beyond type signature

### Design Principles

- **Types document themselves** - Don't repeat what TypeScript already knows
- **Semantic depth** - Document behavior, constraints, side effects
- **TSDoc standard** - Follow Microsoft's specification for tooling compatibility
- **Public API focus** - Internal code needs less documentation

### Post-Execution Checklist

- [ ] eslint.config.js has jsdoc plugin with TypeScript preset
- [ ] All exported functions have doc comments
- [ ] All exported classes/interfaces have doc comments
- [ ] No type annotations in doc comments
- [ ] Side effects explicitly documented
- [ ] `npx eslint .` passes jsdoc rules

## ESLint Configuration

```javascript
// eslint.config.js
import jsdoc from 'eslint-plugin-jsdoc';

export default [
  jsdoc.configs['flat/recommended-typescript'],
  {
    rules: {
      // TypeScript provides types - don't require them in docs
      'jsdoc/require-param-type': 'off',
      'jsdoc/require-returns-type': 'off',
      
      // Require docs for public APIs
      'jsdoc/require-jsdoc': ['warn', {
        publicOnly: true,
        require: {
          FunctionDeclaration: true,
          MethodDefinition: true,
          ClassDeclaration: true,
          ArrowFunctionExpression: false,
          FunctionExpression: false,
        },
      }],
      
      // Ensure param names match function signature
      'jsdoc/check-param-names': 'error',
      'jsdoc/check-tag-names': 'error',
    },
  },
];
```

**Key difference from JavaScript config:** The `flat/recommended-typescript` preset automatically disables type-related rules since TypeScript provides type information.

## TSDoc Syntax Reference

### Basic Tags

**@param** - Document parameter (no type needed)
- Example: `@param name - The user's display name`

**@returns** - Document return value
- Example: `@returns The created user object`

**@throws** - Document exceptions
- Example: `@throws Error if validation fails`

**@remarks** - Additional details
- Example: `@remarks This method is idempotent`

**@example** - Usage example (see examples below)

**@see** - Cross-reference
- Example: `@see {@link UserService}`

**@deprecated** - Mark as deprecated
- Example: `@deprecated Use newMethod instead`

### TSDoc vs JSDoc Differences

**Type annotations:**
- JSDoc: `@param {string} name`
- TSDoc: Not needed (types in code)

**Links:** Same syntax (`{@link Foo}`)

**Inline tags:**
- JSDoc: Limited
- TSDoc: `{@inheritDoc}`, `{@label}`

**Modifiers:**
- JSDoc: None
- TSDoc: `@public`, `@internal`, `@virtual`

## Documentation Patterns

### Function Documentation

```typescript
/**
 * Fetch user by unique identifier.
 *
 * @param userId - Stable UUID identifier for the user
 * @param options - Optional fetch configuration
 * @returns The user object with populated profile
 * @throws UserNotFoundError if the user does not exist
 * @throws PermissionError if caller lacks read access
 *
 * @example
 * ```typescript
 * const user = await fetchUser('123e4567-e89b-12d3-a456-426614174000');
 * console.log(user.name);
 * ```
 */
export async function fetchUser(
  userId: string,
  options?: FetchOptions
): Promise<User> {
  // Implementation
}
```

**Key points:**
- No `{string}` type in `@param` - TypeScript provides this
- Parameter description after dash: `@param name - description`
- `@throws` documents error conditions
- `@example` with fenced code block

### Class Documentation

```typescript
/**
 * Service for managing user CRUD operations.
 *
 * @remarks
 * This service caches user lookups for 5 minutes. Cache is invalidated
 * on any write operation.
 *
 * @example
 * ```typescript
 * const service = new UserService(database);
 * const user = await service.getById('user-123');
 * ```
 */
export class UserService {
  /**
   * Create a new UserService instance.
   *
   * @param db - Database connection instance
   * @param cacheTtl - Cache timeout in seconds (default: 300)
   */
  constructor(
    private readonly db: Database,
    private readonly cacheTtl: number = 300
  ) {}

  /**
   * Retrieve a user by their unique identifier.
   *
   * @param id - User's unique identifier
   * @returns User object or null if not found
   */
  async getById(id: string): Promise<User | null> {
    // Implementation
  }
}
```

### Interface Documentation

```typescript
/**
 * Configuration options for the API client.
 *
 * @remarks
 * All timeout values are in milliseconds.
 */
export interface ApiClientOptions {
  /** Base URL for all API requests */
  baseUrl: string;
  
  /** Request timeout in milliseconds (default: 30000) */
  timeout?: number;
  
  /** Number of retry attempts for failed requests (default: 3) */
  retries?: number;
  
  /**
   * Custom headers to include with every request.
   * Authorization headers are added automatically.
   */
  headers?: Record<string, string>;
}
```

### Type Alias Documentation

```typescript
/**
 * Possible states for an async operation.
 *
 * @remarks
 * Use with discriminated union pattern for type-safe state handling.
 */
export type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };
```

## When Documentation Adds Value

### Document These (High Value)

1. **Public API exports** - Entry points consumers will use
2. **Complex generics** - Type parameters with constraints
3. **Side effects** - I/O, mutations, network calls
4. **Non-obvious behavior** - Edge cases, gotchas
5. **Business logic** - Domain concepts not evident from types

```typescript
/**
 * Calculate prorated subscription cost.
 *
 * @remarks
 * Uses calendar-day proration (not 30-day month). Minimum charge is $1.
 * Refunds are calculated at the original subscription rate, not current.
 */
export function calculateProratedCost(
  subscription: Subscription,
  cancelDate: Date
): Money {
  // Types are clear; business rules are not
}
```

### Skip Documentation (Types Suffice)

```typescript
// Self-documenting - types explain everything
export function add(a: number, b: number): number {
  return a + b;
}

// Self-documenting - clear from types
export interface Point {
  x: number;
  y: number;
}

// Self-documenting - getter with obvious purpose
get isActive(): boolean {
  return this.status === 'active';
}
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Duplicating Types

```typescript
// BAD: Redundant type information
/**
 * @param {string} name - The name
 * @param {number} age - The age
 * @returns {User} The user
 */
function createUser(name: string, age: number): User
```

**Problem:** Type annotations in doc comments duplicate TypeScript's type system. This creates maintenance burden and can become stale.

**Correct Pattern:**
```typescript
/**
 * Create a new user account.
 *
 * @param name - Display name (2-50 characters)
 * @param age - Age in years (must be 13+)
 * @returns Newly created user with generated ID
 */
function createUser(name: string, age: number): User
```

### Anti-Pattern 2: Restating the Obvious

```typescript
// BAD: No value added
/**
 * Gets the user ID.
 * @returns The user ID.
 */
get userId(): string { return this._userId; }
```

**Problem:** Documentation that simply restates what the code already shows adds noise without value. IDEs already show the type signature.

**Correct Pattern:**
```typescript
/** Stable identifier persisted across sessions. */
get userId(): string { return this._userId; }
// Or skip documentation entirely for trivial getters
```

### Anti-Pattern 3: Stale Documentation

```typescript
// BAD: Signature changed, docs didn't
/**
 * @param userId - The user ID
 * @param role - The role to assign  // WRONG - parameter removed!
 */
function getUser(userId: string, options?: GetOptions): Promise<User>
```

**Problem:** Documentation that doesn't match the actual signature is worse than no documentation. It misleads developers and causes bugs.

**Correct Pattern:**
```typescript
/**
 * @param userId - The user ID
 * @param options - Optional fetch configuration
 */
function getUser(userId: string, options?: GetOptions): Promise<User>
// ESLint's jsdoc/check-param-names rule catches this automatically
```

## Side Effects Documentation

Always document side effects explicitly:

```typescript
/**
 * Save user preferences to persistent storage.
 *
 * @param prefs - User preference object
 *
 * @remarks
 * Side Effects:
 * - Writes to localStorage under 'user-prefs' key
 * - Triggers 'prefsChanged' event on window
 * - Sends analytics event to tracking service
 *
 * @throws QuotaExceededError if localStorage is full
 */
export function savePreferences(prefs: UserPreferences): void {
  // Implementation
}
```

## Module Documentation

```typescript
/**
 * Authentication utilities for the application.
 *
 * @remarks
 * This module handles JWT token management, session persistence,
 * and OAuth2 flow integration.
 *
 * Public API:
 * - {@link authenticate} - Primary login function
 * - {@link refreshToken} - Token refresh flow
 * - {@link AuthContext} - React context for auth state
 *
 * @example
 * ```typescript
 * import { authenticate, AuthContext } from './auth';
 *
 * const user = await authenticate(credentials);
 * ```
 *
 * @packageDocumentation
 */
```

## Tooling Integration

### TypeDoc Generation

```bash
# Install TypeDoc
npm install -D typedoc

# Generate documentation
npx typedoc --entryPoints src/index.ts --out docs
```

### API Extractor (for libraries)

```json
// api-extractor.json
{
  "mainEntryPointFilePath": "<projectFolder>/dist/index.d.ts",
  "docModel": {
    "enabled": true,
    "apiJsonFilePath": "<projectFolder>/temp/api.json"
  }
}
```

## Common ESLint Issues

**`jsdoc/require-jsdoc`** - Missing doc on export
- Fix: Add TSDoc comment

**`jsdoc/check-param-names`** - Param name mismatch
- Fix: Sync doc with signature

**`jsdoc/no-types`** - Type in `@param`
- Fix: Remove `{type}` annotation

**`jsdoc/require-returns`** - Missing `@returns`
- Fix: Add return description

**`jsdoc/check-tag-names`** - Invalid tag
- Fix: Use TSDoc tags only
