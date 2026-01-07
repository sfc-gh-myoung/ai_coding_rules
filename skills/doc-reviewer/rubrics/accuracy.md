# Accuracy Rubric (25 points)

## Scoring Criteria

### 5/5 (25 points): Excellent
- All file paths exist and are correct
- All commands execute successfully
- Code examples are current and functional
- Function/class names match codebase
- No broken references (>95% valid)

### 4/5 (20 points): Good
- 90-95% of references valid
- 1-2 minor path errors
- Most commands work
- Code examples mostly current

### 3/5 (15 points): Acceptable
- 75-89% of references valid
- 3-5 path errors
- Some commands outdated
- Code examples partially outdated

### 2/5 (10 points): Needs Work
- 60-74% of references valid
- 6-10 path errors
- Many commands don't work
- Code examples significantly outdated

### 1/5 (5 points): Poor
- <60% of references valid
- >10 path errors
- Most commands broken
- Code examples completely outdated

## Cross-Reference Verification

### File Path Verification

Check every file path mentioned in documentation:

```bash
# For each path in docs
ls -la path/to/file
# Or
test -f path/to/file && echo "EXISTS" || echo "MISSING"
```

**Track in table:**

- **`src/main.py`** - Line: 45, Type: File, Status: Exists, Notes: -
- **`config/settings.json`** - Line: 67, Type: File, Status: Missing, Notes: Should be `config/settings.yaml`
- **`utils/helpers.py`** - Line: 89, Type: File, Status: Exists, Notes: -

### Command Verification

Test every command shown in documentation:

```bash
# For setup commands
npm install  # Does this work?
pytest       # Does this execute?
task build   # Does this succeed?
```

**Safety considerations:**
- Only test read-only/safe commands
- Don't run destructive commands (rm, delete, drop)
- Don't run commands requiring auth/credentials
- Use dry-run flags when available

**Track in table:**

- **`npm install`** - Line: 23, Works?: Yes, Output: Success, Fix Needed: -
- **`python setup.py test`** - Line: 45, Works?: No, Output: ModuleNotFoundError, Fix Needed: Use `pytest` instead
- **`task lint`** - Line: 67, Works?: Yes, Output: Success, Fix Needed: -

### Code Example Verification

Check that code examples are current:

**Verify:**
- Imports still valid
- API calls match current version
- Syntax is current
- No deprecated patterns

**Example:**

```python
# Doc shows (line 123):
from flask import Flask
app = Flask(__name__)

# Verify:
 Flask still uses this pattern (valid as of 3.0.x)
```

```python
# Doc shows (line 145):
df.append(new_row)  # Deprecated!

# Should be:
df = pd.concat([df, new_row])
```

### Function/Class Name Verification

Verify names in documentation match codebase:

```bash
# Search for function in codebase
grep -r "def process_data" src/

# Search for class
grep -r "class UserManager" src/
```

**Track mismatches:**

- **`processData()`** - Line: 78, Codebase Name: `process_data()`, Status: Wrong case
- **`UserMgr`** - Line: 89, Codebase Name: `UserManager`, Status: Abbreviated
- **`calculate()`** - Line: 102, Codebase Name: `calculate()`, Status: Correct

## Scoring Formula

```
Base score = 5/5 (25 points)

File path errors: -0.5 points each (up to -10)
Command failures: -1 point each (up to -8)
Outdated code examples: -0.5 points each (up to -5)
Name mismatches: -0.3 points each (up to -3)

Minimum score: 1/5 (5 points)
```

## Critical Gate

If <60% of references are valid:
- Cap score at 1/5 (5 points) maximum
- Mark as CRITICAL issue
- Recommendation: Comprehensive accuracy audit required

## Common Accuracy Issues

### Issue 1: Outdated File Paths

**Problem:** Doc references `lib/` but code uses `src/`

**Fix:**
```diff
- See implementation in `lib/utils.py`
+ See implementation in `src/utils.py`
```

### Issue 2: Deprecated Commands

**Problem:** Doc shows `python setup.py test`

**Fix:**
```diff
- python setup.py test
+ pytest
```

### Issue 3: Wrong Function Names

**Problem:** Doc uses camelCase but code uses snake_case

**Fix:**
```diff
- Call `processData()` to begin
+ Call `process_data()` to begin
```

### Issue 4: Broken Code Examples

**Problem:** Example uses deprecated API

**Fix:**
```diff
- df.append(row, ignore_index=True)
+ df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
```

## Verification Table Template

Create this table during review:

- **File** - Reference: `src/main.py`, Line: 23, Status: Valid, Fix Required: -
- **File** - Reference: `config/old.json`, Line: 45, Status: Missing, Fix Required: Update to `config/new.yaml`
- **Command** - Reference: `npm test`, Line: 67, Status: Works, Fix Required: -
- **Command** - Reference: `make build`, Line: 89, Status: Fails, Fix Required: No Makefile exists
- **Function** - Reference: `getData()`, Line: 102, Status: Wrong, Fix Required: Should be `get_data()`
- **Class** - Reference: `Manager`, Line: 134, Status: Valid, Fix Required: -

**Summary:**
- Total references: 6
- Valid: 4 (67%)
- Invalid: 2 (33%)
- Score: 3/5 (15 points) based on 67% accuracy
