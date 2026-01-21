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

## Score Decision Matrix (ENHANCED)

**Purpose:** Convert rationale coverage and assumption documentation into dimension score. No interpretation needed - just look up the tier.

### Input Values

From completed worksheet:
- **Rationale Coverage %:** Key decisions with rationale / Total key decisions × 100
- **Non-Obvious Explained:** Count of non-obvious choices with explanations
- **Assumption Types:** Count of 4 types documented (Data/Environment/Behavior/External)
- **Tradeoffs:** Present with alternatives / Present without / Missing

### Scoring Table

| Rationale % | Non-Obvious | Assumptions | Tradeoffs | Tier | Raw Score | × Weight | Points |
|-------------|-------------|-------------|-----------|------|-----------|----------|--------|
| 100% | All | 4/4 | With alternatives | Perfect | 10/10 | × 0.5 | 5 |
| 95-99% | All | 4/4 | Present | Near-Perfect | 9/10 | × 0.5 | 4.5 |
| 90-94% | Most | 4/4 | Present | Excellent | 8/10 | × 0.5 | 4 |
| 85-89% | Most | 3/4 | Some | Good | 7/10 | × 0.5 | 3.5 |
| 80-84% | Most | 3/4 | Some | Acceptable | 6/10 | × 0.5 | 3 |
| 70-79% | Some | 2/4 | Few | Borderline | 5/10 | × 0.5 | 2.5 |
| 60-69% | Some | 2/4 | Few | Below Standard | 4/10 | × 0.5 | 2 |
| 50-59% | Few | 1/4 | None | Poor | 3/10 | × 0.5 | 1.5 |
| 40-49% | Few | 1/4 | None | Very Poor | 2/10 | × 0.5 | 1 |
| 30-39% | None | 0/4 | None | Critical | 1/10 | × 0.5 | 0.5 |
| <30% | None | 0/4 | None | No Context | 0/10 | × 0.5 | 0 |

### Tie-Breaking Algorithm (Deterministic)

**When rationale coverage falls exactly on tier boundary:**

1. **Check Assumption Coverage:** If assumptions > tier requirement → HIGHER tier
2. **Check Tradeoff Quality:** If tradeoffs include alternatives → HIGHER tier
3. **Check Decision Impact:** If unexplained decisions are low-impact → HIGHER tier
4. **Default:** LOWER tier (conservative - missing context affects reproducibility)

### Edge Cases

**Edge Case 1: Self-evident decisions (no rationale needed)**
- **Example:** "Use Python (existing codebase is Python)"
- **Rule:** Count as having rationale (context is self-evident)
- **Rationale:** Obvious choices don't need explicit justification

**Edge Case 2: Standard defaults**
- **Example:** "Use port 8080 for web server" (no explanation)
- **Rule:** Standard defaults don't reduce rationale coverage
- **Rationale:** Industry conventions are implicit rationale

**Edge Case 3: Referenced documentation**
- **Example:** "Configure per company standard (see wiki/config)"
- **Rule:** Count as having rationale if reference is valid
- **Rationale:** External documentation provides context

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

## Non-Issues (Do NOT Count)

**Purpose:** Eliminate false positives by explicitly defining what is NOT a context issue.

### Pattern 1: Self-Evident Choices (Existing Stack)

**Example:**
```markdown
"Use Flask for the API endpoint"
(Project already uses Flask throughout)
```
**Why NOT an issue:** Using existing stack is self-evident, no rationale needed  
**Overlap check:** N/A - consistency with codebase  
**Correct action:** Do not flag stack-consistent choices

### Pattern 2: Standard Defaults

**Example:**
```markdown
"Set timeout=30s for API calls"
```
**Why NOT an issue:** 30 seconds is industry-standard default for HTTP  
**Overlap check:** Not Executability - value is explicit  
**Correct action:** Do not flag standard default values

### Pattern 3: Rationale in Referenced Document

**Example:**
```markdown
"Use architecture from ADR-005"
(ADR-005 exists and contains rationale)
```
**Why NOT an issue:** Rationale exists in referenced document  
**Overlap check:** Not Dependencies - it's a context reference  
**Correct action:** Count as having rationale if reference is valid

### Pattern 4: Industry Best Practice

**Example:**
```markdown
"Use 3 replicas for high availability"
```
**Why NOT an issue:** 3 replicas is standard HA pattern  
**Overlap check:** N/A - well-known pattern  
**Correct action:** Do not require explanation for standard patterns

