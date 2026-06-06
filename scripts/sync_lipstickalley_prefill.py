#!/usr/bin/env python3
"""Refresh INPUT_SCHEMA raw_payload prefill from Wayback Lipstick Alley HTML."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "INPUT_SCHEMA.json"
ASSET = ROOT / "assets" / "prefill-lipstickalley-wayback.html"
WAYBACK_URL = "https://web.archive.org/web/2024/https://www.lipstickalley.com/"
MAX_CHARS = 25_000  # Apify Console + INPUT_SCHEMA stay responsive


def fetch_html() -> str:
    import httpx

    r = httpx.get(WAYBACK_URL, follow_redirects=True, timeout=60.0)
    r.raise_for_status()
    html = r.text
    if len(html) > MAX_CHARS:
        html = html[:MAX_CHARS] + "\n<!-- truncated for Apify input prefill demo -->"
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    ASSET.write_text(html, encoding="utf-8")
    return html


def apply_prefill(html: str) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    schema["properties"]["urls"]["prefill"] = []
    schema["properties"]["raw_payload"]["prefill"] = html
    SCHEMA.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    html = ASSET.read_text(encoding="utf-8") if "--local" in sys.argv else fetch_html()
    apply_prefill(html)
    print(f"Updated {SCHEMA} ({len(html)} chars prefill)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
