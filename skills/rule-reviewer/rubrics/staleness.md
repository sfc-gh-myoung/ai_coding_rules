# Staleness Rubric (10 points)

## Scoring Criteria

### 5/5 (10 points): Excellent
- LastUpdated within 60 days of review
- All tools/versions current
- No deprecated patterns
- External links valid
- Recommended practices align with current standards

### 4/5 (8 points): Good
- LastUpdated 61-180 days ago
- Tools mostly current (1-2 minor version changes)
- No critical deprecations
- Links valid

### 3/5 (6 points): Acceptable
- LastUpdated 181-365 days ago
- Some outdated tool versions (3-5 changes needed)
- 1-2 deprecated patterns present
- Some broken links

### 2/5 (4 points): Needs Work
- LastUpdated >365 days ago
- Multiple outdated tools (>5 changes needed)
- 3-5 deprecated patterns
- Multiple broken links

### 1/5 (2 points): Poor
- LastUpdated >730 days ago OR not declared
- Extensive obsolete content
- >5 deprecated patterns
- Most links broken
- Recommends superseded approaches

## LastUpdated Field Check

Calculate staleness from review date:

```python
review_date = "2026-01-06"
last_updated = "2026-01-05"  # From rule metadata

days_stale = (review_date - last_updated).days

if days_stale <= 60:
    freshness = "Excellent"
elif days_stale <= 180:
    freshness = "Good"
elif days_stale <= 365:
    freshness = "Acceptable"
elif days_stale <= 730:
    freshness = "Needs update"
else:
    freshness = "Stale"
```

## Tool and Version Currency

### Python Ecosystem

Check for outdated tools:

**Deprecated (update needed):**
- ❌ `flake8` → Use `ruff` instead
- ❌ `black` → Use `ruff format` instead
- ❌ `isort` → Use `ruff check --select I` instead
- ❌ `pip` for project management → Use `uv` instead
- ❌ `mypy` (when ty available) → Use `ty` (Astral toolchain)
- ❌ `pytest-cov` alone → Use `coverage` with pytest
- ❌ `setuptools` + `setup.py` → Use `pyproject.toml` only

**Current tools:**
- ✅ `uv` (package management)
- ✅ `ruff` (linting + formatting)
- ✅ `ty` or `mypy` (type checking)
- ✅ `pytest` (testing)
- ✅ `pyproject.toml` (configuration)

### Snowflake Features

Check for outdated patterns:

**Deprecated:**
- ❌ Old Snowpipe syntax (pre-2023)
- ❌ `COPY INTO` without file format objects
- ❌ Manual warehouse management (use auto-suspend/resume)
- ❌ Classic web UI references (use Snowsight)

**Current:**
- ✅ Snowflake Native Apps (2023+)
- ✅ Streams + Tasks for incremental patterns
- ✅ Snowsight UI references
- ✅ Cortex AI functions (2024+)
- ✅ Semantic Views (2024+)

### JavaScript/TypeScript

Check for outdated tools:

**Deprecated:**
- ❌ `eslint` + `prettier` separately → Use `biome` instead
- ❌ `webpack` → Use `vite` or `esbuild`
- ❌ `babel` standalone → Often built into modern bundlers
- ❌ `create-react-app` → Use `vite` templates

**Current:**
- ✅ `biome` (linting + formatting)
- ✅ `vite` (build tool)
- ✅ `pnpm` or `npm` (package management)
- ✅ TypeScript 5.x

### Shell Scripting

Check for outdated patterns:

**Deprecated:**
- ❌ `#!/bin/sh` without explicit POSIX compliance
- ❌ Unquoted variables (`$var` instead of `"$var"`)
- ❌ `eval` for command construction
- ❌ `which` command → Use `command -v` instead

**Current:**
- ✅ `#!/usr/bin/env bash` or `#!/bin/bash`
- ✅ Strict mode: `set -euo pipefail`
- ✅ ShellCheck compliance
- ✅ `command -v` for existence checks

## External Link Validation

### Check Link Status

For each external link in References section:

