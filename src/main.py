"""
Refinery HTML to Text Cleaner - Apify Actor
Ultra-fast HTML text extraction for RAG and AI agents
"""

import asyncio
import json
import time
import httpx
from apify import Actor

CHARGE_EVENT = "html-extraction"


async def fetch_url(url: str) -> str:
    """Fetch HTML content from a URL"""
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def load_refinery_core():
    import sys
    from pathlib import Path

    core_dir = Path(__file__).resolve().parent.parent / "refinery_core_src"
    sys.path.insert(0, str(core_dir))
    import refinery_core

    return refinery_core


def extract_html(html: str, *, include_metadata: bool, extract_mentions: bool, extract_hashtags: bool) -> dict:
    refinery_core = load_refinery_core()
    start_time = time.time()
    result_json = refinery_core.refinery_json(html)

    if isinstance(result_json, dict):
        result = result_json
    else:
        result = json.loads(result_json)

    result["processing_time_ms"] = round((time.time() - start_time) * 1000, 2)
    result["success"] = True

    if not include_metadata:
        result = {
            "text": result.get("text", ""),
            "success": result.get("success", True),
        }

    if not extract_mentions:
        result.pop("mentions", None)

    if not extract_hashtags:
        result.pop("hashtags", None)

    return result


async def charge_page() -> bool:
    """Charge primary PPE event. Returns False if user spending limit reached."""
    try:
        charge_result = await Actor.charge(event_name=CHARGE_EVENT)
    except Exception as exc:
        Actor.log.warning(f"Charge skipped (local/dev): {exc}")
        return True

    if getattr(charge_result, "event_charge_limit_reached", False):
        Actor.log.warning("User spending limit reached; stopping further charges")
        return False
    return True


async def push_row(row: dict) -> None:
    await Actor.push_data(row)


async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}

        include_metadata = input_data.get("includeMetadata", True)
        remove_scripts = input_data.get("removeScripts", True)
        remove_styles = input_data.get("removeStyles", True)
        extract_mentions = input_data.get("extractMentions", False)
        extract_hashtags = input_data.get("extractHashtags", False)
        raw_payload = input_data.get("raw_payload", "")
        urls = input_data.get("urls", [])

        _ = remove_scripts, remove_styles  # handled in Rust core defaults

        if urls:
            Actor.log.info(f"Processing {len(urls)} URLs")
            for url in urls:
                try:
                    html = await fetch_url(url)
                    Actor.log.info(f"Fetched {url} ({len(html)} bytes)")
                except Exception as exc:
                    msg = f"Failed to fetch {url}: {exc}"
                    Actor.log.error(msg)
                    await push_row(
                        {
                            "success": False,
                            "error": msg,
                            "url": url,
                            "text": "",
                            "word_count": 0,
                            "content_type": "web",
                        }
                    )
                    continue

                if len(html) > 10 * 1024 * 1024:
                    await push_row(
                        {
                            "success": False,
                            "error": "Payload too large (max 10MB)",
                            "url": url,
                            "text": "",
                            "word_count": 0,
                            "content_type": "web",
                        }
                    )
                    continue

                try:
                    result = extract_html(
                        html,
                        include_metadata=include_metadata,
                        extract_mentions=extract_mentions,
                        extract_hashtags=extract_hashtags,
                    )
                    result["url"] = url
                except Exception as exc:
                    await push_row(
                        {
                            "success": False,
                            "error": f"Extraction failed: {exc}",
                            "url": url,
                            "text": "",
                            "word_count": 0,
                            "content_type": "web",
                        }
                    )
                    continue

                if not await charge_page():
                    return

                await push_row(result)
            return

        html = raw_payload
        if not html or not str(html).strip():
            msg = (
                "No HTML provided in input. "
                "Set either raw_payload or urls (for example https://example.com)."
            )
            Actor.log.warning(msg)
            await push_row(
                {
                    "success": False,
                    "error": msg,
                    "text": "",
                    "word_count": 0,
                    "content_type": "web",
                }
            )
            return

        if len(html) > 10 * 1024 * 1024:
            msg = "Payload too large (max 10MB)"
            Actor.log.warning(msg)
            await push_row(
                {
                    "success": False,
                    "error": msg,
                    "text": "",
                    "word_count": 0,
                    "content_type": "web",
                }
            )
            return

        Actor.log.info(f"Processing HTML payload ({len(html)} bytes)")

        try:
            result = extract_html(
                html,
                include_metadata=include_metadata,
                extract_mentions=extract_mentions,
                extract_hashtags=extract_hashtags,
            )
        except Exception as exc:
            msg = f"Extraction failed: {exc}"
            Actor.log.error(msg)
            await push_row(
                {
                    "success": False,
                    "error": msg,
                    "text": "",
                    "word_count": 0,
                    "content_type": "web",
                }
            )
            return

        if not await charge_page():
            return

        await push_row(result)
        Actor.log.info("Output pushed successfully")


if __name__ == "__main__":
    asyncio.run(main())
