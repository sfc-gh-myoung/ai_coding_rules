# Skill Timing Self-Validation

Procedures for validating skill-timing functionality before deployment or after changes.

## Quick Validation

Run the automated test suite:

```bash
bash skills/skill-timing/tests/test_skill_timing.sh
```

**Expected:** All tests pass (10+ tests).

## Schema Validation

Validate completed timing data against the JSON schema:

```bash
# Install jsonschema if needed
pip install jsonschema

# Validate a specific timing file
python3 -c "
import json
from jsonschema import validate, ValidationError

schema = json.load(open('skills/skill-timing/schemas/timing-output.schema.json'))
data = json.load(open('reviews/.timing-data/skill-timing-XXXX-complete.json'))

try:
    validate(data, schema)
    print('Schema validation: PASSED')
except ValidationError as e:
    print(f'Schema validation: FAILED')
    print(f'  Path: {e.json_path}')
    print(f'  Error: {e.message}')
"
```

## Manual Validation Checklist

### Timing Start

- [ ] Returns valid 16-character hex `run_id`
- [ ] Creates timing file in `reviews/.timing-data/`
- [ ] Updates agent recovery registry
- [ ] `TIMING_RUN_ID`, `TIMING_FILE`, `TIMING_AGENT_ID` in output

```bash
# Test
OUTPUT=$(bash skills/skill-timing/scripts/run_timing.sh start \
    --skill test-skill \
    --target test.md \
    --model test-model)

echo "$OUTPUT" | grep -q "TIMING_RUN_ID=" && echo "PASS: run_id present"
RUN_ID=$(echo "$OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
[[ "$RUN_ID" =~ ^[a-f0-9]{16}$ ]] && echo "PASS: run_id format valid"
```

### Timing Checkpoint

- [ ] Records checkpoint with elapsed time
- [ ] Preserves previous checkpoints
- [ ] Handles missing timing file gracefully
- [ ] `CHECKPOINT_STATUS=recorded` in output

```bash
# Test (requires valid run_id from start)
OUTPUT=$(bash skills/skill-timing/scripts/run_timing.sh checkpoint \
    --run-id "$RUN_ID" \
    --name test_checkpoint)

echo "$OUTPUT" | grep -q "CHECKPOINT_STATUS=recorded" && echo "PASS: checkpoint recorded"
```

### Timing End

- [ ] Computes correct duration
- [ ] Validates timing data before output
- [ ] Cleans up in-progress file
- [ ] Saves completed data to `reviews/.timing-data/`
- [ ] Outputs standardized format

```bash
# Test (requires valid run_id from start)
touch test-output.md
OUTPUT=$(bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id "$RUN_ID" \
    --output-file test-output.md \
    --skill test-skill)

echo "$OUTPUT" | grep -q "TIMING_STATUS=completed" && echo "PASS: status completed"
echo "$OUTPUT" | grep -q "TIMING: skill-timing v" && echo "PASS: standardized header"
rm -f test-output.md
```

### Output Formats

- [ ] Human format includes all sections
- [ ] JSON format is valid JSON
- [ ] Markdown format is valid table
- [ ] Quiet format produces no output

```bash
# Start fresh timing
OUTPUT=$(bash skills/skill-timing/scripts/run_timing.sh start \
    --skill format-test --target test.md --model test-model)
RUN_ID=$(echo "$OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
touch test-output.md

# Test JSON format
JSON=$(bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id "$RUN_ID" \
    --output-file test-output.md \
    --skill format-test \
    --format json 2>&1) || true

echo "$JSON" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null \
    && echo "PASS: JSON format valid" || echo "FAIL: JSON format invalid"

rm -f test-output.md
```

### Error Handling

- [ ] Invalid run_id triggers recovery attempt
- [ ] Missing timing file logs warning, continues
- [ ] Negative duration detected as clock skew

```bash
# Test invalid run_id
OUTPUT=$(bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id "invalid-format" \
    --output-file test.md \
    --skill test-skill 2>&1) || true

echo "$OUTPUT" | grep -q "Invalid run_id format" && echo "PASS: invalid run_id detected"
```

### Exit Codes

- [ ] Exit 0 for success
- [ ] Exit 1 for general error
- [ ] Exit 2 for shortcut detection
- [ ] Exit 3 for above baseline

```bash
# Test exit codes (requires baseline set)
# This test requires manual setup of alert thresholds
```

## Integration Validation

Test timing integration with another skill:

1. Enable timing in rule-reviewer (set `timing_enabled: true` in inputs)
2. Execute rule-reviewer on a test file
3. Verify timing metadata appears in output file
4. Check completed timing data in `reviews/.timing-data/`

```bash
# Example integration test
# 1. Run rule-reviewer with timing enabled
# 2. Check output file
grep -q "## Timing Metadata" reviews/test-review.md && echo "PASS: timing metadata present"

# 3. Check timing data directory
ls reviews/.timing-data/skill-timing-*-complete.json | head -1 && echo "PASS: timing data saved"
```

## Performance Validation

Verify timing overhead is acceptable:

```bash
# Measure timing overhead
START=$(date +%s.%N)

for i in {1..10}; do
    OUTPUT=$(bash skills/skill-timing/scripts/run_timing.sh start \
        --skill perf-test --target test.md --model test-model 2>/dev/null)
    RUN_ID=$(echo "$OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
    
    touch test-output.md
    bash skills/skill-timing/scripts/run_timing.sh end \
        --run-id "$RUN_ID" \
        --output-file test-output.md \
        --skill perf-test \
        --format quiet >/dev/null 2>&1 || true
    rm -f test-output.md
done

END=$(date +%s.%N)
ELAPSED=$(echo "$END - $START" | bc)
AVG=$(echo "scale=3; $ELAPSED / 10" | bc)

echo "Average timing overhead: ${AVG}s per start/end cycle"
# Expected: <0.5s per cycle
```

## Cleanup After Validation

```bash
rm -f reviews/.timing-data/skill-timing-*-test*.json
rm -f reviews/.timing-data/skill-timing-registry.json
```
