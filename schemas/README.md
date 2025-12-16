# Rule Schema v3.1 Documentation

**Location:** `schemas/rule-schema.yml`  
**Version:** 3.1  
**Purpose:** Validation schema for AI coding rules per 002-rule-governance.md v3.1

## Overview

This schema defines the structure, content, and format requirements for all AI coding rule files. It is used by `scripts/schema_validator.py` to validate rule files.

## Schema Structure

The schema is organized into 9 main sections:

1. **Metadata Validation** - RuleVersion, Keywords, TokenBudget, ContextTier, Depends
2. **Document Structure** - Required sections, order, placement
3. **Content Validation** - Deep content checks (code blocks, keywords, etc.)
4. **Placement Rules** - Section positioning (Contract before line 160)
5. **Format Restrictions** - No emojis, no YAML frontmatter, universal format
6. **Link Validation** - Rule references, external URLs
7. **Error Reporting** - Grouping, severity levels, formatting
8. **Excluded Files** - Files to skip during validation
9. **Validation Behavior** - Global settings

## Using the Schema

### Validate Single File

```bash
python scripts/schema_validator.py rules/100-snowflake-core.md
```

### Validate Directory

```bash
python scripts/schema_validator.py rules/
```

### Strict Mode (Warnings as Errors)

```bash
python scripts/schema_validator.py rules/ --strict
```

### Custom Schema Path

```bash
python scripts/schema_validator.py rules/ --schema schemas/custom-schema.yml
```

## Severity Levels

Errors are classified by severity:

- **CRITICAL** ❌ - Must fix, blocking (missing required sections, emojis)
- **HIGH** ⚠️  - Should fix, important (missing keywords, wrong order)
- **MEDIUM** ℹ️  - Consider fixing, quality (pattern counts, style)
- **INFO** ✓ - Informational, suggestions

## Metadata Validation

All rule files must have 5 metadata fields in this exact order:

1. **RuleVersion:** Semantic version format (vX.Y.Z)
2. **Keywords:** 10-15 comma-separated semantic terms
3. **TokenBudget:** ~NUMBER format (e.g., ~1500)
4. **ContextTier:** Critical | High | Medium | Low
5. **Depends:** Comma-separated list of prerequisite rules

**Example:**
```markdown
**RuleVersion:** v1.0.0
**Keywords:** snowflake, sql, data warehouse, query optimization, performance, caching, clustering, partitioning, snowpipe, stages, external tables, streams, tasks, materialized views, security
**TokenBudget:** ~2500
**ContextTier:** Critical
**Depends:** rules/000-global-core
```

## Required Sections

All rules must have these 9 sections in order:

1. **Purpose** - 1-2 sentences (what and why)
2. **Rule Scope** - Single line (domain coverage)
3. **Quick Start TL;DR** - 30-second reference (6-7 patterns, 5-7 checklist items)
4. **Contract** - Must appear before line 160 (6 required fields)
5. **Anti-Patterns and Common Mistakes** - 2+ code examples
6. **Quick Compliance Checklist** - 5+ checklist items
7. **Validation** - How to validate compliance
8. **Response Template** - Code examples for output
9. **References** - External Documentation and Related Rules subsections

## Content Validation Rules

### Quick Start TL;DR

Must contain:
- ✅ "MANDATORY" keyword
- ✅ 6-7 Essential Patterns
- ✅ 5-7 Quick Checklist items

### Contract

Must contain all 6 fields:
- ✅ Inputs/Prereqs
- ✅ Allowed Tools
- ✅ Forbidden Tools
- ✅ Required Steps (5-10 numbered steps)
- ✅ Output Format
- ✅ Validation Steps

### Anti-Patterns

Must contain:
- ✅ At least 2 code blocks
- ✅ "Problem:" keyword
- ✅ "Correct Pattern:" keyword

### Response Template

Must contain:
- ✅ At least 1 code block
- ✅ Non-empty content

## Placement Rules

### Contract Placement

**Rule:** Contract section must appear before line 160

**Rationale:** Progressive disclosure - critical contract information must be accessible early in the file

**Calculation:** Line number accounts for:
- Metadata length
- Purpose section length
- Adjustments for long titles/descriptions

### Quick Start Placement

**Rule:** Quick Start TL;DR must be after Rule Scope, before Contract

**Rationale:** Users need quick reference immediately after understanding scope

## Format Restrictions

### No Emojis

**Rule:** No emojis allowed in rule files  
**Severity:** CRITICAL  
**Rationale:** Machine-readable text-only markup required for universal compatibility

### No YAML Frontmatter

**Rule:** No YAML frontmatter blocks (`---`)  
**Severity:** CRITICAL  
**Rationale:** Universal output format - metadata in inline **Field:** format

### Universal Markdown Format

**Rule:** Pure Markdown syntax only  
**Severity:** HIGH  
**Rationale:** Compatible with all Markdown parsers and tools

## Link Validation

### Rule References

**Pattern:** `rules/[filename].md`  
**Check:** File exists  
**Allowed Placeholders:**
- `filename.md`
- `rule-name.md`
- `NNN-technology-core.md`

### External URLs

**Pattern:** `http://` or `https://`  
**Check:** Reachability (optional, disabled by default)  
**Severity:** INFO

## Error Reporting

Errors are grouped by section for easier fixing:

```
================================================================================
VALIDATION REPORT: rules/100-snowflake-core.md
================================================================================

SUMMARY:
  ❌ CRITICAL: 1
  ⚠️  HIGH: 2
  ℹ️  MEDIUM: 3
  ✓ Passed: 12 checks

CRITICAL ISSUES (1):
─────────────────────────────────────────────────────────────────────────────
[Structure] Missing required section: "Anti-Patterns and Common Mistakes"
  Line: N/A
  Fix: Add "## Anti-Patterns and Common Mistakes" section with 2-5 examples
  Reference: 002-rule-governance.md Section 5a

HIGH ISSUES (2):
─────────────────────────────────────────────────────────────────────────────
[Contract] Missing required field: "Validation Steps"
  Line: 89-120
  Fix: Add "**Validation Steps:**" to Contract section
  
[Quick Start] Only 4 patterns found, expected 6-7
  Line: 94-110
  Fix: Add 2-3 more essential patterns to Quick Start TL;DR section

MEDIUM ISSUES (3):
─────────────────────────────────────────────────────────────────────────────
[Metadata] Keywords count: 12 (expected 15-20)
  Line: 3
  Fix: Add 3-8 more semantic keywords for better discovery

================================================================================
RESULT: ❌ FAILED (1 CRITICAL, 2 HIGH, 3 MEDIUM issues)
================================================================================
```

## Schema Versioning

**Current Version:** 3.1  
**Strategy:** Single version file - all rules use latest schema (version tracked inside file)

**When Schema Changes:**
1. Update `schemas/rule-schema.yml` (version field inside file)
2. Document breaking changes in CHANGELOG
3. Run validation on all rules
4. Fix high-priority rules
5. Document known issues

## Extending the Schema

### Adding New Validation Rules

**Example: Add minimum word count for Purpose section**

```yaml
structure:
  required_sections:
    - name: "Purpose"
      level: 2
      order: 1
      required: true
      content_validation:
        min_word_count: 20  # NEW RULE
        max_word_count: 100  # NEW RULE
```

### Adding New Content Checks

**Example: Check for specific keywords in Validation section**

```yaml
content_rules:
  validation_section:  # NEW SECTION
    section: "Validation"
    validations:
      - type: "keyword_presence"
        must_contain: ["test", "verify", "check"]
        error_message: "Validation section must mention testing"
        severity: "MEDIUM"
```

### Adding New Error Groups

**Example: Add "Performance" error group**

```yaml
error_reporting:
  error_groups:
    - "Metadata"
    - "Structure"
    - "Performance"  # NEW GROUP
```

## Common Validation Scenarios

### Scenario 1: Missing Required Section

**Error:**
```
[Structure] Missing required section: "Contract"
```

**Fix:**
```markdown
## Contract

- **Inputs/Prereqs:** [Required context]
- **Allowed Tools:** [List tools]
- **Forbidden Tools:** [List restrictions]
- **Required Steps:**
  1. [First step]
  2. [Second step]
- **Output Format:** [Expected format]
- **Validation Steps:** [Validation checks]
```

### Scenario 2: Contract Too Late

**Error:**
```
[Contract] Contract section must appear before line 160
  Current line: 175
```

**Fix:** Move Contract section earlier, or reduce Purpose/metadata length

### Scenario 3: Missing Keywords

**Error:**
```
[Metadata] Keywords count: 12 (expected 15-20)
```

**Fix:** Add 3-8 more semantic keywords:
```markdown
**Keywords:** [original 12], [new keyword 1], [new keyword 2], [new keyword 3]
```

### Scenario 4: Anti-Patterns Missing Code

**Error:**
```
[Anti-Patterns] Must have at least 2 code examples
  Current: 0
```

**Fix:**
```markdown
## Anti-Patterns and Common Mistakes

**Problem:** [Description]
```python
# Incorrect approach
bad_code()
```

**Correct Pattern:**
```python
# Correct approach
good_code()
```
```

## Schema Validation Performance

**Expected Performance:**
- Single file: ~10-20ms
- All 87 rules: ~1-2 seconds
- Parallel mode: ~0.5-1 second

**Optimization:**
- Schema caching (loaded once)
- Parallel validation (optional)
- Early exit on critical errors (optional `--fail-fast`)

## Troubleshooting

### Schema Not Found

**Error:** `FileNotFoundError: schemas/rule-schema.yml`

**Fix:** Ensure schema file exists, or specify path:
```bash
python scripts/schema_validator.py rules/ --schema /path/to/schema.yml
```

### Too Many Errors

**Error:** Validation report shows 100+ errors

**Fix:** Use `--fail-fast` to stop on first critical error:
```bash
python scripts/schema_validator.py rules/ --fail-fast
```

### Validation Too Strict

**Issue:** Many false positives, too many warnings

**Fix:** 
1. Check if rule genuinely needs fixing
2. Update schema if rule is correct and schema is too strict
3. Use `--no-strict` to ignore warnings

## References

**Related Documentation:**
- `rules/002-rule-governance.md` - Rule standards (Section 11)
- `[removed - boilerplate deprecated]` - Canonical template
- `docs/YAML_SCHEMA_IMPLEMENTATION_PLAN.md` - Implementation plan
- `docs/schema_design_spec.md` - Schema design specification

**Schema File:**
- `schemas/rule-schema.yml` - This schema

**Validator:**
- `scripts/schema_validator.py` - Validation engine

---

**Last Updated:** 2025-12-16  
**Version:** 3.1  
**Status:** Active
