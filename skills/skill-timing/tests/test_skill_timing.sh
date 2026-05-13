#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TIMING_DATA_DIR="$PROJECT_ROOT/reviews/.timing-data"

PYTHON=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/find_python.sh")
TIMING_PY="$PROJECT_ROOT/skills/skill-timing/scripts/skill_timing.py"

echo "========================================"
echo "Skill Timing Test Suite"
echo "========================================"
echo ""

# Test 1: find_python.sh is executable and returns a valid interpreter
echo "TEST 1: find_python.sh permissions and output"
if [[ ! -x "$PROJECT_ROOT/skills/skill-timing/scripts/find_python.sh" ]]; then
    echo "❌ FAIL: find_python.sh not executable"
    exit 1
fi
if [[ -z "$PYTHON" ]]; then
    echo "❌ FAIL: find_python.sh returned empty string"
    exit 1
fi
echo "✓ PASS: find_python.sh is executable (PYTHON=$PYTHON)"
echo ""

# Test 2: Python module loads without errors
echo "TEST 2: Python module syntax"
if ! python3 -m py_compile "$PROJECT_ROOT/skills/skill-timing/scripts/skill_timing.py" 2>/dev/null; then
    echo "❌ FAIL: Python module has syntax errors"
    exit 1
fi
echo "✓ PASS: Python module syntax valid"
echo ""

# Test 3: Start command and validate run_id capture
echo "TEST 3: Start command"
OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill test-skill \
    --target test.md \
    --model test-model 2>&1)

RUN_ID=$(echo "$OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

if [[ ! "$RUN_ID" =~ ^[a-f0-9]{16}$ ]]; then
    echo "❌ FAIL: Invalid run_id format: $RUN_ID"
    echo "Output was: $OUTPUT"
    exit 1
fi

echo "✓ PASS: Captured valid RUN_ID: $RUN_ID"
echo ""

# Test 4: Checkpoint command
echo "TEST 4: Checkpoint command"
CHECKPOINT_OUTPUT=$($PYTHON "$TIMING_PY" checkpoint \
    --run-id "$RUN_ID" \
    --name test_checkpoint 2>&1)

if ! echo "$CHECKPOINT_OUTPUT" | grep -q "CHECKPOINT_STATUS=recorded"; then
    echo "❌ FAIL: Checkpoint not recorded"
    echo "Output was: $CHECKPOINT_OUTPUT"
    exit 1
fi

echo "✓ PASS: Checkpoint recorded"
echo ""

# Test 5: End command
echo "TEST 5: End command"
touch "$PROJECT_ROOT/test-output.md"

END_OUTPUT=$($PYTHON "$TIMING_PY" end \
    --run-id "$RUN_ID" \
    --output-file "$PROJECT_ROOT/test-output.md" \
    --skill test-skill \
    --input-tokens 1000 \
    --output-tokens 500 2>&1)

if ! echo "$END_OUTPUT" | grep -qE "TIMING_STATUS=(completed|warning)"; then
    echo "❌ FAIL: End command did not complete"
    echo "Output was: $END_OUTPUT"
    exit 1
fi

rm -f "$PROJECT_ROOT/test-output.md"
echo "✓ PASS: End command completed"
echo ""

# Test 6: Invalid run_id handling
echo "TEST 6: Invalid run_id format"
INVALID_OUTPUT=$($PYTHON "$TIMING_PY" end \
    --run-id "invalid-format-12345" \
    --output-file test.md \
    --skill test-skill 2>&1 || true)

if ! echo "$INVALID_OUTPUT" | grep -q "Invalid run_id format"; then
    echo "❌ FAIL: Invalid run_id not detected"
    echo "Output was: $INVALID_OUTPUT"
    exit 1
fi

echo "✓ PASS: Invalid run_id handled correctly"
echo ""

# Test 7: Parallel execution safety (collision resistance)
echo "TEST 7: Parallel execution (10 concurrent runs)"

rm -f "$TIMING_DATA_DIR"/skill-timing-*.json 2>/dev/null

for i in {1..10}; do
    $PYTHON "$TIMING_PY" start \
        --skill parallel-test-skill \
        --target "test-$i.md" \
        --model test-model >/dev/null 2>&1 &
done
wait

RUN_IDS=$(ls -1 "$TIMING_DATA_DIR"/skill-timing-*.json 2>/dev/null | grep -v "registry" | grep -v "\-complete" | wc -l | tr -d ' ')

if [[ "$RUN_IDS" -ne 10 ]]; then
    echo "❌ FAIL: Expected 10 unique run IDs, got $RUN_IDS"
    echo "Timing files created:"
    ls -1 "$TIMING_DATA_DIR"/skill-timing-*.json 2>/dev/null
    rm -f "$TIMING_DATA_DIR"/skill-timing-*.json
    exit 1
fi

rm -f "$TIMING_DATA_DIR"/skill-timing-*.json

echo "✓ PASS: Parallel execution safe (10 unique run IDs)"
echo ""

# Test 8: Timing files created in project directory (not /tmp)
echo "TEST 8: Project-local file storage"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill storage-test --target test.md --model test-model 2>&1)
TEST_FILE=$(echo "$TEST_OUTPUT" | grep "TIMING_FILE=" | cut -d= -f2)