```bash
# Quick check (if curl available)
curl -I --max-time 5 https://docs.snowflake.com/ 2>&1 | head -1
# Expected: HTTP/2 200 or HTTP/1.1 200
```

**Common issues:**
- 404: Page not found (broken link)
- 301/302: Redirects (update to final URL)
- Timeout: Site unreachable (verify URL)

### Link Categories

**Official Documentation (High Priority):**
- Snowflake: https://docs.snowflake.com/
- Python: https://docs.python.org/
- Claude: https://docs.anthropic.com/
- Tool docs: Ruff, uv, Vite, etc.

**Community Resources (Medium Priority):**
- GitHub repositories
- Best practices guides
- Community tutorials

**Versioned URLs (Watch for staleness):**
- https://docs.python.org/3.11/ ← Version-specific
- https://docs.python.org/3/ ← Version-agnostic (better)

## Deprecated Pattern Detection

### Python Anti-Patterns

**Search for these outdated patterns:**

```python
# Deprecated: requirements.txt + pip
pip install -r requirements.txt

# Current: pyproject.toml + uv
uv sync

# Deprecated: setup.py
python setup.py install

# Current: pyproject.toml
uv pip install -e .
```

### Snowflake Anti-Patterns

**Search for these outdated patterns:**

```sql
-- Deprecated: Manual warehouse sizing
ALTER WAREHOUSE my_wh SET WAREHOUSE_SIZE = 'LARGE';
-- Better: Use auto-scaling with min/max
CREATE WAREHOUSE my_wh 
  AUTO_SUSPEND = 60 
  AUTO_RESUME = TRUE
  MIN_CLUSTER_COUNT = 1
  MAX_CLUSTER_COUNT = 3;

-- Deprecated: Classic UI mention
"View results in Snowflake UI"
-- Current: Reference Snowsight
"View results in Snowsight"
```

### General Anti-Patterns

- References to Python 2.x
- Node.js < 18 (LTS is 20.x as of 2024)
- Git commands without `--no-verify` awareness
- Docker without BuildKit
- Manual dependency installation vs package managers

## Scoring Formula

```
Base score = 5/5 (10 points)

LastUpdated staleness:
  ≤60 days: 0 penalty
  61-180 days: -1 point
  181-365 days: -2 points
  366-730 days: -3 points
  >730 days: -4 points

Outdated tools:
  Per deprecated tool: -0.5 points (up to -3)

Deprecated patterns:
  Per pattern: -0.5 points (up to -2)

Broken external links:
  Per broken link: -0.3 points (up to -2)

Minimum score: 1/5 (2 points)
```

## Common Staleness Issues

### Issue 1: LastUpdated Not Updated

**Problem:** LastUpdated says 2023-06-15 but review is 2026-01-06
**Impact:** 925 days stale → 1/5 score
**Recommendation:** Update LastUpdated field when modifying rule

### Issue 2: Using Deprecated Tools

**Problem:** Rule recommends `flake8` and `black`
**Impact:** -1 point (2 deprecated tools × 0.5)
**Recommendation:** Update to `ruff` for both linting and formatting

### Issue 3: Broken Documentation Links

**Problem:** Link to `docs.snowflake.com/en/v2.0/...` returns 404
**Impact:** -0.3 points per broken link
**Recommendation:** Update to current documentation URLs

### Issue 4: Outdated Version Requirements

**Problem:** Rule specifies "Python 3.8+"
**Impact:** Python 3.8 EOL was Oct 2024
**Recommendation:** Update to "Python 3.11+" (current stable baseline)

## Special Cases

### Intentionally Historical Content

If rule documents legacy patterns for migration purposes:

```markdown
## Legacy Patterns (For Migration Only)

> **Note:** This section documents deprecated patterns for teams migrating
> from older codebases. DO NOT use these patterns in new code.

### Old Pattern: setup.py
[Documentation of old pattern]

### Current Pattern: pyproject.toml
[Documentation of current pattern]
```

**Scoring:** Do not penalize for documented legacy patterns if:
- Clearly marked as deprecated
- Current alternative provided
- Migration path documented
