# Agentic Job Hunter — PRD

**Version:** 1.0  
**Author:** Satish Gowda  
**Stack:** Python · LangGraph · Gmail API · Google Sheets API · Puppeteer · Claude API  
**Goal:** Automate job discovery, resume tailoring, match scoring, and logging — so you wake up to a clean shortlist every morning.

---

## 1. Problem

You get job emails daily but most go unread. Manually reading JDs, judging fit, tailoring resume, and logging applications is slow and inconsistent. High-quality opportunities are slipping through because the overhead is too high.

---

## 2. What This System Does

1. Reads your Gmail inbox for job-related emails
2. Extracts the JD — either from email body or by scraping the linked URL
3. Scores how well the JD matches your profile (0–100%)
4. If score is 80%+: tailors your base resume to the JD
5. Takes a screenshot of the job listing
6. Logs everything to Google Sheets
7. Sends you a daily summary — what matched, what was skipped

You review the shortlist. You decide to apply. System handles everything before that decision.

---

## 3. What This Is NOT

- It does NOT auto-apply. That's fragile and counterproductive for senior roles.
- It does NOT scrape LinkedIn or Naukri (they block bots aggressively — not worth it).
- It does NOT replace your judgment — it informs it.

---

## 4. Agents

### Agent 1 — Gmail Reader

**Job:** Connect to Gmail, find job-related emails, extract JD text or URL.  
**Input:** Your Gmail inbox  
**Output:** List of `{ subject, sender, body_text, jd_url, date }`

### Agent 2 — JD Scraper

**Job:** If email contains a URL, scrape the full JD text from that page.  
**Input:** JD URL  
**Output:** Full job description text

### Agent 3 — Match Scorer

**Job:** Compare JD against your profile. Return a score and reasoning.  
**Input:** JD text + your profile (skills, experience, preferences)  
**Output:** `{ score: 85, matched_skills: [...], gaps: [...], reasoning: "..." }`

### Agent 4 — Resume Tailor

**Job:** Rewrite your base resume to emphasize what the JD values.  
**Input:** JD text + your base resume (markdown file)  
**Output:** Tailored resume as a new markdown file

### Agent 5 — Logger

**Job:** Write a row to Google Sheets for every processed job.  
**Input:** All data from above agents  
**Output:** New row in sheet with: Company, Role, Score, Match Highlights, Gaps, JD URL, Screenshot path, Date, Status

### Agent 6 — Notifier

**Job:** Send you a daily email summary of what was processed.  
**Input:** All logged rows from today  
**Output:** Clean summary email — "5 jobs processed today. 2 matched 80%+."

### Orchestrator

**Job:** Runs all agents in sequence. Decides routing based on score threshold.  
**Logic:** Gmail → Scraper → Scorer → if score ≥ 80 then (Tailor + Screenshot + Log as "Shortlisted") else (Log as "Skipped")

---

## 5. Tech Stack

| Layer | Tool | Why |
|---|---|---|
| Agent framework | LangGraph | Same stack as your Agentic Ecommerce Ops project |
| Language | Python 3.11+ | Best ecosystem for Gmail/Sheets APIs |
| Gmail integration | Gmail API (official) | Reliable, no scraping needed |
| JD scraping | Playwright (Python) | Handles JS-rendered pages |
| Screenshot | Playwright | Same library, one install |
| Resume tailoring | Claude API (Sonnet) | Best at rewriting with context |
| Match scoring | Claude API (Sonnet) | Structured reasoning output |
| Logging | Google Sheets API | Already in your workflow |
| Notification | Gmail API (send) | Same auth, no extra setup |
| Config | `.env` file | API keys, thresholds, paths |
| Storage | Local filesystem | Screenshots + tailored resumes saved locally |

---

## 6. Folder Structure

```
agentic-job-hunter/
├── agents/
│   ├── gmail_reader.py
│   ├── jd_scraper.py
│   ├── match_scorer.py
│   ├── resume_tailor.py
│   ├── logger.py
│   └── notifier.py
├── orchestrator.py
├── config/
│   └── profile.md          ← Your skills, experience, preferences
├── resumes/
│   └── base_resume.md      ← Your master resume in markdown
├── output/
│   ├── tailored/           ← Tailored resumes saved here
│   └── screenshots/        ← JD screenshots saved here
├── .env                    ← API keys (never commit this)
├── requirements.txt
├── CLAUDE.md               ← Project context for Claude Code sessions
└── README.md
```

---

## 7. Google Sheet Structure

| Column | Value |
|---|---|
| Date | 2026-03-30 |
| Company | Razorpay |
| Role | Senior Frontend Engineer |
| Score | 87% |
| Matched Skills | React, Next.js, TypeScript, Performance |
| Gaps | Go experience preferred |
| JD URL | https://... |
| Screenshot | /output/screenshots/razorpay_030326.png |
| Tailored Resume | /output/tailored/razorpay_030326.md |
| Status | Shortlisted |
| Applied | No |
| Notes | Warm contact: check LinkedIn |

---

## 8. Your Profile File (config/profile.md)

This is what the Match Scorer reads. You write this once.

```markdown
# Satish Gowda — Profile

## Skills
React, Next.js, TypeScript, JavaScript, Node.js, Performance Optimization,
Core Web Vitals, Checkout Flows, PCI Compliance, Design Systems,
Micro Frontends, Turborepo, Shopify, LangGraph (learning), FastAPI (learning)

## Experience
12+ years frontend. Last role: Senior Frontend Architect.
Built azafashions.com from scratch — luxury Indian fashion ecommerce.
Worked at: Aza Fashions, Unifynd, Stylabs, WhiteHat Jr.

## Preferences
- Role type: Senior Frontend / Architect / Lead
- Company type: Startups, Product companies
- No: Pure DSA interview companies
- Location: Mumbai / Remote
- Salary: [add your range]

## Dealbreakers
- Junior-heavy roles with no architectural scope
- Outsourcing / service companies
- Roles requiring Java or .NET
```

