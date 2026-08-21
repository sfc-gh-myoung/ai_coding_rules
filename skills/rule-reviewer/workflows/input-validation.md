# Workflow: Input Validation

## Inputs (required)

- `target_file`: must end in `.md`
- `review_date`: must match `YYYY-MM-DD`
- `review_mode`: must be one of `FULL`, `FOCUSED`, `STALENESS`
- `model`: slug preferred (example: `claude-sonnet45`) or raw model name

## Inputs (optional)

- `output_root`: root directory for output files (default: `reviews/`)
  - Trailing slash auto-normalized (both `reviews` and `reviews/` accepted)
  - Supports relative paths including `../`
  - Subdirectory `rule-reviews/` appended automatically

## Steps

1. Verify `target_file` ends with `.md`.
2. Verify `review_date` matches `YYYY-MM-DD` exactly.
3. Verify `review_mode` is one of `FULL`, `FOCUSED`, `STALENESS`.
4. Verify `target_file` exists and is readable.
5. Normalize `output_root`:
   - Add trailing `/` if missing
   - Auto-create `{output_root}/rule-reviews/` directory if it doesn't exist

## Output

- Validated inputs ready for downstream workflows
- `output_root`: normalized path with trailing slash (e.g., `reviews/` or `../mytest/`)

## Supported File Types

**Rule Files (`rules/*.md`):**
- Domain-specific patterns and guidelines loaded on-demand by agents
- Full schema validation against `schemas/rule-schema.yml`
- All 6 dimensions scored (100 points max)
- TokenBudget variance check applies

**Project Files (`PROJECT.md`):**
- Bootstrap and configuration documents loaded once during project initialization
- Schema validation skipped (different structure than rules)
- All 6 dimensions scored (100 points max)
- TokenBudget variance skipped (no declared budget)
- Evaluated for actionability, completeness, consistency, markdown quality, and currency

**Key Differences:**

| Aspect | Rule Files | Project Files |
|--------|------------|---------------|
| Schema validation | Full check | Skipped |
| Parsability scoring | Schema + markdown | Markdown only |
| Token efficiency | Budget variance + redundancy | Redundancy + structure only |
| Metadata required | 7 fields (SchemaVersion, etc.) | None |
| Section structure | Scope → Contract → Content | Custom per project |
| Max score | 100 points | 100 points |

Both file types are agent-executable documents; they follow different schemas optimized for their architectural roles.

## File-Type Detection

After input validation, determine whether `target_file` is a rule file or a project file. This controls whether schema validation is run.

```bash
target_basename=$(basename "$target_file")

if [[ "$target_basename" =~ ^PROJECT\.md$ ]]; then
    FILE_TYPE="project"
    SKIP_SCHEMA=true
    echo "File type: Project configuration (schema validation skipped)"
elif [[ "$target_file" == rules/*.md ]]; then
    FILE_TYPE="rule"
    SKIP_SCHEMA=false
    echo "File type: Rule (full schema validation)"
else
    echo "ERROR: Target must be PROJECT.md or rules/*.md"
    exit 1
fi
```

**Rationale:** `PROJECT.md` is a project configuration file with different structure than domain rules. It does not use rule metadata (`SchemaVersion`, `RuleVersion`, `TokenBudget`) or rule sections (`Scope`, `Contract`, `References`).

**Outputs set:**
- `FILE_TYPE`: one of `rule`, `project`
- `SKIP_SCHEMA`: boolean, consumed by `schema-validation.md`
