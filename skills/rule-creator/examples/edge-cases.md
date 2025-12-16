# Edge Cases: Rule Creator

This document captures ambiguous scenarios, unusual inputs, and their resolutions. Use these patterns when standard workflows don't clearly apply.

## Edge Case 1: Technology Spans Multiple Domains

**Scenario:** User requests a rule for "React Testing Library"

**Ambiguity:** Could be:
- Frontend domain (440-449) - React-specific
- Testing domain (400-419) - General testing tool
- Python domain (200-299) - If pytest-react variant

**Resolution Pattern:**
```
Analysis: "React Testing Library" is primarily:
1. React-specific (not general testing)
2. JavaScript ecosystem (not Python)
3. Component testing focus

Recommendation: Frontend domain (440-449)
Suggested number: 442-react-testing-library-core

Rationale: Library is tightly coupled to React; users searching 
for React patterns would expect to find it in React domain.

Alternative considered: 415-testing-react (testing domain)
Rejected because: React specificity outweighs testing generality
```

**User prompt if unclear:**
```
"React Testing Library" could fit multiple domains:

A. Frontend/React (440-449) - React-specific testing patterns
B. Testing (400-419) - General frontend testing tool
C. Other - Please specify

Recommended: A (Frontend/React)
Reason: Library is React-specific, not a general testing framework

Please confirm or select alternative.
```

---

## Edge Case 2: Technology Has No Existing Domain

**Scenario:** User requests a rule for "Rust language patterns"

**Ambiguity:** No existing Rust rules in RULES_INDEX.md

**Resolution Pattern:**
```
Analysis: Rust is a systems programming language
Existing language domains:
- Python: 200-299
- Golang: 600-699
- JavaScript: 420-449

Options:
A. Create new domain 700-799 for Rust
B. Use existing 600-699 (languages) with subrange 650-699
C. Ask user for domain preference

Recommendation: Option B - Use 650-rust-core
Rationale: 600-699 is "languages" domain, Rust fits naturally
```

**User prompt:**
```
No existing Rust rules found. Proposed approach:

Domain: 650-699 (within Languages range 600-699)
First rule: 650-rust-core

This places Rust alongside Golang (600-649) in the languages domain.

Alternative: Create dedicated 700-799 range for Rust ecosystem

Proceed with 650-rust-core? (yes/no/alternative)
```

---

## Edge Case 3: Conflicting Best Practices Found

**Scenario:** Web research returns contradictory recommendations

**Example:** DaisyUI documentation says "use semantic classes" but popular tutorials recommend "use utility classes directly"

**Resolution Pattern:**
```
Conflict detected in best practices research:

Source 1 (Official docs): "Use semantic component classes"
Source 2 (Tutorial): "Use Tailwind utilities directly"

Resolution hierarchy:
1. Official documentation (highest authority)
2. Recent (2024-2025) community consensus
3. Older tutorials (lowest authority)

Decision: Follow official docs, note alternative in rule:

## Key Principles

### 1. Semantic Classes (Recommended)
Use DaisyUI's semantic classes for components:
```html
<button class="btn btn-primary">Click me</button>
```

### Note on Utility Classes
Some developers prefer Tailwind utilities directly. This works
but loses DaisyUI's theme consistency benefits.
```

---

## Edge Case 4: Technology Version Matters Significantly

**Scenario:** User requests rule for "Next.js" but doesn't specify version

**Ambiguity:** Next.js 13+ (App Router) vs Next.js 12 (Pages Router) have fundamentally different patterns

**Resolution Pattern:**
```
Version ambiguity detected: Next.js

Major versions with different patterns:
- Next.js 14/15 (2024-2025): App Router, Server Components
- Next.js 12/13 (legacy): Pages Router, getServerSideProps

Recommendation: Default to latest stable (Next.js 14+)
Rule name: 425-nextjs-app-router-core

If legacy support needed: Create separate 426-nextjs-pages-router
```

**User prompt:**
```
Next.js has significantly different patterns by version:

A. Next.js 14+ (App Router) - Current recommended approach
B. Next.js 12-13 (Pages Router) - Legacy but still widely used
C. Both - Create two rules

Recommended: A (Next.js 14+ App Router)
Reason: Official recommendation, new projects should use App Router

Please confirm or select alternative.
```

---

## Edge Case 5: Aspect Unclear from Request

**Scenario:** User says "create a rule for pytest"

**Ambiguity:** What aspect?
- Core usage (206-python-pytest)
- Fixtures (207-python-pytest-fixtures)
- Mocking (209-python-pytest-mock)
- Performance testing
- Security testing

**Resolution Pattern:**
```
Check existing rules first:
$ grep -i "pytest" RULES_INDEX.md

Found:
- 206-python-pytest.md (core)
- 209-python-pytest-mock.md (mocking)

If core exists: Ask about specific aspect
If core missing: Default to core aspect
```

