# Example: DaisyUI Frontend Framework Rule Creation

## User Request

```
Create a new Cursor rule documenting DaisyUI best practices following schema
```

## Complete Workflow Execution

### Phase 1: Discovery & Research

**Step 1.1: Extract Technology**
- Technology: DaisyUI
- Aspect: core (default for foundational rule)
- Related: Tailwind CSS, components, UI library

**Step 1.2: Search RULES_INDEX.md**
```bash
$ grep -i "daisyui" RULES_INDEX.md
# No results - new technology

$ grep -i "javascript\|tailwind\|frontend" RULES_INDEX.md
|| `420-javascript-core.md` | JavaScript and frontend foundations | ...
|| `421-javascript-alpinejs-core.md` | Alpine.js 3.x usage | ...
```

**Step 1.3: Analyze Results**
- Domain pattern: 420, 421 → domain is 420-449 (JavaScript/Frontend)
- Next available: 422 (after 421, before 430)

**Step 1.4: Load Domain Core**
```
Reading rules/420-javascript-core.md for JavaScript/Frontend context...
```

**Step 1.5: Web Research**
```
Search 1: "2024 2025 DaisyUI best practices"
Search 2: "DaisyUI official documentation component guide"
Search 3: "DaisyUI common mistakes pitfalls"
Search 4: "DaisyUI theme customization optimization"
```

**Key Findings:**
- Semantic HTML with Tailwind utilities
- Theme customization via CSS variables
- Accessibility-first component approach
- Zero runtime JavaScript overhead
- Component composition patterns
- data-theme attribute for theme switching

**Step 1.6: Extract Keywords (15)**
```
daisyui, tailwind, components, ui library, themes, accessibility,
semantic html, css variables, responsive design, customization,
utility-first, design system, best practices, patterns, optimization
```

**Step 1.7: Essential Patterns (4)**
1. Use semantic HTML elements with DaisyUI classes
2. Apply themes via data-theme attribute and CSS variables
3. Leverage zero-JS components for performance
4. Compose complex UIs from base components

**Step 1.8: Anti-Patterns (3)**
1. Using !important to override component styles
2. Not testing theme color contrast
3. Mixing DaisyUI with other component libraries

**Step 1.9: External References**
- https://daisyui.com/docs/
- https://daisyui.com/components/
- https://github.com/saadeghi/daisyui

 **Phase 1 Complete**

---

### Phase 2: Template Generation

**Step 2.1: Determine ContextTier**
- New technology rule: Medium
- Not foundational (not Critical/High)
- Not specialized/rare (not Low)
- **Selected: Medium**

**Step 2.2: Execute ai-rules new**
```bash
$ uv run ai-rules new 422-daisyui-core \
    --context-tier Medium \
    --output-dir rules/

 Created rule template: rules/422-daisyui-core.md

Next steps:
1. Edit rules/422-daisyui-core.md and replace all placeholders
2. Validate: uv run ai-rules validate rules/422-daisyui-core.md
3. Add to RULES_INDEX.md
```

**Step 2.3: Verify Template**
```bash
$ ls -lh rules/422-daisyui-core.md
-rw-r--r--  1 user  staff   3.2K Dec 11 15:30 rules/422-daisyui-core.md

$ grep -c "^## " rules/422-daisyui-core.md
9  # All 9 required sections present 

$ grep -c "<inputs_prereqs>\|<mandatory>\|<forbidden>\|<steps>\|<output_format>\|<validation>" rules/422-daisyui-core.md
6  # All 6 Contract XML tags present 

$ grep -n "^## Contract" rules/422-daisyui-core.md
35:## Contract  # Before line 160 
```

 **Phase 2 Complete**

---

### Phase 3: Content Population

**Step 3.1: Update Metadata**
```markdown
## Metadata

**SchemaVersion:** v3.0
**Keywords:** daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization, utility-first, design system, best practices, patterns, optimization
**TokenBudget:** ~1200
**ContextTier:** Medium
**Depends:** rules/000-global-core.md, rules/420-javascript-core.md
```

**Step 3.2: Write Purpose**
```markdown
## Purpose

Establishes best practices for DaisyUI component library usage, covering theme customization, accessibility patterns, and semantic HTML integration with Tailwind CSS utilities for building consistent, performant user interfaces.
```

**Step 3.3: Write Rule Scope**
```markdown
## Rule Scope

All web applications using DaisyUI v4.0+ component library for UI development with Tailwind CSS v3.0+.
```

