---
schema_version: v4.0
rule_version: v5.0.0
description: "React with TypeScript: follow the project's framework and structure, server/client state separation, accessible typed components and behavior-focused tests."
last_updated: 2026-10-07
keywords:
  - kw:feature-based architecture
  - kw:TanStack Query
  - kw:RSC server components
  - kw:Zustand client state
  - kw:named exports components
  - kw:shadcn Tailwind patterns
  - kw:tsx
token_budget: ~1150
context_tier: High
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
    - 420-javascript-core.md  # JavaScript patterns
    - 430-typescript-core.md  # TypeScript strict typing
  optional:
    - 440a-react-anti-patterns.md  # Anti-patterns, error recovery, hydration, resource exhaustion, cleanup, output examples
    - 441-react-backend.md  # Python backend patterns, API communication, authentication
---
# React Core

## Scope

**What This Rule Covers:**
React function components in TypeScript: framework and rendering-model detection, feature-based structure, server/client state, Server Components, styling conventions, accessibility and tests.

**When to Load This Rule:**
When creating or reviewing React `.tsx` code; read `440a-react-anti-patterns.md` for error, hydration, cleanup and performance review and `441-react-backend.md` for API/auth integration.

## Contract

### Inputs and Prerequisites

- `package.json`, lockfile, React/framework versions (Next.js, Vite, Remix/React Router, other), tsconfig paths and existing directory layout.
- Existing data-fetching, state, styling, component library, lint/format and test tooling, plus the project's lint/type-check/test commands.

### Mandatory

- Investigate before editing: identify framework, router, rendering model (CSR, SSR, RSC) and established conventions. Follow them for new code; restructuring, framework changes or new dependencies are separate approved work.
- Prefer feature-based organization (`src/features/<domain>` with shared UI in a common components directory) for new projects or where already used; do not mass-migrate an existing layout as a side effect.
- Write function components with typed props; avoid `any` and use runtime validation (such as Zod) at untrusted boundaries. Class components remain acceptable only where required, such as custom error boundaries.
- Prefer named component exports; default exports are required for framework convention files (for example Next.js App Router `page`, `layout`, `loading`, `error`, `not-found`, `template`, `default`) and lazy-loaded modules where the API expects them.
- Fetch server data with the framework's data mechanism (Server Components, loaders, server actions) or the project's server-state library (TanStack Query, SWR, RTK Query). Do not hand-roll fetching with `useEffect` + `useState` for new code; where unavoidable, handle cancellation, races and errors.
- Keep server state out of global client stores. Use local state first, lift or compose before adding a store, and use the project's client-state library (Zustand, Redux Toolkit, Context for low-frequency values) for genuinely shared UI state.
- Never keep auth tokens or secrets in client stores or localStorage; follow `441-react-backend.md` for session handling.
- In RSC frameworks, mark `'use client'` only at the boundary that needs state, effects, event handlers or browser APIs; keep server-only code and secrets out of client modules and pass only serializable props across the boundary.
- Follow the project's styling system (Tailwind/shadcn-style composition where established); do not introduce a new styling approach without approval.
- Components are accessible: semantic elements, labelled controls, keyboard operation, focus management and correct ARIA where native semantics are insufficient.
- Test user-visible behavior with React Testing Library queries by role/label and `user-event`, not internal state; mock network at the boundary.
- Keep `React.StrictMode` where the project uses it; do not remove it to hide double-invocation bugs.
- Run the project's actual lint, type-check and test commands; do not claim rendering or interaction correctness from static review.

### Execution Steps

1. Read package, framework, tsconfig, directory and existing component/state/test conventions; confirm rendering model.
2. Implement the minimal typed, accessible component and data/state change using established libraries and boundaries.
3. Add or update behavior tests and run available lint, type-check, tests and build.
4. Report files, rendering/state choices, commands with results and any unverified browser or accessibility behavior.

### Validation

- Changes follow the detected framework, structure and libraries; no unapproved dependencies or migrations.
- Server data uses framework or server-state tooling; client stores hold no server data or credentials.
- Client/server boundaries minimal and serializable; components typed and accessible.
- Behavior tests, lint, type-check and build pass, or failures and gaps are reported.

## References

- [React documentation](https://react.dev/)
- [Server Components](https://react.dev/reference/rsc/server-components)
- ['use client'](https://react.dev/reference/rsc/use-client)
- [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview)
- [Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Next.js file conventions](https://nextjs.org/docs/app/api-reference/file-conventions)
