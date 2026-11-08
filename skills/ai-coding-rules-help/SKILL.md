---
name: ai-coding-rules-help
description: Print a one-screen reference card for the ai-coding-rules plugin covering its shipped skills, how rule loading works, configuration, updates and documentation links. Read-only; triggered explicitly by $ai-coding-rules-help.
version: 1.0.0
---

# ai-coding-rules-help

> User-invocable skill: `$ai-coding-rules-help` (Claude Code: `/ai-coding-rules:ai-coding-rules-help`)

## Purpose

Show a new user what the ai-coding-rules plugin does, which skills it ships, when to use each one and how to configure and update it, in one short reference card.

## Use this skill when

- Triggered explicitly by the user via `$ai-coding-rules-help`
- The user asks what the ai-coding-rules plugin does or which of its skills to use

## Instructions

1. Output everything below the Reference card heading verbatim, without that heading.
2. Do not run tools, read rule files, or write, create or modify any file, flag or setting. The card is static text.
3. Do not change modes or persist anything. After printing the card, stop and wait for the user.

## Reference card

**ai-coding-rules** loads the right coding rules for each prompt: a deterministic matcher scores your request against rule keywords, file extensions and paths, and the assistant reads only the rules that matched.

### Skills

| Skill | Trigger | What it does |
|---|---|---|
| `rule-loader` | Automatic through the hook, or `$rule-loader` on demand | Selects rules for a request: foundation, domain and activity matches, dependencies and token budget. |
| `show-rules` | `$show-rules` (explicit only) | Prints the PRE-FLIGHT block: which rules loaded for this prompt and why. Diagnostic only. |
| `ai-coding-rules-help` | `$ai-coding-rules-help` (explicit only) | Prints this card. Read-only. |

In Claude Code, invoke skills as `/ai-coding-rules:<skill>`.

### How rule loading works

- **Hook (opt-in):** with `--with-hook`, a `UserPromptSubmit` hook runs the matcher on every prompt and injects the micro-kernel foundation plus absolute paths of the matched rules.
- **No hook:** invoke `$rule-loader` when you want rules for a task.
- **Diagnose:** if the assistant does not cite the rules you expect, run `$show-rules`.

### Configuration

Set at install time from a clone of the repository:

- `--target cortex|claude|all`: which assistant to install for
- `--with-hook`: enable automatic discovery (off by default)
- `--project <dir>`: install into one project instead of globally (in CoCo, a global install wins over a project install)
- `--force`: overwrite an existing install

To change a setting, reinstall with the new flags plus `--force`, or uninstall with `uv run ai-rules plugin uninstall --target <target>`.

### Update

```bash
git pull
make env-sync
uv run --locked ai-rules plugin build
uv run ai-rules plugin verify
uv run ai-rules plugin install --target <target> --force   # add --with-hook to keep the hook
```

Then run `/plugin reload` or restart the assistant.

### Docs

- README: <https://github.com/sfc-gh-myoung/ai_coding_rules#readme>
- Rule loader guide: <https://github.com/sfc-gh-myoung/ai_coding_rules/blob/main/docs/USING_RULE_LOADER_SKILL.md>
- Architecture: <https://github.com/sfc-gh-myoung/ai_coding_rules/blob/main/docs/ARCHITECTURE.md>
- Issues: <https://github.com/sfc-gh-myoung/ai_coding_rules/issues>
