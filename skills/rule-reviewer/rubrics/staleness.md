# Staleness Rubric (10 points)

## Scoring Criteria

### 5/5 (10 points): Excellent
- LastUpdated: ≤60 days from review date
- 0 deprecated tools
- 0 deprecated patterns
- 0 broken external links

### 4/5 (8 points): Good
- LastUpdated: 61-180 days
- 0-1 deprecated tools
- 0 deprecated patterns
- 0-1 broken links

### 3/5 (6 points): Acceptable
- LastUpdated: 181-365 days
- 2-3 deprecated tools
- 1 deprecated pattern
- 2-3 broken links

### 2/5 (4 points): Needs Work
- LastUpdated: 366-730 days
- 4-5 deprecated tools
- 2-3 deprecated patterns
- 4-5 broken links

### 1/5 (2 points): Poor
- LastUpdated: >730 days OR not declared
- >5 deprecated tools
- >3 deprecated patterns
- >5 broken links

## Counting Definitions

### LastUpdated Staleness

**Calculation:**
```python
days_stale = review_date - last_updated

# Example:
review_date = 2026-01-06
last_updated = 2025-10-15
days_stale = 83 days = 4/5 tier
```

**Staleness tiers (mutually exclusive):**
- 0-60 days (Fresh): 5/5 eligible
- 61-180 days (Recent): 4/5 max
- 181-365 days (Aging): 3/5 max
- 366-730 days (Stale): 2/5 max
- >730 days (Obsolete): 1/5 max
- Not declared (Unknown): 1/5 max

### Deprecated Tools

**Count each deprecated tool mentioned in rule:**

Use this canonical deprecated tools list:

**Python Ecosystem (deprecated as of 2025):**
- flake8: Use ruff (deprecated 2024-01)
- black: Use ruff format (deprecated 2024-01)
- isort: Use ruff check --select I (deprecated 2024-01)
- pip (for project mgmt): Use uv (deprecated 2024-06)
- mypy (when ty available): Use ty (deprecated 2025-06)
- pytest-cov alone: Use coverage + pytest (deprecated 2024-01)
- setuptools + setup.py: Use pyproject.toml (deprecated 2023-01)
- pipenv: Use uv (deprecated 2024-06)
- poetry (for new projects): Use uv (deprecated 2024-06)

**JavaScript/TypeScript (deprecated as of 2025):**
- eslint + prettier: Use biome (deprecated 2024-06)
- webpack: Use vite or esbuild (deprecated 2024-01)
- babel (standalone): Use built into bundlers (deprecated 2024-01)
- create-react-app: Use vite templates (deprecated 2023-06)
- yarn v1: Use pnpm or npm (deprecated 2024-01)

**Shell (deprecated as of 2025):**
- #!/bin/sh (non-POSIX): Use #!/usr/bin/env bash (deprecated 2020-01)
- which command: Use command -v (deprecated 2020-01)
- eval for commands: Use direct execution (deprecated 2020-01)
- unquoted variables: Use "$var" always (deprecated 2020-01)

**Snowflake (deprecated as of 2025):**
- Classic web UI refs: Use Snowsight (deprecated 2023-01)
- Old Snowpipe syntax: Use Current Snowpipe (deprecated 2023-06)
- Manual warehouse mgmt: Use Auto-suspend/resume (deprecated 2023-01)

### Deprecated Patterns

**Count each deprecated coding pattern:**

**Deprecated Pattern Checklist:**
- requirements.txt + pip: Use pyproject.toml + uv
- setup.py: Use pyproject.toml
- Python 3.8/3.9 refs: Use Python 3.11+
- Node.js <18 refs: Use Node.js 20+
- Manual Docker builds: Use BuildKit

### Broken External Links

**Check each external link:**
```bash
curl -I --max-time 5 [URL] 2>&1 | head -1
```

**Link status categories:**
- 200 OK: Valid (count 0)
- 301/302 Redirect: Stale (count 0.5)
- 404 Not Found: Broken (count 1)
- Timeout: Broken (count 1)
- Connection refused: Broken (count 1)

## Score Decision Matrix

**Score Tier Criteria:**
- **5/5 (10 pts):** ≤60 days stale, 0 deprecated tools, 0 patterns, 0 broken links
- **4/5 (8 pts):** 61-180 days stale, 0-1 deprecated tools, 0 patterns, 0-1 broken links
- **3/5 (6 pts):** 181-365 days stale, 2-3 deprecated tools, 1 pattern, 2-3 broken links
- **2/5 (4 pts):** 366-730 days stale, 4-5 deprecated tools, 2-3 patterns, 4-5 broken links
- **1/5 (2 pts):** >730 days stale, >5 deprecated tools, >3 patterns, >5 broken links

