#!/usr/bin/env bash
# Local + live Apify QA. Run before deploy or after actor changes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> local unit tests"
python3 scripts/test_local.py

echo ""
echo "==> import validation"
python3 validate_imports.py

echo ""
echo "==> production QA (Apify API)"
python3 scripts/qa_production.py

echo ""
echo "All tests passed."
