# Refinery production QA — 2026-06-28

## Summary

| Check | Result |
|-------|--------|
| Empty input `{}` (Apify QA simulation) | **PASS** — SUCCEEDED, `success: false`, graceful error |
| URL mode `https://example.com` | **PASS** — word_count 18 |
| Paste minimal smoke | **PASS** |
| Paste Lipstick Wayback (~25KB) | **PASS** — word_count 208 |
| Live `lipstickalley.com` URL | **PASS** — SUCCEEDED, graceful `success: false` (Cloudflare block) |
| Oversized payload (>10MB) | **PASS** — graceful error, no crash |
| Local unit tests (`scripts/test_local.py`) | **PASS** — 10/10 |
| Import validation | **PASS** |
| Docker deploy | **PASS** — build **1.1.18** |
| Store notice | **PASS** — `NONE` |
| Try-actor prefill | **PASS** — `example.com` URL prefill synced |

## Run full suite

```bash
cd /root/ACTIVE_PROJECTS/refinery/refinery-rust
bash scripts/run_all_tests.sh
```

Production-only:

```bash
python3 scripts/qa_production.py
```

Latest results: `QA_PRODUCTION_LATEST.json`

## Console (Try actor)

1. **Paste mode** prefilled with Wayback Lipstick HTML — run as-is for heavy-HTML demo.
2. **URL mode:** use `https://example.com` (not live lipstickalley.com — Cloudflare blocks Apify).
3. **Restore example input** at bottom of form if textarea looks empty after sync.

## Sync Console without rebuild

```bash
python3 scripts/sync_console_source.py
python3 scripts/sync_store_readme.py
```

## Deploy

```bash
bash scripts/deploy_actor.sh
```

See `APIFY_DEPLOY.md` for org account checks and cleanup inventory.

Post-mortem: `/root/TOOLS/postmortems/2026-06-20-refinery-apify-qa-empty-input-fix.md`