**Step 3.4: Write Quick Start TL;DR**
```markdown
## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Semantic HTML first:** Use native HTML elements with DaisyUI classes rather than div-soup for better accessibility and SEO
- **Theme via data-theme:** Apply themes using data-theme attribute on HTML element for automatic color scheme switching
- **Zero-JS components:** Leverage DaisyUI's CSS-only components for better performance
- **Component composition:** Build complex UI by composing base components rather than overriding styles

**Pre-Execution Checklist:**
- [ ] Tailwind CSS v3.0+ installed and configured
- [ ] DaisyUI v4.0+ added to Tailwind plugins
- [ ] Project uses semantic HTML structure
- [ ] Understanding of utility-first CSS principles
- [ ] Accessibility requirements defined (WCAG level)
```

**Step 3.5: Fill Contract** *(shortened for brevity - all 6 XML tags filled)*

**Step 3.6: Write Anti-Patterns** *(2 complete anti-patterns with code examples)*

**Step 3.7-3.10: Complete remaining sections...**

 **Phase 3 Complete** - All placeholders replaced with real content

---

### Phase 4: Validation Loop

**Iteration 1:**
```bash
$ uv run ai-rules validate rules/422-daisyui-core.md

================================================================================
VALIDATION REPORT: rules/422-daisyui-core.md
================================================================================

SUMMARY:
   CRITICAL: 1
    HIGH: 0
  ℹ️  MEDIUM: 0
   Passed: 457 checks

 CRITICAL ISSUES (1):
────────────────────────────────────────────────────────────────────────────────
[Metadata] Keywords count: 14 (expected 10-15)
  Line: 5
  Fix: Keywords count is within range, but validator detected as 9 - recount

RESULT:  FAILED (exit code 1)
```

**Fix Applied:**
Recounted keywords - actually had 9, needed 10-15. Added "component-design" keyword.

**Iteration 2:**
```bash
$ uv run ai-rules validate rules/422-daisyui-core.md

================================================================================
VALIDATION REPORT: rules/422-daisyui-core.md
================================================================================

SUMMARY:
   CRITICAL: 0
    HIGH: 0
  ℹ️  MEDIUM: 1
   Passed: 458 checks

ℹ️  MEDIUM ISSUES (1):
────────────────────────────────────────────────────────────────────────────────
[Output Format] Could include additional code examples for completeness

RESULT:   WARNINGS ONLY (exit code 0)
```

 **Phase 4 Complete** - Validation passed (exit code 0)

---

### Phase 5: Indexing

**Step 5.1: Format Index Entry**
```markdown
| 422-daisyui-core | DaisyUI component library patterns and best practices | daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization | rules/420-javascript-core.md |
```

**Step 5.2: Determine Insertion Position**
```bash
$ grep "^|| \`42[0-9]-\|^|| \`43[0-9]-" RULES_INDEX.md
|| `420-javascript-core.md` | ...
|| `421-javascript-alpinejs-core.md` | ...
|| `430-typescript-core.md` | ...

# Insert after 421, before 430
```

**Step 5.3: Insert Entry**
*Entry added to RULES_INDEX.md between lines for 421 and 430*

**Step 5.4: Verify**
```bash
$ grep "422-daisyui-core" RULES_INDEX.md
|| `422-daisyui-core.md` | DaisyUI component library patterns and best practices | daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization | rules/420-javascript-core.md |

 Entry added successfully
 Numeric order maintained (421 → 422 → 430)
 Table formatting intact
```

 **Phase 5 Complete** - Rule indexed

---

## Final Output

```
 Production-ready rule created: rules/422-daisyui-core.md

File Details:
- Location: rules/422-daisyui-core.md
- Size: ~18KB (approximately 450 lines)
- TokenBudget: ~1200 tokens
- Validation: 0 CRITICAL errors, 0 HIGH errors
- Indexed: Yes (RULES_INDEX.md updated)

Ready for use: rules/422-daisyui-core.md
```

## Key Takeaways

**What Worked Well:**
- Domain detection was clear (420-449 for frontend)
- Web research provided current best practices
- ai-rules new created perfect structure
- Validation caught keyword count issue early
- Passed validation on iteration 2 (within 3 attempt limit)

**Challenges:**
- Initial keyword count was off by 1 (easy fix)
- Had to research DaisyUI v4.0 specifics (2024 release)
- Needed to distinguish from similar libraries (Alpine.js)

**Time Estimate:**
- Phase 1 (Discovery): ~5 minutes
- Phase 2 (Template): ~1 minute
- Phase 3 (Population): ~10 minutes
- Phase 4 (Validation): ~2 minutes (2 iterations)
- Phase 5 (Indexing): ~1 minute
- **Total: ~19 minutes**

**Comparison to Manual:**
- Manual rule creation: ~45-60 minutes
- With script orchestration: ~19 minutes
- **Time savings: ~65% faster**

