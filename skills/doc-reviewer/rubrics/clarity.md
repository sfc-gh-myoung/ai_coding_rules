# Clarity Rubric (20 points)

## Mandatory Verification Table (REQUIRED)

**CRITICAL:** You MUST create and fill this table BEFORE calculating score.

### Why This Is Required

- **Eliminates jargon variance:** Same doc → same table → same score
- **Prevents missed terms:** Systematic scan catches all
- **Provides evidence:** Table shows exactly what was evaluated
- **Enables audit:** Users can verify scoring decisions

### Verification Table Template

**Jargon Audit:**

| Line | Term | Explained? | Fix Needed |
|------|------|------------|------------|
| 45 | "idempotent" | No | Add: "produces same result when repeated" |
| 67 | "webhook" | No | Add: "HTTP callback when event occurs" |
| 12 | "API" | Yes | - |
| 89 | "CRDT" | No | Add: "Conflict-free Replicated Data Type" |

**Concept Order:**

| Line Used | Concept | Line Explained | Order OK? |
|-----------|---------|----------------|-----------|
| 10 | webhook | 50 | No (used before explained) |
| 25 | API | 5 | Yes |
| 60 | cache | 55 | Yes |

**New User Test:**

| Scenario | Passes? |
|----------|---------|
| Can understand what project does | Y/N |
| Can install and run it | Y/N |
| Can complete basic task | Y/N |
| Can troubleshoot basic error | Y/N |

### Verification Protocol (5 Steps)

**Step 1: Create Empty Tables**
- Copy all templates above
- Do NOT start reading doc yet

**Step 2: Read Doc Systematically**
- Start at line 1, read to END (no skipping)
- For EACH technical term: Add row to Jargon table
- For EACH concept: Note line introduced and line used

**Step 3: Perform New User Test**
- Mentally simulate new user experience
- Answer each scenario Y/N
- Note specific failures

**Step 4: Calculate Totals**
- Count unexplained jargon
- Count concepts out of order
- Count New User Test passes (0-4)

**Step 5: Look Up Score**
- Use New User Test result as base
- Apply deductions for jargon/order issues
- Record score with table evidence

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 4
**Points:** Raw × (4/2) = Raw × 2.0

## Scoring Criteria

### 10/10 (20 points): Perfect
- New user can follow without prior knowledge
- No unexplained jargon
- Concepts explained before use
- Examples clarify complex topics
- Clear, simple language throughout

### 9/10 (18 points): Near-Perfect
- Accessible to new users
- 1 unexplained term
- All concepts explained
- Excellent examples

### 8/10 (16 points): Excellent
- Mostly accessible to new users
- 1-2 unexplained jargon
- Most concepts explained
- Good examples present

### 7/10 (14 points): Good
- Accessible to most users
- 2-3 unexplained jargon
- Most concepts explained
- Good examples present

### 6/10 (12 points): Acceptable
- Some assumptions about prior knowledge
- 3-4 unexplained jargon
- Concepts partially explained
- Limited examples

### 5/10 (10 points): Borderline
- Assumes some prior knowledge
- 4-5 unexplained jargon
- Concepts partially explained
- Few examples

### 4/10 (8 points): Needs Work
- Assumes significant prior knowledge
- 5-7 unexplained jargon
- Concepts rarely explained
- Few examples

### 3/10 (6 points): Poor
- Assumes significant prior knowledge
- 7-9 unexplained jargon
- Concepts rarely explained
- Inadequate examples

### 2/10 (4 points): Very Poor
- Assumes expert knowledge
- 9-12 unexplained jargon
- No concept explanations
- Almost no examples

### 1/10 (2 points): Inadequate
- Impenetrable to new users
- >12 unexplained jargon
- No concept explanations
- No examples

### 0/10 (0 points): Not Clear
- Completely inaccessible
- Pervasive unexplained terminology
- Impossible to follow

## New User Test

**Question:** Could someone with no project knowledge follow these docs?

**Test scenarios:**
1. Can they understand what the project does?
2. Can they install and run it?
3. Can they complete basic task?
4. Can they troubleshoot basic error?

**Scoring:**
- All 4: 10/10
- 3 of 4: 7/10
- 2 of 4: 5/10
- 1 of 4: 3/10
- 0 of 4: 1/10

## Jargon Audit

Search for unexplained technical terms:

- **"idempotent"** - Line: 45, Explained?: No, Fix Needed: Add: "produces same result when repeated"
- **"webhook"** - Line: 67, Explained?: No, Fix Needed: Add: "HTTP callback when event occurs"
- **"API"** - Line: 12, Explained?: Yes, Fix Needed: Already explained
- **"CRUD"** - Line: 89, Explained?: No, Fix Needed: Add: "Create, Read, Update, Delete operations"

**Penalty:** -0.25 points per unexplained term (up to -2.5 points)

## Concept Introduction Order

Check that concepts are explained before use:

**Bad example:**
```markdown
Line 10: Configure your webhook endpoint
Line 50: (later) A webhook is an HTTP callback...
→  Used before explained
```

**Good example:**
```markdown
Line 10: A webhook is an HTTP callback that notifies your app when events occur
Line 15: Configure your webhook endpoint
→  Explained before use
```

## Language Complexity

### Sentence Length

Check for overly complex sentences:

**Bad (65 words):**
```markdown
When you configure the application, which requires setting up various environment variables that control the behavior of different subsystems including the database connection, caching layer, and external service integrations, you must ensure that all required values are properly set according to the deployment environment specifications.
```

**Good (3 sentences, 15-20 words each):**
```markdown
Configure the application using environment variables. These control database connections, caching, and external services. Set all required values for your deployment environment.
```

### Active Voice

Prefer active over passive voice:

**Passive (unclear):**
```markdown
The data is processed by the system
```

**Active (clear):**
```markdown
The system processes the data
```

## Examples Quality

### Example Requirements

Good examples should:
- Be complete (copy-pasteable)
- Show realistic use case
- Include expected output
- Explain what's happening

**Bad example:**
```python
# Use the function
result = process(data)
```
→ Where does `data` come from? What is `result`?

**Good example:**
```python
# Process user data from form submission
form_data = {"name": "Alice", "email": "alice@example.com"}
result = process_user(form_data)
# Returns: {"id": 123, "status": "created"}
```

## Scoring Formula

```
Base score = 10/10 (20 points)

New User Test:
  0/4 scenarios: 1/10 (2 points)
  1/4 scenarios: 3/10 (6 points)
  2/4 scenarios: 5/10 (10 points)
  3/4 scenarios: 7/10 (14 points)
  4/4 scenarios: 10/10 (20 points)

Deductions from base:
  Unexplained jargon: -0.25 per term (up to -2.5)
  Concepts out of order: -0.5 per instance (up to -1.5)
  Overly complex sentences: -0.25 per instance (up to -1)
  Poor examples: -0.5 per example (up to -1.5)

Minimum score: 0/10 (0 points)
```

## Critical Gate

If documentation is impenetrable to new users:
- Cap score at 2/10 (4 points) maximum
- Mark as CRITICAL issue
- Documentation fails primary purpose

## Common Clarity Issues

### Issue 1: Assumed Knowledge

**Problem:**
```markdown
Configure your kubectl context and apply the manifests
```

**Fix:**
```markdown
Configure Kubernetes access:
1. Install kubectl: `brew install kubernetes-cli`
2. Set context: `kubectl config use-context my-cluster`
3. Apply configuration: `kubectl apply -f manifests/`
```

### Issue 2: Unexplained Jargon

**Problem:**
```markdown
The service uses eventual consistency with CRDT semantics
```

**Fix:**
```markdown
The service uses eventual consistency (data syncs over time, not instantly) with CRDT (Conflict-free Replicated Data Type) semantics for automatic conflict resolution.
```

### Issue 3: No Context

**Problem:**
```markdown
Run: python manage.py migrate
```

**Fix:**
```markdown
Apply database migrations to set up your database schema:
```bash
python manage.py migrate
```
This creates tables and relationships defined in your models.
```

### Issue 4: Missing "Why"

**Problem:**
```markdown
Set MAX_CONNECTIONS=100
```

**Fix:**
```markdown
Set MAX_CONNECTIONS=100 to limit concurrent database connections. Higher values use more memory but handle more simultaneous users. Start with 100 and adjust based on your traffic.
```

## Clarity Checklist

During review, verify:

- [ ] Project purpose clear in first paragraph
- [ ] Setup instructions step-by-step
- [ ] All jargon explained on first use
- [ ] Concepts introduced before referenced
- [ ] Examples are complete and realistic
- [ ] Error messages explained
- [ ] "Why" provided for non-obvious choices
- [ ] Can new user complete basic task

## Non-Issues (Do NOT Count as Jargon)

**Review EACH flagged item against this list before counting.**

### Pattern 1: Industry Standard Terms
**Pattern:** Common technical term with well-known meaning
**Example:** "API", "HTTP", "JSON", "CLI"
**Why NOT an issue:** Universally understood in tech context
**Action:** Remove from table with note "Standard term"

### Pattern 2: Already Defined Earlier
**Pattern:** Term defined earlier in same document
**Example:** "webhook" at line 100, defined at line 10
**Why NOT an issue:** Definition exists earlier in doc
**Action:** Remove from table with note "Defined at line N"

### Pattern 3: Target Audience Term
**Pattern:** Term expected to be known by target audience
**Example:** "Docker container" in DevOps documentation
**Why NOT an issue:** Target audience knows this term
**Action:** Remove from table with note "Audience term"

### Pattern 4: Linked Definition
**Pattern:** Term with hyperlink to definition
**Example:** "[idempotent](https://en.wikipedia.org/wiki/Idempotence)"
**Why NOT an issue:** Definition accessible via link
**Action:** Remove from table with note "Linked"
