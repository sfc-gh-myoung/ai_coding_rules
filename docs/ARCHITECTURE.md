# Architecture: AI Coding Rules

**Last Updated:** 2026-05-14

> **What this document is**
> Design and rationale of the AI Coding Rules system: how it's shaped, why, and what extension points exist.
>
> **What this document is not**
> - Installation and usage → see [README.md](../README.md)
> - Contributing rules → see [CONTRIBUTING.md](../CONTRIBUTING.md)
> - Per-skill guides → see [docs/USING_*_SKILL.md](.)
> - Token budget tooling → see [TOKEN_BUDGETS.md](TOKEN_BUDGETS.md)
> - Memory bank usage → see [MEMORY_BANK.md](MEMORY_BANK.md)

## Table of Contents

- [1. Overview](#1-overview)
- [2. Key Architectural Concepts](#2-key-architectural-concepts)
- [3. System Components](#3-system-components)
- [4. Rule Loading Workflow](#4-rule-loading-workflow)
- [5. Design Decisions](#5-design-decisions)
- [6. Extension Points](#6-extension-points)
- [7. Related Documentation](#7-related-documentation)

---

## 1. Overview

> **Architecture:** Rule discovery is performed by the plugin's `UserPromptSubmit` hook, which scores rules deterministically and injects a compact foundation (the micro-kernel) together with the matched rule paths. The canonical Rule Loading Contract lives in `rules/000-global-core.md`; the detailed workflow content (foundation loading, domain matching, dependency resolution, token budget, anti-patterns, failure modes) lives in the `rule-loader` skill under `skills/rule-loader/`. An earlier design deployed a per-project bootstrap file; that path has been retired in favor of the plugin (§3.5).

### 1.1 The Problem

AI assistants need consistent, high-signal guidance to produce reliable code across many domains. The default options are poor: stuffing every rule into a single system prompt wastes context, and IDE-specific formats fragment the same information across tools that don't share a standard.

AI Coding Rules solves this by storing rules as Markdown files with embedded metadata. An AI assistant loads a foundation rule, searches an index for task-relevant rules, and pulls only what it needs. This keeps context small while preserving depth.

### 1.2 Core Architecture Principles

1. **Production-Ready by Default.** Rule files in `rules/` are directly editable and deployment-ready.
2. **No Generation Step.** Rules live in their final form, so there's no build step.
3. **Universal Format.** Standard Markdown with embedded metadata works with any AI assistant or IDE.
4. **Schema-Validated.** A declarative YAML schema enforces consistency.
5. **Agent-Agnostic Distribution.** Rules ship as a plugin whose hook injects matched rules into any assistant that supports `UserPromptSubmit`.

### 1.3 High-Level System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    AI CODING RULES                               │
│                                                                  │
│   rules/ ──────────┐                                             │
│   (195 files)      │                                             │
│                    ▼                                             │
│   schemas/ ────► ai-rules CLI ────► ai-coding-rules-plugin/      │
│   (validation)   (validate,         (rules + skills + hook)      │
│                   tokens, plugin)          │                     │
│                                            ▼                     │
│   skills/  ──────────────────────►  AI Assistant                 │
│   (rule-loader,                     (CoCo, Claude Code, …)       │
│    show-rules)                             │                     │
│                                            ▼                     │
│                                     UserPromptSubmit hook        │
│                                     injects matched rules        │
└──────────────────────────────────────────────────────────────────┘
```

The user clones this repository, optionally edits or adds rules, and runs `ai-rules plugin build` to assemble the plugin. Installing the plugin registers the skills and the `UserPromptSubmit` hook, which performs rule discovery on every prompt.

---

## 2. Key Architectural Concepts

### 2.1 Rule Files

A rule is a single Markdown file under `rules/`. Every rule has metadata (version, keywords, dependencies, token budget, context tier), a scope statement, references, and a structured contract that defines mandatory and forbidden behaviors plus execution steps.

Rules are designed to be loaded by an LLM with no preprocessing. The same file is editable by a human contributor, parsed by the validator, indexed by the index generator, and consumed by the AI assistant at runtime.

For the full rule template and field-by-field structure, see [CONTRIBUTING.md → Rule Structure](../CONTRIBUTING.md#rule-structure). The authoritative schema lives in [`schemas/rule-schema.yml`](../schemas/rule-schema.yml).

### 2.2 Companion Rule Pattern

Rules use letter suffixes to split large topics into focused, independently-loadable companion files. This is the primary architectural pattern for managing token budgets without losing depth.

**Naming Convention:** `<NNN><letter>-<technology>-<aspect>.md`

- Core rule: `NNN-technology-core.md` (no suffix). Foundation, always loaded first.
- Companions: `NNNa-technology-aspect.md`, `NNNb-…`, `NNNc-…`, etc.
- Letter suffixes must be single lowercase letters (a-z); multi-character suffixes are not permitted.

**How it works:**

1. The core rule provides foundational concepts and is the dependency target.
2. Companion rules extend the core with specialized subtopics.
3. Only the companions relevant to the current task are loaded.
4. All companions declare the core rule in their `Depends` field with the `required:` bucket prefix (see `rules/000-global-core.md` R8 and `rules/002-rule-governance.md` "Depends Bucket Semantics").

**Token budget benefits:**

- A Streamlit security task loads `101-core` + `101c-security` (~4K tokens) instead of all 15 Streamlit files (~25K+ tokens).
- Progressive expansion: start with core, add companions as task complexity grows.
- Independent updates: modify a companion without affecting siblings.

**Design constraints:**

- Core rule must be self-sufficient for basic tasks (companions are optional extensions).
- Companions must not create circular dependencies.
- Each companion should cover a single, clearly delineated subtopic.
- Split when a rule exceeds ~5500 tokens and covers multiple separable concepts.

**Rule size thresholds:**

| Threshold | Lines | Tokens | Action |
|-----------|-------|--------|--------|
| Optimal | 200-400 | ~2000-3500 | Standard rules, load normally |
| Advisory limit | 500 | ~5000 | Begin evaluating split candidates |
| Hard cap | 600 | ~5500+ | Must split into companion files |

### 2.3 Context Management

The repository uses a dual-layer approach for context preservation:

**Primary layer: natural language instructions (universal):**
- CRITICAL warnings in `000-global-core.md`.
- CORE RULE / FOUNDATION RULE markers in all `-core.md` and `002-series` files.
- Context Management Protocol in `000-global-core.md` teaching explicit preservation hierarchy.
- Works across all LLMs: Claude, GPT, Gemini, Llama, etc.

**Secondary layer: `ContextTier` metadata (project-specific):**
- Critical / High / Medium / Low values in rule metadata.
- Provides fine-grained prioritization within natural-language tiers.
- Validated by schema but not universally recognized by LLMs.
- Kept for compatibility and secondary signaling.

**Design principle:** never rely solely on metadata that LLMs don't natively understand. Natural-language instructions are the primary mechanism for ensuring consistent behavior.

See `000-global-core.md` → "Context Window Management Protocol" for implementation details.

### 2.4 Schema-First Design

Rule structure is declared in [`schemas/rule-schema.yml`](../schemas/rule-schema.yml) rather than hard-coded in validator logic. The schema is the specification: validator code interprets it, contributors read it to understand requirements, and external tools can parse it without coupling to the validator implementation.

Adding a new validation requirement is typically a schema-only change. See §5.3 for the full rationale.

### 2.5 Directive Language

Rules use a structured directive vocabulary (`Critical`, `Mandatory`, `Always`, `Requirement`, `Rule`, `Consider`) so that AI agents can apply consistent priority across rule content. The hierarchy is defined canonically in [CONTRIBUTING.md → Directive Language](../CONTRIBUTING.md#directive-language). Rules consume the vocabulary but do not redefine it.

### 2.6 Rule Numbering Convention

The `rules/` directory uses numeric ranges to group rules by domain. The full mapping (000-099 foundation, 100-199 Snowflake, 200-299 Python, 300-399 shells, 400-499 JavaScript, 500-599 frontend, 600-699 systems, 800-899 project tooling, 900-999 dbt, etc.) is documented in [README.md → Rule Categories](../README.md#rule-categories).

A new rule's number is determined by the domain it covers. Within a range, the core rule has no suffix and companions use single-letter suffixes per §2.2.

---

## 3. System Components

Each component below is described at the architecture layer only. For installation, command reference, and how-to material, follow the link to the component's canonical documentation.

### 3.1 The `rules/` Directory

The `rules/` directory is the single source of truth for all rules. Files are production-ready and directly editable; no generation step stands between source and deployment.

**Layout:**

```
rules/
├── 000-global-core.md             # Foundation (always loaded first)
├── 001-memory-bank.md             # Optional memory-bank protocol
├── 002-rule-governance.md (+002a-002m, 002n companions)
├── 100-snowflake-core.md          # Domain cores with companion families
├── 101-snowflake-streamlit-core.md (+101a-101n)
├── 200-python-core.md (+200a-200b)
├── 600-golang-core.md
├── ...                            # 194 rules covering all domains
└── examples/                      # Validated implementation examples
```

**Design decisions:**

- Files are loaded by AI assistants verbatim. Anything that should not appear in an LLM's context window does not belong in this directory.
- Rule metadata lives in each rule's YAML frontmatter; there is no generated catalog file to keep in sync.
- `examples/` holds runnable reference implementations validated against `schemas/example-schema.yml` rather than the rule schema.

For the file naming convention, rule lifecycle, and contribution flow, see [CONTRIBUTING.md](../CONTRIBUTING.md).

### 3.2 The Schema (`schemas/rule-schema.yml`)

The schema is a declarative YAML document that defines what a valid rule file looks like: required sections, metadata fields and patterns, severity levels, allowed orderings, and section-specific constraints. The validator (`ai-rules validate`) reads the schema and applies it to rule files.

**Architecture:**

```
schemas/rule-schema.yml
├── version + project metadata
├── metadata.required_fields[]      # SchemaVersion, RuleVersion, etc.
├── sections.required[]             # Scope, References, Contract, …
├── content_validation              # tier/keyword/dependency rules
└── severity_levels                 # CRITICAL / HIGH / MEDIUM / LOW
```

**Key design decisions:**

1. **Schema is the specification.** Contributors learn rule structure from the YAML, not from validator code.
2. **Severity-tiered findings.** CRITICAL fails CI; HIGH/MEDIUM/LOW are reported but configurable.
3. **External-tool friendly.** Other tools (linters, generators, IDE plugins) can parse the schema without depending on `ai-rules`.

For schema field reference and validation usage, see [`schemas/rule-schema.yml`](../schemas/rule-schema.yml) and [CONTRIBUTING.md → Rule Validation](../CONTRIBUTING.md#rule-validation).

### 3.3 The CLI (`ai-rules`)

The `ai-rules` CLI is a Typer-based Python application installed as a package entry point in `pyproject.toml`. It owns all rule lifecycle operations: creation, validation, indexing, token-budget checks, deployment, and badge updates.

**Architecture:**

```
src/ai_rules/
├── __main__.py        # python -m ai_rules entry point
├── cli.py             # Typer app: registers all commands
├── _shared/           # Cross-command utilities (paths, console)
└── commands/          # One module per command (validate, index, deploy, …)
```

**Key design decisions:**

1. **One command per file.** Each subcommand lives in its own module under `commands/` for testability.
2. **Shared utilities only in `_shared/`.** Cross-cutting helpers (project root detection, Rich console formatting) avoid duplication without coupling.
3. **All commands write structured output.** Logs flow through `_shared/console.py` so verbose / quiet modes are uniform.

For the full command reference, see [README.md → CLI Commands](../README.md#cli-commands).

### 3.4 Agent Skills Architecture

The project includes Agent Skills following [Anthropic's best practices](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills). Skills are agent-invokable, modular capabilities that live under `skills/<skill-name>/` with a consistent layout.

**Common Skill Layout:**

```
skills/<skill-name>/
├── SKILL.md           # Main entrypoint with YAML frontmatter
├── CHANGELOG.md       # Skill version history
├── workflows/         # Optional: phase-specific guides loaded on demand
├── rubrics/           # Optional: scoring rubrics for review-style skills
├── examples/          # Optional: walkthroughs and edge-case scenarios
└── tests/             # Optional: test cases for skill validation
```

`SKILL.md` is the only required file. Optional subdirectories are added as a skill grows in complexity, allowing simple skills to remain a single file while larger skills decompose into focused workflow and rubric files.

**YAML Frontmatter (SKILL.md):**

```yaml
---
name: <skill-name>
description: <one-sentence purpose plus invocation triggers>
version: 1.0.0
---
```

The frontmatter is parsed by the agent at skill discovery time. The `description` field doubles as the trigger surface: it should describe both what the skill does and the phrases that should invoke it.

**Design decisions:**

1. **Hybrid Code Embedding.** Simple validation lives inline in `SKILL.md`; complex scripts are external files referenced by path.
2. **Progressive Disclosure.** Workflow files are loaded on demand by the skill, not eagerly at invocation time. This keeps the entrypoint small and predictable.
3. **Edge Case Documentation.** Skills with non-trivial decision logic include an `examples/edge-cases.md` covering ambiguous scenarios.
4. **Cross-Skill Integration.** Reviewer skills can be invoked against the output of authoring skills to enforce quality gates without coupling.

**User-facing documentation:**

Larger project-maintenance skills ship with a `docs/USING_<SKILL_NAME>_SKILL.md` user guide containing examples, mode tables, FAQ, and reference material. Smaller workflow skills are documented primarily in their own `SKILL.md` files. Architectural details about how a specific skill works belong in that skill's own documentation, not in this file.

### 3.5 The Plugin (`ai-coding-rules-plugin/`)

The plugin is the distribution path for Cortex Code and Claude Code's native plugin system. It installs once and activates automatically across all projects.

**Architecture:**

```
ai-coding-rules-plugin/
├── .cortex-plugin/plugin.json    # Plugin manifest (hooks, skills declaration)
├── hooks/user-prompt-submit      # UserPromptSubmit hook (entry point)
├── micro_kernel_content.md       # Foundation micro-kernel (~500 tokens)
├── rules/                        # Full rule library (same as rules/)
└── skills/
    ├── rule-loader/              # Deterministic matcher + manifest builder
    │   └── scripts/match_rules.py  # Stdlib-only Python scorer
    └── show-rules/               # $show-rules diagnostic skill
```

**How it works:**

1. On every user prompt, the IDE invokes the `UserPromptSubmit` hook.
2. The hook runs `match_rules.py` — a deterministic scorer that matches the prompt against rule keywords/extensions.
3. The hook injects a `<system-reminder>` containing the micro-kernel (foundation behaviors) and a list of matched rule paths.
4. The agent reads the most relevant matched rules, up to the 3-rule cap.

**Key design decisions:**

1. **Hook-driven, not file-driven.** Discovery happens deterministically in the hook each turn, with no catalog file to grep and no per-project bootstrap file.
2. **Micro-kernel over full foundation.** The micro-kernel is a compact compression of `000-global-core.md` covering only mandatory behaviors. Full rules are still read on demand.
3. **PRE-FLIGHT is on-demand.** The plugin does not require PRE-FLIGHT output by default. Use `$show-rules` for diagnostics.
4. **Single manifest.** `.cortex-plugin/plugin.json` is accepted by both Cortex Code and Claude Code — no need for separate `.claude-plugin/` directory.
5. **Stdlib-only matcher.** `match_rules.py` requires no pip dependencies, enabling zero-install plugin distribution. It is **vendored** into the plugin by the build rather than imported from an installed package — see [4.5 Plugin Build and Install Flow](#45-plugin-build-and-install-flow) for why, and how copy drift is caught.

**Why the plugin replaced per-project deployment:**

An earlier design copied rules, skills, and a bootstrap file into each target
project. That produced duplicate copies of the same artifacts across a developer's
machine, and every rule update required re-copying into each project. The plugin
installs once and the hook applies everywhere, so there is a single copy of the
rule library.

Note that rules are not a first-class plugin capability — plugin manifests declare
skills, subagents, commands, hooks, and MCP servers. The rule library ships
alongside those as plain files that the hook reads at match time.

For build and install commands, see [README.md → Install the plugin](../README.md#install-the-plugin).

---

## 4. Rule Loading Workflow

AI assistants follow a two-phase loading process: the hook injects the micro-kernel and matched rule paths on every prompt, then the agent reads the rules it selects on demand.

### 4.1 Loading Sequence

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER SUBMITS A PROMPT                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: HOOK FIRES (UserPromptSubmit)                                  │
│                                                                         │
│   ┌──────────────────────────┐                                          │
│   │ hooks/user-prompt-submit │  Receives {"prompt": "..."} on stdin     │
│   └──────────────────────────┘                                          │
│              │                                                          │
│              ▼                                                          │
│   ┌──────────────────────────┐                                          │
│   │ match_rules.py           │  Score keywords, file extensions, paths  │
│   │ (deterministic, stdlib)  │  Resolve required dependencies           │
│   └──────────────────────────┘                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: CONTEXT INJECTION                                              │
│                                                                         │
│   A <system-reminder> is prepended to the turn containing:              │
│                                                                         │
│   ┌────────────────────────┐                                            │
│   │ micro_kernel_content   │  Foundation: mandatory behaviors,          │
│   │ (compact foundation)   │  validation sequence, loading contract     │
│   └────────────────────────┘                                            │
│              +                                                          │
│   ┌────────────────────────┐                                            │
│   │ Matched rule paths     │  Candidates, ranked; entry cap applied     │
│   └────────────────────────┘                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: AGENT READS AND APPLIES                                        │
│                                                                         │
│   Reads the most relevant rules (up to the cap) plus required           │
│   dependencies, cites them under RULES_LOADED, then acts.               │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 File Responsibilities

| File | Loading | Purpose |
|------|---------|---------|
| **`micro_kernel_content.md`** | Injected by the hook every prompt | Compact foundation: mandatory behaviors, validation sequence, rule-loading contract |
| **PROJECT.md** | Auto-loaded by IDE | Project-specific tooling, validation requirements, critical violations |
| **rules/000-global-core.md** | Full foundation, read on demand | Execution protocols, validation gates, workflows |
| **rules/XXX-*.md** | Loaded on demand | Domain and activity-specific rules selected by the matcher |

### 4.3 Key Design Decisions

1. **Discovery is deterministic.** The hook scores rules with a fixed algorithm rather than relying on the model to grep a catalog.
2. **`PROJECT.md` is not part of the rule chain.** It's project configuration, not a rule file.
3. **Dependencies load in order.** Required dependencies resolve ahead of the rules that declare them.
4. **Lazy loading.** Only matched rules are read, and the entry cap bounds how many.

### 4.4 Rule Creation Flow

```mermaid
flowchart TD
    Start([User: Create New Rule]) --> Generate
    Generate["ai-rules new XXX"] --> Template
    Template[ai-rules new] --> Create[Create rules/XXX.md<br/>with v3.5 structure]
    Create --> Edit[User: Edit Content]
    Edit --> Validate{Validate?}
    Validate -->|"ai-rules validate rules/"| SchemaVal[ai-rules validate]
    SchemaVal --> Pass{Passed?}
    Pass -->|No| Fix[Fix Errors]
    Fix --> Edit
    Pass -->|Yes| Build["ai-rules plugin build"]
    Build --> Commit[git commit]
    Commit --> End([Rule Ready])
```

### 4.5 Plugin Build and Install Flow

`ai-rules plugin build` assembles the plugin tree from the source tree. The plugin
directory is **generated output** — it is gitignored and must never be hand-edited,
because every build recreates it. Edit the source and rebuild.

The build performs seven steps, implemented in `src/ai_rules/commands/plugin.py`:

| Step | Action | Source |
|------|--------|--------|
| 1 | Copy the matcher into the skill's `scripts/` | `src/ai_rules/match_rules.py` |
| 2 | Copy the rule library | `rules/*.md` |
| 3 | Copy the hook | `hooks/` |
| 4 | Copy the `rule-loader` skill (`SKILL.md`, `workflows/`, `examples/`) | `skills/rule-loader/` |
| 4b | Copy the `show-rules` skill (`SKILL.md` only) | `skills/show-rules/` |
| 5 | Copy the micro-kernel content | `src/ai_rules/plugin/micro_kernel_content.md` |
| 6 | Generate the plugin manifest | written, not copied |
| 7 | Validate that the copied matcher runs standalone | executes the script |
| 7b | Validate the artifact contract | same check as `plugin verify` |

**The artifact contract.** `plugin.py` declares what a correct build looks like and
checks it in **both** directions:

- `EXPECTED_ARTIFACTS` — eight named files that must be present.
- `EXPECTED_TREES` — three directory prefixes (`rules`, and the rule-loader
  `examples/` and `workflows/`) whose contents vary. Splitting static files from
  dynamic trees is what keeps "add a rule" from requiring a code change.
- `check_artifacts()` asserts every declared artifact exists **and** that every
  emitted file is either declared or falls under a declared tree. The second
  direction is the important one: it catches a copy step that silently stops
  emitting something, which a presence-only check cannot.

`ai-rules plugin verify` runs the same `check_artifacts()` the build does, so the
two cannot disagree. CI additionally builds twice into separate directories and
diffs them, proving the build is deterministic, and diffs the vendored matcher
against its canonical source.

**The manifest contract.** `check_manifest()` validates the generated
`.cortex-plugin/plugin.json`: required keys present and non-empty, hook events
recognised, each hook entry shaped correctly, and every referenced hook command
actually present and executable in the build. The Cortex CLI has **no**
`plugin validate` subcommand, so without this a malformed manifest would surface
only at install time on a consumer's machine. `check_artifacts()` calls it, so
both `build` and `verify` enforce it.

**Vendored matcher, not a trampoline.**

There are two ways to give the hook a matcher, and the choice matters:

- **Trampoline (rejected).** Ship a thin shim that imports `ai_rules.match_rules`
  from an installed package. This keeps one copy of the code, but it only works if
  the interpreter that resolves at hook time has `ai_rules` importable. The hook runs
  in whatever environment the IDE happens to provide, and the plugin is meant to work
  on machines that have never installed this project — so the import would frequently
  fail, and failure would be silent.
- **Vendored (chosen).** Build step 1 copies `src/ai_rules/match_rules.py` into
  `skills/rule-loader/scripts/`. The hook executes that copy directly with any
  `python3` on `PATH`. No install, no virtualenv, no import path.

The cost is a second copy of the file, which can drift from its source. That cost is
paid down mechanically rather than by discipline: the build diffs the copy against
the canonical source, `plugin verify` re-checks it, CI asserts
`diff -q src/ai_rules/match_rules.py <build>/skills/rule-loader/scripts/match_rules.py`,
and a unit test asserts the same. Drift therefore fails the build rather than
silently shipping a stale matcher.

The canonical source is `src/ai_rules/match_rules.py`. Never edit the vendored copy.


```mermaid
flowchart TD
    Start([User: Build Plugin]) --> Command
    Command["ai-rules plugin build"] --> Assemble
    Assemble[Assemble plugin tree] --> CopyRules[rules/*.md]
    Assemble --> CopySkills[skills/rule-loader, skills/show-rules]
    Assemble --> CopyHook[hooks/user-prompt-submit]
    Assemble --> CopyKernel[micro_kernel_content.md]
    Assemble --> CopyMatcher[match_rules.py into skill scripts/]
    Assemble --> Manifest[.cortex-plugin/plugin.json generated]
    Manifest --> Standalone{Matcher runs standalone?}
    Standalone -->|Fail| Error[Error: matcher is not self-contained]
    Standalone -->|Pass| Contract{check_artifacts: declared == emitted?}
    Contract -->|Fail| Error2[Error: missing or undeclared artifact]
    Contract -->|Pass| Install["cortex plugin install ./ai-coding-rules-plugin"]
    Install --> Registry[(~/.snowflake/cortex/plugins/registry.json)]
    Registry --> Active([Hook active on every prompt])

    Error --> End([Failed])
    Error2 --> End
```

---

## 5. Design Decisions

This section captures the rationale behind the major architectural choices. Each subsection follows the same shape: decision, rationale, trade-offs accepted.

### 5.1 Why Production-Ready Rules?

**Decision:** Store rules in final, deployable form instead of templates requiring generation.

**Rationale:**

1. **Simplicity.** Users clone and use immediately, no build step.
2. **Transparency.** What you see is what you get; no hidden transformations.
3. **Maintainability.** Single source of truth (no template/generated divergence).
4. **Universality.** Standard Markdown works with any AI assistant or IDE.
5. **Velocity.** Direct editing is faster than an edit-generate-deploy cycle.

**Trade-offs accepted:**

- Cannot generate IDE-specific formats (e.g., Cursor `.mdc` with auto-apply).
- Manual metadata management (mitigated by schema validation).
- Larger git diffs (entire rule files, not just templates).

**Industry alignment:**

- Hugo / Jekyll use content directly (not templates).
- Modern CI/CD prefers artifact generation over source generation.
- Infrastructure-as-code stores desired state, not generation instructions.

### 5.2 Why a Single Universal Format?

**Decision:** Use one Markdown format instead of multiple IDE-specific formats.

**Rationale:**

1. **No lock-in.** Users are free to switch AI assistants without migration.
2. **Broader compatibility.** Works with emerging tools (Claude Code, Cursor, Gemini, etc.).
3. **Easier contribution.** Contributors edit one file, not four.
4. **Metadata preservation.** `Keywords` / `TokenBudget` / `ContextTier` enable intelligent loading.
5. **Simpler architecture.** Focused CLI commands instead of monolithic generation.

**What we lost:**

- IDE-specific features (Cursor `globs`/`alwaysApply`, Copilot `appliesTo`).
- Automatic rule application (users must configure paths).
- Format-specific optimizations.

**What we gained:**

- Universal compatibility.
- Simpler maintenance.
- Faster contribution workflow.
- Clear upgrade path to future AI tools.

### 5.3 Why a Declarative Schema?

**Decision:** Define validation in YAML instead of hard-coded Python logic.

**Rationale:**

1. **Separation of concerns.** Schema definition is separate from validation implementation.
2. **Extensibility.** Add new checks without modifying validator code.
3. **Documentation.** The schema file is the specification.
4. **Version control.** Schema changes tracked independently.
5. **Tooling.** External tools (linters, generators) can parse the schema directly.

**Implementation pattern:**

```yaml
# schemas/rule-schema.yml
sections:
  required:
    - name: Contract
      order: 4
      required_before_line: 160
```

vs. the older hard-coded approach:

```python
if "Contract" not in sections:
    errors.append("Missing Contract section")
if sections["Contract"]["line"] > 160:
    errors.append("Contract must appear before line 160")
```

**Benefits realized:**

- New validation rules added with schema-only edits.
- Contributors can read requirements from the schema alone.
- Validator logic stays small.

### 5.4 Why Parallel Sub-Agents for Bulk Operations?

**Decision:** Use parallel sub-agents (not sequential in-context execution) for bulk rule reviews.

**Rationale:**

1. **Context drift prevention.** Fresh context per sub-agent eliminates quality degradation after 50+ rules.
2. **Speed.** Roughly 5× faster execution (~50 minutes vs 4-6 hours for 180 rules).
3. **Isolation.** One sub-agent failing doesn't stop others; partial results are preserved.
4. **Full protocol preservation.** Each sub-agent loads complete protocols freshly.
5. **No file conflicts.** Unique filenames (`rule-name-model-date.md`) prevent write races.

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    BULK-RULE-REVIEWER (Coordinator)                      │
│   • Partitions rules into N groups                                       │
│   • Launches N sub-agents in background                                  │
│   • Monitors progress via agent_output polling                           │
│   • Aggregates results when all complete                                 │
└─────────────────────────────────────────────────────────────────────────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker 4 │  │ Worker 5 │
   │ Rules    │  │ Rules    │  │ Rules    │  │ Rules    │  │ Rules    │
   │ 1-26     │  │ 27-52    │  │ 53-78    │  │ 79-104   │  │ 105-129  │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │           Direct File Writes (No Conflicts)                       │
   │   reviews/rule-reviews/<rule>-<model>-<date>.md                   │
   └──────────────────────────────────────────────────────────────────┘
```

**Trade-offs accepted:**

- More complex orchestration logic.
- Requires `agent_output` polling for progress.
- Higher token usage (duplicate protocol loading per sub-agent).

**Why not sequential?**

- Context drift causes quality degradation in long sessions.
- Single-threaded: 4-6 hours for 100+ rules.
- One failure can halt the entire process.
- Sequential is available as a fallback via `max_parallel: 1`.

---

## 6. Extension Points

The system is designed to be extended without forking. The four most common extension surfaces are below.

### 6.1 Adding New Rules

Rule authoring is the most frequent extension. Use `uv run ai-rules new NNN-description` to scaffold a new rule, then fill in content per the schema. Validate with `uv run ai-rules validate rules/`, then rebuild the plugin with `uv run ai-rules plugin build`.

For the full rule-creation workflow, see [CONTRIBUTING.md → Adding a New Rule](../CONTRIBUTING.md#adding-a-new-rule).

### 6.2 Customizing the Schema

Organizations that need additional validation (e.g., requiring an `Author` field, enforcing peer review) can fork the schema rather than the validator code:

1. Copy `schemas/rule-schema.yml` to `schemas/custom-schema.yml`.
2. Add or modify validation rules in YAML.
3. Run with `ai-rules validate rules/ --schema schemas/custom-schema.yml`.

**Trade-offs:** custom schemas prevent direct upstream merges and require maintenance when the upstream schema evolves.

### 6.3 Adding Custom Automation

To add organization-specific commands, drop a new module under `src/ai_rules/commands/`, register it in `src/ai_rules/cli.py`. Existing commands (`validate.py`, `index.py`) work as templates. Tests follow the patterns in `tests/cli/`.

### 6.4 IDE-Specific Enhancements

Universal Markdown is the default, but IDE-specific formats (Cursor `.mdc`, Copilot `appliesTo`, etc.) can be generated at deploy time. The pattern is to add a deploy variant (e.g., `deploy_cursor.py`) that wraps the universal Markdown with IDE-specific frontmatter rather than maintaining parallel source files.

This preserves the single-source-of-truth invariant while letting downstream consumers opt into richer formats.

### 6.5 Periodic Rule Review

The `rule-reviewer` and `bulk-rule-reviewer` skills automate quality reviews. Recommended cadence:

- **Foundation rules (000-*):** quarterly, FULL mode.
- **Domain cores (1XX, 2XX, …):** quarterly, STALENESS mode.
- **Specialized / activity rules:** semi-annually, STALENESS mode.
- **Reference rules (>5000 tokens):** annually, STALENESS mode.

For review modes, scoring rubrics, and invocation, see [USING_RULE_REVIEWER_SKILL.md](USING_RULE_REVIEWER_SKILL.md) and [USING_BULK_RULE_REVIEWER_SKILL.md](USING_BULK_RULE_REVIEWER_SKILL.md).

---

## 7. Related Documentation

### 7.1 Core Documentation

- **[README.md](../README.md)**: quick start, deployment, and CLI reference.
- **[CONTRIBUTING.md](../CONTRIBUTING.md)**: development guidelines, rule authoring, and PR workflow.
- **[CHANGELOG.md](../CHANGELOG.md)**: version history.

### 7.2 Per-Skill Guides

| Skill | Guide |
|-------|-------|
| `bulk-rule-reviewer` | [USING_BULK_RULE_REVIEWER_SKILL.md](USING_BULK_RULE_REVIEWER_SKILL.md) |
| `rule-creator` | [USING_RULE_CREATOR_SKILL.md](USING_RULE_CREATOR_SKILL.md) |
| `rule-loader` | [USING_RULE_LOADER_SKILL.md](USING_RULE_LOADER_SKILL.md) |
| `rule-reviewer` | [USING_RULE_REVIEWER_SKILL.md](USING_RULE_REVIEWER_SKILL.md) |
| `skill-timer` | [USING_SKILL_TIMER_SKILL.md](USING_SKILL_TIMER_SKILL.md) |

### 7.3 Tooling and Optional Features

- **[TOKEN_BUDGETS.md](TOKEN_BUDGETS.md)**: token-budget validation tool reference.
- **[MEMORY_BANK.md](MEMORY_BANK.md)**: optional Memory Bank system for long-running projects.
- **[EVALUATING_RULE_LOADER.md](EVALUATING_RULE_LOADER.md)**: Rule Loading Evaluator. Pre-commit live-agent sanity check that the agent loads the expected rules (including dependency rules) for each fixture. CI runs only the trigger-evidence invariant; the live SDK runs locally.

### 7.4 Schema and Validation

- **[Schema Documentation](../schemas/README.md)**: current schema specification and field reference.
- **[`schemas/rule-schema.yml`](../schemas/rule-schema.yml)**: authoritative declarative validation schema.

### 7.5 External References

- **[Anthropic Agent Skills best practices](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills)**: background on the Agent Skills model used in section 3.5.
- **[CommonMark Spec](https://spec.commonmark.org/)**: all rule files comply with CommonMark Markdown.
