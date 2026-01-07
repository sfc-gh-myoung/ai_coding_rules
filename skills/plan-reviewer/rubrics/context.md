# Context Rubric (5 points)

## Scoring Criteria

### 5/5 (5 points): Excellent
- Rationale provided for decisions
- "Why" explained for non-obvious choices
- Context preserved throughout
- Assumptions documented
- Tradeoffs acknowledged

### 4/5 (4 points): Good
- Most rationale provided
- Most "why" explained
- Context mostly preserved

### 3/5 (3 points): Acceptable
- Some rationale provided
- Some "why" explained
- Some context present

### 2/5 (2 points): Needs Work
- Little rationale
- Minimal "why"
- Context sparse

### 1/5 (1 point): Poor
- No rationale
- No "why"
- No context

## Context Requirements

### 1. Provide Rationale

Explain WHY for key decisions:

**No context (poor):**
```markdown
Use PostgreSQL for the database
```

**With context (good):**
```markdown
Use PostgreSQL for the database

Rationale:
- Supports JSON columns (needed for flexible metadata)
- ACID compliance required for financial transactions
- Team has PostgreSQL expertise
- Excellent Django ORM support

Alternatives considered:
- MySQL: No native JSON support
- MongoDB: No ACID guarantees for multi-document transactions
```

### 2. Document Assumptions

State assumptions explicitly:

**Good example:**
```markdown
## Assumptions

1. User table has <10M rows (affects index strategy)
2. 95% of requests are reads (justifies read replicas)
3. Peak load: 1000 RPS (sizing consideration)
4. Data retention: 7 years (legal requirement)
5. Downtime window: Saturdays 2-4 AM UTC (maintenance)
```

### 3. Explain Non-Obvious Choices

**No explanation (poor):**
```markdown
Set MAX_CONNECTIONS=100
```

**With explanation (good):**
```markdown
Set MAX_CONNECTIONS=100

Reasoning:
- Each connection uses ~10MB RAM
- Server has 2GB RAM available for connections (2000MB / 10MB = 200 max)
- Reserve 50% headroom → 100 connections
- Current peak usage: 60 connections
- Provides 40-connection buffer for traffic spikes
```

### 4. Acknowledge Tradeoffs

**No tradeoffs (poor):**
```markdown
Use Redis for caching
```

**With tradeoffs (good):**
```markdown
Use Redis for caching

Tradeoffs:
✓ Pros:
  - Sub-millisecond latency
  - Reduces DB load by 80%
  - Simple key-value semantics

✗ Cons:
  - Adds operational complexity (another service)
  - Cache invalidation complexity
  - Memory cost: ~$200/month for 10GB

Decision: Benefits outweigh costs for this use case
```

### 5. Preserve Context

Link related decisions:

**Good example:**
```markdown
## Architecture Decisions

### Decision 1: Use microservices
Rationale: Enable independent team scaling

### Decision 2: Use Docker
Rationale: Supports Decision 1 (microservices need containerization)

### Decision 3: Use Kubernetes
Rationale: Supports Decisions 1+2 (orchestrate multiple containerized services)
```

## Context Tracking Table

Use during review:

| Decision/Choice | Rationale Provided? | Assumptions Stated? | Tradeoffs Acknowledged? |
|-----------------|---------------------|---------------------|-------------------------|
| Use PostgreSQL | ✅ Yes | ✅ Yes | ✅ Yes |
| Set timeout=30s | ❌ No | ❌ No | ❌ No |
| 3 replicas | ⚠️  Partial | ❌ No | ✅ Yes |
| Redis caching | ✅ Yes | ✅ Yes | ✅ Yes |

**Missing context:** 1 decision has no rationale (timeout value)

## Scoring Formula

```
Base score = 5/5 (5 points)

Context quality:
  All key decisions have rationale: 5/5
  Most have rationale: 4/5 (-1)
  Some have rationale: 3/5 (-2)
  Few have rationale: 2/5 (-3)
  No rationale: 1/5 (-4)

Additional deductions:
  No assumptions documented: -1 point
  No tradeoffs acknowledged: -0.5 points

Minimum score: 1/5 (1 point)
```

## Common Context Issues

### Issue 1: No Rationale

**Problem:**
```markdown
Use Kubernetes for orchestration
```

**Fix:**
```markdown
Use Kubernetes for orchestration

Rationale:
- 15 microservices need coordination
- Auto-scaling required (traffic varies 10x daily)
- Self-healing needed (services crash occasionally)
- Industry standard (large talent pool)
- Strong ecosystem (monitoring, logging, service mesh)

Why not simpler alternatives:
- Docker Compose: No auto-scaling or self-healing
- ECS: AWS lock-in (want multi-cloud)
- Nomad: Smaller ecosystem and talent pool
```

### Issue 2: Undocumented Assumptions

**Problem:**
```markdown
Scale to 100 servers
```

**Fix:**
```markdown
Scale to 100 servers

Assumptions:
- Traffic projection: 10M requests/day by Q4
- Each server handles: 100K requests/day
- Required servers: 10M / 100K = 100
- Based on: Current load testing + 20% headroom

If assumptions change:
- Actual traffic <5M/day: Scale down to 50 servers
- Actual traffic >15M/day: Scale up to 150+ servers
```

### Issue 3: Missing Tradeoffs

**Problem:**
```markdown
Use microservices architecture
```

**Fix:**
```markdown
Use microservices architecture

Tradeoffs:
✓ Pros:
  - Independent deployments (reduce deployment risk)
  - Technology flexibility (right tool per service)
  - Team autonomy (5 teams, each owns services)
  - Horizontal scaling per service

✗ Cons:
  - Operational complexity (monitoring, debugging distributed)
  - Network overhead (inter-service calls)
  - Data consistency challenges
  - Deployment complexity (15 services vs 1 monolith)

Decision: At our scale (5 teams, 15 services), benefits outweigh costs
```

### Issue 4: Lost Context

**Problem:**
```markdown
Task 5: Add caching
Task 15: Increase cache size to 10GB
```
→ Task 15 references cache but context is 10 tasks ago

**Fix:**
```markdown
Task 5: Add Redis caching (2GB, TTL=1hour)

Task 15: Increase cache size to 10GB
Context: Builds on Task 5 (Redis caching)
Reason: Cache hit rate only 60% with 2GB
Target: 90% hit rate requires 10GB (analysis: logs show 10GB working set)
```

## Context Checklist

During review, verify:

- [ ] Key decisions have "why" explanation
- [ ] Non-obvious values explained (timeouts, sizes, counts)
- [ ] Assumptions documented explicitly
- [ ] Alternatives considered and rejected (why not X?)
- [ ] Tradeoffs acknowledged (pros and cons)
- [ ] Context links decisions together
- [ ] Technical choices justified
- [ ] Sizing/scaling rationale provided
- [ ] Future context preserved (why we did this)
