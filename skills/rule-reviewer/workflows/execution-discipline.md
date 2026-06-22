# Execution Discipline

**FOUNDATIONAL PRINCIPLE:** This skill prioritizes ACCURACY over efficiency. The user authorized this review knowing the scope. Proceed with the full process.

## Forbidden behaviors

- Calculating or mentioning projected completion time.
- Asking about time constraints mid-execution.
- Proposing "faster" or "streamlined" alternatives.
- Creating template-based reviews without analysis.
- Estimating scores without consulting rubrics.
- Skipping dimensions, schema validation, or Agent Execution Test.
- Expressing concern about token costs or scope.
- Abbreviating reviews to save tokens.

## Required behaviors

- Read the complete rule file (line 1 to END).
- Run schema validator (`uv run ai-rules validate`).
- Measure line count (`wc -l`).
- Consult rubrics for each scored dimension.
- Generate specific recommendations with line numbers.
- Write complete review (3000–8000 bytes for FULL mode).

## Skills vs Rules distinction

- **Rules** are loaded 100s–1000s of times → token efficiency CRITICAL.
- **Skills** are used occasionally → quality over efficiency, tokens IRRELEVANT.
- Do NOT apply token-efficiency principles from rules to this skill's execution.

## Self-correction triggers

If you think or write any of these, STOP, re-read this section, and resume the comprehensive process silently:

- "to save time"
- "for efficiency"
- "should I continue with"
- "would you prefer"
- "let me create a streamlined"

## Pre-execution commitment

Before starting any review, confirm you will:

- NOT calculate projected time.
- NOT ask about time constraints.
- NOT create template-based reviews.
- NOT propose faster alternatives.
- WILL read the file completely.
- WILL consult rubrics.
- WILL write specific analysis.
