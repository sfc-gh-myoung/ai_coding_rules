# React Backend Integration: Python-First Full-Stack Patterns

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** React backend, FastAPI, Flask, Python API, CORS, JWT, authentication, API integration, full-stack, Express alternative, fetch, axios, TanStack Query backend, Next.js API routes, httpOnly cookies
**TokenBudget:** ~1800
**ContextTier:** High
**Depends:** rules/440-react-core.md, rules/200-python-core.md

## Purpose

Establishes backend integration patterns for React applications, with Python (FastAPI/Flask) as the organizational default. Covers API communication, authentication flows, CORS configuration, and type sharing between frontend and backend.

## Rule Scope

Applies to all React applications requiring backend API integration. Covers framework selection, API patterns, authentication, and development workflows for full-stack applications.

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **[Organizational Default]** - Use **Python backend** (FastAPI or Flask) unless user explicitly requests otherwise.
- **[Lightweight Option]** - For Next.js apps with simple APIs, **Next.js API routes** are acceptable.
- **[Alternative]** - **Node.js/Express** only when user explicitly requests or team has Node expertise.
- **[API Communication]** - Use **TanStack Query** for all API calls; never raw `useEffect` + `fetch`.
- **[Authentication]** - Store JWT in **httpOnly cookies**, not localStorage.
- **[CORS]** - Configure CORS on backend; never use `*` in production.

**Pre-Execution Checklist:**
- [ ] Determine if separate backend is needed (vs Next.js API routes)
- [ ] Identify backend framework: FastAPI (async, OpenAPI) vs Flask (simpler, mature)
- [ ] Check existing backend code/patterns before adding new endpoints
- [ ] Verify CORS configuration exists for development and production
- [ ] Confirm authentication strategy (JWT, session, OAuth)
- [ ] Review environment variable setup for API URLs

## Contract

<contract>
<inputs_prereqs>
React application (per 440-react-core.md); Python environment (per 200-python-core.md); understanding of REST API patterns
</inputs_prereqs>

<mandatory>
TanStack Query for API state; httpOnly cookies for JWT; environment variables for API URLs; CORS middleware on backend
</mandatory>

<forbidden>
Node.js/Express backend (unless user explicitly requests); JWT in localStorage; hardcoded API URLs; `*` CORS origin in production; raw fetch in useEffect for data fetching
</forbidden>

<steps>
1. **Determine Backend Need:** Assess if Next.js API routes suffice or separate backend required.
2. **Select Framework:** Choose FastAPI (async, auto-docs) or Flask (simpler) based on requirements.
3. **Configure CORS:** Set up CORS middleware with specific origins for dev and production.
4. **Implement Authentication:** Set up JWT with httpOnly cookies and refresh token rotation.
5. **Set Up TanStack Query:** Configure QueryClient with appropriate defaults for API communication.
6. **Create API Layer:** Build typed API functions that TanStack Query will call.
7. **Configure Environment:** Set up environment variables for API URLs across environments.
8. **Validate Integration:** Test CORS, auth flow, and API calls end-to-end.
</steps>

<output_format>
TypeScript React code (`.tsx`) with TanStack Query hooks; Python backend code (FastAPI or Flask) with CORS and auth middleware.
</output_format>

<validation>
- Frontend: `npm run test` passes, `npm run type-check` clean
- Backend: `uv run pytest` passes, `uvx ruff check .` clean
- Integration: API calls succeed with proper CORS headers and auth tokens
</validation>

</contract>

## Key Principles

### 1. Backend Framework Selection

#### 1.1 Decision Tree

**When to use FastAPI:**
- Async operations, WebSockets
- Auto-generated OpenAPI docs needed
- ML/AI integration (async preferred)

**When to use Flask:**
- Simple REST API, quick setup
- Large existing Flask codebase
- ML/AI integration (sync acceptable)

**When to use Next.js API Routes:**
- Simple API within Next.js app

**When to use Express:**
- Team has strong Node.js expertise (when user requests)

#### 1.2 Organizational Default Rationale

This organization defaults to Python backends because:
- Team expertise in Python ecosystem
- Integration with data science/ML workflows
- Mature tooling (FastAPI, Pydantic, SQLAlchemy)
- Strong typing with Pydantic models

**Note:** This is an organizational preference, not a universal industry standard. Node.js backends are equally valid when team expertise or project requirements favor them.

### 2. API Communication Patterns

#### 2.1 TanStack Query Setup

```typescript
// src/lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

#### 2.2 Typed API Layer

```typescript
// src/features/users/api/userApi.ts
import { z } from 'zod';

const API_BASE = import.meta.env.VITE_API_URL;

export const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string(),
});

export type User = z.infer<typeof UserSchema>;

export async function fetchUser(userId: string): Promise<User> {
  const response = await fetch(`${API_BASE}/users/${userId}`, {
    credentials: 'include', // Include httpOnly cookies
  });
  if (!response.ok) throw new Error('Failed to fetch user');
  const data = await response.json();
  return UserSchema.parse(data);
}
```

#### 2.3 Query Hook Usage

```typescript
// src/features/users/hooks/useUser.ts
import { useQuery } from '@tanstack/react-query';
import { fetchUser } from '../api/userApi';

