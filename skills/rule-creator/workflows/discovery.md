# Phase 1: Discovery & Research Workflow

## Purpose

Identify the correct domain range, determine the next available rule number, and research current best practices for the technology to establish a foundation for rule content.

## Inputs

- User request containing technology name
- Access to `@RULES_INDEX.md`
- Web search capability

## Outputs

- Domain range (e.g., 420-449 for JavaScript/Frontend)
- Next available rule number (e.g., 422)
- 10-15 semantic keywords for metadata
- Best practices summary
- Anti-pattern candidates
- External documentation links

## Step-by-Step Instructions

### Step 1.1: Extract Technology Name

Parse the user request to identify:
- **Primary technology:** e.g., "DaisyUI", "pytest-mock", "Snowflake Hybrid Tables"
- **Aspect:** "core" (default), "security", "testing", "performance", etc.
- **Related technologies:** e.g., "Tailwind" for DaisyUI, "React" for React Testing Library

### Step 1.2: Search RULES_INDEX.md

Execute comprehensive search:

```bash
# Primary technology search
grep -i "[technology]" RULES_INDEX.md

# Related technology search (broader)
grep -i "[related-tech]" RULES_INDEX.md

# Domain search if no exact match
grep -i "javascript\|frontend\|python\|snowflake" RULES_INDEX.md
```

**Example: DaisyUI**
```bash
$ grep -i "daisyui" RULES_INDEX.md
# (No results - new technology)

$ grep -i "javascript\|tailwind" RULES_INDEX.md
| 420-javascript-core.md | ...
| 421-javascript-alpinejs-core.md | ...
```

### Step 1.3: Analyze Search Results

From matches, extract:
1. **Rule numbers:** 420, 421 → identifies domain
2. **Domain pattern:** 42X → domain is 420-449
3. **Next available:** 422 (after 421, before 430)
4. **Related keywords:** javascript, frontend, components

### Step 1.4: Domain Range Reference

| Domain | Range | Technologies |
|--------|-------|--------------|
| Core | 000-099 | Foundational, framework |
| Snowflake | 100-199 | Snowflake platform, SQL |
| Python | 200-299 | Python language, libraries |
| Shell | 300-399 | Bash, Zsh, scripting |
| Docker | 400-499 | Containers, Docker |
| JavaScript | 420-449 | JavaScript, frontend frameworks |
| Data Science | 500-599 | Analytics, ML |
| Golang | 600-699 | Go language |
| Project Mgmt | 800-899 | Docs, automation, workflow |
| Demos | 900-999 | Examples, samples |

### Step 1.5: Confirm Domain Assignment

**If clear match found:**
- Use identified domain range
- Determine next sequential number

**If ambiguous:**
- Technology could fit multiple domains
- Example: "React Testing Library" → Frontend (440s) or Testing (400s)?
- **Action:** Ask user to clarify preferred domain

**If no match (new domain):**
- Propose domain based on technology type
- Example: "Rust" → suggest 600-699 (language range)
- **Action:** Confirm with user before proceeding

### Step 1.6: Load Domain Core Rule

Based on identified domain, load core rule for context:

```
JavaScript/Frontend (420-449) → rules/420-javascript-core.md
Python (200-299) → rules/200-python-core.md
Snowflake (100-199) → rules/100-snowflake-core.md
Shell (300-399) → rules/300-bash-scripting-core.md
Docker (400-499) → rules/350-docker-best-practices.md
Golang (600-699) → rules/600-golang-core.md
```

Read core rule to understand:
- Domain conventions
- Existing patterns
- Related dependencies
- Terminology standards

### Step 1.7: Web Research Best Practices

Execute targeted web searches:

```
Search 1: "2024 2025 [TECHNOLOGY] best practices"
→ Current industry standards, recent updates

Search 2: "[TECHNOLOGY] official documentation guide"
→ Authoritative source patterns

Search 3: "[TECHNOLOGY] common mistakes pitfalls"
→ Anti-pattern candidates

Search 4: "[TECHNOLOGY] performance optimization"
→ Advanced patterns
```

**Example: DaisyUI**
```
"2024 2025 DaisyUI best practices"
"DaisyUI official documentation component guide"
"DaisyUI common mistakes pitfalls"
"DaisyUI theme customization optimization"
```

### Step 1.8: Extract Research Findings

From web research, identify:

**Essential Patterns (3+ required):**
- Core practices widely adopted
- Performance optimizations
- Security/accessibility patterns

**Anti-Patterns (2+ required):**
- Common mistakes with consequences
- Deprecated approaches
- Performance anti-patterns

**Keywords (10-15 required):**
- Technology name (e.g., "daisyui")
- Related technologies (e.g., "tailwind")
- Use cases (e.g., "components", "ui library")
- Patterns (e.g., "themes", "accessibility")
- Implementation (e.g., "semantic html", "css variables")

