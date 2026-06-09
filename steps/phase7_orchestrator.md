# Phase 7 — Orchestrator + Notifier

## Goal
Wire all agents into a single runnable pipeline. One command runs everything — read emails, scrape, score, tailor, log.

---

## Input sources (MVP)
- Gmail reader only — portal scanner not built yet (Phase 3.5)

---

## Pipeline per job

```
gmail_reader.read_job_emails()
    → list[JobInfo]

for each JobInfo:
    1. jd_scraper.scrape_jd(job.url)
       → ScrapedJD | None
       if None → log as Skipped, continue

    2. match_scorer.score_job(scraped_jd)
       → ScoringResult | None
       if None (suspicious) → log as Skipped, continue

    3. Route by composite score:
       >= 80 → resume_tailor.tailor_resume(scraped_jd, scoring_result)
               → resume_path
               → logger.log_job(SHORTLISTED, scraped_jd, scoring_result, resume_path)

       60-79 → logger.log_job(REVIEW_MANUALLY, scraped_jd, scoring_result)

       < 60  → logger.log_job(SKIPPED, scraped_jd, scoring_result)
```

---

## Steps

### 1. `orchestrator.py` — main loop
- Call `read_job_emails()` → get list of jobs
- Loop over each job
- Call scraper, scorer, router in sequence
- Call logger every time — no exceptions

### 2. Error handling per job
- Wrap each job in try/except
- One job failing must NOT stop the rest
- Log the error, continue to next job

### 3. Summary collection
- Track counts: shortlisted, review, skipped, errors
- Pass to notifier at end

### 4. `agents/notifier.py`
- Send summary email via Gmail API (send scope needed)
- Plain text: counts + list of shortlisted jobs (company, role, score)

---

## What to skip for now
- Portal scanner input (Phase 3.5)
- Liveness check in scraper (pending fix)
- PDF resume output (needs texlive)
- Blacklist/filter logic (no portal scanner yet)

---

## Order of implementation
1. orchestrator.py main loop (no notifier yet)
2. Test end-to-end with real email
3. notifier.py
4. Test full run
