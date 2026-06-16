#!/usr/bin/env python3
"""Push INPUT_SCHEMA.json to Apify version source (Console input form, no Docker rebuild)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "INPUT_SCHEMA.json"
ACTOR_ID = "E5JQI6n1Xle0Mn0G6"
VERSION = "1.1"
AUTH_PATH = Path("/root/.apify/auth.json")


def main() -> int:
    if not SCHEMA.is_file():
        print(f"Missing {SCHEMA}", file=sys.stderr)
        return 1

    schema_text = SCHEMA.read_text(encoding="utf-8")
    if len(schema_text) > 300_000:
        print(f"INPUT_SCHEMA too large ({len(schema_text)} bytes)", file=sys.stderr)
        return 1

    token = json.loads(AUTH_PATH.read_text())["token"]
    payload = {
        "sourceType": "GIT_REPO",
        "gitRepoUrl": "https://github.com/LareLabs/refinery-html-to-llm-cleaner",
        "buildTag": "latest",
        "sourceFiles": [
            {"name": "INPUT_SCHEMA.json", "format": "TEXT", "content": schema_text},
        ],
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
        with urllib.request.urlopen(req, timeout=120) as resp:
            json.load(resp)
    except urllib.error.HTTPError as e:
        print(e.read().decode(), file=sys.stderr)
        return 1

    print(f"Pushed {SCHEMA} to actor {ACTOR_ID} version {VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
