# JavaScript Core: Modern Standards & Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
> 
> This rule defines essential JavaScript patterns. Load for JavaScript tasks.
> Specialized rules depend on this foundation.


## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** JavaScript, ES2024, ESM, Node.js, JSDoc, Biome, node:test, Immutability, Async/Await, Functional Programming
**TokenBudget:** ~2000
**ContextTier:** High
**Depends:** rules/000-global-core.md

## Purpose
Establishes the definitive standards for writing modern, robust JavaScript in 2025. This rule enforces the use of ECMAScript Modules (ESM), immutable data patterns (using ES2023+ methods), Type Safety via JSDoc, and modern tooling (Biome, Node Native Test Runner) to ensure maintainability and performance without the need for a compilation step.

## Rule Scope
Applies to all pure JavaScript projects, Node.js scripts, and backend logic. Covers syntax, asynchronous patterns, testing, and project configuration.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **[ESM]** - Set `"type": "module"` in package.json; use `import` / `export`.
- **[Immutability]** - Use `arr.toSorted()` instead of `arr.sort()`.
- **[Async]** - Use top-level `await` and `try/catch` (or `Promise.allSettled`).
- **[Grouping]** - Use `Object.groupBy()` for data grouping.
- **[Testing]** - Use `import { test } from 'node:test'` and `node:assert`.
- **[Linting]** - Use **Biome** for fast linting/formatting.

**Quick Checklist:**
- [ ] `"type": "module"` present in package.json
- [ ] No `var` keywords used
- [ ] `// @ts-check` enabled for complex logic
- [ ] `node:test` used for unit tests
- [ ] Native `fetch` used for HTTP requests
- [ ] `Object.groupBy` used instead of lodash `_.groupBy`
## Contract

<contract>
<inputs_prereqs>
Node.js 20+ (LTS), ECMAScript 2024+ support.
</inputs_prereqs>

<mandatory>
`npm`, `pnpm`, `bun`, `node` (native runner), `biome`.
</mandatory>

<forbidden>
`var`, `require` (CommonJS), `eval`, `axios` (use native `fetch`), legacy looping (`for-in` without checks).
</forbidden>

<steps>
1. **Enforce ESM:** Ensure `package.json` contains `"type": "module"`.
2. **Verify Type Safety:** Add `// @ts-check` to the top of files and use JSDoc for critical functions.
3. **Prefer Immutability:** Use new array methods (`toSorted`, `with`, `toSpliced`) instead of mutating originals.
4. **Use Native APIs:** Prefer `fetch`, `node:test`, and `node:assert` over third-party libraries for core functionality.
</steps>

<output_format>
Modern JavaScript (`.js` or `.mjs`), documented with JSDoc.
</output_format>

<validation>
Run `node --test` and lint with `biome`.
</validation>

</contract>

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

## Post-Execution Checklist
- [ ] Project is configured as `"type": "module"`
- [ ] JSDoc comments present for exported functions
- [ ] `node:test` used for testing (or Vitest for larger suites)
- [ ] No `require()` statements found
- [ ] Native `fetch` used instead of `axios`/`request`
- [ ] `Object.groupBy` used for grouping logic
- [ ] Biome configuration file (`biome.json`) present

## Validation
- **Success checks:**
 - `npm test` runs using `node --test`
 - `npx biome check .` passes
 - Code uses `import`/`export` exclusively
- **Negative tests:**
 - Presence of `var` should fail linting
 - `module.exports` should trigger a warning

> **Investigation Required**
> When applying this rule:
> 1. **Check `package.json`** for `"type": "module"` before writing any code.
> 2. **Verify Node.js version** (`node -v`) to ensure support for `toSorted` (Node 20+) and `groupBy` (Node 21+).
> 3. **Scan for existing CommonJS** files (`.cjs`) to ensure interoperability if needed.

## Output Format Examples

```markdown
MODE: ACT

Investigation:
- Checked package.json: "type": "module" is set.
- Node version: 20.11.0 (LTS).
- Goal: Implement data processing utility with immutable patterns.

Implementation:
Creating `src/processor.js` using standard ESM and `toSorted` for data handling.
```

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

 // specific immutable sort
 return transactions.toSorted((a, b) =>
 new Date(a.date).getTime() - new Date(b.date).getTime()
 );
}
```

```javascript
// tests/processor.test.js
import { test, it } from 'node:test';
import assert from 'node:assert/strict';
import { processTransactions } from '../src/processor.js';

test('processTransactions sorts by date', () => {
 const input = [
 { amount: 100, date: '2023-01-02' },
 { amount: 50, date: '2023-01-01' }
 ];

 const result = processTransactions(input);

 assert.equal(result[0].amount, 50);
 assert.equal(input[0].amount, 100); // Ensure original is not mutated
});
```

## References

### External Documentation
- [MDN Web Docs - JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) - The official standard reference.
- [Node.js Test Runner](https://nodejs.org/api/test.html) - Official docs for the native test runner.
- [Biome](https://biomejs.dev/) - Fast formatter and linter for JavaScript.
- [JSDoc Documentation](https://jsdoc.app/) - Syntax reference for type comments.

### Related Rules
- **Global Core**: `rules/000-global-core.md`
- **React Core**: `rules/440-react-core.md`

> ** Claude 4 Specific Guidance**
> **Claude 4 Optimizations:**
> - **ESNext Mastery:** Claude is aware of standard stage-4 features like `Object.groupBy`; explicit instructions help it choose these over `reduce`.
> - **JSDoc Generation:** Ask Claude to "add JSDoc types" and it will generate strict, compatible comments.
> - **Test Generation:** It can write complete `node:test` suites without needing external libraries.

## 1. Modern Syntax & Project Structure

### 1.1 Module System (ESM)
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

### 1.2 Type Safety (JSDoc)
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

## 2. Data Manipulation & Immutability

### 2.1 Array Methods (ES2023+)
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

### 2.2 Grouping (ES2024)
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

## 3. Asynchronous Patterns

### 3.1 Top-Level Await
- **Rule:** Use top-level `await` in ESM modules for initialization logic.
- **Avoid:** Wrapping code in `(async () => { ... })()` IIFEs.

```javascript
// db.js
import { connect } from 'some-db-driver';

// Allowed in modules
export const db = await connect(process.env.DB_URL);
```

### 3.2 Structured Error Handling
- **Always:** Use `cause` property in Errors to preserve stack traces when wrapping errors.

```javascript
try {
 await riskyOperation();
} catch (err) {
 throw new Error('Operation failed', { cause: err });
}
```

## 4. Testing & Tooling

### 4.1 Native Test Runner
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

### 4.2 Linting
- **Recommended:** Use **Biome** (`@biomejs/biome`) for linting and formatting. It is significantly faster than ESLint + Prettier and requires less configuration.
