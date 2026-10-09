# Phase 3: Activity Matching

> **Layer: SOFT (best-effort, non-deterministic).** Keyword extraction and matching
> are LLM-mediated. The **high-risk-action check (Step 4)** is the exception: it is
> HARD (mandatory fixed lookups regardless of keyword judgment).

## Purpose

Discover activity-specific rules by searching rule frontmatter for keywords extracted from the user request.

## Algorithm

### Step 1: Extract Keywords

From the user request, identify:
1. **Primary verb** (test, deploy, lint, commit, help, fix, create, etc.)
2. **Primary technology** (Python, Docker, Snowflake, Streamlit, etc.)
3. **File extensions** (.py, .sql, .tsx, etc.) - already handled in Phase 2
4. **Domain nouns** (dashboard, api, notebook, agent, etc.)

If ANY word could be a keyword, extract it. Only fail if the request is truly empty.

**Multi-technology splitting heuristic:**

When the user request contains multiple technologies joined by delimiters (`+`, `and`, `with`, `,`, `using`):

1. Split request on delimiters to identify individual technologies
2. Technical terms (capitalized, hyphenated, acronyms like SSE/API/SPCS) are almost always keywords
3. Each technology should be included in the matcher prompt

**Example:** `"FastAPI + HTMX + SSE in SPCS"` becomes:
```bash
python3 src/ai_rules/match_rules.py --prompt "FastAPI + HTMX + SSE in SPCS" --rules-dir rules/
```

### Step 2: Run the deterministic matcher

Run the matcher once with the complete user request. It scans YAML frontmatter
directly from `rules/` and returns a metadata-only manifest.

```bash
python3 src/ai_rules/match_rules.py --prompt "$USER_REQUEST" --rules-dir rules/
```

Use `candidate_rules`, `load_sequence`, and `deferred_rules` from the returned
manifest. Rule bodies do not appear in the manifest.

**If the matcher is unavailable:** Read YAML frontmatter from the relevant
`rules/*.md` files directly and record the degraded discovery mode. Do not use
or recreate a generated index.

**FORBIDDEN:** Substituting a deleted or generated rule index for the matcher.

### Step 2.5: Sanity Check (MANDATORY)

Zero results for a common request may indicate a malformed prompt or unavailable
rules directory. Inspect the matcher result before treating it as a valid
foundation-only selection.

**On zero results for any common keyword (python, sql, docker, deploy, test, snowflake, fastapi, streamlit):**

1. Re-execute grep once (transient failure recovery)
2. If still zero: Execute the direct-frontmatter fallback immediately
3. Document anomaly in response: "Matcher returned unexpectedly empty - used frontmatter fallback"

**Expected output volume:**
- Multi-technology requests: 5-50 matching lines
- Single-technology requests: 1-10 matching lines
- Zero lines for reasonable keywords = ANOMALY requiring fallback

### Step 3: Record Matches

From the matcher manifest, identify matching activity rules. Record each with reason:
- `"(keyword: test)"` for keyword matches

### Step 4: High-Risk Action Check

Certain keywords trigger mandatory additional searches:

| Keyword | Must Search For | Expected Rule |
|---------|----------------|---------------|
| git, commit, push, merge | `"git"` | `803-project-git-workflow.md` |
| deploy, deployment | `"deploy"` | `820-taskfile-automation.md` |
| test, pytest | `"test"` | `206-python-pytest.md` |
| README, documentation | `"readme"` | `801-project-readme.md` |
| CHANGELOG | `"changelog"` | `800-project-changelog.md` |

If any high-risk keyword is present, the corresponding search is mandatory even if a rule was already matched for that keyword.

## Rules

- Gate 2 passes if the matcher (or direct-frontmatter fallback) was executed AND specific matched rules can be cited
- A Gate 2 claim without tool execution is INVALID
- Never claim Gate 2 passed based on memory or prior session context
- If the matcher returns no matches for a keyword: note "No rules found for [keyword]"
- **Zero results for common keywords (python, docker, deploy, test, snowflake, fastapi) is an ANOMALY**: re-execute the matcher once, then use direct frontmatter fallback
