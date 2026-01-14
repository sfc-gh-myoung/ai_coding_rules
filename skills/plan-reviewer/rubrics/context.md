# Context Rubric (5 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 1
**Points:** Raw × (1/2) = Raw × 0.5

## Scoring Criteria

### 10/10 (5 points): Perfect
- 100% of key decisions have rationale
- All non-obvious choices explained
- Assumptions documented explicitly (4/4 types)
- Tradeoffs acknowledged with alternatives
- Context preserved across tasks

### 9/10 (4.5 points): Near-Perfect
- 95-99% of key decisions have rationale
- All non-obvious choices explained
- Assumptions documented (4/4 types)
- Tradeoffs acknowledged

### 8/10 (4 points): Excellent
- 90-94% of key decisions have rationale
- Most non-obvious choices explained
- Assumptions documented (4/4 types)
- Tradeoffs acknowledged

### 7/10 (3.5 points): Good
- 85-89% of key decisions have rationale
- Most non-obvious choices explained
- Most assumptions documented (3/4 types)
- Some tradeoffs acknowledged

### 6/10 (3 points): Acceptable
- 80-84% of key decisions have rationale
- Most non-obvious choices explained
- Most assumptions documented (3/4 types)
- Some tradeoffs acknowledged

### 5/10 (2.5 points): Borderline
- 70-79% of key decisions have rationale
- Some non-obvious choices explained
- Some assumptions documented (2/4 types)
- Few tradeoffs

### 4/10 (2 points): Needs Work
- 60-69% of key decisions have rationale
- Some non-obvious choices explained
- Some assumptions documented (2/4 types)
- Few tradeoffs

### 3/10 (1.5 points): Poor
- 50-59% of key decisions have rationale
- Few explanations
- Assumptions sparse (1/4 types)
- No tradeoffs

### 2/10 (1 point): Very Poor
- 40-49% of key decisions have rationale
- Few explanations
- Assumptions sparse (1/4 types)
- No tradeoffs

### 1/10 (0.5 points): Inadequate
- 30-39% of key decisions have rationale
- No explanations
- No assumptions (0/4 types)
- No tradeoffs

### 0/10 (0 points): No Context
- <30% of key decisions have rationale
- No explanations
- No assumptions
- No tradeoffs

## Counting Definitions

### Key Decisions

**Definition:** Choices that affect implementation approach, tool selection, or architecture.

**Key decision types (count each):**
- Tool/technology selection
- Architecture choices
- Configuration values
- Ordering decisions
- Scope boundaries
- Resource allocations

### Rationale Coverage

**Step 1:** Count key decisions in plan
**Step 2:** Count decisions with explicit "why" or rationale
**Step 3:** Calculate coverage

```
Rationale coverage % = (decisions with rationale / total key decisions) × 100
```

### Non-Obvious Choices

**Definition:** Values or selections that aren't self-evident defaults.

**Non-obvious examples:**
- Specific timeout values (why 30s?)
- Connection pool sizes (why 100?)
- Retry counts (why 3?)
- Memory allocations (why 2GB?)
- Batch sizes (why 1000?)

**Count:**
- Non-obvious choices identified
- Non-obvious choices with explanation

### Assumption Documentation

**Required assumption types:**

**Assumption Type Checklist:**
- Data assumptions (volumes, formats): Documented?
- Environment assumptions (resources): Documented?
- Behavior assumptions (user patterns): Documented?
- External assumptions (APIs, services): Documented?

**Scoring:**
- 4/4 types documented: Full credit
- 3/4 types documented: -0.5 points
- 2/4 types documented: -1 point
- 0-1/4 types documented: -2 points

### Tradeoff Acknowledgment

**Requirements:**
- Pros and cons listed
- Decision justification
- Alternatives considered

**Scoring:**
- Present with alternatives: Full credit
- Present without alternatives: -0.5 points
- Missing: -1 point

## Score Decision Matrix

**Score Tier Criteria:**
- **10/10 (5 pts):** 100% rationale coverage, all non-obvious explained, 4/4 assumption types, tradeoffs with alternatives
- **9/10 (4.5 pts):** 95-99% rationale coverage, all non-obvious explained, 4/4 assumption types, tradeoffs present
- **8/10 (4 pts):** 90-94% rationale coverage, most non-obvious explained, 4/4 assumption types, tradeoffs present
- **7/10 (3.5 pts):** 85-89% rationale coverage, most non-obvious explained, 3/4 assumption types, some tradeoffs
- **6/10 (3 pts):** 80-84% rationale coverage, most non-obvious explained, 3/4 assumption types, some tradeoffs
- **5/10 (2.5 pts):** 70-79% rationale coverage, some non-obvious explained, 2/4 assumption types, few tradeoffs
- **4/10 (2 pts):** 60-69% rationale coverage, some non-obvious explained, 2/4 assumption types, few tradeoffs
- **3/10 (1.5 pts):** 50-59% rationale coverage, few explanations, 1/4 assumption types, no tradeoffs
- **2/10 (1 pt):** 40-49% rationale coverage, few explanations, 1/4 assumption types, no tradeoffs
- **1/10 (0.5 pts):** 30-39% rationale coverage, none explained, 0/4 assumption types, no tradeoffs
- **0/10 (0 pts):** <30% rationale coverage, none explained, no assumptions, no tradeoffs

## Context Requirements

### 1. Provide Rationale

**Without rationale (poor):**
```markdown
Use PostgreSQL for the database
```

**With rationale (good):**
```markdown
Use PostgreSQL for the database

Rationale:
- Supports JSON columns (needed for flexible metadata)
- ACID compliance required for financial transactions
- Team has PostgreSQL expertise
- Excellent Django ORM support

Alternatives considered:
- MySQL: No native JSON support
- MongoDB: No ACID for multi-document transactions
```

