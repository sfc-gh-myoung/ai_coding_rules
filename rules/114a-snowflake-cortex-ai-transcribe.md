---
schema_version: v4.0
rule_version: v3.0.0
description: Authorized bounded audio transcription with FILE references, mode-aware limits, truthful error accounting and per-file speaker semantics.
last_updated: 2026-10-07
keywords:
  - kw:AI_TRANSCRIBE
  - kw:TO_FILE syntax
  - kw:speaker diarization
  - kw:audio transcription
  - kw:FILE type reference
  - kw:staged audio formats
  - kw:ai_complete
token_budget: ~1100
context_tier: Medium
depends:
  required:
    - 114-snowflake-cortex-aisql.md  # Core Cortex AISQL patterns, governance, and cost control
---
# Snowflake Cortex AI_TRANSCRIBE Best Practices

## Scope

**What This Rule Covers:**
Staged audio FILE inputs, transcription/word/speaker modes, bounded costs, per-file results/errors, quality review and privacy.

**When to Load This Rule:**
When designing or troubleshooting AI_TRANSCRIBE calls, batch audio processing, or speaker/timestamp parsing.

## Contract

### Inputs and Prerequisites

- Approved audio manifest, consent/privacy handling, stage/files/access, actual format/duration/size/language and expected output mode.
- Current function/region availability, documented Cortex access role, stage-type permissions, compute/cost bounds and explicit inference authorization.

### Mandatory

- AI_TRANSCRIBE takes a FILE object; supported TO_FILE(stage, relative_path) constructs a staged reference. URL strings from presigned/scoped URL functions are not equivalent FILE input; inspect current TO_FILE overloads rather than claim it has only one possible form forever.
- Verify actual readable audio, not extension alone: supported FLAC/MP3/OGG/WAV/WebM, correct audio stream, language and corruption/resampling constraints. Conversion/splitting preserves approved original and needs authorized local/file scope.
- Current docs specify 700 MB maximum and 60 minutes for word/speaker timestamp modes, 120 minutes without timestamps. Recheck current limits/availability before execution; splitting must preserve offsets/context and account for quality loss.
- Select timestamp_granularity word or speaker when needed. Default output has text; timestamp modes use segments and may not include full text. Parse actual schema rather than require text for every mode.
- Track audio_duration in seconds and segments with start/end/text plus speaker_label for speaker mode. Preserve file identity and segment order; validate boundaries and offset translation after chunking.
- Speaker labels are scoped to each file, not verified people or stable cross-file identities. Semantic roles inferred from transcript context are uncertain and require authorized separate classification/review; do not automatically export to speaker-ID services.
- Preselect a bounded approved manifest/subquery before expensive calls; an outer LIMIT is not a reliable total-cost guarantee. Start with authorized small samples and explicit duration/cost bounds, not a universal ten-file query limit.
- Transcription can contain personal/confidential data. Store/query outputs in approved governed locations, redact diagnostics and avoid logging/exporting raw transcripts or generating additional model calls without authorization.
- Account for current per-row error behavior and return_error_details mode. Successful query completion can include NULL/error rows; distinguish valid blank/silent audio from failed transcription and retain per-file errors.
- Inspect actual wrapper/value/error schema before flattening segments; FLATTEN can drop empty/error rows. Maintain file-level outcome accounting so failed files do not disappear from summaries.
- Verify transcription quality and speaker segmentation against representative expected audio, not merely non-NULL output; document accents/noise/language/overlap limitations and human-review needs.
- Costs depend on actual audio billing rules/current pricing, including minimum billable duration. Do not fabricate linear sample extrapolation precision or spent-credit refunds on cancellation.
- Upload/inference/persistence/reprocessing are authorized operations; retain recorded attempts and file hashes, inspect partial outcomes before scoped retry and avoid duplicate paid processing by default.

### Execution Steps

1. Inspect approved manifest/files/function contract, privacy/availability and mode-specific size/duration constraints.
2. Prepare FILE references and bounded processing plan with explicit output/error/cost accounting.
3. Under inference approval, process a representative authorized sample and review quality/segments/errors.
4. Scale only within approved bounds, preserving file outcomes and chunk timing; classify roles only if separately requested/approved.
5. Report exact processed/failed/unattempted files, quality evidence, costs and unresolved checks without substituting failures.

### Validation

- Correct FILE/type/mode references, actual supported readable audio and documented current limits/access.
- Mode-appropriate result/segment/error parsing and complete file accounting, speaker labels not identities.
- Quality/privacy/cost evidence reviewed, calls bounded before invocation and failures retained.
- Deliver reviewed processing design and actual outcomes; unexecuted audio/cloud tests remain unverified.

## References

- [AI_TRANSCRIBE contract and limits](https://docs.snowflake.com/en/sql-reference/functions/ai_transcribe)
- [TO_FILE](https://docs.snowflake.com/en/sql-reference/functions/to_file)
- `114-snowflake-cortex-aisql.md` for AI governance/cost boundaries.
- `108-snowflake-data-loading.md` for approved staging and file evidence.
