# Fixture Authoring Guide (v3.15.0)

This guide describes how to author fixtures for the rule-loader eval. The
fixtures test whether realistic user prompts cause the agent to load the
correct rules.

## Schema (v3)

```yaml
schema_version: 3
updated: 2026-05-19T08:00:00-04:00
id: <kebab-case-id>
description: <one-line description>
variant: simple | complex
prompt: |
  <Realistic user prompt. Use natural language. Avoid hyphens
  for descriptive concepts; use them only for literal identifiers
  the user would type verbatim (e.g. `auto-suspend`, `hx-get`).>
expected:
  required:
    - rules/000-global-core.md   # foundation (REQUIRED in every fixture)
    - rules/<rule>.md            # MUST load
  forbidden: []                  # rules that MUST NOT load
  optional:
    - rules/<related>.md         # MAY load; harness tolerates over-read on these
trigger_evidence:
  kw: [<keyword phrase>, ...]    # at least one kw token from each required rule must be a substring of the prompt
  ext: [.sql]                    # any extension that should fire ext-matching
  file: [snowflake.yml]          # filename triggers
  dir: [skills/]                 # directory triggers
```

## Pass / Fail Semantics (v3.15.0)

A fixture **passes** when:

1. `rules/000-global-core.md` is loaded (the foundation is injected on every request, and every fixture must declare it as required).
2. Every rule in `required:` appears in the agent's loaded set.
3. No rule in `forbidden:` appears in the loaded set.
4. No `cited_without_read` (R1 fabrication: rule cited but no `read_file`).
5. No `read_without_cite_unexpected` (rule read but neither cited nor in `optional:`).

A fixture **does not fail** for:

- Extra rules loaded that aren't in any list (warned as `extras`).
- `read_without_cite_tolerated`: rule read for triage and listed in `optional:`. Benign.
- Citation drift on `RuleVersion`/`LastUpdated` (those fields were dropped from citation format in v3.14.0).

## When to use each list

| List | Use when |
|---|---|
| `required:` | Rule MUST load; missing it = failure. The fixture's main test target. |
| `optional:` | Rule MAY load; if read but not cited, benign. Use for plausibly-related rules that some agents will explore. |
| `forbidden:` | Rule MUST NOT load. Use sparingly for cases where over-loading is the bug being tested. |

## Authoring Checklist

1. **Prompt is realistic and natural-language.** Imagine a real user typing this.
2. **Hyphens only for literal identifiers.** `cortex search` not `cortex-search` (unless the rule's keywords specifically use the hyphenated form for product naming).
3. **Every `required:` rule has at least one `kw:`/`ext:`/`file:`/`dir:` evidence in the prompt.** The validator enforces this via substring matching. Run `uv run ai-rules rule-loader validate --fixture <id>` to check.
4. **`optional:` includes plausibly-related rules.** This is the harness convenience that prevents over-read failures. Be generous here; spurious extras don't fail.
5. **`forbidden:` is opt-in.** Most fixtures should leave it `[]`.

## Common Pitfalls

- **Required rule has no kw evidence in prompt:** Validator rejects at load time. Either rephrase the prompt or demote the rule to `optional:`.
- **Rule's keywords have hyphenated forms but prompt uses spaces:** The matcher uses substring match; `kw:cortex-search` won't match `cortex search`. Add both forms to the rule keywords if both phrasings are common, OR keep only the space-form everywhere (preferred).
- **Multiple-word kw entries don't match because the prompt has them in different positions:** The matcher requires all tokens (split on whitespace) to appear, but as a phrase the substring check is stricter — the literal phrase must be a contiguous substring. Test with `validate`.

## Tools

- `uv run ai-rules rule-loader validate` — deterministic kw-matcher test (no LLM); run on every fixture/rule edit.
- `uv run ai-rules rule-loader eval` — LLM behavioral test; run × 3 (or 5) for flake_score.
- `uv run ai-rules rule-loader compare <baseline> <new>` — diff two snapshots; gating threshold = flake_score < 0.5.