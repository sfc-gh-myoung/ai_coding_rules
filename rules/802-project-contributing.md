# Contribution Workflow

## Metadata

**SchemaVersion:** v3.1
**RuleVersion:** v1.0.0
**Keywords:** CONTRIBUTING, pull requests, code review, contribution guidelines, branching strategy, Conventional Commits, rule authoring, PR templates, project governance, git workflow
**TokenBudget:** ~2800
**ContextTier:** Medium
**Depends:** rules/000-global-core.md

## Purpose
Establish directives for a professional contribution workflow covering commits, pull requests, changelog discipline, and rule authoring standards to ensure consistent project collaboration and quality.

## Rule Scope
Professional contribution workflows for commits, pull requests, and rule authoring standards

## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Conventional Commits** - type(scope): imperative summary
- **Update CHANGELOG** - Add under ## [Unreleased] for user-facing changes
- **Descriptive scopes** - Align with project structure
- **PR templates** - Use issue linking, clear descriptions
- **Code review** - Address all feedback before merge
- **Rule authoring** - Follow 002-rule-governance standards
- **Never use "WIP" subjects** - Write meaningful commit messages

**Pre-Execution Checklist:**
- [ ] Fork repository and create feature branch
- [ ] Development environment set up (Python 3.11+, Task, uv, Ruff)
- [ ] Read CONTRIBUTING.md and understand project conventions
- [ ] Verified rule numbering scheme (if creating new rules)
- [ ] Identified correct scope for conventional commit

> **Investigation Required**
> When applying this rule:
> 1. **Read CONTRIBUTING.md BEFORE making changes** - Understand current workflow and standards
> 2. **Check existing rule structure** - Verify numbering scheme, inspect similar rules
> 3. **Never assume project conventions** - Read 002-rule-governance.md for actual standards
> 4. **Verify tool availability** - Check Taskfile.yml for available commands, don't invent tasks
> 5. **Validate before committing** - Run task rules:validate, never skip validation
>
> **Anti-Pattern:**
> "I'll add a new rule as 150-new-feature.md (without checking if 150 range is appropriate)"
> "Updating deployed rules without validation"
>
> **Correct Pattern:**
> "Let me check the rule numbering scheme in 002-rule-governance.md first."
> [reads governance, identifies correct range]
> "I see 100-199 is for Snowflake. I'll use next available number in that range and edit rules/"

## Contract

<contract>
<inputs_prereqs>
- Forked repository with feature branch
- Development environment set up (Python 3.11+, Task, uv, Ruff)
- Understanding of rule numbering scheme and governance standards
- Access to CONTRIBUTING.md and 002-rule-governance.md
</inputs_prereqs>

<mandatory>
- Git (fork, clone, branch, commit, PR)
- Task runner (lint, format, validate, generate)
- Ruff (linting and formatting)
- uv (package management)
- Python validation scripts
</mandatory>

<forbidden>
- Direct editing of deployed rule files outside rules/ directory
- Committing without validation (task rules:validate)
- Force push to main/master branches
- Amending commits authored by others
</forbidden>

<steps>
1. Fork repository and create feature branch following naming conventions
2. Edit rules/ directory files directly (production-ready rules)
3. Follow Conventional Commits format for all commit messages
4. Update CHANGELOG.md under ## [Unreleased] for user-facing changes
5. Validate with task rules:validate and task lint
6. Submit PR with descriptive title and complete description
7. Address all code review feedback before merge
</steps>

<output_format>
- Well-structured pull request with:
- Conventional Commit title
- Clear description of changes and motivation
- Links to related issues
- Validation checklist completed
- Before/after examples (if applicable)
</output_format>

<validation>
- task rules:validate passes without critical errors
- task lint passes cleanly
- task format passes without changes
- CHANGELOG.md updated (if user-facing change)
- All commits follow Conventional Commits format
- Generated files included in PR (task rule:all run)
</validation>

</contract>

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Editing Deployed Rules Without Validation**
```bash
# Bad: Direct edit without validation
vim /some/project/.cursor/rules/100-snowflake-core.md
git add /some/project/.cursor/rules/100-snowflake-core.md
```
**Problem:** Changes to deployed rules should be made in source rules/ directory, not in deployment locations.

**Correct Pattern:**
```bash
# Good: Edit source rules
vim rules/100-snowflake-core.md
task rules:validate  # Validate changes
git add rules/100-snowflake-core.md
```
**Benefits:** Changes in canonical source location, validated before deployment


**Anti-Pattern 2: Vague Commit Messages**
```bash
# Bad: No context or type
git commit -m "updated stuff"
git commit -m "WIP"
git commit -m "fixed bug"
```
**Problem:** Unclear change type, no scope, breaks changelog automation, unhelpful for code review

**Correct Pattern:**
```bash
# Good: Conventional Commits with clear scope
git commit -m "feat(snowflake): add Snowpipe continuous ingestion patterns"
git commit -m "fix(python): correct FastAPI async route examples"
git commit -m "docs(readme): update Quick Start with dual-platform git clone"
```
**Benefits:** Clear change type, automated changelog generation, searchable commit history


