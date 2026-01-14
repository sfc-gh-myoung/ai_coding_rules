# Schema Validator Usage: Validation Commands and Error Resolution

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> This rule defines essential governance patterns for the ai_coding_rules system.
> Load when creating, reviewing, or maintaining rules.

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v3.1.0
**LastUpdated:** 2026-01-13
**Keywords:** schema validator, validation errors, error resolution, exit codes, command options, output parsing, error severity, CRITICAL errors, HIGH warnings, MEDIUM info
**TokenBudget:** ~2250
**ContextTier:** High
**Depends:** 002-rule-governance.md, 000-global-core.md

## Scope

**What This Rule Covers:**
Core guide for running `schema_validator.py` against v3.2 rules. Covers command usage, interpreting validation output, resolving common errors, and understanding severity levels.

**When to Load This Rule:**
- Validating rule files against v3.2 schema
- Debugging validation errors
- Understanding exit codes and error severity levels
- Resolving common validation errors

**For Advanced Topics:**
- CI/CD integration: Load `002f-schema-validator-advanced.md`
- Automated fix workflows: Load `002f-schema-validator-advanced.md`
- Programmatic JSON parsing: Load `002f-schema-validator-advanced.md`

## References

### Dependencies

**Must Load First:**
- **002-rule-governance.md** - Schema requirements and v3.2 standards
- **000-global-core.md** - Foundation for all rules

**Related:**
- **002f-schema-validator-advanced.md** - CI/CD integration and automation workflows
- **002a-rule-creation.md** - Rule creation workflow with validation steps
- **002c-rule-optimization.md** - Token budgets and performance

### External Documentation

