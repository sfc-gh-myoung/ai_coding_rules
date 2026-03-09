# Staleness Rubric

> **STATUS: INFORMATIONAL ONLY - NOT SCORED**
>
> As of Scoring Rubric v2.0, Staleness is **no longer a scored dimension**. This rubric is retained for:
> - Historical reference
> - Informational reporting in reviews
> - Guidance on identifying outdated content
>
> **Findings from this rubric appear in the recommendations section, not in the score.**

---

## Staleness Check (Informational)

When reviewing rules, note staleness issues to inform recommendations:

| Finding Type | Recommendation |
|--------------|----------------|
| LastUpdated >180 days | Flag for review |
| Deprecated tools | Note in recommendations |
| Broken links | Priority fix |
| Outdated patterns | Suggest updates |

---

## Original Rubric (Historical Reference)

The following content is preserved for historical reference and to guide staleness analysis.

---

## Mandatory Issue Inventory (REQUIRED)

**CRITICAL:** You MUST create and fill this inventory BEFORE calculating score.

### Why This Is Required

- **Eliminates counting variance:** Same rule → same inventory → same score
- **Prevents false negatives:** Systematic checks catch all staleness issues
- **Provides evidence:** Inventory shows exactly what was evaluated
- **Enables verification:** Users can audit scoring decisions

### Inventory Template

**LastUpdated Assessment:**

| Metric | Value |
|--------|-------|
| LastUpdated value | YYYY-MM-DD |
| Review date | YYYY-MM-DD |
| Days stale | NNN |
| Staleness tier | X/5 |

**Deprecated Tools:**

| Line | Tool Found | Status | Replacement |
|------|------------|--------|-------------|
| 45 | ruff | Current | - |
| 67 | flake8 | Deprecated | ruff |
| 89 | black | Deprecated | ruff format |

**Deprecated Patterns:**

| Line | Pattern Found | Status | Replacement |
|------|---------------|--------|-------------|
| 30 | pyproject.toml | Current | - |
| 120 | requirements.txt | Deprecated | pyproject.toml + uv |

**External Links:**

| Line | URL | Status | Notes |
|------|-----|--------|-------|
| 150 | https://docs.snowflake.com/... | 200 | Valid |
| 180 | https://old-blog.example.com | 404 | Broken |

### Counting Protocol (5 Steps)

**Step 1: Create Empty Inventory**
- Copy templates above into working document
- Do NOT start reading rule yet

**Step 2: Calculate Days Stale**
- Extract LastUpdated from metadata
- Calculate: review_date - last_updated
- Look up staleness tier

**Step 3: Read Rule Systematically**
- Start at line 1, read to END (no skipping)
- Check each tool reference against deprecated list
- Check each pattern against deprecated list
- Record each external link

**Step 4: Verify External Links**
- Test each URL: `curl -I --max-time 5 [URL]`
- Record status codes
- Count broken links (404, timeout, connection refused)

**Step 5: Look Up Score**
- Use adjusted totals in Score Decision Matrix
- Record score with inventory evidence

## Scoring Formula

**Raw Score:** 0-10
**Weight:** 2
**Points:** Raw × (2/2) = Raw × 1.0

## Scoring Criteria

### 10/10 (10 points): Perfect
- LastUpdated: ≤30 days from review date
- 0 deprecated tools
- 0 deprecated patterns
- 0 broken external links

### 9/10 (9 points): Near-Perfect
- LastUpdated: 31-60 days
- 0 deprecated tools
- 0 deprecated patterns
- 0 broken links

### 8/10 (8 points): Excellent
- LastUpdated: 61-90 days
- 0 deprecated tools
- 0 deprecated patterns
- 0-1 broken links

### 7/10 (7 points): Good
- LastUpdated: 91-180 days
- 0-1 deprecated tools
- 0 deprecated patterns
- 0-1 broken links

### 6/10 (6 points): Acceptable
- LastUpdated: 181-270 days
- 1-2 deprecated tools
- 0 deprecated patterns
- 1-2 broken links

### 5/10 (5 points): Borderline
- LastUpdated: 271-365 days
- 2-3 deprecated tools
- 1 deprecated pattern
- 2-3 broken links

### 4/10 (4 points): Needs Work
- LastUpdated: 366-500 days
- 3-4 deprecated tools
- 1-2 deprecated patterns
- 3-4 broken links

### 3/10 (3 points): Poor
- LastUpdated: 501-730 days
- 4-5 deprecated tools
- 2-3 deprecated patterns
- 4-5 broken links

### 2/10 (2 points): Very Poor
- LastUpdated: 731-1000 days
- 5-6 deprecated tools
- 3-4 deprecated patterns
- 5-6 broken links

### 1/10 (1 point): Inadequate
- LastUpdated: >1000 days OR not declared
- >6 deprecated tools
- >4 deprecated patterns
- >6 broken links

### 0/10 (0 points): Obsolete
- LastUpdated not declared
- Core technology deprecated
- Rule no longer applicable

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
- **10/10 (10 pts):** ≤30 days stale, 0 deprecated tools, 0 patterns, 0 broken links
- **9/10 (9 pts):** 31-60 days stale, 0 deprecated tools, 0 patterns, 0 broken links
- **8/10 (8 pts):** 61-90 days stale, 0 deprecated tools, 0 patterns, 0-1 broken links
- **7/10 (7 pts):** 91-180 days stale, 0-1 deprecated tools, 0 patterns, 0-1 broken links
- **6/10 (6 pts):** 181-270 days stale, 1-2 deprecated tools, 0 patterns, 1-2 broken links
- **5/10 (5 pts):** 271-365 days stale, 2-3 deprecated tools, 1 pattern, 2-3 broken links
- **4/10 (4 pts):** 366-500 days stale, 3-4 deprecated tools, 1-2 patterns, 3-4 broken links
- **3/10 (3 pts):** 501-730 days stale, 4-5 deprecated tools, 2-3 patterns, 4-5 broken links
- **2/10 (2 pts):** 731-1000 days stale, 5-6 deprecated tools, 3-4 patterns, 5-6 broken links
- **1/10 (1 pt):** >1000 days stale OR not declared, >6 deprecated tools, >4 patterns, >6 broken links
- **0/10 (0 pts):** Not declared, core technology deprecated, rule obsolete

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

