# React Anti-Patterns & Recovery Patterns

> **COMPANION RULE: LOAD WITH 440-react-core.md**
>
> Anti-patterns, error recovery, and output format examples for React development.
> Load alongside 440-react-core.md for complete guidance.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.3.0
**LastUpdated:** 2026-03-25
**Keywords:** React, Anti-Patterns, Error Recovery, Hydration, Suspense, ErrorBoundary, useEffect, use client, Resource Exhaustion, Cleanup, Unmount, AbortController
**TokenBudget:** ~2200
**ContextTier:** Medium
**Depends:** 440-react-core.md, 430-typescript-core.md
**LoadTrigger:** kw:anti-pattern, kw:error boundary, kw:hydration

## Scope

**What This Rule Covers:**
Common React anti-patterns, error recovery strategies (hydration, Suspense, TanStack Query errors, `'use client'` directives), resource exhaustion prevention, and cleanup/unmount patterns.

**When to Load This Rule:**
- Debugging React rendering or hydration issues
- Implementing error boundaries or Suspense patterns
- Reviewing code for common React mistakes
- Optimizing bundle size or query cache usage
- Fixing memory leaks from missing cleanup

## References

### Dependencies

**Must Load First:**
- **440-react-core.md** - Core React architecture and patterns
- **430-typescript-core.md** - TypeScript patterns (AbortController)

**Related:**
- **420-javascript-core.md** - JavaScript foundation

## Contract

### Inputs and Prerequisites

- React 18+ project with TypeScript
- Understanding of React hooks and component lifecycle
- TanStack Query configured (for error recovery patterns)

### Mandatory

- Error boundaries around independently loadable sections
- Cleanup functions in every `useEffect` that creates subscriptions, timers, or listeners
- `gcTime` configured on QueryClient to prevent unbounded cache growth

### Forbidden

- `useEffect` + `useState` for data fetching (use TanStack Query or RSC)
- Missing cleanup in `useEffect` that creates side effects
- Unbounded query caches without `gcTime`

### Output Format

Anti-pattern review results as inline code comments or checklist items identifying violations and their correct replacements per the patterns documented below.

### Execution Steps

1. Review component for anti-pattern violations listed below
2. Check error boundary placement (per-section, not page-level)
3. Verify cleanup functions in all side-effect `useEffect` calls
4. Audit QueryClient configuration for cache limits
5. Check bundle size if adding new dependencies

### Validation

**Pre-Task-Completion Checks:**
- [ ] No `useEffect` used for data fetching
- [ ] Error boundaries wrap feature sections (not entire pages)
- [ ] Every `useEffect` with side effects returns cleanup function
- [ ] QueryClient has `gcTime` configured
- [ ] Lists >100 items use virtualization

**Success Criteria:**
- No hydration mismatch warnings in console
- No memory leaks from missing cleanup (verify in React DevTools Profiler)
- Bundle size <500KB compressed for initial load

### Post-Execution Checklist

- [ ] Anti-patterns from this file checked during code review
- [ ] Error boundaries tested with intentional failures
- [ ] Cleanup verified by unmounting components during active operations

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Data Fetching in useEffect**
```typescript
// Bad: Manual fetching management
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  fetch('/api/user').then(d => {
    setData(d);
    setLoading(false);
  });
}, []);
```
**Problem:** Race conditions, no caching, no deduplication, boiler-plate heavy.

**Correct Pattern:**
```typescript
// Good: Using Query
const { data } = useQuery({ queryKey: ['user'], queryFn: fetchUser });
```
**Benefits:** Automatic caching, deduplication, background refetching, loading/error states handled.

**Anti-Pattern 2: Prop Drilling**
```typescript
// Bad: Passing props down 5 levels
<Layout user={user} theme={theme} settings={settings} />
```
**Problem:** Components become tightly coupled to data they don't use.

**Correct Pattern:**
```typescript
// Good: Composition or Zustand
const user = useUserStore(s => s.user); // Direct access
// OR
<Layout>
  <Header user={user} />
</Layout>
```
**Benefits:** Decouples components, easier refactoring.

**Hydration Mismatch Recovery (SSR/RSC):**
```tsx
// Hydration-safe pattern for client-only values (Date.now(), window.innerWidth, localStorage)
function useClientValue<T>(serverValue: T, clientValue: T): T {
  const [value, setValue] = useState(serverValue);
  useEffect(() => setValue(clientValue), [clientValue]);
  return value;
}
// Usage: const theme = useClientValue("light", getSystemTheme());
```

**Suspense Boundary Placement:**
```tsx
// Place Suspense boundaries around independently loadable sections, not at page level
<Suspense fallback={<HeaderSkeleton />}>
  <Header />
</Suspense>
<Suspense fallback={<ContentSkeleton />}>
  <MainContent />
</Suspense>
```

