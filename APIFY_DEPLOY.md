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

Per [Apify publish docs](https://docs.apify.com/platform/actors/publishing/publish) and [monetize docs](https://docs.apify.com/platform/actors/publishing/monetize):

- **Store listing metadata** = **Publication → Display information** (icon, name, description, **Categories**, custom SEO). There is **no separate “Tags” field** on the Publication page.
- **Categories** are the store taxonomy (`AI`, `DEVELOPER_TOOLS`, `AGENTS`, etc.) — syncable via API (`categories` on `PUT /v2/acts/{id}`).
- **Search keywords** (rag, html-cleaner, …) come from **description**, **seoTitle**, **seoDescription**, and **README** — not a tags picker.
- **Major monetization changes** (new PPE events, price increases, model changes) require a **14-day notice** per Apify policy — cannot be activated immediately via API or Console.
- **Agentic payments** (`allowsAgenticUsers=true`) are **automatic** when: pay-per-event is **live**, limited permissions, no Standby. No separate opt-in. See [monetize → agentic payments](https://docs.apify.com/platform/actors/publishing/monetize).
- **Quality score** = **Console → Insights → Actor quality** (no public API).

Run after listing changes:

```bash
bash scripts/sync_all_listing.sh
bash scripts/run_all_tests.sh
```

| Signal | Status | Action if missing |
|--------|--------|-------------------|
| Store SEO (#1 on target queries) | ✅ | Re-run `sync_all_listing.sh` after README edits |
| `seoTitle` / `seoDescription` | ✅ | `sync_actor_metadata.py` |
| **Categories** (AI, Developer tools, Agents) | ✅ | `sync_actor_metadata.py` or Publication → Display information |
| README images (Imgur → apifyusercontent) | ✅ | `embed_store_readme.py` + `sync_store_readme.py` |
| Try-actor `exampleRunInput` | ✅ | Must be real demo JSON — **not** placeholder `helloWorld` |
| INPUT + OUTPUT schema on version | ✅ | `sync_console_source.py` |
| Pay-per-event pricing ($0.002/page) | 🟡 scheduled Jul 1 | **14-day notice required** when PPE was first added. Goes live on schedule; `Actor.charge()` logs “does not use pay-per-event” until then. |
| `Actor.charge('html-extraction')` in code | ✅ build 1.1.19+ | Required for custom PPE events; deployed |
| Automated QA (empty input) | ✅ | Graceful `success: false`, run SUCCEEDS |
| MCP Registry (`io.github.LareLabs/refinery-mcp`) | ✅ | npm + `mcp-publisher-official publish` |
| 30d success rate ≥95% | 🟡 ~58% | Old failures roll off; new runs all pass |
| **Limited permissions** | ✅ | `actorPermissionLevel: LIMITED_PERMISSIONS` (Publication → Actor permissions) |
| **Agentic discovery** | ⬜ after Jul 1 | Store still shows `FREE` until PPE starts; then `allowsAgenticUsers` should flip automatically |
| Reviews / bookmarks | ⬜ 0 | Grows with real users |
| Store Task (one-click demo) | ✅ | `refinery-clean-example-url` → https://console.apify.com/organization/vTZ0XDFG4cZCNAdQl/actor-tasks/6179DcT8CK5oOmSnX |
| Glama (`glama.json`) | 🟡 | In repo; submit at https://glama.ai/mcp/servers |
| mcp.so directory | 🟡 | Issue https://github.com/chatmcp/mcpso/issues/2933 |

**Revenue paths:** Apify Store PPE runs ($0.002/page from Jul 1) · MCP → npm → Apify credits · agent discovery via MCP Registry + Apify MCP `search-actors` (quality score affects ranking).

### What API/CLI can vs cannot do

| Via `PUT /v2/acts/{id}` + scripts | Console-only |
|-----------------------------------|--------------|
| `title`, `description`, `seoTitle`, `seoDescription` | Initial PPE wizard (first setup) |
| `categories` | Major pricing changes (14-day notice UI) |
| `exampleRunInput`, README, INPUT/OUTPUT schema | Quality score dashboard |
| `pricingInfos` append (14+ days out for major changes) | Payout approval |
| Deploy, QA, tasks, runs | — |

**Not a store field:** `tags` in `.actor/actor.json` is local metadata only — Apify API has no store `tags` field (only `categories` and build `taggedBuilds` like `latest`).

### Post–Jul 1 verification (agent or you)

After PPE goes live (`2026-07-01T01:32:39Z`), confirm:

```bash
cd /root/ACTIVE_PROJECTS/refinery/refinery-rust
bash scripts/run_all_tests.sh
python3 -c "
import json, urllib.request
from pathlib import Path
t = json.loads(Path('/root/.apify/auth.json').read_text())['token']
req = urllib.request.Request(
  'https://api.apify.com/v2/store?search=refinery-html-to-llm-cleaner&allowsAgenticUsers=true',
  headers={'Authorization': f'Bearer {t}'})
n = len(json.loads(urllib.request.urlopen(req, timeout=30).read())['data']['items'])
print('agentic-eligible:', n > 0)
"
```

Expect: store `currentPricingInfo` = `PAY_PER_EVENT`, agentic search returns the actor, run logs show successful `html-extraction` charges.

### Optional Console boost (Examples tab + SEO)

Publish the saved task so it appears on the Actor **Examples** tab ([publish-task docs](https://docs.apify.com/platform/actors/publishing/publish-task)):

1. Open [refinery-clean-example-url task](https://console.apify.com/organization/vTZ0XDFG4cZCNAdQl/actor-tasks/6179DcT8CK5oOmSnX)
2. **Publication** tab → complete Display information → **Publish task**

Creates a public example page and helps Store/AI discovery. No API endpoint for this.

### Runtime defaults (API-synced)

- `maxTotalChargeUsd` raised from **$0.01 → $5** (was blocking bulk URL runs for paying users)
- `defaultRunOptions`: build `latest`, 512 MB, 3600s timeout

### Realistic expectations (honest)

**Technically ready:** build 1.1.19, last 20 runs 20/20 pass, Publication complete, MCP/npm/registry live, limited permissions on.

**Why user count is still ~2:** almost all 112 runs are org self-QA; PPE was not charging; agentic discovery waits until Jul 1; niche SEO queries have low volume; Refinery is a **post-scrape pipeline** (users find Firecrawl/BS4 first, not HTML cleaners).

**Not a total failure** — it's an **unmonetized, undistributed utility** with solid infra. Jul 1 turns on revenue + agentic indexing. Meaningful user growth still needs **outbound distribution** (integrations, content, dev communities) — Store alone rarely floods pipeline tools with traffic.

**Jul 13:** deprecated actor (`archived-00307`) goes FREE → unpublish in Console to stop duplicate-store confusion.


- Post-mortems:
  - `/root/TOOLS/postmortems/2026-06-20-refinery-apify-qa-empty-input-fix.md` (QA empty-input fix)
  - `/root/TOOLS/postmortems/2026-06-16-refinery-apify-build-worker-migration.md` (worker migration)
