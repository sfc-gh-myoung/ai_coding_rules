# Phase 3: Content Population Workflow

## Purpose

Replace all placeholder content in the template with researched, high-quality content that reflects 2024-2025 best practices, ensuring all schema requirements are met.

## Inputs

From Phase 1:
- 10-15 semantic keywords
- 3+ essential patterns
- 2+ anti-patterns with correct alternatives
- External documentation links

From Phase 2:
- Template file: `rules/NNN-technology-aspect.md`
- All sections with placeholder content

## Outputs

- Fully populated rule file ready for validation
- All metadata fields filled correctly
- All required sections with real content
- Code examples in Anti-Patterns and Output Format Examples

## Content Population Sequence

### 3.1: Update Metadata (Lines 3-11)

Replace placeholder values:

```markdown
## Metadata

**SchemaVersion:** v3.0
**Keywords:** [REPLACE with 10-15 keywords from Phase 1]
**TokenBudget:** ~[ESTIMATE: lines × 2, round to 50]
**ContextTier:** [KEEP from template_generator.py]
**Depends:** rules/000-global-core.md, rules/[domain-core].md
```

**Keywords Format:**
- Exactly 10-15 comma-separated terms
- No quotes, no brackets
- Example: `daisyui, tailwind, components, ui library, themes, accessibility, semantic html, css variables, responsive design, customization, utility-first, design system, best practices, patterns, optimization`

**TokenBudget Estimation:**
- Quick formula: (expected_lines × 2) rounded to nearest 50
- Or count words: (words × 1.33) rounded to nearest 50
- Most new rules: ~1200 to ~1800
- Format: `~1200` (tilde required)

**Depends Field:**
- Always include: `rules/000-global-core.md`
- Add domain core: `rules/420-javascript-core.md` (for frontend)
- Add related rules if dependent on specific patterns

### 3.2: Write Purpose (1-2 Sentences)

**Template:**
```markdown
## Purpose

[What problem does this rule solve? Why is it important for [TECHNOLOGY] users?]
```

**Guidelines:**
- Be specific about the problem being solved
- Mention the technology by name
- Keep to 1-2 sentences maximum
- Focus on value proposition

**Example: DaisyUI**
```markdown
## Purpose

Establishes best practices for DaisyUI component library usage, covering theme customization, accessibility patterns, and semantic HTML integration with Tailwind CSS utilities for building consistent, performant user interfaces.
```

### 3.3: Write Rule Scope (1 Line)

**Template:**
```markdown
## Rule Scope

[Define exact applicability: technologies, contexts, use cases]
```

**Guidelines:**
- Single line only
- Define who should use this rule
- Be specific about context
- Mention versions if relevant

**Example: DaisyUI**
```markdown
## Rule Scope

All web applications using DaisyUI v4.0+ component library for UI development with Tailwind CSS v3.0+.
```

### 3.4: Write Quick Start TL;DR

**Template:**
```markdown
## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **[Pattern 1 name]:** [Actionable description]
- **[Pattern 2 name]:** [Actionable description]
- **[Pattern 3 name]:** [Actionable description]
[Add more as needed - no maximum]

**Pre-Execution Checklist:**
- [ ] [Prerequisite 1]
- [ ] [Prerequisite 2]
- [ ] [Prerequisite 3]
- [ ] [Prerequisite 4]
- [ ] [Prerequisite 5]
[5-7 items recommended]
```

**Essential Patterns Guidelines:**
- Minimum 3, no maximum
- Use bold for pattern names
- Make descriptions actionable (developers can apply immediately)
- Draw from Phase 1 research findings
- Each pattern should be a core best practice

**Pre-Execution Checklist Guidelines:**
- 5-7 items recommended
- Verify prerequisites (dependencies installed, configs present)
- Check understanding (concepts, terminology)
- Confirm access (permissions, files)
- Use checkbox format: `- [ ] Item`