if [[ "$TEST_FILE" != reviews/.timing-data/* ]]; then
    echo "❌ FAIL: Timing file not in reviews/.timing-data/: $TEST_FILE"
    exit 1
fi

TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
touch "$PROJECT_ROOT/test-storage.md"
$PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-storage.md" \
    --skill storage-test --format quiet >/dev/null 2>&1 || true
rm -f "$PROJECT_ROOT/test-storage.md"

echo "✓ PASS: Timing files stored in reviews/.timing-data/"
echo ""

# Test 9: CLI help text
echo "TEST 9: CLI help text"
if ! $PYTHON "$TIMING_PY" --help 2>&1 | grep -q "Available commands"; then
    echo "❌ FAIL: Help text not comprehensive"
    exit 1
fi
echo "✓ PASS: CLI help text present"
echo ""

# Test 10: Baseline with lowered min-samples for testing
echo "TEST 10: Baseline system (with --min-samples 2)"
for i in {1..2}; do
    TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
        --skill baseline-test \
        --target test.md \
        --model test-model 2>&1)
    TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

    sleep 1

    touch "$PROJECT_ROOT/test-baseline.md"
    $PYTHON "$TIMING_PY" end \
        --run-id "$TEST_RUN_ID" \
        --output-file "$PROJECT_ROOT/test-baseline.md" \
        --skill baseline-test >/dev/null 2>&1
    rm -f "$PROJECT_ROOT/test-baseline.md"
done

BASELINE_OUTPUT=$($PYTHON "$TIMING_PY" baseline set \
    --skill baseline-test \
    --mode FULL \
    --model test-model \
    --days 1 \
    --min-samples 2 2>&1 || true)

if ! echo "$BASELINE_OUTPUT" | grep -q "Baseline set"; then
    echo "❌ FAIL: Baseline not set with --min-samples 2"
    echo "Output was: $BASELINE_OUTPUT"
    exit 1
fi

rm -f "$PROJECT_ROOT/reviews/.timing-baselines.json"

echo "✓ PASS: Baseline system works with --min-samples flag"
echo ""

# Test 11: JSON output format validation
echo "TEST 11: JSON output format"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill json-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

touch "$PROJECT_ROOT/test-json.md"
JSON_OUTPUT=$($PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-json.md" \
    --skill json-test \
    --format json 2>&1) || true

if ! echo "$JSON_OUTPUT" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null; then
    echo "❌ FAIL: JSON output is not valid JSON"
    echo "Output was: $JSON_OUTPUT"
    rm -f "$PROJECT_ROOT/test-json.md"
    exit 1
fi
rm -f "$PROJECT_ROOT/test-json.md"
echo "✓ PASS: JSON output is valid"
echo ""

# Test 12: Markdown output format validation
echo "TEST 12: Markdown output format"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill md-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

touch "$PROJECT_ROOT/test-md.md"
MD_OUTPUT=$($PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-md.md" \
    --skill md-test \
    --format markdown 2>&1) || true

if ! echo "$MD_OUTPUT" | grep -q "## Timing Metadata"; then
    echo "❌ FAIL: Markdown output missing header"
    echo "Output was: $MD_OUTPUT"
    rm -f "$PROJECT_ROOT/test-md.md"
    exit 1
fi

if ! echo "$MD_OUTPUT" | grep -q "| Field | Value |"; then
    echo "❌ FAIL: Markdown output missing table headers"
    rm -f "$PROJECT_ROOT/test-md.md"
    exit 1
fi
rm -f "$PROJECT_ROOT/test-md.md"
echo "✓ PASS: Markdown output is valid"
echo ""

# Test 13: CI mode exit codes
echo "TEST 13: CI mode (--ci flag)"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill ci-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

touch "$PROJECT_ROOT/test-ci.md"
$PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-ci.md" \
    --skill ci-test \
    --ci > /dev/null 2>&1
CI_EXIT=$?
rm -f "$PROJECT_ROOT/test-ci.md"

if [[ "$CI_EXIT" -ne 0 && "$CI_EXIT" -ne 2 && "$CI_EXIT" -ne 3 ]]; then
    echo "❌ FAIL: Unexpected CI exit code: $CI_EXIT"
    exit 1
fi
echo "✓ PASS: CI mode returns appropriate exit code ($CI_EXIT)"
echo ""

# Test 14: Analyze --format json
echo "TEST 14: Analyze command JSON format"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill analyze-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
touch "$PROJECT_ROOT/test-analyze.md"
$PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-analyze.md" \
    --skill analyze-test \
    --format quiet >/dev/null 2>&1 || true
rm -f "$PROJECT_ROOT/test-analyze.md"

ANALYZE_JSON=$($PYTHON "$TIMING_PY" analyze \
    --skill analyze-test \
    --days 1 \
    --format json 2>&1)

if ! echo "$ANALYZE_JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'count' in d" 2>/dev/null; then
    echo "❌ FAIL: Analyze JSON output invalid"
    echo "Output was: $ANALYZE_JSON"
    exit 1
fi
echo "✓ PASS: Analyze JSON format valid"
echo ""

# Test 15: Completed-file recovery (idempotent end)
echo "TEST 15: Completed-file recovery"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill recovery-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

touch "$PROJECT_ROOT/test-recovery.md"
$PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-recovery.md" \
    --skill recovery-test --format quiet >/dev/null 2>&1 || true

RECOVERY_OUTPUT=$($PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-recovery.md" \
    --skill recovery-test --format markdown 2>&1) || true

if ! echo "$RECOVERY_OUTPUT" | grep -q "## Timing Metadata"; then
    echo "❌ FAIL: Completed-file recovery did not return timing data"
    echo "Output was: $RECOVERY_OUTPUT"
    rm -f "$PROJECT_ROOT/test-recovery.md"
    exit 1
fi
rm -f "$PROJECT_ROOT/test-recovery.md"
echo "✓ PASS: Completed-file recovery works (idempotent end)"
echo ""

# Final cleanup
rm -f "$TIMING_DATA_DIR"/skill-timing-*-complete.json
rm -f "$TIMING_DATA_DIR"/skill-timing-registry.json
rm -f "$TIMING_DATA_DIR"/skill-timing-*.json

# Test 16: Dimension timings passed via --dimension-timings
echo "TEST 16: Dimension timings via --dimension-timings"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill dim-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

sleep 1

touch "$PROJECT_ROOT/test-dim.md"
DIM_JSON='[{"dimension":"actionability","duration_seconds":42.3,"mode":"checkpoint"},{"dimension":"rule_size","duration_seconds":0.1,"mode":"inline"}]'
DIM_MD_OUTPUT=$($PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-dim.md" \
    --skill dim-test \
    --format markdown \
    --dimension-timings "$DIM_JSON" 2>&1) || true

if ! echo "$DIM_MD_OUTPUT" | grep -q "### Per-Dimension Timing"; then
    echo "❌ FAIL: Markdown output missing Per-Dimension Timing table"
    echo "Output was: $DIM_MD_OUTPUT"
    rm -f "$PROJECT_ROOT/test-dim.md"
    exit 1
fi

COMPLETED_FILE="$TIMING_DATA_DIR/skill-timing-${TEST_RUN_ID}-complete.json"
if ! python3 -c "import json; d=json.load(open('$COMPLETED_FILE')); assert 'dimension_timings' in d, 'missing dimension_timings'" 2>/dev/null; then
    echo "❌ FAIL: Completed JSON missing dimension_timings array"
    rm -f "$PROJECT_ROOT/test-dim.md"
    exit 1
fi

rm -f "$PROJECT_ROOT/test-dim.md"
echo "✓ PASS: Dimension timings stored and rendered in markdown"
echo ""

# Test 17: Dimension timings in JSON output format
echo "TEST 17: Dimension timings in JSON format"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill dim-json-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

sleep 1

touch "$PROJECT_ROOT/test-dim-json.md"
DIM_JSON='[{"dimension":"parsability","duration_seconds":38.7,"mode":"self-report"}]'
DIM_JSON_OUTPUT=$($PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-dim-json.md" \
    --skill dim-json-test \
    --format json \
    --dimension-timings "$DIM_JSON" 2>&1) || true

if ! echo "$DIM_JSON_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'dimension_timings' in d and isinstance(d['dimension_timings'], list)" 2>/dev/null; then
    echo "❌ FAIL: JSON output missing or invalid dimension_timings"
    echo "Output was: $DIM_JSON_OUTPUT"
    rm -f "$PROJECT_ROOT/test-dim-json.md"
    exit 1
fi

rm -f "$PROJECT_ROOT/test-dim-json.md"
echo "✓ PASS: Dimension timings present in JSON output"
echo ""

# Test 18: Empty dimension timings (graceful handling)
echo "TEST 18: Empty dimension timings"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill dim-empty-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

sleep 1

touch "$PROJECT_ROOT/test-dim-empty.md"
DIM_EMPTY_OUTPUT=$($PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-dim-empty.md" \
    --skill dim-empty-test \
    --format markdown \
    --dimension-timings '[]' 2>&1) || true

if echo "$DIM_EMPTY_OUTPUT" | grep -q "### Per-Dimension Timing"; then
    echo "❌ FAIL: Empty array should not produce Per-Dimension table"
    rm -f "$PROJECT_ROOT/test-dim-empty.md"
    exit 1
fi

rm -f "$PROJECT_ROOT/test-dim-empty.md"
echo "✓ PASS: Empty dimension timings handled gracefully"
echo ""

# Test 19: Malformed dimension timings (error handling)
echo "TEST 19: Malformed dimension timings"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill dim-malformed-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

sleep 1

touch "$PROJECT_ROOT/test-dim-malformed.md"
DIM_MALFORMED_OUTPUT=$($PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-dim-malformed.md" \
    --skill dim-malformed-test \
    --format markdown \
    --dimension-timings 'not-json' 2>&1) || true

if ! echo "$DIM_MALFORMED_OUTPUT" | grep -qi "VALIDATION ERROR.*parse"; then
    echo "❌ FAIL: No VALIDATION ERROR for malformed JSON"
    echo "Output was: $DIM_MALFORMED_OUTPUT"
    rm -f "$PROJECT_ROOT/test-dim-malformed.md"
    exit 1
fi

if ! echo "$DIM_MALFORMED_OUTPUT" | grep -q "## Timing Metadata"; then
    echo "❌ FAIL: Timing still should complete despite malformed dimension-timings"
    rm -f "$PROJECT_ROOT/test-dim-malformed.md"
    exit 1
fi

rm -f "$PROJECT_ROOT/test-dim-malformed.md"
echo "✓ PASS: Malformed dimension timings handled gracefully"
echo ""

# Test 20: Analyze with --per-dimension
echo "TEST 20: Analyze with --per-dimension"
for i in {1..2}; do
    TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
        --skill pd-analyze-test --target test.md --model test-model 2>&1)
    TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
    sleep 1
    touch "$PROJECT_ROOT/test-pd-analyze.md"
    DIM_JSON='[{"dimension":"actionability","duration_seconds":40.0,"mode":"checkpoint"},{"dimension":"parsability","duration_seconds":35.0,"mode":"checkpoint"}]'
    $PYTHON "$TIMING_PY" end \
        --run-id "$TEST_RUN_ID" \
        --output-file "$PROJECT_ROOT/test-pd-analyze.md" \
        --skill pd-analyze-test \
        --format quiet \
        --dimension-timings "$DIM_JSON" >/dev/null 2>&1 || true
    rm -f "$PROJECT_ROOT/test-pd-analyze.md"
done

PD_ANALYZE_OUTPUT=$($PYTHON "$TIMING_PY" analyze \
    --skill pd-analyze-test \
    --days 1 \
    --format json \
    --per-dimension 2>&1)

if ! echo "$PD_ANALYZE_OUTPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); assert 'per_dimension' in d" 2>/dev/null; then
    echo "❌ FAIL: Analyze JSON missing per_dimension"
    echo "Output was: $PD_ANALYZE_OUTPUT"
    exit 1
fi

echo "✓ PASS: Analyze --per-dimension works"
echo ""

# Test 21: Baseline set with --per-dimension
echo "TEST 21: Baseline set with --per-dimension"
for i in {1..3}; do
    TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
        --skill pd-baseline-test --target test.md --model test-model --mode FULL 2>&1)
    TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
    sleep 1
    touch "$PROJECT_ROOT/test-pd-baseline.md"
    DIM_JSON='[{"dimension":"actionability","duration_seconds":42.0,"mode":"checkpoint"},{"dimension":"rule_size","duration_seconds":0.1,"mode":"inline"}]'
    $PYTHON "$TIMING_PY" end \
        --run-id "$TEST_RUN_ID" \
        --output-file "$PROJECT_ROOT/test-pd-baseline.md" \
        --skill pd-baseline-test \
        --format quiet \
        --dimension-timings "$DIM_JSON" >/dev/null 2>&1 || true
    rm -f "$PROJECT_ROOT/test-pd-baseline.md"
done

BASELINE_PD_OUTPUT=$($PYTHON "$TIMING_PY" baseline set \
    --skill pd-baseline-test \
    --mode FULL \
    --model test-model \
    --days 1 \
    --min-samples 3 \
    --per-dimension 2>&1 || true)

if ! echo "$BASELINE_PD_OUTPUT" | grep -q "Baseline set"; then
    echo "❌ FAIL: Baseline not set with --per-dimension"
    echo "Output was: $BASELINE_PD_OUTPUT"
    exit 1
fi

BASELINES_FILE="$PROJECT_ROOT/reviews/.timing-baselines.json"
if ! python3 -c "
import json
d=json.load(open('$BASELINES_FILE'))
dims=d['pd-baseline-test']['FULL']['test-model'].get('dimensions',{})
assert 'actionability' in dims, 'missing actionability dimension'
assert 'avg_seconds' in dims['actionability'], 'missing avg_seconds'
assert 'stddev_seconds' in dims['actionability'], 'missing stddev_seconds'
" 2>/dev/null; then
    echo "❌ FAIL: Baselines JSON missing dimensions sub-key"
    exit 1
fi

echo "✓ PASS: Baseline set with --per-dimension works"
echo ""

# Test 22: Baseline compare with per-dimension output
echo "TEST 22: Baseline compare with per-dimension"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill pd-baseline-test --target test.md --model test-model --mode FULL 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
sleep 1
touch "$PROJECT_ROOT/test-pd-compare.md"
DIM_JSON='[{"dimension":"actionability","duration_seconds":142.0,"mode":"checkpoint"},{"dimension":"rule_size","duration_seconds":0.1,"mode":"inline"}]'
$PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-pd-compare.md" \
    --skill pd-baseline-test \
    --format quiet \
    --dimension-timings "$DIM_JSON" >/dev/null 2>&1 || true
rm -f "$PROJECT_ROOT/test-pd-compare.md"

COMPARE_OUTPUT=$($PYTHON "$TIMING_PY" baseline compare \
    --run-id "$TEST_RUN_ID" 2>&1 || true)

if ! echo "$COMPARE_OUTPUT" | grep -q "Per-Dimension Comparison"; then
    echo "❌ FAIL: Baseline compare missing per-dimension output"
    echo "Output was: $COMPARE_OUTPUT"
    exit 1
fi

if ! echo "$COMPARE_OUTPUT" | grep -q "significantly"; then
    echo "❌ FAIL: Outlier dimension not flagged"
    echo "Output was: $COMPARE_OUTPUT"
    exit 1
fi

echo "✓ PASS: Baseline compare with per-dimension works"
echo ""

# Test 23: Analyze with mixed runs (some with/without dimension_timings)
echo "TEST 23: Analyze with mixed runs"
TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
    --skill mixed-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
sleep 1
touch "$PROJECT_ROOT/test-mixed.md"
$PYTHON "$TIMING_PY" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-mixed.md" \
    --skill mixed-test \
    --format quiet >/dev/null 2>&1 || true
rm -f "$PROJECT_ROOT/test-mixed.md"

for i in {1..2}; do
    TEST_OUTPUT=$($PYTHON "$TIMING_PY" start \
        --skill mixed-test --target test.md --model test-model 2>&1)
    TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
    sleep 1
    touch "$PROJECT_ROOT/test-mixed.md"
    DIM_JSON='[{"dimension":"actionability","duration_seconds":40.0,"mode":"checkpoint"}]'
    $PYTHON "$TIMING_PY" end \
        --run-id "$TEST_RUN_ID" \
        --output-file "$PROJECT_ROOT/test-mixed.md" \
        --skill mixed-test \
        --format quiet \
        --dimension-timings "$DIM_JSON" >/dev/null 2>&1 || true
    rm -f "$PROJECT_ROOT/test-mixed.md"
done

MIXED_OUTPUT=$($PYTHON "$TIMING_PY" analyze \
    --skill mixed-test \
    --days 1 \
    --format json \
    --per-dimension 2>/dev/null)

MIXED_CHECK=$(echo "$MIXED_OUTPUT" | python3 -c "
import json,sys
d=json.load(sys.stdin)
pd=d.get('per_dimension',{})
act=pd.get('actionability',{})
print(act.get('count',0))
" 2>/dev/null)

if [[ "$MIXED_CHECK" != "2" ]]; then
    echo "❌ FAIL: Expected 2 runs in per-dimension, got $MIXED_CHECK"
    echo "Output was: $MIXED_OUTPUT"
    exit 1
fi

echo "✓ PASS: Mixed runs handled correctly (only 2 contribute to per-dimension)"
echo ""

# Test cleanup
rm -f "$TIMING_DATA_DIR"/skill-timing-*-complete.json
rm -f "$TIMING_DATA_DIR"/skill-timing-registry.json
rm -f "$TIMING_DATA_DIR"/skill-timing-*.json
rm -f "$PROJECT_ROOT/reviews/.timing-baselines.json"
rm -f /tmp/skill_timing_test_*

echo "========================================"
echo "All 23 tests passed!"
echo "========================================"
