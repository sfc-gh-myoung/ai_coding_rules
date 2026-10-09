#!/usr/bin/env bash
# Script: run-eval.sh
# Description: Run ai-rules rule-loader eval across multiple models

set -euo pipefail
IFS=$'\n\t'

readonly SCRIPT_NAME="${BASH_SOURCE[0]##*/}"

# --- Configuration (update as needed) ---
readonly CONNECTION="default"
readonly RUNS=5
readonly RETRY_INFRA=2
readonly CONCURRENCY=3

readonly MODELS=(
  auto-intelligent
  auto-efficient
  openai-gpt-6-astra
  claude-opus-5-5
  openai-gpt-6-sol
  claude-opus-5
  claude-opus-4-8
  claude-opus-4-7
  claude-opus-4-6
  claude-opus-4-5
  claude-sonnet-5
  claude-sonnet-4-6
  claude-sonnet-4-5
  openai-gpt-5.6-sol
  openai-gpt-5.5
  openai-gpt-5.4
  openai-gpt-5.2
  gemini-3.1-pro
  gemini-3.8-flash
  openai-gpt-6-luna
  kimi-k3
  deepseek-v4-flash
  glm-5.2
  openai-gpt-5.6-terra
  openai-gpt-5.6-luna
  grok-4.6
  gemini-3.7-flash
)

show_usage() {
  cat <<USAGE
Usage: ${SCRIPT_NAME} [options]

Run ai-rules rule-loader eval across multiple models.

Options:
    -h                  Show this help message
    --max-turns N       Max agent turns per fixture (default: eval default)
    --effort LEVEL      Effort level: low|medium|high (default: eval default)
    --label TEXT        Label recorded in manifest.json
    --without-plugin    Use prompt-only discovery (no manifest injection)
USAGE
}

cleanup() {
  local exit_code=$?
  if [[ ${exit_code} -ne 0 ]]; then
    echo "ERROR: ${SCRIPT_NAME} exited with code ${exit_code}" >&2
  fi
  exit "${exit_code}"
}
trap cleanup EXIT INT TERM

main() {
  local max_turns=""
  local effort=""
  local label=""
  local without_plugin=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help) show_usage; exit 0 ;;
      --max-turns) max_turns="$2"; shift 2 ;;
      --effort) effort="$2"; shift 2 ;;
      --label) label="$2"; shift 2 ;;
      --without-plugin) without_plugin=true; shift ;;
      *) echo "ERROR: Unknown option: $1" >&2; show_usage >&2; exit 1 ;;
    esac
  done

  if ! command -v ai-rules &>/dev/null; then
    echo "ERROR: ai-rules command not found" >&2
    exit 1
  fi

  # Build extra args array
  local -a extra_args=()
  [[ -n "${max_turns}" ]] && extra_args+=(--max-turns "${max_turns}")
  [[ -n "${effort}" ]] && extra_args+=(--effort "${effort}")
  [[ -n "${label}" ]] && extra_args+=(--label "${label}")
  [[ "${without_plugin}" == "true" ]] && extra_args+=(--without-plugin)

  echo "Starting eval run: ${#MODELS[@]} models, ${RUNS} runs each"

  local -a failed_models=()

  for model in "${MODELS[@]}"; do
    echo "=== Running eval: ${model} ==="
    local rc=0
    ai-rules rule-loader eval \
      --connection "${CONNECTION}" \
      --model "${model}" \
      --runs "${RUNS}" \
      --retry-infra "${RETRY_INFRA}" \
      --concurrency "${CONCURRENCY}" \
      "${extra_args[@]+"${extra_args[@]}"}" || rc=$?
    if [[ ${rc} -ge 3 ]]; then
      echo "WARNING: eval infrastructure failure for model ${model} (exit code: ${rc}), continuing..." >&2
      failed_models+=("${model}")
    elif [[ ${rc} -eq 1 ]]; then
      echo "INFO: eval completed for ${model} with fixture failures (exit code: 1)" >&2
    elif [[ ${rc} -eq 2 ]]; then
      echo "INFO: eval completed for ${model} with drift detected (exit code: 2)" >&2
    fi
  done

  echo "--- Summary ---"
  echo "Total models: ${#MODELS[@]}"
  echo "Failed: ${#failed_models[@]}"
  if [[ ${#failed_models[@]} -gt 0 ]]; then
    printf '  - %s\n' "${failed_models[@]}"
    exit 1
  fi
  echo "All model evals complete."
}

main "$@"
