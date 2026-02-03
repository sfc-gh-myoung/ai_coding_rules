# Completeness Rubric (25 points)

## Mandatory Verification Table (REQUIRED)

**CRITICAL:** You MUST create and fill this table BEFORE calculating score.

### Why This Is Required

- **Eliminates coverage variance:** Same doc → same table → same score
- **Prevents missed gaps:** Systematic inventory catches all
- **Provides evidence:** Table shows exactly what was evaluated
- **Enables audit:** Users can verify scoring decisions

### Verification Table Template

**Feature Coverage:**

| Feature | Location | Documented? | Gap |
|---------|----------|-------------|-----|
| User auth | `src/auth.py` | Yes | - |
| Data export | `src/export.py` | No | Need export docs |
| API integration | `src/api/` | Yes | - |
| Caching | `src/cache.py` | No | Need caching docs |

**Setup Steps:**

| Step | Present? | Complete? | Gap |
|------|----------|-----------|-----|
| Prerequisites | Y/N | Y/N | |
| Installation | Y/N | Y/N | |
| Configuration | Y/N | Y/N | |
| Verification | Y/N | Y/N | |
| Common errors | Y/N | Y/N | |

**Troubleshooting Coverage:**

| Error Type | Documented? | Has Resolution? |
|------------|-------------|-----------------|
| Installation errors | Y/N | Y/N |
| Runtime errors | Y/N | Y/N |
| Usage errors | Y/N | Y/N |

### Verification Protocol (5 Steps)

**Step 1: Create Empty Tables**
- Copy all templates above
- Do NOT start reading doc yet

**Step 2: Discover Features**
- List directory structure: `ls -la src/`
- Identify all major features/modules
- Add each to Feature Coverage table

**Step 3: Read Doc Systematically**
- Read from line 1 to END
- Mark Y/N for each feature
- Mark Y/N for each setup step
- Mark Y/N for troubleshooting coverage

**Step 4: Calculate Coverage**
- Feature %: `(documented features / total features) × 100`
- Setup %: `(complete steps / required steps) × 100`

**Step 5: Look Up Score**
- Use feature coverage % in Score Decision Matrix
- Apply deductions for missing setup/troubleshooting
- Record score with table evidence

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 5
**Points:** Raw × (5/2) = Raw × 2.5

## Scoring Criteria

### 10/10 (25 points): Perfect
- All features documented
- Complete setup instructions (prerequisites → working state)
- API/CLI reference complete
- Troubleshooting section present
- Examples for all major features

### 9/10 (22.5 points): Near-Perfect
- 98%+ features documented
- Setup complete with verification
- API/CLI complete
- Comprehensive troubleshooting

### 8/10 (20 points): Excellent
- 95-97% features documented
- Setup mostly complete (1 step missing)
- API/CLI mostly covered
- Good troubleshooting

### 7/10 (17.5 points): Good
- 90-94% features documented
- Setup mostly complete (1-2 steps missing)
- API/CLI mostly covered
- Some troubleshooting present

### 6/10 (15 points): Acceptable
- 85-89% features documented
- Setup has minor gaps (2-3 steps missing)
- API/CLI partially documented
- Limited troubleshooting

### 5/10 (12.5 points): Borderline
- 75-84% features documented
- Setup has gaps (3-4 steps missing)
- API/CLI partially documented
- Minimal troubleshooting

### 4/10 (10 points): Needs Work
- 65-74% features documented
- Setup incomplete (4-5 steps missing)
- API/CLI barely documented
- No troubleshooting

### 3/10 (7.5 points): Poor
- 55-64% features documented
- Setup has major gaps (>5 steps missing)
- API/CLI barely documented
- No troubleshooting

### 2/10 (5 points): Very Poor
- 45-54% features documented
- Setup unusable
- Minimal API/CLI docs
- No troubleshooting

### 1/10 (2.5 points): Inadequate
- 30-44% features documented
- Setup unusable
- No API/CLI docs
- No troubleshooting

### 0/10 (0 points): Not Complete
- <30% features documented
- No setup instructions
- Not usable

## Coverage Checklist

### Feature Coverage

List all features in codebase, mark if documented:

- **User authentication** - Location: `src/auth.py`, Documented?: Yes, Gap: -
- **Data export** - Location: `src/export.py`, Documented?: No, Gap: Need export docs
- **API integration** - Location: `src/api/`, Documented?: Yes, Gap: -
- **Caching** - Location: `src/cache.py`, Documented?: No, Gap: Need caching docs

**Coverage calculation:**
- Total features: 4
- Documented: 2 (50%)
- Gap: 2 undocumented features

### Setup Completeness

Verify setup instructions include:

