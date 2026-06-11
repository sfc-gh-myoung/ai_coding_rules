# Evaluating the Rule Loader

This document is the full reference for the Rule Loading Evaluator. It covers
the trigger-evidence invariant, fixture schema, all `ai-rules rule-loader`
subcommands, the pre-commit hook, CI behavior, and batch refresh/compare
workflows.

Related: [`fixtures/rule_loader_eval/AUTHORING_GUIDE.md`](../fixtures/rule_loader_eval/AUTHORING_GUIDE.md)

---

## Purpose

The Rule Loading Evaluator is a two-layer sanity check that the Cortex Code
Agent SDK, given `AGENTS.md` + a fixture prompt, loads exactly the rules each
fixture declares:

| Layer | Command | Requires live SDK? | Runs in CI? |
|---|---|---|---|
| Trigger-evidence invariant | `rule-loader validate` | No | Yes |
| Behavioral (live agent) | `rule-loader eval` | Yes | **No — manual only** |

> **`rule-loader eval` is an explicit, opt-in command.** It never runs
> automatically — not in CI, not in pre-commit, not in `dev test run`, and not
> in the default pytest suite. The `live` pytest marker is deselected by
> default (`addopts = ["-m", "not live"]` in `pyproject.toml`). To run the live
> behavioral evaluation, invoke it directly:
>
> ```bash
> uv run ai-rules rule-loader eval
> ```

**Trigger-evidence invariant** (`validate`): a deterministic, millisecond-fast
check that every fixture's `prompt` contains a literal token that would fire
each required rule's `ext:` / `file:` / `dir:` trigger. No SDK, no LLM.

**Behavioral eval** (`eval`): sends each fixture prompt to a live Cortex Code
Agent session and verifies that the agent's loaded-rule set matches the fixture
declaration. Accounts for LLM variance by running multiple passes and
aggregating with a flake score.

---

## The Trigger-Evidence Invariant

Every fixture's `expected.required` list contains rules whose `**Keywords:**`
metadata declares typed triggers (`kw:`, `ext:`, `file:`, `dir:`). The
invariant checks that the fixture `prompt` contains a literal substring that
would cause each required rule to fire:

| Trigger type | Fixture prompt must contain |
|---|---|
| `ext:.py` | A filename ending in `.py` (e.g. `analytics/etl_pipeline.py`) |
| `ext:.sql` | A filename ending in `.sql` (e.g. `queries.sql`) |
| `file:snowflake.yml` | The literal string `snowflake.yml` |
| `dir:skills/` | The literal string `skills/` |
| `kw:logging` | The literal string `logging` |

A fixture that declares `ext:.py` in a required rule but has no `.py` filename
in the prompt is rejected at fixture-load time (exit 4).

Run the invariant with:

```bash
uv run ai-rules rule-loader validate
```

This reports every failing fixture in a single pass (not bail-on-first-error).
Use `--fixture <id>` to check a single fixture, `--debug` / `-v` for full
tracebacks.

---

## Required, Dependencies, Optional, Forbidden

Each fixture `expected` block has four lists:

| List | Semantics | Eval behavior |
|---|---|---|
| `required` | Rules the prompt directly targets. Trigger-evidence invariant is enforced here. | Missing = failure |
| `dependencies` | Rules that should load because a `required` rule declares `Depends:` for them. The agent reads + cites them as part of its bootstrap. | Missing = failure (reported separately from `required` gaps) |
| `optional` | Rules that may load; if read but not cited, the harness treats it as benign. Use for plausibly-related rules some agents explore. | Neither missing nor extra triggers a failure |
| `forbidden` | Rules that must not appear in the loaded set. | Present = failure |

The evaluator checks the agent's loaded set against `required ∪ dependencies`
and reports gaps under separate buckets so you can distinguish "prompt didn't
fire the rule" (required gap) from "rule didn't propagate its dependency" (deps
gap).