## Complete Pattern Inventory

**Purpose:** Eliminate interpretation variance by providing exhaustive lists. If it's not in this list, don't invent it. Match case-insensitive.

### Category 1: Rationale Indicators (25 Phrases)

**Phrases that signal rationale present:**
1. "because"
2. "since"
3. "rationale:"
4. "reason:"
5. "why:"
6. "due to"
7. "this is because"
8. "the reason is"
9. "chosen for"
10. "selected because"
11. "to ensure"
12. "to prevent"
13. "to enable"
14. "in order to"
15. "so that"
16. "which allows"
17. "which prevents"
18. "for the purpose of"
19. "to support"
20. "to avoid"
21. "to improve"
22. "to reduce"
23. "to maintain"
24. "given that"
25. "considering"

**Regex Patterns:**
```regex
\b(because|since|due\s+to|given\s+that|considering)\b
\b(rationale|reason|why)\s*:\s*
\bchosen\s+(for|because)\b
\b(to|in\s+order\s+to)\s+(ensure|prevent|enable|support|avoid|improve|reduce|maintain)\b
\bso\s+that\b
\bwhich\s+(allows|prevents|enables)\b
```

**Context Rules:**
- Rationale indicator near decision → Count as has rationale
- Decision without any indicator → Count as no rationale
- Exception: Self-evident decisions (existing stack) don't need rationale

### Category 2: Non-Obvious Value Patterns (20 Types)

**Values requiring explanation:**
1. Timeout values (5s, 30s, 60s, 300s)
2. Connection pool sizes (10, 50, 100, 200)
3. Retry counts (3, 5, 10)
4. Memory allocations (512MB, 1GB, 2GB, 4GB)
5. Batch sizes (100, 500, 1000, 5000)
6. Thread/worker counts (4, 8, 16, 32)
7. Cache TTL (60s, 300s, 3600s, 86400s)
8. Rate limits (100/min, 1000/hour)
9. Queue sizes (100, 1000, 10000)
10. File size limits (1MB, 10MB, 100MB)
11. Replica counts (2, 3, 5)
12. Partition counts (3, 6, 12)
13. Shard counts
14. Buffer sizes
15. Concurrency limits
16. Max connections
17. Keep-alive intervals
18. Health check intervals
19. Circuit breaker thresholds
20. Backoff multipliers

