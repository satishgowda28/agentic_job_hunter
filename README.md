# Agentic Job Hunter

A multi-agent pipeline that reads your Gmail, scores job matches against your profile, tailors your resume for strong matches, and logs everything to Google Sheets. Run it once a day — wake up to a shortlist, not an inbox.

---

## What It Does

```
Gmail Inbox (job emails)
         ↓
   Parse & classify
         ↓
   Scrape JD (Playwright)
         ↓
   Score against profile (Sonnet)
         ↓
   Score ≥ 80%  →  Tailor resume → Log as Shortlisted
   Score 60-79% →  Log as Review Manually
   Score < 60%  →  Log as Skipped
         ↓
   Google Sheets (every job, no exceptions)
         ↓
   Daily summary email
```

---

## Stack

| Component | Tool |
|---|---|
| Language | Python 3.11+ |
| Scraping | Playwright |
| AI — scoring & tailoring | Claude Sonnet |
| AI — extraction & pre-filter | Claude Haiku |
| Gmail | Gmail API (OAuth2) |
| Logging | Google Sheets API |
| Config | `.env` + `config/profile.md` |

---

## Project Structure

```
agentic-job-hunter/
├── agents/
│   ├── gmail_reader.py       # Read inbox, classify, extract jobs
│   ├── jd_scraper.py         # Scrape JD via Playwright
│   ├── match_scorer.py       # Score JD against profile (Sonnet)
│   ├── resume_tailor.py      # Tailor base resume per JD (Sonnet)
│   ├── logger.py             # Write to Google Sheets
│   ├── notifier.py           # Send daily summary email
│   └── site_scrapers/
│       ├── hirist.py         # hirist.tech scraper
│       └── linkedin.py       # LinkedIn public JD scraper
├── config/
│   ├── profile.md            # Your skills, preferences, dealbreakers
│   ├── portals.yml           # Company career page URLs (portal scanner)
│   └── blacklist.yml         # Known outsourcing companies — auto-reject
├── resumes/
│   └── base_resume.md        # Master resume — never edit directly
├── output/
│   ├── tailored/             # Tailored resumes (.tex) per job
│   └── screenshots/          # JD screenshots (fallback extraction)
├── orchestrator.py           # Entry point — runs full pipeline
└── .env                      # API keys — never commit
```

---

## Setup

### 1. Clone and create virtualenv

```bash
git clone <repo>
cd agentic-job-hunter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Environment variables

Create `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...
SPREADSHEET_ID=your_google_sheet_id
USER_AGENT=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...
```

### 3. Google OAuth (Gmail + Sheets)

- Create a Google Cloud project
- Enable Gmail API and Google Sheets API
- Download `credentials.json` → place in `_creds/`
- First run will open browser for OAuth consent → saves `token.pickle`

### 4. Configure your profile

Edit `config/profile.md` — this is what the scorer compares every JD against. Include:
- Skills and years of experience
- Preferred roles, cities, seniority
- Dealbreakers

### 5. Gmail label

Create a Gmail label `jobs_agents`. Apply it to all job emails you want the system to process.

---

## Run

```bash
source .venv/bin/activate
python orchestrator.py
```

Reads all emails tagged `jobs_agents` from today, runs the full pipeline, logs to Sheets, sends summary email.

---

## Scraper Strategy

1. Navigate to JD URL via Playwright
2. Wait for page to fully render (React/JS apps)
3. Extract fields from DOM
4. If DOM extraction fails or JD text too short → grayscale screenshot → Haiku vision extraction
5. If page load itself fails → log as `Scrape Failed`

---

## Google Sheets Schema

| Column | Example |
|---|---|
| Date | 2026-06-24 |
| Company | Adobe Systems |
| Role | Senior Frontend Engineer |
| Score | 87% |
| Matched Skills | React, Next.js, TypeScript |
| Gaps | Go preferred |
| JD URL | https://... |
| Screenshot | output/screenshots/adobe_240626.jpg |
| Tailored Resume | output/tailored/adobe_240626.tex |
| Status | Shortlisted |
| Applied | No |

### Job Statuses

| Status | Meaning |
|---|---|
| `Shortlisted` | Score ≥ 80% — tailored resume generated |
| `Review Manually` | Score 60–79% |
| `Skipped` | Score < 60% |
| `Filtered` | Rejected before scoring (city/role/seniority mismatch) |
| `Blacklisted` | Company in `config/blacklist.yml` |
| `Scrape Failed` | Could not extract JD |

---

## Hard Rules

- Never modify `resumes/base_resume.md` — tailoring goes to `output/tailored/` only
- Never fabricate experience in tailored resumes — only reframe what exists
- Never auto-apply — system shortlists, human decides
- Never commit `.env` or OAuth credentials

---

## Build Status

- [x] Phase 1 — Project structure
- [x] Phase 2 — Gmail reader
- [x] Phase 3 — JD Scraper (hirist + LinkedIn)
- [x] Phase 4 — Match Scorer
- [x] Phase 5 — Resume Tailor
- [x] Phase 6 — Google Sheets Logger
- [x] Phase 7 — Orchestrator + Notifier
- [ ] Phase 3.5 — Portal Scanner (next)
