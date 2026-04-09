# Agentic Job Hunter — CLAUDE.md

## What This Is

A multi-agent system that reads Gmail, scores job matches against my profile,
tailors my resume for matches above 80%, screenshots the JD, and logs everything
to Google Sheets. Runs on a schedule — I wake up to a shortlist, not an inbox.

---

## Stack

- **Language:** Python 3.11+
- **Agent framework:** LangGraph
- **AI:** Claude API — Haiku for cheap tasks, Sonnet for scoring and tailoring
- **Gmail:** Gmail API (OAuth2)
- **Scraping:** Playwright
- **Logging:** Google Sheets API
- **Config:** `.env` for secrets, `config/profile.md` for my profile
- **Storage:** Local filesystem for screenshots and tailored resumes

---

## Key Files

| File | Purpose |
|---|---|
| `orchestrator.py` | Entry point — runs all agents in sequence |
| `config/profile.md` | My skills, preferences, dealbreakers (used by scorer) |
| `resumes/base_resume.md` | Master resume — never modify this directly |
| `.env` | All API keys — never print, never commit |
| `agents/gmail_reader.py` | Reads inbox, classifies emails, extracts jobs |
| `agents/jd_scraper.py` | Scrapes JD from URL, takes screenshots |
| `agents/match_scorer.py` | Scores JD against profile using Sonnet |
| `agents/resume_tailor.py` | Tailors base resume per JD using Sonnet |
| `agents/logger.py` | Writes every job to Google Sheets |
| `agents/notifier.py` | Sends daily summary email |
| `agents/portal_scanner.py` | Scrapes company career pages for new listings |
| `config/portals.yml` | List of company career page URLs to scan |
| `config/blacklist.yml` | Known outsourcing/service companies to auto-reject |

---

## Folder Structure

```
agentic-job-hunter/
├── agents/
│   ├── gmail_reader.py
│   ├── jd_scraper.py
│   ├── match_scorer.py
│   ├── resume_tailor.py
│   ├── logger.py
│   ├── notifier.py
│   └── portal_scanner.py
├── orchestrator.py
├── config/
│   ├── profile.md
│   ├── portals.yml
│   └── blacklist.yml
├── resumes/
│   └── base_resume.md
├── output/
│   ├── tailored/
│   └── screenshots/
├── .env
├── requirements.txt
├── CLAUDE.md
└── README.md
```

---

## Orchestrator Logic

```
Input Source 1: Gmail Reader (inbox)
Input Source 2: Portal Scanner (career pages)
         ↓              ↓
    Both feed the same orchestrator pipeline

For each job:
    1. Classify email type
       ├── LinkedIn alert → parse multiple jobs from HTML → Haiku pre-filter → log
       └── Regular email → extract URL or body → JD Scraper

    2. JD Scraper
       ├── Check job is still active (Playwright verify)
       ├── Try DOM extraction first
       └── Fallback: grayscale screenshot → Haiku vision extract

    3. Match Scorer (Sonnet)
       └── Returns: score, matched_skills, gaps, reasoning

    4. Routing by score:
       ├── 80%+  → Resume Tailor → PDF → Screenshot → Log as Shortlisted
       ├── 60-79% → Log as Review Manually
       └── <60%  → Log as Skipped

    5. Logger → Google Sheets (every single job, no exceptions)

    6. Notifier → Daily summary email
```

---

## Email Types

### Regular Job Emails

- One job per email
- Has JD text in body OR a URL to scrape
- Full pipeline applies

### LinkedIn Alert Emails

- Sender: `jobalerts-noreply@linkedin.com`
- Multiple jobs per email (HTML structured blocks)
- LinkedIn URLs are blocked — do NOT attempt to scrape
- Parse email HTML with BeautifulSoup to extract: title, company, location, URL
- Run Haiku pre-filter only — no scraping, no scoring, no tailoring
- Log as `Review Manually` (passed filter) or `Filtered` (failed filter)

---

## Pre-filter Criteria (LinkedIn + Portal Scanner)

```
Cities:     Mumbai, Pune, Bengaluru, Bangalore, Remote
Seniority:  Senior, Lead, Architect — reject Junior, Intern, Freelancer
Role:       Frontend, React, Next.js, Fullstack — reject Java, .NET, DevOps
Blacklist:  config/blacklist.yml — known outsourcing/service companies
```

---

## Google Sheets Schema

