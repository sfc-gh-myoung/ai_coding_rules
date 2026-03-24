#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TIMING_DATA_DIR="$PROJECT_ROOT/reviews/.timing-data"

echo "========================================"
echo "Skill Timing Test Suite"
echo "========================================"
echo ""

# Test 1: Wrapper script is executable
echo "TEST 1: Wrapper script permissions"
if [[ ! -x "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" ]]; then
    echo "❌ FAIL: Wrapper not executable"
    exit 1
fi
echo "✓ PASS: Wrapper is executable"
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
OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
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
CHECKPOINT_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" checkpoint \
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

END_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
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
INVALID_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
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
    bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
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
TEST_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
    --skill storage-test --target test.md --model test-model 2>&1)
TEST_FILE=$(echo "$TEST_OUTPUT" | grep "TIMING_FILE=" | cut -d= -f2)

if [[ "$TEST_FILE" != reviews/.timing-data/* ]]; then
    echo "❌ FAIL: Timing file not in reviews/.timing-data/: $TEST_FILE"
    exit 1
fi

TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
touch "$PROJECT_ROOT/test-storage.md"
bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-storage.md" \
    --skill storage-test --format quiet >/dev/null 2>&1 || true
rm -f "$PROJECT_ROOT/test-storage.md"

echo "✓ PASS: Timing files stored in reviews/.timing-data/"
echo ""

# Test 9: CLI help text
echo "TEST 9: CLI help text"
if ! bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" --help 2>&1 | grep -q "Available commands"; then
    echo "❌ FAIL: Help text not comprehensive"
    exit 1
fi
echo "✓ PASS: CLI help text present"
echo ""

# Test 10: Baseline with lowered min-samples for testing
echo "TEST 10: Baseline system (with --min-samples 2)"
for i in {1..2}; do
    TEST_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
        --skill baseline-test \
        --target test.md \
        --model test-model 2>&1)
    TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

    sleep 1

    touch "$PROJECT_ROOT/test-baseline.md"
    bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
        --run-id "$TEST_RUN_ID" \
        --output-file "$PROJECT_ROOT/test-baseline.md" \
        --skill baseline-test >/dev/null 2>&1
    rm -f "$PROJECT_ROOT/test-baseline.md"
done

BASELINE_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" baseline set \
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
TEST_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
    --skill json-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

touch "$PROJECT_ROOT/test-json.md"
JSON_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
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
TEST_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
    --skill md-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

touch "$PROJECT_ROOT/test-md.md"
MD_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
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
TEST_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
    --skill ci-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

touch "$PROJECT_ROOT/test-ci.md"
bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
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
TEST_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
    --skill analyze-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
touch "$PROJECT_ROOT/test-analyze.md"
bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-analyze.md" \
    --skill analyze-test \
    --format quiet >/dev/null 2>&1 || true
rm -f "$PROJECT_ROOT/test-analyze.md"

ANALYZE_JSON=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" analyze \
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
TEST_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
    --skill recovery-test --target test.md --model test-model 2>&1)
TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)

touch "$PROJECT_ROOT/test-recovery.md"
bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
    --run-id "$TEST_RUN_ID" \
    --output-file "$PROJECT_ROOT/test-recovery.md" \
    --skill recovery-test --format quiet >/dev/null 2>&1 || true

RECOVERY_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
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

echo "========================================"
echo "All 15 tests passed!"
echo "========================================"
