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

## Score Decision Matrix (ENHANCED)

**Purpose:** Convert task size distribution and organization metrics into dimension score. No interpretation needed - just look up the tier.

### Input Values

From completed worksheet:
- **In-Range %:** (Optimal 15-60min + Acceptable 61-120min) / Total tasks × 100
- **Monolithic Count:** Tasks >240 min (4 hours)
- **Parallelization:** Explicitly identified / Mentioned / Not mentioned
- **Grouping:** Logical with phases / Present informal / Tasks scattered

### Scoring Table

| In-Range % | Monolithic | Parallelization | Grouping | Tier | Raw Score | × Weight | Points |
|------------|------------|-----------------|----------|------|-----------|----------|--------|
| 100% | 0 | Identified | Logical | Perfect | 10/10 | × 0.5 | 5 |
| 95-99% | 0 | Identified | Logical | Near-Perfect | 9/10 | × 0.5 | 4.5 |
| 90-94% | 0 | Identified | Present | Excellent | 8/10 | × 0.5 | 4 |
| 85-89% | 0 | Some | Present | Good | 7/10 | × 0.5 | 3.5 |
| 80-84% | 0 | Some | Present | Acceptable | 6/10 | × 0.5 | 3 |
| 70-79% | 1 | Limited | Some | Borderline | 5/10 | × 0.5 | 2.5 |
| 60-69% | 1 | Limited | Some | Below Standard | 4/10 | × 0.5 | 2 |
| 50-59% | 2 | None | Poor | Poor | 3/10 | × 0.5 | 1.5 |
| 40-49% | 2-3 | None | Poor | Very Poor | 2/10 | × 0.5 | 1 |
| 30-39% | 3-4 | None | None | Critical | 1/10 | × 0.5 | 0.5 |
| <30% | 5+ | None | None | No Decomposition | 0/10 | × 0.5 | 0 |

### Tie-Breaking Algorithm (Deterministic)

**When in-range % falls exactly on tier boundary:**

1. **Check Monolithic Count:** If monolithic = 0 → HIGHER tier
2. **Check Parallelization:** If explicitly identified with tasks → HIGHER tier
3. **Check Grouping Quality:** If logical phases with names → HIGHER tier
4. **Default:** HIGHER tier (decomposition is generally good)

### Edge Cases

**Edge Case 1: Small tasks intentionally grouped**
- **Example:** 10 tasks under 15 min each, logically grouped
- **Rule:** Don't penalize small tasks if grouped logically
- **Rationale:** Grouping compensates for granularity

**Edge Case 2: Large task with checkpoint structure**
- **Example:** 3-hour task with clear milestones every 30 min
- **Rule:** Count as acceptable if checkpoints enable progress tracking
- **Rationale:** Checkpoints provide decomposition benefit

**Edge Case 3: Variable task sizes by nature**
- **Example:** "Write unit tests" (varies by coverage needed)
- **Rule:** Estimate based on plan scope, not theoretical maximum
- **Rationale:** Size assessment should be practical

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

## Non-Issues (Do NOT Count)

**Purpose:** Eliminate false positives by explicitly defining what is NOT a decomposition issue.

### Pattern 1: Small Tasks (<15 min) Grouped Logically

**Example:**
```markdown
Task 1.1: Setup auth module (30 min)
  - Import library (5 min)
  - Create test file (5 min)
  - Write initial tests (10 min)
```
**Why NOT an issue:** Small items are sub-steps, parent task is correct size  
**Overlap check:** Not Success Criteria - these are implementation details  
**Correct action:** Count parent task, not sub-steps

### Pattern 2: Implicit Parallelization from Independence

**Example:**
```markdown
Phase 1: Independent setup tasks
- Task 1.1: Setup frontend (no deps)
- Task 1.2: Setup backend (no deps)
- Task 1.3: Setup database (no deps)
```
**Why NOT an issue:** Independence implies parallelization  
**Overlap check:** Not Dependencies - ordering clear  
**Correct action:** Count "no deps" annotation as parallelization identification

### Pattern 3: Section Headers Provide Grouping

