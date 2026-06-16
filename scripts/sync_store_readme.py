#!/usr/bin/env python3
"""Push README.md to Apify version source (Console Information tab + Store body)."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
ACTOR_ID = "E5JQI6n1Xle0Mn0G6"
VERSION = "1.1"
AUTH_PATH = Path("/root/.apify/auth.json")


def main() -> int:
    if not README.is_file():
        print(f"Missing {README}", file=sys.stderr)
        return 1

    readme = README.read_text(encoding="utf-8")
    if len(readme) > 250_000:
        print(f"README too large ({len(readme)} bytes); compress images first.", file=sys.stderr)
        return 1

    token = json.loads(AUTH_PATH.read_text())["token"]
    payload = {
        "sourceType": "GIT_REPO",
        "gitRepoUrl": "https://github.com/LareLabs/refinery-html-to-llm-cleaner",
        "buildTag": "latest",
        "sourceFiles": [
            {"name": "README.md", "format": "TEXT", "content": readme},
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
    except urllib.error.HTTPError as exc:
        print(exc.read().decode(), file=sys.stderr)
        return 1

    print(f"Synced README ({len(readme):,} bytes) to Apify version {VERSION}.")
    print("Hard-refresh Console → Information → latest → readme.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
