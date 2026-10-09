---
schema_version: v4.0
rule_version: v3.0.0
description: "Writing standards for human-facing project documentation - voice, tone, sentence structure, capitalization, punctuation, inclusive language, list conventions, code sample presentation, link text, and"
last_updated: 2026-10-06
keywords:
  - kw:technical writing style
  - kw:sentence case headings
  - kw:inclusive language
  - kw:active voice prose
  - kw:fenced code block language identifier
  - kw:descriptive link text
token_budget: ~1000
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation rule with core patterns
  optional:
    - 801-project-readme.md  # README-specific structure and required sections
    - 804-project-documentation.md  # docs/ folder organization
    - 002g-agent-optimization.md  # Contrasting audience: rule files for agents
---
# Technical Writing Style for Human-Facing Documentation

## Scope

**What This Rule Covers:**
Clear, inclusive and accessible prose, headings, lists, code samples and links for human readers.

**When to Load This Rule:**
When writing README, CONTRIBUTING, guides, ADRs or other human-facing documentation. Rule files use agent-first governance; CHANGELOG follows its own change-history format.

## Contract

### Inputs and Prerequisites

- Document audience/type, existing style and verified product behavior.
- Project Markdown lint configuration and relevant accessibility requirements.

### Mandatory

- Write as a knowledgeable colleague: direct, respectful, concrete, concise and present tense. Use second person for reader instructions, active voice with an explicit actor.
- Passive voice is acceptable to emphasize the object or when actor is irrelevant/unknown; do not let it obscure responsibility in procedures.
- Use sentence-case headings/UI labels while preserving product/proper-noun casing. Maintain contiguous semantic heading hierarchy.
- Put conditions before instructions and use short sentences with parallel list/heading structure. Remove filler, unsupported ease/speed claims, slang, idioms and exclamation marks.
- Use serial commas, one space after punctuation, periods for full-sentence list items and no end punctuation for short labels/headings. Follow established punctuation style rather than introducing decorative separators.
- Use singular they and neutral role terms for generic people; respect actual people's pronouns. Prefer primary/replica, allowlist/blocklist and perimeter network terminology where those accurately express meaning; do not rename literal API/config identifiers and break functionality.
- Use numbered lists for ordered actions, bullets for unordered collections and tables only for genuine tabular relationships. Introduce lists/code with a clear lead-in.
- Every fenced block needs a language tag. Show correct code only, and mark intentional omissions with language-appropriate comments/non-copyable annotation where available; do not disguise an incomplete snippet as runnable.
- Use descriptive links, relative internal paths and meaningful image/badge/diagram alt text. Decorative images may have empty alt text. Do not rely solely on color/position/screenshots to convey required steps.
- Explain prerequisites, observable outcomes and unavailable checks. Never invent verified capabilities, tested examples or working links.

### Execution Steps

1. Identify audience/document type and read current content and governing project style.
2. Draft concrete active prose and sentence-case headings, preserving technical identifiers and verified behavior.
3. Format parallel lists, language-tagged correct samples and descriptive links; add text alternatives to visual information.
4. Inspect inclusive terminology, punctuation, hierarchy and clarity without needless rewrites of unaffected text.
5. Run project Markdown checks and relevant link/example verification; fix findings or disclose blocked verification before completion.

### Validation

- Audience can identify actor, prerequisites, action and expected result; no filler or unsupported certainty.
- Sentence case and semantic hierarchy consistent; proper nouns/literal identifiers retained.
- Generic pronouns/roles inclusive and examples suitable for global readers.
- Code fences labeled, samples correct or explicitly incomplete, each introduced clearly.
- Links descriptive/current, images accessible and no color-only instructions.
- Markdown lint passes under project config; manual prose/accessibility review supplements lint.

## References

- [Google developer documentation style](https://developers.google.com/style)
- [Microsoft writing style](https://learn.microsoft.com/en-us/style-guide/welcome/)
- [CommonMark](https://spec.commonmark.org/)
