# LoadTrigger Guidelines

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Extracted from 002-rule-governance.md for token efficiency.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**Keywords:** loadtrigger, dynamic rule loading, rule discovery, file extension trigger, keyword trigger, directory trigger, filename trigger, RULES_INDEX
**TokenBudget:** ~2100
**ContextTier:** Medium
**Depends:** 002-rule-governance.md

## Scope

**What This Rule Covers:**
LoadTrigger metadata field specification for dynamic rule discovery based on file context, keywords, or activities.

**When to Load This Rule:**
- Adding or modifying LoadTrigger fields on rules
- Understanding dynamic rule discovery mechanisms
- Debugging rule loading behavior

## References

### Dependencies

**Must Load First:**
- **002-rule-governance.md** - Parent rule for schema standards

**Related:**
- **002a-rule-creation.md** - Rule creation workflow (includes LoadTrigger step)

## Contract

### Inputs and Prerequisites

- A rule file that needs dynamic loading triggers
- Understanding of trigger types (ext, file, dir, kw)

### Mandatory

- Use 2-4 triggers per rule
- Combine extension + keyword triggers for language rules
- Regenerate index after adding triggers: `uv run ai-rules index generate`

### Forbidden

- Adding LoadTriggers to foundation rules (000-series, 001-core, 002-governance)
- Using LoadTriggers for sub-rules that should be loaded via Depends
- Using overly generic keywords that match 3+ rules

### Execution Steps

1. Determine if rule needs LoadTrigger (see decision process below)
2. Select appropriate trigger types
3. Add LoadTrigger field to metadata
4. Regenerate index: `uv run ai-rules index generate`
5. Validate: `uv run ai-rules validate rules/<rule>.md`

### Output Format

LoadTrigger metadata field in rule file:
```markdown
**LoadTrigger:** ext:.py, kw:python, kw:testing
```

### Validation

**After adding LoadTrigger:**
1. Regenerate index: `uv run ai-rules index generate`
2. Validate references: `uv run ai-rules refs check`
3. Run tests: `uv run pytest --tb=short -q`
4. Check formatting: `uvx ruff check .` (validates Python scripts that process LoadTrigger values)

**Pre-Task-Completion Checks:**
1. Target rule file exists and passes `uv run ai-rules validate`
2. Rule is not a foundation rule (000-series, 001-core, 002-governance)
3. Rule has no unresolved Depends chain

**Success Criteria:**
- LoadTrigger uses valid trigger types (ext, file, dir, kw)
- 2-4 triggers per rule
- No overly generic keywords

**Negative Tests:**
- LoadTrigger with invalid prefix (e.g., `type:.py`) should fail validation
- More than 4 triggers per rule should generate a warning
- Foundation rule (000-series) with LoadTrigger should be flagged

### Error Recovery

- **`uv run ai-rules index generate` fails:** Verify Python environment, check for syntax errors in rule file metadata, try regenerating with `--verbose`
- **LoadTrigger format errors:** Check trigger prefix (ext:/file:/dir:/kw:), verify no trailing whitespace, ensure comma separation between triggers
- **Conflicting triggers with existing rules:** Some overlap is intentional (see Best Practices). If >3 rules share identical triggers, consolidate trigger coverage or make keywords more specific.

### Post-Execution Checklist

- [ ] LoadTrigger uses valid trigger types
- [ ] 2-4 triggers defined
- [ ] Index regenerated
- [ ] Validation passes

## What is LoadTrigger?

**LoadTrigger** is an optional metadata field that enables dynamic rule discovery based on file context, keywords, or activities. It allows the system to automatically suggest relevant rules when specific conditions are met.

## When to Use LoadTrigger

**Add LoadTrigger when:**
- Rule applies to specific file extensions (e.g., `.py`, `.sql`, `.tsx`)
- Rule applies to specific filenames (e.g., `pyproject.toml`, `Dockerfile`)
- Rule applies to specific directories (e.g., `rules/`, `tests/`)
- Rule provides guidance for specific activities or keywords (e.g., `kw:testing`, `kw:performance`)

**Skip LoadTrigger for:**
- Foundation/infrastructure rules (always loaded automatically)
- Sub-rules with explicit Depends relationships (loaded via parent rule)
- Highly specialized rules (loaded only when explicitly requested)

## LoadTrigger Syntax

LoadTrigger uses four trigger types:

```markdown
**LoadTrigger:** ext:.py, kw:python, kw:testing
```

**Trigger Types:**

