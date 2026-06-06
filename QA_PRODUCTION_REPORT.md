# Refinery production QA — 2026-05-25

## Summary

| Check | Result |
|-------|--------|
| URL mode `https://example.com` | **PASS** — clean text, word_count 18 |
| Paste minimal smoke | **PASS** |
| Paste Lipstick Wayback (~25KB) | **PASS** — word_count 208, text_len 1214 |
| Live `lipstickalley.com` URL | **Expected** — 403 / run fails until graceful-error deploy lands |
| Console schema + example input synced | **PASS** — API sync |
| Store README synced | **PASS** |
| Docker `apify push` | **Blocked** — builds `1.1.60`–`1.1.64` fail instantly (Apify “unexpected system error”). **Live runs use `1.1.59`.** |

## Console (Try actor) — what you should see

1. **URL mode:** prefilled `https://example.com` only (not lipstickalley.com).
2. **Paste mode:** prefilled Wayback Lipstick Alley HTML (~25KB). If textarea looks empty, use **Restore example input** at bottom of form.
3. **Do not** run live `https://www.lipstickalley.com/` in URL mode — Cloudflare blocks Apify.

## Production runs (API)

Latest automated suite: `QA_PRODUCTION_LATEST.json`

Re-run:

```bash
python3 scripts/qa_production.py
```

## Sync production Console without rebuild

```bash
python3 scripts/sync_console_source.py   # INPUT_SCHEMA + exampleRunInput
python3 scripts/sync_store_readme.py
```

Hard-refresh Console after sync.

## Pending deploy (`main.py`)

- URLs win when both url + paste set
- URL fetch all-fail → dataset row with `success: false` + error message (no crash)

```bash
apify actors push --force
```

Until that build is green, blocked URLs show **Failed** run instead of a friendly dataset error.
