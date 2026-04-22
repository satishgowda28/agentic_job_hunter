# Phase 3 — JD Scraper

**File:** `agents/jd_scraper.py`

**Input:** a `JobInfo` (has `url`, maybe partial `company`/`role`)
**Output:** a `ScrapedJD(url, title, company, location, jd_text, screenshot_path, is_active)` — new dataclass, likely in the scraper file for now.

---

## Flow (per CLAUDE.md)

```
scrape_jd(job: JobInfo) -> ScrapedJD | None
  1. Launch Playwright (sync or async — pick one, stick with it)
  2. Navigate to job.url
  3. Check "is still active":
       - HTTP status != 200 → inactive
       - Page contains "job no longer available" / "expired" / "position filled" → inactive
       - Redirected to a listings page → inactive 
  4. Try DOM extraction:
       - Grab <title>, meta og:title, main content container
       - Most JD pages wrap content in <main>, <article>, or a known class
       - Return text if length > threshold (say 500 chars)
  5. If DOM extraction fails OR looks blocked (captcha, login wall):
       - Take full-page screenshot
       - Convert to grayscale, resize to max 800px width, JPEG quality 60
       - Save to output/screenshots/{company}_{ddmmyy}.jpg
       - Call Haiku vision with a prompt like "Extract the job description as plain text"
  6. Return ScrapedJD
```

---

## Libraries / APIs to look at

| Need | API |
|---|---|
| Launch browser | `playwright.sync_api.sync_playwright()` → `chromium.launch()` |
| Navigate | `page.goto(url, wait_until="domcontentloaded", timeout=30000)` |
| DOM text | `page.locator("main").inner_text()` or `page.content()` + BeautifulSoup |
| Screenshot | `page.screenshot(path=..., full_page=True)` |
| Image processing | `Pillow` (`PIL.Image`): `.convert("L")`, `.thumbnail((800, ...))`, `.save(quality=60)` |
| Haiku vision | Anthropic SDK — `messages.create` with an `image` content block (base64) |

**Install (ask first per CLAUDE.md):** `playwright`, `pillow`, `anthropic`. Plus `playwright install chromium` post-install.

---

## Decisions to make before coding

1. **Sync vs async Playwright?** Sync is easier to learn; async fits better when LangGraph enters the picture. Suggest start **sync**, refactor later.
2. **One browser per run, or per URL?** Per run. Open once at orchestrator level, pass `page`/`browser` to the scraper. Avoids 2-3s launch per job.
3. **Timeout + retry policy?** Retry once on timeout, skip on 2nd fail, always log the reason.
4. **How do you know DOM extraction "failed"?** Heuristic: text length < 500 chars, OR page title contains "access denied" / "403" / "captcha".
5. **Where does the Haiku call live?** Helper `_extract_text_from_screenshot(path) -> str` inside the scraper, or separate `agents/vision_extract.py` if reusable later.

---

## Suggested order of implementation (smallest learning steps)

1. Stub `scrape_jd()` that just does `page.goto()` + prints the title. Run on one real Hirist URL end-to-end.
2. Add DOM extraction — try a couple of sites, see what container holds the JD.
3. Add the "is still active" check.
4. Add screenshot + Pillow processing — verify the output file looks right.
5. Add Haiku vision call (needs `ANTHROPIC_API_KEY` in `.env`).
6. Wire into orchestrator.

---

## LinkedIn Scraper — Implementation Steps

### Decision (2026-04-22)
LinkedIn job alert emails contain `/comm/jobs/view/<id>/` URLs — these redirect to login.
Transforming to `/jobs/view/<id>/` gives public access without login via Playwright.
Anti-detection is applied at the browser context level (not per-scraper) so all site scrapers benefit.

### Anti-detection setup (in `jd_scraper.py` when creating browser context)
```
1. Spoof user-agent → browser.new_context(user_agent="real Chrome UA string")
2. Hide webdriver flag → context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
3. Warm up → visit google.com before hitting LinkedIn (reduces fingerprint suspicion)
4. Random delay → time.sleep(random.uniform(2, 4)) after page.goto()
```

### LinkedinScraper.extract_jd() steps
```
1. Transform URL: url.replace("/comm/jobs/view/", "/jobs/view/")
2. page.goto(transformed_url, wait_until="domcontentloaded", timeout=30000)
3. Random human delay
4. Check is_active:
     - page.url redirected away from /jobs/view/ → inactive
     - page content contains "No longer accepting applications" / "job has expired" → inactive
5. DOM extraction (LinkedIn public job page selectors):
     - Title:    h1.top-card-layout__title  OR  h1[class*="job-title"]
     - Company:  a.topcard__org-name-link  OR  span[class*="company-name"]
     - Location: span.topcard__flavor--bullet  OR  span[class*="location"]
     - JD text:  div.show-more-less-html__markup  OR  div[class*="description__text"]
6. If text length < 500 → screenshot fallback (same as base flow)
7. Return ScrapedJD
```

### Source of anti-detection patterns
Learned from `vertexcover-io/linkedin-spider` (open source, MIT licensed).
Translated their Selenium CDP stealth patterns to Playwright equivalents.

---

## Current Build Status (2026-04-22)

### Completed
- [x] `BaseSiteScraper` — abstract base with `_screenshot_fallback()` and `_dataExtractor()`
- [x] `ScrapedJD` dataclass defined in `base_scraper.py`
- [x] `LinkedinScraper.extract_jd()` — DOM extraction + "show more" button click + screenshot fallback
- [x] `LinkedinScraper.is_active()` — checks CTA container
- [x] `_screenshot_fallback()` — Playwright screenshot → Pillow grayscale/resize → Haiku vision → returns `(data, path)`
- [x] `_dataExtractor()` — Haiku vision call, returns parsed JSON dict
- [x] Anti-detection in `jd_scraper.py` — user-agent spoof, webdriver flag hidden, Google warmup, random delay
- [x] Haiku prompt — extracts `title`, `company`, `location`, `jd_text`, `is_active` as JSON

### Remaining
- [ ] `jd_scraper.py` — URL dispatcher (if/elif on domain → pick scraper)
- [ ] `jd_scraper.py` — call `scraper.extract_jd(url, page)` and return result
- [ ] `jd_scraper.py` — browser lifecycle fix (`with sync_playwright()` context manager)
- [ ] `hirist.py` — implement `is_active()` and `extract_jd()` (same pattern as LinkedIn)
- [ ] Test against real LinkedIn `/jobs/view/` URL end-to-end
- [ ] Test against real Hirist URL
- [ ] Verify screenshot saves to `output/screenshots/`
- [ ] Verify Haiku extraction returns valid JSON

### Key Decisions Made
- Fallback threshold: `len(job_data) < 500` chars triggers screenshot path
- "Show more" button always clicked before screenshot (expands hidden JD text)
- `wait_for_timeout(1000)` after button click — JS animation needs time to render
- `_dataExtractor` is a module-level private function (not a class method) — functional style preference
- `_screenshot_fallback` returns `(data, path)` tuple — caller unpacks both
- URL transform (`/comm/` → `/jobs/`) happens at email parser level, not in `LinkedinScraper`

---

## Open items from Phase 2 cleanup (non-blocking)

- `gmail_reader.py:105` — `payload = txt["payload"]` assigned but unused.
- `gmail_reader.py:13` — commented-out `Credentials` import, delete it.
- `emailParsers/hirist.py` — `HIRIST_SIGNLE` typo and duplicate `"Matching Jobs"` in `HIRIST_DIGEST_SUBJECT`.
