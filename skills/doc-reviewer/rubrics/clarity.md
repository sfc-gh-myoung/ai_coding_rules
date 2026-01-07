# Clarity Rubric (20 points)

## Scoring Criteria

### 5/5 (20 points): Excellent
- New user can follow without prior knowledge
- No unexplained jargon
- Concepts explained before use
- Examples clarify complex topics
- Clear, simple language throughout

### 4/5 (16 points): Good
- Mostly accessible to new users
- Minimal unexplained jargon (1-2 terms)
- Most concepts explained
- Good examples present

### 3/5 (12 points): Acceptable
- Some assumptions about prior knowledge
- Some unexplained jargon (3-5 terms)
- Concepts partially explained
- Limited examples

### 2/5 (8 points): Needs Work
- Assumes significant prior knowledge
- Much unexplained jargon (6-10 terms)
- Concepts rarely explained
- Few examples

### 1/5 (4 points): Poor
- Impenetrable to new users
- Extensive jargon (>10 terms)
- No concept explanations
- No examples

## New User Test

**Question:** Could someone with no project knowledge follow these docs?

**Test scenarios:**
1. Can they understand what the project does?
2. Can they install and run it?
3. Can they complete basic task?
4. Can they troubleshoot basic error?

**Scoring:**
- All 4: 5/5
- 3 of 4: 4/5
- 2 of 4: 3/5
- 1 of 4: 2/5
- 0 of 4: 1/5

## Jargon Audit

Search for unexplained technical terms:

- **"idempotent"** - Line: 45, Explained?: No, Fix Needed: Add: "produces same result when repeated"
- **"webhook"** - Line: 67, Explained?: No, Fix Needed: Add: "HTTP callback when event occurs"
- **"API"** - Line: 12, Explained?: Yes, Fix Needed: Already explained
- **"CRUD"** - Line: 89, Explained?: No, Fix Needed: Add: "Create, Read, Update, Delete operations"

**Penalty:** -0.5 points per unexplained term (up to -5 points)

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
Base score = 5/5 (20 points)

New User Test:
  0/4 scenarios: 1/5 (4 points)
  1/4 scenarios: 2/5 (8 points)
  2/4 scenarios: 3/5 (12 points)
  3/4 scenarios: 4/5 (16 points)
  4/4 scenarios: 5/5 (20 points)

Deductions from base:
  Unexplained jargon: -0.5 per term (up to -5)
  Concepts out of order: -1 per instance (up to -3)
  Overly complex sentences: -0.5 per instance (up to -2)
  Poor examples: -1 per example (up to -3)

Minimum score: 1/5 (4 points)
```

## Critical Gate

If documentation is impenetrable to new users:
- Cap score at 1/5 (4 points) maximum
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
