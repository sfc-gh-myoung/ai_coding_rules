# Phase 3: Activity Matching

## Purpose

Discover activity-specific rules by searching RULES_INDEX.md for keywords extracted from the user request.

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
3. Each technology should be included in the grep OR pattern

**Example:** `"FastAPI + HTMX + SSE in SPCS"` becomes:
```bash
grep -iE "fastapi|htmx|sse|spcs" {rules_path}/RULES_INDEX.md
```

### Step 2: Search RULES_INDEX.md

Execute a single compound grep combining all keywords:

```bash
grep -iE "KEYWORD1|KEYWORD2|KEYWORD3" {rules_path}/RULES_INDEX.md
```

**Expected outcome for typical requests:**
- 5-50 matching lines for multi-technology requests
- 1-10 matching lines for single-technology requests
- 0 lines = ANOMALY (re-execute grep once, then use fallback immediately)

**If grep unavailable:** Read RULES_INDEX.md via `read_file` and manually scan for keywords. This is the required fallback.

**FORBIDDEN:** Substituting glob, find, ls, or any file-discovery tool for grep.

### Step 2.5: Sanity Check (MANDATORY)

Zero results is almost always an anomaly. RULES_INDEX.md contains 750+ lines with 159 keyword entries across 100+ rules.

**On zero results for any common keyword (python, sql, docker, deploy, test, snowflake, fastapi, streamlit):**

1. Re-execute grep once (transient failure recovery)
2. If still zero: Execute `read_file` fallback immediately
3. Document anomaly in response: "Grep returned unexpectedly empty - used fallback"

**Expected output volume:**
- Multi-technology requests: 5-50 matching lines
- Single-technology requests: 1-10 matching lines
- Zero lines for reasonable keywords = ANOMALY requiring fallback

### Step 3: Record Matches

From grep output, identify rules listed in Section 3 (Activity Rules). Record each with reason:
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

- Gate 2 passes if grep (or read_file fallback) was executed AND specific matched lines can be cited
- A Gate 2 claim without tool execution is INVALID
- Never claim Gate 2 passed based on memory or prior session context
- If grep returns no matches for a keyword: note "No rules found for [keyword]"
- **Zero results for common keywords (python, docker, deploy, test, snowflake, fastapi) is an ANOMALY** — re-execute grep once, then use read_file fallback
- **Consistency check:** Keywords searched in Gate 2 must produce rules in Gate 3, or explicitly state "no rules found"