- **Schema Definition:** `schemas/rule-schema.yml` - Authoritative v3.2 schema
- **Validator Script:** `scripts/schema_validator.py` - Validation implementation
- **[CommonMark Spec](https://spec.commonmark.org/)** - Markdown specification

## Contract

### Inputs and Prerequisites

- Rule file to validate
- `schemas/rule-schema.yml` (v3.2)
- Python 3.8+ environment
- PyYAML library installed

### Mandatory

- `scripts/schema_validator.py`
- `schemas/rule-schema.yml`
- Python 3 with PyYAML
- Text editor for fixes

### Forbidden

- Committing rules with CRITICAL errors
- Skipping validation before commits
- Modifying `schema_validator.py` to pass invalid rules

### Execution Steps

1. Run `schema_validator.py` on rule file
2. Review validation output (CRITICAL, HIGH, MEDIUM, INFO)
3. Fix CRITICAL errors (required for passing)
4. Review and fix HIGH errors (strongly recommended)
5. Consider MEDIUM errors (optional improvements)
6. Re-run validation until 0 CRITICAL errors

### Output Format

Validation report showing:
- Passed checks count
- Error counts by severity (CRITICAL, HIGH, MEDIUM)
- Line numbers and fix suggestions for each error
- Overall PASS/FAIL result

### Validation

**Pre-Task-Completion Checks:**
- Python 3.8+ installed with PyYAML library
- `schema_validator.py` accessible in scripts/ directory
- Rule file exists and is readable

**Success Criteria:**
- Command runs without Python errors
- Validation report shows PASSED or WARNINGS ONLY
- CRITICAL error count is 0
- Error messages include fix suggestions

**Negative Tests:**
- Missing metadata field triggers CRITICAL error
- Wrong Keywords count triggers HIGH error
- Missing Contract subsection triggers CRITICAL error

### Post-Execution Checklist

- [ ] `schema_validator.py` runs without Python errors
- [ ] All CRITICAL errors fixed (0 CRITICAL required)
- [ ] HIGH errors reviewed and fixed
- [ ] Rule re-validated after fixes

## Running the Validator

### Basic Commands

```bash
# Validate single rule file
python3 scripts/schema_validator.py rules/002-rule-governance.md

# Validate all rules in directory
python3 scripts/schema_validator.py rules/

# Verbose output with detailed checks
python3 scripts/schema_validator.py rules/002-rule-governance.md --verbose

# Quiet mode (summary only)
python3 scripts/schema_validator.py rules/ --quiet

# JSON output for programmatic parsing
python3 scripts/schema_validator.py rules/ --json

# Strict mode (warnings = errors)
python3 scripts/schema_validator.py rules/ --strict
```

### Command Options

- **`[file/dir]`** - Path to validate
- **`--verbose`, `-v`** - Show all check details
- **`--quiet`, `-q`** - Show only summary
- **`--json`** - Output results in JSON format
- **`--strict`** - Treat warnings as errors
- **`--schema SCHEMA`** - Custom schema file path

### Exit Code Behavior

- **Exit 0:** No CRITICAL or HIGH errors (PASS or WARN)
- **Exit 1:** One or more CRITICAL or HIGH errors (FAIL)
- **Exit 1 with --strict:** Any errors including MEDIUM

```bash
python3 scripts/schema_validator.py rules/002-rule-governance.md
if [ $? -eq 0 ]; then
    echo "[PASS] Validation passed"
else
    echo "[FAIL] Validation failed"
fi
```

### Success Output

```
================================================================================
VALIDATION REPORT: rules/002-rule-governance.md
================================================================================

SUMMARY:
  CRITICAL: 0
  HIGH: 0
  MEDIUM: 1
  Passed: 458 checks

MEDIUM ISSUES (1):
────────────────────────────────────────────────────────────────────────────────
[Anti-Patterns] Anti-Patterns section is strongly recommended but optional

================================================================================
RESULT: WARNINGS ONLY
================================================================================
```

### Failure Output

```
================================================================================
VALIDATION REPORT: rules/bad-rule.md
================================================================================

SUMMARY:
  CRITICAL: 2
  HIGH: 1
  MEDIUM: 0
  Passed: 420 checks

CRITICAL ISSUES (2):
────────────────────────────────────────────────────────────────────────────────
[Metadata] Missing required field: Keywords
  Fix: Add **Keywords:** [5-20 comma-separated terms]
[Contract] Missing Markdown subsection: ### Mandatory
  Line: 45
  Fix: Add ### Mandatory header in Contract section

================================================================================
RESULT: FAILED
================================================================================
```

## Error Severity Levels

- **CRITICAL:** Blocks validation - MUST fix before commit
- **HIGH:** Important issue - Strongly recommended to fix
- **MEDIUM:** Optional improvement - Review and consider
- **INFO:** Informational - No action needed

## Common Errors and Fixes

### Error 1: Missing Keywords Field

**Error:** `[Metadata] Missing required field: Keywords`

**Fix:**
```markdown
**Keywords:** keyword1, keyword2, keyword3, keyword4, keyword5
```
Keywords must have 5-20 comma-separated terms.

### Error 2: Keywords Count Wrong

**Error:** `[Metadata] Keywords count: 3 (expected 5-20)`

**Fix:** Add more keywords to reach 5-20 count.
```markdown
# Before (3 keywords)
**Keywords:** SQL, Snowflake, CTE

# After (10 keywords)
**Keywords:** SQL, Snowflake, CTE, query optimization, performance, warehouse sizing, clustering, partitioning, query plan, cost analysis
```

### Error 3: TokenBudget Format Wrong

**Error:** `[Metadata] TokenBudget format invalid: expected ~NUMBER format`

**Fix:**
```markdown
# Wrong formats
**TokenBudget:** 1200      # Missing tilde
**TokenBudget:** small     # Text forbidden

# Correct format
**TokenBudget:** ~1200
```

### Error 4: Missing Required Section

**Error:** `[Structure] Missing required section: Scope`

**Fix:** Add Scope section after Metadata:
```markdown
## Scope

**What This Rule Covers:**
[1-2 sentence description]

**When to Load This Rule:**
- [Condition 1]
- [Condition 2]
```

### Error 5: Contract Missing Subsection

**Error:** `[Contract] Missing Markdown subsection: ### Mandatory`

**Fix:** Add missing ### header in Contract:
```markdown
## Contract

### Inputs and Prerequisites
[content]

### Mandatory
[content]

### Forbidden
[content]

### Execution Steps
[content]

### Output Format
[content]

### Validation
[content]

### Post-Execution Checklist
[content]
```

### Error 6: Section Order Wrong

**Error:** `[Structure] Sections out of order: Contract should come before Key Principles`

**Fix:** Reorder per v3.2 schema:
1. Metadata
2. Scope
3. References
4. Contract
5. [Content sections]
6. Anti-Patterns (optional)

### Error 7: Invalid RuleVersion Format

**Error:** `[Metadata] RuleVersion must be semantic version format (e.g., v1.0.0)`

**Fix:**
```markdown
# Wrong
**RuleVersion:** 1.0.0     # Missing v prefix
**RuleVersion:** v1        # Missing minor.patch

# Correct
**RuleVersion:** v1.0.0
```

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Ignoring MEDIUM Warnings

**Problem:** Never addressing MEDIUM warnings because they don't fail validation.

**Why It Fails:** Accumulated warnings create noise, hide new issues, degrade quality.

**Correct Pattern:**
```bash
# BAD: Only check for CRITICAL
python3 scripts/schema_validator.py rules/
# "No CRITICAL errors, ship it!"

# GOOD: Track and address warnings
python3 scripts/schema_validator.py rules/ --quiet
# Target: 0 CRITICAL, 0 HIGH, <10 MEDIUM total
```

### Anti-Pattern 2: Skipping Re-validation

**Problem:** Fixing errors without re-running validation to confirm fixes worked.

**Why It Fails:** Fixes may introduce new errors, or not resolve original issue.

**Correct Pattern:**
```bash
# Fix error
vim rules/<rule-file>.md

# Always re-validate
python3 scripts/schema_validator.py rules/<rule-file>.md
```

## ContextTier Validation

The validator checks ContextTier is one of: Critical, High, Medium, Low.

For tier selection guidance, see `002c-rule-optimization.md`.