- [ ] Prerequisites (tools, versions, access)
- [ ] Installation steps
- [ ] Configuration steps
- [ ] Verification steps (how to test it works)
- [ ] Common setup errors and fixes

**Missing steps penalty:** -1 point per missing area

### API/CLI Documentation

For libraries with APIs or CLIs:

**API docs must include:**
- [ ] All public functions/methods
- [ ] Parameters with types
- [ ] Return values
- [ ] Exceptions/errors
- [ ] Usage examples

**CLI docs must include:**
- [ ] All commands
- [ ] All flags/options
- [ ] Examples for each command
- [ ] Exit codes
- [ ] Error messages

### Troubleshooting Coverage

Must address:

- [ ] Common errors (installation, runtime, usage)
- [ ] Error message explanations
- [ ] Resolution steps
- [ ] Where to get help

### Examples Coverage

Must include:

- [ ] Basic usage example
- [ ] Advanced usage example
- [ ] Real-world use case
- [ ] Common patterns

## Scoring Formula

```
Base score = 10/10 (25 points)

Feature coverage:
  <30%: Cap at 0/10 (0 points)
  30-44%: Max 1/10 (2.5 points)
  45-54%: Max 2/10 (5 points)
  55-64%: Max 3/10 (7.5 points)
  65-74%: Max 4/10 (10 points)
  75-84%: Max 5/10 (12.5 points)
  85-89%: Max 6/10 (15 points)
  90-94%: Max 7/10 (17.5 points)
  95-97%: Max 8/10 (20 points)
  98-99%: Max 9/10 (22.5 points)
  100%: Full 10/10 available

Missing setup steps: -0.5 points each (up to -5)
Incomplete API/CLI docs: -1 point
No troubleshooting: -1 point
Missing examples: -0.5 points per type (up to -2)

Minimum score: 0/10 (0 points)
```

## Critical Gate

If setup instructions are incomplete (can't get from zero to working):
- Cap score at 4/10 (10 points) maximum
- Mark as CRITICAL issue
- Users cannot onboard successfully

## Common Completeness Gaps

### Gap 1: Missing Prerequisites

**Problem:** Jumps straight to installation without listing requirements

**Fix:**
```markdown
## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Node.js 20+
- Access to AWS S3 (for file storage)
```

### Gap 2: Incomplete Setup

**Problem:** Doesn't explain configuration

**Fix:**
```markdown
## Configuration

1. Copy template: `cp .env.example .env`
2. Edit `.env` and set:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `AWS_ACCESS_KEY`: Your AWS key
   - `SECRET_KEY`: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
```

### Gap 3: Undocumented Features

**Problem:** Feature exists in code but not in docs

**Fix:** Add feature documentation section with examples

### Gap 4: No Troubleshooting

**Problem:** No guidance when things go wrong

**Fix:**
```markdown
## Troubleshooting

**Error: `ModuleNotFoundError: No module named 'psycopg2'`**

Solution: Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

**Error: `Connection refused on port 5432`**

Solution: Ensure PostgreSQL is running:
```bash
brew services start postgresql@15
```
```

## Coverage Tracking Table

Use during review:

- **Features** - Items: 10, Documented: 8, Missing: 2, Coverage %: 80%
- **Setup steps** - Items: 5, Documented: 5, Missing: 0, Coverage %: 100%
- **API methods** - Items: 25, Documented: 20, Missing: 5, Coverage %: 80%
- **CLI commands** - Items: 8, Documented: 8, Missing: 0, Coverage %: 100%
- **Troubleshooting** - Items: 10 common errors, Documented: 6, Missing: 4, Coverage %: 60%

**Overall:** 41/48 documented = 85% → Score: 6/10 (15 points)

## Non-Issues (Do NOT Count as Missing)

**Review EACH flagged item against this list before counting.**

### Pattern 1: Internal/Private Features
**Pattern:** Feature is internal implementation detail
**Example:** Private helper function `_format_internal()` not documented
**Why NOT an issue:** Internal features don't need public docs
**Action:** Remove from table with note "Internal/private"

### Pattern 2: Self-Evident Prerequisites
**Pattern:** Prerequisite obvious from project context
**Example:** README doesn't say "computer required"
**Why NOT an issue:** Obvious prerequisites don't need explicit docs
**Action:** Remove from table with note "Self-evident"

### Pattern 3: Covered in External Docs
**Pattern:** Feature documented in linked external resource
**Example:** "See API docs at https://api.example.com/docs"
**Why NOT an issue:** Coverage exists via external reference
**Action:** Remove from table with note "External docs"

### Pattern 4: Deprecated/Removed Features
**Pattern:** Feature no longer exists in current version
**Example:** v1 feature removed in v2, not in current docs
**Why NOT an issue:** Feature doesn't exist to document
**Action:** Remove from table with note "Deprecated/removed"
