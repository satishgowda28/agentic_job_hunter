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

## Open items from Phase 2 cleanup (non-blocking)

- `gmail_reader.py:105` — `payload = txt["payload"]` assigned but unused.
- `gmail_reader.py:13` — commented-out `Credentials` import, delete it.
- `emailParsers/hirist.py` — `HIRIST_SIGNLE` typo and duplicate `"Matching Jobs"` in `HIRIST_DIGEST_SUBJECT`.
