# Phase 5: Keyword Generation Workflow

## Purpose

After creating and validating a rule, verify its keyword metadata and discovery behavior. The matcher reads YAML frontmatter directly; no separate index file is needed. Model-assisted generation is optional.

## Inputs

- Validated rule file path (e.g., `rules/422-daisyui-core.md`)

## Outputs

- Reviewed `keywords:` field in rule frontmatter and discovery-check results

## Steps

### Step 5.1: Generate Keywords

Keep meaningful manually authored keywords unless model-assisted generation is useful. Before using the command below, obtain authorization for the model, cost limit, and transmission of the rule content. Replace the path with the actual authorized rule:

```bash
uv run ai-rules rule-loader keywords run rules/<NNN-technology-aspect>.md --update
```

This calls Cortex AI to analyze the rule content and generate 5-7 semantic (`kw:`) discovery keywords.

### Step 5.2: Verify Keywords

Read the complete frontmatter and inspect the diff if generation changed it. Preserve required dependencies and unrelated edits.

Verify the `keywords:` section contains 5-7 semantic (`kw:`) terms (structural `ext:`/`file:`/`dir:` triggers add to the combined 5-11 total).

### Step 5.3: Test Discovery

Verify the matcher can find the new rule:

```bash
python3 skills/rule-loader/scripts/match_rules.py --keywords "daisyui" --rules-dir rules
```

This direct matcher command is a test, not normal runtime discovery. Use the actual new rule's task terms and verify it appears in `load_sequence`. Also test a representative task with competing terms and an irrelevant request; an exact keyword self-match alone is insufficient.

Revalidate metadata and integrated discovery after any keyword edit:

```bash
uv run ai-rules validate rules/<NNN-technology-aspect>.md
uv run ai-rules rule-loader validate
uv run ai-rules rule-loader validate-trigger-contract
task plugin:verify
```

### Step 5.4: Check for Collisions

Optionally verify no keyword over-collision:

```bash
uv run ai-rules rule-loader keywords collisions --max-collision 3
```

If the new rule's keywords appear in the `violations` list, consider more specific compound phrases.

## Completion Checklist

- [ ] Manually authored or authorized generated keywords reviewed in frontmatter
- [ ] Rule discoverable via `python3 skills/rule-loader/scripts/match_rules.py --keywords "<technology>" --rules-dir rules`
- [ ] No excessive keyword collisions (optional)
- [ ] Post-edit schema, loader, trigger-contract, and plugin checks pass