**Example:**
```markdown
### User Authentication
- Task 1.1: Login
- Task 1.2: Logout
### Data Migration
- Task 2.1: Export
- Task 2.2: Import
```
**Why NOT an issue:** Section headers provide logical grouping  
**Overlap check:** N/A - structure is present  
**Correct action:** Count section headers as logical grouping

### Pattern 4: Large Tasks (>120 min) with Checkpoint Structure

**Example:**
```markdown
Task 3.1: Implement search (180 min)
  Checkpoint 1: Basic search (60 min)
  Checkpoint 2: Filters (60 min)
  Checkpoint 3: Sorting (60 min)
```
**Why NOT an issue:** Internal checkpoints provide effective decomposition  
**Overlap check:** N/A - risk is mitigated  
**Correct action:** Count checkpointed large tasks as acceptable

## Complete Pattern Inventory

**Purpose:** Eliminate interpretation variance by providing exhaustive lists. If it's not in this list, don't invent it. Match case-insensitive.

### Category 1: Duration Indicators (20 Patterns)

**Explicit Duration Patterns:**
1. "X minutes"
2. "X min"
3. "X hours"
4. "X hr"
5. "~X min"
6. "approximately X"
7. "about X minutes"
8. "around X hours"
9. "X-Y minutes" (range)
10. "≤X min"
11. "≥X min"
12. "(30 min)"
13. "[1 hour]"
14. "Duration: X"
15. "Time: X"
16. "Estimate: X"
17. "ETA: X"
18. "takes X"
19. "requires X"
20. "X min effort"

**Regex Patterns:**
```regex
\b(\d+)\s*(min|minutes?|hrs?|hours?)\b
\b(~|approximately|about|around)\s*(\d+)\s*(min|hours?)\b
\b(\d+)\s*-\s*(\d+)\s*(min|hours?)\b
\b(duration|time|estimate|ETA)\s*:\s*(\d+)\s*(min|hours?)\b
```

### Category 2: Task Heading Indicators (15 Patterns)

**Task-Level Headings (COUNTABLE):**
1. "### Task X.Y"
2. "### Task X.Y:"
3. "#### Task X.Y"
4. "**Task X.Y:**"
5. "Task X.Y -"
6. "Step X:"
7. "Phase X Task Y"
8. "X.Y [Task Name]"
9. "[ ] Task:"
10. "- [ ] Task"

**Sub-Step Patterns (NOT COUNTABLE):**
11. "1. [action]" (numbered under task)
12. "- [action]" (bullet under task)
13. "  - [sub-item]" (indented)
14. "    1. [sub-step]" (indented numbered)
15. "* [detail]"

**Regex Patterns:**
```regex
# Countable tasks
^#{2,4}\s*Task\s+\d+\.?\d*\s*[:\-]?\s*
^\*\*Task\s+\d+\.?\d*\s*[:\-]\*\*
^Step\s+\d+\s*:

# Sub-steps (not countable)
^\s+\d+\.\s+
^\s+-\s+
^\s+\*\s+
```

### Category 3: Size Category Boundaries

**Size Classifications:**
| Category | Duration | Classification |
|----------|----------|----------------|
| Too Small | <15 min | Combine with related |
| Optimal | 15-60 min | Ideal |
| Acceptable | 61-120 min | OK |
| Large | 121-240 min | Should split |
| Monolithic | >240 min | MUST split |

**Boundary Clarifications:**
- 15 min exactly = Optimal (inclusive)
- 60 min exactly = Optimal (inclusive)
- 61 min exactly = Acceptable
- 120 min exactly = Acceptable (inclusive)
- 121 min exactly = Large
- 240 min exactly = Large (inclusive)
- 241 min exactly = Monolithic

### Category 4: Parallelization Indicators (15 Patterns)

**Explicit Parallelization:**
1. "can run in parallel"
2. "can run simultaneously"
3. "parallelizable"
4. "concurrent"
5. "independent tasks"
6. "no dependencies"
7. "no deps"
8. "(parallel)"
9. "at the same time"
10. "while X runs"

**Sequential Indicators:**
11. "depends on"
12. "after X"
13. "requires X first"
14. "blocked by"
15. "sequential"

