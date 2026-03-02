# CI/CD Integration Example

## Scenario

Integrate skill timing into automated CI/CD pipelines with machine-readable output and proper exit codes.

## Exit Codes

| Code | Meaning | CI Action |
|------|---------|-----------|
| 0 | Success (within baseline or no baseline) | Pass |
| 1 | General error (missing file, invalid data) | Fail |
| 2 | Duration below error threshold (shortcut detected) | Fail |
| 3 | Duration significantly above baseline | Warning/Fail |

## Output Formats

### JSON Format (for parsing)

```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id a1b2c3d4e5f67890 \
    --output-file output.md \
    --skill rule-reviewer \
    --format json
```

**Output:**
```json
{
  "run_id": "a1b2c3d4e5f67890",
  "skill_name": "rule-reviewer",
  "model": "claude-sonnet-45",
  "duration_seconds": 225.5,
  "duration_human": "3m 45s",
  "status": "completed",
  "alerts": [],
  "baseline_comparison": {
    "delta_percent": 6.4,
    "status": "within_normal"
  }
}
```

### CI Mode (JSON + exit codes)

```bash
bash skills/skill-timing/scripts/run_timing.sh end \
    --run-id a1b2c3d4e5f67890 \
    --output-file output.md \
    --skill rule-reviewer \
    --ci

echo "Exit code: $?"
```

### CSV Format (for analysis)

```bash
bash skills/skill-timing/scripts/run_timing.sh analyze \
    --skill rule-reviewer \
    --days 7 \
    --format csv
```

**Output:**
```csv
skill,model,run_id,duration_seconds,status
rule-reviewer,claude-sonnet-45,a1b2c3d4,225.5,completed
rule-reviewer,claude-sonnet-45,b2c3d4e5,198.3,completed
```

## GitHub Actions Example

```yaml
name: Skill Timing CI

on: [push, pull_request]

jobs:
  timing-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Run skill with timing
        id: timing
        run: |
          # Start timing
          TIMING_OUTPUT=$(python skills/skill-timing/scripts/skill_timing.py start \
            --skill my-skill \
            --target input.md \
            --model claude-sonnet-45)
          
          RUN_ID=$(echo "$TIMING_OUTPUT" | grep TIMING_RUN_ID | cut -d= -f2)
          echo "run_id=$RUN_ID" >> $GITHUB_OUTPUT
          
          # Run your skill here
          # python run_my_skill.py input.md output.md
          touch output.md  # Placeholder
          
          # End timing with CI mode
          python skills/skill-timing/scripts/skill_timing.py end \
            --run-id "$RUN_ID" \
            --output-file output.md \
            --skill my-skill \
            --ci > timing-result.json
          
          # Save exit code
          EXIT_CODE=$?
          echo "exit_code=$EXIT_CODE" >> $GITHUB_OUTPUT
          
          # Parse duration for annotation
          DURATION=$(jq -r '.duration_human' timing-result.json)
          echo "duration=$DURATION" >> $GITHUB_OUTPUT
          
          exit $EXIT_CODE
      
      - name: Check for shortcuts
        if: failure()
        run: |
          if [ "${{ steps.timing.outputs.exit_code }}" == "2" ]; then
            echo "::error::Shortcut detected - skill completed too quickly"
          fi
      
      - name: Report timing
        if: always()
        run: |
          echo "::notice::Skill completed in ${{ steps.timing.outputs.duration }}"
      
      - name: Upload timing data
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: timing-data
          path: |
            timing-result.json
            reviews/.timing-data/
```

## GitLab CI Example

```yaml
timing-check:
  stage: test
  script:
    - |
      # Start timing
      TIMING_OUTPUT=$(python skills/skill-timing/scripts/skill_timing.py start \
        --skill my-skill \
        --target input.md \
        --model claude-sonnet-45)
      RUN_ID=$(echo "$TIMING_OUTPUT" | grep TIMING_RUN_ID | cut -d= -f2)
      
      # Run skill
      touch output.md
      
      # End timing
      python skills/skill-timing/scripts/skill_timing.py end \
        --run-id "$RUN_ID" \
        --output-file output.md \
        --skill my-skill \
        --format json > timing.json
      
      # Check exit code
      EXIT_CODE=$?
      if [ $EXIT_CODE -eq 2 ]; then
        echo "ERROR: Shortcut detected"
        exit 1
      fi
      
      cat timing.json
  artifacts:
    paths:
      - timing.json
    when: always
```

## Shell Script Integration

```bash
#!/bin/bash
set -e

run_with_timing() {
    local skill="$1"
    local target="$2"
    local output="$3"
    local model="${4:-claude-sonnet-45}"
    
    # Start timing
    local timing_output
    timing_output=$(bash skills/skill-timing/scripts/run_timing.sh start \
        --skill "$skill" \
        --target "$target" \
        --model "$model")
    
    local run_id
    run_id=$(echo "$timing_output" | grep TIMING_RUN_ID | cut -d= -f2)
    
    # Run your skill here
    # ...
    
    # End timing with JSON output
    bash skills/skill-timing/scripts/run_timing.sh end \
        --run-id "$run_id" \
        --output-file "$output" \
        --skill "$skill" \
        --format json
    
    local exit_code=$?
    
    case $exit_code in
        0) echo "Success" ;;
        2) echo "ERROR: Shortcut detected"; return 1 ;;
        3) echo "WARNING: Slower than baseline" ;;
        *) echo "ERROR: Timing failed"; return 1 ;;
    esac
    
    return 0
}

# Usage
run_with_timing "rule-reviewer" "rules/100.md" "reviews/100-review.md"
```

## Aggregate Timing Data

For reporting across multiple runs:

```bash
# Aggregate from review files
bash skills/skill-timing/scripts/run_timing.sh aggregate \
    reviews/*.md \
    --format json > aggregate.json

# Or as CSV for spreadsheet import
bash skills/skill-timing/scripts/run_timing.sh aggregate \
    reviews/*.md \
    --format csv > aggregate.csv
```
