# Agentic Job Hunter — Tasks

## Current Phase

Phase 3 — JD Scraper

## This Week Goals

1. Fix HTML body bug in gmail_reader.py
2. Filter noise from links list (tracking URLs, unsubscribe)
3. jd_scraper.py scrapes one real job URL successfully

## Today

- [ ] Fix: uncomment body = parsedHtml.get_text() in HTML branch
- [ ] Filter links — keep only URLs starting with http, exclude gmail/google/unsubscribe

## In Progress

Nothing — pick one task above and start

## Done

- [x] Project structure created
- [x] Dependencies installed (uv)
- [x] orchestrator.py running
- [x] Google Cloud project created
- [x] Gmail API enabled + OAuth configured
- [x] gmail_reader.py reads today's emails
- [x] Body extraction working (plain text + HTML)
- [x] Link extraction working (regex + BeautifulSoup)
- [x] CLAUDE.md created
- [x] TASKS.md created

## Blocked

Nothing currently

## Notes

- Started: April 4, 2026
- Python is new — struggle first, ask second
- LinkedIn URLs → never scrape, pre-filter only
- Every session: update Done section before closing
