# Using the Rule Creator Skill

**Last Updated:** 2026-03-27

The Rule Creator Skill automates creation of production-ready Cursor rules following schema v3.2 standards. It guides you through research, template generation, content population, validation, and RULES_INDEX.md registration—reducing rule creation time by ~60-70%.

> **Internal Use Only:** This skill is excluded from deployment to consuming projects. See [Deployment Exclusion](#deployment-exclusion) for rationale.

## Examples

### Minimal Required Example

```text
Use the rule-creator skill.

rule_name: 422-daisyui-core          # Required — rule filename (NNN-lowercase-hyphenated)
domain: JavaScript/Frontend           # Required — technology domain
```

### With All Optional Settings

```text
Use the rule-creator skill.

rule_name: 209-python-pytest-security  # Required
domain: Python                         # Required
context_tier: High                     # Optional (default: Medium) — token budget tier
timing_enabled: true                   # Optional (default: false) — track creation duration
```

### With Aspect (Non-Core Rule)

```text
Create a new rule for pytest security testing patterns
```

Creates: `209-python-pytest-security.md` (aspect: "security").

### Multiple Dependencies

```text
Create a new rule for Snowflake+Python integration patterns
```

Agent adds both `rules/100-snowflake-core.md` and `rules/200-python-core.md` to Depends.


## Workflow Phases

| Phase | Name | What Happens |
|-------|------|--------------|
| 1 | **Discovery & Research** | Searches RULES_INDEX.md, identifies domain, checks for duplicates |
| 2 | **Template Generation** | Runs `ai-rules new` with domain and context tier |
| 3 | **Content Population** | Fills all schema sections with researched, domain-specific content |
| 4 | **Validation Loop** | Runs `ai-rules validate` until 0 CRITICAL errors |
| 5 | **Indexing** | Adds entry to RULES_INDEX.md with metadata |

### Phase 1: Discovery & Research

The skill reads RULES_INDEX.md to:
- Check for existing rules covering the same technology
- Identify the correct domain range (000-999 based on technology)
- Gather context from related rules

### Phase 4: Validation Loop

The skill iterates until all CRITICAL errors are resolved:

```text
Iteration 1: 3 CRITICAL, 5 RECOMMENDED
Iteration 2: 1 CRITICAL, 3 RECOMMENDED
Iteration 3: 0 CRITICAL, 2 RECOMMENDED ✓ (passed)
```

RECOMMENDED issues are logged but do not block completion.


## Understanding Your Results

### Verdicts

| Outcome | Criteria | Action |
|---------|----------|--------|
| **PASSED** | 0 CRITICAL errors | Rule is schema-compliant |
| **FAILED** | ≥1 CRITICAL errors after 3 iterations | Manual intervention required |

### Output Artifacts

The skill produces three artifacts:

1. **Rule file:** `rules/<rule-name>.md` — The complete rule document
2. **Index entry:** Line added to `RULES_INDEX.md` — Enables rule-loader discovery
3. **Validation log:** Console output — Shows iteration history

### Validation Gates

All rules must pass these gates before completion:

| Gate | Requirement |
|------|-------------|
| Discovery | RULES_INDEX.md searched, domain identified, number available |
| Template | `ai-rules new` executed, v3.2 sections present |
| Metadata | Keywords (5-20), TokenBudget (~NUMBER), ContextTier valid |
| Contract | 6 Markdown headers present, placed before line 160 |
| Validation | `ai-rules validate` returns exit code 0 |
| Indexing | Entry added to RULES_INDEX.md in correct position |

### Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Keywords count: 3 (expected 5-20)` | Too few keywords | Add more semantic keywords |
| `TokenBudget format invalid` | Missing tilde | Change `1200` to `~1200` |
| `Missing header: ### Validation` | Incomplete Contract | Add all 6 required headers |
| `Contract after line 160` | Contract too late | Move Contract earlier in file |
| `Invalid filename format` | Wrong casing/format | Use `NNN-lowercase-hyphenated` |


## Advanced Usage

### Domain Selection

Rules are numbered by domain range. The skill auto-suggests the next available number.

| Range | Domain | Examples |
|-------|--------|----------|
| 000-099 | Core/Foundational | 000-global-core, 002-rule-governance |
| 100-199 | Snowflake | 100-snowflake-core, 125-hybrid-tables |
| 200-299 | Python | 200-python-core, 209-pytest-mock |
| 300-399 | Shell/Bash | 300-bash-scripting-core |
| 420-449 | JavaScript/Frontend | 420-javascript-core, 422-daisyui-core |
| 600-699 | Golang | 600-golang-core |
| 800-899 | Project Management | 800-project-changelog |
| 900-999 | Demos/Examples | 900-demo-creation |

### Context Tier Options

| Tier | Token Budget | Use Case |
|------|--------------|----------|
| **Critical** | <500 | Always-loaded core rules |
| **High** | 500-1500 | Domain foundations |
| **Medium** | 1500-3000 | Most rules (default) |
| **Low** | 3000-5000 | Specialized/reference |

```text
context_tier: High
```

### Execution Timing

```text
timing_enabled: true
```

Adds timing metadata to track total duration, per-phase breakdown, and validation iterations.

**Timing thresholds:**
- <5 minutes: Warning (possible shortcut)
- 17-23 minutes: Normal range
- >30 minutes: Warning (possible issue)

**Checkpoints tracked:**
- `skill_loaded` → `discovery_complete` → `template_generated` → `content_populated` → `validation_complete` → `indexing_complete`

### Specifying Aspect

For non-core rules, specify aspect:

```text
Create a new rule for pytest security testing patterns
```

Creates: `209-python-pytest-security.md` (aspect: "security")

### Multiple Dependencies

If rule depends on multiple domains:

```text
Create a new rule for Snowflake+Python integration patterns
```

Agent adds both `rules/100-snowflake-core.md` and `rules/200-python-core.md` to Depends.

### Manual CLI Execution

If needed, CLI commands can be run directly:

```bash
ai-rules new 422-daisyui-core --context-tier Medium
ai-rules validate rules/422-daisyui-core.md
```


## FAQ

### How long does rule creation take?

| Method | Duration |
|--------|----------|
| Manual | 45-60 minutes |
| With skill | 17-23 minutes |

**Time savings: ~60-70%**

### What if validation keeps failing?

After 3 iterations, the skill stops and reports remaining errors. Common fixes:
1. Check for missing required sections (Examples, Anti-patterns)
2. Ensure all 6 Contract headers are present
3. Verify keywords are in 5-20 range

### How do I verify the skill executed correctly?

**During execution:** Look for `ai-rules new` output, `ai-rules validate` iterations (multiple), and web research queries.

**After execution:** Verify rule file exists (4000-12000 bytes typical), contains no placeholders ("TODO", "[Add content]"), and `ai-rules validate` returns exit code 0.

**Red flags:**
- Completion in <5 minutes
- File size <3000 bytes
- Contains placeholder markers
- No visible validation iterations

### Can I use this skill in deployed projects?

Not directly. The skill requires:
- Write access to `rules/` directory
- Access to `ai-rules` CLI commands
- Access to `schemas/rule-schema.yml`

**Alternatives:**
1. Clone ai_coding_rules and load skill from source path
2. Follow manual guide: `rules/002a-rule-creation.md`

### Can teams create rules without this skill?

Yes. Teams can:
1. Follow `rules/002a-rule-creation.md`
2. Copy and adapt existing rules as templates
3. Use the skill from the source repository

The skill is a productivity tool, not a requirement.

### What domain should I use for ambiguous technologies?

Check RULES_INDEX.md for similar technologies. If still unclear, ask the user. Example: "React Testing Library" → Frontend (420s) or Testing (200s)?


## Reference

### Architecture

```text
User Request
│
├── Phase 1: Discovery
│   ├── Read RULES_INDEX.md
│   ├── Identify domain range
│   └── Check for duplicates
│
├── Phase 2: Template Generation
│   └── ai-rules new
│
├── Phase 3: Content Population
│   ├── Research via web/docs
│   └── Fill all schema sections
│
├── Phase 4: Validation Loop
│   └── ai-rules validate (max 3 iterations)
│
└── Phase 5: Indexing
    └── Append to RULES_INDEX.md
```

### File Structure

```text
skills/rule-creator/
├── SKILL.md               # Main skill (entrypoint)
├── test_cases.yaml        # Evaluation test cases
├── examples/              # Complete workflow examples
│   ├── frontend-example.md
│   ├── python-example.md
│   ├── snowflake-example.md
│   └── edge-cases.md
├── testing/               # Testing and maintenance
│   └── TESTING.md
├── tests/                 # Skill test cases
└── workflows/             # Step-by-step guides
    ├── discovery.md
    ├── template-gen.md
    ├── content-population.md
    ├── validation.md
    └── indexing.md
```

### CLI Commands

| Command | Purpose |
|---------|---------|
| `ai-rules new` | Creates rule skeleton from domain |
| `ai-rules validate` | Validates against rule-schema.yml |
| `ai-rules index` | Maintains RULES_INDEX.md |

### Integration with Other Skills

| Skill | Relationship |
|-------|--------------|
| **rule-reviewer** | Review created rules for quality |
| **rule-loader** | Load rules by domain/activity match |
| **skill-timing** | Track creation duration metrics |

### Deployment Exclusion

This skill is excluded from deployment via `pyproject.toml`:

```toml
[tool.rule_deployer]
exclude_skills = ["rule-creator/"]
```

**Rationale:** Specific to ai_coding_rules project structure, requires source repository CLI and schemas, generates rules for this project only.

**For deployed project teams:**
1. Clone ai_coding_rules and load skill from source path
2. Follow manual guide: `rules/002a-rule-creation.md`

### Support

- **Skill entrypoint:** `skills/rule-creator/SKILL.md`
- **Workflow guides:** `skills/rule-creator/workflows/*.md`
- **Examples:** `skills/rule-creator/examples/*.md`
- **Rule governance:** `rules/002-rule-governance.md`
- **Schema validation:** `rules/002d-schema-validator-usage.md`
