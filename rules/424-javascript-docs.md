# JavaScript Documentation and JSDoc

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.2.0
**LastUpdated:** 2026-04-11
**Keywords:** JavaScript, JSDoc, documentation, eslint-plugin-jsdoc, API docs, type annotations
**TokenBudget:** ~3800
**ContextTier:** High
**Depends:** 420-javascript-core.md
**LoadTrigger:** kw:jsdoc, kw:documentation, kw:comments, ext:.js, ext:.mjs

## Scope

**What This Rule Covers:**
JSDoc-based documentation standards for JavaScript projects. Covers type annotations in doc comments, eslint-plugin-jsdoc configuration, API documentation patterns, and TypeScript-powered type checking via `// @ts-check`.

**When to Load This Rule:**
- Writing or reviewing JavaScript documentation
- Setting up documentation standards for a JavaScript project
- Configuring eslint-plugin-jsdoc
- Adding type safety to JavaScript via JSDoc
- Documenting public APIs and libraries

## References

### Dependencies

**Must Load First:**
- **420-javascript-core.md** - JavaScript foundation and modern patterns

**Related:**
- **434-typescript-docs.md** - TSDoc patterns (TypeScript doesn't need type annotations)

### External Documentation

- [JSDoc 3](https://jsdoc.app/) - De facto JavaScript documentation standard
- [eslint-plugin-jsdoc](https://github.com/gajus/eslint-plugin-jsdoc) - ESLint rules for JSDoc
- [TypeScript JSDoc Reference](https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html) - JSDoc types supported by TypeScript
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html#jsdoc)

## Contract

### Inputs and Prerequisites

- JavaScript project (ESM recommended)
- ESLint 9+ with flat config
- `eslint-plugin-jsdoc` for documentation linting
- Optional: TypeScript for `// @ts-check` validation

### Mandatory

- **Use JSDoc 3 syntax** - `@param`, `@returns`, `@throws`, `@typedef`, `@type`
- **Include type annotations** - `@param {string} name` (JavaScript has no type syntax)
- **Document public APIs** - Exported functions, classes, constructors
- **Enable eslint-plugin-jsdoc** - Use `flat/recommended` preset
- **Use `// @ts-check`** - Enable for files >100 lines or complex logic

### Forbidden

- Missing type annotations in `@param` and `@returns` tags
- Undocumented exported functions
- Comments that restate code without adding context
- `@type {any}` without justification

### Execution Steps

1. Install eslint-plugin-jsdoc: `npm install -D eslint-plugin-jsdoc`
2. Configure ESLint with JavaScript preset (see Configuration below)
3. Add JSDoc comments with type annotations to all exports
4. Enable `// @ts-check` for type validation
5. Document parameters with types and descriptions
6. Run `npx eslint .` to validate

### Output Format

- JSDoc comments with type annotations
- Comments explaining intent and trade-offs
- ESLint configuration with jsdoc plugin

### Validation

**Success Criteria:**
- `npx eslint .` passes all jsdoc rules
- All exported symbols have documentation with types
- `// @ts-check` enabled on complex files

**During-Execution Checks:**
- Verify each `@param` has a type annotation
- Verify `@returns` has a type annotation

### Design Principles

- **Types in comments** - JavaScript lacks type syntax; JSDoc provides it
- **Semantic depth** - Document behavior, constraints, side effects
- **TypeScript validation** - Use `// @ts-check` for compile-time type checking
- **Public API focus** - Internal code needs less documentation

### Post-Execution Checklist

- [ ] eslint.config.js has jsdoc plugin configured
- [ ] All exported functions have JSDoc with types
- [ ] All `@param` tags include `{type}` annotations
- [ ] `@returns` tags include `{type}` annotations
- [ ] `// @ts-check` enabled on complex files
- [ ] `npx eslint .` passes jsdoc rules

## ESLint Configuration

```javascript
// eslint.config.js
import jsdoc from 'eslint-plugin-jsdoc';

export default [
  jsdoc.configs['flat/recommended'],
  {
    rules: {
      // Require types in JSDoc (JavaScript needs them)
      'jsdoc/require-param-type': 'error',
      'jsdoc/require-returns-type': 'error',
      
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
      'jsdoc/check-types': 'error',
      'jsdoc/valid-types': 'error',
    },
  },
];
```

**Key difference from TypeScript config:** The `flat/recommended` preset requires type annotations since JavaScript has no native type syntax.

## JSDoc Syntax Reference

### Type Annotation Syntax

**`{string}`** - Primitive type
- Example: `@param {string} name`

**`{number}`** - Number type
- Example: `@param {number} age`

**`{boolean}`** - Boolean type
- Example: `@param {boolean} active`

**`{Object}`** - Object (any shape)
- Example: `@param {Object} options`

**`{Array<string>}`** or **`{string[]}`** - Array of strings
- Example: `@param {Array<string>} items`

**`{?string}`** - Nullable type
- Example: `@param {?string} name`

**`{string=}`** - Optional parameter
- Example: `@param {string=} name`

**`{*}`** - Any type
- Example: `@param {*} data`

**`{Function}`** - Function type
- Example: `@param {Function} callback`

**`{Promise<User>}`** - Promise type
- Example: `@returns {Promise<User>}`

### Basic Tags

**@param** - Document parameter with type
- Example: `@param {string} name - User's name`

**@returns** - Document return value
- Example: `@returns {User} The created user`

**@throws** - Document exceptions
- Example: `@throws {Error} If validation fails`

**@type** - Declare variable type
- Example: `/** @type {string} */`

**@typedef** - Define custom type (see examples below)

**@callback** - Define function type (see examples below)

**@example** - Usage example (code block)

**@deprecated** - Mark as deprecated
- Example: `@deprecated Use newFn instead`

## Documentation Patterns

### Function Documentation

```javascript
// @ts-check

/**
 * Fetch user by unique identifier.
 *
 * @param {string} userId - Stable UUID identifier for the user
 * @param {Object} [options] - Optional fetch configuration
 * @param {boolean} [options.includeRoles=false] - Include role memberships
 * @param {number} [options.timeout=5000] - Request timeout in milliseconds
 * @returns {Promise<User>} The user object with populated profile
 * @throws {UserNotFoundError} If the user does not exist
 * @throws {PermissionError} If caller lacks read access
 *
 * @example
 * const user = await fetchUser('123e4567-e89b-12d3-a456-426614174000');
 * console.log(user.name);
 *
 * @example
 * // With options
 * const user = await fetchUser('user-123', { includeRoles: true });
 */
export async function fetchUser(userId, options = {}) {
  // Implementation
}
```

**Key points:**
- Type in braces: `{string}`, `{Object}`, `{Promise<User>}`
- Optional parameters: `[options]` in name, or `{string=}`
- Destructured options: Document each property
- `@throws` documents error conditions

### Type Definitions

```javascript
/**
 * User account information.
 *
 * @typedef {Object} User
 * @property {string} id - Unique identifier
 * @property {string} name - Display name
 * @property {string} email - Email address
 * @property {('admin'|'user'|'guest')} role - User role
 * @property {Date} createdAt - Account creation timestamp
 */

/**
 * Fetch options for API requests.
 *
 * @typedef {Object} FetchOptions
 * @property {number} [timeout=5000] - Request timeout in milliseconds
 * @property {boolean} [includeDeleted=false] - Include soft-deleted records
 * @property {Object<string, string>} [headers] - Additional HTTP headers
 */
```

### Callback Type Definitions

```javascript
/**
 * Event handler callback.
 *
 * @callback EventHandler
 * @param {Event} event - The DOM event object
 * @param {Object} context - Handler context
 * @param {string} context.target - Target element ID
 * @returns {void}
 */

/**
 * Register an event handler.
 *
 * @param {string} eventName - Event name to listen for
 * @param {EventHandler} handler - Callback function
 * @returns {Function} Unsubscribe function
 */
export function on(eventName, handler) {
  // Implementation
  return () => off(eventName, handler);
}
```

### Class Documentation

```javascript
// @ts-check

/**
 * Service for managing user CRUD operations.
 *
 * Caches user lookups for 5 minutes. Cache is invalidated
 * on any write operation.
 *
 * @example
 * const service = new UserService(database);
 * const user = await service.getById('user-123');
 */
export class UserService {
  /**
   * Create a new UserService instance.
   *
   * @param {Database} db - Database connection instance
   * @param {number} [cacheTtl=300] - Cache timeout in seconds
   */
  constructor(db, cacheTtl = 300) {
    /** @type {Database} */
    this.db = db;
    
    /** @type {number} */
    this.cacheTtl = cacheTtl;
    
    /** @private @type {Map<string, User>} */
    this._cache = new Map();
  }

  /**
   * Retrieve a user by their unique identifier.
   *
   * @param {string} id - User's unique identifier
   * @returns {Promise<User|null>} User object or null if not found
   */
  async getById(id) {
    // Implementation
  }
}
```

### Variable Type Annotations

```javascript
// @ts-check

/** @type {string} */
const API_BASE = 'https://api.example.com';

/** @type {number} */
let retryCount = 0;

/** @type {Array<User>} */
const users = [];

/** @type {Object<string, number>} */
const scores = {};

/** @type {Map<string, User>} */
const userCache = new Map();

/** @type {Set<string>} */
const processedIds = new Set();
```

## TypeScript Type Checking with @ts-check

### Enable Type Checking

```javascript
// @ts-check

/**
 * @param {number} a
 * @param {number} b
 * @returns {number}
 */
function add(a, b) {
  return a + b;
}

// TypeScript error: Argument of type 'string' is not assignable to parameter of type 'number'
add('1', 2); // Error caught!
```

### Import Types from TypeScript

```javascript
// @ts-check

/** @typedef {import('./types').User} User */
/** @typedef {import('./types').Config} Config */

/**
 * @param {User} user
 * @returns {string}
 */
function formatUser(user) {
  return `${user.name} <${user.email}>`;
}
```

### Generic Types

```javascript
// @ts-check

/**
 * Wrap a value in an array if not already an array.
 *
 * @template T
 * @param {T|T[]} value - Value to wrap
 * @returns {T[]} Array containing the value(s)
 */
function toArray(value) {
  return Array.isArray(value) ? value : [value];
}

/**
 * Create a typed map with string keys.
 *
 * @template V
 * @param {Object<string, V>} initial - Initial entries
 * @returns {Map<string, V>} New Map instance
 */
function createMap(initial) {
  return new Map(Object.entries(initial));
}
```

## When Documentation Adds Value

### Document These (High Value)

1. **Exported functions** - Type signatures and behavior
2. **Complex parameters** - Options objects, callbacks
3. **Side effects** - I/O, mutations, network calls
4. **Non-obvious behavior** - Edge cases, gotchas
5. **Business logic** - Domain concepts

```javascript
/**
 * Calculate prorated subscription cost.
 *
 * Uses calendar-day proration (not 30-day month). Minimum charge is $1.
 * Refunds are calculated at the original subscription rate, not current.
 *
 * @param {Subscription} subscription - Active subscription
 * @param {Date} cancelDate - Cancellation date
 * @returns {Money} Prorated amount
 */
export function calculateProratedCost(subscription, cancelDate) {
  // Types explain the shape; comments explain the business rules
}
```

### Skip Documentation (Self-Evident)

```javascript
// Simple utility - JSDoc optional (but types still help @ts-check)
/** @type {(a: number, b: number) => number} */
const add = (a, b) => a + b;

// Obvious from context - minimal doc is fine
/**
 * @param {number} ms
 * @returns {Promise<void>}
 */
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Missing Types

```javascript
// BAD: No types - defeats purpose of JSDoc
/**
 * @param name - The name
 * @param age - The age
 * @returns The user
 */
function createUser(name, age)
```

**Problem:** JSDoc without type annotations defeats its primary purpose in JavaScript. Unlike TypeScript, JavaScript has no type syntax, so JSDoc types are essential for editor support and `@ts-check` validation.

**Correct Pattern:**
```javascript
/**
 * @param {string} name - Display name (2-50 characters)
 * @param {number} age - Age in years (must be 13+)
 * @returns {User} Newly created user with generated ID
 */
function createUser(name, age)
```

### Anti-Pattern 2: Wrong Types

```javascript
// BAD: Types don't match implementation
/**
 * @param {string} id
 * @returns {User}  // Actually returns Promise<User>!
 */
async function getUser(id) { ... }
```

**Problem:** Incorrect types cause type checking failures and mislead developers. Async functions always return Promises, which must be reflected in the `@returns` type.

**Correct Pattern:**
```javascript
/**
 * @param {string} id
 * @returns {Promise<User>}
 */
async function getUser(id) { ... }
```

### Anti-Pattern 3: Incomplete Object Types

```javascript
// BAD: Generic Object type
/**
 * @param {Object} options
 */
function configure(options) { ... }
```

**Problem:** Generic `{Object}` provides no useful type information. Consumers don't know what properties are expected or their types.

**Correct Pattern:**
```javascript
/**
 * @param {Object} options - Configuration object
 * @param {string} options.host - Server hostname
 * @param {number} [options.port=3000] - Server port
 * @param {boolean} [options.ssl=false] - Enable HTTPS
 */
function configure(options) { ... }
```

## Side Effects Documentation

Always document side effects explicitly:

```javascript
/**
 * Save user preferences to persistent storage.
 *
 * Side Effects:
 * - Writes to localStorage under 'user-prefs' key
 * - Triggers 'prefsChanged' event on window
 * - Sends analytics event to tracking service
 *
 * @param {UserPreferences} prefs - User preference object
 * @throws {QuotaExceededError} If localStorage is full
 * @returns {void}
 */
export function savePreferences(prefs) {
  // Implementation
}
```

## Module Documentation

```javascript
/**
 * Authentication utilities for the application.
 *
 * Handles JWT token management, session persistence,
 * and OAuth2 flow integration.
 *
 * @module auth
 *
 * @example
 * import { authenticate, isAuthenticated } from './auth.js';
 *
 * if (!isAuthenticated()) {
 *   await authenticate(credentials);
 * }
 */

export { authenticate } from './authenticate.js';
export { isAuthenticated } from './session.js';
```

## Complex Type Patterns

### Union Types

```javascript
/**
 * Result of an async operation.
 *
 * @typedef {Object} SuccessResult
 * @property {'success'} status
 * @property {*} data
 *
 * @typedef {Object} ErrorResult
 * @property {'error'} status
 * @property {Error} error
 *
 * @typedef {SuccessResult|ErrorResult} Result
 */

/**
 * Execute operation and return result.
 *
 * @param {Function} operation
 * @returns {Promise<Result>}
 */
async function tryExecute(operation) {
  try {
    const data = await operation();
    return { status: 'success', data };
  } catch (error) {
    return { status: 'error', error };
  }
}
```

### Function Types

```javascript
/**
 * Comparator function for sorting.
 *
 * @callback Comparator
 * @param {*} a - First item
 * @param {*} b - Second item
 * @returns {number} Negative if a < b, positive if a > b, zero if equal
 */

/**
 * Sort array with custom comparator.
 *
 * @template T
 * @param {T[]} arr - Array to sort
 * @param {function(T, T): number} compare - Comparison function
 * @returns {T[]} New sorted array (original unchanged)
 */
export function sortBy(arr, compare) {
  return arr.toSorted(compare);
}
```

## Common ESLint Issues

**`jsdoc/require-param-type`** - Missing `{type}`
- Fix: Add type annotation

**`jsdoc/require-returns-type`** - Missing return type
- Fix: Add `{type}` to `@returns`

**`jsdoc/check-param-names`** - Param name mismatch
- Fix: Sync doc with signature

**`jsdoc/valid-types`** - Invalid type syntax
- Fix: Fix type annotation

**`jsdoc/check-types`** - Inconsistent type
- Fix: Use consistent casing (`String` becomes `string`)

**`jsdoc/require-jsdoc`** - Missing doc on export
- Fix: Add JSDoc comment

## Migration from No Documentation

1. **Add `// @ts-check`** to each file
2. **Fix TypeScript errors** by adding `@type` annotations
3. **Add `@param` and `@returns`** to exported functions
4. **Create `@typedef`** for repeated object shapes
5. **Run ESLint** to catch remaining issues
6. **Enable stricter rules** incrementally
