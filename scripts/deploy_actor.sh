#!/usr/bin/env bash
# Deploy via lean staging dir (Apify zip >3MB or extra files can fail on some build workers).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ACTOR_ID="${APIFY_ACTOR_ID:-E5JQI6n1Xle0Mn0G6}"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

echo "==> staging lean deploy to $STAGE"
for item in .actor app src requirements.txt README.md INPUT_SCHEMA.json OUTPUT_SCHEMA.json Dockerfile .apifyignore .dockerignore refinery_core_src; do
  cp -a "$ROOT/$item" "$STAGE/"
done

echo "==> apify push $ACTOR_ID"
if (cd "$STAGE" && apify actors push "$ACTOR_ID" --force); then
  echo "==> push OK; syncing Console prefill + README"
  python3 "$ROOT/scripts/sync_console_source.py"
  python3 "$ROOT/scripts/sync_store_readme.py"
  python3 "$ROOT/scripts/qa_production.py"
else
  echo "==> push FAILED"
  exit 1
fi