**Regex Patterns:**
```regex
# Parallel
\b(parallel|concurrent|simultaneous|independent)\b
\b(can\s+run|run)\s+(in\s+parallel|simultaneously|concurrently)\b
\bno\s+(dependencies|deps)\b

# Sequential
\b(depends?\s+on|after|requires?\s+first|blocked\s+by|sequential)\b
```

### Category 5: Grouping Indicators (10 Patterns)

**Logical Grouping Present:**
1. "## Phase X:"
2. "### Phase X:"
3. "## [Section Name]"
4. "--- [Separator]"
5. "**[Group Name]**"
6. "Phase X Tasks"
7. "[Category] Tasks"
8. Numbered phases (Phase 1, Phase 2)
9. Named sections (Setup, Implementation, Testing)
10. Horizontal rules between groups

**No/Poor Grouping:**
- Tasks listed without section headers
- Random ordering
- Mixed concerns in same list

**Regex Patterns:**
```regex
^#{2,3}\s*(Phase|Section|Part)\s+\d+
^#{2,3}\s*(Setup|Implementation|Testing|Validation|Deployment|Cleanup)
^\*\*[A-Z][a-z]+\s+(Tasks?|Steps?)\*\*
```

### Category 6: Checkpoint Indicators (Large Task Mitigation)

**Internal Checkpoints:**
- "Checkpoint X:"
- "Milestone:"
- "At X min mark:"
- "After X min:"
- "Progress check:"
- "Save point:"

**Checkpoint Presence = Large Task Acceptable:**
- 180 min task with 3 × 60 min checkpoints = OK
- 180 min task without checkpoints = Should split

**Regex Patterns:**
```regex
\b(checkpoint|milestone|progress\s+check|save\s+point)\s*:?\s*\d*\b
\bat\s+(\d+)\s*(min|hour)\s+mark\b
```

### Ambiguous Cases Resolution

**Case 1: Sub-step vs task**

**Pattern:** Numbered item under task heading

**Ambiguity:** Is this a countable task?

**Resolution Rule:**
- Apply Task Counting Standard from Success Criteria
- Has independent deliverable = Task
- Implementation detail under task = Sub-step
- Use heading level and indentation as guide

**Case 2: Duration not specified**

**Pattern:** "Implement login feature" (no duration)

**Ambiguity:** How to classify size?

**Resolution Rule:**
- Use heuristics based on complexity
- Simple CRUD operation: ~30-60 min
- Feature with tests: ~60-120 min
- Complex feature: ~120+ min
- When uncertain, don't count toward in-range %

**Case 3: Range given instead of point estimate**

**Pattern:** "30-60 min"

**Ambiguity:** Use min, max, or midpoint?

**Resolution Rule:**
- Use MIDPOINT of range: (30+60)/2 = 45 min
- Classify based on midpoint
- Note range in worksheet

**Case 4: Parallel opportunity not explicitly stated**

**Pattern:** Tasks with "no deps" annotation

**Ambiguity:** Is "no deps" = parallelization identified?

**Resolution Rule:**
- "No deps" implies parallel-safe
- Count as parallelization opportunity identified
- More explicit is better but annotation sufficient

**Case 5: Section headers provide grouping**

**Pattern:** `### User Authentication` followed by tasks

**Ambiguity:** Does section header = logical grouping?

**Resolution Rule:**
- Section headers = logical grouping present
- Don't require explicit "Phase X" format
- Semantic grouping (by feature/concern) is valid

**Case 6: Large task with internal structure**

**Pattern:** 3-hour task with clear 60-min milestones

**Ambiguity:** Monolithic or structured?

