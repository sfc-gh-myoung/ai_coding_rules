# Phase 2: Domain Matching

## Purpose

Select domain rules based on file extensions and directory paths mentioned in the user request.

## Algorithm

### Step 0: Project Context (check FIRST)

```
IF PROJECT.md exists in workspace root:
    Load via read_file, extract project context
    Apply any project-specific rule overrides
IF PROJECT.md does not exist:
    Skip (no error, PROJECT.md is optional)
```

### Step 1: Directory-Based Rules

```
IF request mentions files in `skills/` directory:
    Load: 002h-claude-code-skills.md
IF request mentions files in `rules/` directory:
    Load: 002-rule-governance.md
IF neither directory mentioned:
    Skip to Step 2
```

### Step 2: File Extension Matching

Extract all file extensions from the user request, then look up each in RULES_INDEX.md Section 2.

**Authoritative Extension Mapping:**

| Extension(s) | Rule |
|-------------|------|
| `.sql` | `102-snowflake-sql-core.md` |
| `.py`, `.pyi` | `200-python-core.md` |
| `.toml`, `.yaml`, `.yml` | `202-markup-config-validation.md` |
| `pyproject.toml` | `203-python-project-setup.md` |
| `.bash`, `.sh` | `300-bash-scripting-core.md` |
| `.zsh` | `310b-zsh-compatibility.md` |
| `Dockerfile`, `docker-compose.yaml` | `350-docker-core.md` |
| `Containerfile`, `podman-compose.yaml` | `351-podman-core.md` |
| `.cjs`, `.js`, `.mjs` | `420-javascript-core.md` |
| `.ts` | `430-typescript-core.md` |
| `.jsx`, `.tsx` | `440-react-core.md` |
| `.go`, `go.mod` | `600-golang-core.md` |
| `CHANGELOG.md` | `800-project-changelog.md` |
| `README.md` | `801-project-readme.md` |
| `CONTRIBUTING.md` | `802-project-contributing.md` |
| `Taskfile.yml` | `820-taskfile-automation.md` |
| `Makefile` | `821-makefile-automation.md` |

**Keyword-to-domain rules (no file extension needed):**

| Keyword | Rule |
|---------|------|
| `streamlit` | `101-snowflake-streamlit-core.md` |
| `snowflake` | `100-snowflake-core.md` |

**Implied extensions from technology keywords:**

When a technology keyword is present without an explicit file extension, the corresponding domain rule should also be loaded:

| Technology Keyword | Implied Extension | Domain Rule |
|--------------------|-------------------|-------------|
| `Python`, `FastAPI`, `Django`, `Flask` | `.py` | `200-python-core.md` |
| `Streamlit` | `.py` | `200-python-core.md` |
| `TypeScript`, `Angular`, `Nest` | `.ts` | `430-typescript-core.md` |
| `React`, `Next.js` | `.tsx` | `440-react-core.md` |
| `Docker` | `Dockerfile` | `350-docker-core.md` |
| `Go`, `Golang` | `.go` | `600-golang-core.md` |

Record implied matches as: `"(implied .py from keyword: FastAPI)"`

### Step 3: Record Selections

For each matched rule, record in the loaded rules list with reason:
- `"(file extension: .py)"` for extension matches
- `"(directory: skills/)"` for directory matches
- `"(keyword: streamlit)"` for keyword-domain matches

If no extensions found and no directory matches, skip to Phase 3.

## Rules

- **MANDATORY:** Use only rule names from RULES_INDEX.md. Never invent rule names.
- **FORBIDDEN:** Guessing `300-sql-core.md` when the index says `102-snowflake-sql-core.md`.
- If an extension has no mapping in RULES_INDEX.md, note: "No domain rule for [extension]"
- Multiple extensions can match (e.g., `.py` + `.sql` loads both domain rules)

## Deduplication

If a rule was already selected in an earlier phase, skip it in later phases but retain the original loading reason.

**Example:** `101-snowflake-streamlit-core.md` matched in Phase 2 (keyword: streamlit). If Phase 3 also matches it via keyword search, do not add it again. The Phase 2 reason `"(keyword: streamlit)"` is retained.

**Rule:** First match wins. Later phases do not override the loading reason.