---

## 9. Build Phases

### Phase 1 — Foundation (Week 1)

Get the project running locally with core infrastructure.

**Steps:**

1. Create project folder and virtual environment
2. Install dependencies (LangGraph, Playwright, Google API client)
3. Set up `.env` with placeholder keys
4. Create `config/profile.md` with your actual profile
5. Create `resumes/base_resume.md` with your master resume
6. Write a basic `orchestrator.py` that just prints "hello from orchestrator"
7. Confirm everything runs without errors

**Done when:** You can run `python orchestrator.py` without crashing.

---

### Phase 2 — Gmail Agent (Week 1)

Read your actual inbox.

**Steps:**

1. Create a Google Cloud project
2. Enable Gmail API
3. Download OAuth credentials JSON
4. Write `agents/gmail_reader.py`
5. Test: run it, print the last 10 emails with "job" or "hiring" in subject
6. Add label filter — only read emails tagged "Jobs" (you create this label in Gmail)
7. Output structured list of job email objects

**Done when:** You see a list of job emails printed in terminal with subject, sender, date.

---

### Phase 3 — JD Scraper + Screenshot (Week 2)

Extract the actual job description from linked URLs.

**Steps:**

1. Install Playwright: `pip install playwright` then `playwright install`
2. Write `agents/jd_scraper.py`
3. Test on 3 known job URLs (Naukri, LinkedIn, company site)
4. Handle failures gracefully — if scraping fails, use email body as fallback
5. Add screenshot logic to same agent — save PNG to `output/screenshots/`

**Done when:** Given a URL, you get back full JD text + a screenshot file.

---

### Phase 4 — Match Scorer (Week 2)

The intelligence layer.

**Steps:**

1. Get Claude API key from console.anthropic.com
2. Write `agents/match_scorer.py`
3. Design the prompt carefully — give it your profile + JD, ask for JSON output: score, matched skills, gaps, reasoning
4. Test on 5 real JDs you have saved
5. Calibrate — if scores feel off, adjust the prompt

**Done when:** Given a JD, you get back a reliable match score with reasoning you agree with.

---

### Phase 5 — Resume Tailor (Week 3)

Auto-customize your resume per JD.

**Steps:**

1. Write `agents/resume_tailor.py`
2. Prompt: give it your base resume + JD, ask it to rewrite emphasizing relevant experience
3. Save output to `output/tailored/companyname_date.md`
4. Review 3 outputs manually — does it sound like you? adjust prompt if not
5. Add guardrail: never fabricate experience, only reframe what exists

**Done when:** You get a tailored resume that sounds like you wrote it for that specific role.

---

### Phase 6 — Google Sheets Logger (Week 3)

Persistent record of everything.

**Steps:**

1. Create a Google Sheet manually with column headers from Section 7
2. Enable Google Sheets API in your Cloud project (same one as Gmail)
3. Write `agents/logger.py`
4. Test: run it with dummy data, confirm a row appears in your sheet
5. Add "Applied" checkbox column — you update this manually after applying

**Done when:** Every processed job automatically appears as a row in your sheet.

---

### Phase 7 — Orchestrator + Notifier (Week 4)

Wire everything together.

**Steps:**

1. Build `orchestrator.py` using LangGraph — define the agent graph and routing logic
2. Routing: if score ≥ 80 → run tailor + screenshot + log as Shortlisted. Else → log as Skipped
3. Write `agents/notifier.py` — sends you a summary email at end of run
4. Run full pipeline end to end on 10 real emails
5. Fix whatever breaks
6. Schedule it — run manually for now, add cron later if you want

**Done when:** You run one command, walk away, and come back to a populated Google Sheet and a summary email.

---

## 10. CLAUDE.md for This Project

Put this at the root of your project before starting any Claude Code session:

```markdown
# Agentic Job Hunter

## What this is
A multi-agent system that reads Gmail, scores job matches against my profile,
tailors my resume for matches above 80%, screenshots the JD, and logs to Google Sheets.

## Stack
Python 3.11, LangGraph, Claude API (Sonnet), Gmail API, Google Sheets API, Playwright

## Key files
- config/profile.md — my skills and preferences (used by match scorer)
- resumes/base_resume.md — my master resume (used by resume tailor)
- .env — all API keys (never modify or print this)
- orchestrator.py — entry point, runs all agents in sequence

## Rules
- Never modify base_resume.md — tailor to output/tailored/ only
- Never fabricate experience in tailored resumes — only reframe what exists
- Always ask before installing new packages
- Keep Claude API calls minimal — batch where possible
- All file outputs go to output/ folder only
- Never commit .env or credentials JSON to git
```

---

## 11. What You Learn Building This

By the time Phase 7 is done, you will have hands-on experience with:

- LangGraph agent orchestration and routing
- OAuth2 authentication flow (Gmail + Sheets)
- Prompt engineering for structured JSON output
- Playwright for scraping and screenshots
- Multi-agent state management
- Real async Python patterns
- API error handling and retries

This is 80% of what the Agentic Ecommerce Ops project teaches — but with a problem you actually care about solving right now.

---

## 12. What Comes After

Once this is running:

- Write the Medium article — "I built an AI agent to handle my job search while I slept"
- Port the Gmail + Sheets patterns directly into Agentic Ecommerce Ops
- Add Obsidian logging as an alternative to Sheets (just markdown files)
- Open source it — other job hunters will use it

---

*Start with Phase 1. Don't read ahead. Ship one phase at a time.*
