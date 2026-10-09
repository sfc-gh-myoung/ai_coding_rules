---
schema_version: v4.0
rule_version: v5.0.0
description: "Clear, enforceable standards for Python documentation, source code comments, and docstrings aligned with PEP 257 and modern tooling (Ruff pydocstyle, Sphinx Napoleon). Covers Google and NumPy styles,"
last_updated: 2026-10-06
keywords:
  - kw:docstring conventions
  - kw:PEP 257
  - kw:Google style docstrings
  - kw:NumPy style docstrings
  - kw:Ruff pydocstyle
  - kw:side effects documentation
token_budget: ~900
context_tier: High
depends:
  required:
    - 200-python-core.md  # Python foundation patterns
    - 201-python-lint-format.md  # Ruff configuration and linting
---
# Python Documentation, Comments, and Docstrings

## Scope

**What This Rule Covers:**
PEP257-compatible docstrings, public API contracts, useful comments, style consistency and documented side effects/concurrency.

**When to Load This Rule:**
When writing/reviewing Python API documentation or configuring docstring checks and generated documentation.

## Contract

### Inputs and Prerequisites

- Existing public signatures/behavior/tests and project Google/NumPy docstring convention.
- Actual Ruff/pydocstyle/Sphinx configuration and authorized edit scope.

### Mandatory

- Use one established Google or NumPy convention; public modules/classes/functions/methods need meaningful documentation subject to justified project/generated-code exemptions.
- Follow a concise imperative summary, blank line then needed details. Do not pad every trivial function with five mandatory sections.
- Document argument meaning, constraints/units, return semantics, exceptions, preconditions and externally visible behavior not already clear from types.
- Document file/network/database/subprocess/state effects, resource lifecycle and concurrency guarantees. Performance statements require measurement/known complexity, not invented timings.
- Class documentation explains abstraction, construction/lifecycle and relevant attributes; follow configured initializer convention. Ruff does not universally infer D107 exemption merely from a class docstring.
- Abstract contracts require documentation; properties document at getter, overrides inherit only when behavior truly unchanged. Generated code uses reviewed config exemptions, not manual edits overwritten by regeneration.
- Comments explain why, business constraints, non-obvious invariants and warnings. Do not restate obvious syntax or keep commented-out obsolete code; update comments when behavior changes.
- Preserve literal API identifiers and actual errors. No illustrative admin bypass, unverified incident/CVE reference or overwrite-without-warning example presented as best practice.
- Configure agreed D rules/convention without replacing other lint selections. Specific suppressions need reason; passing lint does not prove docstring truthfulness.

### Execution Steps

1. Read source, callers/tests and current docstring/tool convention.
2. Update affected public contracts and meaningful comments to match actual signatures/behavior and side effects.
3. Review class/initializer/property/override/generated-code policies under installed tool configuration.
4. Run configured lint, syntax and relevant documentation/example tests; inspect semantics manually.
5. Report tested/unverified claims and update user-facing docs where API behavior changed.

### Validation

- Signature names, constraints, units, returns/exceptions and effects match implementation.
- Public contract documentation meaningful without redundant type/narrative padding.
- Concurrency/lifecycle/performance claims evidenced; secrets absent.
- Project D rules/convention and generated-doc build pass when applicable.
- Comments useful/current and suppressions narrowly justified; no false semantic certification from lint.

## References

- [PEP257](https://peps.python.org/pep-0257/)
- [Google Python documentation style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [NumPy docstrings](https://numpydoc.readthedocs.io/en/latest/format.html)
- [Sphinx Napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html)
- [Ruff pydocstyle rules](https://docs.astral.sh/ruff/rules/)