| Column | Example |
|---|---|
| Date | 2026-04-08 |
| Company | Razorpay |
| Role | Senior Frontend Engineer |
| Score | 87% |
| Matched Skills | React, Next.js, TypeScript, Performance |
| Gaps | Go experience preferred |
| JD URL | https://... |
| Screenshot | /output/screenshots/razorpay_080426.png |
| Tailored Resume | /output/tailored/razorpay_080426.md |
| Status | Shortlisted |
| Filter Reason | null |
| Applied | No |
| Notes | Warm contact: check LinkedIn |

### Canonical Statuses

| Status | Meaning |
|---|---|
| `Shortlisted` | Score 80%+ — tailored resume generated |
| `Review Manually` | Score 60-79% or LinkedIn pre-filter passed |
| `Skipped` | Score <60% — auto rejected by scorer |
| `Filtered` | Rejected before scoring — city/seniority/role mismatch |
| `Blacklisted` | Company in blacklist |
| `Applied` | Manually marked after applying |
| `Interviewing` | In process |
| `Rejected` | Rejected by company |

**Log every single job regardless of outcome. No exceptions.
This is how we improve the system over iterations.**

---

## Scraper Strategy

```
1. Verify job is still active (Playwright check)
2. Try DOM extraction via Playwright
3. If blocked or fails → grayscale screenshot (quality 60, max 800px width)
4. Pass screenshot to Haiku for text extraction (cheap vision call)
5. Pass clean text to Sonnet for scoring/tailoring
```

---

## Claude API Usage — Cost Rules

- **Haiku:** pre-filtering, text extraction from screenshots, simple classification
- **Sonnet:** match scoring, resume tailoring only
- Never use Sonnet for tasks Haiku can handle
- Batch API calls where possible — don't call per field, call per job

---

## Hard Rules

- **Never modify `resumes/base_resume.md`** — all tailoring goes to `output/tailored/`
- **Never fabricate experience** in tailored resumes — only reframe what exists
- **Never commit `.env`** or OAuth credentials JSON to git
- **Never auto-apply** — system shortlists, human decides and applies
- **Always ask before installing new packages**
- **All file outputs go to `output/` only**
- **Log every job** — even filtered and skipped ones

---

## Current Build Status

- [x] Phase 1 — Project structure and folder setup
- [x] Phase 2 — Gmail reader (`gmail_reader.py` reads inbox, extracts body + links)
- [ ] Phase 3 — JD Scraper (in progress — known issue: HTML body commented out)
- [ ] Phase 3.5 — Portal Scanner
- [ ] Phase 4 — Match Scorer
- [ ] Phase 5 — Resume Tailor (output as PDF, not just markdown)
- [ ] Phase 6 — Google Sheets Logger
- [ ] Phase 7 — Orchestrator + Notifier

**Update this section as phases are completed.**

---

## Decisions Already Made

- LinkedIn URLs — not scraped, pre-filtered from email HTML only
- City preferences — Mumbai, Pune, Bengaluru, Remote
- Score threshold — 80% for full pipeline, 60% for manual review flag
- Resume output — PDF (via Playwright/HTML template), not just markdown
- Logging — everything gets logged, including filtered and skipped
- Dedup — never create duplicate company+role rows, update existing entry
- Portal scanner — uses `config/portals.yml` for company career page URLs
- STAR story bank — Phase 8 backlog, not MVP

---

## Backlog (Post-MVP)

- PDF resume output with styled HTML template
- STAR story bank accumulated per evaluation
- LinkedIn outreach draft generated per shortlisted job
- A-F weighted scoring dimensions (v2 of scorer)
- Cron job scheduling (manual run for now)
- Go TUI dashboard (after Flocuz — don't mix projects)

---

## How I Want to Learn (Important)

Python is new for me. I learn by struggling, not by copy-pasting.

**Do NOT give me full code blocks unless I am completely stuck.**

- Explain the concept or approach first
- Point me to the right docs or library
- Ask me to try it, then review what I wrote
- If I'm wrong, tell me why — don't just fix it silently
- If I'm right but it can be improved, show me after I've solved it

**Exceptions — just give me these, not where the learning is:**

- Boilerplate (virtualenv setup, folder init, basic imports)
- OAuth setup steps (it's config, not logic)
- pip install commands
- Google Sheets / Gmail API credential setup

The real learning is in:

- Writing the agent logic myself
- Designing prompts for Haiku and Sonnet
- Structuring the LangGraph graph
- Handling errors and retries
- Debugging when it breaks

```

---

*Update this file as the project evolves. This is the single source of truth.*
*Last updated: April 2026*
