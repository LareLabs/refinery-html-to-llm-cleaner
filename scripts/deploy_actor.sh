#!/usr/bin/env bash
# Deploy Docker image (lean zip) then restore Console prefill via API.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> deploy as larelabs (apify info skipped — can hang)"

SCHEMA_BACKUP="$(mktemp)"
ACTOR_BACKUP="$(mktemp)"
cp INPUT_SCHEMA.json "$SCHEMA_BACKUP"
cp .actor/actor.json "$ACTOR_BACKUP"

echo "==> lean zip for Docker build (avoid huge prefill in archive)"
python3 <<'PY'
import json
from pathlib import Path
schema = json.loads(Path("INPUT_SCHEMA.json").read_text(encoding="utf-8"))
schema["properties"]["raw_payload"]["prefill"] = ""
schema["properties"]["raw_payload"]["description"] = (
    "Paste HTML. After deploy: hard-refresh Console or run scripts/sync_console_source.py for Lipstick demo prefill."
)
Path("INPUT_SCHEMA.json").write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

actor = json.loads(Path(".actor/actor.json").read_text(encoding="utf-8"))
actor["exampleRunInput"] = {
    "body": '{"urls":["https://example.com"],"removeScripts":true,"removeStyles":true,"includeMetadata":true}',
    "contentType": "application/json; charset=utf-8",
}
Path(".actor/actor.json").write_text(json.dumps(actor, indent=2) + "\n", encoding="utf-8")
print("lean schema + example ready")
PY

# cache bust
sed -i "s/ARG REFINERY_VERSION=.*/ARG REFINERY_VERSION=1.1.63-qa-deploy/" Dockerfile

echo "==> apify push"
if apify actors push --force; then
  echo "==> push OK; restoring Console prefill via API"
  cp "$SCHEMA_BACKUP" INPUT_SCHEMA.json
  cp "$ACTOR_BACKUP" .actor/actor.json
  python3 scripts/sync_console_source.py
  python3 scripts/sync_store_readme.py
  python3 scripts/qa_production.py
else
  echo "==> push FAILED; restoring local files"
  cp "$SCHEMA_BACKUP" INPUT_SCHEMA.json
  cp "$ACTOR_BACKUP" .actor/actor.json
  exit 1
fi
