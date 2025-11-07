**Keywords:** Python docstrings, documentation, comments, pydocstyle, Ruff DOC rules, API documentation, Google style, NumPy style, PEP 257
**TokenBudget:** ~1800
**ContextTier:** Medium
**Depends:** 200-python-core, 201-python-lint-format

# Python Documentation, Comments, and Docstrings

## Purpose
Provide clear, enforceable standards for Python documentation (project docs), source code comments, and docstrings, aligned with widely accepted industry practices (PEP 257, PEP 8) and modern tooling (Ruff pydocstyle, Sphinx Napoleon).

## Rule Type and Scope

- **Type:** Agent Requested
- **Scope:** Python comments, docstrings, and developer-facing documentation across libraries, apps, CLIs, and services

## Quick Start TL;DR (Read First - 30 Seconds)

**MANDATORY:**
**Essential Patterns:**
- **Choose ONE docstring style** - Google (recommended) or NumPy, configure in pyproject.toml
- **All public APIs need docstrings** - Modules, classes, functions, methods
- **Enable Ruff D rules** - `select = ["D"]` in [tool.ruff.lint]
- **Use comments for "why"** - Not "what" (code shows what)
- **Follow PEP 257** - One-line summary, then blank line, then details
- **Never mix docstring styles** - Consistency across entire project

**Quick Checklist:**
- [ ] pyproject.toml has `[tool.ruff.lint.pydocstyle]` with convention
- [ ] All public functions have docstrings
- [ ] All classes have docstrings
- [ ] Docstrings start with one-line summary
- [ ] Args, Returns, Raises documented
- [ ] `uvx ruff check .` passes D rules
- [ ] Comments explain "why", not "what"

## Contract
- **Inputs/Prereqs:** Python 3.11+; `pyproject.toml`; Ruff; optional Sphinx with Napoleon
- **Allowed Tools:** `uvx ruff` for lint/format; `uv run` for project execution; Sphinx for docs
- **Forbidden Tools:** Inconsistent, project-specific ad-hoc styles without configuration
- **Required Steps:**
  1. Choose one docstring style for the repo: Google (recommended) or NumPy
  2. Configure Ruff pydocstyle rules and convention
  3. Add and maintain docstrings for all public modules/classes/functions/methods
  4. Use comments to explain "why" and intent; avoid restating code
  5. Prevent and fix common mistakes via lint and review
- **Output Format:** Docstrings and comments following requirements below; updated `pyproject.toml` config
- **Validation Steps:** `uvx ruff check .` passes with D-rules; docs build (if applicable) succeeds

## Key Principles
- Prefer Google-style docstrings with Sphinx Napoleon (or NumPy if already established)
- Follow PEP 257 for structure and placement; PEP 8 for comment style
- Document behavior, constraints, side-effects, exceptions, and units over implementation
- Use type hints; do not duplicate types in docstrings
- Keep comments high-signal: explain intent and trade-offs

## 1. Docstring Standards (PEP 257 + Google/NumPy)
- **Requirement:** Use triple double-quotes for all docstrings. First line is a concise imperative summary ending with a period.
- **Requirement:** For multi-line docstrings, include a blank line after the summary, then details.
- **Requirement:** Maintain a single consistent style across the repo: Google (recommended) or NumPy.
- **Requirement:** Provide docstrings for all public modules, packages, classes, functions, and methods.
- **Rule:** Private helpers may omit docstrings if trivially obvious; otherwise document rationale and behavior.
- **Requirement:** Do not duplicate type annotations in docstrings; focus on semantics, constraints, and units.
- **Requirement:** Document non-trivial exceptions in a `Raises` section; document side-effects (I/O, logging, network, global state).
- **Requirement:** Place module docstrings as the first statement in the file. Describe purpose, public APIs, environment variables, and notable side-effects.
- **Rule:** Property docstrings should describe the attribute (not "Get X").

### 1.1 Google-style Examples
```python
def fetch_user(user_id: str, include_roles: bool = False) -> User:
    """Fetch user by identifier.

    Args:
      user_id: Stable user identifier (UUID string).
      include_roles: When true, also loads role memberships.

    Returns:
      User: Hydrated user object. If `include_roles` is true, roles are populated.

    Raises:
      UserNotFoundError: If the user_id does not exist.
      PermissionError: If the caller lacks access to this user.

    """


class RateLimiter:
    """Token-bucket rate limiter.

    Controls request throughput using a token bucket with burst capacity.
    Thread-safe for concurrent callers.
    """


"""Payment processing integration.

Exposes public entry points for charge and refund workflows.
Reads API keys from environment variables. Emits audit logs to `payments_audit`.
"""
```

