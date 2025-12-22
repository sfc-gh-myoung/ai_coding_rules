# Using the Rule Reviewer Skill (Internal Only)

**Note:** The Rule Reviewer Skill is **not deployed** to team projects. It remains in the ai_coding_rules source repository for internal use only.

## Background

The rule-reviewer skill automates running the Agent-Centric Rule Review prompt against
a target rule file and writing the results to `reviews/` using the required filename
format from `skills/rule-reviewer/PROMPT.md`.

Key behaviors:

- Uses the rubric and required output structure from `skills/rule-reviewer/PROMPT.md`
- **100-point scoring system** with weighted dimensions (Actionability 25, Completeness 25, Consistency 15, Parsability 15, Token Efficiency 10, Staleness 10)
- **Priority Compliance Gate** — Evaluates rules against Design Priority Hierarchy before scoring
- **Agent Execution Test** — First gate counts blocking issues (undefined thresholds, missing branches, ambiguous actions)
- Computes `OUTPUT_FILE` as:
  - `reviews/<rule-name>-<model>-<YYYY-MM-DD>.md`
- **No-overwrite safety:** If file exists, uses suffix `-01.md`, `-02.md`, etc.
- Supports three review modes: FULL, FOCUSED, STALENESS

## Design Priority Hierarchy

Reviews evaluate rules against the priority order defined in `000-global-core.md`:

1. **Priority 1:** Agent Understanding and Execution Reliability (CRITICAL)
2. **Priority 2:** Token and Context Window Efficiency (HIGH)
3. **Priority 3:** Human Readability (TERTIARY)

**Scoring Impact:**
- 3-5 Priority 1 violations: Actionability capped at 15/25 (3/5)
- 6+ Priority 1 violations: Overall score capped at 60/100 (NEEDS_REFINEMENT)

## Why Not Deployed?

The rule-reviewer skill is designed for **rule maintainers** working in the source
ai_coding_rules repository. It:

1. **Requires the rubric prompt** — `skills/rule-reviewer/PROMPT.md` (colocated with skill)
2. **Writes to reviews/** — A directory structure specific to rule maintenance
3. **Targets rule files** — Most useful for rule authors validating their work

For deployed projects, teams should reference the skill's `PROMPT.md` directly if they need to review rules.

## Configuration

Both skills are excluded from deployment in [`pyproject.toml`](../pyproject.toml):

```toml
[tool.rule_deployer]
exclude_skills = [
    "rule-creator/",
    "rule-reviewer/",
]
```

## For ai_coding_rules Contributors

If you're working in the ai_coding_rules repository and want to run rule reviews:

### 1. Load the skill

```text
@skills/rule-reviewer/SKILL.md
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

The skill will write the review to:

`reviews/810-project-readme-claude-sonnet45-2025-12-12.md`

If the file already exists, it uses suffixes: `-01.md`, `-02.md`, etc.

## FAQ

### Q: What happens if the output file already exists?

**A:** The rule-reviewer skill uses no-overwrite safety. It appends suffixes (`-01.md`, `-02.md`, etc.) to avoid overwriting existing reviews.

### Q: What should I pass for `model`?

**A:** Prefer a slug like `claude-sonnet45`. If you provide a raw model name, the
skill will normalize it to a slug before writing the file.

### Q: Does `target_file` have to be under `rules/`?

**A:** The expected use case is reviewing files under `rules/`, but the skill can
review any readable `.md` file path you provide.
The output filename always uses the base filename (without extension) of `target_file`.

### Q: Where does the rubric come from?

**A:** The skill uses `skills/rule-reviewer/PROMPT.md` as the rubric and required
output format and writes the final review to `reviews/`.

### Q: Can I use rule-reviewer in a deployed project?

**A:** No, this skill is internal-only. For deployed projects, reference the
skill's `PROMPT.md` directly for the review rubric.
