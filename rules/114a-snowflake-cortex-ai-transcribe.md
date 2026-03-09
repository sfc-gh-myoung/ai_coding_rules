# Snowflake Cortex AI_TRANSCRIBE Best Practices

## Metadata

**SchemaVersion:** v3.2
**RuleVersion:** v1.0.0
**LastUpdated:** 2026-03-09
**LoadTrigger:** kw:ai_transcribe, kw:transcribe, kw:audio, kw:diarization
**Keywords:** AI_TRANSCRIBE, audio transcription, TO_FILE, speaker diarization, timestamp_granularity, FLAC, MP3, OGG, WAV, WebM
**TokenBudget:** ~3500
**ContextTier:** Medium
**Depends:** 114-snowflake-cortex-aisql.md, 100-snowflake-core.md

## Scope

**What This Rule Covers:**
Audio transcription patterns using Snowflake Cortex AI_TRANSCRIBE, including correct TO_FILE syntax, speaker diarization, common type errors, and batch transcription from staged audio files.

**When to Load This Rule:**
- Transcribing audio files with AI_TRANSCRIBE
- Working with TO_FILE for audio file references
- Implementing speaker diarization (timestamp_granularity)
- Debugging AI_TRANSCRIBE type errors (VARCHAR vs FILE)
- Processing audio from internal stages (FLAC, MP3, OGG, WAV, WebM)

### Quantification Standards

**Performance Thresholds:**
- **Audio file size limit:** Up to 60 minutes per file for speaker diarization mode
- **Batch processing:** Process up to 10 files per query; use LIMIT to control costs during development
- **Supported formats:** FLAC, MP3, OGG, WAV, WebM

> **Investigation Required**
> When applying this rule:
> 1. **Verify stage access** - Check stages and file permissions for TO_FILE usage
> 2. **Check audio format** - Confirm file is FLAC, MP3, OGG, WAV, or WebM
> 3. **Test with single file first** - Transcription costs scale with audio duration
> 4. **Verify CORTEX_USER grants** - AI_TRANSCRIBE requires SNOWFLAKE.CORTEX_USER role
>
> **Anti-Pattern:**
> "Let me add AI_TRANSCRIBE - it should handle any audio format..."
>
> **Correct Pattern:**
> "Let me check your stage files and verify the audio format is supported."
> [checks DIRECTORY listing, verifies file extensions]
> "Your .mp3 files are supported. Here's the TO_FILE pattern for batch transcription..."

## References

### Dependencies

**Must Load First:**
- **114-snowflake-cortex-aisql.md** - Core Cortex AISQL patterns, governance, and cost control
- **100-snowflake-core.md** - Snowflake foundation patterns

**Related:**
- **108-snowflake-data-loading.md** - Stage management for audio files
- **111-snowflake-observability-core.md** - Observability and tracing

### External Documentation

- [Cortex AI Audio (AI_TRANSCRIBE)](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-audio) - Audio transcription, speaker diarization, timestamp extraction with TO_FILE syntax

## Contract

### Inputs and Prerequisites

- Audio files staged in a Snowflake internal stage (FLAC, MP3, OGG, WAV, or WebM)
- SNOWFLAKE.CORTEX_USER database role granted to the executing role
- Stage READ privileges for the audio file stage

### Mandatory

AI_TRANSCRIBE function calls must use TO_FILE with two arguments (stage name, file path) to create a FILE type reference.

### Forbidden

- Using GET_PRESIGNED_URL or BUILD_SCOPED_FILE_URL as input to AI_TRANSCRIBE (returns VARCHAR, not FILE)
- Passing a single argument to TO_FILE (requires two: stage and path)
- Processing audio files longer than 60 minutes in speaker diarization mode without splitting

### Execution Steps

1. Stage audio files in an internal Snowflake stage
2. Verify file format is supported (FLAC, MP3, OGG, WAV, WebM)
3. Use `TO_FILE('@stage_name', 'relative_path')` to create FILE references
4. Test with a single file before batch processing
5. For speaker diarization, add `{'timestamp_granularity': 'speaker'}` option
6. Extract results from JSON output (text, audio_duration, segments)

### Output Format