export const useUser = (userId: string) => {
  return useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    enabled: !!userId,
  });
};
```

### 3. Authentication Flow

#### 3.1 JWT with httpOnly Cookies (Recommended)

```python
# FastAPI backend - auth endpoint
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/auth/login")
async def login(response: Response, credentials: LoginRequest):
    # Validate credentials, generate JWT
    token = create_access_token(credentials.email)

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="lax",
        max_age=3600,
    )
    return {"message": "Login successful"}
```

#### 3.2 Frontend Auth State

```typescript
// src/features/auth/hooks/useAuth.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export const useAuth = () => {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: fetchCurrentUser,
    retry: false,
  });

  const logout = useMutation({
    mutationFn: logoutApi,
    onSuccess: () => {
      queryClient.setQueryData(['auth', 'me'], null);
      queryClient.invalidateQueries();
    },
  });

  return { user, isLoading, isAuthenticated: !!user, logout };
};
```

### 4. CORS Configuration

#### 4.1 FastAPI CORS

```python
# Development: specific origin
origins = ["http://localhost:5173", "http://localhost:3000"]

# Production: your domain
origins = ["https://app.example.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Never use ["*"] in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

#### 4.2 Flask CORS

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
```

### 5. Environment Management

```bash
# Frontend (.env.development)
VITE_API_URL=http://localhost:8000/api

# Frontend (.env.production)
VITE_API_URL=https://api.example.com

# Backend (.env)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
JWT_SECRET=your-secret-key
```

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: JWT in localStorage**
```typescript
// Bad: Vulnerable to XSS attacks
localStorage.setItem('token', jwt);
```
**Problem:** Any XSS vulnerability exposes the token.

**Correct Pattern:**
```typescript
// Good: httpOnly cookie (set by backend)
fetch('/api/data', { credentials: 'include' });
```


**Anti-Pattern 2: Hardcoded API URLs**
```typescript
// Bad: Hardcoded URL
fetch('http://localhost:8000/api/users');
```
**Problem:** Breaks in production, hard to configure per environment.

**Correct Pattern:**
```typescript
// Good: Environment variable
const API_URL = import.meta.env.VITE_API_URL;
fetch(`${API_URL}/users`);
```


**Anti-Pattern 3: Data Fetching in useEffect**
```typescript
// Bad: Manual state management
useEffect(() => {
  fetch('/api/user').then(setUser);
}, []);
```
**Problem:** No caching, no loading states, race conditions.

**Correct Pattern:**
```typescript
// Good: TanStack Query
const { data: user } = useQuery({
  queryKey: ['user'],
  queryFn: fetchUser,
});
```

## Post-Execution Checklist

- [ ] Backend framework selected (FastAPI/Flask) with clear rationale
- [ ] CORS configured with specific origins (no `*` in production)
- [ ] JWT stored in httpOnly cookies (not localStorage)
- [ ] TanStack Query configured with appropriate defaults
- [ ] API layer created with Zod validation
- [ ] Environment variables set up for API URLs
- [ ] Authentication flow tested end-to-end
- [ ] Both frontend and backend tests passing
- [ ] Development workflow documented (how to run both servers)

## Validation

- **Success checks:**
  - Frontend `npm run test` and `npm run type-check` pass
  - Backend `uv run pytest` and `uvx ruff check .` pass
  - CORS headers present in API responses
  - Cookies set correctly with httpOnly flag
  - API calls work across environments (dev, staging, prod)
- **Negative tests:**
  - Requests from unauthorized origins should be blocked
  - Missing auth token should return 401
  - Invalid JWT should be rejected

> **Investigation Required**
> When applying this rule:
> 1. **Check existing backend** - Is there already a backend? What framework?
> 2. **Review auth requirements** - OAuth? SAML? Simple JWT?
> 3. **Identify API complexity** - Simple CRUD or complex business logic?
> 4. **Check deployment model** - Monorepo? Separate repos? Serverless?

## Output Format Examples

```markdown
MODE: PLAN

Investigation:
- Reviewed project: React + Vite frontend, no existing backend.
- Requirements: User auth, CRUD for projects, file uploads.
- Decision: FastAPI backend (async file handling, auto OpenAPI docs).

Implementation:
1. Create FastAPI backend with CORS and JWT auth
2. Set up TanStack Query in React app
3. Create typed API layer with Zod schemas
```

```python
# Backend: FastAPI with auth middleware
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Project API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/projects")
async def list_projects(user: User = Depends(get_current_user)):
    return await ProjectService.list_for_user(user.id)
```

```bash
# Validation commands
# Frontend
npm run lint && npm run test && npm run type-check

# Backend
uvx ruff check . && uvx ruff format --check . && uv run pytest
```

## References

### External Documentation
- [TanStack Query Docs](https://tanstack.com/query/latest) - Server state management
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Python async API framework
- [Flask Documentation](https://flask.palletsprojects.com/) - Python micro-framework
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html) - JWT security best practices

### Related Rules
- **React Core**: `rules/440-react-core.md` - Frontend patterns
- **Python Core**: `rules/200-python-core.md` - Python tooling and standards
- **FastAPI Core**: `rules/210-python-fastapi-core.md` - FastAPI patterns
- **Flask Core**: `rules/250-python-flask.md` - Flask patterns
- **TypeScript Core**: `rules/430-typescript-core.md` - Type safety patterns
