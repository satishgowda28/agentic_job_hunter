# Agentic Job Hunter — Planned Upgrades from career-ops

Borrowed patterns from [career-ops](../career-ops). Visit when each phase is done.

---

## Phase 3 — JD Scraper (do these first)

### 1. Liveness check — port `liveness-core.mjs`
**File to create:** `agents/liveness.py`  
**Source:** `../career-ops/liveness-core.mjs` — `classifyLiveness()`  
**What:** Regex patterns classify job posting as `active | expired | uncertain` before scraping.  
**Why:** Skip dead listings before DOM extraction or Sonnet calls.

```python
HARD_EXPIRED = [
    r"job (is )?no longer available",
    r"position has been filled",
    r"this job has expired",
    r"no longer accepting applications",
    r"job (listing )?not found",
]
LISTING_PAGE = [r"\d+\s+jobs?\s+found", r"search for jobs page is loaded"]
APPLY_SIGNALS = [r"\bapply\b", r"easy apply", r"submit application", r"start application"]

def classify_liveness(status, body_text, controls):
    if status in (404, 410): return "expired"
    if any(re.search(p, body_text, re.I) for p in HARD_EXPIRED): return "expired"
    if any(re.search(p, c, re.I) for c in controls for p in APPLY_SIGNALS): return "active"
    if any(re.search(p, body_text, re.I) for p in LISTING_PAGE): return "expired"
    if len(body_text.strip()) < 300: return "expired"
    return "uncertain"
```

---

### 2. LinkedIn URL transform
**File:** `agents/jd_scraper.py`  
**Source:** `../career-ops/CLAUDE.md` — Decisions section  
**What:** `/comm/jobs/view/` → `/jobs/view/` before navigating.

```python
def normalize_linkedin_url(url):
    return url.replace("/comm/jobs/view/", "/jobs/view/")
```

---

### 3. Scraper fallback chain
**File:** `agents/jd_scraper.py`  
**Source:** career-ops `modes/oferta.md` + `liveness-core.mjs`  
**Chain:**
1. Navigate → `classify_liveness()`
2. Try DOM selector
3. If blocked/empty → grayscale screenshot (quality=60, max_width=800px)
4. Pass screenshot to Haiku vision → extract text
5. Return clean text to scorer

---

## Phase 4 — Match Scorer

### 4. Multi-dimensional scoring
**File:** `agents/match_scorer.py`  
**Source:** `../career-ops/modes/_shared.md` — Scoring System  
**What:** Replace flat `%` with 4 axes. Route on individual axes, not just composite.

```json
{
  "role_fit": 90,
  "seniority_match": 85,
  "location_match": 100,
  "legitimacy": "high",
  "composite": 87
}
```

**Routing rule:** Skip if `location_match=0` OR `legitimacy=suspicious` regardless of composite.

---

### 5. Block G legitimacy — pre-Sonnet Haiku call
**File:** `agents/match_scorer.py` (pre-filter step)  
**Source:** `../career-ops/modes/oferta.md` — Block G  
**What:** Cheap Haiku call before Sonnet. Returns legitimacy tier.

```
Prompt Haiku:
Given this job posting, assess:
1. Is an Apply button/link present? (yes/no)
2. Requirements realistic? (no 10yr exp for 3yr old tech?)
3. Tech specificity: does it name real tools/frameworks?
4. Any contradictions (entry-level title + staff requirements)?

Return JSON: { "apply_present": bool, "requirements_sane": bool,
               "tech_specific": bool, "contradictions": bool,
               "tier": "high|caution|suspicious" }
```

If `tier=suspicious` → log as `Filtered`, skip Sonnet entirely.

---

## Phase 5 — Resume Tailor

### 6. Proof points layer — `article-digest.md` pattern
**File to create:** `resume/proof_points.md`  
**Source:** `../career-ops/article-digest.md` — structure  
**What:** Separate file of specific metrics/achievements. Feed into tailor prompt alongside base resume.

```markdown
## Performance wins
- Reduced bundle size 40% — migrated to RSC
- Led migration of 5 legacy jQuery apps to Next.js 14 — 0 regressions

## Architecture decisions
- Designed micro-frontend split for 8-team org
```

Tailor prompt: base_resume + proof_points → pick what matches JD → insert specifics.

---

## Config (do anytime)

### 7. Title filter structure from `portals.example.yml`
**File:** `config/portals.yml`  
**Source:** `../career-ops/templates/portals.example.yml`  
**What:** Add `title_filter.positive` / `title_filter.negative` YAML block.

```yaml
title_filter:
  positive:
    - "Frontend"
    - "React"
    - "Next.js"
    - "Fullstack"
    - "UI Engineer"
  negative:
    - "Junior"
    - "Intern"
    - "Java"
    - ".NET"
    - "DevOps"
```

---

## Status

| # | Upgrade | Phase | Done |
|---|---------|-------|------|
| 1 | Liveness check | 3 | [ ] |
| 2 | LinkedIn URL transform | 3 | [ ] |
| 3 | Scraper fallback chain | 3 | [ ] |
| 4 | Multi-dimensional scoring | 4 | [ ] |
| 5 | Block G legitimacy (Haiku pre-filter) | 4 | [ ] |
| 6 | Proof points layer | 5 | [ ] |
| 7 | Title filter YAML structure | config | [ ] |
