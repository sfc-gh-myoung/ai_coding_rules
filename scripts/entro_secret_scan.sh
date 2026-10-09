#!/usr/bin/env bash

echo "Running entro security custom pre-commit hook..."

if git config --bool entro.skipSecretScan; then
  echo "Custom Hook: 🛑 Skipping secret scan due to git config 'entro.skipSecretScan' is true."
  exit 0
fi

echo "Custom Hook: ✅ 'entro.skipSecretScan' is NOT true. Proceeding with scan."

entro scan pre-commit . --fail-on-findings "$@" || { # '||' means: if previous command fails (non-zero exit)
  echo "Custom Hook: ❌ entro cli scan FAILED! Please fix issues before committing."
  exit 1
}

echo "Custom Hook: ✅ entro cli scan completed successfully."
exit 0
