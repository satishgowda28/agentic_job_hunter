# Code Review — Phase 3 JD Scraper (2026-04-22)

Files reviewed:
- `agents/jd_scraper.py`
- `agents/site_scrapers/__init__.py`
- `agents/site_scrapers/base_scraper.py`
- `agents/site_scrapers/linkedin.py`
- `agents/site_scrapers/hirist.py`

---

## agents/jd_scraper.py

### Issues

**1. Browser never closes — resource leak**
`pw = sync_playwright().start()` is never stopped. If `scrape_jd()` raises an exception, the browser process stays open indefinitely.
Fix: use `with sync_playwright() as pw:` context manager (already noted as TODO).

**2. `if url is not None` is always True**
`sys.argv` always returns strings — it can never be `None`. The check is meaningless.
Fix: remove the condition, or validate that the URL format is correct instead.

**3. Scraper never called**
`scrape_jd()` navigates to the URL but never dispatches to a site scraper or returns anything.
Fix: add the Factory dispatcher and `scraper.extract_jd(url, page)` call.

**4. Commented-out code**
Lines 33-34 are dead code. Remove them.

**5. Warmup delay is in the wrong place**
`time.sleep(random.uniform(2, 4))` fires after Google warmup but before LinkedIn navigation. This is correct, but the intent is not obvious. A comment or rename would help future readers.

---

## agents/site_scrapers/__init__.py

### Issues

**1. `get_scraper()` is not implemented**
The function body is just `pass`. This is the most critical missing piece — nothing can dispatch to a scraper until this is done.
Fix: parse the domain from the URL using `urllib.parse.urlparse(url).netloc` and look it up in `SCRAPER_REGISTRY`.

**2. `HiristScraper` missing from registry**
`_scraper = [LinkedinScraper()]` — `HiristScraper` is imported but not added to the list.
Fix: add `HiristScraper()` to the list once it is implemented.

**3. No fallback for unknown domains**
If a URL doesn't match any registered domain, `get_scraper()` will return `None` (once implemented). The caller needs to handle this — either with a `GenericScraper` fallback or by logging and skipping.

---

## agents/site_scrapers/base_scraper.py

### Issues

**1. `ai_client` is a module-level global**
`ai_client = Anthropic(...)` is instantiated at import time. This means every test or import loads the `.env` and creates an API client, even if no scraping is happening.
Fix: acceptable for now at MVP stage, but worth moving inside `_dataExtractor` or making lazy later.

**2. `_dataExtractor` is not actually private**
Python convention for private module-level functions is `_name`. It's named `_dataExtractor` (camelCase) which mixes conventions — Python style is `_snake_case`.
Fix: rename to `_extract_from_image` or `_data_extractor`.

**3. `json.loads()` can throw if Haiku returns malformed JSON**
If Haiku returns anything other than valid JSON (e.g. adds a preamble despite instructions), `json.loads(block.text)` raises `json.JSONDecodeError` and the whole scrape fails silently via the outer `except`.
Fix: wrap `json.loads()` in a `try/except json.JSONDecodeError` and return `None` with a logged error.

**4. `_screenshot_fallback` return type annotation is imprecise**
`-> (Any | None, str)` is not a valid Python type hint for a tuple.
Fix: use `-> tuple[dict | None, str]`.

**5. `output/screenshots/` directory may not exist**
`page.screenshot(path=path)` will throw if the directory doesn't exist.
Fix: add `os.makedirs("output/screenshots", exist_ok=True)` before the screenshot call.

**6. `is_active` is abstract in base but not all sites implement it the same way**
Marking `is_active` as `@abstractmethod` forces every scraper to implement it. This is correct, but `HiristScraper` currently has it commented out — meaning `HiristScraper` cannot be instantiated.

---

## agents/site_scrapers/linkedin.py

### Issues

**1. Single-selector fragility**
Each field uses exactly one selector (e.g. `.topcard__org-name-link`). LinkedIn changes class names frequently. If any one selector fails, the entire `extract_jd()` falls into the `except` block and returns `None`.
Fix (future): try a list of fallback selectors per field, as noted in `phase3_site_scrapers_oo.md`.

**2. All DOM extractions inside one `try` block**
If `company` locator fails, `job_data`, `job_location`, `job_title` are never extracted either — even if those selectors would have worked.
Fix (future): wrap each locator call independently so partial data can still be returned.

**3. `data_from_image = None` is unused in the happy path**
Initialised on line 36 but only used inside the `if` block. No impact, just unnecessary noise.

**4. `is_active` uses CTA container presence as proxy**
Checking `.top-card-layout__cta-container` is a reasonable heuristic but not definitive — the container can exist even for expired jobs (it just says "See who LinkedIn knows at..."). A stronger check would look for the "No longer accepting applications" text explicitly.
Fix (future): add text-based check as secondary signal.

---

## agents/site_scrapers/hirist.py

### Issues

**1. Not implemented**
`is_active()` and `extract_jd()` are commented out. `HiristScraper` cannot be instantiated — it will throw `TypeError` due to unimplemented abstract methods.
Fix: implement both methods before adding to the registry.

**2. Stale `from abc import abstractmethod` import**
Not used since the methods are commented out.
Fix: remove it.

---

## Summary — Priority Order

| Priority | File | Issue |
|---|---|---|
| P0 | `__init__.py` | `get_scraper()` not implemented — nothing works without this |
| P0 | `hirist.py` | Abstract methods not implemented — can't be instantiated |
| P0 | `jd_scraper.py` | Scraper never called — no end-to-end flow yet |
| P1 | `base_scraper.py` | `output/screenshots/` dir may not exist |
| P1 | `base_scraper.py` | `json.loads()` unprotected — silent failure on bad Haiku output |
| P1 | `jd_scraper.py` | Browser never closes — resource leak |
| P2 | `linkedin.py` | Single-selector fragility — will break when LinkedIn changes HTML |
| P2 | `base_scraper.py` | `_dataExtractor` naming convention mismatch |
| P3 | `jd_scraper.py` | `if url is not None` always True |
| P3 | `__init__.py` | No fallback for unknown domains |
