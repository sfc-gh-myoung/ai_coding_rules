# Decomposition Rubric (5 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 1
**Points:** Raw × (1/2) = Raw × 0.5

## Scoring Criteria

### 10/10 (5 points): Perfect
- 100% tasks within 15-120 min range
- 0 monolithic tasks (>4 hours)
- Parallelization opportunities identified
- Logical grouping present
- Dependencies minimized

### 9/10 (4.5 points): Near-Perfect
- 95-99% tasks within range
- 0 monolithic tasks
- Parallelization identified
- Logical grouping present

### 8/10 (4 points): Excellent
- 90-94% tasks within range
- 0 monolithic tasks
- Parallelization identified
- Grouping present

### 7/10 (3.5 points): Good
- 85-89% tasks within range
- 0 monolithic tasks
- Some parallelization noted
- Grouping present

### 6/10 (3 points): Acceptable
- 80-84% tasks within range
- 0 monolithic tasks
- Some parallelization noted
- Grouping present

### 5/10 (2.5 points): Borderline
- 70-79% tasks within range
- 1 monolithic task
- Limited parallelization
- Some grouping

### 4/10 (2 points): Needs Work
- 60-69% tasks within range
- 1 monolithic task
- Limited parallelization
- Some grouping

### 3/10 (1.5 points): Poor
- 50-59% tasks within range
- 2 monolithic tasks
- No parallelization
- Poor grouping

### 2/10 (1 point): Very Poor
- 40-49% tasks within range
- 2-3 monolithic tasks
- No parallelization
- Poor grouping

### 1/10 (0.5 points): Inadequate
- 30-39% tasks within range
- 3-4 monolithic tasks
- No parallelization
- No grouping

### 0/10 (0 points): No Decomposition
- <30% tasks within range
- 5+ monolithic tasks
- No decomposition
- No grouping

## Counting Definitions

### Task Size Classification

**Acceptable range:** 15-120 minutes

**Size categories:**
- Too small (<15 min): Combine with related tasks
- Optimal (15-60 min): Ideal
- Acceptable (61-120 min): OK
- Large (121-240 min): Should split
- Monolithic (>240 min): MUST split

### Task Size Calculation

**Count tasks by category (fill in during review):**

**Task Size Inventory:**
- Too small (<15 min): ___ tasks
- Optimal (15-60 min): ___ tasks
- Acceptable (61-120 min): ___ tasks
- Large (121-240 min): ___ tasks
- Monolithic (>240 min): ___ tasks

**In-range calculation:**
```
In-range % = (optimal + acceptable) / total tasks × 100
```

### Parallelization Assessment

**Check for:**
- Independent tasks identified
- "Can run simultaneously" noted
- Dependency-free tasks grouped

**Scoring:**
- Explicitly identified with tasks: Full credit
- Mentioned but not detailed: -0.5 points
- Not mentioned: -1 point

### Grouping Assessment

**Check for:**
- Related tasks grouped together
- Logical phases or sections
- Clear separation of concerns

**Scoring:**
- Logical with phase names: Full credit
- Present but informal: -0.5 points
- Tasks scattered randomly: -1 point

### Dependency Chain Assessment

**Measure coupling:**
- Low: Most tasks can run independently
- Medium: Some sequential chains
- High: Long sequential chains (A->B->C->D->E)

**Scoring:**
- Low (most independent): Full credit
- Medium (some chains): -0.5 points
- High (long chains): -1 point

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (5 pts):** 100% in-range, 0 monolithic, parallelization identified, logical grouping
- **9/10 (4.5 pts):** 95-99% in-range, 0 monolithic, parallelization identified, logical grouping
- **8/10 (4 pts):** 90-94% in-range, 0 monolithic, parallelization identified, grouping present
- **7/10 (3.5 pts):** 85-89% in-range, 0 monolithic, some parallelization, grouping present
- **6/10 (3 pts):** 80-84% in-range, 0 monolithic, some parallelization, grouping present
- **5/10 (2.5 pts):** 70-79% in-range, 1 monolithic, limited parallelization, some grouping
- **4/10 (2 pts):** 60-69% in-range, 1 monolithic, limited parallelization, some grouping
- **3/10 (1.5 pts):** 50-59% in-range, 2 monolithic, no parallelization, poor grouping
- **2/10 (1 pt):** 40-49% in-range, 2-3 monolithic, no parallelization, poor grouping
- **1/10 (0.5 pts):** 30-39% in-range, 3-4 monolithic, no parallelization, no grouping
- **0/10 (0 pts):** <30% in-range, 5+ monolithic, no decomposition, no grouping

## Task Sizing Guidelines

### Optimal Size: 15-60 minutes

**Why this range:**
- Small enough to complete in one focus session
- Large enough to be meaningful
- Easy to track progress
- Reasonable checkpoint frequency

### Too Large (>120 min) - Split Required

