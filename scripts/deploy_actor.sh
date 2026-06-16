#!/usr/bin/env bash
# Deploy Docker image from lean git source, then restore Console prefill via API.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> apify push (git source is lean — prefill restored via sync_console_source.py)"
if apify actors push --force; then
  echo "==> push OK; syncing Console prefill + README"
  python3 scripts/sync_console_source.py
  python3 scripts/sync_store_readme.py
  python3 scripts/qa_production.py
else
  echo "==> push FAILED"
  exit 1
fi
