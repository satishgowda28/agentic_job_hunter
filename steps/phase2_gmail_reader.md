# Phase 2 — Gmail Reader

## Status
DONE. Key commits: `b6bd789` (Apr 4), `ae8c02b`, `53eea66` (Apr 11, 2026)

---

## What Was Built

`agents/gmail_reader.py` — connects to Gmail via OAuth2, reads inbox, extracts job data per email type.

---

## Architecture Decision: Parser Registry Pattern

Emails come from different senders — Hirist, LinkedIn, company recruiters. Each has a different HTML structure.

**Problem:** One big `if/else` chain in `gmail_reader.py` would get unmaintainable fast.

**Solution:** Parser registry — `agents/emailParsers/` package with:
- `base_parser.py` — abstract base class with `parse_job()` interface
- `hirist.py` — Hirist digest parser (multiple jobs per email)
- `linkedin.py` — LinkedIn alert parser (structured HTML blocks)
- `__init__.py` — `get_parser(sender_email)` factory function

`gmail_reader.py` calls `get_parser(email)` → gets right parser → calls `parse_job()`. No conditionals in reader.

**Why this matters:** Adding a new email source = add one parser file, register it. Gmail reader never changes.

---

## Key Decisions

### OAuth2 with pickle token cache
- `token.pickle` stores refreshed credentials locally
- Avoids re-authenticating on every run
- Never committed (in `.gitignore`)

### Gmail label filter: `label:jobs_agents`
- Only reads emails in a specific Gmail label, not full inbox
- User manually labels job emails (or sets Gmail filter rules)
- Prevents processing irrelevant mail

### Read-only scope
- `SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]`
- System never sends, never deletes — read-only by design

### HTML preferred over plain text
- For multipart emails, HTML part parsed with BeautifulSoup
- Plain text fallback with regex URL extraction
- LinkedIn alert emails are HTML-structured — BeautifulSoup needed for job block parsing

### LinkedIn URLs — no scraping attempted at parser level
- LinkedIn alert emails contain job URLs
- Parser extracts title, company, location, URL only
- Scraping decision deferred to JD Scraper (Phase 3)

### JobInfo dataclass as output contract
```python
@dataclass
class JobInfo:
    source: str   # "hirist_single", "hirist_digest", "linkedin_alert"
    url: str
    subject: str
    company: str
    role: str
    experience: str
```
Each parser returns `list[JobInfo]` — consistent shape for orchestrator regardless of email source.

---

## What Was Harder Than Expected

- Gmail API multipart email structure — emails can be nested parts, not flat
- LinkedIn email HTML — heavily nested divs, had to inspect raw HTML to find job blocks
- OAuth flow on first run requires browser — `run_local_server(port=0)` handles it

---

## Article Notes

- Parser registry pattern is a clean real-world example of Open/Closed Principle
- OAuth pickle token is a pragmatic shortcut — production would use a secrets manager
- Separating email parsing from Gmail API connection was the right call early
