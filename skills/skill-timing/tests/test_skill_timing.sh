#!/usr/bin/env bash
# Comprehensive test suite for skill-timing
# Tests all timing commands, error handling, and edge cases

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

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

# Note: Don't clean up RUN_ID timing file yet, needed for checkpoint test

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
# Create a dummy output file for the test
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

# Cleanup dummy file and completed timing files from this test
rm -f "$PROJECT_ROOT/test-output.md"
TEMP_DIR=$(python3 -c "import tempfile; print(tempfile.gettempdir())")
rm -f "$TEMP_DIR"/skill-timing-*-complete.json 2>/dev/null

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
# Get temp directory
TEMP_DIR=$(python3 -c "import tempfile; print(tempfile.gettempdir())")

# Clean up any existing timing files from previous runs
rm -f "$TEMP_DIR"/skill-timing-*.json 2>/dev/null
rm -f "$TEMP_DIR"/skill-timing-registry.json 2>/dev/null

for i in {1..10}; do
    bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
        --skill parallel-test-skill \
        --target "test-$i.md" \
        --model test-model >/dev/null 2>&1 &
done
wait

# Count unique timing files created (exclude registry file)
RUN_IDS=$(ls -1 "$TEMP_DIR"/skill-timing-*.json 2>/dev/null | grep -v "registry" | wc -l | tr -d ' ')

if [[ "$RUN_IDS" -ne 10 ]]; then
    echo "❌ FAIL: Expected 10 unique run IDs, got $RUN_IDS"
    echo "Timing files created:"
    ls -1 "$TEMP_DIR"/skill-timing-*.json 2>/dev/null
    # Cleanup
    rm -f "$TEMP_DIR"/skill-timing-*.json
    exit 1
fi

# Cleanup parallel test timing files
rm -f "$TEMP_DIR"/skill-timing-*.json

echo "✓ PASS: Parallel execution safe (10 unique run IDs)"
echo ""

# Test 8: Cross-platform temp directory
echo "TEST 8: Cross-platform path handling"
python3 -c "
import tempfile
from pathlib import Path

temp_dir = Path(tempfile.gettempdir())
assert temp_dir.exists(), 'Temp directory not accessible'
assert temp_dir.is_absolute(), 'Temp directory not absolute path'
print(f'✓ PASS: Temp directory: {temp_dir}')
"
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
# Create 2 test timing runs
for i in {1..2}; do
    TEST_OUTPUT=$(bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" start \
        --skill baseline-test \
        --target test.md \
        --model test-model 2>&1)
    TEST_RUN_ID=$(echo "$TEST_OUTPUT" | grep "TIMING_RUN_ID=" | cut -d= -f2)
    
    # Wait a moment to ensure different durations
    sleep 1
    
    touch "$PROJECT_ROOT/test-baseline.md"
    bash "$PROJECT_ROOT/skills/skill-timing/scripts/run_timing.sh" end \
        --run-id "$TEST_RUN_ID" \
        --output-file "$PROJECT_ROOT/test-baseline.md" \
        --skill baseline-test >/dev/null 2>&1
    rm -f "$PROJECT_ROOT/test-baseline.md"
done

# Try to set baseline with min-samples 2
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

# Cleanup baseline file
rm -f "$PROJECT_ROOT/reviews/.timing-baselines.json"

echo "✓ PASS: Baseline system works with --min-samples flag"
echo ""

# Cleanup all test timing files
rm -f "$TEMP_DIR"/skill-timing-*-complete.json
rm -f "$TEMP_DIR"/skill-timing-registry.json

echo "========================================"
echo "✅ All tests passed!"
echo "========================================"