**User prompt:**
```
Existing pytest rules found:
- 206-python-pytest.md (core patterns)
- 209-python-pytest-mock.md (mocking)

Which aspect would you like to add?

A. Fixtures - pytest fixture patterns and best practices
B. Parametrization - test parametrization patterns
C. Plugins - popular pytest plugin usage
D. Performance - pytest-benchmark and profiling
E. Other - Please specify

Please select an aspect.
```

---

## Edge Case 6: Rule Number Collision

**Scenario:** During template generation, discover number is already taken

**Example:** Assigned 422 for DaisyUI, but 422-javascript-vue-core.md exists

**Resolution Pattern:**
```
Collision detected: 422 already assigned to Vue.js

Options:
1. Use next available: 423
2. Renumber existing rule (not recommended)
3. Use gap in sequence if exists

Resolution: Use 423-daisyui-core

Verification:
$ ls rules/42*.md
422-javascript-vue-core.md
# No 423 - available
```

---

## Edge Case 7: Technology is Deprecated

**Scenario:** User requests rule for deprecated technology

**Example:** "Create a rule for AngularJS (1.x)"

**Resolution Pattern:**
```
Technology status check: AngularJS 1.x

Status: DEPRECATED (EOL December 2021)
Successor: Angular (2+)

Options:
A. Create rule with deprecation warnings
B. Suggest Angular (modern) rule instead
C. Decline - not worth documenting deprecated tech

Recommendation: Option B
Reason: New projects should not use AngularJS

Response: "AngularJS 1.x reached end-of-life in December 2021.
Would you like me to create a rule for Angular (2+) instead?
If you specifically need AngularJS patterns for legacy maintenance,
I can create a rule with appropriate deprecation warnings."
```

---

## Edge Case 8: Insufficient Research Results

**Scenario:** Web search returns minimal current (2024-2025) information

**Example:** Niche library with limited documentation

**Resolution Pattern:**
```
Research quality check:

Searches performed:
1. "2024 2025 [tech] best practices" - 2 results
2. "[tech] official documentation" - 1 result (outdated)
3. "[tech] common mistakes" - 0 results

Quality threshold: NOT MET
- Need 3+ authoritative sources
- Need 2024+ content for "current" practices

Options:
A. Proceed with available information + disclaimer
B. Use official docs only (may be outdated)
C. Request user provide additional sources
D. Decline - insufficient information

Recommendation: Option A with disclaimer

Rule header addition:
> **Note:** Limited 2024-2025 best practices available.
> This rule is based on official documentation v[X.Y] as of [DATE].
> Community patterns may have evolved.
```

---

## Edge Case 9: User Requests Non-Standard Aspect

**Scenario:** User wants "security" aspect but technology has no security-specific patterns

**Example:** "Create a DaisyUI security rule"

**Resolution Pattern:**
```
Aspect analysis: DaisyUI + Security

DaisyUI is a CSS component library.
Security concerns are minimal/non-existent:
- No server-side code
- No data handling
- No authentication
- CSS-only (client styling)

Resolution:
"DaisyUI is a CSS-only component library with no inherent security 
concerns. Security patterns would apply to the underlying framework 
(React, Vue, etc.) rather than DaisyUI itself.

Would you like me to:
A. Create a DaisyUI core rule (standard patterns)
B. Create a security rule for your framework (React/Vue/etc.)
C. Explain why DaisyUI doesn't need a security rule"
```

---

## Edge Case 10: Multi-Technology Rule Request

**Scenario:** User requests rule spanning multiple technologies

**Example:** "Create a rule for Snowflake + Python integration"

**Resolution Pattern:**
```
Multi-technology request detected:
- Snowflake (100-199 domain)
- Python (200-299 domain)

Options:
A. Single rule in one domain with cross-references
B. Two separate rules with dependencies
C. Integration rule in higher domain (800s)

Analysis:
- If patterns are tightly coupled → Option A
- If patterns are separable → Option B
- If patterns are workflow-focused → Option C

Recommendation for Snowflake+Python: Option A
Place in: 100-199 (Snowflake domain)
Name: 130-snowflake-python-integration
Depends: rules/100-snowflake-core.md, rules/200-python-core.md

Rationale: Snowflake is the "primary" technology; Python is the 
client. Integration patterns are Snowflake-centric.
```

---

## Quick Reference: Edge Case Decision Tree

```
Is technology domain clear?
├─ YES → Proceed to number assignment
└─ NO → Ask user (Edge Case 1, 2)

Does technology have multiple versions with different patterns?
├─ YES → Clarify version (Edge Case 4)
└─ NO → Proceed

Is aspect specified?
├─ YES → Verify aspect makes sense (Edge Case 9)
└─ NO → Check if core exists, ask if needed (Edge Case 5)

Is research quality sufficient?
├─ YES → Proceed to template
└─ NO → Add disclaimer or request sources (Edge Case 8)

Is technology deprecated?
├─ YES → Suggest alternative (Edge Case 7)
└─ NO → Proceed

Does number collide?
├─ YES → Use next available (Edge Case 6)
└─ NO → Proceed to template generation
```

