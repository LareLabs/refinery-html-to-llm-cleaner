#!/usr/bin/env python3
"""Push Console-facing source to Apify version 1.1 (no Docker rebuild)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTOR_ID = "jOcx8jK2FdhZhoKrE"
VERSION = "1.1"
AUTH_PATH = Path("/root/.apify/auth.json")
FILES = [
    ROOT / "INPUT_SCHEMA.json",
    ROOT / ".actor" / "actor.json",
]


def main() -> int:
    token = json.loads(AUTH_PATH.read_text())["token"]
    source_files = []
    for path in FILES:
        if not path.is_file():
            print(f"Missing {path}", file=sys.stderr)
            return 1
        content = path.read_text(encoding="utf-8")
        name = "INPUT_SCHEMA.json" if path.name == "INPUT_SCHEMA.json" else ".actor/actor.json"
        source_files.append({"name": name, "format": "TEXT", "content": content})
        print(f"  + {name} ({len(content)} bytes)")

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
