# 002-minimal-test-rule

## Metadata

**Keywords:** minimal, basic, test, fixture, validation, simple, baseline, schema-v3, required, essential
**TokenBudget:** ~450
**ContextTier:** Medium
**Depends:** rules/000-global-core.md

## Purpose

Minimal rule with only required sections for testing baseline schema validation.

## Rule Scope

Minimal testing scenarios with only essential sections.

## Quick Start TL;DR

**MANDATORY:**

**Essential Patterns:**
- **Basic validation:** Check minimum requirements
- **Simple structure:** Use only required sections
- **Clear purpose:** Document minimal intent

**Pre-Execution Checklist:**
- [ ] Basic prerequisites met
- [ ] Minimal requirements verified
- [ ] Structure validated
- [ ] Content checked
- [ ] References confirmed

## Contract

<inputs_prereqs>
Test environment with minimal setup
</inputs_prereqs>

<mandatory>
Basic testing tools
</mandatory>

<forbidden>
Complex dependencies
</forbidden>

<steps>
1. Validate minimal requirements
2. Execute basic checks
3. Verify structure
4. Check completeness
5. Document results
</steps>

<output_format>
Simple test results
</output_format>

<validation>
Basic validation passes
</validation>

## Post-Execution Checklist

- [ ] Minimal checks completed
- [ ] Structure validated
- [ ] Basic requirements met
- [ ] Documentation reviewed
- [ ] Results verified

## Validation

**Success Checks:**
- All required sections present
- Metadata fields complete
- Basic structure valid

## Output Format Examples

```bash
# Basic test execution
pytest tests/minimal/

# Expected output
===== test session starts =====
collected 5 items
tests/minimal/test_basic.py .....
===== 5 passed in 0.5s =====
```

## References

### Related Rules
- `000-global-core.md`