### 2. Document Assumptions

**Example (complete):**
```markdown
## Assumptions

1. User table has <10M rows (affects index strategy)
2. 95% of requests are reads (justifies read replicas)
3. Peak load: 1000 RPS (sizing consideration)
4. Data retention: 7 years (legal requirement)
5. Downtime window: Saturdays 2-4 AM UTC
```

### 3. Explain Non-Obvious Choices

**Without explanation (poor):**
```markdown
Set MAX_CONNECTIONS=100
```

**With explanation (good):**
```markdown
Set MAX_CONNECTIONS=100

Reasoning:
- Each connection uses ~10MB RAM
- Server has 2GB available (2000MB / 10MB = 200 max)
- Reserve 50% headroom = 100 connections
- Current peak: 60 connections
- Provides 40-connection buffer for spikes
```

### 4. Acknowledge Tradeoffs

**Without tradeoffs (poor):**
```markdown
Use Redis for caching
```

**With tradeoffs (good):**
```markdown
Use Redis for caching

Tradeoffs:
 Pros:
  - Sub-millisecond latency
  - Reduces DB load by 80%
  - Simple key-value semantics

 Cons:
  - Adds operational complexity
  - Cache invalidation challenges
  - Memory cost: ~$200/month for 10GB

Decision: Benefits outweigh costs for this use case
```

### 5. Preserve Context

**Link related decisions:**
```markdown
## Architecture Decisions

### Decision 1: Use microservices
Rationale: Enable independent team scaling

### Decision 2: Use Docker
Rationale: Supports Decision 1 (microservices need containers)

### Decision 3: Use Kubernetes
Rationale: Supports Decisions 1+2 (orchestrate containers)
```

## Context Tracking Table

Use during review:

**Decision Tracking Inventory (example):**
- Use PostgreSQL (line 45): Rationale (Yes), Explained (Yes), Tradeoffs (Yes)
- Set timeout=30s (line 67): Rationale (No), Explained (No), Tradeoffs (No)
- 3 replicas (line 89): Rationale (Partial), Explained (No), Tradeoffs (Yes)
- Redis caching (line 120): Rationale (Yes), Explained (Yes), Tradeoffs (Yes)

**Rationale coverage:** 3/4 = 75%

## Worked Example

**Target:** Infrastructure plan

### Step 1: Identify Key Decisions

**Key Decision Inventory:**
- Use PostgreSQL (line 30)
- Set max_connections=100 (line 45)
- Use Redis for caching (line 60)
- 3 application replicas (line 75)
- Use Kubernetes (line 90)

**Total:** 5 key decisions

### Step 2: Check Rationale

**Rationale Assessment:**
- PostgreSQL: Yes - "ACID required"
- max_connections=100: No - None provided
- Redis caching: Yes - "Reduce DB load"
- 3 replicas: No - None provided
- Kubernetes: Yes - "Auto-scaling"

**Coverage:** 3/5 = 60%

### Step 3: Check Non-Obvious Explanations

**Non-Obvious Value Assessment:**
- max_connections=100: No explanation
- 3 replicas: No explanation
- Redis 10GB: Yes - "Working set size"

**Explained:** 1/3 = 33%

### Step 4: Check Assumptions

**Assumption Type Assessment:**
- Data: Yes - "10M rows"
- Environment: No
- Behavior: Yes - "95% reads"
- External: No

**Coverage:** 2/4 types

### Step 5: Check Tradeoffs

```markdown
Only Redis section has tradeoffs listed
PostgreSQL, Kubernetes: no alternatives mentioned
```

**Quality:** Present but incomplete (-0.5)

### Step 6: Calculate Score

**Component Assessment:**
- Rationale: 60% = 3/5 baseline
- Non-obvious: 33% = -1 point
- Assumptions: 2/4 = -1 point
- Tradeoffs: Incomplete = -0.5 points

**Total deductions:** -2.5 points from baseline
**Final:** 5/10 (2.5 points)

### Step 7: Document in Review

```markdown
## Context: 5/10 (2.5 points)

**Rationale coverage:** 60% (3/5 decisions)
- [YES] PostgreSQL: ACID requirements explained
- [NO] max_connections=100: No rationale
- [YES] Redis: Performance rationale
- [NO] 3 replicas: No rationale
- [YES] Kubernetes: Auto-scaling rationale

**Non-obvious values:** 33% explained
- [NO] max_connections=100: Why 100?
- [NO] 3 replicas: Why 3?
- [YES] Redis 10GB: Working set explained

**Assumptions:** 2/4 types
- [YES] Data, Behavior
- [NO] Environment, External missing

**Tradeoffs:** Partial (Redis only)

**Priority fixes:**
1. Add rationale for max_connections (memory calc)
2. Add rationale for replica count (availability req)
3. Document environment assumptions
4. Add tradeoffs for PostgreSQL vs alternatives
```

## Context Checklist

During review, verify:

- [ ] Key decisions have "why" explanation
- [ ] Non-obvious values explained (timeouts, sizes, counts)
- [ ] Assumptions documented explicitly
- [ ] Alternatives considered (why not X?)
- [ ] Tradeoffs acknowledged (pros and cons)
- [ ] Context links decisions together
- [ ] Technical choices justified
- [ ] Sizing/scaling rationale provided

## Inter-Run Consistency Target

**Expected variance:** ±10% rationale coverage

**Verification:**
- Count key decisions explicitly
- Check for "rationale:", "why:", "reason:" keywords
- Use tracking table

**If variance exceeds threshold:**
- Re-count using decision type list
- Apply rationale definition strictly
