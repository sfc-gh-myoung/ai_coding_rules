**Keywords:** complete, example, test, validation
**TokenBudget:** ~800
**ContextTier:** High
**Version:** 1.0.0
**LastUpdated:** 2025-01-13
**Depends:** 000-global-core.md

# Complete Test Rule

## Purpose
A complete rule file with all required sections and metadata for testing.

## Rule Type and Scope
- **Type:** Agent Requested
- **Scope:** Testing and validation scenarios

## Contract
- **Inputs/Prereqs:** Test environment
- **Allowed Tools:** All testing tools
- **Forbidden Tools:** Production tools
- **Required Steps:**
  1. Validate input
  2. Execute test
  3. Verify output
- **Output Format:** Test results in markdown
- **Validation Steps:** Check all assertions pass

## Key Principles
- Test thoroughly
- Document clearly
- Validate completely

## Quick Start TL;DR (Read First - 30 Seconds)
**MANDATORY:**
**Essential Patterns:**
- Always validate inputs
- Use proper test isolation
- Document test intent

## Quick Compliance Checklist
- [ ] Tests are isolated
- [ ] Assertions are clear
- [ ] Documentation is complete

## Validation
- **Success Checks:** All tests pass; coverage >80%
- **Negative Tests:** Error handling verified

## Response Template
```bash
# Run tests
pytest tests/

# Check coverage
pytest --cov=src
```

## References
### External Documentation
- [Testing Documentation](https://example.com/docs)
### Related Rules
- `000-global-core.md`