**TanStack Query Error Recovery:**
```tsx
import { QueryErrorResetBoundary } from '@tanstack/react-query';
import { ErrorBoundary } from 'react-error-boundary';

// Wrap feature sections with error boundary + retry
function FeatureSection() {
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          onReset={reset}
          fallbackRender={({ resetErrorBoundary }) => (
            <div>
              <p>Something went wrong loading this section.</p>
              <button onClick={() => resetErrorBoundary()}>Retry</button>
            </div>
          )}
        >
          <Suspense fallback={<FeatureSkeleton />}>
            <FeatureContent />
          </Suspense>
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
}
```

Enable error propagation in individual queries:
```typescript
// In useQuery options — propagate failures to nearest ErrorBoundary
useQuery({
  queryKey: ['feature', id],
  queryFn: fetchFeature,
  throwOnError: true,  // TanStack Query v5+
  retry: 3,            // Retries before propagating to boundary
});
```

**'use client' Directive Recovery (Next.js):**

If a component uses hooks (`useState`, `useEffect`, `useQuery`) without `'use client'`, Next.js throws:
> "You're importing a component that needs useState. It only works in a Client Component but none of its parents are marked with 'use client'."

**Fix:** Add `'use client'` as the very first line of the file (before imports):
```typescript
'use client';

import { useState } from 'react';
// ...
```

**Guidelines:**
- Only add `'use client'` to the nearest component that needs interactivity — don't mark entire feature directories
- Server Components (default in Next.js App Router) can import Client Components, but not vice versa for server-only logic
- If unsure, check: does this component use `useState`, `useEffect`, `useContext`, `useQuery`, or browser APIs? If yes, it needs `'use client'`

## Resource Exhaustion Prevention

### Bundle Size Budget
- Target: <500KB JavaScript (compressed) for initial load
- Use `next-bundle-analyzer` (Next.js) or `rollup-plugin-visualizer` (Vite) to audit
- Code-split routes with `React.lazy()` + `Suspense` for CSR, or dynamic `import()` in RSC

### Query Cache Limits
- Set `gcTime` (garbage collection) to prevent unbounded cache growth:
  ```typescript
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        gcTime: 10 * 60 * 1000,  // 10 minutes — evict unused cache entries
        staleTime: 5 * 60 * 1000,
      },
    },
  });
  ```
- For paginated queries, set `maxPages` to cap retained pages:
  ```typescript
  useInfiniteQuery({
    queryKey: ['items'],
    queryFn: fetchItems,
    maxPages: 5,
  });
  ```

### List Virtualization
- Lists >100 items MUST use virtualization (`@tanstack/react-virtual` or `react-window`)
- Prevents DOM node exhaustion and jank on scroll

## Cleanup & Unmount Patterns

### AbortController for Data Fetching
```typescript
function useAbortableFetch(url: string) {
  const { data } = useQuery({
    queryKey: ['data', url],
    queryFn: ({ signal }) => fetch(url, { signal }).then(r => r.json()),
  });
  return data;
}
```
TanStack Query v5 passes `signal` via `queryFn` context — use it to cancel in-flight requests on unmount.

### useEffect Cleanup
```typescript
useEffect(() => {
  const subscription = eventSource.subscribe(handler);
  return () => subscription.unsubscribe();
}, [eventSource]);
```
Every `useEffect` that creates a subscription, timer, or listener MUST return a cleanup function.

### External Store Subscriptions
Use `useSyncExternalStore` for subscribing to external stores (e.g., browser APIs, third-party state):
```typescript
import { useSyncExternalStore } from 'react';

const width = useSyncExternalStore(
  (cb) => { window.addEventListener('resize', cb); return () => window.removeEventListener('resize', cb); },
  () => window.innerWidth,
  () => 1024  // SSR fallback
);
```

## Output Format Examples

```markdown
MODE: PLAN

Investigation:
- Reviewed `package.json`: Found Next.js 14, TypeScript, Tailwind.
- Checked `src` structure: Currently flat structure, will migrate to Feature-based.
- Analysis: Need to implement `Auth` feature using Server Actions and Zustand.

Implementation:
Moving auth logic to `src/features/auth`. Creating strict separation between Server Components (forms) and Client Components (interactivity).
```

```tsx
// src/features/auth/components/LoginForm.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { loginSchema, type LoginInput } from '../types';
import { useAuthStore } from '../stores/authStore';

export const LoginForm = () => {
  const setUser = useAuthStore((s) => s.setUser);
  const { register, handleSubmit } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema)
  });

  const onSubmit = async (data: LoginInput) => {
    // Implementation...
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <input {...register('email')} className="input-primary" />
      <button type="submit" className="btn-primary">Login</button>
    </form>
  );
};
```

```bash
# Validation commands
npm run lint
npm run test
npm run type-check
```
