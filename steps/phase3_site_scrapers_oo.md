# Phase 3 — Site Scrapers OO Architecture

This document outlines the procedure for implementing the site-specific scraper helpers, incorporating "Stealth Mode" and "Robustness" patterns.

## 1. Architecture: The Scraper Helper Pattern
Instead of a single giant script, we use a Factory pattern to delegate site-specific logic.

### Folder Structure
```text
agents/site_scrapers/
├── __init__.py          # The Factory (get_scraper_for_url)
├── base_scraper.py      # Abstract Base Class (The Blueprint)
├── linkedin.py          # LinkedIn-specific logic
├── hirist.py            # Hirist-specific logic
└── generic.py           # Fallback for all other sites
```

---

## 2. Implementation Procedure

### Step 1: Base Blueprint (`base_scraper.py`)
- [x] Define `ScrapedJD` dataclass (url, title, company, jd_text, etc.).
- [x] Define `BaseSiteScraper` ABC.
- [ ] **New:** Add `stealth_scroll(page)` and `human_delay()` methods to the base class so all scrapers can reuse them.

### Step 2: The Factory (`__init__.py`)
- Implement `get_scraper_for_url(url: str) -> BaseSiteScraper`.
- It should parse the domain using `urllib.parse` and return the correct instance.

### Step 3: Robust LinkedIn Scraper (`linkedin.py`)
Incorporate findings from the "VertexCover" article:
- **Multi-Selector Fallback:** Define a list of selectors for the JD (e.g., `.decorated-job-posting__details`, `.jobs-description`, `article`). Iterate until one works.
- **Is Active Check:** Specifically look for "No longer accepting applications" or "This job is expired" strings.
- **Stealth:** Call `stealth_scroll` before extracting text to ensure lazy-loaded content is visible.

### Step 4: Generic Fallback (`generic.py`)
- Target common semantic tags: `<main>`, `<article>`, or high-density text divs.
- Return `None` for JD text if length is `< 500` characters (triggering the Vision fallback).

---

## 3. "Stealth Mode" & Anti-Detection
Based on the LinkedIn Scraper MCP article, we should implement these in `agents/jd_scraper.py`:

| Technique | Implementation Detail |
|---|---|
| **User-Agent Spoofing** | Use a real-looking browser string in Playwright launch. |
| **Random Interaction** | Wait `random.uniform(1.0, 3.0)` seconds after navigation. |
| **Incremental Scroll** | Scroll in steps of 200-400px rather than jumping to the bottom. |
| **Persistent Context** | Use `browser_type.launch_persistent_context()` to save session data and avoid repeated "New Login" flags. |

---

## 4. Final Wiring
Update `agents/jd_scraper.py` to:
1. Initialize the Playwright Browser once.
2. For each job:
   - Identify the scraper helper via the Factory.
   - Run the helper's `extract_jd(page)` method.
   - If extraction fails (DOM blocked/changed) → **Trigger Haiku Vision Fallback**.
