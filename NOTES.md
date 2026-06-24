# Project Notes

Append-only log of decisions, findings, and insights.

---

## 2026-06-24 — 17:46

**Topic:** Portal scanner — use ATS APIs, not Playwright

Most tech companies use one of three ATS platforms: Greenhouse, Ashby, or Lever. Each exposes a public JSON API that returns all job listings as structured JSON, without requiring Playwright, DOM selectors, or any scraping. The approach was observed in the career-ops project (`scan.mjs`). Detect which ATS a company uses by pattern-matching their careers page URL, then call the corresponding API directly.

API endpoints:
- Greenhouse: `https://boards-api.greenhouse.io/v1/boards/{slug}/jobs`
- Ashby: `https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true`
- Lever: `https://api.lever.co/v0/postings/{slug}`

Benefits over Playwright scraping: no bot detection, zero AI tokens for extraction, faster (pure HTTP), never breaks due to DOM changes. Fall back to Playwright only for companies on fully custom career sites that don't use one of these three ATSes.

---

## 2026-06-24 — 18:00

**Topic:** LiteLLM — provider-agnostic AI layer

Replace direct `anthropic` SDK calls with LiteLLM so the AI provider can be switched via `.env` without touching agent code. LiteLLM supports 100+ models with a unified `completion()` interface — change `LLM_MODEL=claude-sonnet-4-6` to `LLM_MODEL=gpt-4o` or `LLM_MODEL=ollama/llama3` and everything works. Planned implementation: a thin wrapper in `utils/ai.py` that reads `LLM_MODEL`, `HAIKU_MODEL` from `.env` and exposes `call_llm(messages, model="haiku"|"sonnet")` used by all agents. This keeps cost-control rules intact (Haiku for cheap tasks, Sonnet for scoring/tailoring) while making the underlying provider swappable.

**Status:** Pending improvement — not MVP blocking.

---

## 2026-06-24 — 18:03

**Topic:** Hosting — ngrok for local FastAPI

No external hosting needed. Run FastAPI locally and expose it via ngrok (`ngrok http 8000`) to get a public HTTPS URL instantly. Free tier works fine for personal use — URL changes on restart but that's acceptable when you're the only user. For a stable permanent URL, options are ngrok paid ($8/mo) or Cloudflare Tunnel (free, more setup). This approach keeps the full pipeline on the local machine with access to credentials, Playwright, and the filesystem — no secrets management or deployment complexity. Revisit hosting only if the tool needs to be shared or always-on without the dev machine running.

---

## 2026-06-24 — 17:56

**Topic:** Two new input methods — FastAPI trigger + email-to-pipeline

**Idea 1 — FastAPI endpoint**

Build a FastAPI service with a single `POST /scan` endpoint that accepts either a raw JD URL or pasted JD text. If a URL is provided, run `scrape_jd()` first; if text is provided, skip the scraper and pass directly to `score_job()`. From there the full pipeline runs as normal — scoring, tailoring if 80%+, logging to Sheets. Returns a JSON response with score, status, and resume path. This enables on-demand pipeline triggering from anywhere — browser, phone, Raycast, or a future Chrome extension — without waiting for the daily scheduled run.

**Idea 2 — Email-yourself trigger**

When browsing and spotting a job, email the URL to yourself (`satishgowda28@gmail.com`) with subject format `JD: <Company Name>`. Set up a Gmail filter: `from:me subject:JD:` → automatically apply label `jobs_agents`. The existing Gmail reader already polls that label, so the job gets picked up on the next scheduled run. Only missing piece is a new email parser in `emailParsers` that handles self-sent emails (sender = own address, body = raw URL). Zero-friction on mobile — no app needed, works in under 10 seconds.

---
