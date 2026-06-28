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
- **Sync listing (no rebuild):** `bash scripts/sync_all_listing.sh` — README, INPUT/OUTPUT schema, exampleRunInput, SEO fields.
- **Sync metadata only:** `python3 scripts/sync_actor_metadata.py` (title, seoTitle, seoDescription, categories, exampleRunInput)
- **README / Console only:** `sync_store_readme.py`, `sync_console_source.py`.

## Monetization & quality score checklist

Quality score is Console-only (no public API). Run after listing changes:

```bash
bash scripts/sync_all_listing.sh
bash scripts/run_all_tests.sh
```

| Signal | Status | Action if missing |
|--------|--------|-------------------|
| Store SEO (#1 on target queries) | ✅ | Re-run `sync_all_listing.sh` after README edits |
| `seoTitle` / `seoDescription` | ✅ | `sync_actor_metadata.py` |
| README images (Imgur → apifyusercontent) | ✅ | `embed_store_readme.py` + `sync_store_readme.py` |
| Try-actor `exampleRunInput` | ✅ | Must be real demo JSON — **not** placeholder `helloWorld` |
| INPUT + OUTPUT schema on version | ✅ | `sync_console_source.py` |
| Pay-per-event pricing ($0.002/page) | 🟡 scheduled | Console → Publication → Monetization — **must be active** (not just configured). Log: `Ignored attempt to charge... does not use pay-per-event` = PPE not live yet. |
| `Actor.charge('html-extraction')` in code | ✅ build 1.1.19+ | Required for custom PPE events; deployed |
| Automated QA (empty input) | ✅ | Graceful `success: false`, run SUCCEEDS |
| MCP Registry (`io.github.LareLabs/refinery-mcp`) | ✅ | npm + `mcp-publisher-official publish` |
| 30d success rate ≥95% | 🟡 ~58% | Old failures roll off; new runs all pass |
| Store tags | ⬜ Console only | Publication → Store listing → Tags (API rejects `tags`) |
| Limited permissions | ⬜ Console only | Settings → enable least-privilege if offered |
| Reviews / bookmarks | ⬜ 0 | Grows with real users |
| Store Task (one-click demo) | ✅ | `refinery-clean-example-url` → https://console.apify.com/organization/vTZ0XDFG4cZCNAdQl/actor-tasks/6179DcT8CK5oOmSnX |
| Agentic discovery (`allowsAgenticUsers`) | ⬜ | Requires PPE active + limited permissions — not in agentic store index yet |
| Glama (`glama.json`) | 🟡 | Added to repo; submit at https://glama.ai/mcp/servers |
| mcp.so directory | ⬜ | API submit rejected (`invalid type`); use GitHub issue on chatmcp/mcpso |

**Revenue paths:** Apify Store runs ($0.002/page) · MCP → npm → Apify credits · agent discovery via MCP Registry + Apify MCP `search-actors`.

### Console-only (you, ~5 min)

1. **Publication → Monetization** — activate PPE now (not July 1 schedule). Event: `html-extraction` @ $0.002.
2. **Publication → Store listing → Tags** — `rag`, `html-cleaner`, `beautifulsoup-alternative`, `llm`, `firecrawl`
3. **Settings → Permissions** — enable limited permissions (unlocks agentic store discovery)
4. **Old actor cleanup** (`jOcx8jK2FdhZhoKrE`) — remove monetization in Console, then unpublish/delete (API blocks while PPE active; FREE pricing needs 2-week `startedAt`)

- Post-mortems:
  - `/root/TOOLS/postmortems/2026-06-20-refinery-apify-qa-empty-input-fix.md` (QA empty-input fix)
  - `/root/TOOLS/postmortems/2026-06-16-refinery-apify-build-worker-migration.md` (worker migration)