**Example: DaisyUI**
```markdown
## Quick Start TL;DR

**MANDATORY:**
**Essential Patterns:**
- **Semantic HTML first:** Use native HTML elements with DaisyUI classes rather than div-soup for better accessibility and SEO
- **Theme via data-theme:** Apply themes using data-theme attribute on HTML element for automatic color scheme switching
- **Zero-JS components:** Leverage DaisyUI's CSS-only components (collapse, modal, dropdown) for better performance
- **Component composition:** Build complex UI by composing base components rather than overriding styles
- **Utility-first styling:** Use Tailwind utilities alongside DaisyUI classes for custom spacing and layout

**Pre-Execution Checklist:**
- [ ] Tailwind CSS v3.0+ installed and configured
- [ ] DaisyUI v4.0+ added to Tailwind plugins
- [ ] Project uses semantic HTML structure
- [ ] Understanding of utility-first CSS principles
- [ ] Accessibility requirements defined (WCAG level)
- [ ] Theme color palette defined
```

### 3.5: Fill Contract Section

**All 6 XML tags must be populated:**

```markdown
## Contract

<inputs_prereqs>
[Replace with: What agent needs before starting]
Example: Project using [TECHNOLOGY] v[VERSION]; configuration files; understanding of [concepts]
</inputs_prereqs>

<mandatory>
[Replace with: Required tools, libraries, permissions]
Example: [TECHNOLOGY] v[VERSION]+; [related tools]; text editor; terminal access; [specific access]
</mandatory>

<forbidden>
[Replace with: Prohibited actions, approaches, anti-patterns]
Example: Don't use deprecated [X]; don't skip [Y]; don't hardcode [Z]; avoid [anti-pattern]
</forbidden>

<steps>
1. [Replace with specific, sequential, actionable step]
2. [Second step - must be achievable]
3. [Third step]
4. [Fourth step]
5. [Fifth step]
[5-10 steps total - not too granular, not too high-level]
</steps>

<output_format>
[Replace with: Expected output description - file type, structure, validation method]
Example: [TECHNOLOGY] configuration file with [structure]; UI component with [properties]; tested with [tool]
</output_format>

<validation>
[Replace with: How to verify success - specific commands and checks]
Example: Run [command]; verify [output shows X]; check [file contains Y]; test [behavior Z works]
</validation>
```

**Example: DaisyUI (complete Contract)**
```markdown
## Contract

<inputs_prereqs>
Web application project using Tailwind CSS v3.0+; tailwind.config.js file; understanding of utility-first CSS and component composition
</inputs_prereqs>

<mandatory>
DaisyUI v4.0+ installed as Tailwind plugin; modern browser for testing; HTML/CSS knowledge; PostCSS configured
</mandatory>

<forbidden>
Don't use inline styles to override DaisyUI components; don't mix DaisyUI with other component libraries; don't use !important to force styles; avoid deprecated v3.x theme syntax
</forbidden>

<steps>
1. Install DaisyUI and add to Tailwind plugins in tailwind.config.js
2. Configure themes array with custom color schemes if needed
3. Apply data-theme attribute to HTML element for theme selection
4. Build UI using semantic HTML with DaisyUI component classes
5. Test theme switching and responsive behavior across breakpoints
6. Validate accessibility with screen readers and keyboard navigation
7. Optimize bundle size by purging unused components
</steps>

<output_format>
HTML templates with semantic structure, DaisyUI component classes, and Tailwind utilities; CSS output with configured themes; passes WCAG 2.1 AA accessibility checks
</output_format>

<validation>
Run `npm run build` and verify CSS bundle includes only used components; test theme switching with data-theme changes; validate with axe DevTools for accessibility; check responsive behavior at 640px, 768px, 1024px breakpoints
</validation>
```

### 3.6: Write Anti-Patterns Section

