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

### Step 2: Search RULES_INDEX.md

For each extracted keyword:

```bash
grep -i "KEYWORD" {rules_path}/RULES_INDEX.md
```

**If grep unavailable:** Read RULES_INDEX.md via `read_file` and manually scan for keywords. This is the required fallback.

**FORBIDDEN:** Substituting glob, find, ls, or any file-discovery tool for grep.

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
