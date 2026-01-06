# Rule Creator - Version 1.2.0 Changes

**Date:** 2026-01-06
**Type:** Critical enforcement improvements

---

## Summary

Added comprehensive enforcement mechanisms to prevent agents from taking shortcuts during rule creation. Agents commonly attempt to optimize by manually creating structure, skipping validation, or leaving placeholder text. These changes mandate strict adherence to the 5-phase workflow.

---

## Files Modified

### 1. SKILL.md
**Added:**
- **Execution Contract (CRITICAL - NON-NEGOTIABLE)** section
  - Lists 7 FORBIDDEN actions (skipping template gen, skipping validation, placeholders)
  - Lists 6 REQUIRED actions (execute scripts, research, complete content, validation loop)
  - Defines enforcement mechanism with required outputs
  - Explains violation consequences
- **Phase Requirements** section
  - Phase 1: Discovery & Research (web search REQUIRED)
  - Phase 2: Template Generation (template_generator.py REQUIRED)
  - Phase 3: Content Population (NO placeholders)
  - Phase 4: Validation Loop (iterate until exit code 0)
  - Phase 5: Indexing (RULES_INDEX.md update)
  - Phase skipping forbidden

### 2. PROMPT.md
**Added:**
- **🚨 CRITICAL EXECUTION PROTOCOL 🚨** header (top of file)
  - Prominent warnings about common violation patterns
  - Required behavior checklist (6 items)
  - Execution acknowledgment protocol

### 3. README.md
**Added:**
- **⚠️ Execution Integrity Warning** section (prominent placement)
  - Lists forbidden shortcuts
  - Verification guidance (during and after execution)
  - Red flags list (timing, file sizes, placeholders, missing script output)

### 4. VALIDATION.md
**Added:**
- **Post-Execution Validation (Quality Assurance)** section
  - validate_rule_size() - file size checks (4000-12000 bytes expected)
  - validate_rule_structure() - required sections check
  - validate_no_placeholders() - checks for TODO, [Add content], etc.
  - validate_schema_clean() - confirms exit code 0 from schema_validator.py
  - validate_indexed() - confirms RULES_INDEX.md entry
  - Protocol violation report format

---

## Key Improvements

### 1. Enforcement of Script Execution
**Problem:** Agents manually create structure instead of running template_generator.py
**Solution:** Mandate script execution, check for output in logs

### 2. Validation Loop Enforcement
**Problem:** Agents run validator once or skip it entirely
**Solution:** Require iteration until exit code 0, max 3 attempts

### 3. Completeness Validation
**Problem:** Agents leave placeholder text or incomplete sections
**Solution:** Post-execution checks for TODOs, [Add content], etc.

### 4. Clear User Guidance
**Problem:** Users may think 10-15 minutes is excessive
**Solution:** Prominent warnings explaining this is expected for quality rules

---

## Design Principles

1. **Script Orchestration (Not Reimplementation):**
   - MUST execute template_generator.py (not create structure manually)
   - MUST execute schema_validator.py (not skip validation)
   - Script output must be visible in execution logs

2. **Iterative Validation:**
   - Run schema_validator.py until exit code 0
   - Max 3 iterations (escalate if still failing)
   - Each iteration: parse errors → fix → re-validate

3. **Complete Content (No Placeholders):**
   - All sections filled with real content
   - NO "TODO", "[Add content]", "...", or similar markers
   - Researched best practices (not generic knowledge)

4. **Quality Over Speed:**
   - 10-15 minutes per rule is CORRECT, not excessive
   - Research and validation take time
   - Shortcuts produce invalid or low-quality rules

5. **Verification Mechanisms:**
   - File size checks (4000-12000 bytes typical)
   - Structure checks (all 9 required sections present)
   - Placeholder checks (no TODO markers)
   - Schema validation (exit code 0)
   - Indexing check (RULES_INDEX.md entry present)

---

## Breaking Changes

**None.** All changes are additive. Existing invocations work unchanged.

---

## Migration Notes

**For Agents:**
- Now MUST execute template_generator.py (visible in logs)
- MUST execute schema_validator.py in loop until clean
- MUST fill all sections (no placeholders)
- MUST add to RULES_INDEX.md

**For Users:**
- Understand 10-15 minutes is expected per rule
- Monitor for red flags (fast completion, small files, placeholders)
- Use post-execution validation to verify quality

---

## Version History

- **v1.0.0:** Initial implementation with 5-phase workflow
- **v1.1.0:** Added web research integration, improved examples
- **v1.2.0 (2026-01-06):** Critical enforcement improvements

---

## References

- **Issue:** Agent shortcuts produce invalid or low-quality rules
- **Request:** Mandate 100% workflow compliance
- **Solution:** Comprehensive enforcement at multiple levels (docs, validation, workflow)
