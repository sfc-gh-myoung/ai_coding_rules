# Phase 2: Template Generation Workflow

## Purpose

Use `ai-rules new` to create a v3.6-compliant rule file with the required Markdown sections and metadata placeholders ready for population.

## Inputs

From Phase 1:
- Rule number (e.g., 422)
- Technology name (e.g., "daisyui")
- Aspect (e.g., "core")
- Recommended ContextTier

## Outputs

- File created: `rules/NNN-technology-aspect.md`
- All 9 required sections present
- Contract section with 6 XML tags
- Metadata structure ready for population
- Placeholder content to replace

## Step-by-Step Instructions

### Step 2.1: Determine ContextTier

Select appropriate tier based on rule importance and usage frequency:

| Tier | When to Use | Token Range | Examples |
|------|-------------|-------------|----------|
| **Critical** | Core framework, always loaded | <500 | 000-global-core |
| **High** | Domain foundations, frequent | 500-1500 | 100-snowflake-core, 200-python-core |
| **Medium** | Specific features, moderate | 1500-3000 | Most new technology rules |
| **Low** | Specialized, rare | 3000-5000 | Advanced/reference docs |

**Decision criteria:**
- Is this a domain foundation? → High
- Is this widely used? → High or Medium
- Is this specialized/advanced? → Medium or Low
- Default for new technology: **Medium**

### Step 2.2: Construct Filename

Format: `NNN-technology-aspect`

**Rules:**
- NNN: 3-digit number (pad with zeros: 001, 042, 422)
- technology: lowercase, hyphens (not underscores)
- aspect: usually "core" for foundational rules

**Examples:**
- ✓ `422-daisyui-core`
- ✓ `231-python-msgspec`
- ✓ `125-snowflake-hybrid-tables`
- ✗ `42-DaisyUI-Core` (wrong: not 3 digits, wrong case)
- ✗ `422_daisyui_core` (wrong: underscores)

### Step 2.3: Execute `ai-rules new`

**Command format:**
```bash
uv run ai-rules new [NNN]-[technology]-[aspect] \
  --context-tier [Critical|High|Medium|Low] \
  --output-dir rules/
```

**Example: DaisyUI**
```bash
uv run ai-rules new 422-daisyui-core \
  --context-tier Medium \
  --output-dir rules/
```

**Example: Snowflake Feature**
```bash
uv run ai-rules new 125-snowflake-hybrid-tables \
  --context-tier High \
  --output-dir rules/
```

**Example: Python Library**
```bash
uv run ai-rules new 231-python-msgspec \
  --context-tier Medium \
  --output-dir rules/
```

### Step 2.4: Verify Success Output

**Expected output:**
```
✅ Created rule template: rules/422-daisyui-core.md

Next steps:
1. Edit rules/422-daisyui-core.md and replace all placeholders with actual content
2. Validate: uv run ai-rules validate rules/422-daisyui-core.md
3. Add to rule frontmatter
```

**Check exit code:**
```bash
if [ $? -eq 0 ]; then
  echo "✓ Template created successfully"
else
  echo "✗ Template creation failed - check error message"
  # See error handling below
fi
```

### Step 2.5: Verify Template Structure

Read created file and confirm presence of:

```markdown
---
schema_version: v3.6
rule_version: v1.0.0
description: [One-sentence rule summary]
last_updated: YYYY-MM-DD
keywords:
  - kw:[semantic keyword]
  - kw:[semantic keyword]
  - kw:[semantic keyword]
  - kw:[semantic keyword]
  - kw:[semantic keyword]
token_budget: ~1200
context_tier: [specified tier]
depends:
  required:
    - 000-global-core.md
---

# [NNN]-[technology]-[aspect]

## Scope

**What This Rule Covers:** [1-2 sentence description]

**When to Load This Rule:**
- [Trigger condition]

## References

### External Documentation

_None._

## Contract

### Inputs and Prerequisites

[What the agent needs]

### Mandatory

[Required tools and behaviors]

### Forbidden

[Prohibited actions]

### Execution Steps

1. [First step]
2. [Second step]
...

### Output Format

[Expected output]

### Validation

[How to verify]

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1:** [Name]
...

## Post-Execution Checklist
- [ ] [Verification item...]

```

### Step 2.6: Count Sections

Verify required frontmatter and top-level sections are present:

1. ✓ YAML frontmatter with v3.6 metadata
2. ✓ Scope
3. ✓ References
4. ✓ Contract
5. ✓ Anti-Patterns and Common Mistakes
6. ✓ Post-Execution Checklist
9. ✓ References

### Step 2.7: Verify Contract XML Tags

Confirm all 6 tags present in Contract section:

