# Rule Loader Eval Fixture Coverage

**Schema version:** 3 (v3.15.0). The `dependencies:` block was removed in v3.15;
fixtures now use `required:`, `optional:`, `forbidden:` only. See
[AUTHORING_GUIDE.md](AUTHORING_GUIDE.md) for fixture authoring.

This file tracks the trigger-kind coverage matrix for fixtures under this
directory. Every fixture passes the trigger-evidence invariant via
`ai-rules rule-loader validate` (run on every CI build and as a
pre-commit hook). The invariant guarantees that every `ext:`/`file:`/`dir:`
trigger declared by a required rule is satisfied by a literal token in the
fixture's `prompt` — so fixtures like the previously broken
`python-file-edit` (which declared `ext:.py` but had no `.py` token in
the prompt) are rejected at fixture-load time.

## Coverage matrix

Target: ≥3 simple AND ≥3 complex fixtures per kind (`kw`, `ext`, `file`,
`dir`). Compound fixtures count toward each kind they exercise.

| Kind | Simple count | Complex count |
|------|--------------|---------------|
| `kw`   | 11 | 12 |
| `ext`  | 3  | 4 |
| `file` | 3  | 3 |
| `dir`  | 3  | 3 |

## Fixtures

### Simple (16)

| ID | Kinds |
|----|-------|
| `simple-sql-edit` | kw, ext |
| `simple-python-task` | ext |
| `simple-sql-procedure` | kw, ext |
| `simple-streamlit-dashboard` | kw |
| `simple-cost-governance` | kw |
| `simple-warehouse` | kw |
| `simple-streams-tasks` | kw |
| `simple-snowcli-file` | file |
| `simple-snowcli-deploy-file` | file |
| `simple-snowcli-app-file` | file |
| `simple-skill-dir` | kw, dir |
| `simple-skill-add-dir` | kw, dir |
| `simple-rules-dir` | dir |
| `simple-cortex-search` | kw |
| `simple-mcp-server` | kw |
| `simple-cortex-agent-build` | kw |

### Complex (14)

| ID | Kinds |
|----|-------|
| `complex-sql-pipeline` | kw, ext |
| `complex-python-etl` | kw, ext |
| `complex-mixed-sql-py` | kw, ext |
| `complex-streamlit-deploy` | kw, ext |
| `complex-cost-investigation` | kw |
| `complex-cortex-search-build` | kw |
| `complex-spcs-app` | kw |
| `complex-snowcli-deploy` | kw, file |
| `complex-snowcli-config` | file |
| `complex-snowcli-app-spec` | kw, file |
| `complex-skill-author` | kw, dir |
| `complex-rule-governance` | dir |
| `complex-skill-pipeline-dir` | kw, dir |
| `complex-cortex-agent-design` | kw |

## Authoring rules

When adding a fixture:

1. The `prompt` MUST contain a literal token for every `ext`/`file`/`dir`
   trigger declared by a required rule. Examples:
   - `ext:.py` → prompt contains `analytics/etl_pipeline.py` (or any
     `*.py` filename).
   - `ext:.sh` → prompt contains `scripts/deploy.sh`.
   - `file:snowflake.yml` → prompt contains `snowflake.yml`.
   - `dir:skills/` → prompt contains `skills/`.
2. `trigger_evidence` MUST declare each literal token. The validator
   cross-checks against the rule's metadata; missing declarations are an
   error even if the prompt happens to contain the token.
3. Run `uv run ai-rules rule-loader validate` to confirm before committing.
4. Update the matrix above so the kind counts stay accurate.
