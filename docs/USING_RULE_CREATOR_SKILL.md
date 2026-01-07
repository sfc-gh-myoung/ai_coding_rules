# Using the Rule Creator Skill (Internal Only)

**Note:** The Rule Creator Skill is **not deployed** to team projects. It remains in the ai_coding_rules source repository for internal use only.

## Background

The rule-creator skill automates the creation of new Cursor rules following schema standards. It's designed for use within the ai_coding_rules project itself, not for deployment to other projects.

## Why Not Deployed?

The skill is excluded from deployment (configured in `pyproject.toml`) because:
- It's specific to ai_coding_rules project structure
- Requires access to source repository scripts and schemas
- Generates rules for this project, not consuming projects
- Needs write access to rules/ directory and RULES_INDEX.md

## Configuration

Exclusions are managed in [`pyproject.toml`](../pyproject.toml):

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator/",
]
```

To modify exclusions, edit this section in `pyproject.toml`.

## For ai_coding_rules Contributors

If you're contributing to ai_coding_rules and need to create new rules:

### 1. Load the skill in this repository

```
Load skills/rule-creator/SKILL.md
```

### 2. Request rule creation

```
Create a new rule for [TECHNOLOGY] best practices following schema standards
```

**Example:**
```
Create a new rule for React Testing Library best practices following schema standards
```

**With execution timing:**
```
Create a new rule for DaisyUI best practices following schema standards

timing_enabled: true
```

### 3. Follow the 5-phase workflow

The skill will guide you through:
- **Phase 1:** Discovery & Research (searches RULES_INDEX.md, identifies domain)
- **Phase 2:** Template Generation (runs `scripts/template_generator.py`)
- **Phase 3:** Content Population (fills all sections with researched content)
- **Phase 4:** Validation Loop (runs `scripts/schema_validator.py` until 0 CRITICAL errors)
- **Phase 5:** Indexing (adds entry to RULES_INDEX.md)

### 4. Scripts run from this repository

All scripts execute from the ai_coding_rules directory:

```bash
# Template generation
python scripts/template_generator.py 422-daisyui-core --context-tier Medium

# Validation
python scripts/schema_validator.py rules/422-daisyui-core.md
```

The agent will provide the correct commands with proper paths automatically.

## For Deployed Project Teams

If you need to create custom rules in your deployed project:

### Option 1: Use the Source Repository

1. Clone or reference the ai_coding_rules repository
2. Load the skill from the source: `@../ai_coding_rules/skills/rule-creator/SKILL.md`
3. Run scripts from the source repository as shown above

### Option 2: Manual Rule Creation

Follow the manual rule creation workflow:
1. Read `@rules/002a-rule-creation-guide.md` in your deployed rules
2. Copy an existing rule as a template
3. Manually fill all sections
4. Validate structure matches schema

## Examples

Complete workflow examples are available in the structured skill:
- `@skills/rule-creator/examples/frontend-example.md` - DaisyUI (JavaScript)
- `@skills/rule-creator/examples/python-example.md` - pytest-mock
- `@skills/rule-creator/examples/snowflake-example.md` - Hybrid Tables

## Time Savings

Using the skill vs. manual rule creation:
- **Manual:** 45-60 minutes
- **With skill:** 17-23 minutes
- **Savings:** ~60-70% faster

## Support

For detailed documentation:
- **Skill README:** `@skills/rule-creator/README.md`
- **Workflow guides:** `@skills/rule-creator/workflows/*.md`
- **Rule governance:** `@rules/002-rule-governance.md`
- **Schema validation:** `@rules/002d-schema-validator-usage.md`

## FAQ

### Q: Can I deploy the rule-creator skill to my project?

**A:** Not recommended. The skill requires:
- Write access to rules/ directory in source repository
- Access to scripts/template_generator.py and scripts/schema_validator.py
- Access to schemas/rule-schema.yml
- Ability to modify RULES_INDEX.md

These are all specific to the ai_coding_rules project structure.

### Q: How do I add custom skills to deployment?

**A:** Create new skills in `skills/` directory. They will be deployed automatically unless added to the exclusion list in `pyproject.toml`.

### Q: How do I exclude additional skills from deployment?

**A:** Edit `pyproject.toml` and add to the `exclude_skills` list:

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator/",
    "your-internal-skill/",  # Add your exclusion here
]
```

### Q: Can teams create their own rules without this skill?

**A:** Yes! Teams can:
1. Follow manual rule creation guide (`@rules/002a-rule-creation-guide.md`)
2. Reference the source repository and use the skill from there
3. Copy and adapt existing rules as templates

The skill is a productivity tool, not a requirement for rule creation.