The evaluator does **not** parse rule-file `Depends:` metadata directly; rules
own that information. The agent loads and reports dependencies in its
`**Bootstrap:**` line and `**Rules Loaded**` section per the Rule Loading
Contract (R1–R8 in `rules/000-global-core.md`).

---

## Fixture YAML Schema (v3)

```yaml
schema_version: 3
updated: 2026-05-17T16:26:51-04:00
id: <kebab-case-id>
description: <one-line description>
variant: simple | complex
prompt: |
  <Realistic natural-language user prompt. Use hyphens only for literal
  identifiers the user would type verbatim (e.g. `auto-suspend`, `hx-get`).>
expected:
  required:
    - rules/000-global-core.md   # foundation — REQUIRED in every fixture
    - rules/<rule>.md            # MUST appear in agent's loaded set
  dependencies: []               # rules that load via Depends: propagation
  forbidden: []                  # rules that MUST NOT load
  optional:
    - rules/<related>.md         # MAY load; harness tolerates over-read
trigger_evidence:
  kw: [<keyword phrase>, ...]    # literal substrings that fire kw: rules
  ext: [.sql]                    # file-extension triggers present in prompt
  file: [snowflake.yml]          # filename triggers present in prompt
  dir: [skills/]                 # directory triggers present in prompt
```

**`variant`**: `simple` = shallow-context prompt (one file, one task); `complex`
= multi-file, cross-concern prompt. The evaluator uses `--effort` and
`--max-turns` defaults tuned per variant.

**`trigger_evidence.kw`**: inline `# suggested:` comments from `create` /
`suggest-kw` show which n-gram matched which rule. Hand-edit freely; the
validator only checks that each listed kw token is a substring of the prompt.

Fixtures live in `fixtures/rule_loader_eval/`. Browse with:

```bash
uv run ai-rules rule-loader list
uv run ai-rules rule-loader list --variant simple
```

---

## Subcommand Reference

All subcommands are under `ai-rules rule-loader`. Run
`uv run ai-rules rule-loader --help` for the top-level list.

### `validate` — trigger-evidence invariant (no SDK)

```
uv run ai-rules rule-loader validate [OPTIONS]

Options:
  --fixture TEXT        Validate only this fixture id.
  --debug / -v          Print full Python traceback for each failure.
  --progress / -P TEXT  auto|screen|rich|plain|json|none  [default: auto]
  --no-progress         Alias for --progress=none.
```

Reports every failing fixture in one pass. Exit 0 = all pass; non-zero =
failures. This is the only rule-loader command that runs in CI.

### `list` — enumerate fixtures

```
uv run ai-rules rule-loader list [OPTIONS]

Options:
  --variant TEXT   Filter by simple|complex.
```

Prints fixture id, variant, required rules, and dependency rules.

### `doctor` — environment health check

```
uv run ai-rules rule-loader doctor [OPTIONS]

Options:
  --with-smoke         Run a trivial agent call to verify model reachability (~3-5s).
  --connection TEXT    Snowflake connection name (overrides SNOWFLAKE_CONNECTION_NAME).
```

Verifies SDK pin, Snowflake connection, and fixture parse. Run before `eval`
if you suspect infrastructure issues. Add `--with-smoke` to confirm the model
endpoint is reachable.

### `eval` — live behavioral evaluation

```
uv run ai-rules rule-loader eval [OPTIONS]

Options:
  --fixture TEXT        Run only this fixture id.
  --runs INTEGER        Number of eval passes (default 3; accounts for LLM variance).
  --effort TEXT         low|medium|high  [default: medium]
  --model TEXT          Model override  [default: auto]
  --connection TEXT     Snowflake connection name.
  --out-dir PATH        Base directory for snapshots. Auto-generates out/eval-run-N.
  --label TEXT          Label stored in meta.json.
  --strict-forbidden    Treat forbidden hits as failures.
  --max-turns INTEGER   [default: 25]
  --debug               Developer diagnostics (timing, signal disagreements) to stderr.
  --progress / -P TEXT  auto|screen|rich|plain|json|none  [default: auto]
  --no-progress         Alias for --progress=none.
```

