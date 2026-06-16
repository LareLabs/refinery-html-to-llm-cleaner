# Refinery — HTML to LLM text cleaner for RAG pipelines

**Apify Actor that cleans bloated HTML before chunking and embedding** — strip scripts, nav, ads, and layout junk from pages you already fetched.  
Pay **$0.002/page** · **~2–8ms** per page (Rust core, after your crawler runs).

[![Price](https://img.shields.io/badge/price-%240.002%2Fpage-blue)](https://apify.com/larelabs/refinery-html-to-llm-cleaner/pricing)
[![Speed](https://img.shields.io/badge/speed-2--8ms%2Fpage-brightgreen)]()

![Refinery pipeline: raw HTML to clean JSON for RAG](https://i.imgur.com/rKLRTc1.png)

---

## Reduce LLM token cost — HTML cleaner for RAG

![Token reduction: bloated HTML vs clean text after Refinery](https://i.imgur.com/RxmHFBz.png)

News-style homepages and heavy DOM pages often waste tokens on chrome. Refinery returns **main-body text** plus `word_count` so you can budget embeddings — **up to ~97% fewer estimated tokens** on bloated HTML (your mileage varies).

---

## Clean social feed HTML for chunking and embeddings

Scraped timelines and comment threads ship messy DOM — scripts, sidebars, widgets. Refinery keeps **post body text** and normalizes **@mentions** / **#hashtags** for RAG chunking without paying for layout noise.

![Social and feed HTML: mentions and hashtags preserved as clean text](https://i.imgur.com/C6fISu7.png)

Paste `raw_payload` from your scraper, or pass URLs if you already fetch HTML elsewhere.

---

## Apify Console output — clean text and word count

Run **Try actor** with the prefilled `example.com` URL — each dataset row includes `text`, `word_count`, and timing:

![Apify dataset output: clean text, word count, and timing](https://i.imgur.com/tZytWi2.png)

---

## Bulk HTML cleaning for crawl batches

Send **many URLs in one run** — each row gets `text`, `word_count`, and `processing_time_ms`. Ideal after a sitemap pass, Firecrawl export, or Apify crawler dataset.

![Bulk URL mode: many pages in, dataset rows out](https://i.imgur.com/GPYU1hT.png)

```json
{
  "urls": [
    "https://example.com",
    "https://www.bbc.com/news",
    "https://httpbin.org/html"
  ],
  "removeScripts": true,
  "removeStyles": true,
  "includeMetadata": true
}
```

---

## Who uses this HTML text extractor

- **RAG and agent builders** cutting OpenAI / Anthropic token spend on page HTML  
- **Scrape pipelines** that already fetch HTML (Firecrawl, Crawl4AI, Playwright, Apify Web Scraper)  
- **Teams** replacing per-worker BeautifulSoup with a fast **HTML parser API** on Apify  

**Refinery is not a web crawler.** It is an HTML-to-text preprocessing step after fetch.

```
Your crawler → raw HTML → Refinery → clean text → chunk → embed → vector DB → LLM
```

---

## Try the HTML to LLM cleaner (3 demos)

**Demo 1** is prefilled in Console. Paste **Demo 2** or **Demo 3** to see different modes.

### Demo 1 — Quick URL

```json
{
  "urls": ["https://example.com"],
  "removeScripts": true,
  "removeStyles": true,
  "includeMetadata": true
}
```

### Demo 1b — Heavy forum HTML (Console prefill)

**Try actor** opens with a **Wayback snapshot** of [lipstickalley.com](https://www.lipstickalley.com/) (~120KB XenForo HTML). Live URL fetch is blocked by Cloudflare — paste mode shows Refinery on real forum bloat. Expect ~600KB archived page → ~28KB clean text when using the full snapshot in `assets/prefill-lipstickalley-wayback.html`.

### Demo 2 — Bloated news homepage

```json
{
  "urls": ["https://www.bbc.com/news"],
  "removeScripts": true,
  "removeStyles": true,
  "includeMetadata": true
}
```

### Demo 3 — Paste HTML (middleware)

```json
{
  "raw_payload": "<html><head><script>gtag('event')</script></head><body><nav>Home · Pricing</nav><article><h1>Update</h1><p>Clean before embedding.</p></article></body></html>",
  "removeScripts": true,
  "removeStyles": true,
  "includeMetadata": true
}
```

---

## Output — text, word_count, language, timing

```json
{
  "text": "Example Product Page\nEnterprise AI Infrastructure...",
  "language": "en",
  "word_count": 12,
  "content_type": "web",
  "processing_time_ms": 19.29,
  "success": true
}
```

| Field | Use it for |
|-------|------------|
| `text` | Chunking, embeddings, LLM context |
| `word_count` | Cost estimates |
| `processing_time_ms` | Latency monitoring |

---

## Firecrawl, Crawl4AI, and BeautifulSoup alternative

![Refinery in your stack: crawler, clean, vector DB, LLM](https://i.imgur.com/mBbhQwd.png)

| You already use… | Refinery's job |
|------------------|----------------|
| **Firecrawl**, **Crawl4AI** | Clean their HTML before chunking — fetch with them, **clean with Refinery** |
| **Apify Web Scraper**, Website Content Crawler | Clean the `html` field in your dataset |
| **BeautifulSoup** (self-hosted) | Same job, ~281× faster hot path in our benchmarks — pay per page on Apify instead of worker CPU |

---

## Pricing — HTML extraction on Apify

| Event | Cost |
|-------|------|
| HTML extraction | **$0.002** / page |
| ~1,000 pages | **~$2.05** |

---

## Integrate via Apify API (JavaScript and Python)

### JavaScript

```javascript
import { ApifyClient } from 'apify-client';
const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor('larelabs/refinery-html-to-llm-cleaner').call({
  urls: ['https://example.com'],
});
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items[0].text, items[0].word_count);
```

### Python

```python
from apify_client import ApifyClient
client = ApifyClient(os.environ["APIFY_TOKEN"])
run = client.actor("larelabs/refinery-html-to-llm-cleaner").call(
    run_input={"urls": ["https://example.com"]}
)
print(next(client.dataset(run["defaultDatasetId"]).iterate_items()))
```

---

## FAQ — HTML cleaning for LLM and RAG

### Is Refinery a replacement for Firecrawl or Crawl4AI?

No. **Fetch with Firecrawl or Crawl4AI, then clean with Refinery.** Refinery does not crawl URLs on its own schedule — it strips noise from HTML you already have (or fetches URLs you pass in this run).

### How do I reduce RAG token cost from bloated HTML?

Run Refinery on raw HTML **before** chunking and embedding. Use `word_count` in the output to estimate savings. Remove scripts, styles, nav, and footer chrome so embeddings only see article body text.

### Is this a BeautifulSoup alternative for HTML text extraction?

Yes — same preprocessing job (HTML → clean text), implemented in **Rust** for low latency. Use it when you want a managed Apify step instead of BeautifulSoup on every worker.

### Can I clean HTML after Apify Web Scraper or Website Content Crawler?

Yes. Pass each page's HTML via `raw_payload`, or pipe URLs from your crawl. Refinery returns plain text ready for chunking.

### Does Refinery handle JavaScript SPAs?

Only if you pass **rendered HTML** from a browser crawler (Playwright, Puppeteer, Firecrawl). Refinery cleans DOM; it does not execute JavaScript.

### Can Refinery scrape social feeds or X / Twitter?

No login or feed scraping. Pass saved timeline HTML via `raw_payload` — Refinery extracts post text and normalizes @mentions / #hashtags.

---

## Support — LareLabs

**LareLabs** · [Apify Store listing](https://apify.com/larelabs/refinery-html-to-llm-cleaner) · [Console](https://console.apify.com/organization/vTZ0XDFG4cZCNAdQl/actors/E5JQI6n1Xle0Mn0G6)

---

*Rust core · Apify Actor · Update WebPs in `assets/store/`, upload PNGs to Imgur, edit `image_urls.json`, then run embed + sync scripts.*
