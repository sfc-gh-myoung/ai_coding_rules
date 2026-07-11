# Technical Writing Style for Human-Facing Documentation

## Metadata

**SchemaVersion:** v3.3
**RuleVersion:** v1.0.1
**LastUpdated:** 2026-07-10
**Keywords:** ext:.md, file:README.md, file:CONTRIBUTING.md, dir:docs/, kw:writing style, kw:voice, kw:active voice, kw:sentence case, kw:inclusive language, kw:bias-free, kw:serial comma, kw:accessibility, kw:microsoft style
**TokenBudget:** ~3350
**ContextTier:** Medium
**Depends:** required:000-global-core.md, optional:801-project-readme.md, optional:804-project-documentation.md, optional:002g-agent-optimization.md

## Scope

**What This Rule Covers:**
Writing standards for human-facing project documentation — voice, tone, sentence structure, capitalization, punctuation, inclusive language, list conventions, code sample presentation, link text, and accessibility. Grounded in the Google Developer Documentation Style Guide, the Microsoft Writing Style Guide, and the CommonMark specification.

**Applies To:**

- `README.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- Any file in `docs/` including ARCHITECTURE.md, DEPLOYMENT.md, ADRs, guides
- Any other Markdown intended for human readers

**Does NOT Apply To:**

- Files in `rules/` — those target autonomous agents and follow the agent-first formatting rules in `002g-agent-optimization.md` (imperative voice, structured lists, token-efficient prose). The two audiences require different conventions; do not apply this rule to rule files.
- `CHANGELOG.md` — governed by `800-project-changelog.md` (Keep a Changelog + Conventional Commits format).

**When to Load This Rule:**

- Creating or editing `README.md`, `CONTRIBUTING.md`, or any file under `docs/`
- Writing ADRs or extended documentation
- Reviewing pull requests that change human-facing documentation
- Establishing writing standards for a new project

## References

### Dependencies

**Must Load First:**

- **000-global-core.md** - Foundation rule with core patterns

**Related:**

- **801-project-readme.md** - README-specific structure and required sections
- **804-project-documentation.md** - docs/ folder organization
- **002g-agent-optimization.md** - Contrasting audience: rule files for agents

### External Documentation

- [Google Developer Documentation Style Guide](https://developers.google.com/style) - Voice, tone, headings, lists, code samples, inclusive language
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/) - Bias-free communication, accessibility, top 10 tips
- [CommonMark Spec](https://spec.commonmark.org/) - Authoritative Markdown specification

## Contract

### Inputs and Prerequisites

- Human-facing Markdown file being created or edited
- Understanding of the target audience (users, contributors, operators)
- Access to `uvx pymarkdownlnt` for lint validation

### Mandatory

- Use active voice with an explicit subject in prose
- Use second person ("you") when addressing the reader
- Use sentence case for all headings and titles
- Use serial (Oxford) commas in lists of three or more
- Use singular "they/them/their" for generic reference to a person
- Use gender-neutral job titles and role terms
- Specify a language identifier on every fenced code block
- Provide alt text for every image and badge
- Use descriptive link text (not "click here" or bare URLs)
- Introduce every code block with a lead-in sentence

### Forbidden

- Title case for headings (e.g., "Getting Started With The API")
- Passive voice that hides the actor (e.g., "the file is saved") outside the narrow exceptions listed below
- "he/she", "s/he", or gender-specific generic pronouns
- "master/slave", "DMZ", "blacklist/whitelist", or other biased terminology
- Ellipsis (`…` or `...`) to indicate omitted code — use a language-appropriate comment
- Placeholder phrases: "please note", "at this time", "simply", "easily", "quickly" in procedures
- Exclamation marks in body prose
- Bare URLs as link text (use `[descriptive text](url)` or `<https://example.com>` autolink form)
- Culture-specific idioms, metaphors, and slang

### Execution Steps

