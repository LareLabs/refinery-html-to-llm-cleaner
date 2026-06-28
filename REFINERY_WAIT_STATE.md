# Refinery — wait state (post-readiness, Jun 2026)

**Status:** Engineering complete. Monetization starts **2026-07-01**. No further deploy work unless something breaks or a sale triggers follow-up.

## Canonical URLs

| Asset | URL |
|-------|-----|
| Apify Store | https://apify.com/larelabs/refinery-html-to-llm-cleaner |
| Apify Console | https://console.apify.com/organization/vTZ0XDFG4cZCNAdQl/actors/E5JQI6n1Xle0Mn0G6 |
| Actor ID | `E5JQI6n1Xle0Mn0G6` |
| MCP landing | https://larelabs.github.io/refinery-mcp/ |
| npm | `@larelabs/refinery-mcp@0.1.6` |
| MCP Registry | `io.github.LareLabs/refinery-mcp` |
| GitHub (actor) | https://github.com/LareLabs/refinery-html-to-llm-cleaner |
| GitHub (MCP) | https://github.com/LareLabs/refinery-mcp |

## What is live

- Build **1.1.19** — graceful errors, `Actor.charge('html-extraction')`, bulk URL rows
- Publication — categories (AI, Developer tools, Agents), custom SEO, published
- **Limited permissions** — required for agentic discovery
- PPE **$0.002/page** (`html-extraction`) — scheduled **2026-07-01T01:32:39Z**
- `maxTotalChargeUsd` **$5** (was $0.01 — would have blocked bulk customers)
- Saved task `refinery-clean-example-url` (not published to Examples tab — Console only)
- MCP + npm + official registry published
- mcp.so issue: https://github.com/chatmcp/mcpso/issues/2933
- QA: `bash scripts/run_all_tests.sh` — 10/10 local + 5/5 production

## Calendar

| Date | Event | Action |
|------|-------|--------|
| **2026-07-01** | PPE goes live | Agent or Cameron: verify charging + `allowsAgenticUsers` (see below) |
| **2026-07-13** | Old actor FREE pricing | Unpublish `refinery-html-to-llm-cleaner-archived-00307` in Console |

## July 1 verification (copy-paste)

```bash
cd /root/ACTIVE_PROJECTS/refinery/refinery-rust
bash scripts/run_all_tests.sh

python3 << 'PY'
import json, urllib.request
from pathlib import Path
t = json.loads(Path("/root/.apify/auth.json").read_text())["token"]
h = {"Authorization": f"Bearer {t}"}
store = json.loads(urllib.request.urlopen(
    urllib.request.Request("https://api.apify.com/v2/store?search=larelabs/refinery-html-to-llm-cleaner", headers=h), timeout=30).read())
agentic = json.loads(urllib.request.urlopen(
    urllib.request.Request("https://api.apify.com/v2/store?search=larelabs/refinery-html-to-llm-cleaner&allowsAgenticUsers=true", headers=h), timeout=30).read())
for items in (store["data"]["items"], agentic["data"]["items"]):
    for a in items:
        if a.get("name") == "refinery-html-to-llm-cleaner":
            p = a.get("currentPricingInfo") or {}
            print("pricing:", p.get("pricingModel"), "| agentic:", a.get("allowsAgenticUsers"))
PY
```

Expect: `pricing: PAY_PER_EVENT`, agentic flag true after Jul 1.

## When the first sale / external user run happens

1. Check Apify Console → **Runs** — confirm external username (not `larelabs`)
2. Confirm run **SUCCEEDED** and dataset has `success: true`
3. Check **Monetization / Insights** for `html-extraction` charge
4. If user left a bad run: check logs, fix, redeploy via `bash scripts/deploy_actor.sh`
5. Optional: thank / support via Apify messaging if they contact you

## Optional boost (not blocking)

- **Publish saved task** → Console → [task](https://console.apify.com/organization/vTZ0XDFG4cZCNAdQl/actor-tasks/6179DcT8CK5oOmSnX) → Publication → Publish (Examples tab + SEO page; no API)
- **Glama** — submit repo with `glama.json` at https://glama.ai/mcp/servers
- **Outbound distribution** — integrations, dev posts (Store alone rarely floods pipeline utilities)

## Do not

- Deploy to `cameronlares` personal Apify account
- Use deprecated actor `jOcx8jK2FdhZhoKrE` / `archived-00307`
- Publish MCP under `io.github.cameronlares/*`
- Hunt for a "Tags" field in Console — use **Categories** + SEO + README only

## Ops commands

```bash
cd /root/ACTIVE_PROJECTS/refinery/refinery-rust
apify info                    # must show larelabs
bash scripts/sync_all_listing.sh
bash scripts/run_all_tests.sh
bash scripts/deploy_actor.sh  # only after code change
```

## Related docs

- `APIFY_DEPLOY.md` — deploy + monetization checklist
- `../refinery-mcp/NPM_DEPLOY.md` — MCP/npm/registry
- Post-mortem: `/root/TOOLS/postmortems/2026-06-28-refinery-apify-store-monetization-readiness.md`
