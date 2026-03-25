# Staleness Rubric

> **STATUS: INFORMATIONAL ONLY - NOT SCORED**
>
> As of Scoring Rubric v2.0, Staleness is **no longer a scored dimension**. Findings appear in recommendations, not in the score.

## What to Look For

When reviewing rules, note these staleness issues for the recommendations section:

| Finding Type | Action |
|--------------|--------|
| LastUpdated >180 days | Flag for review |
| Deprecated tools (see list below) | Note replacement in recommendations |
| Broken external links (404, timeout) | Priority fix |
| Outdated patterns (old Python/Node versions) | Suggest updates |

## Deprecated Tools Reference

**Python (deprecated as of 2025):**

| Deprecated | Replacement |
|------------|-------------|
| flake8 | ruff |
| black | ruff format |
| isort | ruff check --select I |
| pip (project management) | uv |
| mypy (when ty available) | ty |
| setuptools + setup.py | pyproject.toml |
| pipenv / poetry | uv |

**JavaScript/TypeScript:**

| Deprecated | Replacement |
|------------|-------------|
| eslint + prettier | biome |
| webpack | vite / esbuild |
| create-react-app | vite templates |
| yarn v1 | pnpm / npm |

**Shell:**

| Deprecated | Replacement |
|------------|-------------|
| `which` | `command -v` |
| Unquoted variables | `"$var"` |

**Snowflake:**

| Deprecated | Replacement |
|------------|-------------|
| Classic web UI | Snowsight |
| Manual warehouse mgmt | Auto-suspend/resume |

## Documentation Currency Check

For URLs in `## External Documentation` sections:
1. Fetch with `web_fetch(url, extract_text=true)`
2. Scan for deprecation signals: "deprecated", "end of life", "no longer supported", "removed in version"
3. Report findings but do NOT apply score penalty

See `workflows/doc-currency-check.md` for detailed steps.

## How to Report Findings

Include in the **Recommendations** section of the review:

```markdown
**Staleness (Informational):**
- LastUpdated: YYYY-MM-DD (NNN days ago)
- Deprecated tools: N (list with replacements)
- Broken links: N (list with status codes)
- Documentation currency signals: N
```

## Non-Issues (Do NOT Flag)

- **Legacy documentation sections** clearly marked "for migration only"
- **Still-supported versions** (not yet EOL)
- **Redirected links** that resolve to valid content (recommend update, not broken)
- **Functional but superseded tools** (mark as 0.5 severity, not 1.0)

> **Historical Reference:** Full scored rubric archived at `_archive/staleness-v1-scored.md`