1. Identify the target audience (user, contributor, operator) and the document type (README, guide, ADR, reference).
2. Draft prose using active voice, second person, and present tense.
3. Format headings in sentence case; verify heading hierarchy is contiguous (H2 under H1, H3 under H2, no skipped levels).
4. Introduce each list and code block with a complete sentence.
5. Add a language identifier to every fenced code block.
6. Add alt text to every image and badge.
7. Replace any biased or gendered terminology with the neutral alternative.
8. Run `uvx pymarkdownlnt scan <file>` (or the project's lint automation target).
9. Fix any Markdown linter errors before marking the task complete.

### Output Format

Human-readable Markdown file conforming to:

- CommonMark 0.31 spec
- Sentence case headings
- Fenced code blocks with language identifiers
- Descriptive link text
- Alt text on all images

### Validation

**Pre-Task-Completion Checks:**

- All headings use sentence case
- All fenced code blocks include a language identifier
- All images have alt text
- No gendered pronouns in generic references
- No biased terminology (master/slave, DMZ, etc.)
- No bare URLs as link text
- Every code block has a lead-in sentence

**Success Criteria:**

- `uvx pymarkdownlnt scan <file>` returns 0 errors under the project's docs pymarkdown config
- No occurrence of forbidden terms (grep `-iE "master.slave|blacklist|whitelist|he/she|s/he"` returns nothing)
- Sentence case verified by inspection

**Negative Tests:**

- A heading in title case must be flagged and rewritten
- A fenced code block without a language identifier must be flagged (MD040)
- A "click here" link must be flagged and rewritten with descriptive text

### Post-Execution Checklist

- [ ] Active voice used in prose
- [ ] Second person ("you") used to address the reader
- [ ] Sentence case for all headings
- [ ] Serial commas in lists of three or more
- [ ] Singular "they/them" used for generic references
- [ ] Gender-neutral role and job terms used
- [ ] No biased terminology (master/slave, DMZ, blacklist/whitelist)
- [ ] Every fenced code block has a language identifier
- [ ] Every image and badge has alt text
- [ ] Descriptive link text (no "click here", no bare URLs)
- [ ] Every code block preceded by a lead-in sentence
- [ ] `uvx pymarkdownlnt scan` returns 0 errors

## Voice and Tone

- Use active voice. State who performs each action. Prefer "The server sends an acknowledgment" over "An acknowledgment is sent by the server". Passive voice is acceptable in three narrow cases: to emphasize the object over the actor ("The file is saved"), to de-emphasize the actor when the actor is irrelevant ("The database was purged in January"), or when the actor is unknown.
- Use second person ("you") to address the reader. Avoid "we" for reader-directed instructions.
- Use present tense.
- Sound like a knowledgeable colleague: conversational, direct, respectful. Avoid frivolity, wackiness, and pop-culture references.
- Use contractions freely (it's, you'll, we're) unless the target audience or translation workflow disallows them.
- Prune every unnecessary word. Prefer "Ready to buy? Contact us." over "If you are ready to make a purchase, please contact us."
- Start statements with verbs. Edit out "you can", "there is", "there are".

## Sentence Structure

- Put conditions before instructions:
  - Good: "If you want to reset, run `reset.sh`."
  - Bad: "Run `reset.sh` if you want to reset."
- Keep sentences short. Split long compound sentences.
- Use parallel structure within lists and heading groups.
- Avoid placeholder phrases: "please note", "at this time", "simply", "easily", "quickly" in procedures.
- Avoid figurative language, metaphors, and ableist expressions.

## Capitalization

- Use sentence case for all headings, titles, and UI labels — capitalize only the first word and any proper nouns.
- Preserve product and proper-noun casing (Snowflake, GitHub, Python, macOS).
- Do not use title case anywhere in headings or subheadings.

## Punctuation

- Use serial (Oxford) commas in every list of three or more items: "Android, iOS, and Windows" (not "Android, iOS and Windows").
- No spaces around em dashes: "pipelines—logical groups of activities—consolidate" (not "pipelines — logical groups of activities — consolidate").
- One space after periods, question marks, and colons.
- Skip end punctuation on headings and on standalone list items of three or fewer words.
- End full-sentence list items with a period.
- Avoid exclamation marks in body prose.

## Inclusive and Bias-Free Language

- Use gender-neutral job titles and role terms:
  - "chair" or "moderator" instead of "chairman"
  - "workforce", "staff", or "personnel" instead of "manpower"
  - "sales representative" instead of "salesman"
  - "operates" or "staffs" instead of "mans"
  - "synthetic" or "manufactured" instead of "manmade"
- Use singular "they/them/their" for generic reference to a single person. Do not use "he/she" or "s/he" constructions.
- When writing about a real person, use the pronouns that person uses.
- Avoid biased or historically loaded terminology:
  - "primary/subordinate" or "leader/follower" instead of "master/slave"
  - "perimeter network" instead of "demilitarized zone (DMZ)"
  - "allowlist/blocklist" instead of "whitelist/blacklist"
  - "stops responding" instead of "hangs"
- Focus on people, not conditions or disabilities: "readers who are blind or have low vision" not "blind readers" when the disability is not the point.
- Represent diverse names, roles, cultures, and contexts in examples.
- Avoid idioms, cultural references, and slang that hinder global comprehension or that risk cultural appropriation.

## Lists

- Use numbered lists for sequences where order matters.
- Use bulleted lists for unordered collections.
- Use description lists (term/definition) for glossaries and pairs of related items.
- Introduce every list with a complete sentence. End the introduction with a colon if it immediately precedes the list, or a period if content appears between the introduction and the list.
- Use parallel syntax across all items in a list.
- Start each item with a capital letter, unless case is semantically meaningful (glossary terms, code identifiers).
- End each item with a period when the item contains a verb and expresses a standalone thought.
- Omit end punctuation for single-word items, items without verbs, and items entirely in code font.
- Do not end lists with "etc." or "and so on" — rewrite the introduction to imply the list is non-exhaustive.

## Code Samples

- Precede every code block with a lead-in sentence.
- End the lead-in with a colon if the block follows immediately, or a period if content appears between the lead-in and the block.
- Always specify a language identifier on the fence: ` ```bash `, ` ```python `, ` ```json ` — never a bare ` ``` `.
- Wrap code lines at 80 characters where practical.
- Indicate omitted code with a language-appropriate comment (for example `# ... other config ...` in Python or `// ...` in JavaScript). Do not use an ellipsis character.
- If a code block contains omissions, mark it as non-click-to-copy where the docs tooling supports that annotation.

## Links

- Use descriptive link text that makes sense out of context. Avoid "click here", "read more", and bare URLs used as link text.
- Prefer relative paths for internal documentation links so links survive forks and branch renames.
- Use the CommonMark autolink form `<https://example.com>` for standalone URL references when a descriptive alternative is not possible.

## Accessibility

- Provide alt text for every image, badge, and diagram. If an image is purely decorative, use empty alt text (`![](path)`).
- Do not rely solely on color, shape, or position to convey meaning. Pair color-coded elements with text labels.
- Use semantic heading hierarchy for screen-reader navigation. Do not skip heading levels.
- Ensure every fenced code block has a language identifier so syntax-highlighting and assistive tools work correctly.
- Use tables only for tabular data with genuine row/column relationships. Prefer definition lists or bulleted lists when the data is simpler.

## Anti-Patterns and Common Mistakes

### Anti-Pattern 1: Title Case in Headings

**Problem:** Title case ("Getting Started With The API") is inconsistent, harder to translate, and clashes with modern documentation conventions.

**Correct Pattern:**

```markdown
# Getting started with the API

## Authenticate a request

### Retrieve an access token
```

### Anti-Pattern 2: Passive Voice Hiding the Actor

**Problem:** "The database is queried and a response is returned" leaves the reader unsure who performs each action.

**Correct Pattern:**

```markdown
The application queries the database. The database returns the response.
```

### Anti-Pattern 3: Gendered Generic Pronouns

**Problem:** "A developer should test his code" excludes readers and dates the documentation.

**Correct Pattern:**

```markdown
A developer should test their code.
Developers should test their code.
Test your code before submitting.
```

### Anti-Pattern 4: Biased or Historically Loaded Terminology

**Problem:** Terms like "master/slave", "whitelist/blacklist", and "DMZ" carry cultural or historical baggage that industry consensus is moving away from.

**Correct Pattern:**

```markdown
The primary node replicates data to subordinate nodes.
Add the domain to the allowlist.
Deploy the service in the perimeter network.
```

### Anti-Pattern 5: Fenced Code Block Without Language Identifier

**Problem:** A bare ` ``` ` fence disables syntax highlighting, hurts screen-reader labeling, and fails pymarkdownlnt MD040.

**Correct Pattern:**

````markdown
```bash
git clone https://github.com/org/repo.git
```
````

### Anti-Pattern 6: Ellipsis for Omitted Code

**Problem:** `…` or `...` in a code block is ambiguous — is it literal syntax or an editorial marker?

**Correct Pattern:**

```python
def process(items):
    for item in items:
        # ... additional validation omitted for brevity ...
        yield item
```

### Anti-Pattern 7: Non-Descriptive Link Text

**Problem:** "Click here for the API docs" fails when the surrounding text is stripped (screen readers, link lists).

**Correct Pattern:**

```markdown
See the [API reference](docs/API.md) for endpoint details.
```