**Standard values (don't need explanation):**
- HTTP timeout: 30s
- HTTP ports: 80, 443, 8080, 3000
- Database ports: 5432 (Postgres), 3306 (MySQL), 27017 (MongoDB)
- Cache ports: 6379 (Redis)
- Replicas for HA: 3

**Regex Patterns:**
```regex
\b(timeout|ttl|interval)\s*[=:]\s*\d+\s*(s|ms|sec|seconds?|min|minutes?)\b
\b(max_connections?|pool_size|workers?|threads?|replicas?)\s*[=:]\s*\d+\b
\b(batch_size|limit|max)\s*[=:]\s*\d+\b
\b\d+\s*(MB|GB|KB)\b
\bretry\s*[=:]\s*\d+\b
```

### Category 3: Assumption Type Patterns (4 Categories)

**Type 1 - Data Assumptions:**
- "row count", "volume", "size"
- "X million", "X GB"
- "records per day"
- "growth rate"
- "data format"
- "schema version"

**Type 2 - Environment Assumptions:**
- "available memory"
- "CPU cores"
- "disk space"
- "network bandwidth"
- "cloud provider"
- "region"

**Type 3 - Behavior Assumptions:**
- "read/write ratio"
- "peak load"
- "concurrent users"
- "request rate"
- "usage pattern"
- "user behavior"

**Type 4 - External Assumptions:**
- "API availability"
- "SLA"
- "uptime"
- "third-party service"
- "external dependency"
- "vendor support"

**Regex Patterns:**
```regex
# Data assumptions
\b(\d+\s*(million|billion|K|M|G)?\s*(rows?|records?|users?|items?|documents?|bytes?)\b
\b(data\s+volume|growth\s+rate|schema)\b

# Environment assumptions
\b(\d+\s*(GB|MB|cores?|CPUs?)\s+(RAM|memory|disk)\b
\b(AWS|GCP|Azure|cloud|region)\b

# Behavior assumptions
\b(\d+%?\s*(reads?|writes?)|read[\/\-]write\s+ratio)\b
\b(peak|concurrent|RPS|QPS)\b

# External assumptions
\b(SLA|uptime|\d+\.?\d*%\s+availability)\b
\b(API|service)\s+(availability|uptime)\b
```

### Category 4: Tradeoff Indicators (15 Phrases)

**Phrases signaling tradeoff discussion:**
1. "pros and cons"
2. "tradeoff"
3. "trade-off"
4. "alternatively"
5. "on the other hand"
6. "however"
7. "drawback"
8. "downside"
9. "benefit"
10. "advantage"
11. "disadvantage"
12. "considered but rejected"
13. "vs"
14. "compared to"
15. "instead of"

**Alternative consideration phrases:**
- "we could also"
- "another option"
- "other approaches"
- "why not X"
- "rejected because"
- "chose X over Y"

**Regex Patterns:**
```regex
\b(pros?\s+and\s+cons?|tradeoffs?|trade-offs?)\b
\b(alternatively|on\s+the\s+other\s+hand|however)\b
\b(drawback|downside|disadvantage|benefit|advantage)\b
\b(considered|rejected)\s+(but\s+rejected|because)\b
\bvs\.?\b|\bversus\b
\b(instead|rather\s+than|over)\s+(of|than)?\s*\b
\b(another|other)\s+(option|approach|alternative)\b
```

### Category 5: Self-Evident Decision Patterns (15 Cases)

**Decisions NOT requiring rationale:**
1. Continue using existing framework (codebase consistency)
2. Continue using existing database (migration unnecessary)
3. Continue using existing language (team expertise)
4. Use standard library over custom (best practice)
5. Use established patterns from codebase
6. Follow company/team coding standards
7. Use industry-standard defaults (30s timeout, etc.)
8. Use same tools as CI/CD pipeline
9. Match existing code style
10. Use version control (git)
11. Use standard testing frameworks (pytest, jest)
12. Use standard linting tools (eslint, ruff)
13. Use standard formatters (prettier, black)
14. Deploy to existing infrastructure
15. Use existing monitoring/logging

**Regex Patterns:**
```regex
\b(existing|current|same|standard)\s+(framework|database|language|library|pattern|tool)\b
\b(continue|keep|maintain)\s+(using|with)\b
\b(per|following)\s+(team|company|project)\s+(standard|convention|guideline)\b
```

### Ambiguous Cases Resolution

**Case 1: Implicit rationale from context**

**Pattern:** "Use PostgreSQL (existing database)"

**Ambiguity:** Is "existing" sufficient rationale?

**Resolution Rule:**
- "Existing" or "current" = valid self-evident rationale
- Continuing with established tech doesn't need justification
- Count as has rationale

**Case 2: Rationale in referenced document**

**Pattern:** "Configure per ADR-005"

**Ambiguity:** Does reference count as rationale?

**Resolution Rule:**
- Valid reference to existing document = rationale present
- Broken/invalid reference = no rationale
- Note: "See ADR-005 for rationale" in worksheet

**Case 3: Standard value without explanation**

**Pattern:** "Set timeout=30s" (no explanation)

**Ambiguity:** Does standard default need explanation?

**Resolution Rule:**
- Standard HTTP timeout (30s) = no explanation needed
- Unusual timeout (300s, 5s) = needs explanation
- See Standard values list

**Case 4: Partial tradeoff discussion**

**Pattern:** Pros listed, no cons mentioned

**Ambiguity:** Is this a tradeoff acknowledgment?

**Resolution Rule:**
- Pros only = partial tradeoff (0.5 credit)
- Pros AND cons = full tradeoff
- Neither = no tradeoff

**Case 5: Assumption stated as constraint**

**Pattern:** "System must support 10M users"

**Ambiguity:** Is requirement statement an assumption?

**Resolution Rule:**
- External requirement = constraint (not assumption)
- Internal estimate = assumption (document type)
- Both valid, categorize appropriately

**Case 6: Multiple decisions in one statement**

**Pattern:** "Use Redis for caching and session storage"

**Ambiguity:** Count as one or two decisions?

**Resolution Rule:**
- Same tool for multiple purposes = 1 decision
- Different tools for same purpose = multiple decisions
- Count decisions by technology choice, not use case

**Case 7: Non-obvious value with implicit justification**

**Pattern:** "3 replicas" (standard HA pattern)

**Ambiguity:** Does HA pattern justify value?

**Resolution Rule:**
- Well-known patterns (3 replicas for HA) = explained
- Unusual values (7 replicas) = needs explanation
- Document: "3 replicas - standard HA (implicit)"

**Case 8: Assumption in different section**

**Pattern:** Data assumption in Prerequisites, not in Assumptions section

**Ambiguity:** Does location matter for counting?

**Resolution Rule:**
- Assumption anywhere in plan = documented
- Search entire plan before marking as missing
- Note location in worksheet

## Anti-Pattern Examples (Common Mistakes)

**❌ WRONG (False Positive):**
- Flagged: "Use PostgreSQL - no rationale provided"
- Rationale given: "Decision lacks 'why'"
- Problem: Project is existing Django app using PostgreSQL
- Impact: Incorrect rationale coverage % reduction

**✅ CORRECT:**
- Not flagged for missing rationale
- Rationale: Continuing existing stack is self-evident
- Condition: Would be flagged IF switching databases

**❌ WRONG (False Positive):**
- Flagged: "timeout=30s not explained"
- Rationale given: "Non-obvious value needs explanation"
- Problem: 30s is standard HTTP timeout
- Impact: Incorrect non-obvious explanation count

**✅ CORRECT:**
- 30s timeout not flagged
- Rationale: Industry standard default
- Condition: Would be flagged IF timeout were 300s (unusual)

## Ambiguous Case Resolution Rules (REQUIRED)

**Purpose:** Provide deterministic scoring when rationale/context is borderline.

### Rule 1: Same-File Context
**Count as has rationale if:** "Why", "Rationale", "Reason", or explanation text within same section  
**Count as no rationale if:** Decision stated without any explanation

### Rule 2: Adjectives Without Quantifiers
**Count as explained if:** Specific reasoning provided (even if brief)  
**Count as NOT explained if:** Only the decision stated, no supporting reasoning

### Rule 3: Pattern Variations
**Count assumption as documented if:** Explicit statement of what is assumed (even without "assumption" keyword)  
**Count assumption as NOT documented if:** Implicit assumptions not stated anywhere

### Rule 4: Default Resolution
**Still uncertain after Rules 1-3?** → Count as no rationale/not documented (conservative scoring)

### Borderline Cases Template

Document borderline decisions in your worksheet:

```markdown
### Decision: "[Decision Description]"
- **Decision:** Has rationale [Y/N], Explained [Y/N], Tradeoffs [Y/N]
- **Rule Applied:** [1/2/3/4]
- **Reasoning:** [Explain why this classification]
- **Alternative:** [Other interpretation and why rejected]
- **Confidence:** [HIGH/MEDIUM/LOW]
```

## Mandatory Counting Worksheet (REQUIRED)

**CRITICAL:** You MUST create and fill this worksheet BEFORE calculating score.

### Worksheet Template

**Key Decision Rationale:**
| Decision | Line | Has Rationale? | Quality |
|----------|------|----------------|---------|
| [Decision 1] | ___ | Y/N | Complete/Partial/None |
| [Decision 2] | ___ | Y/N | Complete/Partial/None |
| **TOTAL** | | **___/total** | |
| **COVERAGE** | | **___%** | |

**Non-Obvious Values:**
| Value | Line | Explained? |
|-------|------|------------|
| [Value 1] | ___ | Y/N |
| [Value 2] | ___ | Y/N |
| **EXPLAINED** | | **___/total** |

**Assumption Documentation (0-4 types):**
| Type | Present? | Description |
|------|----------|-------------|
| Data assumptions | Y/N | |
| Environment assumptions | Y/N | |
| Behavior assumptions | Y/N | |
| External assumptions | Y/N | |
| **TOTAL** | **___/4** | |

**Tradeoff Acknowledgment:**
| Aspect | Status |
|--------|--------|
| Pros/cons listed? | Y/N |
| Decision justification? | Y/N |
| Alternatives considered? | Y/N |

### Counting Protocol

1. List all key decisions and check for rationale
2. Calculate rationale coverage percentage
3. List non-obvious values and check for explanations
4. Check assumption documentation by type
5. Assess tradeoff acknowledgment
6. Use Score Decision Matrix to determine raw score
7. Include completed worksheet in review output

## Inter-Run Consistency Target

**Expected variance:** ±10% rationale coverage

**Verification:**
- Count key decisions explicitly
- Check for "rationale:", "why:", "reason:" keywords
- Use tracking table

**If variance exceeds threshold:**
- Re-count using decision type list
- Apply rationale definition strictly
