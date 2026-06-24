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
