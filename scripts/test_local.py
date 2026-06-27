#!/usr/bin/env python3
"""Fast local tests — no Apify API. Run before deploy."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest

import httpx
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "refinery_core_src"))


class _FakeActor:
    pass


def _ensure_apify_stub() -> None:
    if "apify" not in sys.modules:
        apify_mod = type(sys)("apify")
        apify_mod.Actor = _FakeActor
        sys.modules["apify"] = apify_mod


def load_main_module():
    _ensure_apify_stub()
    spec = importlib.util.spec_from_file_location("refinery_main", ROOT / "src" / "main.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


async def run_actor(input_data: dict, *, fetch_side_effect=None) -> list[dict]:
    """Run src/main.py with mocked Apify Actor."""
    main = load_main_module()
    pushed: list[dict] = []

    mock_actor = MagicMock()
    mock_actor.__aenter__ = AsyncMock(return_value=mock_actor)
    mock_actor.__aexit__ = AsyncMock(return_value=None)
    mock_actor.get_input = AsyncMock(return_value=input_data)
    mock_actor.push_data = AsyncMock(side_effect=lambda row: pushed.append(row))
    mock_actor.log = MagicMock()

    patches = [patch.object(main, "Actor", mock_actor)]
    if fetch_side_effect is not None:
        patches.append(patch.object(main, "fetch_url", AsyncMock(side_effect=fetch_side_effect)))

    for p in patches:
        p.start()
    try:
        await main.main()
    finally:
        for p in reversed(patches):
            p.stop()
    return pushed


class RefineryCoreTests(unittest.TestCase):
    def test_extracts_body_text(self):
        import refinery_core

        raw = refinery_core.refinery_json(
            "<html><head><script>x()</script></head>"
            "<body><nav>Home</nav><article><h1>QA</h1><p>Smoke test.</p></article></body></html>"
        )
        result = json.loads(raw) if isinstance(raw, str) else raw
        self.assertTrue(result["success"])
        self.assertIn("Smoke test", result["text"])
        self.assertGreaterEqual(result["word_count"], 2)


class SchemaTests(unittest.TestCase):
    def test_input_schema_valid(self):
        schema = json.loads((ROOT / "INPUT_SCHEMA.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["schemaVersion"], 1)
        urls = schema["properties"]["urls"]
        self.assertEqual(urls["editor"], "stringList")
        self.assertIn("prefill", urls)
        self.assertIn("prefill", schema["properties"]["raw_payload"])

    def test_actor_json_example_input_valid(self):
        actor = json.loads((ROOT / ".actor" / "actor.json").read_text(encoding="utf-8"))
        body = json.loads(actor["exampleRunInput"]["body"])
        self.assertIsInstance(body.get("urls"), list)
        self.assertTrue(body["urls"], "exampleRunInput should include a working demo URL")

    def test_apify_prefill_simulation(self):
        """Apify QA may use schema prefills — empty or example.com URL should not crash."""
        schema = json.loads((ROOT / "INPUT_SCHEMA.json").read_text(encoding="utf-8"))
        simulated = {
            "urls": schema["properties"]["urls"].get("prefill", []),
            "raw_payload": schema["properties"]["raw_payload"].get("prefill", ""),
            "removeScripts": schema["properties"]["removeScripts"].get("default", True),
            "removeStyles": schema["properties"]["removeStyles"].get("default", True),
            "includeMetadata": schema["properties"]["includeMetadata"].get("default", True),
        }
        has_html = bool(simulated["urls"]) or bool(str(simulated["raw_payload"]).strip())
        self.assertTrue(has_html, "Try actor prefill should include example.com or paste demo")


class ActorInputTests(unittest.IsolatedAsyncioTestCase):
    async def test_empty_object_does_not_raise(self):
        rows = await run_actor({})
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["success"])
        self.assertIn("No HTML provided", rows[0]["error"])

    async def test_schema_prefill_input_graceful(self):
        rows = await run_actor({
            "urls": [],
            "raw_payload": "",
            "removeScripts": True,
            "removeStyles": True,
            "includeMetadata": True,
        })
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["success"])
        self.assertEqual(rows[0]["word_count"], 0)

    async def test_failed_url_fetch_graceful(self):
        async def boom(_url):
            raise httpx.HTTPStatusError("403", request=MagicMock(), response=MagicMock(status_code=403))

        rows = await run_actor(
            {"urls": ["https://blocked.example/"], "raw_payload": ""},
            fetch_side_effect=boom,
        )
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["success"])
        self.assertIn("URL fetches failed", rows[0]["error"])

    async def test_paste_mode_extracts(self):
        html = (
            "<html><body><article><h1>Local</h1><p>Unit test.</p></article></body></html>"
        )
        rows = await run_actor({"raw_payload": html, "urls": []})
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["success"])
        self.assertIn("Unit test", rows[0]["text"])

    async def test_oversized_payload_graceful(self):
        rows = await run_actor({"raw_payload": "x" * (10 * 1024 * 1024 + 1), "urls": []})
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["success"])
        self.assertIn("too large", rows[0]["error"])

    async def test_urls_win_over_paste(self):
        html = "<html><body><p>paste</p></body></html>"

        async def fake_fetch(url):
            self.assertEqual(url, "https://example.com")
            return "<html><body><p>fetched</p></body></html>"

        rows = await run_actor(
            {"urls": ["https://example.com"], "raw_payload": html},
            fetch_side_effect=fake_fetch,
        )
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["success"])
        self.assertIn("fetched", rows[0]["text"])


def main() -> int:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(RefineryCoreTests))
    suite.addTests(loader.loadTestsFromTestCase(SchemaTests))
    suite.addTests(loader.loadTestsFromTestCase(ActorInputTests))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
