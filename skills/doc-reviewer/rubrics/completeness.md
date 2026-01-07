# Completeness Rubric (25 points)

## Scoring Criteria

### 5/5 (25 points): Excellent
- All features documented
- Complete setup instructions (prerequisites → working state)
- API/CLI reference complete
- Troubleshooting section present
- Examples for all major features

### 4/5 (20 points): Good
- Most features documented (90%+)
- Setup mostly complete (1-2 steps missing)
- API/CLI mostly covered
- Some troubleshooting present

### 3/5 (15 points): Acceptable
- Core features documented (75-89%)
- Setup has gaps (3-4 steps missing)
- API/CLI partially documented
- Limited troubleshooting

### 2/5 (10 points): Needs Work
- Many features missing (60-74%)
- Setup incomplete (>4 steps missing)
- API/CLI barely documented
- No troubleshooting

### 1/5 (5 points): Poor
- Most features undocumented (<60%)
- Setup unusable
- No API/CLI docs
- No troubleshooting

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
Base score = 5/5 (25 points)

Feature coverage:
  <60%: Cap at 2/5 (10 points)
  60-74%: Max 3/5 (15 points)
  75-89%: Max 4/5 (20 points)
  90-100%: Full 5/5 available

Missing setup steps: -1 point each (up to -5)
Incomplete API/CLI docs: -2 points
No troubleshooting: -2 points
Missing examples: -1 point per type (up to -4)

Minimum score: 1/5 (5 points)
```

## Critical Gate

If setup instructions are incomplete (can't get from zero to working):
- Cap score at 2/5 (10 points) maximum
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

**Overall:** 41/48 documented = 85% → Score: 4/5 (20 points)
