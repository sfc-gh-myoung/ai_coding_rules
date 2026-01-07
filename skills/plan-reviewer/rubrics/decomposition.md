# Decomposition Rubric (5 points)

## Scoring Criteria

### 5/5 (5 points): Excellent
- Tasks right-sized (30-60 min each)
- Clear parallelization opportunities
- Logical grouping
- Dependencies minimal

### 4/5 (4 points): Good
- Most tasks right-sized
- Some parallelization possible

### 3/5 (3 points): Acceptable
- Tasks somewhat sized
- Limited parallelization

### 2/5 (2 points): Needs Work
- Tasks poorly sized (too large/small)
- No parallelization

### 1/5 (1 point): Poor
- Monolithic tasks (>4 hours)
- No decomposition

## Task Sizing Guidelines

### Optimal Size: 30-60 minutes

**Too large (>2 hours):**
```markdown
❌ Task: Implement user authentication system
```
→ Should be split into smaller tasks

**Right-sized:**
```markdown
✓ Task 1: Add OAuth2 library (30 min)
✓ Task 2: Implement login endpoint (45 min)
✓ Task 3: Implement logout endpoint (30 min)
✓ Task 4: Add JWT token generation (45 min)
✓ Task 5: Add token validation middleware (60 min)
```

**Too small (<15 minutes):**
```markdown
❌ Task 1: Import library
❌ Task 2: Add one line
❌ Task 3: Run formatter
```
→ Should be combined

**Right-sized:**
```markdown
✓ Task: Set up OAuth2 library (import, configure, test - 30 min)
```

## Parallelization Opportunities

### Identify Independent Tasks

**Example with dependencies:**
```markdown
Tasks:
1. Write API endpoints (45 min) - No dependencies
2. Write tests (45 min) - Depends: Task 1
3. Update documentation (30 min) - No dependencies
4. Run linter (15 min) - No dependencies

Parallel execution possible:
- Phase 1 (parallel): Tasks 1, 3, 4 (save ~30 min)
- Phase 2 (serial): Task 2 (depends on Task 1)

Total time: 45min (phase 1) + 45min (phase 2) = 90 min
Sequential time: 135 min
Time saved: 45 min (33%)
```

## Logical Grouping

### Group Related Tasks

**Poor grouping:**
```markdown
1. Update user model
2. Fix CSS bug
3. Add user validation
4. Update navbar
5. Add user tests
```

**Good grouping:**
```markdown
## User Model Updates
1. Update user model (30 min)
2. Add user validation (45 min)
3. Add user tests (45 min)

## UI Updates
4. Fix CSS bug (20 min)
5. Update navbar (25 min)
```

## Dependency Minimization

### Reduce Task Dependencies

**High coupling (poor):**
```markdown
1. Task A → depends on nothing
2. Task B → depends on A
3. Task C → depends on B
4. Task D → depends on C
```
→ Must run sequentially (no parallelization)

**Low coupling (good):**
```markdown
1. Task A → depends on nothing
2. Task B → depends on nothing
3. Task C → depends on A
4. Task D → depends on B
```
→ A+B run parallel, then C+D run parallel

## Task Decomposition Table

Use during review:

| Task | Size (min) | Right-Sized? | Dependencies | Can Parallelize? |
|------|-----------|--------------|--------------|------------------|
| Setup DB | 30 | ✅ Yes | None | ✅ With Task 2 |
| Setup API | 30 | ✅ Yes | None | ✅ With Task 1 |
| Write tests | 240 | ❌ Too large | Tasks 1+2 | ❌ Depends on 1+2 |
| Update docs | 20 | ⚠️  Small | None | ✅ With others |

**Issues:**
- Task 3 too large (240 min → split into 4x60 min tasks)
- Task 4 too small (combine with another)

## Scoring Formula

```
Base score = 5/5 (5 points)

Task sizing:
  All tasks 30-120 min: 5/5
  Most tasks right-sized: 4/5 (-1 point)
  Many wrong-sized: 3/5 (-2 points)
  Mostly wrong-sized: 2/5 (-3 points)
  Monolithic: 1/5 (-4 points)

Additional deductions:
  No parallelization opportunities: -1 point
  Poor grouping: -0.5 points
  High coupling: -0.5 points

Minimum score: 1/5 (1 point)
```

## Common Decomposition Issues

### Issue 1: Monolithic Task

**Problem:**
```markdown
Task: Build entire authentication system (8 hours)
```

**Fix:**
```markdown
## Authentication System (8 tasks, 4-5 hours total)

Phase 1 (parallel):
1. Install OAuth2 library (30 min)
2. Design database schema (45 min)
3. Create API contract (30 min)

Phase 2 (parallel):
4. Implement login endpoint (60 min) - Depends: 1, 3
5. Implement logout endpoint (30 min) - Depends: 1, 3
6. Add database models (45 min) - Depends: 2

Phase 3 (parallel):
7. Write tests (60 min) - Depends: 4, 5, 6
8. Update documentation (30 min) - Depends: 4, 5
```

### Issue 2: Overly Granular

**Problem:**
```markdown
1. Import pytest (5 min)
2. Create test file (5 min)
3. Write first test (10 min)
4. Write second test (10 min)
5. Run tests (5 min)
```

**Fix:**
```markdown
1. Write test suite for auth module (45 min)
   - Import pytest
   - Create test_auth.py
   - Write 5 test cases
   - Run and verify
```

### Issue 3: Poor Grouping

**Problem:**
```markdown
1. Update user model
2. Update order model
3. Add user validation
4. Add order validation
```

**Fix:**
```markdown
## User Module
1. Update user model + validation (45 min)

## Order Module
2. Update order model + validation (45 min)

(Can run in parallel)
```

### Issue 4: Sequential Dependency Chain

**Problem:**
```markdown
1. Task A (30 min)
2. Task B (30 min) - depends A
3. Task C (30 min) - depends B
4. Task D (30 min) - depends C
Total: 120 min (must run sequentially)
```

**Fix (reduce dependencies):**
```markdown
1. Task A (30 min) - independent
2. Task B (30 min) - independent
3. Task C (30 min) - depends A
4. Task D (30 min) - depends B
Total: 60 min (A+B parallel, then C+D parallel)
```

## Decomposition Checklist

During review, verify:

- [ ] All tasks 15-120 minutes
- [ ] No monolithic tasks (>4 hours)
- [ ] No micro-tasks (<15 minutes)
- [ ] Related tasks grouped logically
- [ ] Parallelization opportunities identified
- [ ] Dependencies minimized where possible
- [ ] Each task has clear inputs/outputs
- [ ] Task breakdown reduces risk
