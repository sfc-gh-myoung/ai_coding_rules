---
schema_version: v4.0
rule_version: v5.0.0
description: "Author and validate skills with clear discovery, input and output contracts, progressive disclosure, safe tool use, and representative evaluations."
last_updated: 2026-09-30
keywords:
- kw:SKILL.md authoring
- kw:YAML frontmatter
- kw:progressive disclosure
- kw:trigger keywords
- kw:input output contracts
- kw:third person description
- kw:skill
- kw:claude code skill
- dir:skills/
token_budget: ~1450
context_tier: High
depends:
  required:
  - 000-global-core.md
  - 002-rule-governance.md
  optional:
  - 002a-rule-creation.md
  - 002d-advanced-rule-patterns.md
---
# Skill Authoring Practices

> **FOUNDATION RULE: PRESERVE WHEN POSSIBLE**
>
> Load when authoring or maintaining skills.

## Scope

**What This Rule Covers:**
Design skills with discoverable descriptions, executable contracts, focused references, and validation evidence. Skills and operational rules both use YAML frontmatter but follow different schemas.

**When to Load This Rule:**
- Create or review a SKILL.md, its workflows, examples, or tests.
- Verify the intended host's current skill specification when portability or platform-specific fields matter.

## Contract

### Inputs and Prerequisites

- A defined workflow, target host, representative requests, and authorized output locations.
- Read `schemas/skill-schema.yml`, nearby skills, and the host specification before assuming supported fields or tools.
- Identify required runtime packages, tools, permissions, and offline constraints.

### Mandatory

- Give the skill a specific lowercase kebab-case name and a description that says what it does and when to use it. Prefer third-person active wording and real user phrases; add exclusions for likely false activations.
- Include the project's required `name`, `description`, and semantic `version` fields. Distinguish repository extensions from host requirements; do not assume every host accepts the same metadata.
- Define required inputs, optional inputs with defaults, accepted formats, output paths, overwrite behavior, and completion evidence.
- Validate inputs before side effects. Never overwrite an existing artifact without authorization; use the documented no-overwrite naming rule when creating new reports.
- Keep essential permissions, safety constraints, and stop conditions in SKILL.md. Load detailed workflows and examples only when needed, with explicit relative paths and load conditions.
- Keep SKILL.md within the project's 500-line check and verify all local references. Do not split essential prerequisites into an optional file solely to meet a size cap.
- Resolve tool names from the current runtime registry. Use fully qualified MCP names when required by that host; do not invent a universal separator or assume a server is available.
- List dependencies and verify availability. Provide approved setup instructions or report the workflow blocked; do not assume runtime network access or install packages silently.
- Test valid inputs, invalid inputs, missing resources, and discovery exclusions. Test intended models before claiming support; paid/live evaluation requires authorization.
- Show correct runnable examples only, with prerequisites and expected outcomes. Do not fabricate evaluation results.

### Execution Steps

1. Inspect existing skills and determine whether to extend an owner or create a new skill. Define the missing behavior and representative evaluation scenarios first.
2. Create the approved skill directory and SKILL.md with frontmatter, Purpose, Use this skill when, Inputs, Outputs, and Workflow guidance.
3. Add only needed scripts, references, workflows, examples, tests, or assets. Keep references shallow and name the condition for each read.
4. Validate required inputs, tools, and dependencies before execution. Choose a default approach and describe alternatives only with concrete selection conditions.
5. Run structural validation and representative workflow tests. Inspect actual navigation and discovery to identify missed or unnecessary reference reads.
6. Update the skill version and matching CHANGELOG.md entry. Report artifact paths, executed checks, and unsupported environments without publishing unless authorized.

### Validation

- [ ] The project's required metadata parses and matches the target host's supported format.
- [ ] Description distinguishes intended requests from related out-of-scope requests.
- [ ] Inputs, defaults, output paths, overwrite policy, and side-effect authorization are explicit.
- [ ] Every referenced local file exists; scripts and packages are available in the tested environment.
- [ ] `uv run ai-rules validate-skills skills/` passes, including size and version/changelog checks.
- [ ] Representative valid and invalid cases produce their expected results; absent tools or files fail clearly before writes.
- [ ] Required safety instructions remain active; only task-specific detail is deferred.
- [ ] Model/host support claims match actual tests and disclose untested cases.

If YAML fails, fix syntax and field types before running the workflow. If discovery fails, test the request against the description rather than adding generic terms indiscriminately. If a tool is missing, report the exact tool and environment limitation. Re-read concurrent edits and ask about conflicting intent instead of choosing the more specific-looking description automatically.

## References

- `schemas/skill-schema.yml`: repository metadata, headings, size, links, and changelog checks.
- [Agent Skills specification](https://agentskills.io/specification): portable skill format; verify host extensions separately.
- [Claude Code skills](https://code.claude.com/docs/en/skills): Claude Code discovery and host-specific configuration.
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices): progressive disclosure and evaluation guidance.
- `002l-skill-advanced-patterns.md`: load for multi-phase validation, visual analysis, or orchestration workflows.

## Organization and versioning

Use SKILL.md as the entrypoint. Optional directories are `scripts/`, `references/`, `workflows/`, `rubrics/`, `examples/`, `tests/`, and `assets/`; create only what the workflow uses. Use `tests/`, not a second `testing/` tree, and forward slashes in relative references.

Keep version history in the skill's CHANGELOG.md and link to it from SKILL.md. A breaking input or workflow change is MAJOR, an additive capability is MINOR, and a non-functional correction is PATCH. Add the matching changelog entry with the version update.

Use canonical section names without decorative suffixes. `## Outputs` is the repository convention even for one artifact, not a universal upstream requirement. Keep host limits and time-sensitive compatibility claims tied to the current specification instead of stale prose.

## Evaluation evidence

Record baseline behavior before substantial new instructions, then evaluate the candidate on the same representative requests. Include intended discovery, irrelevant requests, invalid inputs, unavailable tools, and protected side effects as applicable. Inspect actual tool and file reads; keyword plausibility alone does not prove runtime discovery.

Report which hosts and models ran, what failed, and what remains untested. Use small deterministic scripts for repeatable transformations when appropriate; do not add an elaborate evaluation framework to a simple skill.