**Primary determinant:** LastUpdated days (overrides if in lower tier)

## Tool Currency Check

### Python Tools

Scan rule for these terms and check against deprecated list:

**Python Tool Inventory (example):**
- ruff (line 45): Current - OK
- flake8 (line 67): Deprecated - Use ruff
- uv (line 89): Current - OK
- pip install (line 120): Deprecated - Use uv pip

### JavaScript Tools

**JavaScript Tool Inventory (example):**
- biome (line 45): Current - OK
- eslint (line 67): Deprecated - Use biome
- vite (line 89): Current - OK

### Shell Patterns

**Shell Pattern Inventory (example):**
- #!/usr/bin/env bash (line 10): Current - OK
- `which python` (line 45): Deprecated - Use command -v
- set -euo pipefail (line 12): Current - OK

## External Link Validation

### Link Check Examples

**Link Status Inventory:**
- https://docs.snowflake.com/...: 200 - Valid
- https://example.com/old-page: 404 - Broken
- https://moved.example.com/...: 301 - Update needed

### Common Stale Link Patterns

**Version-specific URLs (often stale):**
- `docs.python.org/3.9/` should be `docs.python.org/3/`
- `nodejs.org/en/docs/v16/` should be current LTS

**Moved documentation:**
- Company acquisitions (e.g., tool X acquired by Y)
- Rebranded products
- Deprecated service documentation

## Worked Example

**Target:** Rule reviewed on 2026-01-06

### Step 1: Check LastUpdated

```markdown
Metadata:
LastUpdated: 2025-06-15
```

Days stale: 205 days = 3/5 tier (181-365 days)

### Step 2: Scan for Deprecated Tools

**Tool Status Inventory:**
- ruff (line 45): Current
- flake8 (line 67): Deprecated
- black (line 89): Deprecated
- uv (line 120): Current

**Count:** 2 deprecated tools

### Step 3: Scan for Deprecated Patterns

**Pattern Status Inventory:**
- pyproject.toml (line 30): Current
- Python 3.11+ (line 50): Current

**Count:** 0 deprecated patterns

### Step 4: Check External Links

**Link Status Inventory:**
- https://docs.snowflake.com/...: 200 Valid
- https://ruff.rs/docs/...: 200 Valid
- https://old-blog.example.com/post: 404 Broken

**Count:** 1 broken link

### Step 5: Calculate Score

**Component Assessment:**
- Days stale: 205 = 3/5 tier
- Deprecated tools: 2 = 3/5
- Deprecated patterns: 0 = 5/5
- Broken links: 1 = 4/5

**Final:** 3/5 (6 points) - days stale is primary determinant

### Step 6: Document in Review

```markdown
## Staleness: 3/5 (6 points)

**LastUpdated:** 2025-06-15 (205 days ago)
- Status: Aging (181-365 days tier)

**Deprecated tools:** 2
- Line 67: flake8 - Replace with ruff
- Line 89: black - Replace with ruff format

**Deprecated patterns:** 0

**Broken links:** 1
- Line 150: https://old-blog.example.com/post (404)

**Priority fixes:**
1. Update LastUpdated to current date
2. Replace flake8/black references with ruff
3. Fix or remove broken blog link
```

## Special Cases

### Intentionally Historical Content

If rule documents legacy patterns for migration purposes:

```markdown
## Legacy Patterns (For Migration Only)

> **Note:** This section documents deprecated patterns for teams migrating
> from older codebases. DO NOT use these patterns in new code.
```

**Scoring:** Do not count as deprecated if:
- Clearly marked as deprecated/legacy
- Current alternative provided
- Migration path documented

### Tool Version Specificity

When rule specifies minimum versions:

```markdown
# Check version currency
Python 3.8+  = Outdated (3.8 EOL Oct 2024)
Python 3.11+ = Current
Node.js 16+  = Outdated (16 EOL Sep 2023)
Node.js 20+  = Current (LTS)
```

## Inter-Run Consistency Target

**Expected variance:** 0 (objective measurements)

**Verification:**
- Days stale: Simple date arithmetic
- Deprecated tools: Use canonical list above
- Broken links: Use curl check (may vary if site is down)

**If link check varies:**
- Re-check after 24 hours
- Document transient vs persistent failures
- Count persistent failures only
