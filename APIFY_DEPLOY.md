# Apify deploy — Lare Labs org only

**Do not deploy to Cameron's personal Apify account.** Wrong account = duplicate actors, failed builds, hours of debugging.

## Verify before every `apify push`

```bash
apify info
```

| Must see | Must NOT see |
|----------|----------------|
| `larelabs` | `cameronlares` |
| `vTZ0XDFG4cZCNAdQl` | `v83urlldkZpIfuYFp` |

- **Lare Labs org:** `larelabs` / `vTZ0XDFG4cZCNAdQl`
- **Personal (wrong):** `cameronlares` / `v83urlldkZpIfuYFp`

If wrong:

```bash
apify logout
apify login --token "$APIFY_LARELABS_TOKEN"   # org token from secure store, not personal
apify info   # confirm again
```

## Canonical actor (only one)

| Field | Value |
|-------|--------|
| Store URL | https://apify.com/larelabs/refinery-html-to-llm-cleaner |
| Actor ID | `E5JQI6n1Xle0Mn0G6` |
| Console | https://console.apify.com/organization/vTZ0XDFG4cZCNAdQl/actors/E5JQI6n1Xle0Mn0G6 |
| Archived (broken worker) | `jOcx8jK2FdhZhoKrE` → renamed `refinery-html-to-llm-cleaner-archived-00307` |
| Namespace | `larelabs/` (not `cameronlares/`) |

## Deploy from this directory only

```bash
cd /root/ACTIVE_PROJECTS/refinery/refinery-rust
bash scripts/deploy_actor.sh
```

**Why not `apify push` from repo root or GitHub auto-build?** Apify’s git-clone path for this repo still hits a broken build cache on some workers. `deploy_actor.sh` stages a lean zip (runtime files only) and pushes reliably to worker `00310`.

GitHub webhook is **disabled** — use `deploy_actor.sh` after merging to `main`.

## Console input / README without Docker rebuild

When `apify push` fails on Apify’s image build but you only changed `INPUT_SCHEMA.json` or `README.md`:

```bash
python3 scripts/sync_console_source.py   # INPUT_SCHEMA + Restore example input
python3 scripts/sync_store_readme.py
python3 scripts/qa_production.py         # live API QA
```

Hard-refresh Console → **Try actor** or **Information** tab.

Source of truth: this repo path. Not `ARCHIVE/`, not personal Apify, not a second actor name.

## Version tags (avoid “three latest” in Console)

In `.actor/actor.json` keep **one** line only:

```json
"version": "1.1",
"buildTag": "latest"
```

Do **not** create `1.2` unless you mean to. After a mistaken `1.2` push, clear its tag in Console or API:

- `1.1` → `buildTag: latest` (and point global `latest` at the last green **1.1.x** build)
- `1.0` / `1.2` → `buildTag: null`

**Current (fixed):** global `latest` = build **1.1.17+** on actor `E5JQI6n1Xle0Mn0G6`; deploy via `scripts/deploy_actor.sh`. Store notice `UNDER_MAINTENANCE` cleared after empty-input fix (2026-06-20).

## Cleanup inventory (2026-06-20)

| Actor | ID | Action |
|-------|-----|--------|
| **Canonical (keep)** | `E5JQI6n1Xle0Mn0G6` | Store listing, `latest` = 1.1.17 |
| Duplicate test actor | `bFE97i9cy2KEvzccK` | **Deleted** (private, all builds failed) |
| Old worker archive | `jOcx8jK2FdhZhoKrE` | Deprecated; remove monetization in Console before delete/unpublish (Apify API 403 otherwise) |

Run tests before deploy: `bash scripts/run_all_tests.sh`

## Store README (Console + public listing)

Git **Build** updates the Docker image but **does not always refresh** the README shown under **Information → latest → readme**. That tab uses **version `sourceFiles`**, which can stay on an old tarball.

After editing `README.md` (or running `scripts/embed_store_readme.py`):

```bash
cd /root/ACTIVE_PROJECTS/refinery/refinery-rust
python3 scripts/sync_store_readme.py   # PUT README to version 1.1
```

Then hard-refresh the Console README page. Optional: **Build** version **1.1** from Git so `latest` matches.

**Store title / short description** (card on apify.com) come from the **actor** record, not README alone:

```bash
# Or update in Console → Publication → Store listing
apify info   # must be larelabs
```

## Store README images

- Apify Store **does not render** `raw.githubusercontent.com`, **jsDelivr**, or large **base64 data URIs** in the HTML listing (broken icons / raw base64 text).
- Working actors use **Imgur** (`i.imgur.com`) or **Apify’s image proxy** (`images.apifyusercontent.com`).
- Workflow: keep source WebPs in `assets/store/`, upload PNGs to Imgur, save links in `assets/store/image_urls.json`, then:

```bash
python3 scripts/embed_store_readme.py
python3 scripts/sync_store_readme.py
```

- Shields.io badges are fine. Keep README text-only aside from Imgur screenshots (~5–10KB total).
- **Do not** use `*.md` in `.apifyignore` — it can exclude `README.md` and leave the Console stuck on an old Store README.

## GitHub

Repo: `https://github.com/LareLabs/refinery-html-to-llm-cleaner` (`main`).

- **Deploy code:** `bash scripts/deploy_actor.sh` (not git webhook — auto-build disabled; git-clone path still fails on Apify).
- **Sync metadata only:** `python3 scripts/sync_actor_metadata.py` (title, seoTitle, seoDescription, categories)
- **README / Console only:** `sync_store_readme.py`, `sync_console_source.py`.
- Post-mortems:
  - `/root/TOOLS/postmortems/2026-06-20-refinery-apify-qa-empty-input-fix.md` (QA empty-input fix)
  - `/root/TOOLS/postmortems/2026-06-16-refinery-apify-build-worker-migration.md` (worker migration)