Three checks are unconditional per fixture:

1. `required + dependencies` must all appear in the agent's loaded set.
2. 2-signal agreement: tool reads vs `**Rules Loaded**` section must match
   (legacy `## Reads Performed` checked when present).
3. Citation drift: declared line counts vs actual rule line counts must be zero.

Any of the three failing fails the fixture. There are no escape flags — rule
loading correctness is non-negotiable.

**Fast iteration profile** (single fixture, single run, low effort):

```bash
uv run ai-rules rule-loader eval \
    --fixture simple-python-task \
    --effort low \
    --runs 1 \
    --debug
```

Expect higher variance at `--runs 1`; use `--runs 3` (default) for definitive
results.

### `create` — author a new fixture from a prompt

```
uv run ai-rules rule-loader create [OPTIONS]

Options:
  --prompt TEXT         Literal prompt text.
  --prompt-file PATH    Read prompt from a plain-text file.
  --id TEXT             Fixture id (kebab-case).
  --variant TEXT        simple|complex  [default: simple]
  --write PATH          Write the skeleton to this path.
  --effort TEXT         [default: medium]
  --max-turns INTEGER   [default: 25]
  --model TEXT          [default: auto]
  --connection TEXT
  --debug
```

Drives the live agent against a candidate prompt and prints a YAML skeleton
with mechanical `# suggested:` comments derived from the rule metadata snapshot.
Use `--write` to save directly:

```bash
uv run ai-rules rule-loader create \
    --prompt 'Update analytics/etl_pipeline.py to add structured logging.' \
    --id simple-logging-task \
    --variant simple \
    --write fixtures/rule_loader_eval/simple-logging-task.yaml
```

After capture, run `validate --fixture <id>` to confirm trigger evidence, then
hand-edit the skeleton to finalize `required` / `optional` / `forbidden` lists.

### `refresh` — re-run and diff a single fixture

```
uv run ai-rules rule-loader refresh [OPTIONS] FIXTURE_PATH

Arguments:
  fixture_path PATH   Path to an existing fixture YAML.  [required]

Options:
  --write             Replace the on-disk fixture with the regenerated skeleton.
  --effort TEXT       [default: medium]
  --max-turns INTEGER [default: 25]
  --model TEXT        [default: auto]
  --connection TEXT
  --debug
  --progress / -P TEXT  auto|screen|rich|plain|json|none  [default: auto]
  --no-progress
```

Default (read-only): regenerates the skeleton and prints a unified diff against
the on-disk YAML. Exit 0 = no drift; 2 = drift detected; 4 = unparseable.

With `--write`: replaces the on-disk file. Note: `--write` re-generates from
the suggestion engine, which sorts rules and emits canonical inline `# suggested:`
comments. Hand-edited comments and custom ordering are lost.

```bash
# Check for drift (read-only):
uv run ai-rules rule-loader refresh \
    fixtures/rule_loader_eval/simple-python-task.yaml

# Accept changes:
uv run ai-rules rule-loader refresh \
    fixtures/rule_loader_eval/simple-python-task.yaml --write
```

### `refresh-all` — batch capture or refresh

```
uv run ai-rules rule-loader refresh-all [OPTIONS]

Options:
  --glob TEXT           Glob pattern (relative to repo root) selecting fixture YAMLs.
  --all                 Process every fixture under fixtures/rule_loader_eval/.
  --concurrency INTEGER Max in-flight SDK sessions.  [default: 2]
  --out-dir PATH        Write per-fixture YAML + summary.json here. Omit to stream to stdout.
  --effort TEXT         [default: medium]
  --max-turns INTEGER   [default: 25]
  --model TEXT          [default: auto]
  --connection TEXT
  --debug
  --progress / -P TEXT  auto|screen|rich|plain|json|none  [default: auto]
  --no-progress
```

