# React Core: Modern Architecture & Best Practices

> **CORE RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential React patterns. Load for React tasks.
> Specialized rules depend on this foundation.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** React, Next.js, RSC, Hooks, Tailwind, Zustand, TanStack Query, Shadcn, Feature-based, TypeScript, Vitest, Testing Library, debug hooks, fix React error, component rendering
**TokenBudget:** ~3050
**ContextTier:** High
**Depends:** 000-global-core.md, 420-javascript-core.md, 430-typescript-core.md

## Scope

**What This Rule Covers:**
Establishes the definitive standards for developing scalable, maintainable React applications in 2025. This rule enforces "Feature-based" architecture, Server Components (RSC) usage, and modern state management patterns to replace legacy approaches like global Redux or huge `useEffect` chains.

**When to Load This Rule:**
- Building or maintaining React applications
- Setting up Next.js or Vite projects
- Implementing React component architecture
- Choosing state management solutions
- Configuring React testing strategies
- Reviewing React code for best practices

## References

### Dependencies

**Must Load First:**
- **000-global-core.md** - Foundation for all rules
- **420-javascript-core.md** - JavaScript patterns
- **430-typescript-core.md** - TypeScript strict typing

**Related:**
- **441-react-backend.md** - Python backend patterns, API communication, authentication

### External Documentation

