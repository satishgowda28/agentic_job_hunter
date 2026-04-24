import logging
import os
import random
import sys
import time

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from .site_scrapers import get_scraper

load_dotenv()


def start():
    [_, url] = sys.argv
    if url is not None:
        scrape_jd(url)


def scrape_jd(url: str):
    job_scraped = None
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(user_agent=os.getenv("USER_AGENT"))
        context.add_init_script(
            """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        )
        page = context.new_page()
        page.goto("https://google.com")
        time.sleep(random.uniform(2, 4))
        try:
            scraper = get_scraper(url)
            if scraper is not None:
                job_scraped = scraper.extract_jd(url, page)
            else:
                logging.warning(f"Scraper not for {url}")
        except Exception as err:
            print(err)
        finally:
            browser.close()
    return job_scraped


if __name__ == "__main__":
    start()
