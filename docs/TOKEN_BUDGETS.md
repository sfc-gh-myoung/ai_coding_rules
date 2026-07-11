# Token Budgets

**Last Updated:** 2026-05-14

## Purpose

Validate and update the `TokenBudget` field in rule front-matter so each
rule's declared budget reflects its actual token count.

## Tool

`ai-rules tokens` (Typer CLI). Token counts use `tiktoken` with the
GPT-4o encoding (`o200k_base`).

```bash
# Validate a single rule
ai-rules tokens rules/100-snowflake-core.md

# Dry run with per-file detail
ai-rules tokens rules/ --dry-run --detailed

# Apply updates across all rules
ai-rules tokens rules/

# Custom threshold (percent)
ai-rules tokens rules/ --threshold 20
```

The same command can be invoked with verbose / dry-run flags:

```bash
uv run ai-rules tokens rules/ --dry-run --detailed   # dry run + detailed
uv run ai-rules tokens rules/                        # apply updates
uv run ai-rules tokens rules/100-snowflake-core.md   # single file
```

## How it works

1. Reads each rule file under the supplied path.
2. Counts tokens with `tiktoken` (`o200k_base`).
3. Compares the count to the declared `TokenBudget` in the front-matter.
4. When the difference exceeds the threshold (default 5%), updates
   `TokenBudget` to the rounded count and bumps `LastUpdated`.

## Options

| Flag | Purpose |
|---|---|
| `PATH` (positional) | File or directory to scan. |
| `--threshold N` | Update threshold percentage (default 5.0). |
| `--dry-run` | Preview without writing. |
| `--detailed` | Per-file analysis output. |
| `--verbose` | Verbose logging. |

## Exit codes

- `0` success.
- `1` errors during analysis.

## Notes

- Always run with `--dry-run` first to preview changes.
- Updates are safe and reversible via git.
- Rule files keep their structure; only the `TokenBudget` and
  `LastUpdated` lines change.

## Related

- `ai-rules validate` checks rule schema compliance.
- `ai-rules index generate` regenerates the human-only `rules/RULES_INDEX.md`.
- `ai-rules deploy` copies rules into a target project.