Runs all matched fixtures concurrently and writes regenerated skeletons to
`--out-dir`. Use for bulk initial capture or bulk refresh before a compare:

```bash
# Refresh all fixtures, write to out/seeds/:
uv run ai-rules rule-loader refresh-all --all \
    --concurrency 4 \
    --out-dir out/seeds/

# Lower concurrency if you hit rate limits:
uv run ai-rules rule-loader refresh-all --all --concurrency 1

# Exhaustive fallback for difficult fixtures:
uv run ai-rules rule-loader refresh-all --all \
    --max-turns 50 --effort high \
    --out-dir out/seeds-high/
```

Exit codes: 0 = all succeeded; 1 = at least one failed; 3 = SDK/connection
error; 4 = invalid arguments.

### `merge-snapshots` — build a noise-resistant baseline

```
uv run ai-rules rule-loader merge-snapshots [OPTIONS] SNAPSHOT_DIRS...

Arguments:
  snapshot_dirs   Two or more snapshot directories from 'eval --out-dir'.  [required]

Options:
  --out-dir / -o PATH  Write merged snapshot here.  [required]
  --label TEXT         Label embedded in meta.json.  [default: merged]
```

Merges N snapshot directories into one baseline. Aggregation policy:

- **Pass status**: strict majority (passes when it passed in more than half of
  the input runs that contained it).
- **Loaded set**: strict majority (a rule appears in merged loaded when it
  appeared in more than half of input runs).
- **Numeric metrics** (turns, duration_ms, etc.): median across runs.

Use this to build a stable baseline before a `compare`:

```bash
for i in 1 2 3; do
  uv run ai-rules rule-loader eval \
      --out-dir out/baseline-$i \
      --label baseline-run-$i
done

uv run ai-rules rule-loader merge-snapshots \
    out/baseline-1 out/baseline-2 out/baseline-3 \
    -o out/baseline-merged --label baseline-merged
```

### `compare` — diff two snapshots

```
uv run ai-rules rule-loader compare [OPTIONS] BASELINE_DIR POST_DIR

Arguments:
  baseline_dir PATH   Snapshot directory for the baseline state.  [required]
  post_dir PATH       Snapshot directory for the post-change state.  [required]

Options:
  --format TEXT                   table (default) | json | markdown
  --alias-map PATH                JSON {old_rule_path: new_rule_path} to neutralize renames.
  --exit-on-regression            Upgrade advisory drift (exit 2) to regression (exit 1).
  --verbose                       Show full per-fixture blocks for load-drift-only fixtures.
  --ignore-flaky / --no-ignore-flaky   Exclude high flake_score fixtures from REGRESSIONS.  [default: ignore-flaky]
  --flake-threshold FLOAT         Jaccard-distance threshold for flaky classification.  [default: 0.5]
```

Exit codes: 0 = identical; 2 = drift (loaded sets shifted, no regressions) —
advisory; 1 = regression (pass → fail) — block landing.

```bash
# Compare baseline to a post-change snapshot:
uv run ai-rules rule-loader compare \
    out/baseline-merged out/post-change

# Treat any drift as a hard failure:
uv run ai-rules rule-loader compare \
    out/baseline-merged out/post-change \
    --exit-on-regression
```

### `suggest-kw` — propose kw: fixes for failing fixtures

```
uv run ai-rules rule-loader suggest-kw [OPTIONS] [FIXTURE_ID]

Arguments:
  fixture_id   Fixture id to analyse. Omit to analyse all failing fixtures in --from-snapshot.

Options:
  --from-snapshot PATH   Snapshot directory from 'rule-loader eval --out-dir'.
  --rule TEXT            Restrict suggestions to a single rule path.
  --top-k INTEGER        Number of candidate kw: terms to show per rule.  [default: 5]
```

Mines the fixture prompt for IDF-scored n-gram candidates and shows exactly
which `kw:` to add (missing-required) or narrow (spurious):