### Documentation Currency Check

**Purpose:** Detect deprecation warnings in linked documentation that HTTP status checks miss.

**Scope:** Only URLs in `## External Documentation` or `### External Documentation` sections.

**Step 1: Extract documentation links**

```python
import re

def extract_doc_links(rule_content: str) -> list[str]:
    """Extract URLs from External Documentation section only."""
    # Find External Documentation section
    pattern = r'##+ External Documentation\s*\n(.*?)(?=\n##|\Z)'
    match = re.search(pattern, rule_content, re.DOTALL)
    if not match:
        return []
    
    section = match.group(1)
    # Extract markdown links and bare URLs
    urls = re.findall(r'\[.*?\]\((https?://[^\)]+)\)', section)
    urls += re.findall(r'(?<!\()(https?://[^\s\)]+)', section)
    return list(set(urls))
```

**Step 2: Fetch and scan each link**

For each URL:
1. Use `web_fetch(url, extract_text=true)` to retrieve content
2. If fetch fails (timeout, auth required): Skip with note "Unable to fetch: [reason]"
3. If fetch succeeds: Scan extracted text for deprecation signals

**Step 3: Deprecation signal detection**

Search fetched content (case-insensitive) for these patterns:

**High-confidence signals (count 1.0 each):**
- "deprecated" followed by feature/function name within 100 chars
- "end of life" or "EOL"
- "sunset" (as verb or noun related to features)
- "no longer supported"
- "removed in version"
- "breaking change" (in changelog context)

**Medium-confidence signals (count 0.5 each):**
- "legacy" (when describing current feature, not migration docs)
- "replaced by" or "superseded by"
- "will be removed"
- "scheduled for removal"

**False positive filters (do NOT count):**
- Signal appears in "Migration from..." or "Upgrading from..." sections
- Signal describes a DIFFERENT product/feature than the rule references
- Signal is in user comments or forum posts (not official docs)

**Step 4: Calculate documentation currency penalty**

| Signals Found | Penalty | Rationale |
|---------------|---------|-----------|
| 0 | 0 points | Documentation current |
| 0.5-1.5 | -0.5 points | Minor concern |
| 2-3 | -1 point | Moderate concern |
| 3.5+ | -2 points | Significant staleness |

**Maximum penalty:** -2 points (documentation currency cannot reduce score below 1/5)

**Step 5: Document findings**

```markdown
**Documentation Currency Check:**
- Links scanned: 4
- Deprecation signals: 2

| URL | Signal | Context |
|-----|--------|---------|
| https://docs.example.com/api | "deprecated since v3.0" | Auth endpoint mentioned in rule |
| https://docs.example.com/guide | None | - |

Penalty: -1 point
```

**See:** `workflows/doc-currency-check.md` for detailed execution steps.

### Documentation Currency Error Handling

**Network failures:**
- Timeout (>10s): Skip link, note "Timeout - unable to verify"
- Connection refused: Skip link, note "Connection refused"
- HTTP 403/401: Skip link, note "Auth required - manual verification needed"

**Content parsing failures:**
- Empty response: Skip link, note "Empty response"
- Non-text content: Skip link, note "Non-text content type"

**Fallback:** If >50% of links cannot be fetched, note "Documentation currency check incomplete" and do not apply penalty.

## Worked Example

**Target:** Rule reviewed on 2026-01-06

### Step 1: Check LastUpdated

```markdown
Metadata:
LastUpdated: 2025-06-15
```

Days stale: 205 days = 6/10 tier (181-270 days)

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

**Final:** 5/10 (5 points) - days stale is primary determinant

### Step 6: Document in Review

```markdown
## Staleness: 5/10 (5 points)

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

## Non-Issues (Do NOT Count as Stale)

**Review EACH flagged item against this list before counting.**

### Pattern 1: Legacy Documentation Section
**Pattern:** Deprecated tool in clearly marked "Legacy" or "Migration" section
**Example:** "## Legacy: Using flake8 (for migration from older projects)"
**Why NOT an issue:** Intentionally documenting old patterns for migration
**Action:** Remove from inventory with note "Legacy section (intentional)"

### Pattern 2: Version Flexibility
**Pattern:** Version range that includes older but still supported versions
**Example:** "Python 3.9+" where 3.9 is still receiving security updates
**Why NOT an issue:** Version is still supported (not EOL)
**Action:** Remove from inventory with note "Still supported version"

### Pattern 3: Redirected Link (Works)
**Pattern:** Link returns 301/302 but redirects to valid content
**Example:** Old URL redirects to new URL that returns 200
**Why NOT an issue:** Content is accessible (recommend update, but not broken)
**Action:** Mark as "Update recommended" not "Broken"

### Pattern 4: Tool Still Functional
**Pattern:** Tool marked as "deprecated" but still works and is maintained
**Example:** "black" is superseded by ruff but still actively maintained
**Why NOT an issue:** Tool is functional (recommend update, but not broken)
**Action:** Mark as "Update recommended" with severity 0.5 (not 1.0)