**Minimum 2 anti-patterns required, each with:**
- Problem description
- Code example (wrong)
- Why it fails (3 reasons)
- Correct pattern
- Code example (right)
- Benefits (3 benefits)

**Template per anti-pattern:**
```markdown
### Anti-Pattern N: [Descriptive Name]

**Problem:** [What developers do wrong - specific behavior]

```[language]
// Wrong approach code example
[Show incorrect pattern with context]
```

**Why It Fails:**
- [Technical consequence]
- [Maintenance issue]
- [Performance/security concern]

**Correct Pattern:**

```[language]
// Right approach code example
[Show correct pattern with context]
```

**Benefits:**
- [Solves technical issue]
- [Improves maintainability]
- [Enhances performance/security]
```

**Example: DaisyUI Anti-Pattern**
```markdown
### Anti-Pattern 1: Overriding Component Styles with !important

**Problem:** Using !important to force custom styles on DaisyUI components instead of using theme customization.

```css
/* Wrong: Using !important to override button colors */
.btn-primary {
  background-color: #custom-blue !important;
  border-color: #custom-blue !important;
}
```

**Why It Fails:**
- Breaks theme switching functionality - !important overrides theme variables
- Creates specificity wars requiring more !important declarations
- Prevents responsive color scheme changes (light/dark mode)

**Correct Pattern:**

```javascript
// tailwind.config.js - Extend theme colors properly
module.exports = {
  daisyui: {
    themes: [
      {
        mytheme: {
          primary: "#custom-blue",
          "primary-focus": "#0056b3",
          "primary-content": "#ffffff",
        },
      },
    ],
  },
}
```

**Benefits:**
- Theme switching works correctly across all components
- Maintains proper CSS specificity hierarchy
- Supports dark mode and responsive color schemes automatically
```

### 3.7: Write Post-Execution Checklist

**5+ items, focused on verification after task completion:**

```markdown
## Post-Execution Checklist

- [ ] [Verification 1 - different from pre-execution]
- [ ] [Verification 2 - check implementation]
- [ ] [Verification 3 - test functionality]
- [ ] [Verification 4 - verify no regressions]
- [ ] [Verification 5 - check documentation]
[5-7 items, should verify completion quality]
```

**Example: DaisyUI**
```markdown
## Post-Execution Checklist

- [ ] DaisyUI components render correctly with semantic HTML
- [ ] Theme switching works via data-theme attribute changes
- [ ] All interactive components function without JavaScript errors
- [ ] Accessibility audit passes WCAG 2.1 AA (ran axe DevTools)
- [ ] Responsive behavior verified at mobile, tablet, desktop breakpoints
- [ ] CSS bundle size optimized (unused components purged)
- [ ] Documentation updated with theme customization examples
```

### 3.8: Write Validation Section

**Two parts required:**

```markdown
## Validation

**Success Checks:**
- [Specific check 1 with command/tool]
- [Specific check 2 with expected outcome]
- [Specific check 3 with measurement]

**Negative Tests:**
- [What should fail and why]
- [Edge case to verify]
- [Error scenario to test]
```

**Example: DaisyUI**
```markdown
## Validation

**Success Checks:**
- Run `npm run build` and verify output CSS < 50KB after purge
- Test theme switching: change data-theme attribute, verify colors update
- Accessibility audit: axe DevTools reports 0 violations
- Component functionality: all interactive elements work without JavaScript
- Responsive check: UI adapts correctly at 640px, 768px, 1024px

**Negative Tests:**
- Invalid theme name: data-theme="nonexistent" should fall back to default
- Missing PostCSS: build should fail with clear error about configuration
- Conflicting styles: !important in custom CSS should be flagged in code review
```

### 3.9: Write Output Format Examples

**Minimum 1 code block with examples:**

```markdown
## Output Format Examples

```bash
# Example command showing usage
[command with actual parameters]

# Expected output:
[realistic output showing success]
```

```[language]
# Example code showing correct implementation
[realistic code example]
```

**Example: DaisyUI**
```markdown
## Output Format Examples