```bash
# Analyse a single fixture:
uv run ai-rules rule-loader suggest-kw simple-python-task

# Analyse all fixtures failing in a snapshot:
uv run ai-rules rule-loader suggest-kw \
    --from-snapshot out/post-change
```

---

## Pre-commit Hook

The `rule-loader-eval` local hook runs five representative fixtures through the
live Cortex Code Agent SDK before each commit, catching regressions before they
land.

### Adding the hook

Add to `.pre-commit-config.yaml` under the `local` repo entry:

```yaml
- repo: local
  hooks:
    - id: rule-loader-eval
      name: Rule loader live eval (5 representative fixtures)
      entry: uv run ai-rules rule-loader eval
      args:
        - --fixture=simple-python-task
        - --fixture=simple-sql-edit
        - --fixture=complex-python-etl
        - --fixture=complex-snowcli-deploy
        - --fixture=complex-skill-author
        - --runs=1
        - --effort=low
        - --no-progress
      language: system
      pass_filenames: false
      stages: [pre-commit]
```

### Bypassing the hook

Commits that lack Snowflake credentials (e.g. offline work, CI, dependency
bumps) should bypass the hook explicitly:

```bash
SKIP=rule-loader-eval git commit -m "your message"
```

Do **not** disable the hook permanently. The live eval is the primary guard
against rule-loading regressions that the deterministic `validate` cannot catch.

### When to run full eval instead

If you changed `AGENTS.md`, `rules/000-global-core.md`, `skills/rule-loader/`,
or a rule's `**Keywords:**` metadata, run the full eval suite (all fixtures,
3 runs) rather than relying on the pre-commit 5-fixture subset:

```bash
uv run ai-rules rule-loader eval --runs 3
```

---

## CI Behavior

CI runs only the trigger-evidence invariant — no live SDK, no credentials
required:

```bash
# .github/workflows/ci.yml
uv run ai-rules rule-loader validate
```

This is also called from `uv run ai-rules dev validate` as part of the
full validation suite. The live `eval` command is explicitly excluded from CI
because it requires a Snowflake connection and accounts for LLM variance only
meaningful over multiple local runs.

---

## Batch Refresh / Compare Workflow

Standard workflow for verifying rule loading before and after a change:

```bash
# 1. Capture a stable baseline (3 runs, then merge):
for i in 1 2 3; do
  uv run ai-rules rule-loader eval \
      --out-dir out/baseline-$i \
      --label baseline-run-$i
done
uv run ai-rules rule-loader merge-snapshots \
    out/baseline-1 out/baseline-2 out/baseline-3 \
    -o out/baseline-merged

# 2. Make your change (edit rules, AGENTS.md, keywords, etc.)

# 3. Capture a post-change snapshot (single run or merged):
uv run ai-rules rule-loader eval \
    --out-dir out/post-change \
    --label post-change

# 4. Compare:
uv run ai-rules rule-loader compare \
    out/baseline-merged out/post-change
```

Exit 0 = no change. Exit 2 = advisory drift (review loaded-set shifts, decide
if intentional). Exit 1 = regression (at least one fixture went pass → fail;
block landing).

For cosmetic rule renames that appear as spurious drift, supply an alias map:

```bash
uv run ai-rules rule-loader compare \
    out/baseline-merged out/post-change \
    --alias-map alias-map.json
```

Where `alias-map.json` maps `{"old/path.md": "new/path.md"}`.

---

## Authoring Checklist

When adding or editing a fixture:

1. Run `uv run ai-rules rule-loader validate --fixture <id>` — must exit 0.
2. Run `uv run ai-rules rule-loader eval --fixture <id> --runs 1 --effort low` — review output.
3. For production-grade acceptance, run `--runs 3` and check `flake_score`.
4. Run `uv run ai-rules rule-loader validate` (all fixtures) before committing.

See [`fixtures/rule_loader_eval/AUTHORING_GUIDE.md`](../fixtures/rule_loader_eval/AUTHORING_GUIDE.md)
for prompt-writing guidance, pass/fail semantics, and common pitfalls.
