#!/usr/bin/env python3
"""Push actor title, description, and SEO fields from .actor/actor.json to Apify."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTOR_JSON = ROOT / ".actor" / "actor.json"
ACTOR_ID = "E5JQI6n1Xle0Mn0G6"
AUTH_PATH = Path("/root/.apify/auth.json")


def main() -> int:
    actor = json.loads(ACTOR_JSON.read_text(encoding="utf-8"))
    payload = {
        "title": actor["title"],
        "description": actor["description"],
        "seoTitle": actor.get("seoTitle"),
        "seoDescription": actor.get("seoDescription"),
        "categories": actor.get("categories", []),
        "exampleRunInput": actor.get("exampleRunInput"),
    }
    token = json.loads(AUTH_PATH.read_text())["token"]
    req = urllib.request.Request(
        f"https://api.apify.com/v2/acts/{ACTOR_ID}",
        data=json.dumps(payload).encode("utf-8"),
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.load(resp).get("data", {})
    except urllib.error.HTTPError as exc:
        print(exc.read().decode(), file=sys.stderr)
        return 1

    print(f"Synced actor metadata for {ACTOR_ID}")
    print(f"  title: {data.get('title')}")
    print(f"  seoTitle: {data.get('seoTitle')}")
    eri = data.get("exampleRunInput", {})
    preview = (eri.get("body") or "")[:80]
    print(f"  exampleRunInput: {preview}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