```html
<!-- Example: Semantic HTML with DaisyUI components -->
<button class="btn btn-primary">
  Primary Action
</button>

<div class="card bg-base-100 shadow-xl">
  <div class="card-body">
    <h2 class="card-title">Card Title</h2>
    <p>Card content using semantic HTML and DaisyUI classes.</p>
    <div class="card-actions justify-end">
      <button class="btn btn-primary">Action</button>
    </div>
  </div>
</div>
```

```javascript
// tailwind.config.js - DaisyUI configuration
module.exports = {
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "dark", "cupcake"],
    darkTheme: "dark",
    base: true,
    styled: true,
    utils: true,
  },
}
```

### 3.10: Write References Section

**Two subsections required:**

```markdown
## References

### Related Rules
- `rules/000-global-core.md` - Global standards and conventions
- `rules/[domain-core].md` - Domain foundation
- `rules/[related].md` - Related patterns

### External Documentation
- [Official Docs](URL) - Official documentation
- [Community Guide](URL) - Community best practices
- [Tutorial](URL) - Getting started guide
```

**Note:** Related Rules can use bare filenames (e.g., `000-global-core.md`) or include the `rules/` prefix. The rules location is defined in AGENTS.md for token efficiency.

**Example: DaisyUI**
```markdown
## References

### Related Rules
- `000-global-core.md` - Global standards and conventions
- `420-javascript-core.md` - JavaScript and frontend foundations
- `421-javascript-alpinejs-core.md` - Alpine.js patterns (complementary to DaisyUI)

### External Documentation
- [DaisyUI Documentation](https://daisyui.com/docs/) - Official component documentation
- [DaisyUI Components](https://daisyui.com/components/) - Complete component reference
- [DaisyUI Themes](https://daisyui.com/docs/themes/) - Theme customization guide
- [Tailwind CSS](https://tailwindcss.com/docs) - Tailwind utility classes
```

## Validation Before Phase 4

Check that all content is populated:

- [x] Metadata: Keywords (10-15), TokenBudget (~NUMBER), ContextTier, Depends
- [x] Purpose: 1-2 meaningful sentences
- [x] Rule Scope: 1 specific line
- [x] Quick Start TL;DR: 3+ Essential Patterns, 5-7 Pre-Execution items
- [x] Contract: All 6 XML tags filled with real content
- [x] Contract placement: Before line 160
- [x] Anti-Patterns: 2+ with code examples and explanations
- [x] Post-Execution Checklist: 5+ verification items
- [x] Validation: Success Checks and Negative Tests defined
- [x] Output Format Examples: 1+ code blocks with examples
- [x] References: Related Rules (with rules/ prefix) and External Docs

## Common Mistakes to Avoid

**Mistake 1:** Leaving placeholder text
```markdown
 **Keywords:** [10-15 keywords here]
 **Keywords:** daisyui, tailwind, components, ...
```

**Mistake 2:** Wrong TokenBudget format
```markdown
 **TokenBudget:** 1200
 **TokenBudget:** medium
 **TokenBudget:** ~1200
```

**Mistake 3:** Missing rules/ prefix in Related Rules
```markdown
 - `420-javascript-core.md` - JavaScript foundation
 - `rules/420-javascript-core.md` - JavaScript foundation
```

**Mistake 4:** Vague Essential Patterns
```markdown
 - **Use best practices:** Follow recommended patterns
 - **Semantic HTML first:** Use native HTML elements with DaisyUI classes
```

**Mistake 5:** Generic Anti-Patterns without code
```markdown
 Don't do bad things with components
 [Show specific wrong code, explain why it fails, show correct alternative]
```

## Next Phase

Proceed to **Phase 4: Validation Loop** (`workflows/validation.md`)

**Preparation:**
- File should be fully populated
- No placeholder text remaining
- Ready for `schema_validator.py` execution

