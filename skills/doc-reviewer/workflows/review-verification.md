# Workflow: Review Verification

## Purpose

Prevent shortcut-based reviews by enforcing evidence requirements that can only be satisfied by actually reading the documentation file.

## Evidence Requirements

Every review MUST include:

### 1. Documentation Quotes (MANDATORY)

Each dimension score MUST cite at least one direct quote from the target documentation with line number.

**Format:**
```
**Evidence:** Line 47 states: "Run `uv sync` to install dependencies"
```

**Verification:** The quoted text MUST appear verbatim at the cited line number. Fabricated quotes = INVALID review.

### 2. Line Reference Density

**Minimum Requirements:**
- FULL mode: ≥15 distinct line references across all dimensions
- FOCUSED mode: ≥5 distinct line references per scored dimension
- STALENESS mode: ≥3 distinct line references

### 3. Doc-Specific Findings

Each review MUST identify at least 2 findings unique to that documentation file:
- Specific file paths, command names, or function references
- Specific heading titles or code examples
- Specific external link URLs
- Specific jargon terms used

**Generic findings that apply to any README/docs file are INSUFFICIENT.**

## Verification Checklist

Before writing review to file, verify:

- [ ] ≥15 line references present (FULL mode)
- [ ] Each dimension cites direct quote with line number
- [ ] Cross-Reference Verification table populated from actual codebase check
- [ ] Link Validation table populated from actual HTTP check
- [ ] Coverage Checklist populated from actual feature enumeration
- [ ] Recommendations reference specific sections by line number

## Detection of Shortcut Attempts

**Red Flags (Automatic INVALID):**

1. **No line references** - Review contains zero "line X" or "(lines X-Y)" references
2. **Round line numbers only** - All references are to lines 10, 20, 30, etc. (fabricated)
3. **Generic content** - Findings could apply to any documentation file without modification
4. **Template patterns** - Multiple reviews share identical phrasing for different docs
5. **Missing quotes** - No direct quotes from documentation content
6. **Empty verification tables** - Cross-Reference / Link Validation / Coverage tables are headers only

## Enforcement

If verification fails:
1. DELETE the invalid review
2. READ the actual documentation file
3. Generate review with proper evidence
4. Re-verify before writing

**Do NOT write reviews that fail verification.**

### 4. Template Compliance

- [ ] Executive Summary table uses exact column headers from `references/REVIEW-OUTPUT-TEMPLATE.md`
- [ ] All required H2 sections present in correct order
- [ ] Post-Review Checklist has 11 items with template wording
- [ ] All 6 dimensions scored (FULL mode)

## Quality Gates

The following gates are applied before a review is considered complete. Gates 1–6 are enforced
implicitly via the checks above. **Gate 7** is a conditional, post-write gate enforced when
`timing_enabled: true`.

### Gate 7: Per-Dimension Timing Presence (conditional)

**Condition:** `timing_enabled == true`.

**Checks:**

- [ ] Output file contains the `### Per-Dimension Timing` heading
- [ ] Table under that heading has ≥6 rows (one per scored dimension: accuracy, completeness, clarity, structure, staleness, consistency)
- [ ] `timing-end` stdout contained `PER_DIMENSION_STATUS=present` or `PER_DIMENSION_STATUS=derived`
- [ ] No `PER_DIMENSION_STATUS=missing` line observed during the run

**Failure remediation (in order):**

1. Re-run `timing-end` with `--auto-dimension-timings` (sequential mode) so the checkpoint pairs
   recorded in Step 4a of SKILL.md are used to derive the `dimension_timings` array.
2. In parallel mode, re-aggregate the sub-agent self-reports and re-run with
   `--dimension-timings` JSON.
3. If the timing data for this run is unrecoverable, append the subsection with a single
   row stating `unavailable` and the failure reason (e.g., `VALIDATION ERROR: ...`) so the
   omission is visible rather than silent.

**Explicit opt-out (`timing_enabled: false`):** Gate 7 is a NO-OP. The review does not need a
`### Per-Dimension Timing` section. (If the caller wishes to include the section anyway for
consistency, a single `not-requested` row is acceptable.)

**Integration point:** This gate is checked in `workflows/file-write.md` (pre-write structural
validation) when `timing_enabled: true`.

## Why This Cannot Be Shortcut

To produce a valid review under these requirements, the agent MUST:
1. Read the documentation file (to find actual line numbers)
2. Extract actual quotes (to cite as evidence)
3. Verify references against the actual codebase (to populate Cross-Reference table)
4. Test actual URLs (to populate Link Validation table)

**There is no way to satisfy these requirements without doing the work.**

## Integration Point

Call this verification before `file-write.md` workflow:
1. Generate review content
2. **Run review-verification.md checklist**
3. If PASS: proceed to file-write.md
4. If FAIL: return to review generation with actual file reading
