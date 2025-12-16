# Phase 5: Indexing Workflow

## Purpose

Add the newly created and validated rule to `RULES_INDEX.md` in the correct numeric position to enable semantic discovery and maintain the organized rule catalog.

## Inputs

From Phase 4:
- Validated rule file: `rules/NNN-technology-aspect.md`
- Exit code 0 from `schema_validator.py`
- Metadata (rule number, keywords, scope, dependencies)

## Outputs

- Entry added to `RULES_INDEX.md`
- Correct numeric ordering maintained
- Table formatting intact
- Rule discoverable via RULES_INDEX search

## Step-by-Step Instructions

### Step 5.1: Extract Rule Metadata

From the validated rule file, extract:

```bash
# Rule number and filename
FILENAME="422-daisyui-core.md"
RULE_NUMBER="422"

# Scope (from ## Rule Scope section)
SCOPE="All web applications using DaisyUI component library..."

# Keywords (from metadata)
KEYWORDS="daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization"

# Dependencies (from Depends metadata)
DEPENDS="rules/420-javascript-core.md"
```

### Step 5.2: Format Index Entry

**RULES_INDEX.md format:**
```markdown
| Rule File | Scope | Keywords/Hints | Depends On |
```

**Entry template:**
```markdown
| NNN-technology-aspect | [Concise scope description] | [Keywords from metadata] | [Dependencies] |
```

**Example: DaisyUI**
```markdown
| 422-daisyui-core | DaisyUI component library patterns and best practices | daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization | rules/420-javascript-core.md |
```

### Step 5.3: Determine Insertion Position

Rules must be in numeric order. Find correct position:

**Search strategy:**
```bash
# Find rules before and after target number
grep "^| 42[0-9]-" RULES_INDEX.md

# Output shows:
| 420-javascript-core |
| 421-javascript-alpinejs-core |
# [INSERT 422 HERE]
| 440-react-core |
```

**Insertion logic:**
- Find last rule with number < target (421 in example)
- Insert new entry on next line
- Verify next rule has number > target (440 in example)

### Step 5.4: Read Current RULES_INDEX.md

```bash
# Open file to find insertion point
# Look for table section starting after "## Rules Index" header
# Find line with last rule number before target
```

**Current structure:**
```markdown
# Rules Index

|| File | Scope | Keywords/Hints | Depends On |
||------|-------|----------------|------------|
|| `000-global-core.md` | ...
|| `420-javascript-core.md` | ...
|| `421-javascript-alpinejs-core.md` | ...
|| `440-react-core.md` | ...
```

### Step 5.5: Insert New Entry

**Method 1: Direct file edit**
```markdown
# Find line with 421-javascript-alpinejs-core
# Add new line after it:

|| `421-javascript-alpinejs-core.md` | ... |
|| `422-daisyui-core.md` | DaisyUI component library patterns and best practices | daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization, utility-first, design system | rules/420-javascript-core.md |
|| `440-react-core.md` | ... |
```

**Important formatting:**
- Start with `||` (double pipe for table cell)
- Wrap filename in backticks: `` `422-daisyui-core.md` ``
- Separate columns with `|`
- End with `|` 
- Maintain spacing consistency with other rows

### Step 5.6: Verify Table Formatting

Check that:
- Table structure is intact (pipes aligned)
- New row matches format of surrounding rows
- No extra/missing pipes
- Backticks around filename
- No line breaks within row

**Validation:**
```bash
# Check line count increased by 1
BEFORE=$(grep -c "^||" RULES_INDEX.md_backup)
AFTER=$(grep -c "^||" RULES_INDEX.md)
echo "Added: $((AFTER - BEFORE)) row(s)"  # Should be 1

# Verify new entry exists
grep "422-daisyui-core" RULES_INDEX.md
```

### Step 5.7: Verify Numeric Ordering

```bash
# Extract all rule numbers from index
grep "^||" RULES_INDEX.md | sed 's/.*`\([0-9]*\)-.*/\1/' | sort -n