**Anti-Pattern 3: Skipping Validation**
```bash
# Bad: Commit without validation
git add rules/new-rule.md
git commit -m "feat(rule): add new rule"
git push
```
**Problem:** May contain structural errors, invalid metadata, broken references, fails CI checks

**Correct Pattern:**
```bash
# Good: Validate before commit
vim rules/new-rule.md
task rules:validate  # Ensure compliance
task lint           # Check code quality
git add rules/new-rule.md
git commit -m "feat(rule): add new rule"
```
**Benefits:** Catch errors early, ensure governance compliance, pass CI checks


**Anti-Pattern 4: Mixing User and Contributor Content in README**
```markdown
# Bad: Detailed development commands in README
```
**Problem:** README should focus on users, not development setup
**Correct Pattern:** Move development setup, build instructions, and contributor guidelines to CONTRIBUTING.md


## Post-Execution Checklist
- [ ] Required dependencies and context verified
- [ ] Appropriate tools selected and validated
- [ ] Implementation follows established patterns
- [ ] Output format matches requirements
- [ ] Validation steps completed successfully

## Validation
- **Success checks:** [How to verify correct implementation]
- **Negative tests:** [What should fail and how to detect failures]

## Output Format Examples

```markdown
MODE: ACT

Investigation:
- Read CONTRIBUTING.md to understand workflow
- Checked rule numbering scheme in 002-rule-governance.md
- Verified 200-299 range is for Python rules
- Identified next available number: 215

Implementation:

Created new rule: rules/215-python-django-core.md

File Structure:
- Metadata: Description, Type, AppliesTo, Keywords, TokenBudget (~2200)
- Quick Start TL;DR with 7 essential patterns
- 5 detailed sections covering Django best practices
- Anti-patterns section with 3 examples
- Investigation-First Protocol
- Response Template

Updated CHANGELOG.md:
```markdown

## References