SQL examples with AI_TRANSCRIBE producing JSON output containing transcription text, audio duration, and optional speaker segments.

### Validation

**Pre-Task-Completion Checks:**
- Stage exists and contains audio files in supported formats
- SNOWFLAKE.CORTEX_USER grants verified for executing role
- TO_FILE uses two-argument syntax (stage, path)
- LIMIT applied for development/testing queries

**Success Criteria:**
- Transcription JSON contains non-null text field
- Audio duration reported in seconds
- Speaker segments (if diarization) contain speaker_label, start, end, text
- No type mismatch errors (VARCHAR vs FILE)

**Negative Tests:**
- GET_PRESIGNED_URL input raises "Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)"
- BUILD_SCOPED_FILE_URL input raises same VARCHAR type error
- Single-argument TO_FILE raises "TO_FILE expects 2 arguments"
- Unsupported audio format raises format error

### Post-Execution Checklist

- [ ] TO_FILE uses two-argument syntax: `TO_FILE('@stage', 'path')`
      Verify: Check all AI_TRANSCRIBE calls use two-argument TO_FILE, not GET_PRESIGNED_URL
- [ ] Audio files are in supported format (FLAC, MP3, OGG, WAV, WebM)
      Verify: Check DIRECTORY listing file extensions
- [ ] Batch queries use LIMIT during development
      Verify: Ensure LIMIT clause present for testing queries
- [ ] Speaker diarization output parsed with LATERAL FLATTEN
      Verify: If using timestamp_granularity='speaker', segments are flattened correctly
- [ ] SNOWFLAKE.CORTEX_USER role verified
      Verify: `SHOW GRANTS TO DATABASE ROLE SNOWFLAKE.CORTEX_USER;`

## AI_TRANSCRIBE - Audio Transcription (CRITICAL SYNTAX)

**CORRECT Pattern - TO_FILE with two arguments:**

```sql
-- Pattern 1: Direct file reference (recommended)
SELECT
    RELATIVE_PATH AS audio_file,
    AI_TRANSCRIBE(TO_FILE('@STAGE_NAME', RELATIVE_PATH)) AS transcription
FROM DIRECTORY('@STAGE_NAME')
WHERE RELATIVE_PATH LIKE '%.mp3';

-- Pattern 2: Inline stage and file path
SELECT AI_TRANSCRIBE(TO_FILE('@financial_consultation', 'consultation.wav')) AS transcript;
```

**INCORRECT Patterns (will cause type errors):**

```sql
-- WRONG: Using GET_PRESIGNED_URL (returns VARCHAR, not FILE type)
SELECT AI_TRANSCRIBE(GET_PRESIGNED_URL('@stage', 'file.mp3'));
-- Error: Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)

-- WRONG: Using BUILD_SCOPED_FILE_URL without TO_FILE wrapper
SELECT AI_TRANSCRIBE(BUILD_SCOPED_FILE_URL(@stage, path));
-- Error: Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)

-- WRONG: Wrapping BUILD_SCOPED_FILE_URL result with TO_FILE (single arg)
SELECT AI_TRANSCRIBE(TO_FILE(BUILD_SCOPED_FILE_URL(@stage, path)));
-- Error: TO_FILE expects 2 arguments (stage, path), not 1
```

**Why TO_FILE('@stage', 'path') is Required:**
- `AI_TRANSCRIBE` expects a FILE reference type, not a VARCHAR string
- `TO_FILE()` takes **two separate arguments**: stage name and file path
- `GET_PRESIGNED_URL()` and `BUILD_SCOPED_FILE_URL()` return VARCHAR strings (HTTP URLs)
- Only `TO_FILE('@stage', 'path')` creates the proper FILE type

**Complete Working Example:**

```sql
-- Transcribe audio files from directory listing
WITH audio_files AS (
    SELECT RELATIVE_PATH
    FROM DIRECTORY('@UTILITY_DEMO.CUSTOMER_DATA.AUDIO_FILES')
    WHERE RELATIVE_PATH LIKE '%.mp3'
    LIMIT 10
)
SELECT
    RELATIVE_PATH AS audio_file,
    AI_TRANSCRIBE(
        TO_FILE('@UTILITY_DEMO.CUSTOMER_DATA.AUDIO_FILES', RELATIVE_PATH)
    ) AS transcription_json,
    transcription_json:text::VARCHAR AS transcription_text,
    transcription_json:audio_duration::FLOAT AS duration_seconds
FROM audio_files;
```

