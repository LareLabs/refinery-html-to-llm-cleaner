#!/usr/bin/env bash
# Sync everything that affects Store SEO, Console UX, and quality score — no Docker rebuild.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> embed + sync Store README"
python3 scripts/embed_store_readme.py
python3 scripts/sync_store_readme.py

echo "==> sync Console input/output schemas + example input"
python3 scripts/sync_console_source.py

echo "==> sync actor metadata (title, SEO, exampleRunInput)"
python3 scripts/sync_actor_metadata.py

echo "==> done — hard-refresh Console + Store page"
