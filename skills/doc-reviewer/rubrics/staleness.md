# Staleness Rubric (10 points)

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 2
**Points:** Raw × (2/2) = Raw × 1.0

## Scoring Criteria

### 10/10 (10 points): Perfect
- All tool versions current
- No deprecated patterns
- All links valid (200 status)
- References match current codebase
- No outdated screenshots/images

### 9/10 (9 points): Near-Perfect
- Tool versions current
- 0 deprecated patterns
- 99%+ links valid
- References current

### 8/10 (8 points): Excellent
- Most tools current (1 minor version old)
- 1 deprecated pattern
- 97-98% links valid
- References mostly current

### 7/10 (7 points): Good
- Most tools current (1-2 minor versions old)
- 1-2 deprecated patterns
- 95-96% links valid
- References mostly current

### 6/10 (6 points): Acceptable
- Some tools current (2-3 minor versions old)
- 2-3 deprecated patterns
- 90-94% links valid
- Some stale references

### 5/10 (5 points): Borderline
- Some tools outdated (3-4 versions old)
- 3-4 deprecated patterns
- 85-89% links valid
- Some stale references

### 4/10 (4 points): Needs Work
- Tools outdated (4-6 versions old)
- 4-5 deprecated patterns
- 75-84% links valid
- Many stale references

### 3/10 (3 points): Poor
- Many tools outdated (6-8 versions old)
- 5-6 deprecated patterns
- 65-74% links valid
- Many stale references

### 2/10 (2 points): Very Poor
- Most tools outdated (8-10 versions old)
- 6-7 deprecated patterns
- 55-64% links valid
- Most references stale

### 1/10 (1 point): Inadequate
- Most tools obsolete (>10 versions old)
- >7 deprecated patterns
- 40-54% links valid
- References completely outdated

### 0/10 (0 points): Obsolete
- Tools EOL
- Pervasive deprecated patterns
- <40% links valid
- Documentation unreliable

## Link Validation

### Test External Links

Test each external URL:

```bash
# Quick test
curl -I --max-time 5 https://example.com/ 2>&1 | head -1

# Expected: HTTP/2 200 or HTTP/1.1 200
```

**Track results:**

- **https://docs.python.org/3/** - Line: 23, Status: 200, Action: None
- **https://oldsite.com/guide** - Line: 45, Status: 404, Action: Remove or update
- **https://api.service.com/v1** - Line: 67, Status: 301 ➡️, Action: Update to final URL

**Scoring:**
- 100% valid: No penalty
- 97-99% valid: -0 points
- 90-96% valid: -0.5 point
- 75-89% valid: -1 point
- 60-74% valid: -1.5 points
- 40-59% valid: -2 points
- <40% valid: -3 points (cap at 2/10)

### Check Redirects

Permanent redirects (301/308) should be updated:

**Example:**
```markdown
# Old (redirects)
https://github.com/user/repo/wiki

# Updated
https://github.com/user/repo/blob/main/docs/
```

## Tool Version Currency

### Version References

Check all tool versions mentioned:

- **Python** - Doc Version: 3.8, Current Version: 3.12, Status: Outdated (3.8 EOL)
- **Node.js** - Doc Version: 18.x, Current Version: 20.x, Status: Prev LTS
- **PostgreSQL** - Doc Version: 15, Current Version: 16, Status: Current
- **React** - Doc Version: 18, Current Version: 18, Status: Current

**Outdated tool penalty:** -0.5 points per tool (up to -3)

### Deprecated Pattern Detection

Search for outdated patterns:

**Python:**
-  `setup.py install` → Use `pip install .`
-  `python -m pytest` still OK, but `pytest` preferred
-  `requirements.txt` alone → Use `pyproject.toml`

**JavaScript:**
-  `npm install --save` → Unnecessary (default since npm 5)
-  `var` → Use `const`/`let`
-  `create-react-app` → Use Vite

**Docker:**
-  `MAINTAINER` → Use `LABEL maintainer=`
-  `ADD` (for URLs) → Use `RUN curl`

**Git:**
-  `git checkout -b` → `git switch -c` (modern)
-  `master` branch → `main` (convention)

**Penalty:** -0.5 points per deprecated pattern (up to -3)

## Screenshot/Image Staleness

Check if screenshots match current UI:

- **dashboard.png** - Line: 45, Matches Current UI?: No, Action: Update screenshot
- **login-flow.gif** - Line: 67, Matches Current UI?: Yes, Action: None
- **settings.png** - Line: 89, Matches Current UI?: Partial, Action: Update or remove

**Penalty:** -0.5 points per outdated image (up to -2)

## Code Example Currency

Verify examples use current syntax:

**Outdated:**
```python
# Old async syntax
@asyncio.coroutine
def fetch_data():
    result = yield from http.get(url)
```

**Current:**
```python
# Modern async/await
async def fetch_data():
    result = await http.get(url)
```

## Scoring Formula

```
Base score = 10/10 (10 points)

Link validation:
  100%: No penalty
  97-99%: -0 points
  90-96%: -0.5 points
  75-89%: -1 point
  60-74%: -1.5 points
  40-59%: -2 points
  <40%: -3 points

Tool versions outdated: -0.25 each (up to -1.5)
Deprecated patterns: -0.25 each (up to -1.5)
Outdated screenshots: -0.25 each (up to -1)

Minimum score: 0/10 (0 points)
```

## Critical Gate

If most links are broken (<40% valid):
- Cap score at 2/10 (2 points) maximum
- Mark as CRITICAL issue
- Documentation is unreliable

## Common Staleness Issues

### Issue 1: Broken Documentation Links

**Problem:**
```markdown
See [official docs](https://docs.example.com/v1.0/)
→ Returns 404
```

**Fix:**
```markdown
See [official docs](https://docs.example.com/latest/)
```

### Issue 2: Outdated Tool Versions

**Problem:**
```markdown
Requires Python 3.7+ (3.7 is EOL)
```

**Fix:**
```markdown
Requires Python 3.11+ (3.11 is current stable)
```

### Issue 3: Deprecated Commands

**Problem:**
```markdown
npm install --save react
```

**Fix:**
```markdown
npm install react
```
(--save is default since npm 5)

### Issue 4: Old Screenshots

**Problem:** Screenshot shows UI from 2 years ago

**Fix:** Update screenshot or add note "UI may differ slightly"

## Staleness Audit Checklist

During review, verify:

- [ ] All external links return 200 status
- [ ] Redirects (301/308) updated to final URLs
- [ ] Tool versions are current or prev LTS
- [ ] No EOL software recommended
- [ ] No deprecated commands/patterns
- [ ] Screenshots match current UI
- [ ] Code examples use modern syntax
- [ ] API endpoints still valid
- [ ] References match current codebase
- [ ] Last updated date reasonable

## Link Validation Table Template

Use during review:

- **https://docs.python.org/3/** - Line: 23, Status: 200, Response Time: 0.3s, Action: None
- **https://oldsite.com** - Line: 45, Status: 404, Response Time: -, Action: Remove
- **https://api.v1.com** - Line: 67, Status: 301 ➡️, Response Time: 0.5s, Action: Update to v2
- **https://example.com** - Line: 89, Status: Timeout ⏱️, Response Time: >5s, Action: Check URL

**Summary:**
- Total links: 4
- Valid (200): 1 (25%)
- Broken/Timeout: 2 (50%)
- Redirects: 1 (25%)
- Action required: 3 links need updates
- Score: 4/10 (4 points) due to <60% valid
