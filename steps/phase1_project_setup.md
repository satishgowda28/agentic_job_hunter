# Phase 1 — Project Setup & Scaffolding

## Status
DONE. Committed: `7150862` (Apr 4, 2026)

---

## What Was Built

Folder structure, config files, and project scaffold for the entire agentic pipeline.

```
agentic-job-hunter/
├── agents/
├── config/
│   └── profile.md       ← my skills, preferences, dealbreakers
├── orchestrator.py      ← entry point placeholder
├── .env.example
├── .gitignore
└── resume/base_resume.md (empty at this point)
```

---

## Key Decisions

### Python + uv
- Chose `uv` over `pip`/`poetry` for speed and simplicity
- `pyproject.toml` as project definition, `uv.lock` for reproducibility

### config/profile.md over hardcoded preferences
- Profile stored as markdown file, not env vars or JSON
- Reason: Claude reads it as natural language — easier to update, easier to reason about
- Scorer reads this file at runtime, so changes take effect without code changes

### Single .env for all secrets
- Gmail OAuth creds, Anthropic API key, Sheets credentials all in `.env`
- Never committed — `.gitignore` covers `.env` and `_creds/`

### Folder conventions decided upfront
- `output/tailored/` — tailored resumes
- `output/screenshots/` — JD screenshots
- `config/` — all non-secret config (profile, portals, blacklist)
- All agent files flat in `agents/` — no sub-packages until needed

---

## Stack Locked In

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.11+ | LangGraph, Anthropic SDK, Playwright all Python-native |
| AI | Claude API (Haiku + Sonnet) | Cost control — Haiku for cheap tasks, Sonnet for scoring/tailoring |
| Gmail | Gmail API (OAuth2) | Read-only access, no third-party mail lib needed |
| Scraping | Playwright | Handles JS-heavy career pages, screenshots built-in |
| Logging | Google Sheets API | Human-readable, shareable, no DB setup |

---

## Article Notes

- First session was about resisting over-engineering — no DB, no Docker, no LangGraph graph yet
- Decision to use `config/profile.md` as natural language input to Claude was a key early insight
- Folder structure designed so each phase maps to one agent file