## 2. Comment Standards (PEP 8)
- **Requirement:** Comments must explain intent, rationale, and trade-offs—the "why"—not restate the code.
- **Requirement:** Place block comments above the code they describe; keep inline comments short and sparing.
- **Requirement:** Remove commented-out code. Use version control or link to issues instead.
- **Rule:** Prefer references to requirements or tickets over long narrative comments.
- **Rule:** Keep comments up to date; when behavior changes, update adjacent comments/docstrings.

## 3. Project Documentation (Optional)
- **Rule:** If publishing developer docs, use Sphinx with Napoleon to parse Google/NumPy docstrings.
- **Rule:** Consider AutoAPI/Autodoc to generate API docs from code; use Intersphinx for cross-project links.
- **Consider:** Add a `docs/` folder with a minimal Sphinx configuration and CI job to build docs on PRs.

## 4. Enforcement with Ruff (pydocstyle)
- **Requirement:** Enable pydocstyle (D) rules in Ruff and set a single convention.

Example `pyproject.toml` snippet:
```toml
[tool.ruff]
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "D"]
ignore = []

[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy"
```

## 5. Common Mistakes & How to Prevent Them
- **Missing docstrings on public APIs** → Enforce D-rules; PRs must add docstrings.
- **Parameter lists out of sync with signatures** → CI lint must fail; reviewers verify.
- **Duplicated types in docstrings when hints exist** → Remove types; describe semantics/units.
- **Undocumented exceptions and side-effects** → Add `Raises` and explicit side-effect notes.
- **No blank line after summary** → Enforce PEP 257 via Ruff.
- **Module docstrings not first** → Enforce placement; move to top.
- **Inconsistent styles** → Pick one project-wide style; document in README.
- **Commenting “what” or leaving dead code** → Remove; write "why" or link to issues.

## Quick Compliance Checklist
- [ ] One docstring style chosen and configured (Google/NumPy)
- [ ] Ruff D-rules enabled with correct convention
- [ ] Public APIs have docstrings with summaries and details
- [ ] Exceptions, side-effects, and units documented where applicable
- [ ] No duplicated types in docstrings when type hints exist
- [ ] Comments explain intent; no commented-out code remains
- [ ] Optional docs build (Sphinx+Napoleon) succeeds

## Validation
- **Lint:** `uvx ruff check .` must pass, including D-rules
- **Format:** `uvx ruff format --check .` passes
- **Docs (optional):** `sphinx-build -b html docs/ docs/_build/html` completes without errors

> **Investigation Required**  
> When applying this rule:
> 1. **Read pyproject.toml BEFORE adding docstrings** - Check if pydocstyle convention is already set
> 2. **Check existing docstring style** - Read a few functions/classes to see Google vs NumPy
> 3. **Never assume docstring format** - Match project's existing convention
> 4. **Verify Ruff D rules enabled** - Check [tool.ruff.lint] select field
> 5. **Read module docstrings** - Understand project's documentation standards
>
> **Anti-Pattern:**
> "Adding Google-style docstrings... (without checking existing style)"
> "Here's the documentation... (without matching project convention)"
>
> **Correct Pattern:**
> "Let me check your existing docstring style first."
> [reads files, checks pyproject.toml pydocstyle config]
> "I see you use Google-style docstrings. Adding documentation following this convention..."

## Response Template
```markdown
## Python Docs & Comments Plan
- Style: Google | NumPy
- Ruff: select includes D; convention set to style
- Scope: Public APIs fully documented; comments updated for intent

## Changes
- Update pyproject ruff config
- Add/repair docstrings
- Remove commented-out code
```

## References
- PEP 257 Docstring Conventions: https://peps.python.org/pep-0257/
- PEP 8 (Comments): https://peps.python.org/pep-0008/#comments
- Ruff pydocstyle rules (D): https://docs.astral.sh/ruff/rules/#pydocstyle-d
- Sphinx Napoleon: https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html