**External References:**
- Official documentation URL
- Community guides
- Popular tutorials
- GitHub repositories

### Step 1.9: Validate Discovery Complete

Check that you have:
- ✓ Domain range identified (e.g., 420-449)
- ✓ Next rule number determined (e.g., 422)
- ✓ 10-15 semantic keywords extracted
- ✓ 3+ essential patterns identified
- ✓ 2+ anti-patterns identified
- ✓ External reference links collected
- ✓ Domain core rule loaded for context

## Example: Complete Discovery Phase

**User Request:** "Create a new rule for DaisyUI best practices"

**Execution:**

```
Step 1: Extract technology
  → Technology: DaisyUI
  → Aspect: core (default)
  → Related: Tailwind CSS, components

Step 2: Search RULES_INDEX.md
  $ grep -i "daisyui" RULES_INDEX.md
  → No results (new technology)
  
  $ grep -i "javascript\|tailwind\|frontend" RULES_INDEX.md
  → 420-javascript-core.md
  → 421-javascript-alpinejs-core.md

Step 3: Analyze results
  → Domain pattern: 420-449 (JavaScript/Frontend)
  → Next available: 422

Step 4: Load domain core
  → Reading rules/420-javascript-core.md for context

Step 5: Web research
  Search: "2024 2025 DaisyUI best practices"
  
  Findings:
  - Semantic HTML with Tailwind utilities
  - Theme customization via CSS variables
  - Accessibility-first component approach
  - Zero runtime JavaScript overhead
  - Component composition patterns

Step 6: Extract keywords (15)
  daisyui, tailwind, components, ui library, themes, 
  accessibility, semantic html, css variables, responsive design, 
  customization, utility-first, design system, best practices, 
  patterns, optimization

Step 7: Identify essential patterns (4)
  1. Use semantic HTML elements with DaisyUI classes
  2. Customize themes via data-theme and CSS variables
  3. Leverage zero-JS components for performance
  4. Compose complex UIs from base components

Step 8: Identify anti-patterns (3)
  1. Using inline styles instead of utility classes
  2. Not testing theme color contrast for accessibility
  3. Overriding component styles with !important

Step 9: Collect references
  - https://daisyui.com/docs/
  - https://daisyui.com/components/
  - https://github.com/saadeghi/daisyui

✓ Discovery complete, ready for Phase 2
```

## Decision Points

### Decision 1: Domain Ambiguous

**Scenario:** Technology could fit multiple domains

**Action:**
```
Example: "React Testing Library"
Could be:
  - 440-449 (React frontend)
  - 400-499 (Testing tools)

Recommendation: 440-449 (React specific)
Reason: Library is React-specific, not general testing

Ask user: "React Testing Library is primarily used for React component testing.
          Recommended domain: 440-449 (React).
          Suggested number: 442-react-testing-library.
          Proceed? (yes/no/alternative)"
```

### Decision 2: No Existing Domain Match

**Scenario:** Technology represents new domain

**Action:**
```
Example: "Rust language core patterns"
No existing Rust rules found.

Proposal:
  - New domain: 600-699 (Languages, currently Golang)
  - Or: 650-699 (Rust-specific subdomain)
  - Number: 650-rust-core (first in subdomain)

Ask user: "No existing Rust rules found.
          Proposed domain: 650-699 (Rust language).
          Proceed with 650-rust-core? (yes/no/alternative)"
```

### Decision 3: Insufficient Research Results

**Scenario:** Web search returns limited current information

**Action:**
```
If 2024-2025 best practices sparse:
1. Search broader: "[TECHNOLOGY] documentation patterns"
2. Check GitHub: "[TECHNOLOGY] awesome list"
3. Use official docs as primary source
4. Note in rule: "Based on official docs v[X.Y] as of [DATE]"

If still insufficient → Request user input:
  "Limited 2024-2025 best practices found for [TECHNOLOGY].
   Available sources: [official docs, version X.Y].
   Proceed with available information? (yes/no/provide additional sources)"
```

## Output Summary

At completion of Phase 1, you should have:

```
Technology: [Name]
Domain: [Range]
Number: [NNN]
Aspect: [core/security/testing/etc]

Keywords (15):
  [keyword1], [keyword2], ..., [keyword15]

Essential Patterns (4):
  1. [Pattern 1]
  2. [Pattern 2]
  3. [Pattern 3]
  4. [Pattern 4]

Anti-Patterns (3):
  1. [Anti-pattern 1]
  2. [Anti-pattern 2]
  3. [Anti-pattern 3]

References:
  - [Official docs URL]
  - [Community guide URL]
  - [Tutorial URL]

Domain Core Loaded: rules/[domain]-core.md

✓ Ready for Phase 2: Template Generation
```

## Next Phase

Proceed to **Phase 2: Template Generation** (`workflows/template-gen.md`)

