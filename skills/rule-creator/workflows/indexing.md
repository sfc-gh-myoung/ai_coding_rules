# Phase 5: Keyword Generation Workflow

## Purpose

After creating and validating a rule file, generate keyword metadata so the deterministic matcher can discover the rule. The matcher reads YAML frontmatter directly from rule files — no separate index file is needed.

## Inputs

- Validated rule file path (e.g., `rules/422-daisyui-core.md`)

## Outputs

- Updated `keywords:` field in rule frontmatter

## Steps

### Step 5.1: Generate Keywords

Run the keywords generation command:

```bash
uv run ai-rules keywords generate --rule-path rules/422-daisyui-core.md
```

This calls Cortex AI to analyze the rule content and generate 5-7 discovery keywords.

### Step 5.2: Verify Keywords

Check the keywords were added to the frontmatter:

```bash
head -20 rules/422-daisyui-core.md
```

Verify the `keywords:` section contains 5-7 relevant terms.

### Step 5.3: Test Discovery

Verify the matcher can find the new rule:

```bash
python3 skills/rule-loader/scripts/match_rules.py --keywords "daisyui" --rules-dir rules
```

Confirm `422-daisyui-core.md` appears in the `load_sequence`.

### Step 5.4: Check for Collisions

Optionally verify no keyword over-collision:

```bash
uv run ai-rules keywords collisions --max-collision 3
```

If the new rule's keywords appear in the `violations` list, consider more specific compound phrases.

## Completion Checklist

- [ ] Keywords generated and added to frontmatter
- [ ] Rule discoverable via `python3 skills/rule-loader/scripts/match_rules.py --keywords "<technology>" --rules-dir rules`
- [ ] No excessive keyword collisions (optional)
