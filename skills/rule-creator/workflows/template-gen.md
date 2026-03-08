# Phase 2: Template Generation Workflow

## Purpose

Execute `ai-rules new` to create a v3.0-compliant rule file structure with all required sections, Contract XML tags, and metadata placeholders ready for population.

## Inputs

From Phase 1:
- Rule number (e.g., 422)
- Technology name (e.g., "daisyui")
- Aspect (e.g., "core")
- Recommended ContextTier

## Outputs

- File created: `rules/NNN-technology-aspect.md`
- All required v3.2 sections present
- Contract section with 6 Markdown subsections
- Metadata structure ready for population
- Placeholder content to replace

## Step-by-Step Instructions

### Step 2.1: Determine ContextTier

Select appropriate tier based on rule importance and usage frequency:

- ****Critical**** - When to Use: Core framework, always loaded, Token Range: <500, Examples: 000-global-core
- ****High**** - When to Use: Domain foundations, frequent, Token Range: 500-1500, Examples: 100-snowflake-core, 200-python-core
- ****Medium**** - When to Use: Specific features, moderate, Token Range: 1500-3000, Examples: Most new technology rules
- ****Low**** - When to Use: Specialized, rare, Token Range: 3000-5000, Examples: Advanced/reference docs

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
-  `422-daisyui-core`
-  `231-python-msgspec`
-  `125-snowflake-hybrid-tables`
-  `42-DaisyUI-Core` (wrong: not 3 digits, wrong case)
-  `422_daisyui_core` (wrong: underscores)

### Step 2.3: Execute ai-rules new

**Command format:**
```bash
ai-rules new [NNN]-[technology]-[aspect] \
  --context-tier [Critical|High|Medium|Low]
```

**Example: DaisyUI**
```bash
ai-rules new 422-daisyui-core --context-tier Medium
```

**Example: Snowflake Feature**
```bash
ai-rules new 125-snowflake-hybrid-tables --context-tier High
```

**Example: Python Library**
```bash
ai-rules new 231-python-msgspec --context-tier Medium
```

### Step 2.4: Verify Success Output

**Expected output:**
```
 Created rule template: rules/422-daisyui-core.md

Next steps:
1. Edit rules/422-daisyui-core.md and replace all placeholders with actual content
2. Validate: ai-rules validate rules/422-daisyui-core.md
3. Add to RULES_INDEX.md
```

**Check exit code:**
```bash
if [ $? -eq 0 ]; then
  echo " Template created successfully"
else
  echo " Template creation failed - check error message"
  # See error handling below
fi
```

### Step 2.5: Verify Template Structure

Read created file and confirm presence of:

```markdown
# [NNN]-[technology]-[aspect]: [Title]

## Metadata

**SchemaVersion:** v3.0
**Keywords:** [placeholder keywords]
**TokenBudget:** ~1200
**ContextTier:** [specified tier]
**Depends:** rules/000-global-core.md

## Purpose
[1-2 sentence description...]

## Rule Scope
[Single line defining...]

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **[Pattern 1]:** [Description]
- **[Pattern 2]:** [Description]
- **[Pattern 3]:** [Description]

**Pre-Execution Checklist:**
- [ ] [First prerequisite]
- [ ] [Second prerequisite]
...

## Contract

<inputs_prereqs>
[What the agent needs...]
</inputs_prereqs>

<mandatory>
[Required tools...]
</mandatory>

<forbidden>
[Prohibited actions...]
</forbidden>

<steps>
1. [First step]
2. [Second step]
...
</steps>

<output_format>
[Expected output...]
</output_format>

<validation>
[How to verify...]
</validation>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1:** [Name]
...

## Post-Execution Checklist
- [ ] [Verification item...]

## Validation

**Success Checks:**
...

**Negative Tests:**
...

## Output Format Examples

```bash
# Example command
...
```

## References

### Related Rules
- `rules/000-global-core.md` - Global standards

### External Documentation
- [Link](URL) - Description
```

### Step 2.7: Check Contract Placement

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

### Error 4: Command Not Found

**Error message:**
```
ai-rules: command not found
```

**Fix:**
- Verify current directory: `pwd`
- Should be in project root: `/Users/myoung/Development/ai_coding_rules`
- Ensure CLI is installed: `pip install -e .` or `uv pip install -e .`
- Verify command works: `ai-rules --help`

### Error 5: Python Environment Issues

**Error message:**
```
ModuleNotFoundError: No module named 'typer'
```

**Fix:**
- Activate virtual environment: `source .venv/bin/activate`
- Install dependencies: `uv pip install -e .`
- Verify Python 3.11+: `python3 --version`

## Validation Checklist

Before proceeding to Phase 3, verify:

- [x] `ai-rules new` executed successfully (exit code 0)
- [x] File created at `rules/NNN-technology-aspect.md`
- [x] All required v3.2 sections present
- [x] Contract section has 6 Markdown headers
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
$ ai-rules new 422-daisyui-core --context-tier Medium

 Created rule template: rules/422-daisyui-core.md

Next steps:
1. Edit rules/422-daisyui-core.md and replace all placeholders
2. Validate: ai-rules validate rules/422-daisyui-core.md
3. Add to RULES_INDEX.md
```

**Verification:**
```bash
$ ls -lh rules/422-daisyui-core.md
-rw-r--r--  1 user  staff   3.2K Dec 11 15:30 rules/422-daisyui-core.md

$ grep -n "^## " rules/422-daisyui-core.md
3:## Metadata
9:## Purpose
13:## Rule Scope
17:## Quick Start TL;DR
35:## Contract (line 35 < 160 )
65:## Anti-Patterns and Common Mistakes
85:## Post-Execution Checklist
95:## Validation
105:## Output Format Examples
120:## References

$ grep -c "<inputs_prereqs>\|<mandatory>\|<forbidden>\|<steps>\|<output_format>\|<validation>" rules/422-daisyui-core.md
6  # All 6 XML tags present 
```

**Output Summary:**
```
 Template created: rules/422-daisyui-core.md
 Size: 3.2KB (reasonable starting point)
 Sections: 9/9 present
 Contract XML tags: 6/6 present
 Contract placement: Line 35 (before 160 )
 Ready for Phase 3: Content Population
```

## Next Phase

Proceed to **Phase 3: Content Population** (`workflows/content-population.md`)

**Inputs to carry forward:**
- File path: `rules/422-daisyui-core.md`
- Keywords from Phase 1 (15 terms)
- Essential Patterns from Phase 1 (4 patterns)
- Anti-Patterns from Phase 1 (3 patterns)
- External references from Phase 1

**Action:** Begin replacing placeholders with rese                