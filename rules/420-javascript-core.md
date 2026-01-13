# JavaScript Core: Modern Standards & Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential JavaScript patterns. Load for JavaScript tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** JavaScript, ES2024, ESM, Node.js, JSDoc, Biome, node:test, Immutability, Async/Await, Functional Programming
**TokenBudget:** ~3200
**ContextTier:** High
**Depends:** 000-global-core.md

## Scope

**What This Rule Covers:**
Definitive standards for writing modern, robust JavaScript in 2025, enforcing ECMAScript Modules (ESM), immutable data patterns (ES2023+ methods), type safety via JSDoc, and modern tooling (Biome, Node Native Test Runner).

**When to Load This Rule:**
- Writing or modifying JavaScript code
- Setting up new Node.js projects
- Implementing async patterns and promise handling
- Establishing JavaScript coding standards
- Configuring JavaScript tooling (Biome, node:test)
- Migrating from CommonJS to ESM
- Adding type safety with JSDoc

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation rule with core patterns and validation gates

**Related:**
- **440-react-core.md** - React-specific patterns and best practices

### External Documentation

**Official Documentation:**
- [MDN Web Docs - JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) - Official JavaScript standard reference
- [Node.js Test Runner](https://nodejs.org/api/test.html) - Native test runner documentation
- [JSDoc Documentation](https://jsdoc.app/) - Type comment syntax reference

**Best Practices Guides:**
- [Biome](https://biomejs.dev/) - Fast formatter and linter for JavaScript
- [ES2024 Features](https://github.com/tc39/proposals/blob/main/finished-proposals.md) - Stage 4 ECMAScript proposals
## Contract

### Inputs and Prerequisites

- Node.js 20+ (LTS) with ECMAScript 2024+ support
- Package manager (npm, pnpm, or bun)
- Biome for linting and formatting
- Project requirements and existing codebase identified

### Mandatory

- **[ESM]** - Set `"type": "module"` in package.json; use `import` / `export`
- **[Immutability]** - Use `arr.toSorted()` instead of `arr.sort()`
- **[Async]** - Use top-level `await` and `try/catch` or `Promise.allSettled`
- **[Grouping]** - Use `Object.groupBy()` for data grouping
- **[Testing]** - Use `node:test` and `node:assert` for unit tests
- **[Linting]** - Use Biome for fast linting/formatting
- **[Type Safety]** - Use `// @ts-check` and JSDoc for complex logic

### Forbidden

- `var` keyword (use `const` or `let`)
- `require()` / `module.exports` (CommonJS - use ESM)
- `eval()` or unsafe dynamic code execution
- `axios` or legacy HTTP libraries (use native `fetch`)
- Legacy looping (`for-in` without hasOwnProperty checks)
- Mutating array methods when immutable alternatives exist

### Execution Steps

1. **Enforce ESM:** Ensure `package.json` contains `"type": "module"`
2. **Verify Type Safety:** Add `// @ts-check` to the top of files and use JSDoc for critical functions
3. **Prefer Immutability:** Use new array methods (`toSorted`, `with`, `toSpliced`) instead of mutating originals
4. **Use Native APIs:** Prefer `fetch`, `node:test`, and `node:assert` over third-party libraries
5. **Configure Biome:** Set up `biome.json` with project-specific rules
6. **Test with node:test:** Write tests using native Node.js test runner

### Output Format

```javascript
// src/processor.js
// @ts-check

/**
 * Processes and sorts transactions by date.
 * @param {Array<{amount: number, date: string}>} transactions
 * @returns {Array<{amount: number, date: string}>}
 */
export function processTransactions(transactions) {
  // Validation
  if (!Array.isArray(transactions)) {
    throw new TypeError('Input must be an array');
  }

  // Immutable sort
  return transactions.toSorted((a, b) =>
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );
}
```

```javascript
// tests/processor.test.js
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { processTransactions } from '../src/processor.js';

test('processTransactions sorts by date', () => {
  const input = [
    { amount: 100, date: '2023-01-02' },
    { amount: 50, date: '2023-01-01' }
  ];

  const result = processTransactions(input);

  assert.equal(result[0].amount, 50);
  assert.equal(input[0].amount, 100); // Ensure original not mutated
});
```

### Validation

**Pre-Task-Completion Validation Gate (CRITICAL):**

Reference: Complete validation protocol in `000-global-core.md` and `AGENTS.md`

**Code Quality:**
- **CRITICAL:** `npx biome check .` passes with no errors
- **CRITICAL:** `"type": "module"` present in package.json
- **CRITICAL:** No `var` keywords used
- **CRITICAL:** No `require()` or `module.exports` statements
- **Format Check:** JSDoc comments present for exported functions
- **Format Check:** `// @ts-check` enabled for complex logic

**Testing:**
- **CRITICAL:** `node --test` or `npm test` passes all tests
- **CRITICAL:** Tests use `node:test` and `node:assert`
- **Negative Test:** `var` usage should fail linting
- **Negative Test:** `module.exports` should trigger warning

**Modern JavaScript Patterns:**
- **Immutability:** `toSorted()`, `toSpliced()`, `with()` used instead of mutating methods
- **Native APIs:** `fetch` used instead of axios/request
- **Grouping:** `Object.groupBy()` used instead of reduce or lodash
- **Async:** `Promise.allSettled()` used for parallel operations with partial failure handling

**Success Criteria:**
- `npm test` runs using `node --test`
- `npx biome check .` passes
- Code uses `import`/`export` exclusively
- Original arrays/objects not mutated

**Investigation Required:**
1. **Check `package.json`** for `"type": "module"` before writing any code
2. **Verify Node.js version** (`node -v`) to ensure support for `toSorted` (Node 20+) and `groupBy` (Node 21+)
3. **Scan for existing CommonJS** files (`.cjs`) to ensure interoperability if needed
4. **Review existing tests** to understand current patterns before adding new ones

**Anti-Pattern Examples:**
- Using `require()` in ESM project
- Using `axios` when native `fetch` is available
- Mutating arrays with `.sort()` instead of `.toSorted()`
- Using `var` keyword

**Correct Pattern:**
- "Let me check your package.json and Node.js version first."
- [reads package.json, verifies "type": "module", checks node -v]
- "I see you're using ESM and Node 20. Here's the implementation using `toSorted()` and native `fetch`..."
- [implements with JSDoc, runs tests, runs biome]

### Design Principles

- **ESM First:** Use ECMAScript Modules exclusively for better tree-shaking and browser compatibility
- **Immutability:** Prefer non-mutating methods to avoid side effects
- **Type Safety:** Use JSDoc for critical functions to catch errors early
- **Native APIs:** Leverage built-in Node.js capabilities over third-party dependencies
- **Modern Syntax:** Use ES2024+ features for cleaner, more expressive code
- **Fast Tooling:** Use Biome for instant feedback during development

### Post-Execution Checklist

**Before Starting:**
- [ ] Rule dependencies loaded (000-global-core.md)
- [ ] Node.js 20+ available
- [ ] Biome installed
- [ ] Existing JavaScript codebase reviewed (if modifying)

**After Completion:**
- [ ] **CRITICAL:** `npx biome check .` passes with no errors
- [ ] **CRITICAL:** `node --test` or `npm test` passes all tests
- [ ] **CRITICAL:** `"type": "module"` present in package.json
- [ ] **CRITICAL:** No `var` keywords used
- [ ] JSDoc comments present for exported functions
- [ ] `// @ts-check` enabled for complex logic
- [ ] `node:test` used for testing
- [ ] No `require()` statements found
- [ ] Native `fetch` used instead of axios/request
- [ ] `Object.groupBy` used for grouping logic
- [ ] Biome configuration file (`biome.json`) present
- [ ] CHANGELOG.md and README.md updated as required

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: CommonJS Require**
```javascript
// Bad: Legacy Node.js pattern
const fs = require('fs');
module.exports = { ... };
```
**Problem:** Breaks tree-shaking, incompatible with browser ESM, considered legacy.

**Correct Pattern:**
```javascript
// Good: Standard ESM
import fs from 'node:fs';
export default { ... };
```

**Anti-Pattern 2: Mutating State**
```javascript
// Bad: Mutates 'users' array directly
const users = ['Charlie', 'Alice', 'Bob'];
users.sort();
```
**Problem:** Unpredictable side effects, especially in React or concurrent contexts.

**Correct Pattern:**
```javascript
// Good: Returns a new array
const sortedUsers = users.toSorted();
```

**Anti-Pattern 3: Ignoring Promise Failures**
```javascript
// Bad: Uncaught rejection potential
const results = await Promise.all(requests);
```
**Problem:** If one request fails, the entire operation rejects immediately.

**Correct Pattern:**
```javascript
// Good: Handle partial failures
const results = await Promise.allSettled(requests);
const successful = results
 .filter(r => r.status === 'fulfilled')
 .map(r => r.value);
```

## Modern Syntax and Project Structure

### Module System (ESM)
- **Requirement:** All JavaScript files must use ECMAScript Modules.
- **Rule:** File extensions should be `.js` (with `"type": "module"`) or explicitly `.mjs`.

```javascript
// package.json
{
 "name": "my-app",
 "type": "module",
 "engines": { "node": ">=20.0.0" }
}

// src/utils.js
export const add = (a, b) => a + b;

// src/index.js
import { add } from './utils.js';
console.log(add(2, 3));
```

### Type Safety with JSDoc
- **Requirement:** Use JSDoc to define signatures for exported functions.
- **Always:** Enable TypeScript checking in JS files using `// @ts-check`.

```javascript
// @ts-check

/**
 * Fetches user data.
 * @param {string} id - The user ID.
 * @returns {Promise<{name: string, email: string}>}
 */
export async function fetchUser(id) {
 const res = await fetch(`https://api.example.com/users/${id}`);
 if (!res.ok) throw new Error('Failed to fetch');
 return res.json();
}
```

## Data Manipulation and Immutability

### Array Methods (ES2023+)
- **Requirement:** Use modern, non-mutating array methods.
- **Avoid:** `sort()`, `splice()`, `reverse()` (these mutate in place).
- **Rule:** Use `toSorted()`, `toSpliced()`, `toReversed()`, and `with()`.

```javascript
const items = [3, 1, 2];

// Bad (Mutates original)
// items.sort();

// Good (Returns new array)
const sortedItems = items.toSorted();

// Good (Replace item at index without mutation)
const updatedItems = items.with(1, 99); // [3, 99, 2]
```

### Data Grouping (ES2024)
- **Rule:** Use the native `Object.groupBy` or `Map.groupBy`.
- **Avoid:** Third-party libraries like Lodash for simple grouping.

```javascript
const inventory = [
 { name: "asparagus", type: "vegetables" },
 { name: "bananas", type: "fruit" },
 { name: "goat", type: "meat" },
];

const result = Object.groupBy(inventory, ({ type }) => type);
/* Result:
{
 vegetables: [{ name: "asparagus", ... }],
 fruit: [{ name: "bananas", ... }],
 meat: [{ name: "goat", ... }]
}
*/
```

## Asynchronous Patterns

### Top-Level Await
- **Rule:** Use top-level `await` in ESM modules for initialization logic.
- **Avoid:** Wrapping code in `(async () => { ... })()` IIFEs.

```javascript
// db.js
import { connect } from 'some-db-driver';

// Allowed in modules
export const db = await connect(process.env.DB_URL);
```

### Structured Error Handling
- **Always:** Use `cause` property in Errors to preserve stack traces when wrapping errors.

```javascript
try {
 await riskyOperation();
} catch (err) {
 throw new Error('Operation failed', { cause: err });
}
```

## Testing and Tooling

### Native Test Runner
- **Requirement:** Use Node.js native test runner (`node:test`) for pure JS projects to reduce dependency tree size.
- **Rule:** Use `node:assert` for assertions.

```javascript
// tests/math.test.js
import { test, describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { add } from '../src/math.js';

describe('Math Utils', () => {
 it('should add two numbers', () => {
 assert.equal(add(2, 2), 4);
 });
});
```

### Linting with Biome
- **Requirement:** Use **Biome** (`@biomejs/biome`) for linting and formatting. It is significantly faster than ESLint + Prettier and requires less configuration.
