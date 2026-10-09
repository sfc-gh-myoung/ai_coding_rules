---
schema_version: v4.0
rule_version: v3.0.0
description: "Reveal.js 6 presentations: pinned current release, valid slide hierarchy, ESM plugin registration, safe content, theming and browser-verified navigation/export."
last_updated: 2026-10-07
keywords:
  - kw:reveal.js 6.0.0
  - kw:slide markup hierarchy
  - kw:code highlighting data-trim
  - kw:plugin registration ESM
  - kw:fragments auto-animate
  - kw:speaker notes view
  - kw:theme CSS custom properties
token_budget: ~1100
context_tier: Medium
depends:
  required:
    - 000-global-core.md  # Foundation for all rules
  optional:
    - 420-javascript-core.md  # ESM and modern JavaScript standards (load if writing custom Reveal.js plugins or extensive JS logic)
    - 501-frontend-browser-globals-collisions.md  # Relevant when embedding Reveal.js alongside other frontend libraries
---
# Reveal.js Presentations

## Scope

**What This Rule Covers:**
Reveal.js 6 setup (npm/ESM or distributed files), `.reveal > .slides > section` markup, vertical slides, fragments, auto-animate, Markdown, code highlighting, plugins, configuration, themes, speaker notes and PDF export.

**When to Load This Rule:**
When creating, modifying or troubleshooting Reveal.js decks; load `501-frontend-browser-globals-collisions.md` when embedding alongside other libraries.

## Contract

### Inputs and Prerequisites

- Existing deck, installed Reveal.js version and delivery (npm/bundler, cloned full setup or vendored dist files), and any custom themes or plugins.
- Node.js version where npm or the full setup is used (current docs require 20.19+), target browsers, hosting, offline needs and export requirements.

### Mandatory

- For new decks use Reveal.js 6 pinned to an exact current patch release from the npm registry or GitHub releases (6.0.2 was latest when verified); keep an existing deck's version unless upgrading is in scope, and read the release notes before any upgrade.
- Load Reveal and plugins once: ESM imports with `new Reveal({ plugins: [...] })` then `initialize()`, or dist scripts with `Reveal.initialize({ plugins: [...] })`. Never use the removed `dependencies` array or register a plugin whose module was not loaded.
- Keep the `.reveal > .slides > section` hierarchy; vertical stacks are nested sections, one level deep.
- Load `reveal.css`, exactly one theme and at most one highlight theme; customize through documented `--r-*` CSS custom properties or a custom theme, never by editing vendored source.
- Code blocks use explicit `language-*` classes, `data-trim` where indentation is source-aligned, and `data-line-numbers` steps only with valid ranges; escape HTML or wrap it in `<script type="text/template">`.
- Do not construct slide HTML or Markdown from untrusted input, and do not include secrets, credentials or private data in slides, notes or embedded iframes.
- External Markdown, Notes and some media require serving over HTTP; use the full setup or a local static server rather than `file://`.
- Configure only needed options; `history` writes browser history, `autoSlide` needs a pause control, and `hash` controls bookmarkable positions.
- Slides are accessible: semantic headings, alt text for images, sufficient contrast, readable font sizes, and fragments/transitions that do not hide essential content; respect reduced-motion where custom animation is added.
- Use `data-src` lazy loading for heavy iframes and media; host fonts and assets locally when the deck must work offline.
- Verify in a browser: no console errors, horizontal/vertical navigation, fragments order, speaker notes (`S`), overview (`O`) and `?print-pdf` export; do not claim rendering from markup review alone.

### Execution Steps

1. Read existing deck, version, delivery method, theme and plugins; confirm the content and output targets.
2. Implement minimal markup, configuration, plugin and theme changes within the supported version.
3. Run available lint/build and serve the deck to verify navigation, notes, code highlighting and PDF export.
4. Report version, files changed, verification evidence and any unverified browsers or export issues.

### Validation

- Exact Reveal 6 version pinned (or existing version preserved); no `dependencies` array.
- Valid slide hierarchy; one theme; plugins imported and registered.
- Code blocks have explicit languages and escaped HTML; no untrusted content or secrets.
- Browser navigation, notes and export verified or explicitly marked unverified.

## References

- [Reveal.js installation](https://revealjs.com/installation/)
- [Markup](https://revealjs.com/markup/)
- [Config options](https://revealjs.com/config/)
- [Plugins](https://revealjs.com/plugins/)
- [Code](https://revealjs.com/code/)
- [Themes](https://revealjs.com/themes/)
- [PDF export](https://revealjs.com/pdf-export/)
