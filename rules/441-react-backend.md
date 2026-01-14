# React Backend Integration: Python-First Full-Stack Patterns

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.0.1
**LastUpdated:** 2026-01-13
**Keywords:** React backend, FastAPI, Flask, Python API, CORS, JWT, authentication, API integration, full-stack, Express alternative, fetch, axios, TanStack Query backend, Next.js API routes, httpOnly cookies
**TokenBudget:** ~3050
**ContextTier:** High
**Depends:** 440-react-core.md, 200-python-core.md

## Scope

**What This Rule Covers:**
Establishes backend integration patterns for React applications, with Python (FastAPI/Flask) as the organizational default. Covers API communication, authentication flows, CORS configuration, and type sharing between frontend and backend.

**When to Load This Rule:**
- Building full-stack React applications
- Integrating React frontend with Python backend
- Implementing authentication flows
- Configuring CORS for API communication
- Choosing backend framework for React apps
- Setting up API layer with TanStack Query

## References

### Dependencies

**Must Load First:**
- **440-react-core.md** - React patterns and architecture
- **200-python-core.md** - Python development standards

**Related:**
- **210-python-fastapi-core.md** - FastAPI patterns and best practices
- **250-python-flask.md** - Flask patterns and best practices

### External Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Modern async Python web framework
- [Flask Documentation](https://flask.palletsprojects.com/) - Mature Python web framework
- [TanStack Query](https://tanstack.com/query/latest) - Async state management for React
- [CORS MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) - Cross-Origin Resource Sharing

## Contract

### Inputs and Prerequisites

- React application (per 440-react-core.md)
- Python environment (per 200-python-core.md)
- Understanding of REST API patterns
- Knowledge of authentication flows

### Mandatory

- TanStack Query for API state management
- httpOnly cookies for JWT storage
- Environment variables for API URLs
- CORS middleware on backend
- Type-safe API layer

### Forbidden

- Node.js/Express backend (unless user explicitly requests)
- JWT in localStorage (security risk)
- Hardcoded API URLs
- `*` CORS origin in production
- Raw fetch in useEffect for data fetching

### Execution Steps

1. **Determine Backend Need:** Assess if Next.js API routes suffice or separate backend required
2. **Select Framework:** Choose FastAPI (async, auto-docs) or Flask (simpler) based on requirements
3. **Configure CORS:** Set up CORS middleware with specific origins for dev and production
4. **Implement Authentication:** Set up JWT with httpOnly cookies and refresh token rotation
5. **Set Up TanStack Query:** Configure QueryClient with appropriate defaults for API communication
6. **Create API Layer:** Build typed API functions that TanStack Query will call
7. **Configure Environment:** Set up environment variables for API URLs across environments
8. **Validate Integration:** Test CORS, auth flow, and API calls end-to-end

### Output Format

TypeScript React code (`.tsx`) with:
- TanStack Query hooks for API calls
- Type-safe API layer
- Environment-based configuration

Python backend code (FastAPI or Flask) with:
- CORS middleware configured
- Authentication middleware
- Type hints and validation

### Validation

**Pre-Task-Completion Checks:**
- [ ] Determine if separate backend is needed (vs Next.js API routes)
- [ ] Identify backend framework: FastAPI (async, OpenAPI) vs Flask (simpler, mature)
- [ ] Check existing backend code/patterns before adding new endpoints
- [ ] Verify CORS configuration exists for development and production
- [ ] Confirm authentication strategy (JWT, session, OAuth)
- [ ] Review environment variable setup for API URLs
- [ ] TanStack Query configured with proper defaults
- [ ] API layer is type-safe
- [ ] Authentication uses httpOnly cookies
- [ ] CORS allows specific origins only

**Success Criteria:**
- Frontend: `npm run test` passes, `npm run type-check` clean
- Backend: `uv run pytest` passes, `uvx ruff check .` clean
- Integration: API calls succeed with proper CORS headers and auth tokens
- No CORS errors in browser console
- JWT tokens stored securely in httpOnly cookies

### Design Principles

- **Python Backend Default:** Use FastAPI or Flask unless explicitly requested otherwise
- **Secure Authentication:** Store JWT in httpOnly cookies, never localStorage
- **Type Safety:** Share types between frontend and backend where possible
- **Environment Configuration:** Use environment variables for all URLs and secrets
- **Proper CORS:** Configure specific origins, never use wildcard in production

### Post-Execution Checklist

- [ ] Backend framework selected (FastAPI or Flask)
- [ ] CORS middleware configured with specific origins
- [ ] Authentication implemented with httpOnly cookies
- [ ] TanStack Query configured for API communication
- [ ] Environment variables set up for API URLs
- [ ] Frontend tests pass (`npm run test`)
- [ ] Backend tests pass (`uv run pytest`)
- [ ] Type checking clean on both frontend and backend
- [ ] No CORS errors in browser console
- [ ] API calls work end-to-end with authentication

## Key Principles

### Backend Framework Selection

#### Decision Tree

**When to use FastAPI:**
- Async operations, WebSockets
- Auto-generated OpenAPI docs needed
- ML/AI integration (async preferred)

**When to use Flask:**
- REST API with <10 endpoints, quick setup
- Large existing Flask codebase
- ML/AI integration (sync acceptable)

**When to use Next.js API Routes:**
- Simple API within Next.js app

**When to use Express:**
- Team has strong Node.js expertise (when user requests)

#### Organizational Default Rationale

This organization defaults to Python backends because:
- Team expertise in Python ecosystem
- Integration with data science/ML workflows
- Mature tooling (FastAPI, Pydantic, SQLAlchemy)
- Strong typing with Pydantic models

**Note:** This is an organizational preference, not a universal industry standard. Node.js backends are equally valid when team expertise or project requirements favor them.

### API Communication Patterns

#### TanStack Query Setup

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

#### Typed API Layer

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

#### Query Hook Usage

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

### Authentication Flow

#### JWT with httpOnly Cookies (Recommended)

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

### CORS Configuration

#### FastAPI CORS

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

### Environment Management

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