## Speaker Recognition (Diarization)

Use `timestamp_granularity: 'speaker'` to get structured segments with speaker changes.

```sql
-- AI_TRANSCRIBE with native speaker identification
WITH audio_files AS (
    SELECT RELATIVE_PATH
    FROM DIRECTORY('@CALL_CENTER.AUDIO.RECORDINGS')
    WHERE RELATIVE_PATH LIKE '%.mp3'
    LIMIT 1
),
transcribed_with_speakers AS (
    SELECT
        RELATIVE_PATH AS audio_file,
        -- timestamp_granularity: 'speaker' returns structured segments
        AI_TRANSCRIBE(
            TO_FILE('@CALL_CENTER.AUDIO.RECORDINGS', RELATIVE_PATH),
            {'timestamp_granularity': 'speaker'}
        ) AS transcription_json
    FROM audio_files
),
-- Flatten segments array to get individual speaker turns
speaker_segments AS (
    SELECT
        audio_file,
        transcription_json:text::VARCHAR AS full_transcript,
        transcription_json:audio_duration::FLOAT AS audio_duration,
        seg.value:speaker_label::VARCHAR AS speaker,  -- SPEAKER_01, SPEAKER_02, etc.
        seg.value:start::FLOAT AS start_time,
        seg.value:end::FLOAT AS end_time,
        seg.value:text::VARCHAR AS segment_text
    FROM transcribed_with_speakers,
    LATERAL FLATTEN(input => transcription_json:segments) seg
)
SELECT
    audio_file,
    speaker,
    ROUND(start_time, 2) AS start_sec,
    ROUND(end_time, 2) AS end_sec,
    ROUND(end_time - start_time, 2) AS duration_sec,
    segment_text
FROM speaker_segments
ORDER BY start_time;
```

**Speaker Recognition Notes:**
- `timestamp_granularity: 'speaker'` returns structured segments with speaker changes
- Speaker labels are generic: SPEAKER_01, SPEAKER_02, etc. (not semantic roles like "agent", "customer")
- Each segment includes: `speaker_label`, `start`, `end`, `text`
- Use LATERAL FLATTEN to extract individual speaker turns
- For semantic role identification (e.g., "Representative" vs "Customer"), chain with AI_COMPLETE
- Supported file types: FLAC, MP3, OGG, WAV, WebM (up to 60 minutes for speaker mode)

## Anti-Patterns and Common Mistakes

**Anti-Pattern 1: Using GET_PRESIGNED_URL or BUILD_SCOPED_FILE_URL as AI_TRANSCRIBE Input**

**Problem:** Developers familiar with other Snowflake file operations instinctively use `GET_PRESIGNED_URL('@stage', 'file.mp3')` or `BUILD_SCOPED_FILE_URL(@stage, path)` to reference audio files. These functions return a VARCHAR (HTTP URL string), but AI_TRANSCRIBE requires a FILE type reference. The query fails with "Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)" — an error message that doesn't clearly explain the root cause is a type mismatch, leading developers to chase permission issues instead.

**Correct Pattern:** Always use `TO_FILE('@stage_name', 'relative_path')` with two separate arguments to create a proper FILE type reference. `TO_FILE` is the only function that produces the FILE type that AI_TRANSCRIBE accepts. Never wrap URL-returning functions with TO_FILE either — `TO_FILE(GET_PRESIGNED_URL(...))` passes a single VARCHAR argument instead of the required two arguments (stage, path).