# Check that numbers are in sequence
# Should not have duplicates
# 422 should appear exactly once
# 422 should be between 421 and next number
```

### Step 5.8: Verify Keywords Match Metadata

Compare keywords in index entry with rule metadata:

**From RULES_INDEX.md:**
```markdown
| 422-daisyui-core | ... | daisyui, tailwind, components, ... | ... |
```

**From rules/422-daisyui-core.md metadata:**
```markdown
**Keywords:** daisyui, tailwind, components, ui library, themes, accessibility, ...
```

**Verification:**
- Keywords should match exactly (preferred)
- Or be a meaningful subset
- No completely different keywords
- Primary technology should be first

### Step 5.9: Verify Dependencies Listed

**From index:**
```markdown
| 422-daisyui-core | ... | ... | rules/420-javascript-core.md |
```

**From rule metadata:**
```markdown
**Depends:** rules/000-global-core.md, rules/420-javascript-core.md
```

**Note:** RULES_INDEX typically lists primary dependency (domain core), not all dependencies. This is acceptable.

## Complete Example: DaisyUI Index Entry

**Before addition:**
```markdown
|| `420-javascript-core.md` | JavaScript and frontend foundations | JavaScript, ES2024, ESM, Node.js, JSDoc, Biome | rules/000-global-core.md |
|| `421-javascript-alpinejs-core.md` | Alpine.js 3.x usage in web applications | Alpine.js, reactivity, x-data, x-bind, x-on, x-model | rules/000-global-core.md |
|| `430-typescript-core.md` | TypeScript files in frontend and backend | TypeScript, Zod, Strict Mode, Type Inference | rules/000-global-core.md |
```

**After addition:**
```markdown
|| `420-javascript-core.md` | JavaScript and frontend foundations | JavaScript, ES2024, ESM, Node.js, JSDoc, Biome | rules/000-global-core.md |
|| `421-javascript-alpinejs-core.md` | Alpine.js 3.x usage in web applications | Alpine.js, reactivity, x-data, x-bind, x-on, x-model | rules/000-global-core.md |
|| `422-daisyui-core.md` | DaisyUI component library patterns and best practices | daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization | rules/420-javascript-core.md |
|| `430-typescript-core.md` | TypeScript files in frontend and backend | TypeScript, Zod, Strict Mode, Type Inference | rules/000-global-core.md |
```

**Verification:**
```bash
$ grep "422-daisyui-core" RULES_INDEX.md
|| `422-daisyui-core.md` | DaisyUI component library patterns and best practices | daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization | rules/420-javascript-core.md |

✓ Entry added successfully
✓ Numeric order maintained (421 → 422 → 430)
✓ Table formatting intact
```

## Error Handling

### Error 1: Table Formatting Broken

**Symptom:** Markdown table doesn't render correctly after edit

**Check:**
```bash
# Count pipes per line - should be consistent
grep "^||" RULES_INDEX.md | awk '{print gsub(/\|/,"")}'
```

**Fix:**
- Ensure each row has same number of pipes
- Check for line breaks within cells
- Verify backticks are paired correctly

### Error 2: Duplicate Entry

**Symptom:** Rule number already exists in index

**Check:**
```bash
grep "^|| \`422-" RULES_INDEX.md | wc -l
# Should be 1 (only one entry for 422)
```

**Fix:**
- If duplicate: Remove one entry (usually older/incorrect one)
- If number conflict: This shouldn't happen if Phase 1 was done correctly
- Verify rule file matches index entry

### Error 3: Wrong Numeric Position

**Symptom:** Rule added but not in numeric order

**Check:**
```bash
# Extract numbers, check sorting
grep "^||" RULES_INDEX.md | sed 's/.*`\([0-9]*\)-.*/\1/' > /tmp/numbers.txt
sort -n /tmp/numbers.txt > /tmp/sorted.txt
diff /tmp/numbers.txt /tmp/sorted.txt
# Should show no differences
```

**Fix:**
- Cut misplaced entry
- Find correct position (between NNN-1 and NNN+1)
- Paste in correct location

## Validation Checklist

Before marking Phase 5 complete:

- [x] Index entry formatted correctly (pipes, backticks, spacing)
- [x] Entry added in correct numeric position
- [x] Numeric ordering verified (NNN-1 < NNN < NNN+1)
- [x] Table structure intact (all rows have same column count)
- [x] Keywords match or are subset of rule metadata
- [x] Dependencies listed accurately
- [x] Scope description is clear and concise
- [x] No duplicate entries for same rule number
- [x] File renders correctly as markdown table

## Testing Discoverability

Verify rule can be found via index search:

```bash
# Test keyword search
grep -i "daisyui" RULES_INDEX.md
# Should return the new 422 entry

grep -i "tailwind\|components" RULES_INDEX.md
# Should include 422 among results

# Test numeric search
grep "^|| \`422-" RULES_INDEX.md
# Should return exactly one entry
```

## Success Criteria

Indexing complete when:
- ✅ Entry added to RULES_INDEX.md
- ✅ Correct numeric position (between NNN-1 and NNN+1)
- ✅ Table formatting intact and renders correctly
- ✅ Keywords enable semantic discovery
- ✅ Rule discoverable via grep searches
- ✅ No duplicate entries

## Completion

**All 5 phases complete!**

```
✅ Phase 1: Discovery & Research - Domain identified, best practices gathered
✅ Phase 2: Template Generation - template_generator.py created structure
✅ Phase 3: Content Population - All sections filled with quality content
✅ Phase 4: Validation Loop - schema_validator.py returned exit code 0
✅ Phase 5: Indexing - Rule added to RULES_INDEX.md

🎉 Production-ready rule created: rules/422-daisyui-core.md
```

**Rule is now:**
- Validated (0 CRITICAL errors)
- Indexed (discoverable via RULES_INDEX.md)
- Ready for immediate use (rule file exists at `rules/422-daisyui-core.md`)
- Compliant with schema standards

## Final Verification

- Confirm the rule file exists: `rules/422-daisyui-core.md`
- Confirm it validates: `python scripts/schema_validator.py rules/422-daisyui-core.md` returns exit code 0

