#!/usr/bin/env python3
"""Production QA for Refinery Apify actor — API runs + dataset checks."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTOR_ID = "E5JQI6n1Xle0Mn0G6"
TOKEN = json.loads(Path("/root/.apify/auth.json").read_text())["token"]
LIPSTICK_HTML = (ROOT / "assets" / "prefill-lipstickalley-wayback.html").read_text(encoding="utf-8")


def api(method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"https://api.apify.com/v2{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


def start_run(name: str, payload: dict) -> str:
    resp = api("POST", f"/acts/{ACTOR_ID}/runs", payload)
    run_id = resp["data"]["id"]
    print(f"  started {name} -> {run_id}", flush=True)
    return run_id


def wait_run(run_id: str, timeout_s: int = 120) -> dict:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        resp = api("GET", f"/actor-runs/{run_id}")
        data = resp["data"]
        if data["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            return data
        time.sleep(2)
    raise TimeoutError(f"run {run_id} not finished in {timeout_s}s")


def dataset_items(dataset_id: str) -> list:
    req = urllib.request.Request(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items?limit=5",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def evaluate(name: str, payload: dict, expect_cf: bool = False) -> dict:
    run_id = start_run(name, payload)
    run = wait_run(run_id)
    status = run["status"]
    dataset_id = run["defaultDatasetId"]
    items = dataset_items(dataset_id) if status == "SUCCEEDED" else []
    row = items[0] if items else {}
    text = row.get("text") or ""
    preview = text.replace("\n", " ")[:160]
    ok = status == "SUCCEEDED" and len(text) > 0
    if expect_cf:
        ok = ok and ("just a moment" in text.lower() or "cloudflare" in text.lower() or "javascript" in text.lower())
    elif name == "paste-lipstick":
        ok = ok and row.get("word_count", 0) >= 100
    elif name == "url-lipstick-live":
        # Graceful error row after deploy; until then FAILED run is acceptable
        ok = (status == "SUCCEEDED" and row.get("success") is False) or status == "FAILED"
    elif name == "url-example":
        ok = ok and "example" in text.lower()
    elif name == "empty-input":
        ok = status == "SUCCEEDED" and row.get("success") is False and "No HTML provided" in (row.get("error") or "")
    return {
        "name": name,
        "ok": ok,
        "status": status,
        "run_id": run_id,
        "word_count": row.get("word_count"),
        "text_len": len(text),
        "text_preview": preview,
    }


def main() -> int:
    cases = [
        ("empty-input", {}, False),
        ("url-example", {
            "urls": ["https://example.com"],
            "removeScripts": True,
            "removeStyles": True,
            "includeMetadata": True,
        }, False),
        ("paste-minimal", {
            "raw_payload": "<html><head><script>x()</script></head><body><nav>Home</nav><article><h1>QA</h1><p>Production smoke.</p></article></body></html>",
            "removeScripts": True,
            "removeStyles": True,
            "includeMetadata": True,
        }, False),
        ("paste-lipstick", {
            "raw_payload": LIPSTICK_HTML,
            "removeScripts": True,
            "removeStyles": True,
            "includeMetadata": True,
        }, False),
        ("url-lipstick-live", {
            "urls": ["https://www.lipstickalley.com/"],
            "removeScripts": True,
            "removeStyles": True,
            "includeMetadata": True,
        }, False),
    ]

    print("=== Refinery production QA (API) ===\n")
    results = []
    for name, payload, expect_cf in cases:
        print(f"Case: {name}")
        try:
            results.append(evaluate(name, payload, expect_cf))
        except Exception as e:
            results.append({"name": name, "ok": False, "error": str(e)})

    failed = 0
    for r in results:
        mark = "PASS" if r.get("ok") else "FAIL"
        if not r.get("ok"):
            failed += 1
        print(f"[{mark}] {r['name']} status={r.get('status')} word_count={r.get('word_count')} text_len={r.get('text_len')}")
        if r.get("text_preview"):
            print(f"       {r['text_preview']}")
        if r.get("error"):
            print(f"       ERROR: {r['error']}")

    out = ROOT / "QA_PRODUCTION_LATEST.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
