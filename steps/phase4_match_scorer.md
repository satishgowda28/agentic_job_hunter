# Phase 4 — Match Scorer

## Status
DONE. Committed: `8d98308` (May 9, 2026)

---

## What Was Built

`agents/match_scorer.py` — two-stage scoring pipeline using Haiku + Sonnet.

---

## Architecture: Two-Stage Pipeline

### Stage 1 — Haiku Legitimacy Check (cheap gate)

Before spending Sonnet tokens scoring a JD, Haiku checks if it's worth scoring at all.

**Three checks:**
1. `requirements_sane` — is this a real external job posting? Not spam, not internal transfer
2. `tech_specific` — does it name actual technologies? Not just "web skills"
3. `contradictions` — does it contradict itself? e.g. "Senior" + "0-2 years exp"

**Tier derivation (priority order):**
```
if contradictions → "suspicious" (stop immediately)
elif !requirements_sane OR !tech_specific → "caution" (log, skip scoring)
else → "high" (proceed to Sonnet)
```

**Why Haiku:** Fast, cheap, this is a binary gate — no nuance needed. Sonnet would be wasteful here.

### Stage 2 — Sonnet Composite Scoring

Only runs for `tier == "high"` JDs.

**Three axes scored 0-100:**
- `role_fit` (weight 50%) — does the JD stack match my profile stack?
- `seniority_match` (weight 30%) — does experience requirement match my level?
- `location_match` (weight 20%) — does location match my preferences?

**Composite formula:**
```python
composite = (role_fit * 0.5) + (seniority_match * 0.3) + (location_match * 0.2)
```

**Why these weights:** Role fit matters most — wrong stack = no point applying. Seniority second. Location last because remote is always acceptable.

**Status routing from composite:**
```
>= 80 → Shortlisted (full pipeline: tailor resume)
>= 60 → Review Manually
< 60  → Skipped
```

---

## Key Decisions

### profile.md as Sonnet input
- Scorer reads `config/profile.md` at runtime
- Profile written in natural language — Sonnet reads it the same way a human recruiter would
- No structured schema — easier to update, more flexible

### Sonnet returns JSON, parsed via Pydantic
- `MatchReport` Pydantic model validates Sonnet output
- If JSON is malformed → `None` returned, job skipped gracefully
- No crashing on bad model output

### Types consolidated into `agents/types.py`
- Before Phase 4: types scattered across parser and scraper files
- Phase 4 unified all shared types: `JobInfo`, `ScrapedJD`, `Legitimacy`, `MatchReport`, `JobFitReport`, `ScoringResult`, `JobStatus`
- Single source of truth — no import cycles, no duplication

### ScoringResult as pipeline contract
```python
@dataclass
class ScoringResult:
    job_fit_report: JobFitReport
    legitimacy_data: Legitimacy
```
Carries both scoring result and legitimacy data forward — orchestrator and resume tailor both need it.

---

## Cost Design

| Task | Model | Reason |
|---|---|---|
| Legitimacy check | Haiku | Binary gate, no nuance needed |
| Profile scoring | Sonnet | Nuanced reasoning against profile required |

Haiku call costs ~10x less than Sonnet. Gate keeps Sonnet calls to genuine candidates only.

---

## What Was Harder Than Expected

- Getting Sonnet to return raw JSON reliably — added explicit "no markdown fences" instruction
- `parsers.extract_and_validate()` utility needed to handle malformed JSON gracefully without crashing the pipeline
- Composite score weighting — took iteration to land on 50/30/20 split

---

## Article Notes

- Two-stage LLM pipeline (cheap gate → expensive scorer) is a reusable pattern for any agentic system
- Pydantic for LLM output validation is essential — models hallucinate structure
- Profile as natural language = the scorer improves just by editing a markdown file, no code change
