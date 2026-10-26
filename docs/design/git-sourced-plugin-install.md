# Git-sourced plugin installation: design and evaluation (issue #36)

| Field | Value |
|---|---|
| Issue | [#36](https://github.com/sfc-gh-myoung/ai_coding_rules/issues/36) (evaluation and design only; nothing here is implemented) |
| Date | 2026-10-25 |
| Baseline | `origin/main` at `d915c2d` |
| Clients tested | Claude Code 2.1.310, Codex CLI 0.139.0, Cortex Code CLI (CoCo) 1.2.24 |
| CoCo Desktop | Not inspected. Every Desktop cell is an assumption. |
| Re-verify when | Any tested client ships a new minor version, a client changes its plugin, marketplace or hook-trust behavior, or more than 90 days pass. Owner and cadence are follow-up F11. |

## Reading this document

Status of every claim is explicit.

- `V:<tag>` means verified. The tag names the evidence (legend below).
- `A:<V-id>` means an assumption. The V-id is the row of the [validation matrix](#11-validation-matrix) that would settle it.
- No human-run verification row (V1-V3, V3b, V6-V12 client parts) has been run. Those rows are reported as NOT YET RUN, with the script that runs them.

| Tag | Evidence |
|---|---|
| `H` | Local `<client> ... --help` output, 2026-10-25 |
| `P` | [Claude plugins reference](https://code.claude.com/docs/en/plugins-reference) |
| `M` | [Claude plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) |
| `X` | Codex docs: [plugins](https://developers.openai.com/codex/plugins), [build](https://developers.openai.com/codex/plugins/build.md), hooks.md |
| `R` | File or directory observed on the research machine (for example the CoCo `registry.json`) |
| `S` | Static repo audit of `origin/main` (`.workbench/issue-36/notes-static-audit.md`) |
| `T` | Direct hook execution on a hand-built install copy, no client involved (`.workbench/issue-36/results-v0-v4-v5.md`, `run1.log`) |

Weaker sources (third-party blogs) are never tagged `V`. A repo code comment that says "verified on CoCo" is secondhand and is tagged `A`.

## 1. Scope and non-goals

In scope: decide how AI Coding Rules can be installed from Git, with no development checkout, no `ai-rules plugin build` and no `ai-rules plugin install`, on Claude Code, Codex and CoCo.

Non-goals and constraints:

- No packaging change, release or real-install modification in #36. Proposed adapter files are drafts in [Appendix A](#appendix-a-draft-adapter-files-untested), not committed.
- No change to rule-selection semantics, rule content or evaluation scoring.
- No parity claim across clients. Manifest schemas, marketplace files, hook trust and path variables differ.
- **No hook-trust bypass, no install-by-default policy, no auto-activation.** This design does not use `--dangerously-bypass-hook-trust`, managed or admin hooks, marketplace `policy.installation: INSTALLED_BY_DEFAULT` (drafts use `AVAILABLE`), or any CoCo auto-activation to make the hook "just work". Hook enablement stays a deliberate user action.
- Windows and `commandWindows` are out of scope.
- Requiring users to install the project's development environment is not an acceptable workaround.

Premise confirmed (`S`, `T` row V0): `ai-coding-rules-plugin/` is untracked and ignored (`.gitignore:250`, 0 tracked files). The repo root has no `.claude-plugin/`, `.cortex-plugin/` or marketplace file. A Git install therefore yields no plugin today. Every file the hook needs is already tracked at the repo root, except the two manifests and an optional `micro_kernel_content.md` copy (section 5).

## 2. Capability matrix

Columns: Claude Code 2.1.310, Codex 0.139.0, CoCo CLI 1.2.24, CoCo Desktop (not inspected). Mixed facts are split into separate rows so each cell has a single status.

| Capability | Claude Code | Codex | CoCo CLI | CoCo Desktop |
|---|---|---|---|---|
| Git-sourced install command | V:H `claude plugin marketplace add <owner/repo\|url\|path>` then `claude plugin install <p>@<m>` | V:H `codex plugin marketplace add <owner/repo[@ref]\|url\|path> [--ref] [--sparse]` then `codex plugin add` | V:H `cortex plugin install <git shorthand\|URL>` | A:V3 |
| Exact Git shorthand grammar | V:M `owner/repo` and URL accepted by `marketplace add` | V:H `owner/repo[@ref]`, HTTPS and SSH URL | A:V1 (help gives no grammar; `registry.json` stores `github:OWNER/REPO/SUBPATH#REF`, V:R) | A:V1 |
| `file://` source accepted | A:V1 | A:V1 | A:V1 | A:V1 |
| Marketplace manifest required | V:M `.claude-plugin/marketplace.json` (name, owner, plugins[].name+source) | V:X `.agents/plugins/marketplace.json` | A:V1 (no marketplace file observed for direct Git installs) | A:V1 |
| Reads Claude-style marketplace file | n/a | A:V7 (docs say legacy `.claude-plugin/marketplace.json` is compatible; untested) | A:V1 | A:V1 |
| Root-level plugin (`source: "./"`) | A:V12 (docs wording only) | A:V7 | A:V12 (subdirectory plugins observed, V:R; root untested) | A:V12 |
| Subdirectory plugin | V:M relative `./path`, git-subdir | V:X `git-subdir` source | V:R existing installs, `SUBPATH` in registry source | A:V12 |
| Plugin manifest location | V:P `.claude-plugin/plugin.json`, only `name` required | V:X root `plugin.json` or legacy `.codex-plugin/plugin.json` | V:R both `.cortex-plugin/` and `.claude-plugin/` exist in installed plugins | A:V1 |
| Manifest precedence when both dirs exist | n/a | n/a | A:V1 | A:V1 |
| Skills discovery | V:P `skills/<n>/SKILL.md`, namespaced `<plugin>:<skill>` | A:V7 (docs say `skills/<n>/SKILL.md`; whether a root `plugin.json` must declare it is unknown) | V:R via manifest `skills: ["./skills"]` only | A:V1 |
| Hook declaration file | V:P `hooks/hooks.json` with top-level `hooks` wrapper | V:X `hooks/hooks.json` or manifest `hooks`, paths `./` inside root | A:V3 (repo comment in `plugin.py` says CLI and Desktop fire `hooks/hooks.json`; secondhand) | A:V3 |
| Plugin-root variable in hook command text | V:P `${CLAUDE_PLUGIN_ROOT}` | A:V7 (command-text substitution unknown) | A:V3 (repo comment says substituted at load) | A:V3 |
| Plugin-root variable in hook environment | A:V3 (docs say the variables are not set in the Bash-tool env, V:P; hook-env behavior untested) | V:X `PLUGIN_ROOT`, `PLUGIN_DATA` and `CLAUDE_*` aliases | A:V3 (repo comment says not exported) | A:V3 |
| Hook consent | A:V6 (not found in fetched docs) | V:X plugin install does not trust hooks; per-hash review; changed hook needs re-review | A:V6 (undocumented) | A:V6 |
| Consent bypass flag exists | A:V6 | V:X `--dangerously-bypass-hook-trust` (not used here) | A:V6 | A:V6 |
| Hook behavior in non-interactive mode | A:V3b | A:V7 (`codex exec` trust behavior unknown) | A:V3b | A:V3b |
| Hook stdin payload field names | A:V3b (hook reads `.prompt` via `jq`) | A:V3b | A:V3b | A:V3b |
| Hook stdout injection format | A:V3b | V:X `UserPromptSubmit` stdout or `additionalContext` becomes developer context | A:V3b | A:V3b |
| Update command | V:H `claude plugin update <plugin>` (restart to apply) | V:H `codex plugin marketplace upgrade`, manual | V:H `cortex plugin update [src]` | A:V9 |
| Update auto-applies | A:V9 | A:V9 (no auto-update found, not verified) | A:V9 | A:V9 |
| Update failure observed | A:V9 (none observed, not exercised) | A:V9 (none observed, not exercised) | V:R `lastUpdateError` ENOENT on `remote_cache` for one plugin, `pendingUpgrade` on another (cause A:V9) | A:V9 |
| Uninstall command | V:H `claude plugin uninstall` (`--keep-data`, `--scope`) | V:H `codex plugin remove` (config and cache); marketplace removed separately | V:H `cortex plugin uninstall\|remove\|delete\|rm <name>` | A:V10 |
| Removing a marketplace uninstalls its plugins | V:M | A:V10 | A:V10 | A:V10 |
| Cache directory exists | V:R `~/.claude/plugins/cache` | A:V1 (location not recorded) | V:R `~/.snowflake/cortex/remote_cache/github_<Owner>_<repo>_<hash>/<ref>/`, installed copy `~/.snowflake/cortex/plugins/<name>/` | A:V1 |
| Cache layout `<m>/<p>/<ver>` and 14-day retention | A:V10 | A:V10 | n/a | A:V10 |
| Sparse checkout | V:H `--sparse` | V:H `--sparse` | A:V12 | A:V12 |
| Pin by tag or SHA on add | A:V11 | V:H `--ref`, `@ref` | A:V11 (`#branch` stored, V:R; tag or SHA after `#` unknown) | A:V11 |
| Pin by marketplace entry `ref`/`sha` | A:V11 (documented in weaker sources only) | V:X entry `ref`/`sha` for `git-subdir` | n/a | n/a |
| Validate command | V:H `claude plugin validate <dir>` (`--strict`) | A:V7 | V:H `cortex plugin validate [path\|name]` | A:V1 |
| Install without activating | n/a | n/a | V:H `--inactive` (`activation.md` discovery only, if present) | A:V1 |
| Skill invocation syntax | V:P `/<plugin>:<skill>` (for example `/ai-coding-rules:show-rules`) | A:V2 (`$show-rules`, new session required, V:X) | A:V2 (`$show-rules`) | A:V2 |
| Runtime prerequisites on the user machine | A:V3 (hook needs `bash`; `python3` and `jq` from the user PATH) | A:V3 | A:V3 | A:V3 |
| IDE extension / desktop app | A:V3 (Claude desktop surfaces not inspected) | V:X Codex IDE extension does **not** support plugins (unsupported); ChatGPT desktop app does | n/a | A:V3 (F10 settles Desktop) |

Notes:

- Codex has a native plugin mechanism (V:H, V:X). Its schema is separate from Claude's. Codex support in this design is **conditional on V7**, and a Codex-specific adapter (F9) is the default expectation, not an optional extra. The Claude-style marketplace file compatibility is an unverified shortcut, not the plan.
- The Codex IDE extension is unsupported. The closest supported options there are the non-plugin fallbacks the docs list (`AGENTS.md`, `~/.codex/hooks.json`, `<repo>/.codex/hooks.json`, standalone skills). Those are not designed here.
- Facts about the installed Claude/CoCo `ai-coding-rules` files outside the repo (for example the dead `local:` registry entry) come from the research machine (V:R) and may not match a user's machine.

## 3. Per-client install, update and uninstall

All commands below are proposals. None was executed by an agent. Run them only inside the scratch environment of the human-run kit (section 11). Placeholders: `<marketplace-name>` is chosen when the marketplace file is authored (F4). The repository identity is `sfc-gh-myoung/ai_coding_rules`.

Hook enablement is deliberate on every client. No step below enables the hook silently.

### 3.1 Claude Code

```text
claude plugin marketplace add sfc-gh-myoung/ai_coding_rules --scope user   # V:H
claude plugin install ai-coding-rules@<marketplace-name>                   # V:H
claude plugin validate .                                                   # V:H; use --strict in CI
claude plugin update ai-coding-rules                                       # V:H; restart to apply
claude plugin uninstall ai-coding-rules                                    # V:H; --keep-data to keep plugin data
```

- Pin variant: marketplace entry `ref`/`sha` (A:V11) or `owner/repo#ref` on add (A:V11).
- Enable the hook: no consent step is documented (A:V6). Confirm by listing hooks (`/hooks`, A:V6) and by the positive injection check in section 9. If the hook does not appear or fire, the install is not active.
- Blockers (not hidden):
  1. No `.claude-plugin/marketplace.json` at the repo root.
  2. No `.claude-plugin/plugin.json` at the repo root; only the generated, ignored dir has one.
  3. The marketplace entry name must equal the `plugin.json` name (V:M).
  4. `source: "./"` for a root plugin is documented by wording only (A:V12).
  5. The hook command in `hooks/hooks.json` is unquoted (`${CLAUDE_PLUGIN_ROOT}/hooks/user-prompt-submit`, V:S). It breaks on install paths with spaces if the host substitutes naively (V:T row V4m). Whether Claude quotes the value is A:V3.

### 3.2 Codex

```text
codex plugin marketplace add sfc-gh-myoung/ai_coding_rules[@ref] [--sparse <path>]   # V:H
codex plugin add ai-coding-rules@<marketplace-name>                                   # V:H (plugin add takes a configured marketplace); exact argument form A:V1
codex plugin marketplace upgrade <marketplace-name>                                   # V:H; manual
codex plugin remove ai-coding-rules                                                   # V:H; remove the marketplace separately
```

- Start a **new** session after install; bundled skills appear only in new sessions (V:X).
- Enable the hook: Codex does not trust plugin hooks on install (V:X). A human reviews and trusts the exact hook definition in the TUI. Trust is by hash, so any change to the hook after an upgrade needs re-review. Confirmation: the review prompt completes and the positive injection check passes. The agent never answers that prompt and never passes `--dangerously-bypass-hook-trust`.
- Blockers:
  1. Needs a root `plugin.json` (or `.codex-plugin/plugin.json`) and a marketplace file under `.agents/plugins/marketplace.json` (or the compatible Claude file, A:V7).
  2. The hook command uses `${CLAUDE_PLUGIN_ROOT}`. Codex exports `PLUGIN_ROOT` and `CLAUDE_*` aliases to the hook env (V:X), but whether the command text is substituted is A:V7. The script's `dirname "$0"` fallback is the safety net (works for real files, V:T V4b-V4d, but not for a symlinked hook file, V:T V4j).
  3. "Installed" is not "active": the hook is skipped until trusted.
  4. `codex exec` hook-trust behavior is unknown (A:V7).
  5. The IDE extension has no plugin support (V:X).

### 3.3 CoCo CLI (Desktop: assumption)

```text
cortex plugin install github:sfc-gh-myoung/ai_coding_rules#<ref>   # shorthand grammar A:V1; stored form is V:R
cortex plugin list                                                 # V:H
cortex plugin validate ai-coding-rules                             # V:H
cortex plugin update ai-coding-rules                               # V:H; known update failures, see 8.1
cortex plugin uninstall ai-coding-rules                            # V:H
```

- Deliberate enablement path if consent is otherwise silent: install with `--inactive` (V:H), inspect, then `cortex plugin enable ai-coding-rules` (V:H command exists; effect on hooks A:V6). The hook-consent flow is undocumented (A:V6).
- Confirmation: `/hooks` listing (A:V6) plus the positive injection check.
- Blockers:
  1. Root-level plugin (no subpath) install is untested (A:V12).
  2. Manifest precedence when both `.cortex-plugin/` and `.claude-plugin/` exist is unknown (A:V1).
  3. Whether CoCo discovers `hooks/hooks.json` from a plugin and substitutes `${CLAUDE_PLUGIN_ROOT}` is secondhand (A:V3).
  4. Same-name install needs `--force` (V:H). The research machine had a dead `local:` registry entry for `ai-coding-rules` (inactive, path missing, V:R). Uninstall it first (section 10).
  5. Update failures were observed on other plugins (V:R). `cortex plugin update` must not be recommended until V9 reproduces and explains them (F8).
  6. Desktop plugin and hook behavior is secondhand (A:V3, F10).

## 4. Layout options and recommendation

Two layouts are considered. Each needs per-client adapters; none is a single file all clients read.

- **Option R (repo root is the plugin).** Add tracked manifests at the root. No `ai-coding-rules-plugin/`, no duplicated tree. Everything the hook needs is already tracked (V:S). Costs: the whole repository lands in each client cache (about 684 tracked files; tests, fixtures, templates and docs add roughly 2.2 MB, V:S), and the four maintainer skills (`rule-creator`, `rule-reviewer`, `bulk-rule-reviewer`, `skill-timer`, about 110 files) sit under `skills/` and are auto-discovered by Claude (V:P) and by CoCo's `skills: ["./skills"]` (V:S). Hiding them is A:V12. `--sparse` can shrink the checkout on Claude and Codex (V:H) but must then include `src/ai_rules/plugin/micro_kernel_content.md` (below).
- **Option S (subdirectory plugin with a committed generated tree, for example `plugins/ai-coding-rules/`).** Installs only the runtime files and hides maintainer skills. Costs: a second committed copy of about 195 rules and the skills, guarded only by a temp-dir rebuild diff (`plugin-verify.sh` already builds into a temp dir, V:S). Symlinks would avoid the copy but there are none in the repo (V:S) and client cache behavior with symlinks is unobserved (A:V12). Not recommended.

**Precondition finding (V0, `micro_kernel_content.md`).** The hook reads `$PLUGIN_ROOT/micro_kernel_content.md` and falls back to `$PLUGIN_ROOT/src/ai_rules/plugin/micro_kernel_content.md` (`hooks/user-prompt-submit:93-104`, V:T). The tracked primary is the `src/` copy. The root copy is generated only into the ignored dir. If neither exists, the hook still exits 0 and emits the path list, but drops the foundation text: 3.0 KB with the kernel versus 1.4 KB without (V:T V4e/V4f; 47 versus 20 output lines in the clone run, V:S). The matcher does not read the kernel. So Option R works as-is only while `src/` is installed, and any sparse or trimmed install must keep it or track a root copy under `sync --check`.

**Recommendation (conditional).** Prefer Option R, because it removes duplication and is the smallest change, **if and only if**:

1. V12 shows a root-level source (`source: "./"` or the client equivalent) installs on every client we intend to support (currently unrun; NOT YET RUN), and
2. the `micro_kernel_content.md` handling is settled: either installs always include `src/`, or a root copy is tracked and staleness-checked (V0 finding above), and
3. exposing the maintainer skills and the repo bulk is accepted, or V12 shows a per-client way to hide them.

If V12 fails on any client, or the exposure is unacceptable, fall back to Option S for that client with a committed generated tree checked in CI. Codex needs its own adapter files in either option (F9). No layout decision should be taken before V0 is recorded in the PR that implements F4.

Drafts of the adapter files are in [Appendix A](#appendix-a-draft-adapter-files-untested). They are untested.

## 5. Runtime-essential versus movable

| Item | Class | Evidence |
|---|---|---|
| `rules/*.md` (195 tracked) | Runtime-essential | hook `--rules-dir "$PLUGIN_ROOT/rules"` (V:S) |
| `skills/rule-loader/scripts/match_rules.py` | Runtime-essential; replica of `src/ai_rules/match_rules.py` kept by `plugin sync --check` | V:S |
| `skills/rule-loader/` SKILL.md, workflows, examples, references | Runtime (skill content) | V:S |
| `skills/show-rules/SKILL.md` | Runtime (skill); built as `required: no` today | V:S |
| `skills/shared/runtime-capabilities.md` | Runtime (copied by build); `reviewer-contract.md` is not | V:S |
| `hooks/hooks.json`, `hooks/user-prompt-submit` (mode 100755) | Runtime-essential | exec bit survives a clone (V:S) |
| Per-client manifests and marketplace files | Required for install; currently string literals in `plugin.py` | Movable to tracked files (F4) |
| `micro_kernel_content.md` | Runtime for foundation text; tracked primary in `src/`; hook silently degrades if absent | V:T |
| `python3` on PATH | Prerequisite; absent means silent exit 0 | V:T V5b |
| `jq` | Soft prerequisite; absent changes ranking because raw JSON becomes the prompt | V:T V5c |
| Version bump into manifests, replica refresh, release artifacts, `plugin verify` | Movable to release automation | F5, F6 |
| `.venv`, `uv`, `ai-rules` CLI, tests, reports, maintainer skills | Not runtime | V:S |
| `ai-rules plugin build/install` | Legacy developer path after F4 | decision deferred to F7 |

Manifest versions are literals `1.0.0` while the package is `4.0.0`, and no check compares them (V:S). Tracked manifests need a release step or a CI check (section 9).

## 6. Path resolution

Two uses of the working directory must not be confused.

- **Intentional cwd use:** the consuming project's files are matched against rule globs. The cwd selects which rules apply, not which rules directory is read.
- **Installed-root use:** rules, matcher, skills, hook and kernel come from the plugin root.

What the hook does (`hooks/user-prompt-submit`, V:T):

1. `PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd -P)}"`.
2. It passes an absolute `--rules-dir "$PLUGIN_ROOT/rules"` to the matcher.
3. The matcher returns logical `rules/<file>` paths (`match_rules.py:690`). The hook's realpath block (lines 69-86) rewrites them to `os.path.realpath($PLUGIN_ROOT/<rule>)` and markdown-escapes them.
4. The foundation rule is found by name in the loaded rules DB (`match_rules.py:1209`, `db.get("000-global-core.md")`), not by path.
5. The matcher CLI default `--rules-dir` is `Path("rules")`, cwd-relative (`match_rules.py:1163`). The hook path never uses it.

Direct-execution results on a hand-built install copy, no client involved (V:T, `run1.log`):

| Scenario | Result |
|---|---|
| Empty cwd with spaces, env set / unset (V4a, V4b) | PASS |
| cwd has no `rules/` (V4c, V4c2) | PASS |
| cwd is a checkout with its own `rules/` (V4d) | PASS; installed rules are used, cwd ignored |
| Source copy renamed away after install (V4g) | PASS |
| Install root is a symlink, env unset / set (V4h, V4i) | PASS; output shows the resolved real path |
| Install path with spaces and non-ASCII, env set / unset (V4k, V4l) | PASS |
| Hook **file** is a symlink, env unset (V4j) | **FAIL**: empty output, exit 0. `pwd -P` resolves the parent dir, not `$0` itself |
| Hook file is a symlink, env set (V4j2) | PASS |
| Unquoted `${CLAUDE_PLUGIN_ROOT}` command, spaced path (V4m) | exit 127 (breaks); quoted (V4n) PASS; unquoted, no spaces (V4o) PASS |
| `CLAUDE_PLUGIN_ROOT` set to the literal unsubstituted `${CLAUDE_PLUGIN_ROOT}` (V5e) | exit 0, empty output (silent) |

What this does not settle: whether any client substitutes or quotes `${CLAUDE_PLUGIN_ROOT}` in command text, and whether any client installs or caches the hook file as a symlink. Both are client-run rows (V3, V7).

**Gap: skill-only invocation.** `show-rules` and `rule-loader` examples use `--rules-dir ./rules` or repo-relative `rules/<name>.md` (`skills/rule-loader/SKILL.md`, `skills/show-rules/SKILL.md`; V:S, V:T). Outside a checkout, with no hook-injected root, those resolve against the consuming project's cwd and are wrong. Claude's plugin-root variables are not in the Bash-tool env (V:P), so a skill cannot read `CLAUDE_PLUGIN_ROOT` from a shell call; it must use a path the hook injected or its own base path. This is follow-up F3.

## 7. Invocation, automatic discovery and hook consent

Three layers, specified separately for each client.

| Layer | Claude Code | Codex | CoCo CLI | CoCo Desktop |
|---|---|---|---|---|
| 1. Explicit skill invocation | V:P `/ai-coding-rules:show-rules` | A:V2 `$show-rules`, new session needed (V:X) | A:V2 `$show-rules` | A:V2 |
| 2. Automatic skill discovery by description | V:P skills auto-loaded | A:V7 | V:R only through manifest `skills` | A:V1 |
| 3. Deterministic `UserPromptSubmit` hook | Declared in `hooks/hooks.json` (V:P); consent A:V6 | V:X skipped until per-hash trust | A:V3, consent A:V6 | A:V3 |
| Fallback if hook is not active | Skills only; rules load when the model chooses the skill | Skills only; hook dormant until trusted | Skills only | Skills only |

Layer 3 is the only mechanism that guarantees rule loading. A Git install can succeed while the hook is dormant, so validation asserts "hook fired and injected the expected path", never "plugin installed". Codex stdout from `UserPromptSubmit` becomes developer context (V:X); that the hook's `<system-reminder>` text is accepted as such is A:V3b. Hook stdin field names per client are A:V3b.

Consent is never bypassed (section 1). Per client, what the user does and how they confirm is in section 3.

## 8. Update, uninstall, cache and coexistence

### 8.1 Update and cache

- Claude: `plugin update`, then restart (V:H). Setting `version` in `plugin.json` pins users until bumped (V:P); omitted `version` uses the Git SHA (A:V11). Cache layout and retention: A:V10.
- Codex: `marketplace upgrade` is manual (V:H). Any change to the hook bytes changes the trust hash, so the update procedure includes re-review, and **V3 is re-run after V9** (V3 after update).
- CoCo: `plugin update [src]` (V:H). Observed `lastUpdateError` and `pendingUpgrade` on other plugins (V:R) must be reproduced (F8) before update is documented as supported.

### 8.2 Uninstall residue

Document and measure per client (V10): installed dir, registry or config entry, cache or clone, hook trust state, plugin data. Known: Claude keeps `${CLAUDE_PLUGIN_DATA}` unless `--keep-data` (V:P); the CoCo `remote_cache` clone and Codex marketplace snapshot are expected to remain (A:V10). **Removing a Claude marketplace uninstalls its plugins (V:M)**, so the uninstall procedure removes the plugin and does not remove a marketplace that other plugins share.

### 8.3 Coexistence and duplicate injection

Two hooks both emitting the rule manifest double-inject context. Rules:

1. Never run a CLI-managed (`ai-rules plugin install`) copy and a Git install active at the same time on one client.
2. Cross-client: a Claude-installed and a CoCo-installed copy on one machine can both fire in a client that reads both locations. The assertion is **exactly one manifest and rule injection per prompt** (V8).
3. CoCo same-name collision needs `--force` (V:H). The collision with a dead `local:` registry entry is reproduced synthetically in the scratch environment, never against the real registry (V8).
4. Claude: adding the same marketplace at user and project scope (V8) and a manual `~/.claude/skills/ai-coding-rules` copy next to the plugin (names are namespaced so they probably do not collide by name but may duplicate, A:V8).
5. Legacy install locations written by `ai-rules plugin install`: `~/.claude/skills/ai-coding-rules`, `<project>/.claude/plugins/ai-coding-rules`, and a CoCo local-path install (V:S).

## 9. CI rules for missing and stale content

Current state (V:S): CI uses `make plugin-verify` (`scripts/plugin-verify.sh optional`), which builds into a temp dir and verifies it, then **prints SKIPPED and passes** when `cortex` is absent. `plugin-verify-strict` fails instead. Nothing validates root manifests, marketplace JSON, `claude`/`codex` loaders, or an install from a clone. Manifest versions already drift (`1.0.0` versus `4.0.0`).

The CI design, as rules:

1. **Run against a clean clone or `git archive HEAD`, never the working tree.** Gitignored files make local checks pass where a fresh clone fails; that is the root problem of #36.
2. **Runtime paths must be tracked.** `git ls-files --error-unmatch` for each of: `rules/000-global-core.md` (and the rules tree), `skills/rule-loader`, `skills/shared`, `skills/show-rules`, `hooks/hooks.json`, `hooks/user-prompt-submit`, `skills/rule-loader/scripts/match_rules.py`, every manifest and marketplace file, and `micro_kernel_content.md` if the layout needs it. Also assert the hook's mode is `100755`, check `.gitattributes` for `export-ignore` (none exists today, V:S) and check for symlink entries (none today, V:S).
3. **SKIPPED is FAIL** unless the job explicitly declares that client optional. A job must never print SKIPPED and go green for a client it claims to support.
4. **Positive injection assertion.** The smoke passes only if injected output contains the expected absolute rule path under the installed root. Hook exit 0 with empty output is FAIL (five silent `exit 0` paths exist today, V:S, V:T V5).
5. **Version consistency.** Manifest `version` equals `pyproject.toml` version equals the CHANGELOG head; each marketplace entry name equals its `plugin.json` name.
6. **Replicas.** Under Option R, the `match_rules.py` replica stays under `plugin sync --check` and the `BUILD_COPIES` machinery is no longer needed for install. Under Option S, the committed generated tree is rebuilt into a temp dir and diffed against the commit.
7. **Two tiers.** The **static tier** (JSON and manifest validity, `git ls-files`, version and name checks, `claude plugin validate --strict` where the binary is available) always runs and never reports success with zero checks. The **client-run tier** (install from `file://` clone, hook fired) runs nightly or manually because client CLIs may not install in GitHub Actions. Record the client versions used in every client-run result.

These are implemented by F1, F5 and F6; #36 changes no CI.

## 10. Migration and rollback

Ordered, each step reversible. Run in a scratch environment first.

1. **Detect existing installs.** `claude plugin list`, `ls ~/.claude/skills/ai-coding-rules`, `codex plugin list`, `cortex plugin list`, and inspect `~/.snowflake/cortex/plugins/registry.json`.
2. **Remove the old install.** `ai-rules plugin uninstall`, or the client's own uninstall. On CoCo, remove any dead `local:` `ai-coding-rules` entry first (V:R existed on the research machine); otherwise a same-name install needs `--force`.
3. **Install from Git pinned to a tag or SHA** (pin forms are A:V11 until run).
4. **Verify**: hook fired with one injection per prompt, absolute installed paths, and use from outside a checkout (V3, V4).
5. **Rollback.** Uninstall the Git install (and its marketplace only if nothing else uses it), reinstall the previous pinned ref, or run `ai-rules plugin install --force` from a checkout.

`ai-rules plugin build/install` stays supported as a fallback for one release; its deprecation is decided in F7. The rollback path is itself unverified (V10).

## 11. Validation matrix

"Who" is the person or agent allowed to run the row. Agent rows run only direct hook executions inside a `mktemp -d` under `$TMPDIR` and never invoke a client. Every client command runs in a human-run scratch environment (`HOME`, `XDG_CONFIG_HOME`, `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, `SNOWFLAKE_HOME` pointing at scratch) with a before/after snapshot of the real `~/.claude`, `~/.codex`, `~/.snowflake`; any diff aborts. Scratch isolation of each client is itself an assumption proven per client by read-only commands first. A scratch HOME has no auth, so prompts that spend credits are human-run.

All client-run rows use a `file://` Git URL created by `git clone --no-hardlinks` plus `git remote remove origin` (a plain local path is read in place and is not a Git install). Record the source form used by every run. One separate human row uses real GitHub shorthand. Log paths are under `docs-git-sourced-plugin-install-36/.workbench/issue-36/` (untracked); the kit is `human-run/` there, with `README.md` giving the order.

| ID | What it checks | Who | Status | Log or script |
|---|---|---|---|---|
| V0 | Baseline: no tracked plugin dir, ignored dir, `hooks.json` text, `micro_kernel_content.md` provenance and runtime use, matcher defaults | agent | PASS | `v0-v4-v5.sh`, `run1.log`, `results-v0-v4-v5.md` |
| V1 | Clean Git install per client from a `file://` source | human | NOT YET RUN | `bash human-run/20-v1-git-install.sh` |
| V1b | Install from real GitHub shorthand | human | NOT YET RUN | manual, same commands as section 3 |
| V2 | Skill files at the installed path; live invocation | human | NOT YET RUN | `bash human-run/21-v2-skill-invocation.sh`, then manual V2b |
| V3 | Installed hook run directly with synthetic JSON from an empty cwd, env unset and set, spaced and non-ASCII path, symlinked hook; consent observed | human | NOT YET RUN | `bash human-run/22-v3-hook-direct.sh` |
| V3b | Probe prompts through `claude -p`, `codex exec`, `cortex -p` (spends credits) | human | NOT YET RUN | `ISSUE36_ALLOW_CREDITS=1 bash human-run/23-v3b-probe-prompts.sh` |
| V4 (direct) | Outside the checkout, path forms, symlinked root, hook symlink, spaces, unquoted command | agent | FAIL (V4j: symlinked hook file with env unset gives empty output; V4m is an expected break of the unquoted command on a spaced path; every other sub-row PASS) | `run1.log`, `results-v0-v4-v5.md` |
| V4 (client) | Same assertions through each installed client | human | NOT YET RUN | rows 3 and 5 of the kit |
| V5 (direct) | No false green: matcher, `rules/`, python and unsubstituted variable each produce rc 0 and empty output, detected by the harness only through the missing path (jq-absent still passes) | agent | PASS (harness detects; hook itself is silent, see F2) | `run1.log`, `results-v0-v4-v5.md` |
| V5 (client) | Same through an installed client copy | human | NOT YET RUN | rows 3 and 5 of the kit |
| V6 | Consent observation on Claude and CoCo (prompt, `/hooks`, silent) | human | NOT YET RUN | `bash human-run/24-v6-consent-checklist.sh` |
| V7 | Codex: command-text substitution, `exec` trust, compat marketplace file, manifest-less root | human | NOT YET RUN | `bash human-run/25-v7-codex-specifics.sh` |
| V8 | Coexistence: double marketplace add, legacy copy, dead `local:` entry, exactly one injection | human | NOT YET RUN | `bash human-run/26-v8-coexistence.sh` |
| V9 | Update from v0.0.1 to v0.0.2, re-trust, reproduce `lastUpdateError`; V3 rerun after | human | NOT YET RUN | `bash human-run/27-v9-update.sh` |
| V10 | Uninstall residue per client; marketplace removal side effects | human | NOT YET RUN | `bash human-run/28-v10-uninstall.sh` |
| V11 | Pin by tag, SHA and Claude entry `sha` | human | NOT YET RUN | `bash human-run/29-v11-pin.sh` |
| V12 | Root source `./`, `--sparse`, installed size, exposed skills | human | NOT YET RUN | `bash human-run/30-v12-sparse-root.sh` |

Results are recorded in the format of [results-template.md](results-template.md). The kit's command grammar is marked `# UNCONFIRMED` where guessed; a failure on such a command can mean the grammar is wrong, not that the capability is missing. A missing binary, a SKIPPED step, empty hook output or an unanswered question is always FAIL.

## 12. Open questions

Answers to the issue's questions, as far as evidence allows:

1. **Which Git-source forms and layouts does each client support?** Section 2. Subdirectory plugins on CoCo are observed; root plugins on all three are NOT YET RUN (V12).
2. **Does Codex support native Git-sourced plugins?** Yes (V:H, V:X) with its own schema; it is not at parity, and the IDE extension does not support plugins (V:X). Whether our repo works unmodified on Codex is conditional on V7.
3. **Which prerequisites are unavoidable, and how are missing ones reported?** `bash` and `python3` are required; `jq` is soft. Today, missing ones are reported not at all (silent exit 0, V:T V5). Reporting is F2.
4. **How is a Git-installed hook enabled deliberately without `--with-hook`?** Per client in section 3: Codex hash review; Claude and CoCo A:V6; CoCo `--inactive` then `enable`. No bypass is used.
5. **Should existing build and install commands remain?** Keep as a fallback for one release; decision in F7.

Remaining unknowns:

- CoCo Desktop plugin and hook behavior (F10).
- Whether the foundation text must be kept when sparse-installing (V0 finding, V12).
- Whether `file://` is accepted by each client (A:V1).
- Hook stdin field names and stdout injection format on Claude and CoCo (V3b).

## 13. Follow-up issues

None of this is done in #36. They are filed after the human-run rows report. Sizes are relative (S/M/L).

| ID | Title | Goal | Size | Depends on |
|---|---|---|---|---|
| F1 | Add a verification harness for Git-sourced install | Promote the V0-V5 checks from the throwaway kit to a supported smoke command | S | #36 |
| F2 | Make hook failures visible | `hooks/user-prompt-submit` emits a diagnostic when the matcher, `rules/` or python is missing, or the kernel is absent, instead of a silent `exit 0` | M | F1 (consumes V5) |
| F3 | Resolve rules from the installed root | `show-rules` and `rule-loader` stop assuming `./rules` outside a checkout | M | #36 section 6 |
| F4 | Implement the layout (R or S) | Tracked manifests and marketplace files; Codex adapter if required; remove templated manifests from `build()`; keep `ai-rules plugin build/install` as legacy | L | F1, F3, V0 and V12 results, F9 if Codex is supported |
| F5 | CI staleness and manifest checks | Static tier and client-run tier from section 9 | M | F1, F4 |
| F6 | Release automation | Version bump into all manifests, tag-based pinning docs, `cut-release` integration | S | F4, F5 |
| F7 | User docs and migration guide | README and usage docs per client; migration and rollback from section 10; decide the legacy command's fate | S | F4, F6 |
| F8 | CoCo update failure investigation | Reproduce `lastUpdateError` / `pendingUpgrade`; file upstream if it is a CoCo bug | S | V9 |
| F9 | Codex adapter | Root `plugin.json` and `.agents/plugins/marketplace.json`, default expectation; or document Codex as unsupported with the reason | S | V7 |
| F10 | Verify CoCo Desktop plugin and hook behavior | Replace the secondhand claim with a human-run result | S | none |
| F11 | Client-version re-verification cadence | Record who re-runs the matrix and when | S | #36 |

Acceptance criteria (each testable):

- **F1:** a smoke command exits non-zero on empty hook output; the V5 negative test fails as designed; it refuses to run when `HOME` is not a temp dir; it records client versions.
- **F2:** removing `match_rules.py` or `python3` yields a visible diagnostic, with a test in `tests/test_plugin/test_hook_integration.py`; the normal path output is byte-identical.
- **F3:** `show-rules` and `rule-loader` emit absolute installed paths from an empty cwd outside a checkout, tested with cwd set to a temp dir.
- **F4:** a fresh `git clone` installs on each supported client per the matrix; `git ls-files` contains every runtime path; `tests/test_plugin` is updated; `ai-coding-rules-plugin/` is no longer needed.
- **F5:** CI fails on a deliberately stale manifest version, a mismatched marketplace name and a SKIPPED client check; it passes on a clean tree.
- **F6:** a tag produces pinned install instructions; the version bump touches all manifests; a `cut-release` dry run passes.
- **F7:** README and migration steps are copy-paste runnable in a scratch HOME, including uninstall of the old install and rollback.
- **F8:** repro steps or an upstream ticket for `lastUpdateError` / `pendingUpgrade`, with the outcome recorded.
- **F9:** the Codex hook fires after trust in a scratch `CODEX_HOME`, or Codex is documented as unsupported with the reason.
- **F10:** a human-run record shows whether a plugin installs and its hook fires on CoCo Desktop, with the version used.
- **F11:** the cadence and an owner are written down, and the doc header points at them.

Order: F1, then F2 and F3 in parallel, then F4, then F5 and F6, then F7. F8, F9, F10 and F11 run in parallel after #36. F4 additionally needs the V0 and V12 results from #36.

## Appendix A: Draft adapter files (untested)

**DRAFT / UNTESTED.** These are the files the human-run kit commits on a scratch branch of a throwaway clone. They are not committed to this repository. Names, fields and the Codex `source` object shape are guesses until V1, V7 and V12 run. The scratch values (`ai-coding-rules-eval`, `0.0.1`) are placeholders; the real marketplace name is chosen in F4.

`.claude-plugin/plugin.json`

```json
{
  "name": "ai-coding-rules",
  "version": "0.0.1",
  "description": "DRAFT/UNTESTED issue-36 eval adapter"
}
```

`.claude-plugin/marketplace.json`

```json
{
  "name": "ai-coding-rules-eval",
  "owner": { "name": "issue-36-eval" },
  "plugins": [
    { "name": "ai-coding-rules", "source": "./", "description": "DRAFT/UNTESTED root-level plugin (source ./)" }
  ]
}
```

`.cortex-plugin/plugin.json`

```json
{
  "name": "ai-coding-rules",
  "version": "0.0.1",
  "description": "DRAFT/UNTESTED issue-36 eval adapter",
  "skills": ["./skills"]
}
```

`plugin.json` (Codex root manifest)

```json
{
  "name": "ai-coding-rules",
  "version": "0.0.1",
  "description": "DRAFT/UNTESTED issue-36 eval adapter (Codex root plugin.json)"
}
```

`.agents/plugins/marketplace.json` (Codex)

```json
{
  "name": "ai-coding-rules-eval",
  "plugins": [
    {
      "name": "ai-coding-rules",
      "source": { "source": "local", "path": "./" },
      "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
      "category": "Developer Tools"
    }
  ]
}
```

None of these sets a hook key, matching the current generated manifests (hooks come from `hooks/hooks.json`). Real manifest versions would come from `pyproject.toml` (F6).

## Appendix B: Issue #36 acceptance criteria checklist

| # | Acceptance criterion | Where | Status |
|---|---|---|---|
| 1 | Versioned capability matrix citing official docs, with evidence or explicit gaps per client | Header, section 2 | Partly satisfied. Versions and evidence tags are recorded; many cells are assumptions pending V1-V12. CoCo Desktop is entirely unverified. |
| 2 | Exact proposed install procedure per client without the project CLI or a local build; unsupported requirements documented as blockers | Section 3 | Partly satisfied. Commands and blockers are given. None has been run; several arguments are A. The repo cannot be installed today without the adapter files (blocker, not marked complete). |
| 3 | Required tracked artifacts, canonical sources, and how CI detects missing or stale content | Sections 4, 5, 9 | Satisfied as design. Nothing implemented (F4, F5). |
| 4 | How `rule-loader`, `show-rules`, matcher, rules and foundation resolve from the installed location, not cwd | Section 6 | Partly satisfied. Hook path verified by direct execution (V4, with one expected FAIL, V4j). Skill-only invocation is an identified gap (F3). Client behavior is NOT YET RUN. |
| 5 | Automatic discovery, hook consent and fallback, separately per client | Section 7, section 3 | Partly satisfied. Codex consent is verified from docs; Claude and CoCo consent are assumptions (V6). |
| 6 | Validation covers clean install, skill invocation, enabled hook, outside the checkout, update, uninstall; no false green | Sections 9, 11 | Designed. Only V0, V4 (direct) and V5 (direct) have run; all client rows are NOT YET RUN. |
| 7 | Migration guidance: CLI-managed installs, duplicates, prerequisites, rollback | Sections 8, 10 | Satisfied as design; rollback is unverified (V10). |
| 8 | Issue links the design and scoped follow-up work before closure | Section 13 | **Not satisfied yet.** The follow-ups are specified here, but they are not filed and the issue is not updated with links. That happens after the human-run rows report. |
