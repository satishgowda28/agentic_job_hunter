# Phase 6 — Google Sheets Logger

## Status
Not started. Branch: `phase6_sheets_logger`

---

## What to Build

`agents/logger.py` — writes every job to Google Sheets regardless of outcome.

---

## Google Sheets Schema

| Column | Example |
|---|---|
| Date | 2026-05-11 |
| Company | Razorpay |
| Role | Senior Frontend Engineer |
| Score | 87% |
| Matched Skills | React, Next.js, TypeScript |
| Gaps | Go experience preferred |
| JD URL | https://... |
| Screenshot | /output/screenshots/razorpay_110526.png |
| Tailored Resume | /output/tailored/razorpay_110526.tex |
| Status | Shortlisted |
| Filter Reason | null |
| Applied | No |
| Notes | |

---

## Inputs

Function receives different data depending on pipeline stage:

| Scenario | Available data |
|---|---|
| Shortlisted | `ScrapedJD` + `ScoringResult` + resume path |
| Review Manually | `ScrapedJD` + `ScoringResult` |
| Skipped | `ScrapedJD` + `ScoringResult` |
| Filtered (LinkedIn/portal pre-filter) | `JobInfo` only — no scrape, no score |
| Blacklisted | `JobInfo` only |

---

## Key Rules

- **Dedup:** never create duplicate company+role rows — update existing entry
- **Log everything:** filtered, skipped, blacklisted — all rows, no exceptions
- **Applied column:** always defaults to "No" — human updates manually

---

## Auth

- Google Sheets API, OAuth2 (same credential pattern as Gmail)
- Scope: `https://www.googleapis.com/auth/spreadsheets`
- Spreadsheet ID in `.env`

---

## Next Step

1. Set up Google Sheets API credentials (OAuth2)
2. Write `agents/logger.py` with `log_job()` function
3. Handle dedup — check existing rows before append