1. ✓ `<inputs_prereqs>...</inputs_prereqs>`
2. ✓ `<mandatory>...</mandatory>`
3. ✓ `<forbidden>...</forbidden>`
4. ✓ `<steps>...</steps>`
5. ✓ `### Output Format`
6. ✓ `### Validation`

### Step 2.8: Check Contract Placement

**Requirement:** Contract section must appear before line 160

**Verification:**
```bash
# Count lines to Contract section
grep -n "^## Contract" rules/422-daisyui-core.md
# Output should show line number < 160
# Example: 48:## Contract
```

**If Contract after line 160:**
- This is an `ai-rules new` issue (unlikely)
- File structure may need adjustment
- Report issue and manually adjust if needed

## Error Handling

### Error 1: Invalid Filename Format

**Error message:**
```
Error: Invalid filename format: 42-DaisyUI-Core
Expected format: NNN-technology-aspect (e.g., 100-snowflake-sql)
```

**Fix:**
- Verify 3-digit number: `42` → `042` or keep as `422`
- Convert to lowercase: `DaisyUI-Core` → `daisyui-core`
- Use hyphens: `daisyui_core` → `daisyui-core`
- Retry with corrected filename

### Error 2: File Already Exists

**Error message:**
```
Error: Rule file already exists: rules/422-daisyui-core.md
Use --force to overwrite
```

**Investigation:**
```bash
# Check if file exists and is populated
ls -lh rules/422-daisyui-core.md
head -20 rules/422-daisyui-core.md
```

**Decision:**
- If file is template (placeholders) → Safe to overwrite with `--force`
- If file has real content → Use different number or aspect
- If duplicate request → Skip template generation, use existing

### Error 3: Invalid ContextTier

**Error message:**
```
Error: Context tier must be one of: Critical, High, Medium, Low
```

**Fix:**
- Check capitalization: `medium` → `Medium`
- Check spelling: `Meduim` → `Medium`
- Retry with correct tier value

### Error 4: CLI Not Found

**Error message:**
```
ai-rules: command not found
```

**Fix:**
- Verify current directory: `pwd`
- Should be in project root: `/Users/myoung/Development/ai_coding_rules`
- If not, cd to project root first
- Sync the environment: `uv sync --all-groups`

### Error 5: Python Not Found

**Error message:**
```
uv: command not found
```

**Fix:**
- Install uv, then run `uv sync --all-groups`
- Verify Python installed: `python3 --version`
- Project requires Python 3.12+

## Validation Checklist

Before proceeding to Phase 3, verify:

- [x] `ai-rules new` executed successfully (exit code 0)
- [x] File created at `rules/NNN-technology-aspect.md`
- [x] All 9 required sections present
- [x] Contract section has 6 XML tags
- [x] Contract placed before line 160
- [x] Metadata structure present (Keywords, TokenBudget, ContextTier, Depends)
- [x] Placeholder content ready for population

## Example: Complete Phase 2 Execution

**Input from Phase 1:**
```
Technology: DaisyUI
Domain: 420-449
Number: 422
Aspect: core
ContextTier: Medium
```

**Execution:**
```bash
$ uv run ai-rules new 422-daisyui-core \
    --context-tier Medium \
    --output-dir rules/

✅ Created rule template: rules/422-daisyui-core.md

Next steps:
1. Edit rules/422-daisyui-core.md and replace all placeholders
2. Validate: uv run ai-rules validate rules/422-daisyui-core.md
3. Add to rule frontmatter
```

**Verification:**
```bash
$ ls -lh rules/422-daisyui-core.md
-rw-r--r--  1 user  staff   3.2K Dec 11 15:30 rules/422-daisyui-core.md

$ grep -n "^## " rules/422-daisyui-core.md
3:## Scope
20:## References
35:## Contract

$ grep -c "^### " rules/422-daisyui-core.md
6  # Required Contract subsections present
```

**Output Summary:**
```
✓ Template created: rules/422-daisyui-core.md
✓ Size: 3.2KB (reasonable starting point)
✓ Sections: 9/9 present
✓ Contract XML tags: 6/6 present
✓ Contract placement: Line 35 (before 160 ✓)
✓ Ready for Phase 3: Content Population
```

## Next Phase

Proceed to **Phase 3: Content Population** (`workflows/content-population.md`)

**Inputs to carry forward:**
- File path: `rules/422-daisyui-core.md`
- Keywords from Phase 1 (15 terms)
- Essential Patterns from Phase 1 (4 patterns)
- Anti-Patterns from Phase 1 (3 patterns)
- External references from Phase 1

**Action:** Begin replacing placeholders with researched content