```markdown
BAD: Implement user authentication system (8 hours)

GOOD (Split into):
1. Install OAuth2 library (30 min)
2. Design database schema (45 min)
3. Implement login endpoint (60 min)
4. Implement logout endpoint (30 min)
5. Add JWT token generation (45 min)
6. Add token validation middleware (60 min)
7. Write unit tests (60 min)
8. Update documentation (30 min)
```

### Too Small (<15 min) - Combine Required

```markdown
BAD (too granular):
1. Import library (5 min)
2. Create test file (5 min)
3. Write first test (10 min)
4. Run formatter (5 min)

GOOD (Combined):
1. Set up test suite for auth module (30 min)
   - Import pytest
   - Create test_auth.py
   - Write 3 test cases
   - Run and format
```

## Parallelization Identification

### Explicit Format (Good)

```markdown
## Phase 1 (Parallel)
Tasks 1, 3, 4 can run simultaneously (no dependencies)
- Task 1: Install deps (30 min)
- Task 3: Update docs (30 min)
- Task 4: Run linter (15 min)

## Phase 2 (Sequential)
Task 2 depends on Task 1
- Task 2: Run tests (45 min) - Depends: Task 1

Time saved: 45 min (30% reduction)
```

### Implicit (Needs Improvement)

```markdown
Tasks:
1. Install deps
2. Run tests
3. Update docs
4. Run linter

(No parallelization noted)
```

## Logical Grouping

### Good Grouping

```markdown
## User Model Updates
1. Update user model (30 min)
2. Add user validation (45 min)
3. Add user tests (45 min)

## UI Updates
4. Fix CSS bug (20 min)
5. Update navbar (25 min)

## Deployment
6. Deploy to staging (30 min)
7. Run integration tests (45 min)
```

### Poor Grouping

```markdown
1. Update user model
2. Fix CSS bug
3. Add user validation
4. Update navbar
5. Add user tests
6. Deploy to staging
7. Run integration tests
```

## Task Decomposition Table

Use during review:

**Task Decomposition Inventory (example):**
- Setup DB (30 min): In range (Yes), Dependencies (None), Parallel (Yes)
- Setup API (30 min): In range (Yes), Dependencies (None), Parallel (Yes)
- Write tests (240 min): In range (No - Large), Dependencies (Tasks 1+2), Parallel (No)
- Update docs (20 min): In range (Yes), Dependencies (None), Parallel (Yes)
- Deploy (480 min): In range (No - Monolithic), Dependencies (All), Parallel (No)

**Issues:**
- Task 3: 240 min - Split into 4x60 min tasks
- Task 5: 480 min - Split into phases

## Worked Example

**Target:** Feature development plan

### Step 1: List Tasks with Estimates

**Task Duration Inventory:**
- Design API: 120 min
- Implement endpoints: 180 min
- Write tests: 90 min
- Update docs: 30 min
- Deploy: 45 min

### Step 2: Classify Sizes

**Size Classification:**
- Too small: 0 tasks
- Optimal: 2 tasks (docs 30min, deploy 45min)
- Acceptable: 2 tasks (design 120min, tests 90min)
- Large: 1 task (endpoints 180min)
- Monolithic: 0 tasks

**In-range:** 4/5 = 80%

### Step 3: Check Parallelization

```markdown
Plan states: "Design must complete before implementation"
No other parallelization mentioned
```

**Assessment:** Limited parallelization (-0.5)

### Step 4: Check Grouping

```markdown
Tasks listed sequentially
No phase grouping
```

**Assessment:** Present but informal (-0.5)

### Step 5: Calculate Score

**Component Assessment:**
- In-range: 80% = 4/5 baseline
- Monolithic: 0 = OK
- Parallelization: Limited = -0.5 points
- Grouping: Informal = -0.5 points

**Total deductions:** -1 point
**Final:** 6/10 - 1 = 5/10 (2.5 points)

### Step 6: Document in Review

```markdown
## Decomposition: 5/10 (2.5 points)

**Task sizing:** 80% in range (4/5)

**Size Distribution:**
- Optimal (15-60): 2 tasks
- Acceptable (61-120): 2 tasks
- Large (121-240): 1 task
- Monolithic (>240): 0 tasks

**Issues:**
- "Implement endpoints" (180 min) should be split

**Parallelization:** Limited
- Only sequential dependency noted
- No parallel opportunities identified

**Grouping:** Informal
- Tasks listed sequentially
- No phase structure

**Recommended fixes:**
1. Split "Implement endpoints" into 3 tasks (60 min each)
2. Identify parallel tasks (design + docs can overlap)
3. Add phase grouping (Setup, Implementation, Validation)
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

## Inter-Run Consistency Target

**Expected variance:** ±10% in-range calculation

**Verification:**
- Use duration estimates from plan
- Apply size categories strictly
- Count parallelization mentions

**If variance exceeds threshold:**
- Re-verify task durations
- Apply category boundaries strictly