**Resolution Rule:**
- Internal checkpoints every 60 min = acceptable
- Count as Large-but-structured (don't penalize as Monolithic)
- Note: "Large task with checkpoints - acceptable"

**Case 7: Task duration in different format**

**Pattern:** "1.5 hours" or "90min" or "1h 30m"

**Ambiguity:** How to parse?

**Resolution Rule:**
- Convert all to minutes for comparison
- 1.5 hours = 90 min
- 1h 30m = 90 min
- Use standardized minutes for worksheet

**Case 8: Phase-level vs task-level duration**

**Pattern:** "Phase 1 (2 hours)" containing 4 tasks

**Ambiguity:** Is 2 hours the task size or phase size?

**Resolution Rule:**
- Phase duration ≠ task duration
- Estimate individual task durations within phase
- Phase duration = sum of tasks (use for validation)

## Anti-Pattern Examples (Common Mistakes)

**❌ WRONG (False Positive):**
- Flagged: "Task too small: Import library (5 min)"
- Rationale given: "Tasks should be 15-120 min"
- Problem: This is a sub-step, not a task
- Impact: Incorrect task count, wrong in-range %

**✅ CORRECT:**
- Sub-steps not counted as separate tasks
- Rationale: Use Task Counting Standard from Success Criteria
- Condition: Would be flagged IF it were a Task heading at same level

**❌ WRONG (False Positive):**
- Flagged: "No parallelization mentioned"
- Rationale given: "Parallelization opportunities not identified"
- Problem: Plan marks tasks as "no deps" (implies parallel-safe)
- Impact: Incorrect -1 point deduction

**✅ CORRECT:**
- "No deps" annotation counts as parallelization identification
- Rationale: Independence = parallelization opportunity
- Condition: Would be flagged IF all tasks have dependencies

## Ambiguous Case Resolution Rules (REQUIRED)

**Purpose:** Provide deterministic scoring when task sizing/structure is borderline.

### Rule 1: Same-File Context
**Count as task if:** Has task-level heading (### Task X.Y or similar) with deliverable  
**Count as sub-step if:** Numbered item within a task without independent deliverable

### Rule 2: Adjectives Without Quantifiers
**Estimate as stated if:** Duration explicitly provided ("30 min", "1 hour")  
**Estimate as unknown if:** No duration - use Task Counting Standard heuristics

### Rule 3: Pattern Variations
**Count as parallelizable if:** "no deps", "independent", or lack of ordering constraints  
**Count as sequential if:** "depends on", "after", or explicit ordering required

### Rule 4: Default Resolution
**Still uncertain after Rules 1-3?** → Count as sub-step (for task counting), sequential (for parallelization)

### Borderline Cases Template

Document borderline decisions in your worksheet:

```markdown
### Item: "[Task/Step Name]"
- **Decision:** Task [Y/N], Duration estimate [X min], Parallel [Y/N]
- **Rule Applied:** [1/2/3/4]
- **Reasoning:** [Explain why this classification]
- **Alternative:** [Other interpretation and why rejected]
- **Confidence:** [HIGH/MEDIUM/LOW]
```

## Mandatory Counting Worksheet (REQUIRED)

**CRITICAL:** You MUST create and fill this worksheet BEFORE calculating score.

### Worksheet Template

**Task Size Distribution:**
| Size Category | Duration | Task Count | Task Names |
|---------------|----------|------------|------------|
| Too small | <15 min | ___ | |
| Optimal | 15-60 min | ___ | |
| Acceptable | 61-120 min | ___ | |
| Large | 121-240 min | ___ | |
| Monolithic | >240 min | ___ | |
| **TOTAL** | | **___** | |
| **IN-RANGE** | | **___** | |
| **IN-RANGE %** | | **___%** | |

**Parallelization Assessment:**
| Aspect | Status |
|--------|--------|
| Independent tasks identified? | Y/N |
| "Can run simultaneously" noted? | Y/N |
| Dependency-free tasks grouped? | Y/N |

**Grouping Assessment:**
| Aspect | Status |
|--------|--------|
| Related tasks grouped together? | Y/N |
| Logical phases or sections? | Y/N |
| Clear separation of concerns? | Y/N |

### Counting Protocol

1. List all tasks with duration estimates
2. Classify each task by size category
3. Calculate in-range percentage: (optimal + acceptable) / total × 100
4. Assess parallelization and grouping
5. Use Score Decision Matrix to determine raw score
6. Include completed worksheet in review output

## Inter-Run Consistency Target

**Expected variance:** ±10% in-range calculation

**Verification:**
- Use duration estimates from plan
- Apply size categories strictly
- Count parallelization mentions

**If variance exceeds threshold:**
- Re-verify task durations
- Apply category boundaries strictly