1. **ext:** - File extension triggers
   - `ext:.py` - Python files
   - `ext:.sql` - SQL files
   - `ext:.tsx` - TypeScript React files

2. **file:** - Specific filename triggers
   - `file:pyproject.toml` - Python project config
   - `file:Dockerfile` - Docker configuration
   - `file:CHANGELOG.md` - Changelog file

3. **dir:** - Directory-based triggers
   - `dir:rules/` - Rules directory
   - `dir:tests/` - Test directory

4. **kw:** - Keyword/activity triggers
   - `kw:testing` - Testing activities
   - `kw:performance` - Performance optimization
   - `kw:security` - Security-related work

## LoadTrigger Patterns

**Language Rules:**
```markdown
**LoadTrigger:** ext:.py, kw:python
```

**Framework Rules:**
```markdown
**LoadTrigger:** kw:fastapi, kw:api, file:main.py
```

**Activity Rules:**
```markdown
**LoadTrigger:** kw:testing, kw:unit-test, kw:pytest
```

**Multi-Context Rules:**
```markdown
**LoadTrigger:** ext:.tsx, kw:react, kw:frontend
```

## LoadTrigger Best Practices

**DO:**
- Use 2-4 triggers per rule (average: 2.1 based on current data)
- Combine extension + keyword triggers for language rules
- Use specific, descriptive keywords
- Include synonyms for discoverability (e.g., `kw:mock, kw:test-data, kw:faker`)
- Check existing rules for similar triggers to maintain consistency

**DON'T:**
- Use overly generic keywords that match 3+ rules
- Duplicate triggers unnecessarily (some overlap is intentional)
- Add LoadTriggers to foundation rules (000-series, 001-core, 002-governance)
- Use LoadTriggers for sub-rules that should be loaded via Depends

## LoadTrigger Examples

**Example 1: Python Core Rule**
```markdown
**LoadTrigger:** ext:.py, ext:.pyi, kw:python
```
Triggers on: Python files OR "python" keyword

**Example 2: FastAPI Testing Rule**
```markdown
**LoadTrigger:** kw:fastapi-testing, kw:test
```
Triggers on: FastAPI testing activities

**Example 3: Multi-Extension React Rule**
```markdown
**LoadTrigger:** ext:.jsx, ext:.tsx, kw:react
```
Triggers on: JSX/TSX files OR "react" keyword

**Example 4: Config File Rule**
```markdown
**LoadTrigger:** file:pyproject.toml, kw:python-project
```
Triggers on: pyproject.toml file OR "python-project" keyword

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Too Generic Triggers

**[BAD]:**
```markdown
**LoadTrigger:** kw:code, kw:file
```
**Problem:** Matches almost everything, no specificity.

**Correct Pattern:** Use domain-specific keywords.

### Anti-Pattern 2: Redundant Keywords

**[BAD]:**
```markdown
**LoadTrigger:** kw:python, kw:py, kw:python-lang, kw:python-code
```
**Problem:** All synonyms, no additional value.

**Correct Pattern:** Pick 1-2 canonical terms.

### Anti-Pattern 3: Wrong Context

**[BAD]:**
```markdown
# In 000-global-core.md
**LoadTrigger:** kw:core
```
**Problem:** Foundation rules should NOT have LoadTriggers.

**Correct Pattern:** Foundation rules are always loaded automatically.

## LoadTrigger Impact on RULES_INDEX.md

When you add LoadTrigger to a rule, it automatically appears in `RULES_INDEX.md` after running:

```bash
uv run ai-rules index generate
```

The index organizes rules by trigger type:
- **Section 2:** Directory and file extension rules
- **Section 3:** Activity rules (keyword-based)

## LoadTrigger Decision Process

When creating or updating a rule, ask:

1. **Is this a foundation rule?** No LoadTrigger (always loaded)
2. **Does it have a parent rule via Depends?** No LoadTrigger (loaded by parent)
3. **Does it apply to specific file types?** Add ext:/file: triggers
4. **Does it guide specific activities?** Add kw: triggers
5. **Is it highly specialized?** Skip LoadTrigger (on-demand only)

**Refer to:** `docs/loadtrigger_decisions.md` for detailed categorization and rationale for all rules in the repository.

**Current Coverage Statistics (as of 2026-01-20, regenerate with `uv run ai-rules index stats`):**
- Total rules: 122
- Rules with LoadTrigger: 84 (69%)
- Average triggers per rule: 2.1
- Target achieved: 125% (target was 67 rules / 55%)