### External Documentation
- [GitHub Contributing Guidelines](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/setting-guidelines-for-repository-contributors) - GitHub's guide for contribution workflows
- [Open Source Guides](https://opensource.guide/) - Best practices for open source project management
- [Conventional Commits](https://www.conventionalcommits.org/) - Standardized commit message format

### Related Rules
- **Global Core**: `rules/000-global-core.md`
- **Changelog Rules**: `rules/800-project-changelog.md`
- **README Rules**: `rules/801-project-readme.md`
- **Rules Governance**: `rules/002-rule-governance.md`

## 1. Commit & Changelog Discipline
- **Requirement:** Follow Conventional Commits: `<type>(<scope>): <imperative summary>`.
- **Requirement:** Valid types: `feat`, `fix`, `perf`, `refactor`, `style`, `docs`, `chore`, `build`, `ci`, `test`.
- **Requirement:** Use descriptive scopes aligned with rule categories:
  - Core: `core`, `governance`, `memory-bank`
  - Snowflake: `snowflake`, `sql`, `streamlit`, `spcs`
  - Python: `python`, `fastapi`, `lint`, `setup`
  - Shell: `bash`, `zsh`, `shell`
  - Project: `changelog`, `readme`, `contributing`, `taskfile`
  - Analytics: `data-science`, `governance`, `business`
- **Always:** After user-facing changes, update `CHANGELOG.md` under `## [Unreleased]`.
- **Requirement:** Each changelog entry is a single concise line; collapse micro-fixes.
- **Requirement:** Avoid anti-patterns: "WIP" subjects, unscoped types for multi-domain changes, mixing features and fixes.

## 2. Rule Authoring Standards

### Rule File Structure
- **Requirement:** Follow 3-digit numbering scheme with clear domain separation:
  - `000-099`: Core Foundation (global, memory-bank, governance)
  - `100-199`: Data Platform - Snowflake
  - `200-299`: Software Engineering - Python
  - `300-399`: Software Engineering - Shell Scripts
  - `500-599`: Data Science & Analytics
  - `600-699`: Data Governance
  - `700-799`: Business Intelligence
  - `800-899`: Project Management
  - `900-999`: Demo & Synthetic Data

### Rule Content Guidelines
- **Requirement:** Keep rules focused and concise (target 150-300 lines; max 500 lines).
- **Requirement:** Split large topics into multiple composable rules within the same range.
- **Requirement:** Use explicit directive language: `Requirement`, `Always`, `Avoid`, `Rule`, `Consider`.
- **Always:** Include metadata header with Description, AppliesTo, AutoAttach, Type, Version, LastUpdated.
- **Always:** Reference related rules using `@rule-name.md` syntax.

### Subdomain Organization
- **Rule:** Use 10-number ranges for framework-specific rules:
  - Python FastAPI: `210-219`
  - Bash Scripting: `300-309`
  - Zsh Scripting: `310-319`
- **Rule:** Use 20-number jumps for major feature areas (e.g., `120` for Snowflake SPCS).

## 3. General Code Standards
- **Requirement:** SQL must use uppercase keywords and explicit identifiers (avoid `SELECT *`).
- **Requirement:** Shell scripts must include proper shebang and error handling (`set -euo pipefail`).
- **Always:** New behavior should include at least one happy-path test and one negative/edge case test.
- **Requirement:** Test function names follow `test_<function>_when_<condition>_should_<result>`.
- **Always:** Reference specialized rules as needed (e.g., `200-python-core.md`, `300-bash-scripting-core.md`).

## Contributing
[50 lines of detailed development workflow]
[Environment setup instructions]
[Rule generation commands]
[Validation procedures]
```
**Problem:** Overwhelms end users, violates progressive disclosure principle, creates maintenance burden

**Correct Pattern:**
```markdown
# Good: Minimal pointer in README

## README vs CONTRIBUTING.md Content Boundaries

**Principle:** Progressive disclosure - users first, contributors second

**README.md Should Contain:**
- Project overview and value proposition
- Quick Start for end users
- Installation and usage instructions
- Troubleshooting for users
- Minimal contributor pointer with quick reference commands
- License and acknowledgments

**CONTRIBUTING.md Should Contain:**
- Complete development workflow
- Environment setup details
- Code quality and linting procedures
- Rule authoring standards
- PR templates and review process
- Configuration safety guidelines
- Testing requirements
- Validation procedures

**Boundary Pattern:**
```markdown

## Dual-Platform Repository Support

**Requirement:** Projects hosted on multiple platforms must document both in CONTRIBUTING.md

**Quick Start Section Pattern:**
```markdown

## 4. Pull Requests & Branching
- **Requirement:** PR titles must follow Conventional Commits.
- **Requirement:** PRs must contain delta-only edits; avoid unrelated formatting.
- **Always:** For multi-user projects, submit PRs to a protected `main` branch.
- **Rule:** When adding new rules, update README.md to reflect the new structure.
- **Rule:** When modifying rule numbering, ensure all cross-references are updated.

## 5. Rule Categories and Examples

### Current Rule Structure

**Core Foundation (000-099):**
- `000-global-core.md`
- `001-memory-bank.md`
- `002-rule-governance.md`

**Snowflake (100-199):**
- 100-109: Core Snowflake
- 110-119: [Reserved]
- 120-129: Snowpark Container Services

**Python (200-299):**
- 200-209: Core Python
- 210-219: FastAPI Framework

**Shell Scripts (300-399):**
- 300-309: Bash Scripting
- 310-319: Zsh Scripting

**Analytics & Data (500-699):**
- 500-599: Data Science
- 600-699: Data Governance

**Business & Project (700-899):**
- 700-799: Business Intelligence
- 800-899: Project Management

**Demo & Templates (900-999):**
- 900-999: Demo Creation

### Adding New Rules
- **Rule:** Choose appropriate number range based on domain
- **Rule:** Use next available number in sequence within the range
- **Rule:** For new frameworks, reserve 10-number subrange (e.g., 220-229 for Django)
- **Always:** Update README.md rule categories section
- **Always:** Validate rule follows governance standards in `002-rule-governance.md`

## 6. Documentation References
- **Always:** Reference Conventional Commits: https://www.conventionalcommits.org/en/v1.0.0/#specification
- **Always:** Follow rule governance: `002-rule-governance.md`
- **Always:** Use README standards: `801-project-readme.md`
- **Always:** Follow changelog discipline: `800-project-changelog.md`

## [Unreleased]
### Added
- New rule 215-python-django-core.md for Django framework patterns
```

Regenerated all formats:
```bash
task rule:all
[PASS] Generated universal format
[PASS] Generated cursor format
[PASS] Generated copilot format
[PASS] Generated cline format
```

Validation:
```bash
task rules:validate
[PASS] All rules pass structural validation
[PASS] Metadata complete and valid
[PASS] No emoji usage detected
[PASS] Section structure compliant

task lint
[PASS] No linting issues found

task format
[PASS] Formatting is correct
```

Commit:
```bash
git add rules/215-python-django-core.md
git add CHANGELOG.md
git commit -m "$(cat <<'EOF'
feat(python): add Django framework core patterns rule

- Add comprehensive Django best practices rule (215)
- Cover models, views, templates, forms, admin
- Include ORM optimization patterns
- Add security guidelines (CSRF, XSS, SQL injection)
- Reference existing Python rules (200, 201, 206)

Closes #123
EOF
)"
```

Pull Request:
- Title: feat(python): add Django framework core patterns rule
- Description:
  - Addresses #123 - need for Django-specific guidance
  - Provides comprehensive patterns for Django development
  - Follows 002-rule-governance.md v5.0 structure
  - Includes anti-patterns and investigation protocol
- Validation checklist: All items completed [PASS]
```
