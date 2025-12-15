# Using the Rule Reviewer Skill

**Note:** The Rule Reviewer Skill is **deployed** to team projects by default (unless
explicitly excluded in `pyproject.toml`).

## Background

The rule-reviewer skill automates running the Agent-Centric Rule Review prompt against
a
target rule file and writing the results to `reviews/` using the required filename
format from `prompts/RULE_REVIEW_PROMPT.md`.

Key behaviors:

- Uses the rubric and required output structure from `prompts/RULE_REVIEW_PROMPT.md`
- Computes `OUTPUT_FILE` as:
  - `reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`
- Writes the full review to `OUTPUT_FILE` (**overwrite** if it already exists)

## Configuration

Skill deployment is managed by the deployer configuration in
[`pyproject.toml`](../pyproject.toml):

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator-skill.md",
    "rule-creator/",
]
```

### Excluding the rule-reviewer skill (optional)

If you want to prevent the rule-reviewer skill from being deployed, add it to
`exclude_skills`:

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator-skill.md",
    "rule-creator/",
    "rule-reviewer-skill.md",
    "rule-reviewer/",
]
```

## For ai_coding_rules Contributors

If you're working in the ai_coding_rules repository and want to run rule reviews:

### 1. Load the skill

**Single-file skill:**

```text
@skills/rule-reviewer-skill.md
```

**Structured skill:**

```text
@skills/rule-reviewer/prompt.md
```

### 2. Request a review

```text
Use the rule-reviewer skill.

target_file: rules/810-project-readme.md
review_date: 2025-12-12
review_mode: FULL
model: claude-sonnet45
```

### 3. Output location

The skill will write (overwrite) the review to:

`reviews/810-project-readme-claude-sonnet45-2025-12-12.md`

## For Deployed Project Teams

If your project has been deployed with `skills/` included, you can use rule-reviewer
directly from your project.

### 1. Confirm skill exists in your project

You should see either (or both):

- `skills/rule-reviewer-skill.md`
- `skills/rule-reviewer/`

### 2. Load the skill

```text
@skills/rule-reviewer/prompt.md
```

### 3. Run a review and write to reviews/

```text
Use the rule-reviewer skill.

target_file: rules/810-project-readme.md
review_date: 2025-12-12
review_mode: STALENESS
model: claude-sonnet45
```

## FAQ

### Q: What happens if the output file already exists?

**A:** The rule-reviewer skill overwrites it.

### Q: What should I pass for `model`?

**A:** Prefer a slug like `claude-sonnet45`. If you provide a raw model name, the
skill will normalize it to a slug before writing the file.

### Q: Does `target_file` have to be under `rules/`?

**A:** The expected use case is reviewing files under `rules/`, but the skill can
review any readable `.md` file path you provide.
The output filename always uses the base filename (without extension) of `target_file`.

### Q: Where does the rubric come from?

**A:** The skill uses `prompts/RULE_REVIEW_PROMPT.md` as the rubric and required
output format and writes the final review to `reviews/`.
