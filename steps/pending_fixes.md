# Pending Fixes — Existing Code

## Priority order (top = blocking)

---

### 1. `agents/gmail_reader.py`
**What:** `read_job_emails()` returns nothing, writes to `email_body.txt`
**Fix:** return `list[JobInfo]`, remove file writes
```python
# current
def read_job_emails():  # returns None, writes to email_body.txt

# target
def read_job_emails() -> list[JobInfo]:  # return accumulated JobInfo objects
```

---

### 2. `agents/types.py`
**What:** `JobStatus` enum missing two statuses needed by logger
**Fix:** add:
```python
FILTERED = "Filtered"      # city/seniority/role mismatch before scoring
BLACKLISTED = "Blacklisted"
```

---

### 3. `agents/match_scorer.py`
**What:** `caution` tier silently returns `None` — jobs lost, never logged
**Fix:** caution tier should call `job_composite()` same as `high` — score output determines status
Also: remove `print("process it with sonnet")` noise
```python
# current
elif job_legitimacy_data.tier == "caution":
    print(f"loggin will come here ...")  # falls through → returns None

# target: caution and high both score, logger handles the rest
```

---

### 4. `agents/jd_scraper.py`
**What 1:** `headless=False` — browser opens visually, breaks unattended runs
**Fix:** `headless=True` before orchestrator wires it up

**What 2:** `liveness.py` exists but `scrape_jd()` never calls it
**Fix:** after page load, call `classify_liveness()`, set `ScrapedJD.is_active = False` if expired

---

### 5. `agents/resume_tailor.py`
**What:** uses `claude-sonnet-4-5`, stale model
**Fix:** update to `claude-sonnet-4-6`

---

### 6. `orchestrator.py`
**What:** just `print("hello from orchestrator")` — Phase 7 work
**Fix:** wire full pipeline:
`gmail_reader` → `jd_scraper` → `match_scorer` → router → `resume_tailor` (80%+) → `logger`

---

## Not started yet
- `agents/logger.py` — Phase 6 (current)
- `agents/notifier.py` — Phase 7
- `agents/portal_scanner.py` — Phase 3.5
