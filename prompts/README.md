# Prompts

This directory contains two kinds of prompts used with the AI Coding Rules framework:

1. **Tutorial example prompts** (`example-*.md`) — illustrative templates that demonstrate how to structure requests so AI agents reliably load the right rules and produce predictable output.
2. **Operational prompts** (everything else) — ready-to-use prompts that drive recurring workflows in this repo (planning, committing, doc maintenance, etc.).

> Skill-specific prompts (rule review rubrics, rule generation templates, etc.) live alongside the skill that owns them under `skills/`. This folder is only for repo-wide tutorial and operational prompts.

---

## Why prompt structure matters

AI agents in this framework load rules dynamically based on signals in your prompt. Effective prompts include:

1. **A clear task description** — what you want accomplished.
2. **File or domain context** — paths, languages, frameworks, or Snowflake objects involved.
3. **Activity keywords** — linting, testing, optimization, deployment, semantic view creation, etc.

The example files below show different shapes of well-formed prompts so you can pick the closest match and adapt it.

---

## Tutorial example prompts

| File | Use case | Pattern strength |
|------|----------|------------------|
| [`example-clear-complete.md`](./example-clear-complete.md) | Fix linting errors with specific error codes and file paths | Maximum specificity — task, files, and exact errors |
| [`example-context-rich.md`](./example-context-rich.md) | Performance optimization with measurable goals and constraints | Adds current behavior, target behavior, and constraints |
| [`example-minimal.md`](./example-minimal.md) | Simple code-quality task (e.g. add type hints) | Minimum viable prompt — task + files |
| [`example-semantic-view.md`](./example-semantic-view.md) | Create a Snowflake semantic view for Cortex Analyst | Snowflake DDL + table/column context |
| [`example-cortex-search.md`](./example-cortex-search.md) | Create a Snowflake Cortex Search Service for document retrieval | Source table + retrieval-tuning context |
| [`example-cortex-agent-hybrid.md`](./example-cortex-agent-hybrid.md) | Create a hybrid Cortex Agent combining structured analytics and document search | References to existing semantic view + search service |
| [`example-cortex-ai-stack.md`](./example-cortex-ai-stack.md) | Build the full Cortex AI stack (semantic view + search + hybrid agent) end-to-end | Largest scope — multi-object, multi-rule trigger |
| [`example-rule-review.md`](./example-rule-review.md) | Review every `rules/*.md` file against the framework's design priorities | Meta-prompt for auditing the rule set itself |

### Picking a pattern

| If your task is… | Start from |
|------------------|------------|
| Fixing linting / formatting | `example-clear-complete.md` |
| Optimizing performance | `example-context-rich.md` |
| A small, well-scoped change | `example-minimal.md` |
| Building a Snowflake semantic view | `example-semantic-view.md` |
| Building a Snowflake Cortex Search service | `example-cortex-search.md` |
| Building a Cortex Agent over existing assets | `example-cortex-agent-hybrid.md` |
| Standing up the full Cortex AI stack | `example-cortex-ai-stack.md` |
| Auditing the rules themselves | `example-rule-review.md` |

---

## Operational prompts

These are not tutorials — they are the prompts to run for recurring workflows in this repo.

| File | Purpose |
|------|---------|
| [`analyze-plan.md`](./analyze-plan.md) | Produce a `MODE: PLAN` task list before any code changes |
| [`execute-plan.md`](./execute-plan.md) | Execute an approved plan in `MODE: ACT` |
| [`commit-changes.md`](./commit-changes.md) | Stage, group, and commit work with conventional commit messages |
| [`update-changelog.md`](./update-changelog.md) | Update `CHANGELOG.md` based on recent commits |
| [`update-project-docs.md`](./update-project-docs.md) | Refresh project documentation (README, AGENTS, rule indexes) when state has drifted |

---

## Keywords that influence rule loading

The `rule-loader` skill matches keywords in your prompt against `rules/*.md (via Keywords metadata)`. Including specific terms from this table makes the right rules load deterministically.

| Keyword(s) in prompt | Likely loads |
|----------------------|--------------|
| `lint`, `format`, `Ruff`, `code quality` | Linting/formatting rules (e.g. `201-python-lint-format`) |
| `test`, `pytest`, `coverage` | Testing rules (e.g. `206-python-pytest`) |
| `optimize`, `performance`, `slow` | Performance rules (e.g. `103-snowflake-performance-tuning`) |
| `security`, `auth`, `validate input` | Security rules (e.g. `101c-snowflake-streamlit-security`) |
| `deploy`, `Docker`, `CI/CD` | Deployment rules (e.g. `400-docker-best-practices`) |
| `Streamlit`, `dashboard`, `st.` | Streamlit rules (e.g. `101-snowflake-streamlit-core`) |
| `FastAPI`, `REST API`, `endpoint` | FastAPI rules (e.g. `210-python-fastapi-core`) |
| `pandas`, `DataFrame` | Pandas rules (e.g. `252-pandas-best-practices`) |
| `SQL`, `query`, `Snowflake` | Snowflake core (e.g. `100-snowflake-core`) |
| `semantic view`, `Cortex Analyst` | Semantic view rules (e.g. `106-snowflake-semantic-views-core`) |
| `Cortex Agent`, `agent tools` | Cortex Agent rules (e.g. `115-snowflake-cortex-agents-core`) |
| `Cortex Search`, `RAG`, `search service` | Cortex Search rules (e.g. `116-snowflake-cortex-search`) |
| `type hints`, `typing`, `annotations` | Python typing rules |

If a needed rule isn't loaded, name it explicitly: *"Also load `rules/201-python-lint-format.md`."*

---

## Tips for better results

**Be specific about file types.**
- Good: `Fix linting in scripts/rule_validator.py`
- Vague: `Fix the validation script`

**Use activity keywords.**
- Good: `Optimize query performance in the Streamlit dashboard`
- Vague: `Make the app faster`

**Mention frameworks and libraries.**
- Good: `Add pytest fixtures for FastAPI endpoint testing`
- Vague: `Add tests`

**Quote error messages verbatim when you have them.**
- Good: `Fix F841: Local variable 'table_end_idx' is assigned but never used`
- Vague: `Fix the linting error`

**Force a mode when you need to.** Add `MODE: PLAN` or `MODE: ACT` explicitly to override drift. Most agents respect the workflow defined in `AGENTS.md` and `rules/000-global-core.md`, but some will silently stay in `ACT` when they should be planning.

**Watch the bootstrap output.** If the `**Rules Loaded**` block doesn't show the rules you expect, stop the agent and tell it to reload. As context fills up, parts of `AGENTS.md` can be evicted during compaction — naming rules explicitly hardens the run.

---

## Expected response shape

When a prompt from this folder is used, the agent's response should begin with the bootstrap and rules manifest defined in `rules/000-global-core.md`, e.g.:

```
**Bootstrap:** rule Keywords metadata scanned (python, lint) — 3 rules loaded, 0 failed.

**Rules Loaded**
- rules/000-global-core.md (foundation) — N lines
- rules/200-python-core.md (python file type) — N lines
- rules/201-python-lint-format.md (activity: linting) — N lines

Task Switch: FIRST

Task List:
1. ...
2. ...
```

See `rules/000-global-core.md` for the authoritative Rule Loading Contract and citation format.

---

## Contributing a new example

1. Add `prompts/example-<short-descriptive-name>.md` (kebab-case, `example-` prefix).
2. Use the structure: H1 title → `## The Prompt` (fenced block) → optional `## Why this works` / `## Triggers`.
3. Update this README's tutorial table and the "Picking a pattern" table.
4. Make sure the example demonstrates a use case not already covered.