- [React.dev (Official Docs)](https://react.dev/) - The definitive guide to modern React
- [TanStack Query Docs](https://tanstack.com/query/latest) - Standard for async state management
- [Zustand Docs](https://github.com/pmndrs/zustand) - Minimalist client state management
- [Redux Toolkit Docs](https://redux-toolkit.js.org/) - Enterprise state management
- [Bulletproof React](https://github.com/alan2207/bulletproof-react) - Architecture reference for feature-based structure

## Contract

### Inputs and Prerequisites

- Node.js 18+ installed
- React 18+ project
- TypeScript 5+ configured
- Understanding of modern React patterns (hooks, functional components)

### Mandatory

- Package manager: `npm`, `pnpm`, `yarn`, or `bun`
- Build tool: `vite` or `next`
- Testing: `vitest` and React Testing Library
- Linting: `biome` (or `eslint`/`prettier`)
- Styling: Tailwind CSS

### Forbidden

- `create-react-app` (deprecated)
- `class components` (legacy pattern)
- `default exports` for components (exception: Next.js pages/layouts require default exports)
- `barrel files` (circular dependency risks)
- `enzyme` testing library (deprecated)
- Manual data fetching with `useEffect` + `useState`

### Execution Steps

1. **Investigate Project:** Read `package.json` to identify framework (Next.js vs Vite) and existing dependencies
2. **Check Configuration:** Review `tsconfig.json` for path aliases (e.g., `@/*`)
3. **Validate Architecture:** Confirm if the project uses Feature-based folder structure before adding files
4. **Check Rendering Strategy:** Identify if the context is Client Side (CSR) or Server Side (RSC) to apply correct data fetching patterns
5. **Enforce Strict Mode:** Ensure `React.StrictMode` is enabled
6. **Prefer Composition:** Use component composition over complex custom hooks for UI logic
7. **Verify Types:** Ensure all props and state are typed with Zod or TypeScript interfaces (no `any`)
8. **Apply State Pattern:** Use TanStack Query for server state, Zustand for client state
9. **Validate Output:** Run linting and tests before marking complete

### Output Format

TypeScript code (`.tsx`, `.ts`) with:
- Functional components using named exports
- Feature-based folder structure
- TanStack Query for async data
- Zustand for global UI state
- Tailwind CSS for styling
- React Testing Library for tests

### Validation

**Pre-Task-Completion Checks:**
- [ ] Read `package.json` to identify framework and dependencies
- [ ] Check `tsconfig.json` for path aliases
- [ ] Scan existing `src` folder structure before adding files
- [ ] Identify rendering strategy: Client Side (CSR) or Server Side (RSC)
- [ ] Confirm `React.StrictMode` is enabled
- [ ] Verify Tailwind and testing libraries are configured
- [ ] Feature code placed in `src/features/<domain>` structure
- [ ] `useQuery` or RSC used for data fetching (no `useEffect` for async)
- [ ] Global UI state uses Zustand (or RTK if enterprise requirement)
- [ ] Components typed with TypeScript interfaces (no `any`)
- [ ] No `useEffect` for derived state (use `useMemo` or direct calculation)
- [ ] `vitest` tests written for user interactions
- [ ] `className` prop support enabled via `cn()` utility
- [ ] All imports use absolute paths (e.g., `@/components/...`)

**Success Criteria:**
- `npm run test` (vitest) passes all tests
- `npm run type-check` (tsc --noEmit) shows no type errors
- `npm run lint` passes without errors
- App builds without strict mode warnings

**Negative Tests:**
- Importing a component via `default` should trigger a lint warning (if configured)
- Direct `fetch` calls in components should be flagged in code review

### Design Principles

- **Feature-Based Architecture:** Organize by business domain, not technical layers
- **Server State Separation:** Use TanStack Query or RSC for async data, never `useEffect`
- **Composition Over Complexity:** Prefer component composition over custom hooks with >50 lines of logic
- **Type Safety:** All components and state fully typed with TypeScript
- **Test User Behavior:** Test interactions, not implementation details

### Post-Execution Checklist

- [ ] Feature code placed in `src/features/<domain>` structure
- [ ] `useQuery` or RSC used for data fetching (no `useEffect` for async)
- [ ] Global UI state uses Zustand (or RTK if enterprise requirement)
- [ ] Components typed with TypeScript interfaces (no `any`)
- [ ] No `useEffect` for derived state (use `useMemo` or direct calculation)
- [ ] `vitest` tests written for user interactions
- [ ] `className` prop support enabled via `cn()` utility
- [ ] All imports use absolute paths (e.g., `@/components/...`)
- [ ] Linting and type-check pass: `npm run lint && npm run type-check`

## Key Principles

### Project Architecture & Structure

#### Feature-Based Organization
- **Requirement:** Organize the `src` directory by "features" (business domains) rather than technical layers.
- **Rule:** Shared UI components go in `src/components/ui`. Domain-specific logic goes in `src/features/<domain>`.

```typescript
// Good: Feature-based structure
src/
  features/
    discussions/
      api/        # Data fetching logic
      components/ # Components scoped to this feature
      hooks/      # Hooks scoped to this feature
      types/      # TypeScript types for this feature
      index.ts    # Public API of the feature
  components/
    ui/           # Generic UI components (Buttons, Inputs)
  lib/            # Application-wide utilities (axios, queryClient)
```

#### Component Definition
- **Requirement:** Use Functional Components with Named Exports.
- **Avoid:** Default exports (re-exporting and refactoring pain).

```typescript
// Good: Named export and explicit return type
import { ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

export const Button = ({ children, onClick, variant = 'primary' }: ButtonProps) => {
  return (
    <button onClick={onClick} className={`btn-${variant}`}>
      {children}
    </button>
  );
};
```

### State Management & Data Fetching

#### Server State (Async Data)
- **Requirement:** DO NOT use `useEffect` + `useState` for data fetching.
- **Always:** Use **TanStack Query** (Client) or **Server Components** (Next.js/RSC) for async operations.

```typescript
// Good: Using TanStack Query
import { useQuery } from '@tanstack/react-query';
import { fetchUser } from './api';

export const UserProfile = ({ userId }: { userId: string }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error</div>;

  return <div>{data.name}</div>;
};
```

#### Client State (Global UI)
- **Recommended:** Use **Zustand** for global client state (sidebar open/close, theme, session tokens).
- **Alternative:** **Redux Toolkit** is valid for complex enterprise apps with extensive middleware needs.
- **Avoid:** React Context for frequently-updating state (performance issues with re-renders).

```typescript
// Good: Zustand Store
import { create } from 'zustand';

interface UIStore {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}

export const useUIStore = create<UIStore>((set) => ({
  isSidebarOpen: false,
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));
```

### Styling & UI Patterns

#### Tailwind & Shadcn/UI
- **Requirement:** Use Utility-First CSS (Tailwind).
- **Rule:** Implement component patterns similar to **Shadcn/UI** (Radix Primitives + Tailwind).
- **Avoid:** CSS Modules, styled-components, or heavy runtime CSS-in-JS libraries.

```tsx
// Good: Tailwind composition with cn utility
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

export const Card = ({ className, ...props }: CardProps) => (
  <div
    className={cn("rounded-xl border bg-card text-card-foreground shadow", className)}
    {...props}
  />
);
```

### Integration & Testing

#### Testing Strategy
- **Requirement:** Write tests using **Vitest** and **React Testing Library**.
- **Rule:** Test user interactions (clicks, typing), not implementation details (state changes, internal methods).

```typescript
// Good: Testing user interaction
import { render, screen, fireEvent } from '@testing-library/react';
import { Counter } from './Counter';

test('increments count when button is clicked', () => {
  render(<Counter />);
  const button = screen.getByRole('button', { name: /increment/i });
  fireEvent.click(button);
  expect(screen.getByText(/count: 1/i)).toBeInTheDocument();
});
```

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

> **Investigation Required**
> When applying this rule:
> 1. **Read `package.json` first** to determine framework (Next.js vs Vite) and dependencies.
> 2. **Check `tsconfig.json`** for path aliases (e.g., `@/*`).
> 3. **Scan existing `src` folder** to respect current architectural patterns if migrating gradually.
> 4. **If uncertain, explicitly state:** "I need to check the routing configuration to recommend the correct data loading strategy."
> 5. **Make grounded recommendations** based on the actual tech stack version (e.g., Next 13 vs 14).

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
