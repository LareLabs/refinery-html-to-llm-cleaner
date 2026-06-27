#!/usr/bin/env python3
"""Push Console-facing source to Apify version 1.1 (no Docker rebuild)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTOR_ID = "E5JQI6n1Xle0Mn0G6"
VERSION = "1.1"
AUTH_PATH = Path("/root/.apify/auth.json")
PREFILL_ASSET = ROOT / "assets" / "prefill-lipstickalley-wayback.html"


def console_input_schema() -> str:
    schema = json.loads((ROOT / "INPUT_SCHEMA.json").read_text(encoding="utf-8"))
    schema["properties"]["urls"]["prefill"] = ["https://example.com"]
    if PREFILL_ASSET.is_file():
        schema["properties"]["raw_payload"]["prefill"] = PREFILL_ASSET.read_text(encoding="utf-8")
        schema["properties"]["raw_payload"]["description"] = (
            "Paste raw HTML from your crawler. Prefilled: Wayback snapshot of lipstickalley.com "
            "— switch to paste mode and run as-is to see heavy-HTML cleanup."
        )
    return json.dumps(schema, indent=2, ensure_ascii=False) + "\n"


def console_actor_json() -> str:
    actor = json.loads((ROOT / ".actor" / "actor.json").read_text(encoding="utf-8"))
    prefill = PREFILL_ASSET.read_text(encoding="utf-8") if PREFILL_ASSET.is_file() else ""
    body = json.dumps(
        {
            "urls": ["https://example.com"],
            "raw_payload": prefill,
            "removeScripts": True,
            "removeStyles": True,
            "includeMetadata": True,
        },
        ensure_ascii=False,
    )
    actor["exampleRunInput"] = {
        "body": body,
        "contentType": "application/json; charset=utf-8",
    }
    return json.dumps(actor, indent=2) + "\n"


def main() -> int:
    token = json.loads(AUTH_PATH.read_text())["token"]
    source_files = [
        {"name": "INPUT_SCHEMA.json", "format": "TEXT", "content": console_input_schema()},
        {"name": ".actor/actor.json", "format": "TEXT", "content": console_actor_json()},
    ]
    for item in source_files:
        print(f"  + {item['name']} ({len(item['content'])} bytes)")

    payload = {
        "sourceType": "GIT_REPO",
        "gitRepoUrl": "https://github.com/LareLabs/refinery-html-to-llm-cleaner",
        "buildTag": "latest",
        "sourceFiles": source_files,
    }

    req = urllib.request.Request(
        f"https://api.apify.com/v2/acts/{ACTOR_ID}/versions/{VERSION}",
        data=json.dumps(payload).encode("utf-8"),
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            json.load(resp)
    except urllib.error.HTTPError as e:
        print(e.read().decode(), file=sys.stderr)
        return 1

    print(f"Synced Console source to {ACTOR_ID} v{VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