```sql
-- Wrong: GET_PRESIGNED_URL returns VARCHAR, not FILE type
SELECT AI_TRANSCRIBE(GET_PRESIGNED_URL('@my_stage', 'recording.mp3'));
-- Error: Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)

-- Wrong: BUILD_SCOPED_FILE_URL also returns VARCHAR
SELECT AI_TRANSCRIBE(BUILD_SCOPED_FILE_URL(@my_stage, 'recording.mp3'));
-- Error: Invalid argument types for function 'AI_TRANSCRIBE': (VARCHAR)

-- Wrong: Wrapping URL function with TO_FILE — single arg instead of two
SELECT AI_TRANSCRIBE(TO_FILE(GET_PRESIGNED_URL('@my_stage', 'recording.mp3')));
-- Error: TO_FILE expects 2 arguments (stage, path), not 1

-- Correct: TO_FILE with two separate arguments creates proper FILE type
SELECT AI_TRANSCRIBE(TO_FILE('@my_stage', 'recording.mp3'));
```

**Anti-Pattern 2: Batch-Transcribing All Stage Files Without LIMIT During Development**

**Problem:** Developers run `SELECT AI_TRANSCRIBE(TO_FILE('@stage', RELATIVE_PATH)) FROM DIRECTORY('@stage')` against a stage containing hundreds of audio files during initial development. Transcription costs scale with audio duration, and a single unconstrained query against a large stage can consume significant credits before results are even reviewed. There's no way to cancel mid-execution and recover spent credits.

**Correct Pattern:** Always add `LIMIT 1` or `LIMIT 5` during development and testing. Verify the output format, check transcription quality, and confirm costs on a small sample before processing the full dataset. Remove the LIMIT only for the final production run after validating the pipeline end-to-end.

```sql
-- Wrong: No LIMIT — transcribes all files, potentially hundreds of hours of audio
SELECT
    RELATIVE_PATH AS audio_file,
    AI_TRANSCRIBE(TO_FILE('@CALL_RECORDINGS', RELATIVE_PATH)) AS transcription
FROM DIRECTORY('@CALL_RECORDINGS')
WHERE RELATIVE_PATH LIKE '%.mp3';
-- Could process 500+ files and burn significant credits before you see any results

-- Correct: Start with LIMIT 1, validate, then scale up
SELECT
    RELATIVE_PATH AS audio_file,
    AI_TRANSCRIBE(TO_FILE('@CALL_RECORDINGS', RELATIVE_PATH)) AS transcription
FROM DIRECTORY('@CALL_RECORDINGS')
WHERE RELATIVE_PATH LIKE '%.mp3'
LIMIT 1;  -- Validate output format and quality first
-- Then LIMIT 5 for cost estimation, then remove LIMIT for production
```

**Anti-Pattern 3: Treating Speaker Labels as Stable Identifiers Across Files**

**Problem:** Developers assume that `SPEAKER_01` in one audio file corresponds to the same person as `SPEAKER_01` in another file, or that speaker labels map to semantic roles (e.g., "SPEAKER_01 is always the agent"). Speaker diarization assigns labels per-file based on order of appearance, so the same person can be SPEAKER_01 in one recording and SPEAKER_02 in another. Building analytics on raw speaker labels across files produces nonsensical aggregations.

**Correct Pattern:** Treat speaker labels as relative identifiers scoped to a single audio file only. For semantic role identification (e.g., "agent" vs. "customer"), chain the transcription output with AI_COMPLETE to classify speakers based on conversational context. For cross-file speaker matching, use external speaker identification before or after transcription.

```sql
-- Wrong: Aggregating raw speaker labels across files — labels are not stable
SELECT
    speaker,
    COUNT(*) AS total_segments,
    SUM(end_time - start_time) AS total_talk_time
FROM TRANSCRIPTION_SEGMENTS
GROUP BY speaker;
-- SPEAKER_01 in file A is a different person than SPEAKER_01 in file B!

-- Correct: Use AI_COMPLETE to classify speakers per-file, then aggregate by role
WITH per_file_transcripts AS (
    SELECT audio_file, full_transcript, speaker, segment_text
    FROM TRANSCRIPTION_SEGMENTS
),
classified AS (
    SELECT
        audio_file, speaker, segment_text,
        AI_COMPLETE('llama3.1-70b',
            'Given this call center transcript, classify ' || speaker
            || ' as either "agent" or "customer" based on context: '
            || full_transcript
        ):role::VARCHAR AS speaker_role
    FROM per_file_transcripts
)
SELECT speaker_role, COUNT(*) AS total_segments
FROM classified
GROUP BY speaker_role;  -- Aggregate by semantic role, not raw label
```
